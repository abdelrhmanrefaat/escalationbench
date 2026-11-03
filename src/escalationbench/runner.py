"""Expand the experiment grid and run it with caching, resume, concurrency and a hard budget."""
from __future__ import annotations

import subprocess
import threading
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass

from .agent import cell_id, run_conversation
from .clients import Client
from .config import REPO_ROOT, ExperimentConfig, prompt_hashes
from .cost import BudgetExceeded, BudgetGuard, Pricing
from .rawlog import RunStore, utc_now
from .tickets import Ticket


@dataclass
class Cell:
    ticket: Ticket
    condition: str
    model: str
    rep: int

    @property
    def id(self) -> str:
        return cell_id(self.ticket.id, self.condition, self.model, self.rep)


def expand_grid(tickets: list[Ticket], cfg: ExperimentConfig, models: list[str] | None = None,
                conditions: list[str] | None = None, repeats: int | None = None) -> list[Cell]:
    models = models or cfg.models
    conditions = conditions or cfg.conditions
    repeats = repeats if repeats is not None else cfg.repeats
    # rep-major ordering: if the budget stops a run early, every ticket/condition has
    # equal coverage up to the last finished repeat (no condition is systematically short).
    return [Cell(t, c, m, r) for r in range(repeats) for t in tickets for m in models for c in conditions]


def git_info() -> dict:
    def run(*args):
        try:
            return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            return ""
    return {
        "commit": run("rev-parse", "HEAD") or None,
        "dirty": bool(run("status", "--porcelain")),
        "prereg_commit": run("log", "-n", "1", "--format=%H", "--", "PREREGISTRATION.md") or None,
    }


def check_confirmatory_allowed() -> dict:
    """Holdout tickets may only be run after PREREGISTRATION.md is committed and the
    prompts are unchanged since that commit."""
    info = git_info()
    if not info["prereg_commit"]:
        raise SystemExit("Refusing confirmatory run: PREREGISTRATION.md has not been committed.")
    diff = subprocess.run(["git", "diff", "--quiet", info["prereg_commit"], "--", "config/prompts", "config/experiment.yaml"],
                          cwd=REPO_ROOT)
    if diff.returncode != 0:
        raise SystemExit("Refusing confirmatory run: prompts or experiment config changed since the preregistration commit.")
    return info


@dataclass
class RunSummary:
    attempted: int
    completed_now: int
    skipped_cached: int
    status_counts: dict
    spent_usd: float
    budget_stopped: bool
    budget_message: str | None


def run_grid(*, cells: list[Cell], client: Client, store: RunStore, cfg: ExperimentConfig,
             pricing: Pricing, max_usd: float, retry_errors: bool = False, concurrency: int | None = None,
             progress: bool = True, manifest_extra: dict | None = None) -> RunSummary:
    done = store.completed_cells(include_errors=not retry_errors)
    todo = [c for c in cells if c.id not in done]
    budget = BudgetGuard(max_usd, already_spent=store.spent_usd())
    store.write_manifest({
        "ts": utc_now(), "dry_run": client.is_mock, "max_usd": max_usd, "n_cells_requested": len(cells),
        "n_cells_todo": len(todo), "config": cfg.raw, "prompt_hashes": prompt_hashes(cfg.company_name),
        "pricing_as_of": pricing.as_of, "git": git_info(), **(manifest_extra or {}),
    })

    stop = threading.Event()
    counts: dict[str, int] = {}
    budget_msg = None
    lock = threading.Lock()
    finished = 0

    def work(cell: Cell):
        if stop.is_set():
            return None
        return run_conversation(client=client, store=store, budget=budget, pricing=pricing, cfg=cfg,
                                ticket=cell.ticket, condition=cell.condition, model=cell.model, rep=cell.rep)

    workers = max(1, concurrency or cfg.concurrency)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending = set()
        it = iter(todo)
        while True:
            while not stop.is_set() and len(pending) < workers * 2:
                nxt = next(it, None)
                if nxt is None:
                    break
                pending.add(pool.submit(work, nxt))
            if not pending:
                break
            finished_set, pending = wait(pending, return_when=FIRST_COMPLETED)
            for f in finished_set:
                try:
                    rec = f.result()
                except BudgetExceeded as e:
                    stop.set()
                    budget_msg = str(e)
                    continue
                if rec is None:
                    continue
                with lock:
                    counts[rec["status"]] = counts.get(rec["status"], 0) + 1
                    finished += 1
                    if progress and (finished % 25 == 0 or finished == len(todo)):
                        print(f"  {finished}/{len(todo)} conversations | spent ${budget.spent:.4f} of ${max_usd:.2f}", flush=True)

    return RunSummary(
        attempted=len(todo), completed_now=finished, skipped_cached=len(cells) - len(todo),
        status_counts=counts, spent_usd=round(budget.spent, 6), budget_stopped=stop.is_set(), budget_message=budget_msg,
    )
