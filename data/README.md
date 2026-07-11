# data/ — pilot inputs

**Synthetic only. No real PHI.** Everything under `data/` except this README is gitignored (bulk cohort files stay out of git).

## What's here

`synthetic_ttr_REACTSP_tsv_datasets.zip` — two TTR / hereditary ATTR amyloidosis cohorts.

**Provenance (per the owner):** genuinely **synthetic** — randomly shuffled datasets produced with **3 rounds of random processing** from randomized TTR EMR-style files + the REACT-SP registry (synthetic profiles → 2nd-round synthetic IDs → date-shifted). Not perturbed real records, and not formally privacy-certified. → **workflow / KG / analytics prototyping only; intern *findings* on this data are not clinically valid.** Real biological findings need the governed real-data track later (the Kosmos-style replication arm, see background eval).

## Cohorts

| | Dataset A | Dataset B |
|---|---|---|
| Source style | deep EMR | registry (REACT-SP) |
| IDs | 230 (A001–A230) | 670 (B001–B670) |
| Density | dense (~140k dx rows) | sparse (~7.5k dx rows) |
| Diabetes signal | 2.9k dx rows + dense glucose | **75 dx rows** (underpowered) |
| Best for | the diabetes-confounder question | ATTR-focused registry questions |

**A and B are NOT poolable** — different provenance/ascertainment/density. Comparing them is itself an ascertainment study (Option C, [ADR-0009](../docs/adr/0009-two-cohort-strategy-emergent-then-mentored.md)).

## Schema (both cohorts, 3 tables + DOB)

- `*_diagnosis.tsv` — `ID, dx ICD code, dx ICD name, Dx date`
- `*_appointments.tsv` — `ID, appointment description, appointment date`
- `*_glucose_labs.tsv` — `ID, lab glucose testing result, value, unit, date`
- `*_id_date_of_birth.tsv` — `ID, date_of_birth`

No genotype/variant table — the cohort *is* the TTR population; mutation info is implicit.

## Known data-quality issues (deliberately left in — they test intern rigor)

- **Glucose values range 0–47,330 mg/dL** (physiologically impossible) → the intern must clean before analyzing (`numerical_sanity` rubric dimension).
- **Duplicated diagnosis rows** across consecutive dates (repeated encounter coding) → needs dedup before counting.
- **Date-shift** (random 1–30 days) but **within-patient structure is coherent** (A001 is a clean ATTR picture: E85.2 + bilateral carpal tunnel + gammopathy) → temporal/longitudinal analyses (time-to-diagnosis, event sequence) are structurally runnable, even though population effects are not "true."

## Access

The intern reads this data only via the portable `run_analysis` tool (local compute, aggregates out) — never raw rows into the prompt ([ADR-0011](../docs/adr/0011-loop-a-tool-design.md)).
