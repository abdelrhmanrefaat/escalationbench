"""Human-label sample export and judge-vs-human agreement (Cohen's kappa).

Two samples, reported separately (DECISIONS.md D-010):
  random   - simple random sample of judged conversations (unbiased estimate of agreement)
  enriched - drawn mostly from items the judge flagged, so rare positives get checked
The labeling sheet is BLIND: no condition, model, judge verdict or sample-set column.
The item -> sample-set key is written to a separate file.
"""
from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

from ..scoring.judge import VERDICT_FIELDS
from .stats import cohens_kappa, kappa_bootstrap

HUMAN_COLS = [f"human_{f}" for f in VERDICT_FIELDS]


def export_label_sample(convs: list[dict], judgments: dict[str, dict], customer_messages: dict[str, str],
                        out_dir: Path, random_n: int, enriched_n: int, seed: int) -> dict:
    judged = [c for c in convs if c["status"] == "COMPLETED" and (judgments.get(c["cell_id"]) or {}).get("verdict")]
    rng = random.Random(seed)
    pool = sorted(judged, key=lambda c: c["cell_id"])
    random_set = rng.sample(pool, min(random_n, len(pool)))
    chosen = {c["cell_id"] for c in random_set}
    flagged = [c for c in pool if c["cell_id"] not in chosen and any(judgments[c["cell_id"]]["verdict"][f] for f in VERDICT_FIELDS[:4])]
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


def agreement_table(labels_csv: Path, key_csv: Path, judgments: dict[str, dict]) -> pd.DataFrame:
    labels = pd.read_csv(labels_csv, dtype=str).fillna("")
    key = pd.read_csv(key_csv, dtype=str)
    d = labels.merge(key, on="item_id", how="inner")
    rows = []
    for sample_set in ("random", "enriched"):
        s = d[d.sample_set == sample_set]
        for f in VERDICT_FIELDS:
            pairs = []
            for _, r in s.iterrows():
                h = _to_bool(r[f"human_{f}"])
                j = (judgments.get(r["cell_id"]) or {}).get("verdict")
                if h is None or not j:
                    continue
                pairs.append((h, bool(j[f])))
            hx, jy = [p[0] for p in pairs], [p[1] for p in pairs]
            k = cohens_kappa(hx, jy) if pairs else float("nan")
            lo, hi = kappa_bootstrap(hx, jy) if pairs else (float("nan"), float("nan"))
            rows.append({"sample_set": sample_set, "field": f, "n_labeled": len(pairs),
                         "human_positive": sum(hx), "judge_positive": sum(jy),
                         "raw_agreement": (sum(a == b for a, b in pairs) / len(pairs)) if pairs else float("nan"),
                         "kappa": k, "kappa_ci_low": lo, "kappa_ci_high": hi})
    return pd.DataFrame(rows)
