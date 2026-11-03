"""Statistics against known reference values."""
import math

import numpy as np
import pandas as pd
import pytest

from escalationbench.analysis.stats import (
    cohens_kappa, contrast, has_separation, holm, paired_permutation, wilson,
)


def test_wilson_reference_values():
    # Reference: Newcombe (1998) / statsmodels proportion_confint(method="wilson")
    from statsmodels.stats.proportion import proportion_confint
    for k, n in [(0, 10), (1, 10), (5, 10), (10, 10), (81, 263)]:
        _, lo, hi = wilson(k, n)
        rlo, rhi = proportion_confint(k, n, method="wilson")
        assert lo == pytest.approx(rlo, abs=1e-9) and hi == pytest.approx(rhi, abs=1e-9)


def test_wilson_empty():
    assert all(math.isnan(v) for v in wilson(0, 0))


def test_kappa_reference():
    # Classic textbook 2x2: a=20 both yes, b=5, c=10, d=15  -> po=0.70, pe=0.50, kappa=0.40
    x = [1] * 20 + [1] * 5 + [0] * 10 + [0] * 15
    y = [1] * 20 + [0] * 5 + [1] * 10 + [0] * 15
    assert cohens_kappa(x, y) == pytest.approx(0.4)


def test_kappa_matches_statsmodels():
    from statsmodels.stats.inter_rater import cohens_kappa as sm_kappa
    rng = np.random.default_rng(1)
    x = rng.integers(0, 2, 200)
    y = np.where(rng.random(200) < 0.8, x, 1 - x)
    table = np.array([[np.sum((x == i) & (y == j)) for j in (0, 1)] for i in (0, 1)])
    assert cohens_kappa(x.tolist(), y.tolist()) == pytest.approx(sm_kappa(table).kappa)


def test_kappa_undefined_when_constant():
    assert math.isnan(cohens_kappa([0, 0, 0], [0, 0, 0]))


def test_holm_reference():
    # Holm (1979) example-style: sorted p * (m - rank), monotone
    adj = holm([0.01, 0.04, 0.03, 0.005])
    assert adj == pytest.approx([0.03, 0.06, 0.06, 0.02])
    assert math.isnan(holm([0.01, float("nan")])[1])


def test_permutation_exact_small():
    # 5 tickets all +1: exact two-sided p = 2/32
    assert paired_permutation(np.ones(5)) == pytest.approx(2 / 32)
    assert paired_permutation(np.zeros(5)) == 1.0


def _synthetic(p_a, p_b, n_tickets=60, reps=5, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for t in range(n_tickets):
        base = rng.normal(0, 1)
        for cond, p in (("A", p_a), ("B", p_b)):
            pt = 1 / (1 + math.exp(-(math.log(p / (1 - p)) + base)))
            for r in range(reps):
                rows.append({"ticket_id": f"t{t}", "condition": cond, "y": bool(rng.random() < pt)})
    return pd.DataFrame(rows)


def test_contrast_detects_real_effect_and_not_null():
    eff = contrast(_synthetic(0.4, 0.1), "y", "A", "B")
    assert eff["risk_diff"] > 0.15 and eff["p_perm"] < 0.01 and eff["gee_ok"] and eff["gee_or"] > 1
    null = contrast(_synthetic(0.2, 0.2, seed=3), "y", "A", "B")
    assert null["p_perm"] > 0.01


def test_separation_detected():
    df = pd.DataFrame({"ticket_id": ["a", "b", "a", "b"], "condition": ["A", "A", "B", "B"], "y": [0, 0, 1, 0]})
    assert has_separation(df, "y", ["A", "B"])
    r = contrast(df, "y", "A", "B")
    assert r["gee_ok"] is False and "separation" in r["gee_note"]
