# CONTEXT — Ubiquitous Language

The canonical glossary for EvolvingScholar. **Terms only** — no implementation details or decisions (those live in `docs/adr/`). Keep this in sync as the language sharpens.

## Scholar
An evolving **AI Scholar Agent** (an AI research agent) — the subject whose capabilities and questioning we watch evolve. Learns by mimicking a human learner; "intern / trainee" is the *analogy*, not the label. **This project builds TWO scholars, each evolving independently:**
- **scholar_SDK** — built on the Claude Agent SDK (rich built-in tools; a "super-intern").
- **scholar_API** — built on the raw Anthropic Messages API (minimal tools; a "basic agent that grows").

**Audience-facing names:** *Scholar 1 (SDK)* = scholar_SDK, *Scholar 2 (API)* = scholar_API — used in slides/talks. `scholar_SDK` / `scholar_API` remain the code identifiers (dirs `scholars/sdk`, `scholars/api`; run IDs).

They **share** an initial setup (cycle-0 persona, base prompt, seed questions) and the **dataset**, but each keeps its **own experience store** and evolves **independently — no cross-pollination** (their accumulated skills are endowment-coupled, so mixing would be incoherent and would blur each one's growth curve). See [ADR-0014](docs/adr/0014-two-evolving-scholars.md).

## Research project
One gene–disease investigation (e.g. TTR/ATTR, PMP22/CMT). A **container for multiple experiment runs** — a scholar may run it many times (and re-run). Scholars need not run the same projects the same way. *(Supersedes the earlier informal term "pair.")*

## Experiment run
One Loop A research pass by **one scholar** on a research project (with optional within-run PI iteration via `--continue`, and re-runs). Evolution **accretes per run, per scholar, gated by PI feedback**: a run *with* a completed PI review → Loop C → updates that scholar's experience store; a run *without* feedback is **captured but skipped** for evolution.

*(Deprecates **"cycle"**, which conflated "research project" with "one Loop A→B→C pass." The pass unit is an experiment run; the project is the container. Supersedes the "cycle = research project" framing and ADR-0009's cohort/pair wording — see [ADR-0014](docs/adr/0014-two-evolving-scholars.md).)*

## Guided self-evolution loop
The overall workflow by which a Scholar improves across experiment runs — a three-nested-loop structure: **Loop A** (research activity), **Loop B** (Scholar↔PI feedback), **Loop C** (system update, which writes the Scholar's typed, versioned artifacts). Growth lives only in those artifacts, never in a swelling prompt ([ADR-0001](docs/adr/0001-growth-is-not-prompt-accumulation.md)). This is the *mechanism* — distinct from the **Scholar** (the agent it improves) and the **harness** (the shared code that implements Loops B/C). *Avoid* using bare "the loop," "the harness," or "the scholar" to mean the workflow as a whole.

## Cohort
A specific patient group within a research project. May be **provided** (e.g. datasets A and B) or **identified by the Scholar** as part of the research (e.g. a stratified subgroup). A single research project may involve multiple cohorts. Two provided cohorts can come from different **data sources** (A = EMR, B = registry) — a difference that is itself an ascertainment consideration, not a difference in the term.

## PI (mentor)
The **role** that gives the Scholar feedback (the discuss/feedback step of a cycle) and judges its development. Currently a **human** (the project owner); a **clinician review team** joins later for multi-rater feedback; an LLM-PI is deferred. Distinct from **PI-level** — the mentor is *who evaluates*, PI-level is *what the Scholar climbs toward*.

## Entrustment level
How far the Scholar is trusted to act unsupervised, on the clinical EPA scale: **1** observe → **2** direct supervision → **3** indirect/on-demand → **4** independent → **5** supervise others. The spine of the **intern → PI** progression.

## PI-level
The **direction** the Scholar grows toward on the entrustment ladder: increasing autonomy in its *own* research (sets its own questions/goals, needs less correction). A **measurement coordinate, not a predicted destination** (see scope non-goals in `docs/design-notes.md`). Distinct from the **PI (mentor)** role — the Scholar climbs toward being *able* to do that role; it is not expected to reach human-expert equivalence.

## EPA (Entrustable Professional Activity)
A unit of professional work the Scholar can be entrusted to perform (e.g. "conduct a targeted literature review," "run and interpret a stratified EMR analysis"). The Scholar's **capabilities** are expressed as EPAs, and evolution is read out as the EPAs **extractable after each cycle** (format may vary — a sentence in a `skill.md`, a structured entry). A human trainee accumulates **knowledge, EPAs, and question-raising ability**; EPAs and question-raising are the AI-comparable dimensions — **knowledge is asymmetric** (the Scholar starts knowledge-rich, ADR-0005).

## Question
An inquiry the **Scholar raises** and pursues, logged in the question registry with its cognitive level (1–9) and medical purpose. Scholar-originated — contrast **Task**.

## Task
A unit of work the **PI assigns** to the Scholar within a cycle (e.g. "also stratify by comorbid diabetes"). PI-originated — contrast **Question**. The iterative within-cycle review may add tasks, prompting a partial re-run (ADR-0013).
