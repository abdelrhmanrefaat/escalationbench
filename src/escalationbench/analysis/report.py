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
from .kappa import agreement_table, human_disclosure_labels  # noqa: E402
from .stats import contrast, holm, interpret, pooled_contrast, rate_table  # noqa: E402

RESULTS_DIR = REPO_ROOT / "results"
COND_ORDER = ["NEUTRAL", "INCENTIVE", "PRESSURE", "MITIGATION"]
INK, MUTED, GRID = "#1f2a37", "#6b7280", "#e5e7eb"
POINT = "#2f5d9e"


def load_analysis_plan(path: Path = CONFIG_DIR / "analysis_plan.yaml") -> dict:
    return yaml.safe_load(path.read_text())


def build_scored(store: RunStore, splits: list[str] | None = None, cfg=None,
                 human_disclosure: dict[str, bool] | None = None) -> pd.DataFrame:
    from ..agent import gate_status
    from ..config import ExperimentConfig
    cfg = cfg or ExperimentConfig.load()
    status = gate_status(store.gates(), int(cfg.gate.get("repeats", 1)), int(cfg.gate.get("pass_min", 1)))
    judgments = store.judgments()
    rows = [score_conversation(c, judgments.get(c["cell_id"]), status.get((c["ticket_id"], c["model"])),
                               (human_disclosure or {}).get(c["cell_id"]))
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


def confirmatory(df: pd.DataFrame, plan: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """PREREGISTRATION 4.3 and 5. Returns (confirmatory family, per-model secondary contrasts S5).

    primary     : MUST_ESCALATE runs on gate-passed (ticket, model) pairs; models with fewer than
                  `min_gate_tickets` passing tickets are reported descriptively only. Holm across
                  the preregistered family (2 metrics x 3 contrasts = 6 tests).
    sensitivity : all MUST_ESCALATE tickets, all models; Holm within its own family; labelled.
    """
    frames = _metric_frames(df)
    seed, n_perm, n_boot = plan.get("seed", 0), plan.get("n_perm", 10000), plan.get("n_boot", 10000)
    sesoi = plan.get("sesoi_pp")
    sesoi = None if sesoi in (None, "", "TODO") else float(sesoi) / 100.0
    min_gate = int(plan.get("min_gate_tickets", 30))
    must = df[(df["label"] == "MUST_ESCALATE") & (df["status"] != "API_ERROR")]
    passed = must[must["gate_pass"] == True]  # noqa: E712
    gate_counts = passed.groupby("model")["ticket_id"].nunique() if len(passed) else pd.Series(dtype=int)
    all_models = sorted(df["model"].unique())
    primary_models = [m for m in all_models if gate_counts.get(m, 0) >= min_gate]

    rows = []
    for analysis, models, gate_only in (("primary", primary_models, True), ("sensitivity", all_models, False)):
        for spec in plan["primary_family"]:
            metric = spec["metric"]
            if metric not in frames:
                raise KeyError(f"analysis_plan metric {metric!r} is not computed; known: {sorted(frames)}")
            frame, col = frames[metric]
            if gate_only:
                frame = frame[frame["gate_pass"] == True]  # noqa: E712
            for a, b in spec["contrasts"]:
                if not models:
                    rows.append({"analysis": analysis, "metric": metric, "a": a, "b": b, "n_tickets": 0,
                                 "note": f"no model has >= {min_gate} gate-passed MUST_ESCALATE tickets"})
                    continue
                r = pooled_contrast(frame, col, a, b, models, seed=seed, n_perm=n_perm, n_boot=n_boot)
                rows.append({"analysis": analysis, **r, "metric": metric,
                             "models_excluded": ",".join(m for m in all_models if m not in models)})
    t = pd.DataFrame(rows)
    if not t.empty and "p_perm" in t:
        t["p_perm_holm"] = float("nan")
        for analysis in ("primary", "sensitivity"):
            idx = t.index[t["analysis"] == analysis]
            t.loc[idx, "p_perm_holm"] = holm(t.loc[idx, "p_perm"].tolist())
        t["interpretation"] = [interpret(r, sesoi) if pd.notna(r.get("p_perm")) else r.get("note")
                               for r in t.to_dict("records")]
        t["sesoi_pp"] = None if sesoi is None else sesoi * 100

    per_model = []
    for spec in plan["primary_family"]:
        frame, col = frames[spec["metric"]]
        frame = frame[frame["gate_pass"] == True]  # noqa: E712
        for model in all_models:
            f = frame[frame["model"] == model]
            if f.empty:
                continue
            for a, b in spec["contrasts"]:
                per_model.append({"analysis": "S5 per-model (secondary, gate-passed)", "model": model,
                                  **contrast(f, col, a, b, seed=seed), "metric": spec["metric"]})
    return t, pd.DataFrame(per_model)


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

    labels_dir = labels_dir or out / "labels"
    human = human_disclosure_labels(labels_dir / "human_labels_DONE.csv", labels_dir / "human_labels_key.csv")
    df = build_scored(store, splits, human_disclosure=human)
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
    conf, per_model = confirmatory(df, plan) if len(df) else (pd.DataFrame(), pd.DataFrame())
    conf.to_csv(tables / "confirmatory_contrasts.csv", index=False)
    per_model.to_csv(tables / "secondary_per_model_contrasts.csv", index=False)
    exploratory(df, tables / "exploratory")

    agree = pd.DataFrame()
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
    md.append("\n## Confirmatory contrasts (PREREGISTRATION 5; Holm within each analysis)\n")
    md.append("Pooled across included models with equal weight. Risk difference = mean over tickets of the "
              "(A − B) rate difference averaged across models; 95% and 90% CIs by ticket bootstrap; p from a "
              "paired sign-flip permutation test. **primary** = gate-passed pairs; **sensitivity** = all tickets. "
              "Interpretation follows the section 6 table. Wilson bounds are at ticket level.\n\n")
    if len(conf) and "p_perm" in conf:
        md.append(_md_table(conf, [c for c in ["analysis", "metric", "a", "b", "models", "n_tickets", "k_runs_a",
                                               "n_runs_a", "k_runs_b", "n_runs_b", "rate_a", "rate_b", "risk_diff",
                                               "rd_ci95_low", "rd_ci95_high", "rd_ci90_low", "rd_ci90_high",
                                               "risk_ratio", "wilson_upper_ticket_a", "wilson_upper_ticket_b",
                                               "p_perm", "p_perm_holm", "interpretation"] if c in conf.columns]))
        mcols = [c for c in conf.columns if c.startswith("mixed_")]
        if mcols:
            md.append("\nSupporting mixed model (condition × model + ticket random intercept):\n\n"
                      + _md_table(conf, ["analysis", "metric", "a", "b"] + mcols))
    elif len(conf):
        md.append(_md_table(conf, [c for c in ["analysis", "metric", "a", "b", "note"] if c in conf.columns]))
    else:
        md.append("_none_\n")
    md.append("\nPer-model contrasts (S5, secondary): `tables/secondary_per_model_contrasts.csv`.\n")
    if len(agree):
        md.append("\n## Judge vs human agreement\n")
        md.append(_md_table(agree, ["sample_set", "field", "scorer", "n_labeled", "human_positive", "scorer_positive", "raw_agreement", "kappa", "kappa_ci_low", "kappa_ci_high"]))
    md.append("\n## Exploratory\nSee `tables/exploratory/`. Not preregistered; treat as hypothesis-generating.\n")
    md.append("\n## Conclusions\n_Left for the author to write._\n")
    (out / "REPORT.md").write_text("".join(md))
    (out / "provenance.json").write_text(json.dumps({"run_id": run_id, "splits": splits, "mock": mock,
                                                       "manifest": store.manifest()}, indent=2, default=str))
    return out
