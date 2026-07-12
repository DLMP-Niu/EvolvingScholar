"""scholars/api/cycle.py — advance one scholar_API experiment run's A→B→C loop by one step.

The arm-2 counterpart to scholars/sdk/cycle.py: the same resumable, human-in-the-
loop state machine over a run directory, reusing the shared harness (pi, loop_c).
The only difference is the Loop A engine (raw Messages API) and how --continue
resumes: the API arm replays the persisted message history rather than a session id.

    python scholars/api/cycle.py                        # start a NEW run (Loop A)
    python scholars/api/cycle.py <run_dir>              # advance THAT run one step
    python scholars/api/cycle.py <run_dir> --skip       # no PI feedback: capture only, no Loop C
    python scholars/api/cycle.py --project TTR-ATTR --cohort B   # new run on a chosen cohort
"""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "common"))
sys.path.insert(0, str(REPO / "scholars" / "api"))
sys.path.insert(0, str(REPO / "harness"))

from engine import CORE, run_project  # noqa: E402
from projects import DEFAULT_PROJECT, resolve_cohort  # noqa: E402
from prompts import resume_prompt, seed_question  # noqa: E402
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


def _run_no(meta: dict) -> int:
    return int(meta.get("run", meta.get("cycle", 1)))


def _stop_for_pi(run_dir: Path, out: dict[str, Path]) -> None:
    print("\n[cycle] STOP — PI review needed.")
    print(f"  read:  {out['packet']}")
    print(f"  fill:  {out['feedback']}  (scores + status + new_tasks)")
    print(f"  then:  python scholars/api/cycle.py {run_dir}")
    print(f"  or:    python scholars/api/cycle.py {run_dir} --skip   (if no PI feedback for this run)")


def _mark_skipped(run_dir: Path, meta: dict) -> None:
    """Record a no-feedback run as captured-but-not-evolved (ADR-0014)."""
    meta["evolution"] = "skipped — no PI feedback for this run"
    (run_dir / "meta.yaml").write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")
    print(f"\n[cycle] SKIPPED — run {run_dir.name} captured, no PI feedback → no Loop C, store unchanged.")


def advance(run_dir: Path | None, project: str = DEFAULT_PROJECT,
            cohort: str | None = None, skip: bool = False) -> None:
    if run_dir is None:
        cohort = resolve_cohort(project, cohort)
        print(f"[cycle] step: Loop A (new run, project={project} cohort={cohort})")
        run_dir = run_project(seed_question(project, cohort), project=project, cohort=cohort)
        _stop_for_pi(run_dir, build_review_packet(run_dir))
        return

    run_dir = Path(run_dir)
    if not (run_dir / "meta.yaml").exists():
        raise SystemExit(f"{run_dir} is not a run dir (no meta.yaml)")
    meta = yaml.safe_load((run_dir / "meta.yaml").read_text())

    if skip:
        _mark_skipped(run_dir, meta)
        return

    state = _feedback_state(run_dir)

    if state == "unfilled":
        # Idempotent: rebuild the packet; build_review_packet never clobbers a filled form.
        _stop_for_pi(run_dir, build_review_packet(run_dir))

    elif state == "needs_more":
        tasks = pending_tasks(run_dir)
        if not tasks:
            raise SystemExit(
                "status is needs_more but new_tasks is empty — add tasks or set status: complete")
        print(f"[cycle] step: Loop A (continue, {len(tasks)} task(s))")
        run_project(resume_prompt(tasks), run_dir=run_dir, resume=True,
                    project=meta.get("project", DEFAULT_PROJECT), cohort=meta.get("cohort"),
                    run_no=_run_no(meta))
        _stop_for_pi(run_dir, build_review_packet(run_dir))

    elif state == "complete":
        load_final_feedback(run_dir)  # gate: status complete + entrustment level set (ADR-0013)
        print("[cycle] step: Loop C (system update)")
        changed = asyncio.run(run_loop_c(run_dir, CORE))  # shared harness Loop C is async
        print(f"\n[cycle] DONE — run complete. {CORE.relative_to(REPO)}/ updated:")
        for c in changed:
            print("  -", c)
        print(f"  inspect: git diff {CORE.relative_to(REPO)}/")

    else:
        raise SystemExit(f"unknown feedback status: {state!r}")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Advance one scholar_API experiment run's A→B→C loop by one step.")
    ap.add_argument("run_dir", nargs="?", help="existing run dir; omit to start a new run")
    ap.add_argument("--project", default=DEFAULT_PROJECT, help="research project id (new runs only)")
    ap.add_argument("--cohort", default=None, help="cohort within the project (new runs only)")
    ap.add_argument("--skip", action="store_true", help="no PI feedback: capture only, no Loop C")
    args = ap.parse_args()
    advance(Path(args.run_dir) if args.run_dir else None,
            project=args.project, cohort=args.cohort, skip=args.skip)
