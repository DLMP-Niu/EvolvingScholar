
# Cohort A — TTR / Hereditary ATTR Amyloidosis Characterization
*Synthetic-data workflow exercise. Findings are NOT clinically valid.*

## 1. What am I studying?
Characterization of cohort A's amyloidosis population: how many patients, the most frequent diagnoses, and whether the expected **cardiac vs. neuropathic** phenotype split of ATTR amyloidosis is reflected among amyloidosis (ICD **E85.x**) patients. Spawned sub-questions: hereditary vs. wild-type ATTR distribution, and whether **diabetes** confounds the neuropathic signal.

## 2. Where do I find information?
- **EMR (cohort A):** `dx` (139,562 rows / 230 pts), `appt`, `glucose` (mixed-analyte lab table), `dob`.
- **Literature (from training knowledge; would need live citation to verify):** ATTR amyloidosis presents as a spectrum — ATTRwt is predominantly **cardiac** (older men, HFpEF/cardiomyopathy); hereditary ATTRv can be **neuropathic (ATTR-PN)**, **cardiac (ATTR-CM)**, or **mixed**, genotype-dependent (e.g., Val30Met neuropathic; Val122Ile/Thr60Ala cardiac). Mixed phenotype is increasingly recognized. Diabetic peripheral neuropathy is a major competing cause of polyneuropathy.

## 3. What EMR data do I have?
- **230 patients total**; **189 (82%) carry ≥1 E85.x amyloidosis code**.
- Most frequent diagnoses (by unique patients): Amyloidosis unspecified (E85.9, 144), Organ-limited (E85.4, 117), **Cardiomyopathy in disease elsewhere (I43, 109)**, Amyloid cardiomyopathy (E85.4+I43, 78), Heredofamilial amyloidosis (E85.2, 74), Cardiomegaly (I51.7, 73), plus HF (I50.9, 62), abnormal ECG (R94.31, 60), **polyneuropathy (G62.9, 56)**. Comorbid hyperlipidemia/hypertension are common background codes.
- **Age (E85.x):** median 72.4 y (IQR 61.6–79.5) — consistent with the older ATTR demographic.

**Data-quality problems found:**
1. **Name variants for identical codes** (e.g., "Amyloidosis, unspecified (HCC)" vs "AMYLOIDOSIS, UNSPECIFIED") — grouping must key on code, not name.
2. **Comma-combined codes** (e.g., `E85.4, I43`) — a single field holds two ICD codes; requires substring matching.
3. **Contradictory subtyping:** 25 patients carry *both* hereditary (E85.0/1/2) *and* wild-type (E85.82) codes — mutually exclusive by definition.
4. **`glucose` table is not pure glucose:** units include %, % A1C, pg/mL, mcg/mL — HbA1c and other analytes are mixed in; must filter to mg/dL (~21.9k rows) before analysis.

## 4. Does EMR confirm the literature?
**Yes, directionally.** Among 189 E85.x patients:
- **Cardiac phenotype: 158 (83.6%)** — I43/I50/I51.7/amyloid-cardiomyopathy markers.
- **Neuropathic phenotype: 104 (55.0%)** — E85.1/G62/G99.0/neuropathy markers.
- **Mixed (both): 92 (48.7%)**; cardiac-only 66; neuro-only 12; neither 19.

The strong **cardiac predominance** and older age fit the expected ATTR-CM–heavy picture, while a substantial neuropathic and mixed fraction matches the known ATTR phenotype spectrum. Subtype codes: hereditary heredofamilial (E85.0/1/2) = **100 pts**, wild-type ATTR (E85.82) = **40 pts**.

## 5. Does EMR suggest anything new?
- **The neuropathy signal is partly confounded by diabetes.** Neuropathy-coded E85 patients had higher max glucose (median **155 vs 112 mg/dL**) and far more hyperglycemia (**31/83 ≥200 mg/dL vs 9/50**); 28/104 also carry a diabetes dx. So a meaningful share of "neuropathic" coding may reflect **diabetic** rather than amyloid neuropathy — caution before attributing polyneuropathy to ATTR.
- **~49% mixed phenotype** is high; combined with the 25 hereditary+wildtype coding contradictions, this suggests **coding noise inflates apparent overlap** — a caveat for any phenotype-based stratification.

## 6. What did I build?
- A code-based (not name-based) phenotype classifier for E85.x patients splitting cardiac / neuropathic / mixed, robust to case variants and comma-combined ICD fields.
- A unit-filtered glucose extractor (mg/dL only) to test diabetes as a confounder.
- A catalogue of 4 concrete data-quality issues for downstream cleaning.

## 7. What did this teach me for the next project?
- **Always key aggregations on ICD code, never free-text name**, and pre-split multi-code fields.
- **Validate lab tables by unit** before trusting values — a "glucose" table held HbA1c and other analytes.
- **Confounders (diabetes → neuropathy)** must be checked before interpreting phenotype prevalence; phenotype from claims codes ≠ verified genotype/mechanism.
- Next step would be linking to actual **TTR genotype** and separating ATTRwt vs ATTRv phenotypes, and resolving the 25 contradictory-subtype patients.
