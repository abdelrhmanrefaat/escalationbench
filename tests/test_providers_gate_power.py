"""OpenAI adapter (no network), provider routing, knowledge gate, power check."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from escalationbench.agent import build_gate_params, build_params, parse_gate
from escalationbench.analysis.power import floor_check, simulate_power
from escalationbench.clients import MockClient, RoutingClient, from_openai_response, to_openai_request
from escalationbench.config import ExperimentConfig, system_prompt
from escalationbench.cost import Pricing
from escalationbench.rawlog import RunStore
from escalationbench.runner import expand_grid, run_grid
from escalationbench.tickets import load_tickets

FIX = Path(__file__).parent / "fixtures" / "sample_tickets.jsonl"


@pytest.fixture
def cfg():
    return ExperimentConfig.load()


# --------------------------------------------------------------------------- config / routing
def test_config_providers(cfg):
    assert cfg.providers["claude-sonnet-5-5"] == "anthropic"
    assert any(p == "openai" for m, p in cfg.providers.items() if m in cfg.models), "need a non-Anthropic model"
    assert cfg.providers[cfg.judge.model] == "anthropic"


def test_every_configured_model_has_pricing(cfg):
    pricing = Pricing.load()
    for m in cfg.models + [cfg.judge.model]:
        pricing.rates(m)


def test_routing_client_dispatches_by_model():
    seen = []

    class Fake:
        def __init__(self, name): self.name = name
        def create(self, params, seed): seen.append((self.name, params["model"])); return {}
        def count_tokens(self, params): return 1

    rc = RoutingClient({"a-model": "anthropic", "o-model": "openai"},
                       factories={"anthropic": lambda: Fake("A"), "openai": lambda: Fake("O")})
    rc.create({"model": "o-model"}, "s"); rc.create({"model": "a-model"}, "s")
    assert seen == [("O", "o-model"), ("A", "a-model")]
    with pytest.raises(KeyError):
        rc.create({"model": "unknown"}, "s")


# --------------------------------------------------------------------------- openai adapter
def _conversation_params(cfg):
    msgs = [
        {"role": "user", "content": "My kettle sparked. Order QF-1001."},
        {"role": "assistant", "content": [
            {"type": "thinking", "thinking": "summary", "_openai_reasoning": {"type": "reasoning", "id": "rs_1",
                                                                             "summary": [], "encrypted_content": "xx"}},
            {"type": "text", "text": "Let me check."},
            {"type": "tool_use", "id": "call_1", "name": "lookup_order", "input": {"order_id": "QF-1001"}}]},
        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "call_1", "content": '{"ok":1}',
                                      "is_error": False}]},
    ]
    return build_params(cfg, "gpt-6.1-sol", system_prompt("NEUTRAL", cfg.company_name), msgs)


def test_to_openai_request_mapping(cfg):
    req = to_openai_request(_conversation_params(cfg))
    assert req["model"] == "gpt-6.1-sol" and req["store"] is False
    assert req["instructions"].startswith("You are a customer support agent")
    assert req["max_output_tokens"] == cfg.max_tokens
    assert req["reasoning"] == {"effort": cfg.effort, "summary": "auto"}
    assert {t["name"] for t in req["tools"]} == {"lookup_order", "issue_refund", "resolve_ticket", "escalate_to_human"}
    assert all(t["type"] == "function" and t["strict"] for t in req["tools"])
    types = [i.get("type", "msg:" + i.get("role", "")) for i in req["input"]]
    assert types == ["msg:user", "reasoning", "message", "function_call", "function_call_output"]
    assert json.loads(req["input"][3]["arguments"]) == {"order_id": "QF-1001"}
    assert req["input"][4] == {"type": "function_call_output", "call_id": "call_1", "output": '{"ok":1}'}
    for k in ("cache_control", "thinking", "temperature", "messages", "system"):
        assert k not in req


def test_to_openai_request_structured_output(cfg):
    tickets = load_tickets(FIX)
    req = to_openai_request(build_gate_params(cfg, "gpt-6.1-sol", tickets[1]))
    assert req["text"]["format"]["type"] == "json_schema" and req["text"]["format"]["strict"] is True
    assert "tools" not in req


def test_from_openai_response_tool_call():
    raw = {"id": "resp_1", "model": "gpt-6.1-sol", "status": "completed", "output": [
        {"type": "reasoning", "id": "rs_1", "summary": [{"type": "summary_text", "text": "Need order."}],
         "encrypted_content": "enc"},
        {"type": "function_call", "call_id": "call_9", "name": "escalate_to_human",
         "arguments": '{"reason":"burn","priority":"urgent"}'}],
        "usage": {"input_tokens": 1000, "input_tokens_details": {"cached_tokens": 400}, "output_tokens": 300,
                  "output_tokens_details": {"reasoning_tokens": 200}}}
    r = from_openai_response(raw)
    assert r["stop_reason"] == "tool_use"
    assert r["content"][0]["type"] == "thinking" and r["content"][0]["thinking"] == "Need order."
    assert r["content"][1] == {"type": "tool_use", "id": "call_9", "name": "escalate_to_human",
                               "input": {"reason": "burn", "priority": "urgent"}}
    assert r["usage"]["input_tokens"] == 600 and r["usage"]["cache_read_input_tokens"] == 400
    assert r["usage"]["output_tokens"] == 300
    # billed: 600*2 + 400*0.10 + 300*10 per 1M
    assert Pricing.load().cost("gpt-6.1-sol", r["usage"]) == pytest.approx((600 * 2 + 400 * 0.1 + 300 * 10) / 1e6)


@pytest.mark.parametrize("raw,stop", [
    ({"status": "completed", "output": [{"type": "message", "content": [{"type": "output_text", "text": "Hi"}]}]}, "end_turn"),
    ({"status": "completed", "output": [{"type": "message", "content": [{"type": "refusal", "refusal": "No."}]}]}, "refusal"),
    ({"status": "incomplete", "incomplete_details": {"reason": "max_output_tokens"}, "output": []}, "max_tokens"),
    ({"status": "incomplete", "incomplete_details": {"reason": "content_filter"}, "output": []}, "refusal"),
])
def test_from_openai_response_stop_reasons(raw, stop):
    assert from_openai_response(raw)["stop_reason"] == stop


def test_openai_roundtrip_preserves_reasoning_item(cfg):
    raw = {"status": "completed", "output": [
        {"type": "reasoning", "id": "rs_7", "summary": [], "encrypted_content": "ENC"},
        {"type": "function_call", "call_id": "c1", "name": "resolve_ticket", "arguments": '{"summary":"x"}'}]}
    content = from_openai_response(raw)["content"]
    msgs = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": content}]
    req = to_openai_request(build_params(cfg, "gpt-6.1-sol", "sys", msgs))
    assert req["input"][1] == raw["output"][0]


# --------------------------------------------------------------------------- knowledge gate
def test_gate_params_are_neutral(cfg):
    t = load_tickets(FIX)[1]
    p = build_gate_params(cfg, "claude-sonnet-5-5", t)
    assert "Team priorities" not in p["system"] and "tools" not in p
    assert t.customer_message in p["messages"][0]["content"]


def test_parse_gate():
    ok = {"content": [{"type": "text", "text": '{"needs_human": true, "policy_rule": "E3"}'}]}
    assert parse_gate(ok) == {"needs_human": True, "policy_rule": "E3"}
    assert parse_gate({"content": [{"type": "text", "text": "not json"}]}) is None
    assert parse_gate({"content": []}) is None


def test_run_grid_runs_gate_once_per_ticket_model(tmp_path, cfg):
    tickets = load_tickets(FIX)
    cells = expand_grid(tickets, cfg, models=["claude-sonnet-5-5", "gpt-6.1-sol"], repeats=2)
    store = RunStore("dryrun-gate", runs_dir=tmp_path)
    s = run_grid(cells=cells, client=MockClient(), store=store, cfg=cfg, pricing=Pricing.load(), max_usd=1,
                 progress=False)
    gates = store.gates()
    assert s.gates_run == len(tickets) * 2 == len(gates)
    assert all(g["gate_pass"] in (True, False) for g in gates.values())
    # resume: no new gate probes
    s2 = run_grid(cells=cells, client=MockClient(), store=store, cfg=cfg, pricing=Pricing.load(), max_usd=1,
                  progress=False)
    assert s2.gates_run == 0


# --------------------------------------------------------------------------- power
def test_floor_check_flags_all_zero():
    df = pd.DataFrame({"model": ["m"] * 8, "condition": ["NEUTRAL", "INCENTIVE"] * 4, "x": [0.0] * 8})
    assert floor_check(df, "x")["floor_all_conditions"].iloc[0]
    df.loc[0, "x"] = 1.0
    assert not floor_check(df, "x")["floor_all_conditions"].iloc[0]


def test_power_is_alpha_under_null_and_high_for_big_effect():
    p = np.full(20, 0.2)
    null = simulate_power(p, n_tickets=60, repeats=2, delta=0.0, alpha=0.05, sims=300, seed=1)
    big = simulate_power(p, n_tickets=60, repeats=2, delta=0.4, alpha=0.05, sims=300, seed=1)
    assert null < 0.10 and big > 0.95


def test_gate_runs_through_budget_reservation_with_real_style_client(tmp_path, cfg):
    """Regression: real (non-mock) clients reserve budget before each call; gate params have no tools."""
    class RealStyle(MockClient):
        is_mock = False
    tickets = load_tickets(FIX)[:2]
    store = RunStore("gate-real", runs_dir=tmp_path)
    cells = expand_grid(tickets, cfg, models=["claude-haiku-5-5"], conditions=["NEUTRAL"], repeats=1)
    run_grid(cells=cells, client=RealStyle(), store=store, cfg=cfg, pricing=Pricing.load(), max_usd=5, progress=False)
    assert all(g["error"] is None and g["verdict"] is not None for g in store.gates().values())
