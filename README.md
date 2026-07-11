# EvolvingScholar

**Guided self-evolution of an AI research intern through sequential gene–disease projects.**

> ⚠️ Working title / directory name is provisional and may be renamed. Git history is name-independent, so a rename is safe — see [`docs/project-structure.md`](docs/project-structure.md).

## What this is

An AI "research intern" (the **Scholar**) that learns the way a real trainee does — mentor-guided, improving across a *sequence* of gene–disease projects — rather than acting as an autonomous co-scientist. Given a gene and a disease it generates research questions, reviews the literature, analyzes (synthetic) EMR data to test associations, and proposes testable hypotheses. At checkpoints it "meets its PI" and receives structured feedback that drives its growth before the next project.

**The question this project actually asks:** *how does research questioning and disease conceptualization evolve* — studied across a human reference panel (college intern → master's → medical student → resident) and an AI intern across cycles. The AI is a **controllable model system** for a developmental process that is knowledge-entangled and hard to isolate in humans.

## The core mechanism — three nested loops

- **Loop A — Research activity** (inner): the intern does the research for one gene–disease pair.
- **Loop B — Intern ↔ PI** (middle): structured mentor feedback at checkpoints.
- **Loop C — System update** (outer): rewrites the intern's **external, typed, versioned artifacts** between projects.

> **Design invariant — growth is NOT prompt accumulation.** The intern does not evolve by growing an ever-longer prompt. Cross-project growth happens only through updates to versioned artifacts in [`scholar_core/`](scholar_core/), so "the intern evolved" is a legible git diff — not a swelling context window. See [ADR-0001](docs/adr/0001-growth-is-not-prompt-accumulation.md).

## What evolves — the evolution stack

From abstract to concrete, these mature in a rough order that traces the student → resident → PhD → PI path:

| Layer | What matures |
|---|---|
| **Goal** | the research aim the work serves |
| **Hypothesis-design logic** | the principles of good question/hypothesis design |
| **Question-asking** | which questions it poses (cognitive × medical-purpose axes) |
| **Concept model** | its working model of the disease |
| **Method repertoire** | good methods found and documented while analyzing |

Knowledge sits *below* this stack, saturated and roughly constant — everything in the stack is the **reasoning/experience** side, made observable.

## Status

**Design → scaffolding.** First gene–disease pair: **TTR / hereditary transthyretin amyloidosis (ATTR)**. Not yet implemented. See [`docs/design-notes.md`](docs/design-notes.md) for the running design log and [`docs/adr/`](docs/adr/) for decisions.

## Repo map

```
scholar_core/   the intern (versioned — its git history = the evolution record)
harness/        shared experiment machinery: PI mentor, Loop C updater, evaluator
runtime/        orchestration entrypoint(s)
experiments/    run configs, logs, results (the scientific data)
data/           synthetic EMR + curated literature for the pilot
docs/           the build record: design log, ADRs, this structure doc, references
```

Full annotated structure: [`docs/project-structure.md`](docs/project-structure.md).
