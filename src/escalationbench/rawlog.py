"""Append-only JSONL storage for a run. This is the raw data every number comes from.

runs/<run_id>/
  manifest.json        config, prompt hashes, git commit, prereg commit, dry_run flag
  calls.jsonl          one line per API call: full request, full response, timing, usage, cost
  conversations.jsonl  one line per finished (ticket, condition, model, repeat) cell
  judgments.jsonl      one line per judged conversation

calls.jsonl doubles as the cache: a call whose key already has a successful
response is never sent (or billed) again, which also makes runs resumable.
"""
from __future__ import annotations

import hashlib
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

RUNS_DIR = Path(__file__).resolve().parents[2] / "runs"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def call_key(params: dict, rep: int, kind: str) -> str:
    """Cache key: the exact request plus the repeat index (so repeats are distinct samples)."""
    return hashlib.sha256(canonical_json({"kind": kind, "rep": rep, "params": params}).encode()).hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


class RunStore:
    def __init__(self, run_id: str, runs_dir: Path = RUNS_DIR):
        self.run_id = run_id
        self.dir = Path(runs_dir) / run_id
        self.dir.mkdir(parents=True, exist_ok=True)
        self.calls_path = self.dir / "calls.jsonl"
        self.convs_path = self.dir / "conversations.jsonl"
        self.judg_path = self.dir / "judgments.jsonl"
        self.manifest_path = self.dir / "manifest.json"
        self._lock = threading.Lock()
        self._cache: dict[str, dict] = {}
        for rec in read_jsonl(self.calls_path):
            if rec.get("response") is not None and rec.get("error") is None:
                self._cache[rec["key"]] = rec["response"]

    # --- cache ---------------------------------------------------------------
    def cached_response(self, key: str) -> dict | None:
        with self._lock:
            return self._cache.get(key)

    def spent_usd(self) -> float:
        return sum(r.get("cost_usd") or 0.0 for r in read_jsonl(self.calls_path) if not r.get("cache_hit"))

    # --- writes --------------------------------------------------------------
    def _append(self, path: Path, rec: dict) -> None:
        line = canonical_json(rec) + "\n"
        with self._lock:
            with path.open("a", encoding="utf-8") as f:
                f.write(line)
                f.flush()

    def log_call(self, rec: dict) -> None:
        self._append(self.calls_path, rec)
        if rec.get("response") is not None and rec.get("error") is None:
            with self._lock:
                self._cache[rec["key"]] = rec["response"]

    def log_conversation(self, rec: dict) -> None:
        self._append(self.convs_path, rec)

    def log_judgment(self, rec: dict) -> None:
        self._append(self.judg_path, rec)

    # --- reads ---------------------------------------------------------------
    def conversations(self, latest_only: bool = True) -> list[dict]:
        """Latest record per cell (a retried API_ERROR cell is superseded by its retry)."""
        recs = read_jsonl(self.convs_path)
        if not latest_only:
            return recs
        latest: dict[str, dict] = {}
        for r in recs:
            latest[r["cell_id"]] = r
        return list(latest.values())

    def completed_cells(self, include_errors: bool = True) -> set[str]:
        return {
            r["cell_id"]
            for r in self.conversations()
            if include_errors or r["status"] != "API_ERROR"
        }

    def judgments(self) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for r in read_jsonl(self.judg_path):
            out[r["cell_id"]] = r
        return out

    def write_manifest(self, manifest: dict) -> None:
        existing = json.loads(self.manifest_path.read_text()) if self.manifest_path.exists() else {}
        history = existing.get("invocations", [])
        history.append(manifest)
        self.manifest_path.write_text(json.dumps({"run_id": self.run_id, "invocations": history}, indent=2, default=str))

    def manifest(self) -> dict:
        return json.loads(self.manifest_path.read_text()) if self.manifest_path.exists() else {}

    def is_dry_run(self) -> bool:
        inv = self.manifest().get("invocations", [])
        return any(i.get("dry_run") for i in inv)
