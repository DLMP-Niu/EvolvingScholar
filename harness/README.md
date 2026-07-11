# harness/ — shared experiment machinery

Everything here operates **on** the intern but is **not** the intern (a separate locus — ADR-0003). Shared across any runtime.

- `pi.py` — **Loop B.** The PI-mentor: structured rubric + feedback. Two review modes (different objects): within-cycle *project* review, and between-cycle *development/entrustment* review.
- `loop_c.py` — **Loop C.** Reads the cycle's trajectory + feedback + errors, and writes typed, versioned artifacts to `scholar_core/`. The learning-vs-static switch lives here (write enabled/disabled).
- `evaluator.py` — builds the tracking structures: question trajectory, revision map, capability-transfer matrix, concept-model diffs.

The judge/evaluator should ideally use a different model family than the intern (self-enhancement bias — ADR-0003). Scoring of questions and results is human-anchored.

_Stubs to be created once module design is frozen._
