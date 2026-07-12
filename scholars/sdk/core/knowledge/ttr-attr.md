# ttr-attr


## cycle 1 · ttrA-20260711-111421 · 2026-07-11
Cohort A EMR (synthetic; NOT clinically valid): 230 patients, median age 76.2y (range 36–108); 189/230 (82%) carry an E85.x amyloidosis code. Among E85.x patients the pattern is cardiac-predominant (81%) with high mixed (48%). Data caveats: compound codes ('E85.4, I43') affect 130 patients; an erroneous-encounter junk code ('10000') affects 40 patients; one code can carry up to 13 distinct name strings; NO TTR genotype field exists, so ATTRv vs ATTRwt is only an ICD proxy. 25% of neuro-marker patients also carry E11 (T2 diabetes) — a polyneuropathy confounder.


## cycle 1 · ttrA-20260711-135248 · 2026-07-11
Validated benchmarks (web-grounded, pre-specified): ATTRwt median dx age ~73, predominantly cardiac; hereditary ATTR onset ~50-75, mixed cardiac+neuropathic common (Val122Ile cardiac-limited; Val30Met neuropathic). Cohort A (synthetic, distinct patients, cleaned): 230 patients, 189 (82%) carry E85.x. Reproduced age gradient: wild-type E85.82 median 78 vs neuropathic-hereditary E85.1 median 64. Phenotype buckets among 189: mixed 84, cardiac-only 69, neuro-only 15, neither 21 (cardiac-predominant, mixed largest). Data caveats: 57 'ERRONEOUS ENCOUNTER' rows must be dropped; compound codes pack >=2 ICDs per field and 105 patients' cardiac involvement is hidden inside 'E85.4, I43' (exact-match misses them, use substring/regex); no genotype field, so subtype is an ICD proxy only. Diabetes-neuropathy association in cohort A: OR 1.83, primary p=0.14 (not significant); borderline (p=0.04) only with ICD-9 markers added.


## cycle 1 · ttrA-20260711-185206 · 2026-07-11
Cohort A (synthetic EMR, not clinically valid): 230 patients; amyloidosis N=206 (E85.x ∪ ICD-9 277.3; 36 ICD-9-only). ICD-10-only regex undercounts the cohort ~17% and can flip confounder results — dual-coding is a systematic, reproducible effect across cohort sizes, not a one-off. Diabetic comorbidity 44/206 (21%); excluding diabetics moves neuro rate only ~4pp (43%→39%), so diabetic polyneuropathy is a minor, non-significant-to-borderline contributor, not the driver. Mixed phenotype detected 32.5% vs 83% literature benchmark → ~61% relative under-detection; gap cannot be closed within cardiac-only+neuro-only buckets. Literature benchmark: mixed ~83%, median onset ~53 (cohort median dx age 69 → ascertainment lag).
