"""scholars/sdk/engine.py — the Claude Agent SDK adapter for scholar_SDK.

Loop A research engine + the SDK glue around the shared, runtime-neutral cores in
`common/`. A NEW run works a project's seed question over a cohort; a `--continue`
run RESUMES the same SDK session with the PI's newly-assigned tasks (partial
re-run — prior context is intact; ADR-0013). The scholar's evolved skills load
from its `core/` at the start of every run (ADR-0001 retrieval; load-all suffices
for the pilot). Four-layer capture throughout.

The pure primitives (capture writers, EMR analysis, prompts, scholar_io,
preflight, project registry) live in `common/` and are SDK-free, so the raw-API
arm (`scholars/api/`) reuses them without importing this module.
"""
from __future__ import annotations

import asyncio
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from claude_agent_sdk import (  # type: ignore
    AssistantMessage,
    ClaudeAgentOptions,
    HookMatcher,
    ResultMessage,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "common"))
sys.path.insert(0, str(REPO / "harness"))
from capture import REGISTER_QUESTION_SCHEMA, RunContext, _clean  # noqa: E402
from emr_tools import run_cohort_analysis  # noqa: E402
from preflight import assert_isolated_and_ready, log_effective_config  # noqa: E402
from projects import DEFAULT_PROJECT, resolve_cohort  # noqa: E402
from prompts import resume_prompt, seed_question, system_prompt  # noqa: E402
from scholar_io import load_scholar_core, next_run_no  # noqa: E402

SCHOLAR = "sdk"
CORE = REPO / "scholars" / "sdk" / "core"
RUNS_DIR = REPO / "scholars" / "sdk" / "runs"
COHORT_DIR = REPO / "data" / "synthetic_ttr_REACTSP_tsv_datasets"

# Restrained (novice) endowment: deny built-ins so the Scholar has only its custom
# tools + web (ADR-0010 knob). WebSearch/WebFetch are ALLOWED — literature is a core
# Loop A capability; how-to-search stays a mentored EPA (ADR-0011).
BUILTIN_TOOLS = [
    "Bash", "Read", "Write", "Edit", "NotebookEdit", "Glob", "Grep",
    "Task", "ToolSearch", "TodoWrite", "BashOutput", "KillShell", "Skill", "ExitPlanMode",
]
ALLOWED_TOOLS = [
    "mcp__scholar__register_question",
    "mcp__scholar_tools__run_analysis",
    "mcp__scholar_tools__save_report",
    "WebSearch",
    "WebFetch",
]


# ---- SDK capture glue (pure primitives live in common/capture.py) --------------

def build_capture(ctx: RunContext) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (mcp_servers, hooks) to merge into ClaudeAgentOptions, wired to `ctx`.
    The register_question @tool (layer 4) and PostToolUse hook (layer 3) are SDK-
    specific; the artifact writers they call are the shared `common/capture.py`."""

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
                "run": ctx.run_no,
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
                            "text": getattr(block, "thinking", None) or getattr(block, "text", ""),
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


# ---- SDK tool adapter (pure core lives in common/emr_tools.py) -----------------

def build_loop_a_tools(cohort_dir: Path, cohort: str, run_dir: Path):
    """SDK adapter: an in-process MCP server exposing run_analysis + save_report."""

    @tool(
        "run_analysis",
        "Run Python (pandas) over the cohort EMR and get printed output back. "
        "Preloaded DataFrames: dx(ID, 'dx ICD code', 'dx ICD name', 'Dx date'); "
        "appt(ID, 'appointment description', 'appointment date'); "
        "glucose(ID, 'lab glucose testing result', 'value', 'unit', 'date'); "
        "dob(ID, 'date_of_birth'). `pd` is available. print() AGGREGATES only — never raw patient rows.",
        {"code": str},
    )
    async def run_analysis(args: dict[str, Any]) -> dict[str, Any]:
        out = run_cohort_analysis(Path(cohort_dir), cohort, args.get("code", ""))
        return {"content": [{"type": "text", "text": out}]}

    @tool(
        "save_report",
        "Save your final run report as Markdown, structured by the 7 questions: "
        "1 What am I studying? 2 Where do I find information? 3 What EMR data do I have? "
        "4 Does EMR confirm literature? 5 Does EMR suggest anything new? 6 What did I build? "
        "7 What did this teach me for the next project?",
        {"markdown": str},
    )
    async def save_report(args: dict[str, Any]) -> dict[str, Any]:
        (Path(run_dir) / "report.md").write_text(args.get("markdown", ""), encoding="utf-8")
        return {"content": [{"type": "text", "text": "report saved"}]}

    return create_sdk_mcp_server("scholar_tools", "0.1.0", tools=[run_analysis, save_report])


def _thinking_config():
    """Enable extended thinking so layer-2 (thinking.jsonl) capture actually fires.
    ThinkingConfigEnabled is a TypedDict requiring BOTH 'type' and 'budget_tokens'
    (verified against SDK 0.2.115). Probe defensively: a mismatch degrades to no
    layer-2 capture rather than breaking the run."""
    try:
        from claude_agent_sdk import ThinkingConfigEnabled  # type: ignore
    except ImportError:
        return None
    try:
        return ThinkingConfigEnabled(type="enabled", budget_tokens=8000)
    except Exception:
        return None


# ---- Loop A run ----------------------------------------------------------------

async def run_project(
    prompt: str,
    resume_session_id: str | None = None,
    run_dir: Path | None = None,
    project: str = DEFAULT_PROJECT,
    cohort: str | None = None,
    run_no: int | None = None,
) -> tuple[str | None, Path]:
    """Run (new) or continue (resume) one experiment run. Returns (session_id, run_dir).

    A NEW run (run_dir=None) is numbered as this scholar's next feedback-gated run
    (`next_run_no`) unless `run_no` is given; a --continue run reuses the number
    from meta.yaml (passed by the caller)."""
    cohort = resolve_cohort(project, cohort)
    if run_dir is None:
        run_id = f"ttr{cohort}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        run_dir = RUNS_DIR / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        if run_no is None:
            run_no = next_run_no(CORE)
    else:
        run_dir = Path(run_dir)
        run_id = run_dir.name
        if run_no is None:
            run_no = 1
    ctx = RunContext(run_id=run_id, run_no=run_no, run_dir=run_dir)  # restores q-counter on continue

    for w in assert_isolated_and_ready(REPO, COHORT_DIR):  # fail loud if not isolated/ready (ADR-0007)
        print("[preflight] note:", w)

    cap_servers, hooks = build_capture(ctx)
    mcp_servers = {**cap_servers, "scholar_tools": build_loop_a_tools(COHORT_DIR, cohort, run_dir)}

    kwargs = dict(
        cwd=str(REPO),
        system_prompt=system_prompt(project, cohort) + load_scholar_core(CORE),
        mcp_servers=mcp_servers,
        allowed_tools=ALLOWED_TOOLS,
        disallowed_tools=BUILTIN_TOOLS,
        hooks=hooks,
        setting_sources=["project"],
        permission_mode="bypassPermissions",
        max_turns=30,
        env={"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"},
    )
    if resume_session_id:
        kwargs["resume"] = resume_session_id

    tc = _thinking_config()
    try:
        options = ClaudeAgentOptions(**({**kwargs, "thinking": tc} if tc is not None else kwargs))
    except TypeError:  # installed SDK doesn't accept `thinking`; layer-2 capture stays empty
        options = ClaudeAgentOptions(**kwargs)

    log_effective_config(run_dir, {  # experiment record (ADR-0004/0007)
        "run_id": run_id, "scholar": SCHOLAR, "project": project, "cohort": cohort, "run": run_no,
        "repo": str(REPO), "cohort_dir": str(COHORT_DIR),
        "setting_sources": ["project"], "permission_mode": "bypassPermissions",
        "allowed_tools": ALLOWED_TOOLS, "disallowed_tools": BUILTIN_TOOLS,
        "disable_auto_memory": True, "thinking_capture": tc is not None,
        "resumed": bool(resume_session_id),
    })

    meta_path = run_dir / "meta.yaml"
    meta = yaml.safe_load(meta_path.read_text()) if meta_path.exists() else {
        "run_id": run_id, "scholar": SCHOLAR, "project": project, "cohort": cohort, "run": run_no,
        "started": datetime.now().isoformat(),
        "seed_question": seed_question(project, cohort), "turns": [],
    }
    meta.setdefault("turns", []).append(
        {"resumed": bool(resume_session_id), "prompt": prompt[:200], "at": datetime.now().isoformat()}
    )
    meta_path.write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")

    print(f"[engine] {'continue' if resume_session_id else 'new'} run={run_id} "
          f"project={project} cohort={cohort} run_no={run_no}")
    result = None
    async for msg in capture_stream(query(prompt=prompt, options=options), ctx):
        if isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, TextBlock) and b.text.strip():
                    print("SCHOLAR:", b.text.strip()[:200])
        if isinstance(msg, ResultMessage):
            result = msg

    session_id = getattr(result, "session_id", None)
    if session_id:
        meta["session_id"] = session_id
        meta_path.write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")
    if result is not None:
        print(f"\n[engine] done — is_error={result.is_error} turns={result.num_turns} "
              f"cost=${result.total_cost_usd} session={session_id}")
    print("artifacts in:", run_dir)
    return session_id, run_dir


def _continue(run_dir: str) -> None:
    from pi import pending_tasks  # noqa: E402

    rd = Path(run_dir)
    meta = yaml.safe_load((rd / "meta.yaml").read_text())
    sid = meta.get("session_id")
    if not sid:
        raise SystemExit(f"no session_id in {rd}/meta.yaml — cannot resume")
    tasks = pending_tasks(rd)
    if not tasks:
        raise SystemExit("no pending tasks (feedback status != 'needs_more' or new_tasks empty)")
    asyncio.run(run_project(
        resume_prompt(tasks), resume_session_id=sid, run_dir=rd,
        project=meta.get("project", DEFAULT_PROJECT), cohort=meta.get("cohort"),
        run_no=int(meta.get("run", meta.get("cycle", 1))),
    ))


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="scholar_SDK Loop A — run or continue an experiment run.")
    ap.add_argument("--continue", dest="cont", metavar="RUN_DIR",
                    help="resume this run with the PI's pending tasks (ADR-0013)")
    ap.add_argument("--project", default=DEFAULT_PROJECT, help="research project id (see common/projects.py)")
    ap.add_argument("--cohort", default=None, help="cohort within the project (default: project default)")
    args = ap.parse_args()
    if args.cont:
        _continue(args.cont)
    else:
        cohort = resolve_cohort(args.project, args.cohort)
        asyncio.run(run_project(seed_question(args.project, cohort),
                                project=args.project, cohort=cohort))
