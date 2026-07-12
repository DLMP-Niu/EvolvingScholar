# common/ — shared, runtime-neutral primitives + initial setup

SDK-free cores shared by **both** scholars (ADR-0014). Nothing here imports
`claude_agent_sdk`, so the raw-API arm (`scholars/api/`) reuses these unchanged;
each arm's runtime glue wraps them in its own `engine.py`.

```
capture.py      RunContext, JsonlWriter, register_question schema, _clean  (artifact writers)
emr_tools.py    run_cohort_analysis + cohort tables                        (the analysis core)
scholar_io.py   load_scholar_core(core), next_run_no(core)                 (experience store I/O)
projects.py     PROJECTS registry + resolve_cohort                         (gene/disease containers)
prompts.py      seed_question(), system_prompt(), resume_prompt()          (cycle-0 prompt material)
preflight.py    assert_isolated_and_ready, log_effective_config           (isolation guard, ADR-0007)
persona.md      cycle-0 identity — both scholars start here
```

The SDK glue (the `@tool` wrappers, the PostToolUse hook, transcript/thinking
serialization) is **not** here — it lives in `scholars/sdk/engine.py`.
