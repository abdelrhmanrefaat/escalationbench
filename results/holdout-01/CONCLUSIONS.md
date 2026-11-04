# Conclusions: `holdout-01`

> **Authorship.** The author asked Claude Code to draft this section because they had no conclusions of their own in mind. It was published at the author's request. Every number below comes from [`REPORT.md`](REPORT.md) and [`tables/`](tables/), which `ebench report` generates from the raw logs in [`runs/holdout-01/`](../../runs/holdout-01/). No number here was typed in by hand from anywhere else.

**Setup:** 160 holdout tickets × 4 conditions × 5 repeats × 3 models = **9,600 conversations**. All of them completed, none were excluded, and the run cost $59.80 against a $70 cap. The analysis is the preregistered one ([`PREREGISTRATION.md`](../../PREREGISTRATION.md)).

## 1. Missed escalations (H1–H4): none observed, so the hypotheses are not supported

- All three models escalated **every** must-escalate ticket in every condition: **4,800 of 4,800** runs.
- The incentive and pressure prompts did not cause a single missed handoff. The 95% upper bound is about 1% per model and condition (0 of 400 runs each).
- Because no ticket was ever missed, there were also no undisclosed misses, no false escalation claims, and nothing for the mitigation prompt to reduce. **H1, H2, H3 and H4 are not supported.**
- The knowledge gate shows the models understood the policy: 1,195 of 1,200 probes passed.
- **What this does and does not mean.** This is a floor effect, as on the dev set (D-037). It shows that *in this setup*, with a written policy, a single customer message, and these models on this date, business pressure did not push the agents into skipping required handoffs. It is **not** evidence that pressure can never cause this. Harder cases were not tested: ambiguous policies, multi-turn pushback, or stronger and longer-running incentives.

## 2. Unnecessary escalations (H5): a large drop, as predicted

On tickets the agent should resolve itself, incentive and pressure prompts cut handoffs by more than half. Rates below are pooled across the three models.

| Contrast | Rate A | Rate B | Difference (95% CI) | Holm p | Preregistered reading |
|---|---|---|---|---|---|
| INCENTIVE vs NEUTRAL | 19.2% | 43.0% | **−23.8 pp** (−29.5 to −18.4) | 0.001 | evidence of an effect |
| PRESSURE vs NEUTRAL | 15.3% | 43.0% | **−27.7 pp** (−33.8 to −21.8) | 0.001 | evidence of an effect |
| MITIGATION vs INCENTIVE | 21.5% | 19.2% | +2.3 pp (+0.7 to +4.1) | 0.066 | no meaningful effect |

- **H5 is supported.** The author predicted that incentive and pressure would reduce unnecessary escalation, and that mitigation would make no difference compared with incentive. Both predictions hold.
- **All three models show the decrease** (secondary per-model analysis):
  - GPT-6.1-sol: 43% → 6–7%, the largest drop.
  - Haiku: 55% → 25–34%.
  - Sonnet: 31% → 15–17%.
- **The mitigation result is "no meaningful effect", not "proven zero".**
  - The whole 95% interval (+0.7 to +4.1 pp) lies below the preregistered smallest effect of interest, 5 pp.
  - The supporting mixed model does detect a small increase (odds ratio 1.36). So there may be a real effect, but it is too small to matter by the standard set before the data came in.

## 3. Putting it together

Under pressure to escalate less, the models cut the handoffs they were **allowed** to skip and kept every handoff they were **required** to make. In this benchmark that is the safe pattern, not the failure mode the study was built to find.

This study did not show that pressure makes support agents unsafe. It showed that pressure changes behaviour strongly where the rules leave room for choice.

## 4. Limitations specific to this result

- **The judge and human-label validation never ran.** Both only apply to missed escalations, and there were none. The hand-labelling sample was empty (`results/holdout-01/labels/`), so there is no κ for the judge.
- **Ticket labels are weakly validated.** The author's blind check agreed with the gold labels on 11/20 (κ = 0.13) before adjudication (D-035). Some "should resolve" tickets may be ones a reasonable person would escalate. If so, part of the unnecessary-escalation drop could be the models declining borderline handoffs rather than good ones.
- **P3 / H5 was added after the dev run** (D-037) and is disclosed as dev-informed in the preregistration.
- **Synthetic, single-turn, one fictional company.** These are not real-world deployment rates.
- **Model- and date-specific.** Differences between models are descriptive and not a ranking.

## 5. What a follow-up could test

Any follow-up must be a **new, separately preregistered study** with new tickets. This holdout set is used up and must not be re-run with changed prompts to "find" an effect. Open questions:

- whether missed escalations appear when the customer pushes back over several turns;
- whether they appear when the escalation rule is less explicit.
