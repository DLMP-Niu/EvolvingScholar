# ADR-0012: Pilot success criteria (pre-registered)

**Status:** Accepted · 2026-07-11 (grilling session)

## Context

With human-expert attainment fenced off as a non-goal (see `docs/design-notes.md` scope note), the pilot needs an **honest, pre-registered** bar — otherwise it can't distinguish real signal from post-hoc storytelling (the overclaiming failure the background eval found in AI-Scientist systems).

## Decision

Success is **staged (option c)**:

1. **Feasibility gate** — the cycle runs end-to-end: Scholar researches → human-PI feedback → Loop C writes *versioned* artifacts → the next cycle consumes them. Evolution is **legible**: extractable EPAs after each cycle (simplest honest floor = a sentence appended to a `skill.md`).
2. **Directional evolution** — at least one **pre-registered** signal moves the expected way across cycles, robust across repetitions. Pre-registered signals: **cross-project method reuse (TTR → PMP22)** and **rising autonomy in question/goal-setting**. A **null result is defined before running.**

**Demo value:** compare the AI-Scholar's cycle experience against the human intern's 7-question record (`docs/2026Intern_research_note.md`).

**Explicitly NOT success:** reaching human-expert level (out of scope).

## Consequences

- Winning signals are named **before** any run; nulls are reported honestly.
- "Surprising results" on the synthetic/workflow-grade data means surprising **Scholar behavior** (an unexpected question, an invented method, or correctly catching data artifacts like the 0–47,330 glucose values) — **not** biological findings, which await the governed real-data track.
- The EPA-extraction-per-cycle is the concrete evolution readout; the two pre-registered signals are the science bar.
