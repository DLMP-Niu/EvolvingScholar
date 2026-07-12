# Design Notes & Tracking Log

_Running log. Newest batch on top. Append dated batches; don't rewrite history._

---

## 2026-07-11 (cont. 4) — Build 5 complete: two-scholar layout + common/ + cycle→run

Branch `build/two-scholars`. Realizes ADR-0014 in full — done in two commits (structural move, then the parts I'd deferred):

- **Per-scholar layout:** `scholars/sdk/` = scholar_SDK's `engine.py` + `core/` + `runs/`; `harness/`, `data/`, `schemas/` stay shared. `experiments/` trimmed to cross-scholar `results/`.
- **`common/`:** SDK-free primitives extracted (`capture`, `emr_tools`, `scholar_io`, `projects`, `prompts`, `preflight`, `persona.md`); SDK glue consolidated into `scholars/sdk/engine.py`. This is the seam arm 2 imports through (no SDK dependency).
- **`cycle`→`run` retired in code:** `meta.yaml`/capture/ledgers now use `run` + `project` + `scholar`; readers fall back to the old `cycle` for the kept artifacts. **Project registry** (`common/projects.py`) makes cohort A **or** B runnable; **run index** auto-increments from the scholar's revision history; **no-feedback runs** are a supported skip (`cycle.py --skip`).
- **SDK store kept** (owner reviewed the results) — moved intact; `next_run_no` reads it → next run is #4.
- Verified: compile + import graph; 2 live Loop A runs; `pi` packet + skip + isolated `apply_updates`. Plan: `docs/restructure-two-scholars.md` (status: COMPLETE).

---

## 2026-07-11 (cont. 3) — Domain model corrected: two evolving scholars, per-run evolution

Owner correction (mimicking real research): a **research project** (gene/disease) is a *container for many experiment runs*, not a "cycle." Evolution **accretes per experiment run, gated by PI feedback** — a run *with* a completed review → Loop C; a run *without* feedback is captured but **skipped**. And the two build arms are **two distinct evolving scholars** — `scholar_SDK` and `scholar_API` — each with its **own experience store** (their skills are endowment-coupled → no cross-pollination). A lab of many diverse AI interns is out of scope; the human panel is the reference.

- Term **"cycle" retired** → **research project** (container) + **experiment run** (one scholar's Loop A pass). `CONTEXT.md` updated.
- → [ADR-0014](adr/0014-two-evolving-scholars.md) (refines ADR-0010's shared-core into *shared mechanism + per-scholar store*).
- **Restructure plan** → `docs/restructure-two-scholars.md` ("Build 5"): shared `data/`+`schemas/`+`harness/`+`common/` vs per-scholar `scholars/<id>/{engine,core,runs}`. Do before building arm 2.

Also this session: **live-tested the SDK cycle runner end-to-end** (new → needs_more → complete) with real PI feedback; validated Build 4 (preflight + layer-2 fix); fixed `loop_c` `max_turns=1→6`.

---

## 2026-07-11 (cont. 2) — Cycle runner + two capture/isolation fixes

**Build 4 — the orchestration entrypoint (`runtime/cycle.py`).** Closes the "entrypoint to be created" gap in `runtime/README.md`. A human-in-the-loop state machine that advances one A→B→C cycle by exactly one step, deriving state from the run dir's `feedback_project.yaml` (unfilled → rebuild packet; `needs_more` → Loop A `--continue`; `complete` → Loop C). Reuses `run_project` / `build_review_packet` / `pending_tasks` / `load_final_feedback` / `run_loop_c` — sequencing only, no new loop logic. Codifies the operator flow from the previous batch into one command. The three sub-loop CLIs still work standalone.

**Fix — layer-2 (thinking) capture was silently dead.** `capture.py` was ready to record `ThinkingBlock`s, but `loop_a.py` never passed a thinking config into `ClaudeAgentOptions`, so `thinking.jsonl` was always empty (and `reconcile.py`'s `abandoned` detector had nothing to read). Added `_thinking_config()` in `loop_a.py`, wired defensively (probes the SDK symbol; degrades to no-capture rather than breaking a run if the API name differs — **confirm against SDK 0.2.115 and pin**).

**Fix — config-isolation guard now implemented (ADR-0007).** New `runtime/preflight.py`: `assert_isolated_and_ready()` fails loudly on an ancestor `CLAUDE.md`, a missing SDK, or unpacked-cohort-absent; `log_effective_config()` writes `run_dir/effective_config.yaml` at every launch. Called from `run_project`, so both the runner and `loop_a --continue` are covered. Guard logic unit-tested; the SDK/data-dependent paths need the real env to exercise end-to-end.

---

## 2026-07-11 (cont.) — Builds 1–3 running; iterative within-cycle review designed

**Build progress (SDK arm).** Loop A (`runtime/loop_a.py` + `capture.py` + `tools.py`), PI review (`harness/pi.py`), and Loop C (`harness/loop_c.py`) all built and validated live end-to-end on cohort A. One demo cycle produced 2 reusable skills, 3 strategy principles, an error ledger, and a revision-map entry in `scholar_core/`. **Web search enabled** in Loop A. Known open link: `loop_a` writes-but-doesn't-read `scholar_core/` — the retrieval side (ADR-0001) isn't wired, so evolution doesn't yet take effect across runs.

**Iterative within-cycle review** → [ADR-0013]. Real workflow = Loop A → PI **adds tasks** (within-cycle) → **partial re-run only if needed** (SDK session resume preserves prior context) → iterate → Loop C at convergence. New domain terms: **Task** (PI-assigned) vs **Question** (Scholar-raised).

**Concrete design for the code change (not built yet):**
- `runtime/loop_a.py`: refactor `main()` → `run_project(prompt, resume_session_id=None, run_dir=None)`; capture `ResultMessage.session_id` into `meta.yaml`; add a `--continue <run_dir>` CLI that resumes the session with the PI's new tasks and **appends** to the same run. `RunContext` restores its question counter from the existing `questions.jsonl` so numbering continues.
- `harness/pi.py`: the feedback form gains `status: complete|needs_more` + `new_tasks: [...]`; add `pending_tasks(run_dir)` returning the tasks when `needs_more`.
- Operator flow (human-paced): `loop_a.py` → `pi.py <run>` (fill scores + status + tasks) → if `needs_more`: `loop_a.py --continue <run>` → repeat → `loop_c.py <run>` when `complete`.
- Related open link to close alongside: wire `scholar_core/` **loading** into `run_project` (load current skills+strategy; relevance-retrieval once the library grows) so re-runs/next cycles actually reflect evolution.

---

## 2026-07-11 — Data, tools, and the two-arm resolution

**Pilot data arrived.** `data/synthetic_ttr_REACTSP_tsv_datasets.zip` — two TTR/ATTR cohorts. Provenance corrected by owner: genuinely **synthetic** (randomly shuffled, 3 rounds of random processing), not perturbed real records → privacy concern resolved; it's **workflow/plumbing-grade**, so intern *findings* here are not clinically valid. Key empirical facts (see `data/README.md`): within-patient timelines are **coherent** (A001 is a clean ATTR picture), so temporal analyses are structurally runnable; **A** = deep EMR (dense dx + glucose), **B** = registry-derived + sparse (75 diabetes rows); glucose has QC garbage (0–47,330 mg/dL) and duplicated dx rows — a built-in test of intern rigor; A and B are **not poolable**.

**Two-cohort strategy → Option C** (emergent, then mentored) — [ADR-0009](adr/0009-two-cohort-strategy-emergent-then-mentored.md). Real EMR discipline: characterize each cohort's data elements one-by-one, crosswalk the differences, then compare. New artifact: per-cohort data-element profile + crosswalk. Reproduces the real intern's "understand data elements first" PI-feedback moment.

**Two build arms = demonstrations, not a controlled contrast** — [ADR-0010](adr/0010-two-arms-are-demonstrations.md). Runtimes differ in built-in tools: Claude Code/SDK = super-intern from day one; raw API = basic agent that grows. The science (evolving capabilities + questions) is measured *within* each arm; different endowments are intended. Endowment = per-arm allow-list knob. Sequencing: shared core → validate on SDK first (restrained endowment) → then raw-API arm.

**Loop A tool design → minimal portable primitives, method withheld** — [ADR-0011](adr/0011-loop-a-tool-design.md). `run_analysis` (portable sandboxed code, not built-in Bash), `search_literature`, `register_question`, minimal save. Withhold method-encoding tools (`characterize_cohort`, `compare_cohorts`, …) — their absence is what makes method emergence observable. Method accrues as self-authored skills in `capabilities/` (Voyager pattern).

**Capture layer built** ([ADR-0008](adr/0008-capture-all-four-layers.md)): `runtime/capture.py` + `harness/reconcile.py`, verified against SDK 0.2.115.

**Scope / non-goal (owner).** The intern→PI ladder is a **scaffold for organizing and measuring** the Scholar's evolution — **not** a prediction that this approach makes an AI a human-like expert. Explicitly out of scope: (a) **recursive mentorship** (a Scholar mentoring another Scholar — EPA-5 "supervise others" is a coordinate, not a literal target here); (b) any claim of **human-equivalent expertise** via following a human learning path. Consistent with ADR-0002 (complementary windows, not a scoreboard) and ADR-0005 (AI starts from the opposite competence profile).

**Next:** build the shared core + a minimal Loop A on the SDK (restrained endowment) to validate machinery + see first evolution.

---

## 2026-07-10 — Design consolidated from planning discussion

Reframing that moved the project off the original brief, plus the decisions now recorded as ADRs.

**Aim (sharpened).** The headline is *not* learning-vs-static performance. It is **how research questioning and disease conceptualization evolve**, studied across a human reference panel and an AI intern. The AI is a controllable *model system* for a developmental process that is knowledge-entangled in humans. → [ADR-0002](adr/0002-headline-is-questioning-evolution.md)

**Knowing vs. reasoning.** We do **not** handicap the intern's starting knowledge. Because knowledge starts saturated and stays ~constant, any capability gain is attributable to reasoning/experience — which isolates, in the AI, a variable that is confounded in human training. → [ADR-0005](adr/0005-do-not-handicap-knowledge.md)

**What evolves — the stack.** Goal → hypothesis-design logic → question-asking → concept model → method repertoire. These mature in a rough order that traces student → resident → PhD → PI. Two axes annotate every question: **cognitive** (Remember→Create) × **medical purpose / lens** (research-mechanistic · clinical-management · counseling-pathway). Keep the taxonomy semi-open so new categories can emerge, but pin ≥1 observable per layer.

**Concept evolution.** The intern's disease concept-model is snapshotted each cycle; diffs (nodes/links added, beliefs corrected, new concepts formed) are the richest readout of reasoning-driven growth. This is the one legitimate use of a "world-model"-style store here — as *instrumentation*, not a performance mechanism.

**Growth ≠ prompt accumulation.** Hard invariant. Cross-cycle growth is only via versioned `scholar_core/` artifacts. → [ADR-0001](adr/0001-growth-is-not-prompt-accumulation.md)

**Two review types (different objects).** Within-cycle review = project-focused (Loop B). Between-cycle review = development-focused / entrustment (feeds Loop C). Build them as two distinct rubrics.

**Human panel.** One subject per stage: college intern (collected); master's, medical student, resident (this month). Cross-sectional stage-*waypoints*, not a longitudinal curve — interpret as reference points, not growth rates. Subjects work the **same** gene/disease pairs as the AI, enabling direct output comparison. Capture their questions/analyses/mistakes in a form comparable to the AI's registry *before* collection.

**Mentor.** The project owner is sole PI-mentor for now (calibrates human + AI to one standard; on-vision for the "digital self" aim). Team of clinicians + CGCs + med students joins after the feasibility test → multi-rater reliability + committee mentorship.

**Pilot pair.** TTR / hereditary ATTR amyloidosis. Real stakeholder questions to use as target waypoints: diabetes as a comorbid confounder (clinician lens, EMR-validated); symptom-to-diagnosis time for testing recommendations (CGC lens).

**Scoring.** Human-judged questions and results (auto Bloom-classification is unreliable, ~46.6% expert agreement). Write a rough rubric now for team consistency later.

**Architecture.** Single intern as the locus of learning; any subagents are execution-only, sharing one canonical artifact store (Kosmos pattern). Start minimal: one intern + separate mentor + separate evaluator. → [ADR-0003](adr/0003-single-intern-locus-of-learning.md)

**Records.** Three separated streams (build / experiment / intern artifacts); git as the revision engine. → [ADR-0004](adr/0004-three-record-streams.md)

**Open (deferred).** Second build arm (SDK vs. raw API) is not scaffolded yet → [ADR-0006](adr/0006-runtime-second-arm-deferred.md). Concept-model elicit-vs-extract still open. Synthetic-EMR circularity control (pre-registered embedded ground truth + power/false-positive reporting) still to design.

**Background evaluation.** A deep-research review of SOTA (Voyager, ExpeL, Reflexion; AI Co-Scientist, Sakana, Kosmos; LLM-as-judge biases) is in the planning folder (`EvolvingScholar_BackgroundEvaluation.md`) — port its action list here when convenient.
