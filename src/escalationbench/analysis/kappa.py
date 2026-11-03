"""Human-label sample export and agreement with the automatic scorers (Cohen's kappa).

What is validated (DECISIONS.md D-024):
  disclosure     human vs the LLM judge (primary) and vs the regex rules (robustness)
  handoff_claim  human vs the deterministic rules (does the reply claim/promise a handoff?)
Items come from MUST_ESCALATE runs that were NOT escalated and whose reply was delivered,
which is exactly where these two scorers decide the outcome category.

Two samples, reported separately (D-010):
  random   - simple random sample (unbiased estimate of agreement)
  enriched - drawn mostly from the rare cases (judge says no disclosure, or rules detect a
             handoff claim), so rare positives get checked
The sheet is BLIND: no condition, model, scorer verdict or sample-set column.
"""
from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

from ..scoring.rules import DELIVERED, actions_from_log, detect_claims
from .stats import cohens_kappa, kappa_bootstrap

LABEL_FIELDS = ["disclosure", "handoff_claim"]
HUMAN_COLS = [f"human_{f}" for f in LABEL_FIELDS]


def _eligible(c: dict) -> bool:
    return (c.get("label") == "MUST_ESCALATE" and c["status"] in DELIVERED and (c.get("final_text") or "").strip()
            and not actions_from_log(c.get("tool_log", []))["escalated"])


def _rare(c: dict, judgments: dict[str, dict]) -> bool:
    cl = detect_claims(c["final_text"])
    v = (judgments.get(c["cell_id"]) or {}).get("verdict") or {}
    return cl["claimed_escalation"] or cl["promised_escalation"] or v.get("disclosure") is False


def export_label_sample(convs: list[dict], judgments: dict[str, dict], customer_messages: dict[str, str],
                        out_dir: Path, random_n: int, enriched_n: int, seed: int) -> dict:
    rng = random.Random(seed)
    pool = sorted([c for c in convs if _eligible(c)], key=lambda c: c["cell_id"])
    random_set = rng.sample(pool, min(random_n, len(pool)))
    chosen = {c["cell_id"] for c in random_set}
    flagged = [c for c in pool if c["cell_id"] not in chosen and _rare(c, judgments)]
    rest = [c for c in pool if c["cell_id"] not in chosen and c not in flagged]
    n_flag = min(len(flagged), round(enriched_n * 0.8))
    enriched = rng.sample(flagged, n_flag) + rng.sample(rest, min(len(rest), enriched_n - n_flag))

    items = [("random", c) for c in random_set] + [("enriched", c) for c in enriched]
    rng.shuffle(items)
    out_dir.mkdir(parents=True, exist_ok=True)
    sheet, key = [], []
    for i, (which, c) in enumerate(items, start=1):
        item_id = f"L{i:03d}"
        sheet.append({"item_id": item_id, "customer_message": customer_messages[c["ticket_id"]],
                      "agent_reply": c["final_text"], **{h: "" for h in HUMAN_COLS}, "notes": ""})
        key.append({"item_id": item_id, "cell_id": c["cell_id"], "sample_set": which})
    pd.DataFrame(sheet).to_csv(out_dir / "human_labels_TODO.csv", index=False)
    pd.DataFrame(key).to_csv(out_dir / "human_labels_key.csv", index=False)
    return {"random": len(random_set), "enriched": len(enriched), "flagged_available": len(flagged)}


def _to_bool(v) -> bool | None:
    s = str(v).strip().lower()
    if s in {"1", "y", "yes", "true", "t"}:
        return True
    if s in {"0", "n", "no", "false", "f"}:
        return False
    return None


def agreement_table(labels_csv: Path, key_csv: Path, judgments: dict[str, dict],
                    convs: dict[str, dict] | None = None) -> pd.DataFrame:
    """Kappa per (sample set, field, automatic scorer). `convs` maps cell_id -> conversation
    and is needed for the rule-based comparisons."""
    labels = pd.read_csv(labels_csv, dtype=str).fillna("")
    key = pd.read_csv(key_csv, dtype=str)
    d = labels.merge(key, on="item_id", how="inner")
    convs = convs or {}

    def auto(scorer: str, field: str, cell: str):
        if scorer == "judge":
            v = (judgments.get(cell) or {}).get("verdict") or {}
            return v.get(field) if isinstance(v.get(field), bool) else None
        c = convs.get(cell)
        if not c:
            return None
        cl = detect_claims(c.get("final_text") or "")
        return cl["disclosure"] if field == "disclosure" else (cl["claimed_escalation"] or cl["promised_escalation"])

    rows = []
    for sample_set in ("random", "enriched"):
        s = d[d.sample_set == sample_set]
        for field, scorer in (("disclosure", "judge"), ("disclosure", "rule"), ("handoff_claim", "rule")):
            pairs = []
            for _, r in s.iterrows():
                h, a = _to_bool(r[f"human_{field}"]), auto(scorer, field, r["cell_id"])
                if h is not None and a is not None:
                    pairs.append((h, bool(a)))
            hx, ay = [p[0] for p in pairs], [p[1] for p in pairs]
            k = cohens_kappa(hx, ay) if pairs else float("nan")
            lo, hi = kappa_bootstrap(hx, ay) if pairs else (float("nan"), float("nan"))
            rows.append({"sample_set": sample_set, "field": field, "scorer": scorer, "n_labeled": len(pairs),
                         "human_positive": sum(hx), "scorer_positive": sum(ay),
                         "raw_agreement": (sum(a == b for a, b in pairs) / len(pairs)) if pairs else float("nan"),
                         "kappa": k, "kappa_ci_low": lo, "kappa_ci_high": hi})
    return pd.DataFrame(rows)
