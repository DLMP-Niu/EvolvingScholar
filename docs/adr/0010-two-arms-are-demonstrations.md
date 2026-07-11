# ADR-0010: Two build arms are demonstrations, not a controlled contrast

**Status:** Accepted · 2026-07-11 · refines [ADR-0006](0006-runtime-second-arm-deferred.md)

## Context

The plan builds the intern two ways: (1) raw Messages **API** + hand-built tools/subagents, and (2) **Claude Code / Agent SDK**. The runtimes differ fundamentally in **built-in tools**: Claude Code/SDK ship rich built-ins (Bash, Read, WebSearch, subagents, skills) — a "super-intern" from day one; the raw API ships none — a "basic" agent that must accumulate capability over cycles. This raised the question: is the two-arm comparison a *controlled scientific contrast* or an *engineering demonstration*?

## Decision

The two arms are **engineering demonstrations of two build approaches — not a controlled scientific contrast.** The science (evolving capabilities + evolving questions) is measured **within each arm**, never as a head-to-head. Different starting endowments are **intended**, not confounds to eliminate. Endowment is a **per-arm config knob** (the tool allow-list), not a code fork.

## Consequences

- **One shared runtime-neutral core** (`scholar_core` + `harness` + portable tools + capture), built once; each arm is a **thin adapter**.
- Each arm uses its **natural endowment**: API arm = minimal hand-built tools (novice that grows); Claude Code arm = rich built-ins (super-intern).
- **Calibration:** expect *vivid* capability/question growth on the basic API arm, and *compressed* growth on the super-intern (it starts near-ceiling on general capability, so its learning curve is masked). The API arm is the headline science vehicle.
- **Sequencing:** build the shared core → validate Loop A→B→C on the SDK first (fastest) with a *restrained* allow-list so growth is observable → then build the raw-API arm as the primary "novice grows" demo.
- If a controlled capability contrast is ever wanted, do it by varying the allow-list **within one runtime**, not by switching engines (which conflates endowment + orchestration).
