# experiments/ — scientific data (cross-scholar analysis outputs)

- Per-scholar **experiment runs** now live under `scholars/<id>/runs/` (one folder per run: config + four-layer capture). Moved out of here by the two-scholar restructure — see [ADR-0014](../docs/adr/0014-two-evolving-scholars.md).
- `results/` — tracking structures and plots derived across runs/scholars: question trajectories, revision maps, transfer matrices, concept-model diffs, ladder-distribution and knowledge-vs-reasoning readouts.

This is experiment output, kept separate from each scholar's own state (`scholars/<id>/core/`) and the build record (`docs/`) — ADR-0004.
