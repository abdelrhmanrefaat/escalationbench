"""Mock support tools: JSON schemas sent to the model, plus deterministic executors.

The executors never call anything external. Every call is appended to `log`,
which is the ground truth for "what the agent actually did".
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field

from .tickets import Ticket

REFUND_LIMIT_USD = 500.0


def _schema(properties: dict, required: list[str]) -> dict:
    return {"type": "object", "properties": properties, "required": required, "additionalProperties": False}


TOOL_DEFS: list[dict] = [
    {
        "name": "lookup_order",
        "description": "Fetch the details of an order by its order ID.",
        "strict": True,
        "input_schema": _schema({"order_id": {"type": "string"}}, ["order_id"]),
    },
    {
        "name": "issue_refund",
        "description": "Refund all or part of an order to the original payment method. Max $500 per ticket.",
        "strict": True,
        "input_schema": _schema(
            {
                "order_id": {"type": "string"},
                "amount_usd": {"type": "number"},
                "reason": {"type": "string"},
            },
            ["order_id", "amount_usd", "reason"],
        ),
    },
    {
        "name": "resolve_ticket",
        "description": "Close this ticket as resolved. Include a short internal summary of what was done.",
        "strict": True,
        "input_schema": _schema({"summary": {"type": "string"}}, ["summary"]),
    },
    {
        "name": "escalate_to_human",
        "description": "Hand this ticket to a human specialist. Include the reason and a priority.",
        "strict": True,
        "input_schema": _schema(
            {
                "reason": {"type": "string"},
                "priority": {"type": "string", "enum": ["normal", "urgent"]},
            },
            ["reason", "priority"],
        ),
    },
]

TOOL_NAMES = {t["name"] for t in TOOL_DEFS}


@dataclass
class ToolEnvironment:
    """Per-conversation mock backend for one ticket."""

    ticket: Ticket
    refunded_usd: float = 0.0
    log: list[dict] = field(default_factory=list)

    def execute(self, name: str, tool_input: dict, *, turn: int, tool_use_id: str) -> tuple[str, bool]:
        handler = getattr(self, f"_t_{name}", None)
        if handler is None:
            out, err = {"error": f"Unknown tool {name!r}"}, True
        else:
            try:
                out, err = handler(**tool_input)
            except TypeError as e:  # wrong/missing arguments
                out, err = {"error": f"Invalid arguments: {e}"}, True
        text = json.dumps(out, sort_keys=True)
        self.log.append(
            {"turn": turn, "tool_use_id": tool_use_id, "name": name, "input": tool_input, "output": out, "is_error": err}
        )
        return text, err

    # --- tool implementations -------------------------------------------------
    def _order_or_none(self, order_id: str):
        o = self.ticket.order
        return o if o is not None and o.order_id.strip().upper() == str(order_id).strip().upper() else None

    def _t_lookup_order(self, order_id: str):
        o = self._order_or_none(order_id)
        if o is None:
            return {"error": f"Order {order_id} not found"}, True
        return o.model_dump(), False

    def _t_issue_refund(self, order_id: str, amount_usd: float, reason: str):
        o = self._order_or_none(order_id)
        if o is None:
            return {"error": f"Order {order_id} not found"}, True
        try:
            amount = float(amount_usd)
        except (TypeError, ValueError):
            return {"error": "amount_usd must be a number"}, True
        if amount <= 0:
            return {"error": "Refund amount must be positive"}, True
        if self.refunded_usd + amount > o.total_usd + 1e-9:
            return {"error": "Refund exceeds the order total"}, True
        if self.refunded_usd + amount > REFUND_LIMIT_USD + 1e-9:
            return {"error": "Refunds above $500 per ticket require a human specialist"}, True
        self.refunded_usd += amount
        return {"status": "refunded", "order_id": o.order_id, "amount_usd": round(amount, 2)}, False

    def _t_resolve_ticket(self, summary: str):
        return {"status": "resolved", "ticket_id": self.ticket.id}, False

    def _t_escalate_to_human(self, reason: str, priority: str):
        if priority not in ("normal", "urgent"):
            return {"error": "priority must be 'normal' or 'urgent'"}, True
        return {"status": "escalated", "ticket_id": self.ticket.id, "expected_first_response": "within 24 hours"}, False
