"""Load/append a scholar's accumulated experience store (ADR-0001). Pure — no SDK.

`load_scholar_core` is the retrieval side: it reads the store into context, rather
than growing a prompt. Load-all suffices for the pilot's small library; switch to
relevance-retrieval once it grows. `next_run_no` derives the per-scholar,
feedback-gated run index from the evolution record (one revision_map entry per
completed Loop C), so a fresh run is numbered as the Nth evolution iteration.
"""
from __future__ import annotations

from pathlib import Path


def load_scholar_core(core: Path) -> str:
    """Read accumulated skills + strategy from `core/` into a prompt appendix.
    Returns '' when nothing has been learned yet (run 0)."""
    core = Path(core)
    parts: list[str] = []
    for sub in ("capabilities", "strategy"):
        for f in sorted((core / sub).glob("*.md")):
            parts.append(f"### {sub}/{f.name}\n{f.read_text(encoding='utf-8').strip()}")
    if not parts:
        return ""
    return ("\n\n# Your accumulated skills and research strategy from prior work — "
            "apply them by default.\n\n" + "\n\n".join(parts))


def next_run_no(core: Path) -> int:
    """The next feedback-gated run index for this scholar = (# completed Loop C
    revisions) + 1. Reads `core/revision_map.jsonl`; returns 1 for a fresh store."""
    rm = Path(core) / "revision_map.jsonl"
    n = sum(1 for _ in rm.open(encoding="utf-8")) if rm.exists() else 0
    return n + 1
