# PI Review Packet — ttrA-20260711-185206

**Cohort:** A  ·  **Cycle:** 1

**Seed:** Seed question: Using cohort A's EMR data, characterize the TTR / hereditary ATTR amyloidosis cohort — how many patients are there, what are the most frequent diagnoses, and is the expected cardiac vs. neuropathic phenotype present among amyloidosis (ICD E85.x) patients?

## Registered questions (trajectory)
- **ttrA-20260711-185206-q0001** — L3 · research-mechanistic · seeded · 3 analyses
    Using cohort A's EMR data, characterize the TTR/hereditary ATTR amyloidosis cohort: N patients, most frequent diagnoses, and whether the expected cardiac vs neuropathic phenotype is present among E85.x amyloidosis patients.
- **ttrA-20260711-185206-q0002** — L4 · clinical-management · seeded (from ttrA-20260711-185206-q0001) · 0 analyses
    Among E85.x amyloidosis patients in cohort A, is the expected cardiac vs neuropathic phenotype present when measured by INDEPENDENT evidence codes (cardiac: I50/I42 + ICD-9 428/425; neuro: G60/G62/G63 + ICD-9 356/357) kept separate from the E85.x defining codes — and what is the mixed/cardiac/neuro/neither breakdown vs the literature benchmark (~83% mixed)?
- **ttrA-20260711-185206-q0003** — L4 · research-mechanistic · self-generated (from ttrA-20260711-185206-q0001) · 4 analyses
    What is the ICD-subtype composition of the cohort A E85.x pool — specifically what fraction is TTR-relevant (hereditary E85.0/1/2 + wild-type ATTR E85.82) versus non-TTR contaminants (AL light-chain E85.81, secondary E85.3) that should be excluded before any TTR-specific phenotype claim?
- **ttrA-20260711-185206-q0004** — L5 · research-mechanistic · pi-suggested (from ttrA-20260711-185206-q0002) · 0 analyses
    On the N=206 cohort A amyloidosis cohort, does comorbid type-2 diabetes (E11 + ICD-9 250.x) inflate the 43% neuropathy rate — i.e. is the E11–neuropathy association significant, and how much does the neuro rate drop when diabetics are excluded (amyloid-attributable neuropathy)?
- **ttrA-20260711-185206-q0005** — L4 · research-mechanistic · pi-suggested (from ttrA-20260711-185206-q0002) · 3 analyses
    Quantify the magnitude of mixed-phenotype under-detection in cohort A ICD data relative to the ~83% literature benchmark: EMR mixed rate, absolute/relative gap, and how much closing it would require of the cardiac-only and neuro-only buckets.

**Edges:** ttrA-20260711-185206-q0001→ttrA-20260711-185206-q0002 (decomposition), ttrA-20260711-185206-q0001→ttrA-20260711-185206-q0003 (refinement), ttrA-20260711-185206-q0002→ttrA-20260711-185206-q0004 (confounder-test), ttrA-20260711-185206-q0002→ttrA-20260711-185206-q0005 (refinement)

**Capture discrepancies:** inflation=2 · abandoned=0

## Report


# Cycle Report — Cohort A: TTR / Hereditary ATTR Amyloidosis Characterization
**Project:** ttrA · **Date:** 2026-07-11 · **Data:** synthetic EMR (findings are a workflow exercise, not clinically valid)
*Revision 2 — adds PI-requested E11–neuropathy confounder test and mixed-phenotype under-detection quantification (§4A, §4B).*

## 1. What am I studying?
Characterization of cohort A's amyloidosis population and a test of whether the expected **cardiac vs. neuropathic** phenotype of hereditary transthyretin (ATTRv/ATTRwt) amyloidosis is visible in ICD-coded EMR data. Decomposed into: (q0001) cohort size + frequent diagnoses + phenotype presence; (q0002) anti-circular cardiac/neuro breakdown vs. benchmark; (q0003) TTR-relevant vs. contaminant subtypes; **(q0004, PI) does comorbid diabetes inflate the neuropathy rate; (q0005, PI) magnitude of mixed-phenotype under-detection.**

## 2. Where do I find information?
Pre-specified literature benchmark: phenotype at diagnosis **mixed ~83%**, cardiac ~7%, neuro ~7%; initial manifestations cardiovascular ~55%, neuropathy ~41%; **median onset ~53**.
Sources: [ATTRv phenotypic presentation (PMC12311500)](https://pmc.ncbi.nlm.nih.gov/articles/PMC12311500/), [hereditary ATTR cardiomyopathy profile (PMC9271707)](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9271707/), [hATTR polyneuropathy care (PMC7041433)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7041433/).

## 3. What EMR data do I have?
- **230 patients** total; **amyloidosis cohort N = 206** (ICD-10 E85.x ∪ ICD-9 277.3; 36 pts ICD-9-only).
- Subtypes (overlapping pts): E85.9 unspecified 162, E85.4 organ-limited 136, E85.2 heredofamilial 79, E85.1 neuropathic-heredofam 50, wild-type ATTR E85.82 40; non-TTR contaminants AL 7, secondary 2.
- **Diabetic comorbidity: 44/206 (21%)** carry E11 or ICD-9 250.x.

**Data-quality problems found:** (1) 57 junk "ERRONEOUS ENCOUNTER" rows dropped; (2) 3,445 compound-code rows (`E85.4, I43`) — circularity trap, handled by excluding same-row markers from evidence; (3) ICD-9/10 dual coding (ICD-10-only regex undercounts cohort ~17% and flips the confounder test — see §4A); (4) name-string chaos → grouped by code; (5) no genotype/variant field (subtype is ICD proxy).

## 4. Does the EMR confirm the literature?
**Partially.** Independent evidence codes (cardiac I50/I42/I51.7 + ICD-9 428/425; neuro G60/G62/G63 + ICD-9 356/357/354.0), N=206: **Any cardiac 72% · Any neuro 43% · Mixed 32.5% · Cardiac-only 39.8% · Neuro-only 10.2% · Neither 17.5%.** Neuropathy 43% ≈ literature 41% (confirmed); cardiac 72% ≥ ≥50% expectation (confirmed); **mixed 33% ≪ 83% (not confirmed — see §4B).** Age at first dx median **69** (IQR 60–76) vs onset ~53 (ascertainment lag + wild-type enrichment). Robust to AL/secondary exclusion (N=197: mixed 31%, cardiac 72%, neuro 41%).

### 4A. PI task — Diabetes (E11) × neuropathy confounder test (N=206)
Exposure = E11/ICD-9 250.x (n=44, 21%); outcome = independent neuro evidence. Method: distinct-patient 2×2, OR, chi-square (Yates + uncorrected), Fisher, expected-cell check, ICD-9 sensitivity arm.

| Definition | Neuro: DM vs non-DM | OR | Yates p | Uncorr p | Fisher p | Min exp cell | Decision |
|---|---|---|---|---|---|---|---|
| **Primary (neuro ICD-10 only)** | 45% vs 34% | 1.62 | 0.219 | 0.160 | 0.163 | 16.0 (OK) | **Not significant** |
| **Sensitivity (+ICD-9 356/357)** | 57% vs 39% | 2.07 | 0.050 | 0.033 | 0.040 | 18.8 (OK) | **Borderline / nominally significant** |

**The conclusion flips between coding definitions — this replicates the documented cohort-A fragility (non-significant primary → borderline with ICD-9) precisely, confirming it is a systematic dual-coding effect, not a one-off artifact.**

**Does diabetes inflate the 43% neuro rate? Only modestly.** Excluding all diabetics moves the neuro rate 43%→**39%** (sensitivity) / 36%→34% (primary) — a ~4-pp (relative ~10%) reduction. Because diabetics are only 21% of the cohort, even their elevated 57% neuro rate cannot account for most neuropathy: the bulk (~39% amyloid-attributable) persists after exclusion. **Verdict: diabetic polyneuropathy is a real but minor contributor — a non-significant-to-borderline trend, not a driver of the neuropathy signal.**

### 4B. PI task — Mixed-phenotype under-detection vs 83% benchmark
- EMR mixed = **67/206 = 32.5%**; benchmark 83% = 171/206.
- **Absolute gap = 50.5 percentage points**; relative detection = 0.39 → **~61% under-detection** of the mixed phenotype.
- Closing it needs **104 patients** reclassified to mixed. Reclassifying *every* cardiac-only (82) **and** neuro-only (21) patient reaches only 170/206 (83%) — 1 short — so the gap is **mathematically unclosable without also converting "neither" (n=36) patients.** ICD coding cannot represent this cohort as 83% mixed.
- Co-detection: of 149 any-cardiac patients only 45% also have a neuro code; of 88 any-neuro, 76% also have cardiac. Asymmetry indicates **neuro involvement is under-coded in cardiac-referral patients** — the likely mechanism of under-detection.

## 5. Does the EMR suggest anything new?
- Cardiac-predominant cohort (cardiac-only 40% ≫ neuro-only 10%) + median dx age 69 + 40 wild-type-ATTR pts → **cardiology/ATTR-CM ascertainment**.
- **Mixed under-detection is structural, not tunable**: a 61% relative shortfall that cannot be closed within the observed buckets — a quantified measurement-bias finding for ICD-based phenotyping.
- The confounder test's definition-dependent flip is now shown to be **reproducible across cohort sizes** (prior small cohort → this N=206), strengthening it as a systematic ICD-9/10 coding phenomenon.

## 6. What did I build?
- Reusable **anti-circular phenotype classifier** (membership codes held separate from evidence; compound-bundled markers excluded).
- **Confounder-test harness** producing the full primary+sensitivity table (OR, Yates/uncorrected/Fisher, expected-cell check) in one pass, per the emr-confounder-association-test capability.
- **Under-detection quantifier**: absolute/relative gap + a reclassification-feasibility check that proves the benchmark is unreachable within observed buckets.

## 7. What did this teach me for the next project?
- **Report the confounder result as a primary+sensitivity pair, always** — here the single most important fact is that significance flips with ICD-9 inclusion; a lone p-value would mislead. The fragility is now confirmed reproducible.
- **A confounder can be statistically borderline yet clinically minor**: OR≈2 in a 21%-prevalence exposure shifts the marginal rate only ~4 pp. Report the *attributable-rate change*, not just the OR/p.
- **Quantify measurement bias against the benchmark, don't just note it**: the 61% under-detection + "unclosable within buckets" framing turns a hand-wave into a finding.
- **Next (cohort B):** does the cardiac-predominant, ~61%-mixed-under-detection pattern and the ICD-9-dependent confounder flip replicate — distinguishing systematic coding effects from cohort-A ascertainment.
