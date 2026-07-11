# ADR-0005: Do not handicap starting knowledge

**Status:** Accepted · 2026-07-10

## Context

An LLM intern begins **knowledge-saturated but skill/judgment-poor** — the opposite profile from a human student, who climbs all rungs at once. We could handicap the AI's knowledge to make a knowledge-acquisition curve observable and more human-comparable, or leave it intact.

## Decision

**Do not handicap.** Accept that the intern starts knowledge-rich. Because knowledge is then held roughly constant, any capability gain across cycles is attributable to **reasoning, skill, and research judgment** — not knowledge acquisition.

## Consequences

- The AI isolates, in a controlled way, a variable (reasoning vs. knowledge) that is hopelessly entangled in human training — a genuine contribution.
- The AI's growth curve is *expected* to differ in shape from a human's; that difference is the finding, not a flaw.
- Requires measuring knowledge and reasoning **separately** (periodically re-probe pure knowledge to confirm it stays flat, so gains attribute to reasoning).
- Alternative (handicap) is a different, also-interesting experiment — deferred, not discarded.
