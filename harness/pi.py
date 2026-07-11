"""Loop B — PI review (human-in-the-loop). Build 2.

Given a Loop A run, `build_review_packet()` assembles a human-readable packet
(`review_packet.md`) plus a structured feedback scaffold (`feedback_project.yaml`)
for the human PI to fill; `load_feedback()` validates the completed form. Loop C
(Build 3) consumes it.

This is the WITHIN-cycle (project) review — scores the research work. The
between-cycle development/entrustment review is a later step. Rubric mirrors
`schemas/review_rubric_project.md`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from reconcile import reconcile  # noqa: E402

# Within-cycle project rubric dimensions — mirrors schemas/review_rubric_project.md.
# NOTE: grilling + the real intern's PI feedback recommend adding research_framing,
# source_quality, method_sequencing, bias_awareness — add here AND in the schema doc
# together when that rubric is formalized (kept in sync deliberately).
REVIEW_DIMENSIONS = [
    "literature_grounding",
    "citation_integrity",
    "data_analysis_validity",
    "numerical_sanity",
    "reasoning_quality",
    "hypothesis_quality",
    "escalation_appropriateness",
    "self_correction",
]

# Between-cycle development/entrustment dimensions (schemas/review_rubric_development.md).
# Filled only at project completion — the combined final review that feeds Loop C.
DEVELOPMENT_DIMENSIONS = [
    "concept_model_growth",
    "questioning_maturation",
    "hypothesis_logic",
    "method_repertoire",
    "goal_autonomy",
    "error_recurrence",
]


def _read_jsonl(p: Path) -> list[dict[str, Any]]:
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def build_review_packet(run_dir: str | Path) -> dict[str, Path]:
    """Write review_packet.md (for the PI to read) + feedback_project.yaml (to fill)."""
    run_dir = Path(run_dir)
    meta = yaml.safe_load((run_dir / "meta.yaml").read_text()) if (run_dir / "meta.yaml").exists() else {}
    questions = _read_jsonl(run_dir / "questions.jsonl")
    traj = reconcile(run_dir)
    report = (run_dir / "report.md").read_text() if (run_dir / "report.md").exists() else "(no report produced)"

    acts = {n["q_id"]: len(n["actions"]) for n in traj["nodes"]}
    lines = [
        f"# PI Review Packet — {meta.get('run_id', run_dir.name)}",
        f"\n**Cohort:** {meta.get('cohort')}  ·  **Cycle:** {meta.get('cycle')}",
        f"\n**Seed:** {str(meta.get('seed_question', '')).strip()}",
        "\n## Registered questions (trajectory)",
    ]
    for q in questions:
        parent = f" (from {q['parent_q_id']})" if q.get("parent_q_id") else ""
        lines.append(
            f"- **{q['q_id']}** — L{q['cognitive_level']} · {q['medical_purpose']} · "
            f"{q['origin']}{parent} · {acts.get(q['q_id'], 0)} analyses\n    {q['text']}"
        )
    if traj["edges"]:
        lines.append("\n**Edges:** " + ", ".join(f"{e['from']}→{e['to']} ({e['type']})" for e in traj["edges"]))
    disc = traj.get("discrepancies", {})
    lines.append(f"\n**Capture discrepancies:** inflation={len(disc.get('inflation', []))} · "
                 f"abandoned={len(disc.get('abandoned', []))}")
    lines.append("\n## Report\n\n" + report)

    packet = run_dir / "review_packet.md"
    packet.write_text("\n".join(lines), encoding="utf-8")

    fb_path = run_dir / "feedback_project.yaml"
    if not fb_path.exists():  # never clobber a form the PI already filled
        scaffold = {
            "review": {
                "type": "project",
                "run_id": meta.get("run_id", run_dir.name),
                "cohort": meta.get("cohort"),
                "cycle": meta.get("cycle"),
                "reviewer": "owner",
                "scores": {d: {"score": None, "note": ""} for d in REVIEW_DIMENSIONS},
                "directives": [{"q_id": q["q_id"], "directive": ""} for q in questions],
                # Iterative within-cycle review (ADR-0013): set status to 'needs_more'
                # and list new_tasks to send the Scholar back for a partial re-run;
                # set 'complete' when the project is done and ready for Loop C.
                "status": "needs_more",
                "new_tasks": [],
                # Filled ONLY at completion (status: complete) — the combined final
                # development/entrustment review that feeds Loop C.
                "development": {
                    "scores": {d: {"score": None, "note": ""} for d in DEVELOPMENT_DIMENSIONS},
                    "entrustment": {"overall_level": None, "per_capability": {}},
                },
                "overall_note": "",
            }
        }
        fb_path.write_text(yaml.safe_dump(scaffold, sort_keys=False), encoding="utf-8")

    return {"packet": packet, "feedback": fb_path}


def load_feedback(run_dir: str | Path) -> dict[str, Any]:
    """Load + validate the filled feedback form (at least one dimension scored)."""
    fb_path = Path(run_dir) / "feedback_project.yaml"
    if not fb_path.exists():
        raise FileNotFoundError(f"no feedback at {fb_path} — run build_review_packet first")
    fb = yaml.safe_load(fb_path.read_text())
    scores = fb.get("review", {}).get("scores", {})
    filled = [d for d, v in scores.items() if isinstance(v, dict) and v.get("score") is not None]
    if not filled:
        raise ValueError(f"feedback not filled — every score is null in {fb_path}")
    return fb


def load_final_feedback(run_dir: str | Path) -> dict[str, Any]:
    """Load + validate the COMBINED final review that feeds Loop C: the project
    form must be filled, marked `status: complete`, and carry an entrustment level
    (ADR-0013). Raises until the final review is done."""
    fb = load_feedback(run_dir)  # project scores filled
    review = fb.get("review", {})
    if review.get("status") != "complete":
        raise ValueError("final review not complete — set review.status: complete before Loop C")
    level = review.get("development", {}).get("entrustment", {}).get("overall_level")
    if level is None:
        raise ValueError("no entrustment level — fill review.development.entrustment.overall_level")
    return fb


def pending_tasks(run_dir: str | Path) -> list[str] | None:
    """The PI's newly-assigned tasks if the within-cycle review asked for more work
    (status: needs_more), else None (project complete / no tasks). Drives
    `loop_a.py --continue` (ADR-0013)."""
    fb_path = Path(run_dir) / "feedback_project.yaml"
    if not fb_path.exists():
        return None
    review = (yaml.safe_load(fb_path.read_text()) or {}).get("review", {})
    if review.get("status") != "needs_more":
        return None
    tasks = [t for t in (review.get("new_tasks") or []) if str(t).strip()]
    return tasks or None


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="PI review (Loop B) for a Loop A run.")
    ap.add_argument("run_dir")
    ap.add_argument("--load", action="store_true", help="validate the filled feedback instead of building the packet")
    a = ap.parse_args()
    if a.load:
        fb = load_feedback(a.run_dir)
        n = sum(1 for v in fb["review"]["scores"].values() if v.get("score") is not None)
        print(f"feedback OK — {n} dimension(s) scored")
    else:
        out = build_review_packet(a.run_dir)
        print("wrote:", out["packet"])
        print("wrote:", out["feedback"], "→ fill it in, then re-run with --load")
