# Build 5 — Restructure to two evolving scholars

Plan for the directory/code restructure that realizes [ADR-0014](adr/0014-two-evolving-scholars.md): **shared foundation + mechanism, per-scholar engine + experience.** Do this *before* building `scholar_API`, while only `scholar_SDK` (arm 1) exists to move. The pilot keeps working throughout (it's a move + reimport + retest).

## Status (branch `build/two-scholars`) — COMPLETE

**1. Structural separation** ✅ `runtime/` → `scholars/sdk/`, `scholar_core/` → `scholars/sdk/core/`, old runs → `scholars/sdk/runs/`, `.gitignore`, `experiments/` trimmed to shared `results/`.

**2. `common/` pure-extraction** ✅ SDK-free cores split out (`capture`, `emr_tools`, `scholar_io`, `projects`, `prompts`, `preflight`, `persona.md`); SDK glue consolidated into `scholars/sdk/engine.py` (was `loop_a`+`capture`+`tools`). `common/` imports no SDK, so arm 2 reuses it directly.

**3. Terminology + behavior** ✅ `cycle`→`run`+`project`+`scholar` in `meta.yaml`/capture/ledgers (readers tolerate the retired `cycle` on kept artifacts); **project registry** (`common/projects.py`) makes cohort A **or** B runnable; **run index** auto-increments from the scholar's revision history (`next_run_no`); **no-feedback-skip** is a supported outcome (`cycle.py --skip`).

**4. SDK store** ✅ **kept** (owner reviewed the results) — moved intact, not cleared; `next_run_no` reads it (→ run 4).

Verified: compile + full import graph; two live `scholar_SDK` Loop A runs (`is_error=False`, all four capture layers + `meta` scholar/project/run → `scholars/sdk/runs/`); `pi` packet + `--skip` + isolated `apply_updates` (ledgers write `run`, paths relative). Ready to build `scholars/api/` with no further restructuring.

## Target layout
```
EvolvingScholar/
  data/                     SHARED dataset
  schemas/                  SHARED contracts
  harness/                  SHARED mechanism: pi.py · loop_c.py · reconcile.py · evaluator.py
  common/                   SHARED runtime-neutral primitives + INITIAL setup:
      capture.py            RunContext, JsonlWriter, register_question schema  (pure — from runtime/capture.py)
      emr_tools.py          run_cohort_analysis, cohort tables                 (pure — from runtime/tools.py)
      preflight.py          isolation/completeness guard                       (from runtime/preflight.py)
      scholar_io.py         load_scholar_core(core_dir), prompt assembly       (from runtime/loop_a.py)
      persona.md            cycle-0 identity (both scholars start here)         (from scholar_core/persona.md)
      prompts.py            base SYSTEM_PROMPT + SEED_QUESTION(s)               (from runtime/loop_a.py)
  scholars/
      sdk/
          engine.py         SDK adapter: build_capture, build_loop_a_tools, run_project, cycle
          core/             scholar_SDK experience store  (from scholar_core/*)
          runs/             scholar_SDK runs             (from experiments/runs/*)
      api/                  (created in the arm-2 build — empty for now)
  docs/  CONTEXT.md  CLAUDE.md
```

## Migration mapping (what moves)
- **Split the pure cores out of the SDK glue:**
  - `runtime/tools.py`: `run_cohort_analysis` + constants → `common/emr_tools.py`; `build_loop_a_tools` (`@tool`/`create_sdk_mcp_server`) → `scholars/sdk/engine.py`.
  - `runtime/capture.py`: `RunContext`/`JsonlWriter`/`REGISTER_QUESTION_SCHEMA`/`_clean` → `common/capture.py`; `build_capture`/`capture_stream`/`_serialize` (SDK types) → `scholars/sdk/engine.py`.
  - `runtime/loop_a.py`: `load_scholar_core`/`SEED_QUESTION`/`SYSTEM_PROMPT` → `common/`; `run_project`/`_continue`/`_thinking_config`/options → `scholars/sdk/engine.py`.
  - `runtime/cycle.py` → `scholars/sdk/engine.py` (or `scholars/sdk/cycle.py`).
  - `runtime/preflight.py` → `common/preflight.py`.
- **Move the data, not just the schema:** `scholar_core/*` → `scholars/sdk/core/`; `experiments/runs/*` → `scholars/sdk/runs/` (see the "clear vs keep" decision first — a clear start is simplest).
- **Parameterize the harness by scholar:** `loop_c.run_loop_c(run_dir, core=...)` already takes `core` — pass `scholars/sdk/core/`. `pi.build_review_packet` works off `run_dir` (no change). Give the engine the two paths (`core_dir`, `runs_dir`).

## Terminology + behavior changes (ADR-0014)
- Rename the `cycle: int` param → a **project** identifier + a **run** id. `meta.yaml` gains `scholar` and `project` (e.g. `scholar: sdk`, `project: TTR-ATTR`); the bare `cycle` field is retired.
- **No-feedback runs are a supported outcome:** the cycle runner's `unfilled` state should accept an explicit "skip — no PI feedback for this run" (captured, no Loop C) rather than looping forever or erroring.
- **Per-project seed/cohort:** a small project registry (`project → gene/disease, seed, cohort(s)`) so a run can target TTR *or* PMP22 (closes the "cohort-B/PMP22 not runnable" gap).

## `.gitignore`
- Ignore each `scholars/*/runs/` (regenerable capture data, like the old `experiments/runs/`).
- Track each `scholars/*/core/` (the per-scholar evolution record — its git diff is that scholar's evolution).

## Verification
- After the move: `python -m py_compile` all moved modules; re-run **one cheap `scholar_SDK` cycle** through the relocated cycle runner (new → review → complete → Loop C) to confirm imports, paths, capture, and Loop C all still work against `scholars/sdk/`.
- Confirm `scholars/sdk/core/` receives the Loop C writes and `scholars/sdk/runs/` the run outputs.

## Sequencing
1. Decide the current SDK store: **clear** (clean start — recommended) or keep. (Blocks nothing else.)
2. **Build 5 restructure** (this doc).
3. Build `scholars/api/` (arm 2) into the new slot — no further restructuring needed.
