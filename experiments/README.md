# experiments/ — the scientific data

- `runs/` — one folder per run: config + logs. Name runs so the learning/static and pair sequence are legible (e.g. `learning__ttr__cycle1/`).
- `results/` — the tracking structures and plots: question trajectories, revision maps, transfer matrices, concept-model diffs, ladder-distribution and knowledge-vs-reasoning readouts.

This is experiment output, kept separate from the intern's own state (`scholar_core/`) and the build record (`docs/`) — ADR-0004.
