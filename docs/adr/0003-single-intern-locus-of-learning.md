# ADR-0003: Single intern as the locus of learning; subagents execute only

**Status:** Accepted · 2026-07-10

## Context

The intern's execution could be decomposed into subagents (lit-review, EMR-analysis, hypothesis). But the unit of study is *one intern* whose concept model, questioning, and methods evolve. Scattering growth across independently-evolving subagents would fragment the "how the intern grew" narrative and make it unsnapshottable.

## Decision

Keep the **locus of learning singular and legible.** Separate agents are used only where validity requires it — the **PI-mentor** and the **evaluator/judge** must be distinct from the intern (judge ideally a different model family, to avoid self-enhancement bias). Any *execution* subagents inside Loop A are capabilities the single intern owns; they read from, and Loop C writes to, one canonical artifact store in `scholar_core/` (the Kosmos shared-world-model pattern).

## Consequences

- For the feasibility pilot, start minimal: **one intern + separate mentor + separate evaluator.** Add execution subagents only when a concrete task forces it.
- Subagents don't inherit skills/history; grant each explicitly. The single canonical store is what lets them share the intern's evolving knowledge without fragmenting it.
- Note: this concerns the *experiment runtime*. Using Claude Code subagents as a *development* tool is a separate, unrestricted choice (see `CLAUDE.local.md`).
