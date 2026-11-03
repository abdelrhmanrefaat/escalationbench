"""Pricing, pre-run cost estimates, and the hard budget guard."""
from __future__ import annotations

import threading
from dataclasses import dataclass
from pathlib import Path

import yaml

from .config import CONFIG_DIR


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class Pricing:
    as_of: str
    models: dict[str, dict[str, float]]

    @classmethod
    def load(cls, path: Path | str = CONFIG_DIR / "pricing.yaml") -> "Pricing":
        raw = yaml.safe_load(Path(path).read_text())
        return cls(as_of=str(raw["as_of"]), models=raw["models"])

    def rates(self, model: str) -> dict[str, float]:
        if model not in self.models:
            raise KeyError(f"No pricing for model {model!r}; add it to config/pricing.yaml")
        return self.models[model]

    def cost(self, model: str, usage: dict | None) -> float:
        """Exact cost of one call from the API's own `usage` numbers. Thinking tokens are billed as output."""
        if not usage:
            return 0.0
        r = self.rates(model)
        return (
            (usage.get("input_tokens") or 0) * r["input"]
            + (usage.get("output_tokens") or 0) * r["output"]
            + (usage.get("cache_creation_input_tokens") or 0) * r["cache_write"]
            + (usage.get("cache_read_input_tokens") or 0) * r["cache_read"]
        ) / 1_000_000


@dataclass
class ConversationAssumptions:
    """Used only for the pre-run estimate. Phase 4 replaces these with pilot measurements."""

    calls_per_conversation: float = 3.0
    growth_tokens_per_call: int = 600   # tool results + previous assistant turn added each call
    output_tokens_per_call: int = 700   # visible text + thinking + tool_use
    safety_margin: float = 1.3


def estimate_conversation_cost(
    pricing: Pricing, model: str, first_call_input_tokens: int, a: ConversationAssumptions
) -> float:
    r = pricing.rates(model)
    n = a.calls_per_conversation
    # sum over calls of (first + growth * i) for i = 0..n-1; no caching assumed (conservative)
    total_in = n * first_call_input_tokens + a.growth_tokens_per_call * n * (n - 1) / 2
    total_out = n * a.output_tokens_per_call
    return (total_in * r["input"] + total_out * r["output"]) / 1_000_000


def estimate_judge_cost(pricing: Pricing, model: str, n_items: int, in_tokens: int = 900, out_tokens: int = 500) -> float:
    r = pricing.rates(model)
    return n_items * (in_tokens * r["input"] + out_tokens * r["output"]) / 1_000_000


class BudgetGuard:
    """Thread-safe hard cap. Each call reserves a pessimistic amount before it is sent;
    the reservation is swapped for the real cost afterwards. Nothing is sent that could
    push committed + in-flight spend over the cap."""

    def __init__(self, max_usd: float, already_spent: float = 0.0):
        self.max_usd = float(max_usd)
        self.spent = float(already_spent)
        self.reserved = 0.0
        self._lock = threading.Lock()

    def reserve(self, amount: float) -> None:
        with self._lock:
            if self.spent + self.reserved + amount > self.max_usd:
                raise BudgetExceeded(
                    f"Budget cap ${self.max_usd:.2f} reached "
                    f"(spent ${self.spent:.4f}, in flight ${self.reserved:.4f}, next call up to ${amount:.4f})"
                )
            self.reserved += amount

    def commit(self, reserved: float, actual: float) -> None:
        with self._lock:
            self.reserved -= reserved
            self.spent += actual

    @property
    def remaining(self) -> float:
        with self._lock:
            return self.max_usd - self.spent - self.reserved
