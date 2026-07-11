# Developer notes (local — NOT loaded into the intern runtime)

> This file loads in interactive Claude Code dev sessions but is excluded from the Scholar runtime (the SDK runs with `setting_sources=["project"]`, which drops the `local` tier). Put anything dev-facing here, never in `CLAUDE.md`.

## Working rules for this repo

Follow the project owner's 12-rule template (caution over speed; simplicity first; surgical changes; read before you write; fail loud). The canonical copy lives at `~/CLAUDE/CLAUDE.md` — do not import it into `CLAUDE.md`, or it would leak into the intern runtime.

## Using Claude Code subagents for development

- **Do** fan out subagents for parallel, independent, well-scoped modules once the design is frozen (e.g. build `harness/pi.py`, the question-registry schema, and the concept-map differ concurrently), and for search/research that would clutter the main thread.
- **Don't** parallelize the design-defining spine while it is still fluid — parallel agents re-derive the architecture from partial context and drift. Keep coherent design work in the main thread.

## Guardrails specific to this project

- Synthetic / de-identified data only. No real PHI in this repo.
- Keep `CLAUDE.md` neutral; keep the intern's growth in `scholar_core/` artifacts, not prompts.
- Append design decisions to `docs/design-notes.md` (dated batch on top) and record consequential ones as ADRs.
