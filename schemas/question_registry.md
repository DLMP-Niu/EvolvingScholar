# Question Registry — schema

One record per question, whether asked by a human subject or the AI intern. This is the backbone of the **question-trajectory** tracking structure and the source for the ladder-distribution, autonomy, branching, and quality readouts.

## Fields

| Field | Type / allowed values | Purpose |
|---|---|---|
| `q_id` | string, unique (e.g. `ttr-c1-007`) | identity |
| `text` | string | the question as posed |
| `asker` | `college-intern` \| `masters` \| `medical` \| `resident` \| `ai` | which instance (keeps human + AI in one dataset) |
| `pair` | string (e.g. `TTR/ATTR`) | gene–disease pair |
| `cycle` | int | which project cycle (AI); session index (human) |
| **`cognitive_level`** | `1`–`9` ladder rung *(see below)* | **axis 1** — cognitive complexity |
| **`medical_purpose`** | `research-mechanistic` \| `clinical-management` \| `counseling-pathway` \| *(extend)* | **axis 2** — professional lens/purpose |
| `origin` | `seeded` \| `self-generated` \| `pi-suggested` \| `spawned` | autonomy signal |
| `parent_q_id` | string \| null | provenance edge source |
| `edge_type` | `refines` \| `spawns` \| `blocks` \| null | provenance edge type |
| `evidence_source` | `literature` \| `emr` \| `both` \| null | where its answer comes from |
| `status` | `open` \| `answered` \| `dropped` | lifecycle |
| `result_summary` | string \| null | short answer/finding |
| `quality` | sub-block *(see below)* | human-judged, once answered |
| `annotation_notes` | string | free notes / reconciliation with legacy tags |

### `cognitive_level` — the 9-rung ladder (axis 1)

`1` factual · `2` knowledge-validation · `3` data-validation · `4` comparative · `5` stratification · `6` discrepancy-driven · `7` explanatory · `8` discovery-hypothesis · `9` generalizable-study-design. (Roughly Remember→Verify→Analyze→Synthesize→Create.)

### `quality` sub-block (human-judged, 1–5 each)

`testability` · `novelty` · `specificity` · `groundedness` (are claims/citations resolvable). Plus `judged_by` (`owner` for now; a rater id later) and `judge_notes`.

## YAML template

```yaml
- q_id: ttr-c1-007
  text: "Does the EMR cohort show elevated ATTR risk in patients with comorbid diabetes?"
  asker: ai
  pair: TTR/ATTR
  cycle: 1
  cognitive_level: 5        # stratification
  medical_purpose: research-mechanistic
  origin: self-generated
  parent_q_id: ttr-c1-003
  edge_type: spawns
  evidence_source: emr
  status: open
  result_summary: null
  quality:
    testability: null
    novelty: null
    specificity: null
    groundedness: null
    judged_by: null
    judge_notes: null
  annotation_notes: "legacy tag: 'update'"
```

## How fields map to the evolution readouts

- **Ladder distribution × cycle** ← `cognitive_level` × `cycle`.
- **Lens breadth / fusion** ← `medical_purpose` spread; a question tagged with a higher lens than its `asker`'s baseline is a maturation marker.
- **Autonomy** ← `origin` shifting `seeded` → `self-generated`.
- **Branching structure** ← `parent_q_id` / `edge_type` (the trajectory graph).
- **Quality trend** ← the `quality` sub-block over cycles.
