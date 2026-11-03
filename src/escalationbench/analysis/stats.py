"""Statistics. Plain-language notes on each method are in DECISIONS.md.

Unit of analysis is the TICKET. Repeated runs of a ticket estimate that ticket's
probability of an outcome; they are not independent observations.
"""
from __future__ import annotations

import math
import warnings

import numpy as np
import pandas as pd
from scipy import stats as st


# --------------------------------------------------------------------------- intervals
def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float, float]:
    """Wilson score interval. Returns (rate, low, high); NaNs when n == 0."""
    if n == 0:
        return (math.nan, math.nan, math.nan)
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return (p, max(0.0, centre - half), min(1.0, centre + half))


def rate_table(df: pd.DataFrame, outcome: str, by: list[str]) -> pd.DataFrame:
    rows = []
    d = df[df[outcome].notna()]
    for keys, g in d.groupby(by, sort=True):
        keys = keys if isinstance(keys, tuple) else (keys,)
        k, n = int(g[outcome].astype(bool).sum()), len(g)
        rate, lo, hi = wilson(k, n)
        rows.append({**dict(zip(by, keys)), "metric": outcome, "k": k, "n": n,
                     "n_tickets": g["ticket_id"].nunique(), "rate": rate, "ci_low": lo, "ci_high": hi})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- paired tests
def ticket_rates(df: pd.DataFrame, outcome: str, condition: str) -> pd.Series:
    d = df[(df["condition"] == condition) & df[outcome].notna()]
    return d.groupby("ticket_id")[outcome].apply(lambda s: s.astype(float).mean())


def paired_permutation(diffs: np.ndarray, n_perm: int = 20000, seed: int = 0) -> float:
    """Two-sided sign-flip permutation test on per-ticket differences (H0: mean diff = 0).
    Exact enumeration when there are <= 16 non-zero tickets."""
    diffs = np.asarray(diffs, dtype=float)
    nz = diffs[diffs != 0]
    if len(nz) == 0:
        return 1.0
    obs = abs(nz.mean())
    if len(nz) <= 16:
        signs = np.array(np.meshgrid(*[[-1, 1]] * len(nz))).reshape(len(nz), -1).T
        null = np.abs((signs * nz).mean(axis=1))
        return float(np.mean(null >= obs - 1e-12))
    rng = np.random.default_rng(seed)
    signs = rng.choice([-1.0, 1.0], size=(n_perm, len(nz)))
    null = np.abs((signs * nz).mean(axis=1))
    return float((np.sum(null >= obs - 1e-12) + 1) / (n_perm + 1))


def cluster_bootstrap_rd(diffs: np.ndarray, n_boot: int = 10000, seed: int = 0) -> tuple[float, float]:
    """95% percentile CI for the mean per-ticket risk difference, resampling tickets."""
    diffs = np.asarray(diffs, dtype=float)
    if len(diffs) == 0:
        return (math.nan, math.nan)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(diffs), size=(n_boot, len(diffs)))
    means = diffs[idx].mean(axis=1)
    return (float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5)))


def discordant_tickets(a: pd.Series, b: pd.Series) -> dict:
    """Tickets where the majority outcome differs between conditions (A>=0.5 vs B<0.5 and vice versa)."""
    j = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
    return {"a_only": int(((j.a >= 0.5) & (j.b < 0.5)).sum()), "b_only": int(((j.b >= 0.5) & (j.a < 0.5)).sum())}


# --------------------------------------------------------------------------- models
def has_separation(df: pd.DataFrame, outcome: str, conditions: list[str]) -> bool:
    d = df[df["condition"].isin(conditions) & df[outcome].notna()]
    rates = d.groupby("condition")[outcome].apply(lambda s: s.astype(float).mean())
    return bool(((rates == 0) | (rates == 1)).any()) or len(rates) < len(conditions)


def gee_logit(df: pd.DataFrame, outcome: str, cond_a: str, cond_b: str) -> dict:
    """Population-average logistic regression, robust SEs clustered by ticket.
    Returns OR for cond_a vs cond_b. Fails cleanly on separation."""
    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    d = df[df["condition"].isin([cond_a, cond_b]) & df[outcome].notna()].copy()
    if has_separation(d, outcome, [cond_a, cond_b]):
        return {"method": "GEE", "ok": False, "note": "separation (a condition has 0% or 100%); model not estimable"}
    d["y"] = d[outcome].astype(int)
    d["x"] = (d["condition"] == cond_a).astype(int)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            res = smf.gee("y ~ x", groups="ticket_id", data=d, family=sm.families.Binomial(),
                          cov_struct=sm.cov_struct.Exchangeable()).fit()
        b, se = float(res.params["x"]), float(res.bse["x"])
        return {"method": "GEE", "ok": True, "or": math.exp(b), "or_low": math.exp(b - 1.96 * se),
                "or_high": math.exp(b + 1.96 * se), "p": float(res.pvalues["x"])}
    except Exception as e:  # report, never hide
        return {"method": "GEE", "ok": False, "note": f"{type(e).__name__}: {e}"}


def mixed_logit(df: pd.DataFrame, outcome: str, cond_a: str, cond_b: str) -> dict:
    """Mixed-effects logistic regression with a random intercept per ticket
    (statsmodels BinomialBayesMixedGLM, variational Bayes). Reports posterior mean OR and 95% interval."""
    from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM

    d = df[df["condition"].isin([cond_a, cond_b]) & df[outcome].notna()].copy()
    if has_separation(d, outcome, [cond_a, cond_b]):
        return {"method": "mixed_VB", "ok": False, "note": "separation; model not estimable"}
    d["y"] = d[outcome].astype(int)
    d["x"] = (d["condition"] == cond_a).astype(int)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m = BinomialBayesMixedGLM.from_formula("y ~ x", {"ticket": "0 + C(ticket_id)"}, d)
            r = m.fit_vb()
        i = list(m.exog_names).index("x")
        b, sd = float(r.fe_mean[i]), float(r.fe_sd[i])
        return {"method": "mixed_VB", "ok": True, "or": math.exp(b), "or_low": math.exp(b - 1.96 * sd),
                "or_high": math.exp(b + 1.96 * sd)}
    except Exception as e:
        return {"method": "mixed_VB", "ok": False, "note": f"{type(e).__name__}: {e}"}


def holm(pvals: list[float]) -> list[float]:
    """Holm-Bonferroni adjusted p-values (NaNs passed through, excluded from m)."""
    p = np.asarray(pvals, dtype=float)
    ok = ~np.isnan(p)
    m = ok.sum()
    adj = np.full_like(p, np.nan)
    order = np.argsort(np.where(ok, p, np.inf))
    running = 0.0
    for rank, i in enumerate(order[:m]):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj.tolist()


def contrast(df: pd.DataFrame, outcome: str, cond_a: str, cond_b: str, seed: int = 0) -> dict:
    a, b = ticket_rates(df, outcome, cond_a), ticket_rates(df, outcome, cond_b)
    j = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
    diffs = (j.a - j.b).to_numpy()
    lo, hi = cluster_bootstrap_rd(diffs, seed=seed)
    gee = gee_logit(df, outcome, cond_a, cond_b)
    mixed = mixed_logit(df, outcome, cond_a, cond_b)
    return {
        "metric": outcome, "a": cond_a, "b": cond_b, "n_tickets": len(j),
        "rate_a": float(j.a.mean()) if len(j) else math.nan, "rate_b": float(j.b.mean()) if len(j) else math.nan,
        "risk_diff": float(diffs.mean()) if len(diffs) else math.nan, "rd_ci_low": lo, "rd_ci_high": hi,
        "p_perm": paired_permutation(diffs, seed=seed),
        **{f"gee_{k}": v for k, v in gee.items() if k != "method"},
        **{f"mixed_{k}": v for k, v in mixed.items() if k != "method"},
        **discordant_tickets(a, b),
    }


# --------------------------------------------------------------------------- agreement
def cohens_kappa(x: list[bool], y: list[bool]) -> float:
    x, y = np.asarray(x, dtype=int), np.asarray(y, dtype=int)
    if len(x) == 0:
        return math.nan
    po = float(np.mean(x == y))
    pe = float(np.mean(x) * np.mean(y) + (1 - np.mean(x)) * (1 - np.mean(y)))
    if pe == 1.0:
        return math.nan  # both raters constant and identical: kappa undefined
    return (po - pe) / (1 - pe)


def kappa_bootstrap(x: list[bool], y: list[bool], n_boot: int = 5000, seed: int = 0) -> tuple[float, float]:
    x, y = np.asarray(x, dtype=int), np.asarray(y, dtype=int)
    rng = np.random.default_rng(seed)
    ks = []
    for _ in range(n_boot):
        i = rng.integers(0, len(x), len(x))
        k = cohens_kappa(x[i].tolist(), y[i].tolist())
        if not math.isnan(k):
            ks.append(k)
    if not ks:
        return (math.nan, math.nan)
    return (float(np.percentile(ks, 2.5)), float(np.percentile(ks, 97.5)))


def mde_two_proportions(p0: float, n_tickets: int, alpha: float = 0.05, power: float = 0.8) -> float:
    """Rough minimum detectable increase for a ticket-level paired design (normal approx,
    assumes ticket-level SD of differences ~ sqrt(2 p (1-p))). Replaced by simulation in Phase 4."""
    za, zb = st.norm.ppf(1 - alpha / 2), st.norm.ppf(power)
    sd = math.sqrt(2 * p0 * (1 - p0)) if 0 < p0 < 1 else 0.3
    return (za + zb) * sd / math.sqrt(n_tickets)
