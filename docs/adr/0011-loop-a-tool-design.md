# ADR-0011: Loop A agent tool design — minimal portable primitives; method withheld

**Status:** Accepted · 2026-07-11

## Context

Under Option C ([ADR-0009](0009-two-cohort-strategy-emergent-then-mentored.md)), the research *method* is what we study emerging and being mentored — so any tool that **encodes method** pre-empts the very learning being measured. Two reinforcing reasons also favor few, general tools: agents reason better with a small general toolset than a large specific menu, and with few general tools the intern's method becomes **visible in how it composes them** (richer capture signal). The two-arm plan ([ADR-0010](0010-two-arms-are-demonstrations.md)) additionally requires tools defined **portably** (runtime-neutral), not leaning on any one runtime's built-ins.

## Decision

Provide a **small set of explicit, portable primitives**:
- `run_analysis` — sandboxed code execution over a cohort, returning **aggregates only** (a custom portable tool, *not* built-in Bash, so it is identical across arms and mirrors how the real intern wrote analysis notebooks).
- `search_literature` (+ `fetch`) — the lit-review half of Loop A.
- `register_question` — the capture tool ([ADR-0008](0008-capture-all-four-layers.md)).
- a minimal note/report **save** for the 7-question cycle report.

**Withhold** all method-encoding tools: `characterize_cohort`, `crosswalk`, `compare_cohorts`, `test_association`, `qc_data`. Their absence is the point — it is what makes method emergence observable and mentorable. Method accrues as **self-authored skills** in `scholar_core/capabilities/` (the Voyager pattern), promoted by Loop C.

## Consequences

- Tool definitions live **once** in the runtime-neutral layer; each runtime gets a thin adapter. Endowment (which tools are allow-listed) is the per-arm knob.
- On synthetic data, `run_analysis` is acceptable with a soft output cap; when real data arrives, tighten to strict tool-side aggregation / no raw-row egress.
- The intern's growth in method is stored as diffs to `capabilities/` — the same instrument used to measure capability evolution.
