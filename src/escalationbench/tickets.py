"""Synthetic ticket schema, loading, and dev/holdout splitting.

Every ticket is fictional. The `synthetic` field is a literal True so a real record
cannot be loaded by accident without editing the schema.
"""
from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

Category = Literal["payment_dispute", "account_security", "safety", "routine", "legal_privacy"]
Label = Literal["MUST_ESCALATE", "SHOULD_RESOLVE"]
Split = Literal["pilot", "dev", "holdout", "test"]


class OrderItem(BaseModel):
    sku: str
    name: str
    qty: int = Field(ge=1)
    unit_price_usd: float = Field(ge=0)


class Order(BaseModel):
    order_id: str
    customer_name: str
    order_date: str
    status: Literal["processing", "shipped", "delivered", "lost_in_transit", "returned", "cancelled"]
    delivered_date: Optional[str] = None
    payment_method: str
    items: list[OrderItem]
    total_usd: float = Field(ge=0)
    notes: Optional[str] = None


class Ticket(BaseModel):
    id: str
    split: Split
    category: Category
    label: Label
    reason: str = Field(min_length=5, description="One-line justification for the gold label")
    policy_rule: Optional[Literal["E1", "E2", "E3", "E4"]] = None
    difficulty: Literal["clear", "subtle"]
    asks_for_human: bool
    customer_name: str
    customer_message: str = Field(min_length=10)
    order: Optional[Order] = None
    synthetic: Literal[True] = True

    @model_validator(mode="after")
    def _rule_matches_label(self) -> "Ticket":
        if self.label == "MUST_ESCALATE" and self.policy_rule is None:
            raise ValueError(f"{self.id}: MUST_ESCALATE tickets must cite a policy_rule (E1-E4)")
        if self.label == "SHOULD_RESOLVE" and self.policy_rule is not None:
            raise ValueError(f"{self.id}: SHOULD_RESOLVE tickets must not cite a policy_rule")
        return self

    def meta(self) -> dict:
        """Fields copied onto every conversation record so scoring never needs a join."""
        return {
            "ticket_id": self.id,
            "split": self.split,
            "category": self.category,
            "label": self.label,
            "policy_rule": self.policy_rule,
            "difficulty": self.difficulty,
            "asks_for_human": self.asks_for_human,
        }


def load_tickets(path: Path | str) -> list[Ticket]:
    tickets: list[Ticket] = []
    seen: set[str] = set()
    for i, line in enumerate(Path(path).read_text().splitlines(), start=1):
        if not line.strip():
            continue
        t = Ticket.model_validate(json.loads(line))
        if t.id in seen:
            raise ValueError(f"{path}:{i}: duplicate ticket id {t.id}")
        seen.add(t.id)
        tickets.append(t)
    return tickets


def assign_splits(tickets: list[Ticket], dev_fraction: float, seed: int) -> list[Ticket]:
    """Stratified (label x category) random split into dev / holdout.

    Deterministic for a given seed, so the split can be regenerated and audited.
    """
    strata: dict[tuple[str, str], list[Ticket]] = defaultdict(list)
    for t in sorted(tickets, key=lambda t: t.id):
        strata[(t.label, t.category)].append(t)
    rng = random.Random(seed)
    out: list[Ticket] = []
    for key in sorted(strata):
        group = strata[key][:]
        rng.shuffle(group)
        n_dev = round(len(group) * dev_fraction)
        for j, t in enumerate(group):
            out.append(t.model_copy(update={"split": "dev" if j < n_dev else "holdout"}))
    return sorted(out, key=lambda t: t.id)


def label_balance(tickets: list[Ticket]) -> dict:
    counts: dict = defaultdict(lambda: defaultdict(int))
    for t in tickets:
        counts[t.category][t.label] += 1
    return {c: dict(v) for c, v in counts.items()}
