# emr-icd-hygiene-audit

# EMR ICD Coding Hygiene Audit

Run this BEFORE any frequency analysis on an EMR diagnosis table. Silent coding artifacts corrupt counts.

## Steps
1. **Count by distinct patient, not rows.** Row counts double-count repeat encounters; report N-patients for every diagnosis frequency.
2. **Detect compound codes.** Single fields may pack multiple codes (e.g. `"E85.4, I43"`). Exact-match grouping misses these — use substring/regex matching per target code. Quantify: how many rows/patients affected.
3. **Exclude junk/placeholder codes.** Scan for erroneous-encounter markers (e.g. `"10000 — ERRONEOUS ENCOUNTER--DISREGARD"`) and drop before counting.
4. **Normalize casing and name variants.** The same code can appear under many name strings (ALL-CAPS, `(HCC)` suffixes, unspecified variants). Group by CODE, never by name string; naive name-based counts inflate cardinality.
5. **Check for missing structured fields** the analysis assumes (e.g. no genotype/variant field) and record the proxy you must use instead.

## Output
A short data-quality note enumerating each artifact found with row/patient counts, plus the cleaning rule applied. Carry this into the report's 'data-quality problems found' section.


## cycle 1 · ttrA-20260711-135248 · 2026-07-11
## ICD-9 / ICD-10 dual-coding is decision-relevant, not just cosmetic

Legacy ICD-9 numeric codes coexist with ICD-10 in the same EMR (cohort A: 70 patients). An ICD-10-only phenotype regex undercounts: adding ICD-9 neuro equivalents (356/357/354.0) raised the neuro count 99->106 (+7), cardiac unchanged. This undercount can change the outcome of a downstream statistical test (in cohort A it moved the diabetes-neuropathy test from non-significant to borderline). **Always build both ICD-9 and ICD-10 marker sets and treat the ICD-9-inclusive version as a mandatory sensitivity arm for any association test.**
