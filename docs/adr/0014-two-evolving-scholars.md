# ADR-0014: Two evolving scholars (SDK, API) with separated experience stores

**Status:** Accepted · 2026-07-11 · refines [ADR-0010](0010-two-arms-are-demonstrations.md), retires the "cycle = research project" framing

## Context

Aligning the model with real research practice (owner) corrected two things:

1. **Per-run, feedback-gated evolution.** A **research project** (gene/disease) is a *container for many experiment runs*, not a single "cycle." Evolution accretes **per experiment run**, gated by PI feedback — a run *with* a completed review updates the scholar's store (Loop C); a run *without* feedback is captured but **skipped**. The term "cycle" conflated project with pass and is retired (→ **research project** + **experiment run**, see `CONTEXT.md`).
2. **Two evolving scholars, not one.** The two build arms are **two distinct evolving scholars** — `scholar_SDK` and `scholar_API` — with *different tool endowments*. Their accumulated skills are therefore **endowment-coupled** (an SDK skill "use WebSearch" is inexecutable for the API arm, which instead grows its own literature tool + retrieval). Sharing one experience store would entangle two incoherent trajectories and blur each one's growth curve.

*(A lab of many diverse AI interns is explicitly out of scope — the human panel is the reference, not a fleet of AI scholars.)*

## Decision

- Build **two evolving scholars**, each with its **own experience store, engine adapter, and runs**; **no cross-pollination** between them.
- **Shared, one copy:** the **dataset**, **schemas**, the **harness mechanism** (Loop B/C, reconcile, evaluator), and **common runtime-neutral primitives + initial setup** (cycle-0 persona, base prompt, seed questions, capture, EMR tools).
- **Per-scholar:** the **engine** (SDK adapter vs. raw-API adapter), the **experience store** (`core/`), and the **runs**.
- Evolution accretes **per experiment run, per scholar, gated by PI feedback**; scholars run projects **independently** (need not mirror).

This refines ADR-0010: "shared core" splits into **shared mechanism** + **per-scholar experience store**.

## Consequences

- `scholar_core/` becomes **per-scholar** (`scholars/<id>/core/`); the harness is parameterized by the scholar's core path (`loop_c.run_loop_c` already takes `core`).
- A directory restructure is required — see `docs/restructure-two-scholars.md` ("Build 5").
- The `cycle` field/args become **run**/project identifiers; "cycle" is retired in `CONTEXT.md`.
- A run with no PI feedback must be a **supported outcome** (captured, no Loop C), not a gate error or a stuck state.
