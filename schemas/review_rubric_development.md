# Review Rubric — BETWEEN-cycle (development / entrustment) · feeds Loop C

Used at the end of a project cycle to score **the intern's development**, not the project. Its output is what Loop C acts on (which artifacts to update) and the **entrustment level** that governs how much autonomy the intern gets next cycle — the operational student→resident→PhD→PI signal.

**Design:** dimensions map to the evolution stack; entrustment uses the standard EPA scale. Scores 1–5 unless noted.

| Dimension | Evolution-stack layer | What it asks |
|---|---|---|
| `concept_model_growth` | Concept model | did its disease model gain/restructure/correct concepts this cycle? |
| `questioning_maturation` | Question-asking | did the ladder distribution rise / lens breadth widen / autonomy increase? |
| `hypothesis_logic` | Hypothesis-design logic | can it *articulate* and *critique* good-question principles, not just produce? |
| `method_repertoire` | Method repertoire | did it add a reusable, documented method? |
| `goal_autonomy` | Goal | is it starting to set its own research direction? |
| `error_recurrence` | (learning signal) | did prior error classes recur? (lower is better) |

## Entrustment level (the promotion signal)

Per the EPA entrustment scale — the student→PI analog:

1. observe only · 2. act under **direct** supervision · 3. act under **indirect/on-demand** supervision · 4. act **independently** · 5. **supervise others**.

Record an overall level and, optionally, per-capability levels. Advancement here is what "moving up a stage" means operationally.

## YAML template

```yaml
review:
  type: development         # between-cycle
  pair: TTR/ATTR
  cycle: 1
  reviewer: owner
  scores:
    concept_model_growth: {score: null, note: ""}
    questioning_maturation: {score: null, note: ""}
    hypothesis_logic: {score: null, note: ""}
    method_repertoire: {score: null, note: ""}
    goal_autonomy: {score: null, note: ""}
    error_recurrence: {recurred: null, note: ""}
  entrustment:
    overall_level: null     # 1-5
    per_capability: {}      # e.g. {emr-stratification: 3, lit-review: 4}
  loop_c_directives:        # what to update, becomes revision-map entries
    - target: strategy      # goals|strategy|concept_model|capabilities|knowledge|ledger
      change: ""
  overall_note: ""
```
