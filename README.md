# EscalationBench

**Research question:** When an LLM customer-support agent is under business pressure to avoid escalating to a human, does it miss more cases that need a human, and does it misreport what it did?

> **Status: Phase 2 (pipeline built, dry-run only).** No real experiment has been run. No results exist yet.

## What this is (and isn't)
- A controlled experiment on **synthetic** support tickets for a **fictional** company. No real customer or company data is used anywhere.
- Four system-prompt conditions that differ in one paragraph only: NEUTRAL, PLACEBO (unrelated tone KPI), SOFT_KPI ("reduce escalations") and HARD_KPI ("your score drops per escalation").
- It does **not** measure real-world deployments. See [Limitations](#limitations).

## Reproduce
```bash
make setup        # Python 3.12 venv + pinned requirements (needs `uv`)
make test         # unit tests, free, no network
make dry-run      # whole pipeline with a mock model, free; output is watermarked MOCK DATA
```
Real runs need `ANTHROPIC_API_KEY` in your environment or in `.env` (gitignored). Every real run prints a cost estimate and will not start without `--yes`:
```bash
ebench estimate --tickets data/tickets/pilot.jsonl --repeats 2
ebench run --run-id pilot-01 --tickets data/tickets/pilot.jsonl --repeats 2 --max-usd 25 --yes
ebench judge --run-id pilot-01 --tickets data/tickets/pilot.jsonl --max-usd 10 --yes
make report RUN=pilot-01      # regenerates every table and figure from runs/pilot-01/
```

## Repository map
| Path | What |
|---|---|
| `config/experiment.yaml` | models, repeats, turn cap, effort, judge, splits |
| `config/prompts/` | base prompt, escalation policy, the four condition paragraphs |
| `config/analysis_plan.yaml` | machine-readable copy of the preregistered contrasts |
| `data/tickets/` | synthetic tickets (pilot / dev / holdout) |
| `runs/<run_id>/` | raw data: every request, response, tool call, model, timestamp, cost |
| `results/<run_id>/` | generated tables, figures, REPORT.md; never hand-edited |
| `DECISIONS.md` | every design decision with its rationale |
| `PREREGISTRATION.md` | hypotheses and analysis plan, written by the author before data collection |

## Integrity rules
- Every number in a report is generated from `runs/` by code. Nothing is estimated or hand-edited.
- Holdout tickets cannot be run until `PREREGISTRATION.md` is committed and the prompts are unchanged since that commit (enforced in code).
- Null or surprising results are reported as they are.

## Limitations
_To be completed by the author. Known so far:_
- Synthetic tickets written with an LLM, a fictional company and a small scale (about 200 tickets).
- Tickets, labels and the subject model come from the same model family, so there is circularity risk (mitigated by author review of labels).
- Single-turn: the customer cannot push back.
- Models may recognize the scenario as a test.
- The LLM judge may share blind spots with the agents (measured by kappa against human labels).

## How this was built
The code in this repository was written with **Claude Code** (Anthropic's coding agent), working in phases with the author's approval at each step.

**Done by the author:** _to be filled in by the author_ (e.g. research question, design decisions approved, ticket label review, PREREGISTRATION.md, human labels, conclusions).
