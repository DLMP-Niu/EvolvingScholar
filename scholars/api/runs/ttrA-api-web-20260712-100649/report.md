
# TTR / Hereditary ATTR Amyloidosis — Cohort A Characterization

*Synthetic-data workflow exercise. Findings are NOT clinically valid.*

## 1. What am I studying?
I characterized cohort A's amyloidosis population — patient count, most frequent diagnoses, and whether the expected **cardiac vs. neuropathic (vs. mixed)** phenotype of hereditary transthyretin (ATTRv) amyloidosis is reflected in the EMR diagnosis codes.

**Questions pursued**
- **q0001 (seed):** Cohort size, top diagnoses, cardiac vs. neuropathic phenotype among E85.x patients.
- **q0002 (spawned):** Balance of cardiac vs. neuropathic phenotype and mixed-phenotype overlap at the patient level.

## 2. Where do I find information?
- **EMR:** `dx` (139,562 rows), `appt` (31,237), `glucose` (22,767), `dob` (230 patients).
- **Literature:** Reviews and case series on ATTRv phenotypic spectrum (Journal of Neurology 2024; Methodist DeBakey CVJ 2022; AJMC; Canadian mixed-phenotype review 2025).

## 3. What EMR data do I have?
- **230 unique patients** across all tables.
- **189 patients** carry an explicit ICD-10 **E85.x** amyloidosis code.
- **41 additional patients** are amyloidosis-labelled but coded with legacy **ICD-9 codes 277.3 / 277.30 / 277.39** (plus Z84.89 family-history). Combining E85.x codes with any "amyloid" diagnosis name yields **211 amyloidosis patients**; the cohort is effectively amyloidosis-selected throughout.
- **Most frequent diagnoses (by patient count):** Amyloidosis unspecified E85.9 (144), Organ-limited E85.4 (117), Cardiomyopathy in diseases classified elsewhere I43 (109), Amyloid cardiomyopathy E85.4+I43 (78), Hereditary cardiac amyloidosis (74), Heredofamilial amyloidosis E85.2 (79), Cardiomegaly I51.7 (73), then hyperlipidemia (72), hypertension (68), heart failure I50.9 (62), abnormal ECG (60), polyneuropathy G62.9.
- **ATTR-relevant subtypes:** E85.2 heredofamilial (79), E85.1 neuropathic heredofamilial (50), E85.82 wild-type ATTR (40), E85.0 non-neuropathic heredofamilial (4), E85.81 AL/light-chain (7).
- **Age at latest dx (E85 pts):** median **70.9 yr** (IQR 60.7–78.1) — consistent with late-onset/wild-type-skewed ATTR.

## 4. Does EMR confirm the literature?
Yes. The literature states ATTRv presents as predominantly cardiac, predominantly neuropathic, or **mixed**, and that wild-type ATTR is predominantly cardiac.

Among the 189 E85.x patients (cardiac codes = I43/I50/I51/R94.31/I42; neuropathic = G62/G60/G99.0/G56.0):
- **Cardiac phenotype: 155 (82%)**
- **Neuropathic phenotype: 98 (52%)**
- **Mixed (both): 83 (44%)**
- Cardiac-only 72; neuropathic-only 15; neither-coded 19.

The **cardiac-predominant skew with a large mixed subset** matches the described ATTR spectrum. The older median age and 40 explicit wild-type (E85.82) diagnoses align with the cardiac dominance. **Carpal tunnel (G56.0), an early ATTR red flag, appears in 46 patients**, and appointment text shows engagement with cardiology (78), neurology (27) and genetics (14) — consistent with multidisciplinary ATTR care described in the literature.

## 5. Does EMR suggest anything new?
- **Mixed phenotype is common (44%)**, reinforcing literature calls for dual cardiac+neuro screening rather than single-specialty framing.
- **Neuropathy confounding:** 39/189 E85 patients also carry a diabetes code (E10/E11) — diabetic polyneuropathy could inflate the "neuropathic" tally, a real-world attribution caveat.
- **Coding heterogeneity is itself a finding:** the same clinical entity is split across ICD-9 (277.3x) and ICD-10 (E85.x), across HCC/non-HCC name variants, mixed casing, and compound codes ("E85.4, I43"). Any naive `code == 'E85'` filter under-counts the cohort by ~18% (189 vs 211+).

## 6. What did I build?
A reproducible pandas workflow that: (a) normalizes casing/prefixes to identify amyloidosis patients across ICD-9 and ICD-10, (b) classifies each patient into cardiac / neuropathic / mixed phenotype by code families, (c) tallies ATTR subtypes and the carpal-tunnel red flag, and (d) computes age-at-diagnosis and comorbidity (diabetes) confounders — all output as aggregates.

## 7. What did this teach me for the next project?
- **Never trust a single code prefix** — reconcile ICD-9/ICD-10 crosswalks and diagnosis-name text before counting a cohort.
- **Phenotyping by code families works** but must be pre-registered with an explicit confounder list (e.g., diabetes for neuropathy).
- **Next steps:** incorporate echo/biopsy/PYP-scan and genotype fields (absent here) to separate ATTRv from ATTRwt, and use appointment timelines to measure diagnostic delay — a known ATTR problem the current tables can only hint at.
