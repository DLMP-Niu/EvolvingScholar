# ADR-0001: Growth is not prompt accumulation

**Status:** Accepted · 2026-07-10

## Context

Self-improving agents can "learn" either by accumulating context (a growing prompt/system message — as Google's AI Co-Scientist does, appending meta-feedback each iteration) or by writing to external, structured state. The project's contribution depends on which mechanism it uses.

## Decision

The intern evolves **only** through updates to external, typed, versioned artifacts in `scholar_core/` (written by Loop C). It must not evolve by persisting a swelling prompt/context between cycles. Within a single cycle the intern naturally uses working context; what is forbidden is carrying that forward as the *growth mechanism*.

## Consequences

- **Pro:** it is the project's actual research bet; it keeps evolution legible (every change is a diff to a named artifact — the instrument for observing concept/skill change); it removes the context-length confound from the evolution measurement.
- **Cost:** requires disciplined artifact schemas and a Loop C that writes them, rather than the easier "append to prompt."
- **Tested by:** a flat-context-dump vs. structured-artifacts ablation.
