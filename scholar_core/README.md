# scholar_core/ — the intern

This directory **is the intern's evolving state.** Its git history is the experiment's revision map: each Loop C write is a commit, and the diff shows exactly how the intern changed and why.

Runtime-neutral: nothing here may assume a particular runtime (see ADR-0006). The learning-vs-static switch is simply *whether Loop C is allowed to write here.*

| Folder | Evolution-stack layer | Holds |
|---|---|---|
| `persona.md` | — | who the Scholar is: goals, taste, publication aim |
| `goals/` | Goal | the research aim(s) the current work serves |
| `strategy/` | Hypothesis-design logic | principles of good question/hypothesis design; research taste |
| `concept_model/` | Concept model | working model of the disease — concept-map snapshots (one per cycle) |
| `capabilities/` | Method repertoire | skills / methods (EPAs) discovered and refined while analyzing |
| `knowledge/` | (below the stack) | validated facts, data caveats — starts rich, stays ~constant |
| `ledger/` | — | error ledger: mistake → correction → artifact change → recurrence check |

**Invariant:** growth is written here as versioned artifacts, never as a growing prompt (ADR-0001).
