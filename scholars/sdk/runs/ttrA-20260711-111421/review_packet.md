# PI Review Packet — ttrA-20260711-111421

**Cohort:** A  ·  **Cycle:** 1

**Seed:** Seed question: Using cohort A's EMR data, characterize the TTR / hereditary ATTR amyloidosis cohort — how many patients are there, what are the most frequent diagnoses, and is the expected cardiac vs. neuropathic phenotype present among amyloidosis (ICD E85.x) patients?

## Registered questions (trajectory)
- **ttrA-20260711-111421-q0001** — L3 · research-mechanistic · seeded (from none) · 2 analyses
    Characterize cohort A's TTR/hereditary ATTR amyloidosis EMR cohort: how many patients, most frequent diagnoses, and whether the expected cardiac vs. neuropathic phenotype is present among amyloidosis (ICD E85.x) patients.
- **ttrA-20260711-111421-q0002** — L5 · research-mechanistic · self-generated (from ttrA-20260711-111421-q0001) · 3 analyses
    Among amyloidosis (E85.x) patients in cohort A, what is the patient-level distribution of cardiac vs. neuropathic phenotype markers, and does it match the ATTR literature expectation (ATTRv can be cardiac, neuropathic, or mixed; ATTRwt predominantly cardiac)?

**Edges:** ttrA-20260711-111421-q0001→ttrA-20260711-111421-q0002 (specializes)

**Capture discrepancies:** inflation=0 · abandoned=0

## Report


# Cohort A — TTR / Hereditary ATTR Amyloidosis: Characterization Report

*Synthetic EMR workflow exercise — findings are NOT clinically valid.*

## 1. What am I studying?
Hereditary transthyretin (TTR) amyloidosis (ATTRv) and its overlap with wild-type ATTR (ATTRwt), as represented in cohort A's EMR. ATTR is a systemic amyloidosis in which misfolded transthyretin deposits in tissue. The literature describes three broad presentations: **cardiac** (cardiomyopathy, HFpEF, conduction disease), **neuropathic** (length-dependent sensorimotor + autonomic polyneuropathy, carpal tunnel), and **mixed**. ATTRwt is predominantly cardiac and elderly; ATTRv varies by genotype.

## 2. Where do I find information?
Four preloaded EMR tables keyed by patient `ID`: `dx` (139,562 diagnosis rows / 230 patients), `appt` (31,237 rows), `glucose` (22,767 labs / 160 patients), `dob` (230 patients). Phenotype was inferred from ICD codes; no genotype/TTR-variant field is present. (External literature/connectors were unavailable this session — claims are grounded only in the EMR.)

## 3. What EMR data do I have?
- **230 patients total.** Median age **76.2 y** (mean 74.1, range 36–108) — an elderly cohort consistent with an ATTR population.
- **189 / 230 (82%)** carry at least one amyloidosis code (E85.x).
- **Top diagnoses (distinct patients):** E85.4 Organ-limited amyloidosis (100), I43 Cardiomyopathy (95), E85.9 Amyloidosis (90), E85.4+I43 Amyloid cardiomyopathy (61), I51.7 Cardiomegaly (60), R94.31 Abnormal ECG (51), plus valve/HF/hypertension codes.
- **ATTR subtype codes present:** E85.2 Heredofamilial (79 pts), E85.1 Neuropathic heredofamilial (50), E85.82 Wild-type ATTR (40).

### Data-quality problems found
1. **Compound codes** ("E85.4, I43" in a single field) affect 3,445 rows / 130 patients — breaks exact-code grouping; required substring matching.
2. **"10000 — ERRONEOUS ENCOUNTER--DISREGARD"** appears for 57 rows / 40 patients — junk that must be excluded.
3. **Inconsistent naming/casing** for the same code (e.g., E85.9 appears as "Amyloidosis (HCC)", "Amyloidosis, unspecified (HCC)", and ALL-CAPS variants; up to 13 distinct name strings for one code like Z23) — inflates naive name-based counts.
4. **No TTR genotype field** — ATTRv vs ATTRwt can only be proxied by ICD code.

## 4. Does the EMR confirm the literature?
**Largely yes.** Among the 189 E85.x patients:
| Phenotype | Patients | % |
|---|---|---|
| Cardiac markers (I43/I50/I51.7/E85.4/E85.82) | 154 | 81% |
| Neuropathic markers (E85.1/G99.0/G6x/G56.0/G90) | 105 | 56% |
| **Mixed (both)** | 90 | 48% |
| Cardiac only | 64 | 34% |
| Neuro only | 15 | 8% |
| Neither | 20 | 11% |

The **cardiac-predominant, high-mixed** pattern matches ATTR literature. Subtype coherence:
- **ATTRwt (E85.82):** 100% cardiac, 65% also carry neuro markers → cardiac-dominant, as expected.
- **Neuropathic heredofamilial (E85.1):** 100% neuro, but 84% *also* cardiac → the expected ATTRv mixed picture.
- **Heredofamilial (E85.2):** 76% cardiac / 62% neuro → mixed, as expected.

**Caveats:** E85.82 sits in the cardiac code list and E85.1 in the neuro list, so those two 100% figures are partly definitional/circular; the informative signals are the *cross-over* rates (ATTRwt 65% neuro, E85.1 84% cardiac). The "neither" group (20 pts) likely reflects unspecified E85.9 coding without organ-specific follow-through.

## 5. Does the EMR suggest anything new?
- **Diabetes as a neuropathy confounder:** 27 of 110 neuro-marker patients (25%) also carry E11 (type 2 diabetes). Diabetic polyneuropathy could inflate "neuropathic" attribution — a genotype/nerve-biopsy field would be needed to disentangle true amyloid neuropathy. This motivates the glucose table's relevance.
- Neuro-marker patients trend slightly younger (mean 70.9 y) than cardiac-marker patients (73.9 y), directionally consistent with ATTRv neuropathy presenting earlier than ATTRwt cardiomyopathy.

## 6. What did I build?
A reproducible patient-level phenotyping pipeline that (a) normalizes messy ICD coding, (b) handles compound codes via substring matching, (c) excludes erroneous encounters, and (d) classifies each E85.x patient as cardiac / neuropathic / mixed / neither, then cross-tabulates against ATTR subtype and age. Two research questions registered (q0001 seed, q0002 phenotype specialization).

## 7. What did this teach me for the next project?
- **Audit coding hygiene first** — compound codes, casing variants, and junk codes ("10000") silently corrupt frequency counts; count by *distinct patient* not rows.
- **Avoid circular phenotype definitions** — don't let the classifying code double as an outcome marker; separate defining codes from evidence codes.
- **Anticipate confounders** (diabetes↔neuropathy) and check for a genotype field before over-interpreting ATTRv vs ATTRwt from ICD codes alone.
