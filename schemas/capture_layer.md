# Capture Layer — spec

How the AI intern's questioning is recorded during a Loop A run. Captures **all four layers** (see [ADR-0008](../docs/adr/0008-capture-all-four-layers.md)) into one run folder, then reconciles them into a canonical trajectory. Written against `claude-agent-sdk` 0.2.115.

## Run-folder layout

```
experiments/runs/<run_id>/
  meta.yaml            # seed, model, artifact version, config snapshot, timestamps
  report.md            # the 7-question deliverable (human-comparable surface)
  questions.jsonl      # LAYER 4 — register_question tool calls  (PRIMARY analysis)
  actions.jsonl        # LAYER 3 — PostToolUse hook (every tool call)
  thinking.jsonl       # LAYER 2 — ThinkingBlock text from the stream
  transcript.jsonl     # LAYER 1 — full message stream (audit ground truth)
  question_trajectory.json   # RECONCILED output (built by harness/reconcile.py)
```

Layers 1–3 are **passive** (no behavioral effect) — always on. Layer 4 is **active** (mild observer effect) — captured, but treated as a variable (see Observer-effect protocol below).

## Layer 4 — `register_question` tool

An in-process SDK MCP tool the intern calls whenever it forms a research question. Populates `questions.jsonl` in the [question_registry](question_registry.md) shape. Tool name as seen by the agent: `mcp__scholar__register_question`.

Input schema (fields the agent supplies):

| field | type | notes |
|---|---|---|
| `text` | str | the question |
| `cognitive_level` | int | 1–9 ladder (agent self-tags; **human-audited** later) |
| `medical_purpose` | str | `research-mechanistic` \| `clinical-management` \| `counseling-pathway` |
| `origin` | str | `seeded` \| `self-generated` \| `pi-suggested` \| `spawned` |
| `parent_q_id` | str | "" if none |
| `edge_type` | str | `refines` \| `spawns` \| `blocks` \| "" |
| `evidence_source` | str | `literature` \| `emr` \| `both` \| "" |

The tool writer adds: `q_id` (assigned), `tool_use_id`, `cycle`, `run_id`, `ts`. `status`/`result_summary`/`quality` stay null at registration (filled at review).

## Layer 3 — PostToolUse hook → `actions.jsonl`

A `PostToolUse` hook (matcher `None` = all tools) appends one record per tool call:
`{ts, tool_use_id, tool_name, tool_input, agent_id, session_id}`. This is the deterministic action log — questions-as-actions (searches, EMR queries). Note the `register_question` calls also pass through here, giving a cross-check against `questions.jsonl`.

## Layer 2 — `thinking.jsonl`

From the `query()` stream: for each `AssistantMessage`, extract `ThinkingBlock` content → `{ts, message_id, text}`. Requires thinking enabled (`thinking=ThinkingConfigEnabled(...)` or `max_thinking_tokens`). This is where nascent, not-yet-acted questions live.

## Layer 1 — `transcript.jsonl`

Every message from the `query()` async iterator, serialized in order. Ground-truth backup. (The SDK also keeps its own transcript at the `transcript_path` given in hook inputs — `transcript.jsonl` is our self-contained copy.)

## Reconciliation → `question_trajectory.json`

`harness/reconcile.py` merges the layers into canonical question nodes (built by `harness/evaluator.py` into the trajectory tracking structure):

1. **Seed nodes** from `questions.jsonl` (layer 4) — one node per `q_id`, with provenance edges from `parent_q_id`/`edge_type`.
2. **Attach actions** (layer 3): order everything by `ts`; actions between question *T* and the next registered question attribute to *T* (`node.actions = [...]`).
3. **Detect discrepancies** — the cross-layer signal:
   - *considered-but-abandoned*: a question-shaped statement in `thinking.jsonl` (layer 2) with no matching `register_question` → candidate abandoned node.
   - *inflation*: a `register_question` with no downstream actions in its window → possible observer-effect performance.
   - *blind-spot*: an action with no registered question in its window → implicit questioning.
4. **Emit** nodes + edges + a `discrepancies` block. Discrepancy counts are themselves metrics.

## Observer-effect protocol

Because layer 4 intervenes: run a subset of repetitions with `register_question` **disabled** (allowed_tools omits it), extract questions post-hoc from layers 1–2 on those runs, and compare the question distribution to the tool-enabled runs. Large divergence ⇒ the tool is shaping behavior; report it. This is why repetition matters (see design-notes): it powers both the signal/noise separation and this ablation.
