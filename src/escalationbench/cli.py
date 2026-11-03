"""Command line: ebench estimate | run | score | judge | export-labels | report | power

Real (paid) runs require --yes AND an estimate within --max-usd, or an explicit
--allow-over-estimate. The hard cap (--max-usd) always applies regardless.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

from .agent import build_gate_params, build_params
from .config import REPO_ROOT, ExperimentConfig, system_prompt
from .cost import ConversationAssumptions, Pricing, estimate_conversation_cost, estimate_judge_cost
from .rawlog import RunStore
from .runner import check_confirmatory_allowed, expand_grid, run_grid
from .tickets import load_tickets


def _client(dry_run: bool, cfg: ExperimentConfig):
    if dry_run:
        from .clients import MockClient
        return MockClient()
    load_dotenv(REPO_ROOT / ".env")  # loads ANTHROPIC_API_KEY / OPENAI_API_KEY into the environment; never printed
    from .clients import RoutingClient
    return RoutingClient(cfg.providers)


def _load(args):
    cfg = ExperimentConfig.load(args.config)
    tickets = load_tickets(args.tickets)
    holdout = [t for t in tickets if t.split == "holdout"]
    if holdout and not args.confirmatory:
        sys.exit(f"{len(holdout)} holdout tickets in {args.tickets}. Holdout runs need --confirmatory "
                 "(which requires a committed PREREGISTRATION.md).")
    if args.confirmatory and not args.dry_run:
        check_confirmatory_allowed()
    if args.ticket_ids:
        keep = set(args.ticket_ids.split(","))
        tickets = [t for t in tickets if t.id in keep]
    models = args.models.split(",") if args.models else cfg.models
    conditions = args.conditions.split(",") if args.conditions else cfg.conditions
    repeats = args.repeats if args.repeats is not None else cfg.repeats
    return cfg, tickets, models, conditions, repeats


def estimate(cfg, tickets, models, conditions, repeats, pricing, client, judge=True) -> dict:
    a = ConversationAssumptions()
    lines, total = [], 0.0
    for model in models:
        for cond in conditions:
            first_tokens = [client.count_tokens(build_params(cfg, model, system_prompt(cond, cfg.company_name),
                                                             [{"role": "user", "content": t.customer_message}]))
                            for t in tickets]
            mean_first = sum(first_tokens) / max(1, len(first_tokens))
            per_conv = estimate_conversation_cost(pricing, model, int(mean_first), a)
            sub = per_conv * len(tickets) * repeats
            total += sub
            lines.append((model, cond, int(mean_first), per_conv, sub))
    gate_total = 0.0
    if cfg.gate.get("enabled", True):
        for model in models:
            r = pricing.rates(model)
            for t in tickets:
                tok = client.count_tokens(build_gate_params(cfg, model, t))
                gate_total += (tok * r["input"] + a.output_tokens_per_call * r["output"]) / 1_000_000
            lines.append((model, "GATE", 0, 0.0, 0.0))
    n_convs = len(tickets) * len(models) * len(conditions) * repeats
    n_must = sum(t.label == "MUST_ESCALATE" for t in tickets) * len(models) * len(conditions) * repeats
    # Upper bound: the judge only sees un-escalated MUST_ESCALATE runs; assume all of them.
    judge_cost = estimate_judge_cost(pricing, cfg.judge.model, n_must) if judge else 0.0
    return {"lines": lines, "agent_total": total + gate_total, "gate_total": gate_total, "judge_total": judge_cost,
            "n_conversations": n_convs, "with_margin": (total + gate_total + judge_cost) * a.safety_margin,
            "assumptions": a}


def print_estimate(e: dict, pricing: Pricing, mock: bool) -> None:
    a = e["assumptions"]
    print(f"\nCost estimate ({'MOCK token counts' if mock else 'token counts from count_tokens API'}; prices as of {pricing.as_of})")
    print(f"Assumes {a.calls_per_conversation} API calls/conversation, +{a.growth_tokens_per_call} input tokens per call, "
          f"{a.output_tokens_per_call} output tokens/call, no caching discount.")
    print(f"{'model':<20}{'condition':<11}{'1st-call in tok':>16}{'$/conv':>10}{'subtotal $':>12}")
    for m, c, tok, per, sub in e["lines"]:
        if c != "GATE":
            print(f"{m:<20}{c:<11}{tok:>16}{per:>10.4f}{sub:>12.2f}")
    print(f"Knowledge gate probes: ${e['gate_total']:.2f} (included in agent total)")
    print(f"Conversations: {e['n_conversations']}  agent ${e['agent_total']:.2f}  judge (upper bound) ${e['judge_total']:.2f}  "
          f"total with x{a.safety_margin} margin: ${e['with_margin']:.2f}\n")


def cmd_estimate(args):
    cfg, tickets, models, conditions, repeats = _load(args)
    pricing = Pricing.load()
    client = _client(args.dry_run, cfg)
    print_estimate(estimate(cfg, tickets, models, conditions, repeats, pricing, client), pricing, client.is_mock)


def cmd_run(args):
    cfg, tickets, models, conditions, repeats = _load(args)
    pricing = Pricing.load()
    client = _client(args.dry_run, cfg)
    if args.dry_run and not args.run_id.startswith("dryrun-"):
        sys.exit("Dry-run run ids must start with 'dryrun-' so they are never mistaken for real data.")
    if not args.dry_run and args.run_id.startswith("dryrun-"):
        sys.exit("Real runs may not use a 'dryrun-' run id.")
    est = estimate(cfg, tickets, models, conditions, repeats, pricing, client, judge=False)
    print_estimate(est, pricing, client.is_mock)
    if not args.dry_run:
        if est["agent_total"] * est["assumptions"].safety_margin > args.max_usd and not args.allow_over_estimate:
            sys.exit(f"Estimated cost exceeds --max-usd ${args.max_usd:.2f}. Not starting. Get approval, then "
                     "raise --max-usd or pass --allow-over-estimate (the hard cap still applies).")
        if not args.yes:
            sys.exit("Real API run not started: pass --yes once the estimate above has been approved.")
    cells = expand_grid(tickets, cfg, models, conditions, repeats)
    store = RunStore(args.run_id)
    print(f"Run {args.run_id}: {len(cells)} cells; hard cap ${args.max_usd:.2f}")
    s = run_grid(cells=cells, client=client, store=store, cfg=cfg, pricing=pricing, max_usd=args.max_usd,
                 retry_errors=args.retry_errors, concurrency=args.concurrency,
                 manifest_extra={"tickets_file": str(args.tickets), "confirmatory": args.confirmatory})
    print(f"Done. gate probes={s.gates_run} new={s.completed_now} cached/skipped={s.skipped_cached} status={s.status_counts} spent=${s.spent_usd:.4f}")
    if s.budget_stopped:
        print(f"STOPPED AT BUDGET: {s.budget_message}\nRe-run the same command with a higher --max-usd to resume.")
        sys.exit(2)


def cmd_score(args):
    from .analysis.report import build_scored
    store = RunStore(args.run_id)
    df = build_scored(store)
    print(f"Scored {len(df)} conversations from runs/{args.run_id}.")
    if len(df):
        print(df.groupby(["model", "condition", "status"]).size().to_string())


def cmd_judge(args):
    from .scoring.judge import judge_run
    cfg = ExperimentConfig.load(args.config)
    store = RunStore(args.run_id)
    tickets = {t.id: t.customer_message for t in load_tickets(args.tickets)}
    client = _client(args.dry_run, cfg)
    if not args.dry_run and not args.yes:
        from .scoring.judge import needs_judgment
        n = len([c for c in store.conversations() if needs_judgment(c)])
        print(f"Judge estimate: ~${estimate_judge_cost(Pricing.load(), cfg.judge.model, n):.2f} for {n} conversations "
              f"with {cfg.judge.model}. Pass --yes to start.")
        sys.exit(1)
    stats = judge_run(store=store, client=client, cfg=cfg, pricing=Pricing.load(), max_usd=args.max_usd,
                      customer_messages=tickets, concurrency=args.concurrency or cfg.concurrency)
    print(stats)


def cmd_export_labels(args):
    from .analysis.kappa import export_label_sample
    from .analysis.report import RESULTS_DIR
    cfg = ExperimentConfig.load(args.config)
    store = RunStore(args.run_id)
    tickets = {t.id: t.customer_message for t in load_tickets(args.tickets)}
    base = RESULTS_DIR / "dryrun" / args.run_id if store.is_dry_run() else RESULTS_DIR / args.run_id
    hl = cfg.human_labels
    info = export_label_sample(store.conversations(), store.judgments(), tickets, base / "labels",
                               hl.get("random_n", 100), hl.get("enriched_n", 50), hl.get("seed", 7))
    print(f"Wrote {base/'labels'/'human_labels_TODO.csv'} ({info}). Fill the human_* columns with yes/no, "
          "then save as human_labels_DONE.csv in the same folder and run `ebench report`.")


def cmd_report(args):
    from .analysis.report import generate
    splits = args.splits.split(",") if args.splits else None
    out = generate(args.run_id, splits=splits)
    print(f"Wrote tables, figures and REPORT.md to {out}")


def cmd_power(args):
    import pandas as pd
    from .analysis.power import floor_check, power_table
    from .analysis.report import RESULTS_DIR, build_scored, load_analysis_plan
    store = RunStore(args.run_id)
    df = build_scored(store)
    df = df[(df["status"] != "API_ERROR") & (df["label"] == "MUST_ESCALATE")]
    if df.empty:
        sys.exit("No scored MUST_ESCALATE runs in this run.")
    plan = load_analysis_plan()
    n_tests = sum(len(s["contrasts"]) for s in plan["primary_family"]) * df["model"].nunique()
    out = (RESULTS_DIR / "dryrun" / args.run_id if store.is_dry_run() else RESULTS_DIR / args.run_id) / "tables"
    out.mkdir(parents=True, exist_ok=True)
    floors, powers = [], []
    for col in args.metrics.split(","):
        d = df[df[col].notna()].assign(**{col: lambda x, c=col: x[c].astype(float)})
        floors.append(floor_check(d, col))
        powers.append(power_table(d, col, args.baseline, args.n_tickets, args.repeats, n_tests, seed=args.seed))
    fl, pw = pd.concat(floors, ignore_index=True), pd.concat(powers, ignore_index=True)
    fl.to_csv(out / "power_floor_check.csv", index=False)
    pw.to_csv(out / "power_simulation.csv", index=False)
    if store.is_dry_run():
        print("MOCK DATA: these numbers test the code path only.")
    print("\nFloor check (pilot rates by condition):\n" + fl.to_string(index=False))
    if fl["floor_all_conditions"].any():
        print("\nFLOOR: at least one model is below 2% in EVERY condition. Per the plan, report this to the "
              "author before changing anything; do not make scenarios more extreme.")
    print(f"\nSimulated power (n_tickets={args.n_tickets}, repeats={args.repeats}, {n_tests} tests, Bonferroni):\n"
          + pw.pivot_table(index=["model", "metric", "baseline_rate"], columns="delta", values="power").round(2).to_string())
    print(f"\nWrote {out/'power_floor_check.csv'} and {out/'power_simulation.csv'}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="ebench")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, tickets=True):
        sp.add_argument("--config", default=str(REPO_ROOT / "config" / "experiment.yaml"))
        if tickets:
            sp.add_argument("--tickets", default=str(REPO_ROOT / "data" / "tickets" / "pilot.jsonl"))
        sp.add_argument("--dry-run", action="store_true", help="use the free mock client")

    for name in ("estimate", "run"):
        sp = sub.add_parser(name)
        common(sp)
        sp.add_argument("--models"); sp.add_argument("--conditions"); sp.add_argument("--ticket-ids")
        sp.add_argument("--repeats", type=int)
        sp.add_argument("--confirmatory", action="store_true", help="allow holdout tickets (requires committed prereg)")
        if name == "run":
            sp.add_argument("--run-id", required=True)
            sp.add_argument("--max-usd", type=float, required=True)
            sp.add_argument("--yes", action="store_true", help="confirm a real, paid run")
            sp.add_argument("--allow-over-estimate", action="store_true")
            sp.add_argument("--retry-errors", action="store_true")
            sp.add_argument("--concurrency", type=int)
            sp.set_defaults(func=cmd_run)
        else:
            sp.set_defaults(func=cmd_estimate)

    sp = sub.add_parser("score"); sp.add_argument("--run-id", required=True); sp.set_defaults(func=cmd_score)

    sp = sub.add_parser("judge"); common(sp)
    sp.add_argument("--run-id", required=True); sp.add_argument("--max-usd", type=float, required=True)
    sp.add_argument("--yes", action="store_true"); sp.add_argument("--concurrency", type=int)
    sp.set_defaults(func=cmd_judge)

    sp = sub.add_parser("export-labels"); common(sp)
    sp.add_argument("--run-id", required=True); sp.set_defaults(func=cmd_export_labels)

    sp = sub.add_parser("report"); sp.add_argument("--run-id", required=True)
    sp.add_argument("--splits", help="comma list, e.g. holdout"); sp.set_defaults(func=cmd_report)

    sp = sub.add_parser("power", help="pilot floor check + simulated power for the planned full run")
    sp.add_argument("--run-id", required=True)
    sp.add_argument("--n-tickets", type=int, default=70, help="MUST_ESCALATE tickets in the planned confirmatory set")
    sp.add_argument("--repeats", type=int, default=2)
    sp.add_argument("--baseline", default="NEUTRAL")
    sp.add_argument("--metrics", default="missed_escalation,is_undisclosed_miss")
    sp.add_argument("--seed", type=int, default=0)
    sp.set_defaults(func=cmd_power)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
