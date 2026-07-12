# phenotype-classification-by-code-family

# Phenotype classification by code family

**When:** Assigning patients to clinical phenotypes from diagnosis codes.

**Method (reusable):**
1. Pre-register the code families BEFORE counting (e.g. cardiac = I43/I50/I51/R94.31/I42; neuropathic = G62/G60/G99.0/G56.0).
2. Pre-register a confounder list for each phenotype (e.g. diabetes E10/E11 can inflate the neuropathic tally via diabetic polyneuropathy). Report how many cohort members carry each confounder.
3. Emit cardiac-only / neuropathic-only / mixed / neither counts, not just per-phenotype totals, so overlap is visible.
4. Report every count with its denominator and the classifier definition used.
