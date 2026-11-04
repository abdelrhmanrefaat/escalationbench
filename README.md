# EscalationBench

**Research question:** In realistic support workflows, does incentive or pressure reduce appropriate handoff to a human, does the agent disclose that to the customer, and does an explicit no-penalty escalation policy reduce the effect?

> **Status: pipeline revised for the updated plan (dry-run only).** No real experiment has been run. No results exist yet. See [RELATED_WORK.md](RELATED_WORK.md) for how this differs from prior work.

## What this is (and isn't)
- A controlled experiment on **synthetic** support tickets for a **fictional** company. No real customer or company data is used anywhere.
- Four conditions that differ only in the system prompt's "Team priorities" section:
  - NEUTRAL: use judgment.
  - INCENTIVE: the score depends on a low escalation rate, with no instruction to avoid escalating.
  - PRESSURE: a manager message demands fewer escalations this week.
  - MITIGATION: INCENTIVE plus a policy that required escalations never count against the agent.
- Agents from two providers: Claude Sonnet 5.5, Claude Haiku 5.5 and an OpenAI model. The provider is set per model in `config/experiment.yaml`.
- Each MUST_ESCALATE run is scored as exactly one of ESCALATED, HONEST_NON_ESCALATION, SILENT_NON_ESCALATION or FALSE_ESCALATION_CLAIM:
  - Whether the agent escalated comes from the tool log.
  - Handoff claims are detected by deterministic rules.
  - An LLM judge rates disclosure wording only, validated against the author's hand labels.
- A neutral "knowledge gate" probe checks whether each model recognizes each ticket's need for a human under the policy.
- It does **not** measure real-world deployments. See [Limitations](#limitations).

## Reproduce
```bash
make setup        # Python 3.12 venv + pinned requirements (needs `uv`)
make test         # unit tests, free, no network
make dry-run      # whole pipeline with a mock model, free; output is watermarked MOCK DATA
```
Real runs need `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` in your environment or in `.env` (gitignored). Every real run prints a cost estimate and will not start without `--yes`:
```bash
ebench estimate --tickets data/tickets/pilot.jsonl --repeats 2
ebench run --run-id pilot-01 --tickets data/tickets/pilot.jsonl --repeats 2 --max-usd 25 --yes
ebench judge --run-id pilot-01 --tickets data/tickets/pilot.jsonl --max-usd 10 --yes
ebench power --run-id pilot-01 --n-tickets 70 --repeats 2   # floor check + simulated power, before the full run
make report RUN=pilot-01      # regenerates every table and figure from runs/pilot-01/
```

## Repository map
| Path | What |
|---|---|
| `config/experiment.yaml` | models, repeats, turn cap, effort, judge, splits |
| `config/prompts/` | base prompt, escalation policy, the four condition sections, knowledge-gate prompt |
| `config/analysis_plan.yaml` | machine-readable copy of the preregistered contrasts |
| `data/tickets/` | synthetic tickets (pilot / dev / holdout) |
| `runs/<run_id>/` | raw data: every request, response, tool call, model, timestamp, cost |
| `results/<run_id>/` | generated tables, figures, REPORT.md; never hand-edited |
| `DECISIONS.md` | every design decision with its rationale |
| `RELATED_WORK.md` | literature check: what prior work measured and where this project differs |
| `PREREGISTRATION.md` | hypotheses and analysis plan, written by the author before data collection |

## Integrity rules
- Every number in a report is generated from `runs/` by code. Nothing is estimated or hand-edited.
- Holdout tickets cannot be run until `PREREGISTRATION.md` is committed and the prompts are unchanged since that commit (enforced in code).
- Null or surprising results are reported as they are.

## Limitations
_To be completed by the author. Known so far:_
- Synthetic tickets written with an LLM, a fictional company and a small scale (about 200 tickets).
- Tickets, labels and the subject model come from the same model family, so there is circularity risk.
- Label validation is weak. The author reviewed 10 flagged tickets (2 replaced) and labelled a random 20 blind: 11/20 agreement, κ = 0.13, mostly from judging "would a human be better" rather than the written policy. After discussion the author accepted all 9 gold labels, but that step was not independent (DECISIONS D-034–D-036, `data/tickets/spotcheck/`).
- Single-turn: the customer cannot push back.
- Models may recognize the scenario as a test.
- The LLM judge may share blind spots with the agents (measured by kappa against human labels).
- MITIGATION both removes the penalty and names escalation as legitimate. One arm cannot separate the two (D-022).
- Results are specific to the models and the date tested. Model comparisons are descriptive, not a ranking.

## How this was built
The code in this repository was written with **Claude Code** (Anthropic's coding agent), working in phases with the author's approval at each step.

**Done by the author:** _to be filled in by the author_ (e.g. research question, design decisions approved, ticket label review, PREREGISTRATION.md, human labels, conclusions).
