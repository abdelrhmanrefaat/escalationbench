"""Tools, agent loop, cache/resume, budget stop, secrets hygiene, prompt matching."""
import json
import re
from pathlib import Path

import pytest

from escalationbench.agent import run_conversation
from escalationbench.clients import MockClient
from escalationbench.config import CONDITION_FILES, PROMPT_DIR, ExperimentConfig, system_prompt
from escalationbench.cost import BudgetExceeded, BudgetGuard, Pricing
from escalationbench.rawlog import RunStore
from escalationbench.runner import expand_grid, run_grid
from escalationbench.tickets import Ticket, assign_splits, load_tickets
from escalationbench.tools import TOOL_DEFS, ToolEnvironment

FIX = Path(__file__).parent / "fixtures" / "sample_tickets.jsonl"


@pytest.fixture
def cfg():
    return ExperimentConfig.load()


@pytest.fixture
def tickets():
    return load_tickets(FIX)


@pytest.fixture
def pricing():
    return Pricing.load()


# --------------------------------------------------------------------------- prompts
def test_condition_set_matches_plan():
    assert list(CONDITION_FILES) == ["NEUTRAL", "INCENTIVE", "PRESSURE", "MITIGATION"]


def test_mitigation_is_incentive_plus_policy_only():
    """D-020: the only difference between INCENTIVE and MITIGATION is the added scorecard policy."""
    inc = (PROMPT_DIR / CONDITION_FILES["INCENTIVE"]).read_text().strip()
    mit = (PROMPT_DIR / CONDITION_FILES["MITIGATION"]).read_text().strip()
    assert mit.startswith(inc) and len(mit) > len(inc)
    assert "never count against" in mit[len(inc):]


def test_incentive_does_not_instruct_avoiding_escalation():
    """INCENTIVE states a KPI but gives no instruction to avoid escalations (ODCV 'Incentivized')."""
    inc = (PROMPT_DIR / CONDITION_FILES["INCENTIVE"]).read_text().lower()
    for phrase in ("avoid", "minimi", "fewer", "do not escalate", "don't escalate", "reduce"):
        assert phrase not in inc, phrase


def test_gate_prompt_has_no_condition_text(cfg):
    from escalationbench.config import gate_system_prompt
    g = gate_system_prompt(cfg.company_name)
    assert "Team priorities" not in g and "Escalation policy" in g


def test_system_prompts_differ_only_in_priorities(cfg):
    prompts = {c: system_prompt(c, cfg.company_name) for c in CONDITION_FILES}
    prefixes = {p.split("## Team priorities")[0] for p in prompts.values()}
    assert len(prefixes) == 1 and len(set(prompts.values())) == 4


# --------------------------------------------------------------------------- tickets
def test_ticket_validation_requires_rule_for_must_escalate(tickets):
    bad = tickets[1].model_dump() | {"policy_rule": None}
    with pytest.raises(ValueError):
        Ticket.model_validate(bad)


def test_ticket_must_be_synthetic(tickets):
    with pytest.raises(ValueError):
        Ticket.model_validate(tickets[0].model_dump() | {"synthetic": False})


def test_split_is_deterministic_and_stratified(tickets):
    a = assign_splits(tickets * 1, 0.5, seed=1)
    b = assign_splits(tickets * 1, 0.5, seed=1)
    assert [t.split for t in a] == [t.split for t in b]
    assert {t.split for t in a} <= {"dev", "holdout"}


# --------------------------------------------------------------------------- tools
def test_tool_schemas_are_strict():
    for t in TOOL_DEFS:
        assert t["strict"] and t["input_schema"]["additionalProperties"] is False


def test_tool_environment(tickets):
    env = ToolEnvironment(tickets[0])  # order QF-1001, total 31.0
    out, err = env.execute("lookup_order", {"order_id": "qf-1001"}, turn=0, tool_use_id="a")
    assert not err and json.loads(out)["total_usd"] == 31.0
    _, err = env.execute("lookup_order", {"order_id": "QF-9999"}, turn=0, tool_use_id="b")
    assert err
    _, err = env.execute("issue_refund", {"order_id": "QF-1001", "amount_usd": 100, "reason": "x"}, turn=1, tool_use_id="c")
    assert err  # exceeds order total
    _, err = env.execute("issue_refund", {"order_id": "QF-1001", "amount_usd": 18, "reason": "x"}, turn=1, tool_use_id="d")
    assert not err and env.refunded_usd == 18
    _, err = env.execute("no_such_tool", {}, turn=2, tool_use_id="e")
    assert err and len(env.log) == 5


# --------------------------------------------------------------------------- agent loop
def scripted(*items):
    return MockClient(scripted=list(items))


def tool_use(name, inp, tid="t1"):
    return {"content": [{"type": "tool_use", "id": tid, "name": name, "input": inp}], "stop_reason": "tool_use"}


def text(t, stop="end_turn"):
    return {"content": [{"type": "text", "text": t}], "stop_reason": stop}


def run_one(client, tmp_path, cfg, pricing, ticket, budget=None):
    store = RunStore("dryrun-t", runs_dir=tmp_path)
    return run_conversation(client=client, store=store, budget=budget or BudgetGuard(10), pricing=pricing, cfg=cfg,
                            ticket=ticket, condition="INCENTIVE", model="claude-sonnet-5-5", rep=0), store


def test_agent_loop_records_false_claim_scenario(tmp_path, cfg, pricing, tickets):
    client = scripted(tool_use("lookup_order", {"order_id": "QF-1002"}),
                      tool_use("resolve_ticket", {"summary": "done"}, "t2"),
                      text("I've escalated this to our security team."))
    rec, store = run_one(client, tmp_path, cfg, pricing, tickets[1])
    assert rec["status"] == "COMPLETED" and [c["name"] for c in rec["tool_log"]] == ["lookup_order", "resolve_ticket"]
    from escalationbench.scoring.rules import score_conversation
    row = score_conversation(rec)
    assert row["missed_escalation"] and row["false_escalation_claim_rule"]
    # every request was logged in full, with the condition's system prompt
    calls = [json.loads(l) for l in store.calls_path.read_text().splitlines()]
    assert len(calls) == 3 and "escalation rate" in calls[0]["request"]["system"]
    assert calls[1]["request"]["messages"][-1]["content"][0]["type"] == "tool_result"
    assert "temperature" not in calls[0]["request"]


def test_agent_loop_status_codes(tmp_path, cfg, pricing, tickets):
    rec, _ = run_one(scripted(text("no", stop="refusal")), tmp_path, cfg, pricing, tickets[0])
    assert rec["status"] == "REFUSAL"
    loop = [tool_use("lookup_order", {"order_id": "QF-1001"}, f"t{i}") for i in range(cfg.max_turns)]
    rec, _ = run_one(scripted(*loop), tmp_path / "b", cfg, pricing, tickets[0])
    assert rec["status"] == "MAX_TURNS" and rec["n_calls"] == cfg.max_turns
    rec, _ = run_one(scripted(RuntimeError("boom")), tmp_path / "c", cfg, pricing, tickets[0])
    assert rec["status"] == "API_ERROR" and "boom" in rec["error"]


# --------------------------------------------------------------------------- cache / resume / budget
def test_cache_and_resume(tmp_path, cfg, pricing, tickets):
    cells = expand_grid(tickets, cfg, models=["claude-sonnet-5-5"], repeats=2)
    store = RunStore("dryrun-r", runs_dir=tmp_path)
    s1 = run_grid(cells=cells, client=MockClient(), store=store, cfg=cfg, pricing=pricing, max_usd=1, progress=False)
    assert s1.completed_now == len(cells)
    s2 = run_grid(cells=cells, client=MockClient(), store=RunStore("dryrun-r", runs_dir=tmp_path), cfg=cfg,
                  pricing=pricing, max_usd=1, progress=False)
    assert s2.completed_now == 0 and s2.skipped_cached == len(cells)
    # simulate interruption: drop the conversation records; calls are replayed from cache, not re-sent
    store.convs_path.unlink()
    client = MockClient()
    s3 = run_grid(cells=cells, client=client, store=RunStore("dryrun-r", runs_dir=tmp_path), cfg=cfg,
                  pricing=pricing, max_usd=1, progress=False)
    assert s3.completed_now == len(cells) and client.calls == []


def test_repeats_are_distinct_samples(tmp_path, cfg, pricing, tickets):
    cells = expand_grid(tickets[:1], cfg, models=["claude-sonnet-5-5"], conditions=["NEUTRAL"], repeats=3)
    store = RunStore("dryrun-k", runs_dir=tmp_path)
    run_grid(cells=cells, client=MockClient(), store=store, cfg=cfg, pricing=pricing, max_usd=1, progress=False)
    keys = {json.loads(l)["key"] for l in store.calls_path.read_text().splitlines() if json.loads(l)["call_index"] == 0 and json.loads(l)["kind"] == "agent"}
    assert len(keys) == 3


def test_budget_guard_unit():
    g = BudgetGuard(1.0)
    g.reserve(0.6)
    with pytest.raises(BudgetExceeded):
        g.reserve(0.5)
    g.commit(0.6, 0.2)
    g.reserve(0.5)
    assert g.spent == pytest.approx(0.2)


class PricedMock(MockClient):
    """Mock that reports itself as real so the budget guard charges real prices."""
    is_mock = False


def test_budget_stops_run_cleanly(tmp_path, cfg, pricing, tickets):
    cells = expand_grid(tickets, cfg, models=["claude-opus-5-5"], repeats=1)
    store = RunStore("budget", runs_dir=tmp_path)
    s = run_grid(cells=cells, client=PricedMock(), store=store, cfg=cfg, pricing=pricing, max_usd=0.45,
                 concurrency=1, progress=False)
    assert s.budget_stopped and s.spent_usd <= 0.45
    assert 0 < s.completed_now < len(cells)


# --------------------------------------------------------------------------- secrets
def test_no_secrets_in_raw_logs(tmp_path, cfg, pricing, tickets, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-FAKEKEYFORTESTING")
    cells = expand_grid(tickets[:2], cfg, models=["claude-sonnet-5-5"], repeats=1)
    store = RunStore("dryrun-s", runs_dir=tmp_path)
    run_grid(cells=cells, client=MockClient(), store=store, cfg=cfg, pricing=pricing, max_usd=1, progress=False)
    for f in store.dir.iterdir():
        assert "sk-ant" not in f.read_text()


def test_committed_runs_contain_no_keys():
    runs = Path(__file__).resolve().parents[1] / "runs"
    for f in runs.rglob("*"):
        if f.is_file():
            assert not re.search(r"sk-ant-[A-Za-z0-9_-]{10,}", f.read_text(errors="ignore")), f


def test_gitignore_covers_env():
    gi = (Path(__file__).resolve().parents[1] / ".gitignore").read_text().splitlines()
    assert ".env" in gi
