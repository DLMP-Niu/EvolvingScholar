# Project Structure

_A presentation-ready map of the repository: what each part is, and how it maps to the design. Last updated 2026-07-10._

The layout separates **three record streams that must never be mixed** (see [ADR-0004](adr/0004-three-record-streams.md)):

1. **Build record** — how *we* built the system (`docs/`).
2. **Experiment data** — what the runs produce (`experiments/`).
3. **Intern artifacts** — the agent's evolving state (`scholar_core/`).

## Annotated tree

```
EvolvingScholar/
├── README.md                 Presentation overview
├── CLAUDE.md                 Minimal, NEUTRAL project context — loads into the intern runtime, kept clean
├── CLAUDE.local.md           Developer rules & workflow — dev-only, excluded from the intern runtime
│
├── scholar_core/             ┌─ THE INTERN (versioned; git diffs of this dir = the evolution record)
│   ├── persona.md            │  who the Scholar is: goals, taste, publication aim
│   ├── goals/                │  ← evolution-stack: research goals the work serves
│   ├── strategy/             │  ← evolution-stack: hypothesis-design logic, research taste
│   ├── concept_model/        │  ← evolution-stack: working model of the disease (concept-map snapshots)
│   ├── capabilities/         │  ← evolution-stack: skills / methods (EPAs)
│   ├── knowledge/            │  validated facts, data caveats (roughly constant — the intern starts knowledge-rich)
│   └── ledger/               └─ error ledger: mistake → correction → artifact change → recurrence check
│
├── harness/                  ┌─ SHARED experiment machinery — NOT the intern (a different locus)
│   ├── pi.py                 │  Loop B: the PI-mentor rubric + feedback
│   ├── loop_c.py             │  Loop C: reads trajectory + feedback → writes scholar_core/
│   └── evaluator.py          └─ builds the tracking structures (question trajectory, revision map, transfer matrix)
│
├── runtime/                  Orchestration entrypoint(s). Single runtime for the pilot;
│                             a second build arm (SDK vs. raw API) is deferred — see ADR-0006.
│
├── experiments/              ┌─ EXPERIMENT DATA (the scientific output)
│   ├── runs/                 │  per-run configs + logs
│   └── results/              └─ trajectories, revision maps, transfer matrices, plots
│
├── data/                     Synthetic EMR cohort + curated literature for the TTR/ATTR pilot
│
└── docs/                     ┌─ THE BUILD RECORD (dev-facing — the intern never reads this)
    ├── project-structure.md  │  this file
    ├── design-notes.md       │  running design log (newest dated batch on top)
    ├── adr/                  │  architecture decision records — the "why" behind each choice
    └── references/           └─ source PDFs (download separately; not committed)
```

## How the tree maps to the design

**Three loops → three homes.**
- Loop A (research activity) runs from `runtime/`, using capabilities in `scholar_core/`.
- Loop B (PI feedback) is `harness/pi.py`.
- Loop C (system update) is `harness/loop_c.py`, and it writes **only** to `scholar_core/`.

**The evolution stack → `scholar_core/` subfolders.** Each layer that matures has a versioned home, so its change over cycles is a diff. The learning-vs-static switch is simply *whether Loop C is allowed to write to `scholar_core/`.*

**Two git histories, never confused.**
- History of `docs/` + code = *how the project was built*.
- History of `scholar_core/` = *how the intern evolved* (this **is** the revision map — the science).

## Isolation & the two `CLAUDE.md` tiers

The repo lives where **no ancestor directory has a `CLAUDE.md`**, so personal/global rules cannot leak into experiment agents.
- `CLAUDE.md` — minimal and neutral; it loads into the intern runtime, so it stays clean.
- `CLAUDE.local.md` — developer rules; loaded in interactive dev sessions but **excluded from the intern runtime** (the SDK runs with `setting_sources=["project"]`, which drops the `local` tier).

See [ADR-0007](adr/0007-config-isolation.md).

## Renaming the project

The directory name is provisional. To rename: `git mv` is unnecessary for the top dir — just rename the folder; git history follows. Only two spots reference the name textually (this file and `README.md`); update those and you're done.
