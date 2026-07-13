# docs/demo — presentation & workflow-run visuals

## Slide decks (self-contained HTML)
- `style-a-builders.html` — AI/builders deck (terminal / version-control world).
- `style-b-clinical.html` — clinical/medical deck (entrustment-ladder world).

Open in a browser (or publish as a Claude Artifact). Keyboard: ← → / space / dots.

## Workflow-run replay → GIF

`scripts/replay_run.py` renders a captured run as a paced terminal "simulation" of
the A→B→C loop — research narrative + tool calls, the report, the PI review +
entrustment, and the EPAs earned. **It reads only on-disk capture** (no live agent,
no API calls, no tokens), so it is deterministic and regenerable.

### Play live in a terminal
```bash
python scripts/replay_run.py scholars/api/runs/ttrA-api-web-20260712-100649
python scripts/replay_run.py scholars/sdk/runs/ttrA-20260711-185206
```

### Regenerate the cast + GIF
```bash
# 1) capture -> asciinema v2 cast (fast, no sleeping)
python scripts/replay_run.py <run_dir> --cast docs/demo/run-<name>.cast --speed 1.5

# 2) cast -> gif   (agg = asciinema's gif renderer)
agg --font-size 15 --theme dracula --idle-time-limit 1.2 \
    docs/demo/run-<name>.cast docs/demo/run-<name>.gif

# 3) shrink (optional)
gifsicle -O3 --lossy=100 --colors 128 docs/demo/run-<name>.gif -o docs/demo/run-<name>.gif
```

### Committed examples
| Arm | Cast (source) | GIF |
|---|---|---|
| Scholar 2 (API) | `run-scholar2-api.cast` | `run-scholar2-api.gif` |
| Scholar 1 (SDK) | `run-scholar1-sdk.cast` | `run-scholar1-sdk.gif` |

The `.cast` files are the text source of truth (diff-able, ~10 KB); the `.gif`s are
regenerated from them. To refresh after new runs, re-run the three steps above.

### Tooling
- **agg** (single static binary): `curl -fsSL -o ~/.local/bin/agg https://github.com/asciinema/agg/releases/latest/download/agg-x86_64-unknown-linux-gnu && chmod +x ~/.local/bin/agg`
- **gifsicle**: `conda install -c conda-forge gifsicle` (optional, for size).
- The replay script itself needs only Python + PyYAML (already in the `evolving-scholar` env).
