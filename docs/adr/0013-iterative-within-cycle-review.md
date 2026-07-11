# ADR-0013: Iterative within-cycle review (task-additive) via session resume

**Status:** Accepted · 2026-07-11

## Context

The real research workflow is not a single A→B→C pass. In practice: the Scholar does initial research (Loop A); the PI reviews and **assigns additional tasks** (project-focused, within-cycle); the Scholar **partially re-runs — only what is needed**, reusing prior work; this may iterate; and Loop C fires **at the end** to capture the evolution. The current single-pass `loop_a` cannot do within-cycle iteration or partial re-run.

## Decision

- The **within-cycle (project) review is iterative and task-additive**: the PI may assign more **tasks** mid-project; the Scholar addresses them; the PI may review again, until it marks the project complete. The **between-cycle (development/entrustment) review stays terminal** and feeds Loop C.
- Distinguish **Task** (a unit of work the PI assigns) from **Question** (an inquiry the Scholar raises) — see `CONTEXT.md`.
- **"Partial re-run only if needed" = SDK session resume.** Resuming the Scholar's session (`resume` / `session_id` / `continue_conversation`) with the new tasks preserves its prior context, so it does only incremental work — no hand-coded diff logic. The judgment of what needs redoing lives in the Scholar on resume, and triages PI feedback into: *re-run-needed* / *report-edit-only* / *defer-to-Loop-C*.
- **Cycle unchanged** (= research project). Within-cycle context growth is permitted by ADR-0001 (working context within a cycle); cross-cycle growth stays artifact-based (Loop C).

## Consequences

- `loop_a` must capture/return the `session_id` and gain a **continue** entry point that resumes the session and **appends** to the same run folder (question numbering and capture continue).
- `pi.py`'s within-cycle review gains a **status** (`complete` | `needs_more`) and a **`new_tasks`** list; the human PI paces the iteration.
- Post-feedback work is captured alongside the original → an **extra, granular evolution-observation surface** (mentorship landing *inside* a project, not only between projects).
- Loop C fires only when the within-cycle iteration converges (`status: complete`).
- PI-assigned tasks are recorded, so "did the Scholar address the assigned tasks" becomes measurable.
