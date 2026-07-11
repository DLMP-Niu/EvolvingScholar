# Review Rubric — WITHIN-cycle (project-focused) · Loop B

Used at a mid/end-of-project checkpoint to score **the research work on this pair this cycle** — not the intern's development (that's the other rubric). Fill one per review session; key comments to `q_id`s.

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

```yaml
review:
  type: project            # within-cycle
  pair: TTR/ATTR
  cycle: 1
  reviewer: owner
  scores:
    literature_grounding: {score: null, note: ""}
    citation_integrity: {hallucinated: null, count: 0, note: ""}
    data_analysis_validity: {score: null, reproduced: null, note: ""}
    numerical_sanity: {flag: null, note: ""}
    reasoning_quality: {score: null, note: ""}
    hypothesis_quality: {score: null, note: ""}
    escalation_appropriateness: {score: null, note: ""}
    self_correction: {score: null, note: ""}
  directives:              # next steps, keyed to questions/findings
    - q_id: ttr-c1-007
      directive: ""
  overall_note: ""
```
