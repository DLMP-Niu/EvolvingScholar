# emr-confounder-association-test

## EPA: Formally test a suspected confounder of a phenotype signal (EMR)

**When to use:** you observe a directional difference in phenotype rate between an exposed and unexposed subgroup (e.g. diabetic vs non-diabetic E85.x patients showing more neuropathy) and want to know if it is real before claiming it.

**Steps:**
1. Pre-specify the phenotype definition and the exposure code set BEFORE looking at the 2x2 (avoid definition-shopping).
2. Build a distinct-patient 2x2 table: exposure (present/absent) x phenotype (present/absent).
3. Run chi-square with Yates correction; also report uncorrected chi-square, Fisher exact p, and the odds ratio.
4. Check the chi-square assumption: all expected cell counts > 5. If violated, report Fisher as primary.
5. Report a decision at alpha=0.05 and state it plainly (significant / not significant / borderline).
6. **Sensitivity analysis:** re-run under the alternative reasonable definition (e.g. add ICD-9 marker equivalents). If the conclusion flips between primary and sensitivity definitions, say so explicitly — a result that is significant only under one coding scheme is a trend, not a finding.

**Output template:** "OR=x.x, primary p=0.xx (not significant); reaches nominal significance only when [definition change]. Conclusion: non-significant trend / robust association."

Carry this method forward across cohorts (PI directive: apply to cohort B).


## cycle 1 · ttrA-20260711-185206 · 2026-07-11
## Assumption checks (added after PI self_correction=3: 'consider stat but not necessarily assumptions')

Before reporting OR / chi-square / Fisher, state and check the assumptions, not just the p-values:
- Independence of observations: confirm the 2×2 counts distinct patients, not encounters/rows.
- Expected-cell adequacy: report min expected cell; if <5, lead with Fisher, not chi-square.
- Effect size vs significance: always report OR + absolute pp change alongside p, so a 'flip' across coding definitions is read as fragility, not discovery.
- Sensitivity-arm coupling: when the ICD-9 arm flips the verdict, treat the coding definition itself as the exposure being tested and say so explicitly.
