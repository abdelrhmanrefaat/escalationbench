"""Load experiment config and assemble the per-condition system prompts.

The four conditions share every byte of the system prompt except the
"Team priorities" section (DECISIONS.md D-020). MITIGATION is the INCENTIVE text
verbatim plus one scorecard-policy paragraph. `prompt_hashes()` lets a run manifest prove which
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
    "INCENTIVE": "incentive.md",
    "PRESSURE": "pressure.md",
    "MITIGATION": "mitigation.md",
}
PROVIDERS = ("anthropic", "openai")


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
    providers: dict[str, str] = field(default_factory=dict)   # model id -> provider
    gate: dict = field(default_factory=dict)
    splits: dict = field(default_factory=dict)
    human_labels: dict = field(default_factory=dict)
    raw: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path | str = CONFIG_DIR / "experiment.yaml") -> "ExperimentConfig":
        raw = yaml.safe_load(Path(path).read_text())
        unknown = set(raw["conditions"]) - set(CONDITION_FILES)
        if unknown:
            raise ValueError(f"Unknown conditions in config: {sorted(unknown)}")
        providers: dict[str, str] = {}
        for m in raw["models"]:
            mid, prov = (m, "anthropic") if isinstance(m, str) else (m["id"], m.get("provider", "anthropic"))
            if prov not in PROVIDERS:
                raise ValueError(f"Unknown provider {prov!r} for model {mid!r}; expected one of {PROVIDERS}")
            providers[mid] = prov
        providers.setdefault(raw["judge"]["model"], raw["judge"].get("provider", "anthropic"))
        judge = {k: v for k, v in raw["judge"].items() if k != "provider"}
        return cls(
            company_name=raw["company_name"],
            conditions=list(raw["conditions"]),
            models=[m if isinstance(m, str) else m["id"] for m in raw["models"]],
            repeats=int(raw["repeats"]),
            max_turns=int(raw["max_turns"]),
            max_tokens=int(raw["max_tokens"]),
            effort=raw["effort"],
            thinking_display=raw.get("thinking_display", "omitted"),
            judge=JudgeConfig(**judge),
            concurrency=int(raw.get("concurrency", 4)),
            providers=providers,
            gate=raw.get("gate", {"enabled": True, "max_tokens": 4000}),
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


def gate_system_prompt(company_name: str) -> str:
    """Knowledge-gate system prompt (D-021): base + policy, with NO condition section."""
    base = _read("base.md").replace("{company_name}", company_name)
    return "\n\n".join([base, _read("policy.md")])


def gate_instructions() -> str:
    return _read("gate.md")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def prompt_hashes(company_name: str) -> dict[str, str]:
    out = {c: sha256_text(system_prompt(c, company_name)) for c in CONDITION_FILES}
    out["GATE"] = sha256_text(gate_system_prompt(company_name) + "\n\n" + gate_instructions())
    return out
