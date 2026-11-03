"""Single-ticket agent loop (manual tool-use loop so every request/response is logged)."""
from __future__ import annotations

import json
import time

from .clients import Client
from .config import ExperimentConfig, system_prompt
from .cost import BudgetGuard, Pricing
from .rawlog import RunStore, call_key, utc_now
from .tickets import Ticket
from .tools import TOOL_DEFS, ToolEnvironment

# Outcome codes for a conversation. Everything except COMPLETED is reported, never dropped.
STATUSES = ("COMPLETED", "MAX_TURNS", "REFUSAL", "MAX_TOKENS", "API_ERROR")


def _clean_block(block: dict) -> dict:
    """Return a content block in request form: drop None-valued fields, keep everything else
    (thinking blocks and their signatures are passed back unchanged)."""
    return {k: v for k, v in block.items() if v is not None}


def build_params(cfg: ExperimentConfig, model: str, system: str, messages: list[dict]) -> dict:
    return {
        "model": model,
        "max_tokens": cfg.max_tokens,
        "system": system,
        "tools": TOOL_DEFS,
        "tool_choice": {"type": "auto"},
        "thinking": {"type": "adaptive", "display": cfg.thinking_display},
        "output_config": {"effort": cfg.effort},
        "cache_control": {"type": "ephemeral"},
        "messages": messages,
    }


def reservation_usd(pricing: Pricing, params: dict) -> float:
    """Pessimistic per-call cost used by the budget guard: ~3 chars/token input, full max_tokens output."""
    r = pricing.rates(params["model"])
    approx_in = len(json.dumps({k: params[k] for k in ("system", "tools", "messages")}, default=str)) / 3
    return (approx_in * max(r["input"], r["cache_write"]) + params["max_tokens"] * r["output"]) / 1_000_000


def cell_id(ticket_id: str, condition: str, model: str, rep: int) -> str:
    return f"{ticket_id}|{condition}|{model}|r{rep}"


def call_api(
    *, client: Client, store: RunStore, budget: BudgetGuard, pricing: Pricing,
    params: dict, rep: int, kind: str, cell: str, call_index: int,
) -> dict:
    """Send one request (or return the cached response). Logs every call. Raises BudgetExceeded
    before sending if the cap would be crossed; re-raises API errors after logging them."""
    key = call_key(params, rep, kind)
    cached = store.cached_response(key)
    if cached is not None:
        return cached
    reserve = reservation_usd(pricing, params) if not client.is_mock else 0.0
    budget.reserve(reserve)
    ts_start, t0 = utc_now(), time.monotonic()
    rec = {
        "key": key, "kind": kind, "cell_id": cell, "call_index": call_index, "rep": rep,
        "model": params["model"], "request": params, "ts_start": ts_start, "dry_run": client.is_mock,
    }
    try:
        resp = client.create(params, seed=f"{cell}#{call_index}")
    except Exception as e:  # logged, then surfaced to the caller
        budget.commit(reserve, 0.0)
        store.log_call({**rec, "response": None, "error": f"{type(e).__name__}: {e}",
                        "ts_end": utc_now(), "latency_s": round(time.monotonic() - t0, 3), "cost_usd": 0.0})
        raise
    cost = pricing.cost(params["model"] if not client.is_mock else "mock-model", resp.get("usage"))
    budget.commit(reserve, cost)
    store.log_call({**rec, "response": resp, "error": None, "ts_end": utc_now(),
                    "latency_s": round(time.monotonic() - t0, 3), "usage": resp.get("usage"),
                    "cost_usd": round(cost, 6), "request_id": resp.get("_request_id"),
                    "response_model": resp.get("model")})
    return resp


def run_conversation(
    *, client: Client, store: RunStore, budget: BudgetGuard, pricing: Pricing,
    cfg: ExperimentConfig, ticket: Ticket, condition: str, model: str, rep: int,
) -> dict:
    cell = cell_id(ticket.id, condition, model, rep)
    system = system_prompt(condition, cfg.company_name)
    env = ToolEnvironment(ticket)
    messages: list[dict] = [{"role": "user", "content": ticket.customer_message}]
    status, final_text, thinking, all_text, error, n_calls = None, "", [], [], None, 0
    stop_details = None

    for turn in range(cfg.max_turns):
        params = build_params(cfg, model, system, messages)
        try:
            resp = call_api(client=client, store=store, budget=budget, pricing=pricing, params=params,
                            rep=rep, kind="agent", cell=cell, call_index=turn)
        except Exception as e:
            from .cost import BudgetExceeded
            if isinstance(e, BudgetExceeded):
                raise
            status, error = "API_ERROR", f"{type(e).__name__}: {e}"
            break
        n_calls += 1
        content = resp.get("content") or []
        texts = [b.get("text", "") for b in content if b.get("type") == "text"]
        thinking += [b.get("thinking") or "" for b in content if b.get("type") == "thinking"]
        all_text += texts
        stop = resp.get("stop_reason")

        if stop == "refusal":
            status, final_text, stop_details = "REFUSAL", "\n".join(texts), resp.get("stop_details")
            break
        if stop == "max_tokens":
            status, final_text = "MAX_TOKENS", "\n".join(texts)
            break
        messages.append({"role": "assistant", "content": [_clean_block(b) for b in content]})
        if stop == "pause_turn":
            continue
        tool_uses = [b for b in content if b.get("type") == "tool_use"]
        if stop == "tool_use" and tool_uses:
            results = []
            for b in tool_uses:
                out, is_err = env.execute(b["name"], b.get("input") or {}, turn=turn, tool_use_id=b["id"])
                results.append({"type": "tool_result", "tool_use_id": b["id"], "content": out, "is_error": is_err})
            messages.append({"role": "user", "content": results})  # all results in ONE user message
            continue
        status, final_text = "COMPLETED", "\n".join(texts)
        break
    else:
        status = "MAX_TURNS"
        final_text = all_text[-1] if all_text else ""

    rec = {
        "cell_id": cell, **ticket.meta(), "condition": condition, "model": model, "rep": rep,
        "status": status, "error": error, "stop_details": stop_details,
        "final_text": final_text, "all_text": all_text, "thinking_text": "\n---\n".join(t for t in thinking if t),
        "tool_log": env.log, "n_calls": n_calls, "ts": utc_now(), "dry_run": client.is_mock,
    }
    store.log_conversation(rec)
    return rec
