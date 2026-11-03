"""Pilot power check (run BEFORE the full run; see the revised plan).

1. Floor check: if a metric is near zero in every condition for a model, say so plainly.
   The plan forbids making scenarios more extreme to manufacture an effect, so a floor is
   reported to the author as a finding, not "fixed".
2. Simulated power for the planned full run, per model: resample tickets (with replacement)
   from the pilot's baseline condition to get per-ticket probabilities p_t, add an absolute
   effect delta to every ticket (clipped to [0, 1]), draw `repeats` runs per ticket per arm,
   and apply the same paired sign-flip permutation test the confirmatory analysis uses, at a
   Bonferroni-adjusted alpha (a conservative stand-in for Holm across the primary family).

The pilot uses dev tickets only; it says nothing about holdout results.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

FLOOR_RATE = 0.02


def floor_check(df: pd.DataFrame, col: str, floor: float = FLOOR_RATE) -> pd.DataFrame:
    rows = []
    for model, g in df.groupby("model"):
        by_cond = g.groupby("condition")[col].agg(["sum", "count"])
        rates = (by_cond["sum"] / by_cond["count"]).to_dict()
        rows.append({"model": model, "metric": col, **{f"rate_{c}": r for c, r in rates.items()},
                     "n_runs": int(by_cond["count"].sum()),
                     "floor_all_conditions": bool(len(rates)) and max(rates.values()) < floor})
    return pd.DataFrame(rows)


def _perm_pvalues(diffs: np.ndarray, n_perm: int, rng: np.random.Generator) -> np.ndarray:
    """diffs: (sims, tickets). Two-sided sign-flip permutation p-value for each simulation."""
    sims, n = diffs.shape
    obs = np.abs(diffs.mean(axis=1))
    signs = rng.choice([-1.0, 1.0], size=(n_perm, n))
    null = np.abs(diffs @ signs.T / n)                      # (sims, n_perm)
    return (1 + (null >= obs[:, None] - 1e-12).sum(axis=1)) / (n_perm + 1)


def simulate_power(p_ticket: np.ndarray, n_tickets: int, repeats: int, delta: float, alpha: float,
                   sims: int = 400, n_perm: int = 999, seed: int = 0) -> float:
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(p_ticket), size=(sims, n_tickets))
    p0 = p_ticket[idx]
    p1 = np.clip(p0 + delta, 0.0, 1.0)
    y0 = rng.binomial(repeats, p0) / repeats
    y1 = rng.binomial(repeats, p1) / repeats
    p = _perm_pvalues(y1 - y0, n_perm, rng)
    return float((p < alpha).mean())


def power_table(df: pd.DataFrame, col: str, baseline: str, n_tickets: int, repeats: int, n_tests: int,
                deltas=(0.05, 0.10, 0.15, 0.20, 0.30), alpha: float = 0.05, seed: int = 0) -> pd.DataFrame:
    rows = []
    alpha_adj = alpha / max(1, n_tests)
    for model, g in df[df["condition"] == baseline].groupby("model"):
        p_ticket = g.groupby("ticket_id")[col].mean().to_numpy(dtype=float)
        if len(p_ticket) == 0:
            continue
        for d in deltas:
            rows.append({"model": model, "metric": col, "baseline": baseline,
                         "baseline_rate": float(p_ticket.mean()), "pilot_tickets": len(p_ticket),
                         "n_tickets": n_tickets, "repeats": repeats, "alpha_adj": alpha_adj, "delta": d,
                         "power": simulate_power(p_ticket, n_tickets, repeats, d, alpha_adj, seed=seed)})
    return pd.DataFrame(rows)
