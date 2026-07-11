# harness/ — shared experiment machinery

Everything here operates **on** the intern but is **not** the intern (a separate locus — ADR-0003). Shared across any runtime.

- `pi.py` — **Loop B.** The PI-mentor (human-in-the-loop). Builds a review packet + a structured feedback form, and validates it. One form spans the whole cycle: the **iterative within-cycle project review** (scores the work; can add tasks), and — at completion — a **combined final review** that also captures the **development/entrustment** dimensions that feed Loop C.
- `loop_c.py` — **Loop C.** Consumes the *completed* final review + the run, and writes typed, versioned artifacts to `scholar_core/`. Gated: refuses to run until `status: complete` with an entrustment level (ADR-0013). The learning-vs-static switch lives here.
- `reconcile.py` — merges the four capture layers into the question trajectory (used by `pi.py`).
- `evaluator.py` — *future stub*: the tracking structures (transfer matrix, concept-model diffs, plots).

The judge/evaluator should ideally use a different model family than the intern (self-enhancement bias — ADR-0003). Scoring is human-anchored.

## PI review workflow (human-in-the-loop, one YAML form per run)

1. **Review:** `python harness/pi.py <run_dir>` → read `review_packet.md`, then edit `feedback_project.yaml`: fill `review.scores.<dim>.score`/`.note` and the per-question `directives`.
2. **Add tasks (within-cycle):** in the same form set `review.status: needs_more` and `review.new_tasks: ["…"]`, then `python runtime/loop_a.py --continue <run_dir>` (resumes the session; partial re-run). Re-run `pi.py` to refresh the packet and review again. Repeat as needed.
3. **Final review → Loop C:** set `review.status: complete`, fill the `review.development` section (6 growth dims + `entrustment.overall_level` 1–5), then `python harness/loop_c.py <run_dir>`.

**Does the final review precede Loop C?** Yes — Loop C is *gated* on the completed final review and reads it (ADR-0013).
