# scholars/sdk/ — scholar_SDK (Claude Agent SDK arm)

`scholar_SDK`'s engine + experience store + runs (ADR-0014). The SDK arm is the
"super-intern": rich built-in tools available, restrained to a novice endowment by
an explicit allow/deny list (ADR-0010). The pure, runtime-neutral cores it builds
on live in `../../common/` (SDK-free, shared with the raw-API arm); the shared
review/evolution mechanism lives in `../../harness/`.

```
engine.py   SDK adapter: Loop A run_project + capture glue + tool wrappers  (imports common/)
cycle.py    the run runner — advances one experiment run's A→B→C loop one step
core/       this scholar's experience store (evolution record; git diff = its growth)
runs/       this scholar's experiment runs (four-layer capture; gitignored)
```

## `cycle.py` — the run runner

Advances one experiment run's A → B → C loop by **exactly one step**, from wherever
the run is. A human-in-the-loop state machine over the run directory — it never
automates the PI; it takes the next action and stops for the human to fill
`feedback_project.yaml`.

```
python scholars/sdk/cycle.py                    # start a NEW run: Loop A → review packet
python scholars/sdk/cycle.py <run_dir>          # advance THAT run one step:
    unfilled feedback  → (re)build the review packet, stop for the PI
    status: needs_more → Loop A --continue with the PI's tasks (ADR-0013), rebuild packet, stop
    status: complete   → Loop C (system update), print the core/ diff
python scholars/sdk/cycle.py <run_dir> --skip   # no PI feedback: capture only, no Loop C (ADR-0014)
python scholars/sdk/cycle.py --project TTR-ATTR --cohort B   # new run on a chosen cohort
```

State is derived from files (no separate state store); re-running the same command
after filling the form advances the loop. `engine.py` also has its own CLI
(`python scholars/sdk/engine.py [--continue <run_dir>] [--project …] [--cohort …]`)
for a single Loop A pass. The project/cohort registry is `common/projects.py`.
Evolution accretes **per experiment run, gated by PI feedback**; a run's index
(`run` in `meta.yaml`) auto-increments from this scholar's revision history.

## Config isolation, enforced at launch (ADR-0007)

Every `run_project` launch sets `setting_sources=["project"]`, an explicit tool
allow/deny list, and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, and calls
`common/preflight.assert_isolated_and_ready(...)`, which **fails loudly**
(`SystemExit`) if:
- any ancestor `CLAUDE.md` exists above the repo root (would bleed into context);
- `claude_agent_sdk` isn't importable, or the cohort data isn't unpacked (`data/…`).

`~/.claude` merely existing is logged as a note, not a failure (it's excluded by
the config above). The effective config is written to `run_dir/effective_config.yaml`
at every run start for the experiment record.
