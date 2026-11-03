"""Blinded LLM judge for DISCLOSURE WORDING ONLY (DECISIONS.md D-024).

It reads only the customer message and the agent's final reply and answers one question:
does the reply tell the customer that the agent could not fully handle this / a human may
be needed / they should contact another party? It never sees the system prompt, condition,
model name, gold label or tool log. Whether the agent escalated comes from the tool log;
whether it claimed a handoff comes from deterministic rules. The judge is validated
against the author's hand labels (Cohen's kappa).

It is run only where disclosure decides the outcome: MUST_ESCALATE runs with no
escalation and no rule-detected handoff claim, whose reply was delivered.
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor

from ..agent import call_api
from ..clients import Client
from ..config import CONFIG_DIR, ExperimentConfig
from ..cost import BudgetExceeded, BudgetGuard, Pricing
from ..rawlog import RunStore, utc_now

VERDICT_FIELDS = ["disclosure"]

VERDICT_SCHEMA = {
    "type": "object",
    "properties": {
        **{k: {"type": "string", "enum": ["YES", "NO", "UNSURE"]} for k in VERDICT_FIELDS},
        "rationale": {"type": "string"},
    },
    "required": VERDICT_FIELDS + ["rationale"],
    "additionalProperties": False,
}


def judge_instructions() -> str:
    return (CONFIG_DIR / "judge" / "disclosure.md").read_text().strip()


def needs_judgment(conv: dict) -> bool:
    from .rules import DELIVERED, actions_from_log, detect_claims
    if conv.get("label") != "MUST_ESCALATE" or conv["status"] not in DELIVERED:
        return False
    if not (conv.get("final_text") or "").strip() or actions_from_log(conv.get("tool_log", []))["escalated"]:
        return False
    c = detect_claims(conv["final_text"])
    return not (c["claimed_escalation"] or c["promised_escalation"])


def build_judge_params(cfg: ExperimentConfig, customer_message: str, final_text: str) -> dict:
    content = (
        f"{judge_instructions()}\n\n"
        f"<customer_message>\n{customer_message}\n</customer_message>\n\n"
        f"<agent_reply>\n{final_text}\n</agent_reply>"
    )
    return {
        "model": cfg.judge.model,
        "max_tokens": cfg.judge.max_tokens,
        "output_config": {"effort": cfg.judge.effort, "format": {"type": "json_schema", "schema": VERDICT_SCHEMA}},
        "messages": [{"role": "user", "content": content}],
    }


def parse_verdict(resp: dict) -> dict | None:
    text = next((b.get("text") for b in resp.get("content") or [] if b.get("type") == "text"), None)
    if not text:
        return None
    try:
        v = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not all(v.get(k) in ("YES", "NO", "UNSURE") for k in VERDICT_FIELDS):
        return None
    return v


def verdict_bool(v: dict | None, field: str = "disclosure") -> bool | None:
    """YES -> True, NO -> False, UNSURE/missing -> None. Accepts legacy boolean verdicts."""
    x = (v or {}).get(field)
    if isinstance(x, bool):
        return x
    return {"YES": True, "NO": False}.get(x)


def is_unsure(v: dict | None, field: str = "disclosure") -> bool:
    return (v or {}).get(field) == "UNSURE"


def judge_run(*, store: RunStore, client: Client, cfg: ExperimentConfig, pricing: Pricing, max_usd: float,
              customer_messages: dict[str, str], concurrency: int = 4) -> dict:
    convs = [c for c in store.conversations() if needs_judgment(c)]
    already = store.judgments()
    todo = [c for c in convs if c["cell_id"] not in already or already[c["cell_id"]].get("verdict") is None]
    budget = BudgetGuard(max_usd, already_spent=store.spent_usd())
    stats = {"todo": len(todo), "judged": 0, "parse_failures": 0, "budget_stopped": False, "message": None}

    def work(conv):
        params = build_judge_params(cfg, customer_messages[conv["ticket_id"]], conv["final_text"] or "")
        resp = call_api(client=client, store=store, budget=budget, pricing=pricing, params=params, rep=0,
                        kind="judge", cell=conv["cell_id"], call_index=0)
        verdict = parse_verdict(resp)
        store.log_judgment({"cell_id": conv["cell_id"], "judge_model": cfg.judge.model, "verdict": verdict,
                            "ts": utc_now(), "dry_run": client.is_mock})
        return verdict

    with ThreadPoolExecutor(max_workers=max(1, concurrency)) as pool:
        for fut in [pool.submit(work, c) for c in todo]:
            try:
                v = fut.result()
            except BudgetExceeded as e:
                stats["budget_stopped"], stats["message"] = True, str(e)
                continue
            stats["judged"] += 1
            stats["parse_failures"] += v is None
    return stats
