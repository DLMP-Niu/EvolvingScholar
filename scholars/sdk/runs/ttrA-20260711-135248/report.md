
# TTR / Hereditary ATTR Amyloidosis — Cohort A Characterization
*Cycle ttrA-20260711-135248 · synthetic EMR · findings are a workflow exercise, not clinically valid*
*Updated per PI review: diabetes–neuropathy association now formally tested (§5).*

## 1. What am I studying?
Characterization of cohort A's TTR / hereditary ATTR amyloidosis population: cohort size, most frequent diagnoses, and whether the expected **cardiac vs. neuropathic** phenotype of ATTR is detectable among amyloidosis (ICD **E85.x**) patients. I extended the seed with two testable sub-questions: (a) subtype cross-over between wild-type (E85.82) and neuropathic-hereditary (E85.1) codes using *independent* evidence markers, and (b) whether comorbid type-2 diabetes inflates the neuropathic signal — now escalated from a directional observation to a **formal chi-square test** (PI-requested).

## 2. Where do I find information?
- **EMR**: `dx` (139,562 rows / 230 patients), `appt`, `glucose`, `dob`.
- **Literature benchmarks (pre-specified before any confirmation claim)**: wild-type ATTR (ATTRwt) median diagnosis age ~73, **predominantly cardiac**; hereditary ATTR onset ~50–75 (mostly post-60), with **mixed cardiac+neuropathic phenotype common** (US-common Val122Ile = cardiac-limited; Val30Met = neuropathic). Sources: [Diagnosis/Screening of hATTR (PMC7434568)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7434568/), [ATTRwt <65 characteristics (PMC12681563)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12681563/), [Hereditary ATTR, UCL](https://www.ucl.ac.uk/medical-sciences/sites/medical_sciences/files/hereditary_attr_amyloidosis.pdf).

## 3. What EMR data do I have? (ran ICD hygiene audit first)
- **230 patients**; **189 (82%) carry an E85.x code** = the amyloidosis cohort. The other 41 carry no E85 code (plausibly at-risk relatives / screening encounters).
- **Data-quality problems found & corrected:**
  1. **57 erroneous-encounter rows** ("ERRONEOUS ENCOUNTER--DISREGARD") — dropped before all counts.
  2. **Compound codes**: 3,445 rows (130 patients) pack ≥2 ICD codes in one field. Critically, **105 patients' cardiac involvement is hidden inside `E85.4, I43` (Amyloid Cardiomyopathy)** — an exact-match on `E85.4` would silently miss them. Used substring/regex matching throughout.
  3. **Name-variant proliferation**: same code appears under many strings (ALL-CAPS, `(HCC)` suffix, "unspecified" variants). Grouped by **code**, never by name.
  4. **ICD-9 / ICD-10 dual coding**: 70 patients carry ICD-9-style numeric codes (temporal legacy). My phenotype regex is ICD-10-based; adding ICD-9 equivalents raised the neuro count 99→106 (+7), cardiac unchanged — a **modest neuro undercount**. This ambiguity turns out to be **decision-relevant for the diabetes test** (see §5).
  5. **No genotype / TTR-variant field**: subtype is an ICD proxy only; cannot resolve specific mutations (Val122Ile vs Val30Met) or definitively separate hereditary from wild-type.
- Counts are reported as **distinct patients**, not rows.

**Most frequent diagnoses (distinct patients, of 230, cleaned):** E85.9 Amyloidosis unspec (162), E85.4 Organ-limited (130), I43 Cardiomyopathy (119), `E85.4, I43` Amyloid cardiomyopathy (105), I51.7 Cardiomegaly (82), I10 Hypertension (79), E85.2 Heredofamilial (79), I50.9 Heart failure (74), R94.31 Abnormal ECG (68), **G62.9 Polyneuropathy (64)**, I48.91 AFib (47), E85.1 Neuropathic heredofam (50), E85.82 Wild-type ATTR (40). The frequency profile is **cardiac-dominant**, with polyneuropathy the leading neuropathic marker.

## 4. Does the EMR confirm the literature?
**Yes, directionally, against pre-specified benchmarks.** Using **independent evidence codes** (cardiac: I50/I42/I43/I51.7/I44/I45/I48; neuro: G60/G62/G56.0/G99.0/G57) kept **separate from the defining E85 codes** to avoid circularity:
- **Both phenotypes present, cardiac-predominant**: of 189 E85 patients — cardiac evidence 153 (81%), neuro evidence 106 (56%); buckets: **mixed 84, cardiac-only 69, neuro-only 15, neither 21**. Mixed phenotype being the largest bucket matches the literature's "overlap is common."
- **Subtype cross-over matches expectation**: Wild-type ATTR (E85.82, N=40) = **98% cardiac**, 68% neuro (bilateral carpal tunnel is a known wtATTR red flag). Neuropathic-hereditary (E85.1, N=50) = **88% neuro**, but also 82% cardiac → strong mixed overlap, as expected for hereditary ATTR.
- **Age gradient matches**: median age at first E85 dx — overall 69; **wild-type 78** vs **neuropathic-hereditary 64** / heredofam-unspec 66. The wild-type > hereditary ordering and the ~73 wtATTR benchmark are both reproduced. Age sanity clean (range 31–91, no impossible values).

## 5. Does the EMR suggest anything new? (formal test — REVISED per PI)
**Hypothesis (cycle 1): diabetic polyneuropathy inflates the neuropathic phenotype rate.**
The directional gap does **not** hold up as a significant association under the pre-specified definition — a formal test tempers the cycle-1 concern.

**Primary test — ICD-10 neuro markers (the definition used for §4 characterization):**

| E85.x patients | neuro+ | neuro− | total | % neuro+ |
|---|---|---|---|---|
| **Diabetic (E11+)** | 25 | 14 | 39 | 64% |
| **Non-diabetic** | 74 | 76 | 150 | 49% |

- Chi-square (Yates-corrected): **χ²=2.147, df=1, p=0.143** → **not significant** at α=0.05.
- Uncorrected χ²=2.707, p=0.100; Fisher exact **p=0.109, OR=1.83**.
- All expected cell counts >5 (min 18.6), so the chi-square assumption is met.

**Sensitivity test — adding ICD-9 neuro markers (356/357/354.0):**

| E85.x patients | neuro+ | neuro− | total | % neuro+ |
|---|---|---|---|---|
| **Diabetic (E11+)** | 28 | 11 | 39 | 72% |
| **Non-diabetic** | 78 | 72 | 150 | 52% |

- Chi-square (Yates): **χ²=4.153, df=1, p=0.042**; Fisher **p=0.030, OR=2.35** → borderline significant.

**Conclusion:** The association is a **non-significant trend under the primary definition (OR 1.83, p=0.14)** and reaches nominal significance **only** when ICD-9 markers are added (OR 2.35, p=0.04). Because significance flips across a defensible coding choice, the result is **fragile and definition-dependent** — I do *not* claim diabetes significantly inflates the neuropathic signal. What survives is: (i) a consistent positive direction (OR ~1.8–2.4), and (ii) the fact that neuropathy remains prevalent (49–52%) in non-diabetics, so amyloid-attributable neuropathy is not an artifact of diabetes. *Caveats*: single 2×2, no multiplicity control, small diabetic stratum (N=39), synthetic data — not clinically valid.

## 6. What did I build?
- A **reusable cleaning pipeline**: junk-row removal → compound-code-aware substring matching → group-by-code → patient-level dedup, with explicit ICD-9/ICD-10 reconciliation.
- A **patient-level phenotype classifier** (cardiac/neuropathic/mixed/neither) from independent evidence codes, plus an informative (non-definitional) **subtype cross-over** report.
- A **formal 2×2 association test** (chi-square with Yates correction + Fisher exact + OR) with a **coding-definition sensitivity analysis** that exposed the result's fragility.

## 7. What did this teach me for the next project?
- **Directional ≠ significant.** The 64% vs 49% gap looked like a real confounder in cycle 1, but a formal test returned p=0.14 under the primary definition. Escalate suggestive gaps to a stated test before treating them as findings.
- **A coding choice can decide significance.** Whether the diabetes–neuropathy p-value lands at 0.04 or 0.14 hinges on including ICD-9 markers — so I now report a definition **sensitivity analysis** alongside any borderline p-value, rather than a single number.
- **Compound codes can hide the primary phenotype** (105 cardiac patients buried in `E85.4, I43`); always substring-match on EMR dx fields.
- **The confirmation held because benchmarks were fixed first** (wtATTR ~73/cardiac; hereditary mixed) — the phenotype-split and age-gradient claims were testable, not post-hoc.
- **Next cycle's question**: The 21 "neither"-phenotype and 41 non-E85 patients are unexplained — test whether a **renal/GI/ocular** marker set reclassifies the "neither" bucket, and whether non-E85 patients cluster as pre-symptomatic gene-carriers (needs a genotype field the EMR currently lacks — flag as a data-model gap).
