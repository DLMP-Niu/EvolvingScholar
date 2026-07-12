# scholars/api/core/ — the scholar_API intern

This directory **is scholar_API's evolving state** — the arm-2 counterpart to
`scholars/sdk/core/`. Same layout and same invariant (growth is written here as
versioned artifacts, never as a growing prompt; ADR-0001). Its git diff is this
scholar's evolution record.

**Starts empty (run 0).** Unlike scholar_SDK — whose store already carries
capabilities earned over its first runs — scholar_API begins with nothing earned:
the "basic agent that grows" (ADR-0014). Its endowment is a minimal raw-API
toolset (run_analysis / register_question / save_report; no literature search),
so its capabilities and concept model accrete from scratch as Loop C runs.

The two scholars **share** the cycle-0 persona (`common/persona.md`), base prompt,
and seed question, but keep **separate** experience stores and evolve
independently — no cross-pollination (their skills are endowment-coupled).

| Folder | Evolution-stack layer | Holds |
|---|---|---|
| `goals/` | Goal | the research aim(s) the current work serves |
| `strategy/` | Hypothesis-design logic | principles of good question/hypothesis design; research taste |
| `concept_model/` | Concept model | working model of the disease — concept-map snapshots (one per run) |
| `capabilities/` | Method repertoire | skills / methods (EPAs) discovered and refined while analyzing |
| `knowledge/` | (below the stack) | validated facts, data caveats |
| `ledger/` | — | error ledger: mistake → correction → artifact change → recurrence check |
