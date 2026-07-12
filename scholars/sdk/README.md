# runtime/ — orchestration entrypoint(s)

Drives Loop A (the intern's research activity) and sequences the A → B → C cycle. Single runtime for the feasibility pilot; a second build arm (SDK vs. raw API) is deferred (ADR-0006).

## `cycle.py` — the cycle runner

`python -m runtime.cycle` advances one A → B → C cycle by **exactly one step**, from wherever the run is. It's a human-in-the-loop state machine over the run directory — it never automates the PI; it takes the next action and stops for the human to fill `feedback_project.yaml`.

```
python -m runtime.cycle            # start a NEW cycle: Loop A (new run) → review packet
python -m runtime.cycle <run_dir>  # advance THAT run one step:
    unfilled feedback  → (re)build the review packet, stop for the PI
    status: needs_more → Loop A --continue with the PI's tasks (ADR-0013), rebuild packet, stop
    status: complete   → Loop C (system update), print the scholar_core/ diff
```

State is derived from files (no separate state store); re-running the same command after filling the form advances the loop. `loop_a.py`, `pi.py`, and `loop_c.py` keep their own CLIs for running a single loop in isolation.

## Config isolation, enforced at launch (ADR-0007)

Every `run_project` launch sets `setting_sources=["project"]`, an explicit tool allow/deny list, and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, and calls `preflight.assert_isolated_and_ready(...)`, which **fails loudly** (`SystemExit`) if:
- any ancestor `CLAUDE.md` exists above the repo root (would bleed into context);
- `claude_agent_sdk` isn't importable, or the cohort data isn't unpacked (`data/…`).

`~/.claude` merely existing is logged as a note, not a failure (it's excluded by the config above). The effective config is written to `run_dir/effective_config.yaml` at every run start for the experiment record.
