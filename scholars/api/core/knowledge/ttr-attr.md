# ttr-attr


## run 1 · ttrA-api-web-20260712-100649 · 2026-07-12
Cohort A (synthetic, NOT clinically valid): 230 unique patients; 189 carry explicit ICD-10 E85.x; 41 more are amyloidosis-coded via legacy ICD-9 277.3/277.30/277.39 (+Z84.89 family history); combining E85.x with any amyloid name yields 211. Naive `code=='E85'` filter undercounts by ~18%. Among 189 E85.x: cardiac 155 (82%), neuropathic 98 (52%), mixed 83 (44%); cardiac-only 72, neuropathic-only 15, neither 19. Median age at latest dx 70.9 yr (IQR 60.7–78.1). Subtypes: E85.2 heredofamilial 79, E85.1 neuropathic heredofamilial 50, E85.82 wild-type ATTR 40, E85.0 non-neuropathic 4, E85.81 AL 7. Carpal tunnel G56.0 in 46 patients. Caveat: 39/189 also carry diabetes (E10/E11) — diabetic polyneuropathy may inflate the neuropathic tally.
