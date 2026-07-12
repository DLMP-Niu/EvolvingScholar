# cohort-assembly-cross-coding

# Cohort assembly across coding systems

**When:** Before counting any disease cohort from EMR `dx` data.

**Method (reusable):**
1. Normalize diagnosis codes and names: lowercase, strip whitespace, split compound codes (e.g. `"E85.4, I43"` → two codes).
2. Do NOT filter on a single ICD-10 prefix. Reconcile the ICD-9↔ICD-10 crosswalk (for amyloidosis: ICD-9 `277.3/277.30/277.39` ↔ ICD-10 `E85.x`) plus any diagnosis-name text matching the entity (e.g. `%amyloid%`).
3. Report the count under each definition (strict prefix vs. reconciled) and state the undercount a naive filter would produce.

**Validated instance:** In cohort A a naive `code == 'E85'` filter returned 189 patients; reconciling ICD-9 277.3x + amyloid name text yielded 211 (~18% undercount).
