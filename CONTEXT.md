# CONTEXT — Ubiquitous Language

The canonical glossary for EvolvingScholar. **Terms only** — no implementation details or decisions (those live in `docs/adr/`). Keep this in sync as the language sharpens.

## Scholar
The AI research intern under study — one per build arm. The subject whose capabilities and questioning we watch evolve.

## Research project
One gene–disease investigation (e.g. TTR/ATTR, PMP22/CMT). The scope of a single **cycle**. *(Supersedes the earlier informal term "pair.")*

## Cycle
One full research-project pass by the Scholar: **research → discuss → feedback → update**, completed before the next cycle begins. **One cycle = one research project.** Evolution and transfer are measured *across* cycles; the system update (Loop C) fires *between* cycles. *(Resolves ADR-0001…0011's loose use of "cycle"; supersedes "cohort/pair" ambiguity in ADR-0009.)*

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
