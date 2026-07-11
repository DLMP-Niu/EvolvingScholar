"""Reconcile the four capture layers of a run into one canonical question
trajectory. See schemas/capture_layer.md. The evaluator turns the output into
the question-trajectory tracking structure.

Status: skeleton. Node/edge/action linking is implemented; the harder
discrepancy detectors (abandoned, blind-spot) are marked TODO.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def reconcile(run_dir: str | Path) -> dict[str, Any]:
    """Merge layers 1-4 in `run_dir` into {nodes, edges, discrepancies}."""
    run_dir = Path(run_dir)
    questions = _read_jsonl(run_dir / "questions.jsonl")  # layer 4 (primary)
    actions = _read_jsonl(run_dir / "actions.jsonl")      # layer 3
    thinking = _read_jsonl(run_dir / "thinking.jsonl")    # layer 2

    # 1. seed canonical nodes from registered questions; edges from provenance.
    nodes = {q["q_id"]: {**q, "actions": []} for q in questions}
    edges = [
        {"from": q["parent_q_id"], "to": q["q_id"], "type": q.get("edge_type") or "spawns"}
        for q in questions
        if q.get("parent_q_id")
    ]

    # 2. attach each research action to the question active at its timestamp.
    q_sorted = sorted(questions, key=lambda q: q.get("ts", 0.0))
    for act in sorted(actions, key=lambda a: a.get("ts", 0.0)):
        if act.get("tool_name") == "mcp__scholar__register_question":
            continue  # a layer-4 event, not a research action
        active = _active_question(q_sorted, act.get("ts", 0.0))
        if active is not None:
            nodes[active["q_id"]]["actions"].append(act.get("tool_use_id"))

    # 3. cross-layer discrepancies — themselves metrics.
    discrepancies = {
        # registered but produced no downstream action → possible observer-effect inflation
        "inflation": [qid for qid, n in nodes.items() if not n["actions"]],
        # question-shaped thinking never registered → considered-but-abandoned
        "abandoned": _abandoned_candidates(thinking, questions),
        # TODO blind_spot: actions with no active question in window (implicit questioning)
    }

    return {"nodes": list(nodes.values()), "edges": edges, "discrepancies": discrepancies}


def _active_question(q_sorted: list[dict[str, Any]], ts: float) -> dict[str, Any] | None:
    """The most recently registered question at or before `ts`."""
    active: dict[str, Any] | None = None
    for q in q_sorted:
        if q.get("ts", 0.0) <= ts:
            active = q
        else:
            break
    return active


def _abandoned_candidates(
    thinking: list[dict[str, Any]], questions: list[dict[str, Any]]
) -> list[str]:
    """Question-shaped statements in the thinking trace that were never registered.

    TODO: implement an extraction pass (rule-based or LLM) that pulls question-
    shaped sentences from `thinking`, fuzzy-matches them against registered
    `text`, and returns the unmatched ones. Placeholder returns []."""
    return []


if __name__ == "__main__":  # pragma: no cover
    import sys

    print(json.dumps(reconcile(sys.argv[1]), indent=2, default=str))
