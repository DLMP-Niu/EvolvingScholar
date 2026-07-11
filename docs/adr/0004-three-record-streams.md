# ADR-0004: Three separated record streams; git as revision map

**Status:** Accepted · 2026-07-10

## Context

Three kinds of "record" look similar but serve different masters and must not be mixed: how the humans built the system, what the experiment produces, and the intern's own evolving state. Conflating them (e.g., dev docs leaking into the intern, or the intern's evolution tangled with build history) breaks both isolation and measurement.

## Decision

Keep three streams in separate homes, with git as the record engine:

| Stream | Home | Whose history |
|---|---|---|
| Build record | `docs/` | git of `docs/`+code = *how the project was built* |
| Experiment data | `experiments/` | per-run scientific data |
| Intern artifacts | `scholar_core/` | git of `scholar_core/` = *how the intern evolved* (the revision map) |

## Consequences

- The two git histories (`docs/`+code vs. `scholar_core/`) answer different questions and are never confused.
- The build record is dev-facing and stays out of the intern runtime.
- Consequential decisions are recorded as ADRs; narrative decisions go in `design-notes.md`.
