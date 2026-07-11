# EvolvingScholar — project context

> This file is **neutral and minimal by design.** It loads into the Scholar (intern) runtime, so it must contain only project context appropriate for the intern to see. Developer instructions, house rules, and workflow notes belong in `CLAUDE.local.md`, which is excluded from the runtime. See `docs/adr/0007-config-isolation.md`.

## What this project is

EvolvingScholar studies how an AI research intern's **questioning and disease conceptualization evolve** across sequential gene–disease projects, under mentor (PI) guidance. Architecture: three nested loops (A: research activity · B: PI feedback · C: system update). The intern's growth lives in versioned artifacts under `scholar_core/`, never in a growing prompt.

## Hard invariant

**Growth is not prompt accumulation.** Do not attempt to make the intern "improve" by appending to its context or system prompt across cycles. All cross-project change is written as typed, versioned artifacts in `scholar_core/` by Loop C. See `docs/adr/0001-growth-is-not-prompt-accumulation.md`.

## Where things are

- `scholar_core/` — the intern's evolving state (persona, goals, strategy, concept_model, capabilities, knowledge, ledger).
- `harness/` — PI mentor, Loop C updater, evaluator (shared machinery, not the intern).
- `runtime/` — orchestration entrypoint(s).
- `docs/` — the build record (design log, ADRs, structure). Dev-facing.
