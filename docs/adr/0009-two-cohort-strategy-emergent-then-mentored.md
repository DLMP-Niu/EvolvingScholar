# ADR-0009: Two-cohort analysis — emergent, then mentored (Option C)

**Status:** Accepted · 2026-07-11

## Context

Pair 1 (TTR/ATTR) ships as **two cohorts**: A (deep EMR, 230 IDs, dense) and B (registry-derived, 670 IDs, sparse). Real multi-source EMR practice is to characterize each cohort's **data elements one at a time**, map the differences (a crosswalk), and only *then* compare — because a cross-cohort result difference is meaningless until you know whether it's biology or a data-element/ascertainment artifact. Three ways to structure this were considered: (A) scaffold the workflow as a fixed pipeline, (B) let it emerge and measure the gap, (C) emergent then mentored.

## Decision

**Option C.** Do **not** scaffold the harmonization workflow. Let the intern attempt the two-cohort work; when it skips characterization or naively pools/compares, the PI feedback (Loop B) corrects it ("understand data elements first"); Loop C promotes the learned harmonization workflow into a reusable capability; it applies the method on the next cohort/pair. This reproduces the real intern's *documented* learning event (the PI gave exactly this feedback because the trainee didn't harmonize spontaneously — see `docs/2026Intern_research_note.md`).

## Consequences

- Introduces a new artifact: a per-cohort **data-element profile** + a cross-cohort **crosswalk**.
- Requires Loop B/C running; cycle-1 output may be methodologically wrong **by design** (that gap is the maturity signal).
- The harmonization workflow becomes a **transferable capability** carried to pair 2 (PMP22/CMT).
- Bootstrap with a light staged single-cohort run to validate machinery before the emergent study.
- A/B are **not poolable** (different provenance/density) — comparing them is itself an ascertainment study.
