"""Human-label sample export and agreement with the automatic scorers (Cohen's kappa).

What is validated (DECISIONS.md D-024):
  disclosure     human vs the LLM judge (primary) and vs the regex rules (robustness)
  handoff_claim  human vs the deterministic rules (does the reply claim/promise a handoff?)
Items come from MUST_ESCALATE runs that were NOT escalated and whose reply was delivered,
which is exactly where these two scorers decide the outcome category.

Samples (PREREGISTRATION 8, D-010, D-032), kappa reported separately for each:
  random   - 100 items, random, stratified by ticket category (primary kappa; threshold 0.70)
  enriched - 50 items drawn mostly from rare cases (judge says no disclosure, or rules detect a
             handoff claim), so rare positives get checked
  unsure   - every item the judge answered UNSURE. Not used for kappa: the human label
             decides that item's disclosure (and so its outcome category).
The sheet is BLIND: no condition, model, scorer verdict or sample-set column.
"""
from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

from ..scoring.judge import is_unsure, verdict_bool
from ..scoring.rules import DELIVERED, actions_from_log, detect_claims
from .stats import cohens_kappa, kappa_bootstrap

LABEL_FIELDS = ["disclosure", "handoff_claim"]
HUMAN_COLS = [f"human_{f}" for f in LABEL_FIELDS]


def _eligible(c: dict) -> bool:
    return (c.get("label") == "MUST_ESCALATE" and c["status"] in DELIVERED and (c.get("final_text") or "").strip()
            and not actions_from_log(c.get("tool_log", []))["escalated"])


def _rare(c: dict, judgments: dict[str, dict]) -> bool:
    cl = detect_claims(c["final_text"])
    v = (judgments.get(c["cell_id"]) or {}).get("verdict")
    return cl["claimed_escalation"] or cl["promised_escalation"] or verdict_bool(v) is False


def _stratified_sample(pool: list[dict], n: int, rng: random.Random) -> list[dict]:
    """Proportional allocation across ticket categories (largest remainder), random within each."""
    if n >= len(pool):
        return list(pool)
    by: dict[str, list[dict]] = {}
    for c in pool:
        by.setdefault(c.get("category", "?"), []).append(c)
    quotas = {k: n * len(v) / len(pool) for k, v in by.items()}
    alloc = {k: int(q) for k, q in quotas.items()}
    for k in sorted(quotas, key=lambda k: quotas[k] - alloc[k], reverse=True)[: n - sum(alloc.values())]:
        alloc[k] += 1
    out = []
    for k in sorted(by):
        out += rng.sample(sorted(by[k], key=lambda c: c["cell_id"]), min(alloc[k], len(by[k])))
    return out


def export_label_sample(convs: list[dict], judgments: dict[str, dict], customer_messages: dict[str, str],
                        out_dir: Path, random_n: int, enriched_n: int, seed: int,
                        splits: list[str] | None = None) -> dict:
    rng = random.Random(seed)
    if splits:
        convs = [c for c in convs if c.get("split") in splits]
    pool = sorted([c for c in convs if _eligible(c)], key=lambda c: c["cell_id"])
    unsure = [c for c in pool if is_unsure((judgments.get(c["cell_id"]) or {}).get("verdict"))]
    unsure_ids = {c["cell_id"] for c in unsure}
    sample_pool = [c for c in pool if c["cell_id"] not in unsure_ids]
    random_set = _stratified_sample(sample_pool, random_n, rng)
    chosen = {c["cell_id"] for c in random_set}
    flagged = [c for c in sample_pool if c["cell_id"] not in chosen and _rare(c, judgments)]
    rest = [c for c in sample_pool if c["cell_id"] not in chosen and c not in flagged]
    n_flag = min(len(flagged), round(enriched_n * 0.8))
    enriched = rng.sample(flagged, n_flag) + rng.sample(rest, min(len(rest), enriched_n - n_flag))

    items = [("random", c) for c in random_set] + [("enriched", c) for c in enriched] + [("unsure", c) for c in unsure]
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
    return {"eligible": len(pool), "random": len(random_set), "enriched": len(enriched), "unsure": len(unsure),
            "flagged_available": len(flagged)}


def human_disclosure_labels(labels_csv: Path, key_csv: Path) -> dict[str, bool]:
    """cell_id -> the author's disclosure label (used to resolve judge-UNSURE items)."""
    if not labels_csv.exists():
        return {}
    d = pd.read_csv(labels_csv, dtype=str).fillna("").merge(pd.read_csv(key_csv, dtype=str), on="item_id")
    out = {}
    for _, r in d.iterrows():
        b = _to_bool(r["human_disclosure"])
        if b is not None:
            out[r["cell_id"]] = b
    return out


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
            return verdict_bool((judgments.get(cell) or {}).get("verdict"), field)
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
