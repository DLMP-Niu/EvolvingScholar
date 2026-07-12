"""scholars/sdk/cycle.py — advance one A→B→C cycle by exactly one step.

A resumable, human-in-the-loop state machine over a run directory. It does NOT
automate the PI (Loop B); it inspects the run's files, takes the single next
action, and stops with an instruction. Re-run the same command after filling
`feedback_project.yaml` to advance. Mirrors the operator flow in design-notes
(2026-07-11 cont.) and reuses the existing loop_a / pi / loop_c functions.

    python scholars/sdk/cycle.py              # start a NEW cycle (Loop A, new run)
    python scholars/sdk/cycle.py <run_dir>    # advance THAT run one step

State is derived from files (no new state store):
    unfilled feedback   → (re)build the review packet, stop for the PI
    status: needs_more  → Loop A --continue with the PI's tasks, rebuild packet, stop
    status: complete    → Loop C (system update), print the scholar_core/ diff
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "scholars" / "sdk"))
sys.path.insert(0, str(REPO / "harness"))

from loop_a import CORE, COHORT, SEED_QUESTION, resume_prompt, run_project  # noqa: E402
from pi import build_review_packet, load_final_feedback, pending_tasks  # noqa: E402
from loop_c import run_loop_c  # noqa: E402


def _feedback_state(run_dir: Path) -> str:
    """One of 'unfilled' | 'needs_more' | 'complete', derived from the feedback form."""
    fb_path = run_dir / "feedback_project.yaml"
    if not fb_path.exists():
        return "unfilled"
    review = (yaml.safe_load(fb_path.read_text()) or {}).get("review", {})
    scores = review.get("scores", {})
    filled = any(isinstance(v, dict) and v.get("score") is not None for v in scores.values())
    if not filled:
        return "unfilled"
    return review.get("status", "needs_more")


def _stop_for_pi(run_dir: Path, out: dict[str, Path]) -> None:
    print("\n[cycle] STOP — PI review needed.")
    print(f"  read:  {out['packet']}")
    print(f"  fill:  {out['feedback']}  (scores + status + new_tasks)")
    print(f"  then:  python scholars/sdk/cycle.py {run_dir}")


def advance(run_dir: Path | None) -> None:
    if run_dir is None:
        print("[cycle] step: Loop A (new run)")
        _, run_dir = asyncio.run(run_project(SEED_QUESTION))
        _stop_for_pi(run_dir, build_review_packet(run_dir))
        return

    run_dir = Path(run_dir)
    if not (run_dir / "meta.yaml").exists():
        raise SystemExit(f"{run_dir} is not a run dir (no meta.yaml)")
    meta = yaml.safe_load((run_dir / "meta.yaml").read_text())
    state = _feedback_state(run_dir)

    if state == "unfilled":
        # Idempotent: rebuild the packet; build_review_packet never clobbers a filled form.
        _stop_for_pi(run_dir, build_review_packet(run_dir))

    elif state == "needs_more":
        tasks = pending_tasks(run_dir)
        if not tasks:
            raise SystemExit(
                "status is needs_more but new_tasks is empty — add tasks or set status: complete"
            )
        sid = meta.get("session_id")
        if not sid:
            raise SystemExit(f"no session_id in {run_dir}/meta.yaml — cannot resume Loop A")
        print(f"[cycle] step: Loop A (continue, {len(tasks)} task(s))")
        asyncio.run(run_project(
            resume_prompt(tasks), resume_session_id=sid, run_dir=run_dir,
            cohort=meta.get("cohort", COHORT), cycle=int(meta.get("cycle", 1)),
        ))
        _stop_for_pi(run_dir, build_review_packet(run_dir))

    elif state == "complete":
        load_final_feedback(run_dir)  # gate: status complete + entrustment level set (ADR-0013)
        print("[cycle] step: Loop C (system update)")
        changed = asyncio.run(run_loop_c(run_dir, CORE))
        print(f"\n[cycle] DONE — cycle complete. {CORE.relative_to(REPO)}/ updated:")
        for c in changed:
            print("  -", c)
        print(f"  inspect: git diff {CORE.relative_to(REPO)}/")

    else:
        raise SystemExit(f"unknown feedback status: {state!r}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Advance one A→B→C cycle by one step.")
    ap.add_argument("run_dir", nargs="?", help="existing run dir; omit to start a new cycle")
    args = ap.parse_args()
    advance(Path(args.run_dir) if args.run_dir else None)
