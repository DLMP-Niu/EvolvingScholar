# scholars/api/ — scholar_API (arm 2)

The **raw Anthropic Messages API** scholar: a "basic agent that grows" (ADR-0014).
The arm-2 counterpart to `scholars/sdk/` (the Claude Agent SDK "super-intern").
Both evolve independently over the same dataset; this arm's distinguishing trait
is a **minimal tool endowment** — a hand-written tool-use loop with just
`run_analysis`, `register_question`, and `save_report`, and **no literature-search
tool** (it draws on training knowledge and must grow its own retrieval later).

Reuses the SDK-free cores in `common/` unchanged. The only arm-specific code is
`engine.py` (the Messages API adapter) and `cycle.py` (the A→B→C runner).

## Run

```bash
conda activate evolving-scholar            # anthropic SDK + pandas live here
export ANTHROPIC_API_KEY=...               # required — the raw API needs its own key
python scholars/api/cycle.py               # new run (Loop A) → stops for PI review
python scholars/api/cycle.py <run_dir>     # advance after filling feedback_project.yaml
python scholars/api/cycle.py <run_dir> --skip   # no PI feedback: capture only, no Loop C
```

`SCHOLAR_API_MODEL` overrides the model (default `claude-opus-4-8`); set it to the
SDK arm's model when comparing arms directly. `SCHOLAR_API_MAX_TOKENS` overrides
the per-turn output cap (default 16000).

## What differs from the SDK arm

| | scholar_SDK | scholar_API |
|---|---|---|
| Loop A engine | `claude_agent_sdk` (built-in tools + MCP) | raw `messages.stream()` tool-use loop |
| Tool endowment | rich (WebSearch/WebFetch + custom) | minimal (3 custom tools, no web) |
| Thinking capture | SDK thinking blocks | adaptive thinking, `display: "summarized"` |
| --continue | server-side session resume | replays persisted `messages.jsonl` |
| Experience store | pre-seeded from prior runs | starts empty (run 0) |

Capture (four layers → `runs/<id>/`) and the review/evolution harness
(`harness/pi.py`, `harness/loop_c.py`) are identical to the SDK arm.
