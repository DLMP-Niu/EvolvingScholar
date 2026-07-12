# emr-patient-phenotype-classification

# Patient-Level Phenotype Classification from ICD Codes

Classify each patient into phenotype buckets (e.g. cardiac / neuropathic / mixed / neither) from cleaned ICD data.

## Method
1. Restrict to the disease cohort (e.g. E85.x amyloidosis patients).
2. Define phenotype code lists **from a guideline/reference source, not ad hoc** — write down the source for each code list.
3. **Keep DEFINING codes separate from EVIDENCE codes.** A code used to define a subtype must NOT also serve as an outcome marker for that subtype — this creates circular 100%-by-construction figures. Report cross-over rates between independent code sets instead (e.g. % of wild-type-coded patients also carrying neuro markers).
4. Assign each patient to buckets via substring matching (handles compound codes).
5. Cross-tabulate phenotype against subtype and age; flag which figures are definitional vs informative.

## Caveat to always state
ICD-derived phenotype is a proxy; note confounders (e.g. diabetes → polyneuropathy) that a code list cannot disentangle without a genotype/biopsy field.
