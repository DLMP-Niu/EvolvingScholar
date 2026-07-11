# Design Notes & Tracking Log

_Running log. Newest batch on top. Append dated batches; don't rewrite history._

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
