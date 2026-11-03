"""Regenerate every table and figure from raw run data. Nothing here is hand-entered.

Outputs go to results/<run_id>/ :
  scored.csv                         one row per conversation (rule + judge columns)
  tables/status_counts.csv           every outcome code, including failures
  tables/rates.csv                   all rates with Wilson 95% CIs
  tables/confirmatory_contrasts.csv  ONLY the family listed in config/analysis_plan.yaml, Holm-adjusted
  tables/exploratory/*.csv           everything else, labelled exploratory
  tables/judge_agreement.csv         kappa vs human labels (if labels exist)
  figures/*.png
  REPORT.md                          generated summary of the above (numbers only, no conclusions)
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from ..config import CONFIG_DIR, REPO_ROOT  # noqa: E402
from ..rawlog import RunStore  # noqa: E402
from ..scoring.rules import score_conversation  # noqa: E402
from .kappa import agreement_table  # noqa: E402
from .stats import contrast, holm, rate_table  # noqa: E402

RESULTS_DIR = REPO_ROOT / "results"
COND_ORDER = ["NEUTRAL", "PLACEBO", "SOFT_KPI", "HARD_KPI"]
INK, MUTED, GRID = "#1f2a37", "#6b7280", "#e5e7eb"
POINT = "#2f5d9e"


def load_analysis_plan(path: Path = CONFIG_DIR / "analysis_plan.yaml") -> dict:
    return yaml.safe_load(path.read_text())


def build_scored(store: RunStore, splits: list[str] | None = None) -> pd.DataFrame:
    judgments = store.judgments()
    rows = [score_conversation(c, judgments.get(c["cell_id"])) for c in store.conversations()]
    df = pd.DataFrame(rows)
    if splits and len(df):
        df = df[df["split"].isin(splits)]
    return df


def _metric_frames(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Each metric with its correct denominator."""
    done = df[df["status"] == "COMPLETED"]
    must_missed = done[(done["label"] == "MUST_ESCALATE") & (done["missed_escalation"] == True)]  # noqa: E712
    return {
        # escalation metrics use ALL conversations except API errors: a refusal or turn-cap
        # without an escalation call is still a missed escalation from the customer's view.
        "missed_escalation": df[(df["label"] == "MUST_ESCALATE") & (df["status"] != "API_ERROR")],
        "unnecessary_escalation": df[(df["label"] == "SHOULD_RESOLVE") & (df["status"] != "API_ERROR")],
        "any_false_claim_rule": done,
        "any_false_claim_judge": done[done["any_false_claim_judge"].notna()],
        "false_escalation_claim_rule": done,
        "false_escalation_claim_judge": done[done["false_escalation_claim_judge"].notna()],
        # disclosure matters most when a MUST_ESCALATE ticket was NOT escalated
        "disclosure_given_miss_rule": must_missed,
        "disclosure_given_miss_judge": must_missed[must_missed["disclosure_judge"].notna()],
        "eval_awareness_rule": df[df["status"] != "API_ERROR"],
    }


_COLUMN = {
    "disclosure_given_miss_rule": "disclosure_rule",
    "disclosure_given_miss_judge": "disclosure_judge",
}


def all_rates(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for metric, frame in _metric_frames(df).items():
        if frame.empty:
            continue
        col = _COLUMN.get(metric, metric)
        t = rate_table(frame, col, ["model", "condition"])
        if not t.empty:
            t["metric"] = metric
            out.append(t)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def confirmatory(df: pd.DataFrame, plan: dict) -> pd.DataFrame:
    frames = _metric_frames(df)
    rows = []
    for spec in plan["primary_family"]:
        metric = spec["metric"]
        col = _COLUMN.get(metric, metric)
        for model in sorted(df["model"].unique()):
            f = frames[metric]
            f = f[f["model"] == model]
            if f.empty or f[col].notna().sum() == 0:
                continue
            for a, b in spec["contrasts"]:
                r = contrast(f, col, a, b, seed=plan.get("seed", 0))
                rows.append({"model": model, **r, "metric": metric})
    t = pd.DataFrame(rows)
    if not t.empty:
        t["p_perm_holm"] = holm(t["p_perm"].tolist())
    return t


def exploratory(df: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = _metric_frames(df)
    for by in (["model", "condition", "category"], ["model", "condition", "difficulty"],
               ["model", "condition", "asks_for_human"], ["model", "condition", "policy_rule"]):
        parts = []
        for metric in ("missed_escalation", "unnecessary_escalation", "any_false_claim_rule"):
            f = frames[metric]
            if not f.empty:
                parts.append(rate_table(f, _COLUMN.get(metric, metric), by))
        if parts:
            pd.concat(parts).to_csv(out_dir / f"rates_by_{by[-1]}.csv", index=False)
    # rule vs judge agreement on claims (no human labels needed)
    d = df[df["any_false_claim_judge"].notna()]
    if not d.empty:
        cross = pd.crosstab(d["any_false_claim_rule"], d["any_false_claim_judge"], rownames=["rule"], colnames=["judge"])
        cross.to_csv(out_dir / "rule_vs_judge_false_claim.csv")


def plot_rates(rates: pd.DataFrame, metrics: list[str], path: Path, watermark: str | None) -> None:
    rates = rates[rates["metric"].isin(metrics)]
    if rates.empty:
        return
    models = sorted(rates["model"].unique())
    fig, axes = plt.subplots(len(metrics), len(models), figsize=(4.2 * len(models), 2.8 * len(metrics)),
                             squeeze=False, sharey="row")
    for i, metric in enumerate(metrics):
        for j, model in enumerate(models):
            ax = axes[i][j]
            r = rates[(rates.metric == metric) & (rates.model == model)].set_index("condition")
            conds = [c for c in COND_ORDER if c in r.index]
            xs = range(len(conds))
            y = [r.loc[c, "rate"] for c in conds]
            lo = [max(0.0, r.loc[c, "rate"] - r.loc[c, "ci_low"]) for c in conds]
            hi = [max(0.0, r.loc[c, "ci_high"] - r.loc[c, "rate"]) for c in conds]
            ax.errorbar(xs, y, yerr=[lo, hi], fmt="o", color=POINT, ecolor=POINT, elinewidth=2, capsize=0, markersize=8)
            for x, c in zip(xs, conds):
                ax.annotate(f"{int(r.loc[c,'k'])}/{int(r.loc[c,'n'])}", (x, r.loc[c, "ci_high"]),
                            textcoords="offset points", xytext=(0, 4), ha="center", fontsize=7, color=MUTED)
            ax.set_xticks(list(xs), conds, fontsize=8, color=INK)
            ax.set_ylim(0, 1.08)
            ax.grid(axis="y", color=GRID, linewidth=0.8)
            ax.set_axisbelow(True)
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            for s in ("left", "bottom"):
                ax.spines[s].set_color(GRID)
            ax.tick_params(colors=MUTED, labelsize=8)
            if i == 0:
                ax.set_title(model, fontsize=10, color=INK)
            if j == 0:
                ax.set_ylabel(metric.replace("_", " "), fontsize=8, color=INK)
    fig.suptitle("Rates by condition (points) with Wilson 95% CIs; labels show k/n runs", fontsize=9, color=MUTED)
    if watermark:
        fig.text(0.5, 0.5, watermark, fontsize=48, color="#d1d5db", ha="center", va="center", rotation=25, alpha=0.6, zorder=0)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def _md_table(df: pd.DataFrame, cols: list[str]) -> str:
    if df.empty:
        return "_none_\n"
    d = df[cols].copy()
    for c in d.columns:
        if d[c].dtype.kind == "f":
            d[c] = d[c].map(lambda v: "" if pd.isna(v) else f"{v:.3f}")
    head = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n"
    return head + "".join("| " + " | ".join(str(v) for v in row) + " |\n" for row in d.itertuples(index=False))


def generate(run_id: str, splits: list[str] | None = None, labels_dir: Path | None = None) -> Path:
    store = RunStore(run_id)
    mock = store.is_dry_run()
    out = RESULTS_DIR / "dryrun" / run_id if mock else RESULTS_DIR / run_id
    tables, figs = out / "tables", out / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    watermark = "MOCK DATA" if mock else None

    df = build_scored(store, splits)
    df.to_csv(out / "scored.csv", index=False)
    status = df.groupby(["model", "condition", "status"]).size().rename("n").reset_index() if len(df) else pd.DataFrame()
    status.to_csv(tables / "status_counts.csv", index=False)

    rates = all_rates(df)
    rates.to_csv(tables / "rates.csv", index=False)
    plan = load_analysis_plan()
    conf = confirmatory(df, plan) if len(df) else pd.DataFrame()
    conf.to_csv(tables / "confirmatory_contrasts.csv", index=False)
    exploratory(df, tables / "exploratory")

    agree = pd.DataFrame()
    labels_dir = labels_dir or out / "labels"
    if (labels_dir / "human_labels_DONE.csv").exists():
        agree = agreement_table(labels_dir / "human_labels_DONE.csv", labels_dir / "human_labels_key.csv", store.judgments())
        agree.to_csv(tables / "judge_agreement.csv", index=False)

    plot_rates(rates, ["missed_escalation", "unnecessary_escalation"], figs / "escalation_rates.png", watermark)
    plot_rates(rates, ["any_false_claim_rule", "any_false_claim_judge", "disclosure_given_miss_judge"],
               figs / "claims_disclosure_rates.png", watermark)

    md = [f"# Results: `{run_id}`\n"]
    if mock:
        md.append("> **MOCK DATA.** Generated by the dry-run mock client to test the pipeline. These are NOT results.\n")
    md.append(f"Generated from `runs/{run_id}/` by `ebench report`. Do not edit by hand.\n")
    md.append(f"Analysis plan: `config/analysis_plan.yaml` (status: **{plan.get('status')}**).\n")
    md.append("\n## Outcome status counts (nothing is dropped)\n")
    md.append(_md_table(status, ["model", "condition", "status", "n"]) if len(status) else "_none_\n")
    md.append("\n## Rates with Wilson 95% CIs\n")
    md.append(_md_table(rates, ["metric", "model", "condition", "k", "n", "n_tickets", "rate", "ci_low", "ci_high"]) if len(rates) else "_none_\n")
    md.append("\n## Confirmatory contrasts (preregistered family only; Holm-adjusted)\n")
    md.append("Risk difference = mean over tickets of (rate in A − rate in B); CI by ticket bootstrap; "
              "p from paired sign-flip permutation; OR from GEE clustered by ticket and from a Bayesian mixed model.\n\n")
    if len(conf):
        md.append(_md_table(conf, ["model", "metric", "a", "b", "n_tickets", "rate_a", "rate_b", "risk_diff",
                                   "rd_ci_low", "rd_ci_high", "p_perm", "p_perm_holm"]))
        notes = conf[[c for c in conf.columns if c.endswith("_note")]].dropna(how="all")
        if len(notes):
            md.append("\nModel notes (e.g. separation):\n\n" + _md_table(conf.loc[notes.index], ["model", "metric", "a", "b"] + list(notes.columns)))
    else:
        md.append("_none_\n")
    if len(agree):
        md.append("\n## Judge vs human agreement\n")
        md.append(_md_table(agree, ["sample_set", "field", "n_labeled", "human_positive", "judge_positive", "raw_agreement", "kappa", "kappa_ci_low", "kappa_ci_high"]))
    md.append("\n## Exploratory\nSee `tables/exploratory/`. Not preregistered; treat as hypothesis-generating.\n")
    md.append("\n## Conclusions\n_Left for the author to write._\n")
    (out / "REPORT.md").write_text("".join(md))
    (out / "provenance.json").write_text(json.dumps({"run_id": run_id, "splits": splits, "mock": mock,
                                                       "manifest": store.manifest()}, indent=2, default=str))
    return out
