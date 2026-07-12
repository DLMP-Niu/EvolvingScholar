# emr-compound-code-decomposition

# EMR compound-code decomposition

**When:** rows carry multiple ICD codes in one field (e.g. `E85.4, I43`). Do NOT drop them — PI: 'Compound-code rows should not be ignored. Code to breakdown.'

**Method (EPA):**
1. Split each compound cell on delimiters (`,` `;` `/` `|`), trim, normalize each token to a canonical ICD code.
2. Explode to long form: one (patient_id, code, source_row) tuple per token, preserving provenance.
3. Tag each exploded code as membership (E85.x/277.3) vs evidence (cardiac/neuro) so the anti-circular rule still holds — but keep the codes as counted data, not discarded.
4. Report the breakdown: how many patients/phenotype signals were recovered from compound rows vs. lost under the old 'exclude same-row markers' rule. Quantify the delta both ways.

**Output:** a per-patient code-set dataframe plus a recovered-vs-excluded reconciliation table. Never silently exclude a populated row; a dropped row is a logged, counted decision.
