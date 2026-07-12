"""Capture layer for a Loop A run — records all four layers of the intern's
questioning into a run folder. See schemas/capture_layer.md.

Written against claude-agent-sdk 0.2.115. Layers 1-3 are passive (no behavioral
effect); layer 4 (register_question) is active and treated as a variable.

Status: skeleton — syntactically checked, NOT yet integration-tested against a
live agent run. Field names marked (verify) need confirmation on first real run.
"""
from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from claude_agent_sdk import (  # type: ignore
    AssistantMessage,
    HookMatcher,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    tool,
)


class JsonlWriter:
    """Thread-safe append-only JSONL writer."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def append(self, record: dict[str, Any]) -> None:
        line = json.dumps(record, default=str, ensure_ascii=False)
        with self._lock, self.path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")


@dataclass
class RunContext:
    """One Loop A run's capture destination."""

    run_id: str
    cycle: int
    run_dir: Path
    seed: int | None = None

    def __post_init__(self) -> None:
        self.run_dir = Path(self.run_dir)
        self.questions = JsonlWriter(self.run_dir / "questions.jsonl")   # layer 4
        self.actions = JsonlWriter(self.run_dir / "actions.jsonl")       # layer 3
        self.thinking = JsonlWriter(self.run_dir / "thinking.jsonl")     # layer 2
        self.transcript = JsonlWriter(self.run_dir / "transcript.jsonl") # layer 1
        # Restore the question counter so a --continue run keeps incrementing ids.
        qf = self.run_dir / "questions.jsonl"
        self._qn = sum(1 for _ in qf.open(encoding="utf-8")) if qf.exists() else 0

    def next_qid(self) -> str:
        self._qn += 1
        return f"{self.run_id}-q{self._qn:04d}"


# Simple dict schema form accepted by claude_agent_sdk.tool (name -> type).
REGISTER_QUESTION_SCHEMA: dict[str, Any] = {
    "text": str,
    "cognitive_level": int,      # 1-9 ladder; agent self-tags, human-audited later
    "medical_purpose": str,      # research-mechanistic | clinical-management | counseling-pathway
    "origin": str,               # seeded | self-generated | pi-suggested | spawned
    "parent_q_id": str,          # "" if none
    "edge_type": str,            # refines | spawns | blocks | ""
    "evidence_source": str,      # literature | emr | both | ""
}

_NULLISH = {"", "none", "null", "n/a", "na"}


def _clean(v: Any) -> Any:
    """Normalize model-supplied sentinel strings ('none', '', ...) to None."""
    if isinstance(v, str) and v.strip().lower() in _NULLISH:
        return None
    return v


def build_capture(ctx: RunContext) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (mcp_servers, hooks) to merge into ClaudeAgentOptions, wired to `ctx`.

    Usage:
        mcp_servers, hooks = build_capture(ctx)
        options = ClaudeAgentOptions(
            mcp_servers=mcp_servers,
            hooks=hooks,
            allowed_tools=[..., "mcp__scholar__register_question"],
            setting_sources=["project"],           # isolation (ADR-0007)
            thinking=ThinkingConfigEnabled(...),   # needed for layer 2
        )
    """

    @tool(
        "register_question",
        "Log a research question you are actively pursuing, the moment you form it. "
        "Call for every genuine research question you decide to pursue — not rhetorical asides.",
        REGISTER_QUESTION_SCHEMA,
    )
    async def register_question(args: dict[str, Any]) -> dict[str, Any]:
        qid = ctx.next_qid()
        ctx.questions.append(
            {
                "q_id": qid,
                "run_id": ctx.run_id,
                "cycle": ctx.cycle,
                "ts": time.time(),
                "asker": "ai",
                "text": args.get("text", ""),
                "cognitive_level": args.get("cognitive_level"),
                "medical_purpose": args.get("medical_purpose"),
                "origin": args.get("origin"),
                "parent_q_id": _clean(args.get("parent_q_id")),
                "edge_type": _clean(args.get("edge_type")),
                "evidence_source": _clean(args.get("evidence_source")),
                "status": "open",
                "result_summary": None,
                "quality": None,
            }
        )
        return {"content": [{"type": "text", "text": f"registered {qid}"}]}

    server = create_sdk_mcp_server("scholar", "0.1.0", tools=[register_question])

    async def on_post_tool_use(input_data: Any, tool_use_id: str | None, context: Any) -> dict[str, Any]:
        # input_data is a PostToolUseHookInput dict.
        ctx.actions.append(
            {
                "ts": time.time(),
                "tool_use_id": input_data.get("tool_use_id"),
                "tool_name": input_data.get("tool_name"),
                "tool_input": input_data.get("tool_input"),
                "agent_id": input_data.get("agent_id"),
                "session_id": input_data.get("session_id"),
            }
        )
        return {}  # no-op: observe only, never block

    hooks = {"PostToolUse": [HookMatcher(matcher=None, hooks=[on_post_tool_use])]}
    mcp_servers = {"scholar": server}
    return mcp_servers, hooks


async def capture_stream(message_iter: Any, ctx: RunContext) -> Any:
    """Wrap the query() async iterator: write transcript + extract thinking,
    re-yielding each message so the caller can still act on it."""
    async for msg in message_iter:
        ctx.transcript.append(_serialize(msg))
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, ThinkingBlock):
                    ctx.thinking.append(
                        {
                            "ts": time.time(),
                            "message_id": getattr(msg, "message_id", None),
                            "text": getattr(block, "thinking", None) or getattr(block, "text", ""),  # (verify) field name
                        }
                    )
        yield msg


def _serialize(msg: Any) -> dict[str, Any]:
    t = type(msg).__name__
    if isinstance(msg, AssistantMessage):
        return {"type": t, "model": msg.model, "content": [_block(b) for b in msg.content]}
    return {"type": t, "repr": repr(msg)}


def _block(b: Any) -> dict[str, Any]:
    t = type(b).__name__
    if isinstance(b, TextBlock):
        return {"type": t, "text": b.text}
    if isinstance(b, ThinkingBlock):
        return {"type": t, "text": getattr(b, "thinking", None) or getattr(b, "text", "")}
    if isinstance(b, ToolUseBlock):
        return {"type": t, "id": b.id, "name": b.name, "input": b.input}
    return {"type": t, "repr": repr(b)}
