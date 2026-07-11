# ADR-0006: Defer the second build arm (SDK vs. raw API)

**Status:** Accepted · 2026-07-10

## Context

The original brief proposed comparing two runtimes (Claude Code / Agent SDK vs. raw Messages API) over shared `scholar_core/` + `harness/`. That comparison is about *orchestration style* and is now secondary to the headline (questioning evolution, ADR-0002). Scaffolding two empty runtime arms up front is speculative (violates simplicity-first).

## Decision

Ship a **single `runtime/`** for the feasibility pilot. Keep `scholar_core/` and `harness/` runtime-neutral so a second arm can be added later without restructuring. Record the two-arm comparison as an open decision, not built yet.

## Consequences

- Faster path to the feasibility result.
- The runtime-neutral boundary must be respected now (no runtime-specific assumptions leaking into `scholar_core/`/`harness/`) so the option stays cheap to exercise later.
- Revisit after the pilot: is the orchestration comparison worth a second arm, or has the question been answered another way?
