"""Pure capture primitives — the artifact-writing hub + question schema. NO SDK
dependency, so any build arm can reuse it. See schemas/capture_layer.md.

The SDK glue (the `register_question` @tool, the PostToolUse hook, transcript/
thinking serialization) lives in `scholars/sdk/engine.py`; the raw-API arm writes
the same artifacts its own way. Layers 1-3 are passive; layer 4 (register_question)
is active and treated as a variable.
"""
from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class JsonlWriter:
    """Thread-safe append-only JSONL writer."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def append(self, record: dict[str, Any]) -> None:
        line = json.dumps(record, default=str, ensure_ascii=False)
        with self._lock, self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


@dataclass
class RunContext:
    """One Loop A run's capture destination.

    `run_no` is the per-scholar, feedback-gated iteration index (ADR-0014's
    experiment-run counter; recorded as the `run` field in capture records).
    """

    run_id: str
    run_no: int
    run_dir: Path
    seed: int | None = None

    def __post_init__(self) -> None:
        self.run_dir = Path(self.run_dir)
        self.questions = JsonlWriter(self.run_dir / "questions.jsonl")   # layer 4
        self.actions = JsonlWriter(self.run_dir / "actions.jsonl")       # layer 3
        self.thinking = JsonlWriter(self.run_dir / "thinking.jsonl")     # layer 2
        self.transcript = JsonlWriter(self.run_dir / "transcript.jsonl") # layer 1
        # Restore the question counter so a --continue run keeps incrementing ids.
        qf = self.run_dir / "questions.jsonl"
        self._qn = sum(1 for _ in qf.open(encoding="utf-8")) if qf.exists() else 0

    def next_qid(self) -> str:
        self._qn += 1
        return f"{self.run_id}-q{self._qn:04d}"


# Simple dict schema form accepted by claude_agent_sdk.tool (name -> type).
REGISTER_QUESTION_SCHEMA: dict[str, Any] = {
    "text": str,
    "cognitive_level": int,      # 1-9 ladder; agent self-tags, human-audited later
    "medical_purpose": str,      # research-mechanistic | clinical-management | counseling-pathway
    "origin": str,               # seeded | self-generated | pi-suggested | spawned
    "parent_q_id": str,          # "" if none
    "edge_type": str,            # refines | spawns | blocks | ""
    "evidence_source": str,      # literature | emr | both | ""
}

_NULLISH = {"", "none", "null", "n/a", "na"}


def _clean(v: Any) -> Any:
    """Normalize model-supplied sentinel strings ('none', '', ...) to None."""
    if isinstance(v, str) and v.strip().lower() in _NULLISH:
        return None
    return v
