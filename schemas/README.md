# schemas/ — capture instruments (shared contract)

Three instruments used identically by the **intern runtime**, the **harness**, and **human data collection**, so human and AI output land in one comparable dataset:

- [`question_registry.md`](question_registry.md) — one record per question (the two-axis annotation + provenance + quality).
- [`review_rubric_project.md`](review_rubric_project.md) — **within-cycle** review (Loop B): scores the *research work*.
- [`review_rubric_development.md`](review_rubric_development.md) — the *development/entrustment* dimensions (scores the intern's growth + entrustment). **Realized as the `review.development` completion section of the project form** (combined final review), which feeds Loop C — not a separate file (ADR-0013).
- [`capture_layer.md`](capture_layer.md) — how the AI intern's live questioning is recorded (4 layers) and reconciled into the trajectory.

## ⚠️ Reconcile with existing TTR annotations

These fields are the **proposed default.** The owner has an existing TTR question set already categorized/annotated (e.g. "knowledge", "update", …). Before the master's/medical/resident data is collected this month, **merge those existing columns into `question_registry.md`** — the existing annotation is the source of truth for any field it already defines; add the axes below that it doesn't yet cover (especially `medical_purpose`).

## Design constraints (already decided)

- **Two axes** on every question: `cognitive_level` × `medical_purpose`.
- **Structured, not free-text** feedback (reward-hacking guard); scores anchored to **checkable facts** where possible; feedback **keyed to `q_id`s**.
- **Human-judged** scoring (auto Bloom-classification is unreliable). Same rubric applied to human subjects and AI.
- One dataset: the `asker` field distinguishes `college-intern | masters | medical | resident | ai`.
