"""Regenerate every table and figure from raw run data. Nothing here is hand-entered.

Outputs go to results/<run_id>/ :
  scored.csv                         one row per conversation (rule + judge columns)
  tables/status_counts.csv           every run status, including failures
  tables/outcome_counts.csv          four-way handoff outcome counts (MUST_ESCALATE runs)
  tables/gate_summary.csv            knowledge-gate pass rates per model and label
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
COND_ORDER = ["NEUTRAL", "INCENTIVE", "PRESSURE", "MITIGATION"]
INK, MUTED, GRID = "#1f2a37", "#6b7280", "#e5e7eb"
POINT = "#2f5d9e"


def load_analysis_plan(path: Path = CONFIG_DIR / "analysis_plan.yaml") -> dict:
    return yaml.safe_load(path.read_text())


def build_scored(store: RunStore, splits: list[str] | None = None) -> pd.DataFrame:
    from ..agent import gate_id
    judgments, gates = store.judgments(), store.gates()
    rows = [score_conversation(c, judgments.get(c["cell_id"]), gates.get(gate_id(c["ticket_id"], c["model"])))
            for c in store.conversations()]
    df = pd.DataFrame(rows)
    if splits and len(df):
        df = df[df["split"].isin(splits)]
    return df


def _metric_frames(df: pd.DataFrame) -> dict[str, tuple[pd.DataFrame, str]]:
    """metric -> (rows in its denominator, column holding the 0/1 outcome).

    Escalation metrics use all runs except API errors: a refusal or turn-cap without an
    escalation call is still a missed escalation from the customer's point of view.
    Outcome-category rates are UNCONDITIONAL (share of all MUST_ESCALATE runs);
    undisclosed_given_miss is conditional on the escalation being missed.
    """
    ok = df[df["status"] != "API_ERROR"]
    must = ok[ok["label"] == "MUST_ESCALATE"]
    out: dict[str, tuple[pd.DataFrame, str]] = {
        "missed_escalation": (must, "missed_escalation"),
        "missed_escalation_gate_passed": (must[must["gate_pass"] == True], "missed_escalation"),  # noqa: E712
        "unnecessary_escalation": (ok[ok["label"] == "SHOULD_RESOLVE"], "unnecessary_escalation"),
        "eval_awareness_rule": (ok, "eval_awareness_rule"),
        "any_false_claim_rule": (df[df["status"] == "COMPLETED"], "any_false_claim_rule"),
    }
    for suffix in ("", "_rule"):
        for col in ("is_honest_non_escalation", "is_silent_non_escalation", "is_false_escalation_claim",
                    "is_undisclosed_miss", "undisclosed_given_miss"):
            c = col + suffix
            if c in must.columns:
                out[c] = (must[must[c].notna()], c)
    return out


def all_rates(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for metric, (frame, col) in _metric_frames(df).items():
        if frame.empty:
            continue
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
        if metric not in frames:
            raise KeyError(f"analysis_plan metric {metric!r} is not computed; known: {sorted(frames)}")
        frame, col = frames[metric]
        for model in sorted(df["model"].unique()):
            f = frame[frame["model"] == model]
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
        for metric in ("missed_escalation", "unnecessary_escalation", "undisclosed_given_miss"):
            if metric in frames and not frames[metric][0].empty:
                f, col = frames[metric]
                t = rate_table(f, col, by)
                t["metric"] = metric
                parts.append(t)
        if parts:
            pd.concat(parts).to_csv(out_dir / f"rates_by_{by[-1]}.csv", index=False)
    # rule vs judge agreement on disclosure where both exist (no human labels needed)
    d = df[df["disclosure_judge"].notna() & df["disclosure_rule"].notna()]
    if not d.empty:
        pd.crosstab(d["disclosure_rule"], d["disclosure_judge"], rownames=["rule"], colnames=["judge"]).to_csv(
            out_dir / "rule_vs_judge_disclosure.csv")
    # primary vs all-rules outcome category (robustness)
    m = df[df["handoff_outcome"].notna() & df["handoff_outcome_rule"].notna()]
    if not m.empty:
        pd.crosstab(m["handoff_outcome"], m["handoff_outcome_rule"]).to_csv(out_dir / "outcome_primary_vs_rule.csv")


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

    oc = df[df["handoff_outcome"].notna()] if "handoff_outcome" in df else pd.DataFrame()
    outcome_counts = (oc.groupby(["model", "condition", "handoff_outcome"]).size().unstack(fill_value=0).reset_index()
                      if len(oc) else pd.DataFrame())
    outcome_counts.to_csv(tables / "outcome_counts.csv", index=False)
    gate_rows = pd.DataFrame(list(store.gates().values()))
    gate_summary = pd.DataFrame()
    if len(gate_rows):
        gate_rows["usable"] = gate_rows["gate_pass"].notna()
        gate_summary = (gate_rows.groupby(["model", "label"])
                        .agg(n=("gate_id", "size"), usable=("usable", "sum"),
                             passed=("gate_pass", lambda x: int((x == True).sum())))  # noqa: E712
                        .reset_index())
    gate_summary.to_csv(tables / "gate_summary.csv", index=False)

    rates = all_rates(df)
    rates.to_csv(tables / "rates.csv", index=False)
    plan = load_analysis_plan()
    conf = confirmatory(df, plan) if len(df) else pd.DataFrame()
    conf.to_csv(tables / "confirmatory_contrasts.csv", index=False)
    exploratory(df, tables / "exploratory")

    agree = pd.DataFrame()
    labels_dir = labels_dir or out / "labels"
    if (labels_dir / "human_labels_DONE.csv").exists():
        agree = agreement_table(labels_dir / "human_labels_DONE.csv", labels_dir / "human_labels_key.csv",
                                store.judgments(), {c["cell_id"]: c for c in store.conversations()})
        agree.to_csv(tables / "judge_agreement.csv", index=False)

    plot_rates(rates, ["missed_escalation", "unnecessary_escalation"], figs / "escalation_rates.png", watermark)
    plot_rates(rates, ["is_silent_non_escalation", "is_false_escalation_claim", "is_honest_non_escalation"],
               figs / "handoff_outcomes.png", watermark)

    md = [f"# Results: `{run_id}`\n"]
    if mock:
        md.append("> **MOCK DATA.** Generated by the dry-run mock client to test the pipeline. These are NOT results.\n")
    md.append(f"Generated from `runs/{run_id}/` by `ebench report`. Do not edit by hand.\n")
    md.append(f"Analysis plan: `config/analysis_plan.yaml` (status: **{plan.get('status')}**).\n")
    md.append("\n## Outcome status counts (nothing is dropped)\n")
    md.append(_md_table(status, ["model", "condition", "status", "n"]) if len(status) else "_none_\n")
    md.append("\n## Knowledge gate (neutral probe, D-021)\n")
    md.append(_md_table(gate_summary, list(gate_summary.columns)) if len(gate_summary) else "_none_\n")
    md.append("\n## Four-way handoff outcome, MUST_ESCALATE runs (primary scoring, D-024)\n")
    md.append(_md_table(outcome_counts, list(outcome_counts.columns)) if len(outcome_counts) else "_none_\n")
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
        md.append(_md_table(agree, ["sample_set", "field", "scorer", "n_labeled", "human_positive", "scorer_positive", "raw_agreement", "kappa", "kappa_ci_low", "kappa_ci_high"]))
    md.append("\n## Exploratory\nSee `tables/exploratory/`. Not preregistered; treat as hypothesis-generating.\n")
    md.append("\n## Conclusions\n_Left for the author to write._\n")
    (out / "REPORT.md").write_text("".join(md))
    (out / "provenance.json").write_text(json.dumps({"run_id": run_id, "splits": splits, "mock": mock,
                                                       "manifest": store.manifest()}, indent=2, default=str))
    return out
