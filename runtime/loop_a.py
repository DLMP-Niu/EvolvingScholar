"""Loop A — research activity. Runs (or continues) one research project.

A NEW run works a seed question over cohort A; a --continue run RESUMES the same
SDK session with the PI's newly-assigned tasks (partial re-run — prior context is
intact, so the Scholar does only what's needed; ADR-0013). The Scholar's evolved
skills/strategy are loaded from scholar_core/ at the start of every run (ADR-0001
retrieval; load-all is fine for the pilot's small library). Four-layer capture
throughout.
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from pathlib import Path

import yaml

from claude_agent_sdk import (  # type: ignore
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "runtime"))
sys.path.insert(0, str(REPO / "harness"))
from capture import RunContext, build_capture, capture_stream  # noqa: E402
from tools import build_loop_a_tools  # noqa: E402
from preflight import assert_isolated_and_ready, log_effective_config  # noqa: E402

COHORT_DIR = REPO / "data" / "synthetic_ttr_REACTSP_tsv_datasets"
CORE = REPO / "scholar_core"
COHORT = "A"

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

SEED_QUESTION = (
    "Seed question: Using cohort A's EMR data, characterize the TTR / hereditary ATTR "
    "amyloidosis cohort — how many patients are there, what are the most frequent "
    "diagnoses, and is the expected cardiac vs. neuropathic phenotype present among "
    "amyloidosis (ICD E85.x) patients?"
)

SYSTEM_PROMPT = """You are the Scholar — an AI research intern in clinical molecular genetics.
You are working on ONE research project: TTR / hereditary ATTR amyloidosis, using a synthetic EMR cohort.

Your complete toolset:
- run_analysis(code): run pandas over the cohort; print aggregates only.
- WebSearch / WebFetch: consult the medical literature and clinical guidelines.
- register_question(...): call this the moment you form a research question you decide to pursue, BEFORE investigating it. Set cognitive_level (1-9), medical_purpose (research-mechanistic|clinical-management|counseling-pathway), origin (seeded|self-generated|pi-suggested|spawned), and parent_q_id/edge_type if it follows from an earlier question.
- save_report(markdown): at the very end, save your report structured by the 7 questions.

Register the questions you pursue, use run_analysis to investigate them, note any data-quality problems you find, then finish by calling save_report. Ground every claim in what the data actually shows. This is synthetic data — findings are not clinically valid; treat it as a workflow exercise."""


def resume_prompt(tasks: list[str]) -> str:
    """The PI's within-cycle tasks framed as a partial-re-run instruction (ADR-0013).
    Shared by `_continue` and runtime/cycle.py so the wording is defined once."""
    return (
        "Your PI reviewed your work and assigned these additional tasks. Address ONLY what is "
        "needed, reusing your prior work — do not redo settled analyses. Register any new "
        "questions, run needed analyses, then update your report via save_report:\n"
        + "\n".join(f"- {t}" for t in tasks)
    )


def _thinking_config():
    """Enable extended thinking so layer-2 (thinking.jsonl) capture actually fires —
    without it, capture_stream's ThinkingBlock branch never runs (see capture.py).
    The exact symbol/params vary across claude-agent-sdk versions, so probe
    defensively: a mismatch degrades to no layer-2 capture rather than breaking the
    run. Confirm against the installed SDK (0.2.115) and pin this once verified."""
    try:
        from claude_agent_sdk import ThinkingConfigEnabled  # type: ignore
    except ImportError:
        return None
    try:
        # ThinkingConfigEnabled is a TypedDict requiring BOTH 'type' and 'budget_tokens'
        # (verified against SDK 0.2.115) — omitting 'type' yields a malformed config.
        return ThinkingConfigEnabled(type="enabled", budget_tokens=8000)
    except Exception:
        return None


def load_scholar_core(core: Path = CORE) -> str:
    """Load accumulated skills + strategy into context (ADR-0001: retrieved, not a
    growing prompt — load-all suffices for the pilot's small library; switch to
    relevance-retrieval once it grows). Returns '' at cycle 0 (nothing learned yet)."""
    parts: list[str] = []
    for sub in ("capabilities", "strategy"):
        for f in sorted((core / sub).glob("*.md")):
            parts.append(f"### {sub}/{f.name}\n{f.read_text(encoding='utf-8').strip()}")
    if not parts:
        return ""
    return ("\n\n# Your accumulated skills and research strategy from prior work — "
            "apply them by default.\n\n" + "\n\n".join(parts))


async def run_project(
    prompt: str,
    resume_session_id: str | None = None,
    run_dir: Path | None = None,
    cohort: str = COHORT,
    cycle: int = 1,
) -> tuple[str | None, Path]:
    """Run (new) or continue (resume) one research project. Returns (session_id, run_dir)."""
    if run_dir is None:
        run_id = f"ttr{cohort}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        run_dir = REPO / "experiments" / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
    else:
        run_dir = Path(run_dir)
        run_id = run_dir.name
    ctx = RunContext(run_id=run_id, cycle=cycle, run_dir=run_dir)  # restores q-counter on continue

    for w in assert_isolated_and_ready(REPO, COHORT_DIR):  # fail loud if not isolated/ready (ADR-0007)
        print("[preflight] note:", w)

    cap_servers, hooks = build_capture(ctx)
    mcp_servers = {**cap_servers, "scholar_tools": build_loop_a_tools(COHORT_DIR, cohort, run_dir)}

    kwargs = dict(
        cwd=str(REPO),
        system_prompt=SYSTEM_PROMPT + load_scholar_core(),
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
        "run_id": run_id, "cohort": cohort, "cycle": cycle,
        "repo": str(REPO), "cohort_dir": str(COHORT_DIR),
        "setting_sources": ["project"], "permission_mode": "bypassPermissions",
        "allowed_tools": ALLOWED_TOOLS, "disallowed_tools": BUILTIN_TOOLS,
        "disable_auto_memory": True, "thinking_capture": tc is not None,
        "resumed": bool(resume_session_id),
    })

    meta_path = run_dir / "meta.yaml"
    meta = yaml.safe_load(meta_path.read_text()) if meta_path.exists() else {
        "run_id": run_id, "cohort": cohort, "cycle": cycle,
        "started": datetime.now().isoformat(), "seed_question": SEED_QUESTION, "turns": [],
    }
    meta.setdefault("turns", []).append(
        {"resumed": bool(resume_session_id), "prompt": prompt[:200], "at": datetime.now().isoformat()}
    )
    meta_path.write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")

    print(f"[loop_a] {'continue' if resume_session_id else 'new'} run={run_id} cohort={cohort} cycle={cycle}")
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
        print(f"\n[loop_a] done — is_error={result.is_error} turns={result.num_turns} "
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
    asyncio.run(run_project(resume_prompt(tasks), resume_session_id=sid, run_dir=rd,
                            cohort=meta.get("cohort", COHORT), cycle=int(meta.get("cycle", 1))))


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Loop A — run or continue a research project.")
    ap.add_argument("--continue", dest="cont", metavar="RUN_DIR",
                    help="resume this run with the PI's pending tasks (ADR-0013)")
    args = ap.parse_args()
    if args.cont:
        _continue(args.cont)
    else:
        asyncio.run(run_project(SEED_QUESTION))
