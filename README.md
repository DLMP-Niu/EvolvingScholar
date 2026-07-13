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

> **Design invariant — growth is NOT prompt accumulation.** The intern does not evolve by growing an ever-longer prompt. Cross-project growth happens only through updates to versioned artifacts under each scholar's [`core/`](scholars/), so "the intern evolved" is a legible git diff — not a swelling context window. See [ADR-0001](docs/adr/0001-growth-is-not-prompt-accumulation.md).

### Workflow

```mermaid
flowchart TB
    IN["Gene–disease project<br/>seed questions · synthetic EMR cohort · literature"]

    subgraph A["Loop A · Research  (inner)"]
      A1["Raise and pursue questions<br/>literature review + EMR analysis"]
      A2["Findings · report<br/>+ new, higher-rung questions"]
      A1 --> A2
    end

    subgraph B["Loop B · Intern ↔ PI  (middle)"]
      B1["Structured rubric feedback<br/>scores · directives · tasks"]
      B2["Entrustment level (1 → 5)"]
      B1 --> B2
    end

    subgraph C["Loop C · System update  (outer — the research contribution)"]
      C1["Write typed, versioned artifacts<br/>only when gated by feedback"]
      CORE["core/<br/>capabilities = EPAs · knowledge<br/>strategy · goals · guardrails"]
      C1 --> CORE
    end

    IN --> A1
    A2 --> B1
    B1 -.->|"needs_more: new tasks"| A1
    B2 --> C1
    CORE ==>|"carried into the next run — growth is a diff, not a bigger prompt"| IN

    CORE --> LADDER["Core EPA growth mimics a human trainee<br/>observe → assist → act independently → supervise others"]

    subgraph FUT["Future aims"]
      F1["Compare EPA growth<br/>Scholar 1 (SDK) vs Scholar 2 (API)"]
      F2["Characterize the spread of<br/>AI self-learning behavior"]
    end
    LADDER -.->|"read out per scholar"| F1
    LADDER -.-> F2

    classDef a fill:#e9f1ff,stroke:#3b6fd4,color:#12213f;
    classDef b fill:#fff3df,stroke:#c98a1e,color:#3a2a08;
    classDef c fill:#e9f8ef,stroke:#2f9e5f,color:#0c3320;
    classDef core fill:#c9edd6,stroke:#1f8a4c,stroke-width:2px,color:#0c3320;
    classDef ladder fill:#fdf1c4,stroke:#c99a1e,stroke-width:2px,color:#3a2e05;
    classDef fut fill:#eef0f4,stroke:#9aa2b1,color:#2a2f3a;
    classDef io fill:#ffffff,stroke:#6b7280,color:#1f2430;
    class A1,A2 a;
    class B1,B2 b;
    class C1 c;
    class CORE core;
    class LADDER ladder;
    class F1,F2 fut;
    class IN io;
```

- **Loop A → B → C is one experiment run.** Loop B may return `needs_more` (new PI tasks) for a partial re-run before it completes.
- **The green path is the contribution:** Loop C writes the earned EPAs into `core/capabilities/`, which are carried into the next run — the growth curve *is* the git diff.
- **The gold node is the human-learner analogy:** EPAs accrue along the clinical entrustment ladder (observe → independent → supervise), the same scaffold a trainee climbs.

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

**Working pilot — `v0.1.0`.** Both scholars are built and each has completed at least one full **A → B → C** run on the first project, **TTR / hereditary transthyretin amyloidosis (ATTR)** (cohort A):

- **Scholar 1 (SDK)** — Claude Agent SDK, rich tools.
- **Scholar 2 (API)** — raw Messages API, minimal tools; at run 1, entrustment **level 2**, with 4 earned EPAs.

Loop A/B/C are implemented; the PI is **human-in-the-loop** (LLM-PI deferred). See [`docs/design-notes.md`](docs/design-notes.md) for the running log, [`docs/adr/`](docs/adr/) for decisions, and [`docs/demo/`](docs/demo/) for run-replay visuals.

## Repo map

```
scholars/<id>/  the two evolving scholars (sdk, api): engine.py + core/ (versioned — git history = the evolution record) + runs/
common/         shared SDK-free primitives: capture, EMR tools, prompts, projects, persona
harness/        shared experiment machinery: PI mentor, Loop C updater, evaluator
schemas/        record schemas: capture layers, question registry, review rubrics
experiments/    cross-scholar analysis outputs (results/): trajectories, transfer matrix, plots
data/           synthetic EMR + curated literature for the pilot
docs/           the build record: design log, ADRs, this structure doc, references
```

Full annotated structure: [`docs/project-structure.md`](docs/project-structure.md).
