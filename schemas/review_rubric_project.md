# Review Rubric — Cycle review (project + final development/entrustment) · Loop B

Scores **the research work this cycle**. The *iterative within-cycle* review adds tasks (`status: needs_more` + `new_tasks`, driving `loop_a --continue`); at completion (`status: complete`) the **same form** also carries the **development/entrustment** section that feeds Loop C — the *combined final review* (ADR-0013). One form per run (`feedback_project.yaml`); key comments to `q_id`s. Development dimensions are defined in [`review_rubric_development.md`](review_rubric_development.md).

**Design:** structured (not free-text), and **anchored to checkable facts** where possible so "PI approval" is separated from verifiable quality (reward-hacking guard). Scores 1–5 unless noted.

| Dimension | What it asks | Anchor |
|---|---|---|
| `literature_grounding` | citations real, relevant, current? | **check:** do cited refs resolve? (verifiable) |
| `citation_integrity` | any hallucinated/unsupported references? | binary flag + count |
| `data_analysis_validity` | correct method, EMR QC, assumptions stated? | **check:** does the analysis code run / reproduce? |
| `numerical_sanity` | results sanity-checked, not fabricated? | binary flag |
| `reasoning_quality` | inference sound, discrepancies engaged? | judgment |
| `hypothesis_quality` | testable, specific, novel (if proposed)? | judgment |
| `escalation_appropriateness` | escalated to the right ladder rung at the right time? | judgment |
| `self_correction` | caught/logged its own errors? | ledger cross-ref |

## YAML template

This is the form `pi.py` actually generates (flat `{score, note}` per dimension, 1–5):

```yaml
review:
  type: project
  run_id: ttrA-20260711-135248
  cohort: A
  cycle: 1
  reviewer: owner
  scores:
    literature_grounding: {score: null, note: ""}
    citation_integrity: {score: null, note: ""}
    data_analysis_validity: {score: null, note: ""}
    numerical_sanity: {score: null, note: ""}
    reasoning_quality: {score: null, note: ""}
    hypothesis_quality: {score: null, note: ""}
    escalation_appropriateness: {score: null, note: ""}
    self_correction: {score: null, note: ""}
  directives:                     # per-question next steps
    - q_id: ttrA-20260711-135248-q0001
      directive: ""
  status: needs_more              # needs_more -> loop_a --continue with new_tasks; complete -> Loop C
  new_tasks: []
  development:                    # filled ONLY at completion (feeds Loop C)
    scores:
      concept_model_growth: {score: null, note: ""}
      questioning_maturation: {score: null, note: ""}
      hypothesis_logic: {score: null, note: ""}
      method_repertoire: {score: null, note: ""}
      goal_autonomy: {score: null, note: ""}
      error_recurrence: {score: null, note: ""}
    entrustment:
      overall_level: null         # EPA scale: 1 observe .. 5 supervise others
      per_capability: {}
  overall_note: ""
```
