# ADR-0008: Capture all four questioning layers

**Status:** Accepted · 2026-07-10

## Context

The AI intern's questioning can be recorded at four levels: (1) the full message transcript, (2) the thinking/reasoning trace, (3) tool-call actions via hooks, and (4) an explicit `register_question` tool. They are complementary, not competing, and the *discrepancies between them* are signal (abandoned questions, observer-effect inflation, implicit questioning). The AI intern produces its cycle output in the human's 7-question format (the comparable surface); the capture layers sit beneath it.

## Decision

Capture **all four** layers per run into `experiments/runs/<run_id>/` (see `schemas/capture_layer.md`), with two qualifications:

- Layers 1-3 are **passive** (no behavioral effect) — always on.
- Layer 4 is **active** (mild observer effect) — captured, but treated as an experimental variable: ablated on a subset of repetitions to quantify its distortion.
- The **question registry (layer 4) is the primary analysis surface**; layers 1-3 are audit, validation, and reconciliation input, not obligatory analysis for the pilot.

## Consequences

- Storage is cheap; the real cost is **reconciliation** — merging four overlapping records into one canonical trajectory (`harness/reconcile.py`). That linking is where the discrepancy metrics come from.
- Requires thinking enabled (layer 2) and the `mcp__scholar__register_question` tool allow-listed (layer 4).
- The human panel yields only the 7-question level → **AI-vs-human comparison stays at that symmetric level**; the live stream is for understanding the AI's process only (ADR-0002).
