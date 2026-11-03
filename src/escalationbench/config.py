"""Load experiment config and assemble the per-condition system prompts.

The four conditions share every byte of the system prompt except one swapped
"Team priorities" paragraph. `prompt_hashes()` lets a run manifest prove which
prompt text was used.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config"
PROMPT_DIR = CONFIG_DIR / "prompts"

CONDITION_FILES = {
    "NEUTRAL": "neutral.md",
    "PLACEBO": "placebo.md",
    "SOFT_KPI": "soft_kpi.md",
    "HARD_KPI": "hard_kpi.md",
}


@dataclass
class JudgeConfig:
    model: str
    effort: str = "medium"
    max_tokens: int = 4000


@dataclass
class ExperimentConfig:
    company_name: str
    conditions: list[str]
    models: list[str]
    repeats: int
    max_turns: int
    max_tokens: int
    effort: str
    thinking_display: str
    judge: JudgeConfig
    concurrency: int = 4
    splits: dict = field(default_factory=dict)
    human_labels: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path | str = CONFIG_DIR / "experiment.yaml") -> "ExperimentConfig":
        raw = yaml.safe_load(Path(path).read_text())
        unknown = set(raw["conditions"]) - set(CONDITION_FILES)
        if unknown:
            raise ValueError(f"Unknown conditions in config: {sorted(unknown)}")
        return cls(
            company_name=raw["company_name"],
            conditions=list(raw["conditions"]),
            models=list(raw["models"]),
            repeats=int(raw["repeats"]),
            max_turns=int(raw["max_turns"]),
            max_tokens=int(raw["max_tokens"]),
            effort=raw["effort"],
            thinking_display=raw.get("thinking_display", "omitted"),
            judge=JudgeConfig(**raw["judge"]),
            concurrency=int(raw.get("concurrency", 4)),
            splits=raw.get("splits", {}),
            human_labels=raw.get("human_labels", {}),
            raw=raw,
        )


def _read(name: str) -> str:
    return (PROMPT_DIR / name).read_text().strip()


def system_prompt(condition: str, company_name: str) -> str:
    """Base + escalation policy + the condition's priorities paragraph."""
    if condition not in CONDITION_FILES:
        raise ValueError(f"Unknown condition {condition!r}")
    base = _read("base.md").replace("{company_name}", company_name)
    return "\n\n".join([base, _read("policy.md"), _read(CONDITION_FILES[condition])])


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def prompt_hashes(company_name: str) -> dict[str, str]:
    return {c: sha256_text(system_prompt(c, company_name)) for c in CONDITION_FILES}
