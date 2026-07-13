# PI Review Packet — ttrA-20260711-135248

**Cohort:** A  ·  **Cycle:** 1

**Seed:** Seed question: Using cohort A's EMR data, characterize the TTR / hereditary ATTR amyloidosis cohort — how many patients are there, what are the most frequent diagnoses, and is the expected cardiac vs. neuropathic phenotype present among amyloidosis (ICD E85.x) patients?

## Registered questions (trajectory)
- **ttrA-20260711-135248-q0001** — L3 · research-mechanistic · seeded · 2 analyses
    Using cohort A's EMR, how many TTR/ATTR amyloidosis patients are there, what are the most frequent diagnoses, and is the expected cardiac vs neuropathic phenotype present among E85.x patients?
- **ttrA-20260711-135248-q0002** — L4 · clinical-management · seeded (from ttrA-20260711-135248-q0001) · 4 analyses
    Among cohort A E85.x amyloidosis patients, is the expected cardiac vs neuropathic phenotype split present, using INDEPENDENT evidence codes (cardiac: I50/I42/I43 heart failure/cardiomyopathy; neuropathic: G60/G62/G56.0 carpal tunnel/G99.0 autonomic) kept separate from the defining E85 codes?
- **ttrA-20260711-135248-q0003** — L5 · research-mechanistic · self-generated (from ttrA-20260711-135248-q0002) · 5 analyses
    Does comorbid type-2 diabetes (E11) account for part of the neuropathic phenotype signal among E85.x patients — i.e. is diabetic polyneuropathy inflating the amyloid-attributable neuropathy rate? Compare neuro-marker prevalence in diabetic vs non-diabetic amyloidosis patients.

**Edges:** ttrA-20260711-135248-q0001→ttrA-20260711-135248-q0002 (decomposition), ttrA-20260711-135248-q0002→ttrA-20260711-135248-q0003 (confound-control)

**Capture discrepancies:** inflation=0 · abandoned=0

## Report


# TTR / Hereditary ATTR Amyloidosis — Cohort A Characterization
*Cycle ttrA-20260711-135248 · synthetic EMR · findings are a workflow exercise, not clinically valid*

## 1. What am I studying?
Characterization of cohort A's TTR / hereditary ATTR amyloidosis population: cohort size, most frequent diagnoses, and whether the expected **cardiac vs. neuropathic** phenotype of ATTR is detectable among amyloidosis (ICD **E85.x**) patients. I extended the seed with two testable sub-questions: (a) subtype cross-over between wild-type (E85.82) and neuropathic-hereditary (E85.1) codes using *independent* evidence markers, and (b) whether comorbid type-2 diabetes inflates the neuropathic signal (carried forward from cycle 1's next-question ledger).

## 2. Where do I find information?
- **EMR**: `dx` (139,562 rows / 230 patients), `appt`, `glucose`, `dob`.
- **Literature benchmarks (pre-specified before any confirmation claim)**: wild-type ATTR (ATTRwt) median diagnosis age ~73, **predominantly cardiac**; hereditary ATTR onset ~50–75 (mostly post-60), with **mixed cardiac+neuropathic phenotype common** (US-common Val122Ile = cardiac-limited; Val30Met = neuropathic). Sources: [Diagnosis/Screening of hATTR (PMC7434568)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7434568/), [ATTRwt <65 characteristics (PMC12681563)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12681563/), [Hereditary ATTR, UCL](https://www.ucl.ac.uk/medical-sciences/sites/medical_sciences/files/hereditary_attr_amyloidosis.pdf).

## 3. What EMR data do I have? (ran ICD hygiene audit first)
- **230 patients**; **189 (82%) carry an E85.x code** = the amyloidosis cohort. The other 41 carry no E85 code (plausibly at-risk relatives / screening encounters).
- **Data-quality problems found & corrected:**
  1. **57 erroneous-encounter rows** ("ERRONEOUS ENCOUNTER--DISREGARD") — dropped before all counts.
  2. **Compound codes**: 3,445 rows (130 patients) pack ≥2 ICD codes in one field. Critically, **105 patients' cardiac involvement is hidden inside `E85.4, I43` (Amyloid Cardiomyopathy)** — an exact-match on `E85.4` would silently miss them. Used substring/regex matching throughout.
  3. **Name-variant proliferation**: same code appears under many strings (ALL-CAPS, `(HCC)` suffix, "unspecified" variants). Grouped by **code**, never by name.
  4. **ICD-9 / ICD-10 dual coding**: 70 patients carry ICD-9-style numeric codes (temporal legacy). My phenotype regex is ICD-10-based; adding ICD-9 equivalents raised the neuro count 99→106 (+7) and cardiac unchanged — a **modest neuro undercount**, no change to the overall picture.
  5. **No genotype / TTR-variant field**: subtype is an ICD proxy only; cannot resolve specific mutations (Val122Ile vs Val30Met) or definitively separate hereditary from wild-type.
- Counts are reported as **distinct patients**, not rows.

**Most frequent diagnoses (distinct patients, of 230, cleaned):** E85.9 Amyloidosis unspec (162), E85.4 Organ-limited (130), I43 Cardiomyopathy (119), `E85.4, I43` Amyloid cardiomyopathy (105), I51.7 Cardiomegaly (82), I10 Hypertension (79), E85.2 Heredofamilial (79), I50.9 Heart failure (74), R94.31 Abnormal ECG (68), **G62.9 Polyneuropathy (64)**, I48.91 AFib (47), E85.1 Neuropathic heredofam (50), E85.82 Wild-type ATTR (40). The frequency profile is **cardiac-dominant**, with polyneuropathy the leading neuropathic marker.

## 4. Does the EMR confirm the literature?
**Yes, directionally, against pre-specified benchmarks.** Using **independent evidence codes** (cardiac: I50/I42/I43/I51.7/I44/I45/I48; neuro: G60/G62/G56.0/G99.0/G57) kept **separate from the defining E85 codes** to avoid circularity:
- **Both phenotypes present, cardiac-predominant**: of 189 E85 patients — cardiac evidence 153 (81%), neuro evidence 106 (56%); buckets: **mixed 84, cardiac-only 69, neuro-only 15, neither 21**. Mixed phenotype being the largest bucket matches the literature's "overlap is common."
- **Subtype cross-over matches expectation**: Wild-type ATTR (E85.82, N=40) = **98% cardiac**, 68% neuro (bilateral carpal tunnel is a known wtATTR red flag). Neuropathic-hereditary (E85.1, N=50) = **88% neuro**, but also 82% cardiac → strong mixed overlap, as expected for hereditary ATTR.
- **Age gradient matches**: median age at first E85 dx — overall 69; **wild-type 78** vs **neuropathic-hereditary 64** / heredofam-unspec 66. The wild-type > hereditary ordering and the ~73 wtATTR benchmark are both reproduced. Age sanity clean (range 31–91, no impossible values).

## 5. Does the EMR suggest anything new? (falsifiable test)
**Hypothesis (from cycle 1): diabetic polyneuropathy inflates the neuropathic phenotype rate. → Partially supported.**
- Diabetic (E11+) amyloidosis patients: **neuro-marker+ 64%** (25/39) vs non-diabetic **49%** (74/150) — a ~15 percentage-point excess consistent with diabetic neuropathy contributing to the signal.
- But **25% of neuro-marker+ patients are diabetic**, and neuropathy remains prevalent (49%) in non-diabetics — so diabetes **inflates but does not explain** the neuropathic phenotype. The amyloid-attributable neuropathy signal survives confounder stratification.
- *Caveat*: descriptive only; no significance test given synthetic data and small diabetic stratum (N=39). ICD cannot etiologically separate amyloid from diabetic neuropathy without a genotype/biopsy field.

## 6. What did I build?
- A **reusable cleaning pipeline** for this cohort: junk-row removal → compound-code-aware substring matching → group-by-code → patient-level dedup, with an explicit ICD-9/ICD-10 reconciliation check.
- A **patient-level phenotype classifier** (cardiac/neuropathic/mixed/neither) built from independent evidence codes, plus a **subtype cross-over** report (wild-type vs neuropathic-hereditary) that is informative rather than definitional.
- A **confounder-stratified test** converting cycle 1's observation into a falsifiable diabetes-vs-amyloid neuropathy comparison.

## 7. What did this teach me for the next project?
- **Compound codes can hide the primary phenotype.** Here the single most important cardiac signal (amyloid cardiomyopathy) was buried in a comma-packed field for 105 patients; exact-match would have understated cardiac involvement badly. Always substring-match against target codes on EMR dx fields.
- **Check for dual coding systems (ICD-9/10) explicitly** — a phenotype regex written for one era silently undercounts the other.
- **The confirmation held because benchmarks were fixed first** (wtATTR ~73/cardiac; hereditary mixed) — the age-gradient and phenotype-split claims were testable, not post-hoc.
- **Next cycle's question**: The 21 "neither"-phenotype and 41 non-E85 patients are unexplained — are they early/screening/at-risk relatives, or organ-limited (renal N18 / GI) presentations not captured by cardiac+neuro markers? Test whether a **renal/GI/ocular** marker set reclassifies the "neither" bucket, and whether non-E85 patients cluster as pre-symptomatic gene-carriers (would need a genotype field the EMR currently lacks — flag as a data-model gap).
