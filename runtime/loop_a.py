"""Build 1 — minimal Loop A on the SDK.

Runs the Scholar on one seeded TTR question over cohort A with a restrained
(novice) tool endowment — built-ins off, only run_analysis / register_question /
save_report — capturing all layers. No PI, no Loop C. Validates the whole
capture path end-to-end.
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime
from pathlib import Path

from claude_agent_sdk import (  # type: ignore
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from capture import RunContext, build_capture, capture_stream  # noqa: E402
from tools import build_loop_a_tools  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
COHORT_DIR = REPO / "data" / "synthetic_ttr_REACTSP_tsv_datasets"
COHORT = "A"

# Restrained (novice) endowment: explicitly deny built-ins so the Scholar has ONLY
# its custom tools (ADR-0010 endowment knob). allowed_tools alone did not block them.
BUILTIN_TOOLS = [
    "Bash", "Read", "Write", "Edit", "NotebookEdit", "Glob", "Grep",
    "WebSearch", "WebFetch", "Task", "ToolSearch", "TodoWrite", "BashOutput",
    "KillShell", "Skill", "ExitPlanMode",
]

SEED_QUESTION = (
    "Seed question: Using cohort A's EMR data, characterize the TTR / hereditary ATTR "
    "amyloidosis cohort — how many patients are there, what are the most frequent "
    "diagnoses, and is the expected cardiac vs. neuropathic phenotype present among "
    "amyloidosis (ICD E85.x) patients?"
)

SYSTEM_PROMPT = """You are the Scholar — an AI research intern in clinical molecular genetics, at the start of training.
You are working on ONE research project: TTR / hereditary ATTR amyloidosis, using a synthetic EMR cohort.

Your complete toolset:
- run_analysis(code): run pandas over the cohort; print aggregates only.
- register_question(...): call this the moment you form a research question you decide to pursue, BEFORE investigating it. Set cognitive_level (1-9), medical_purpose (research-mechanistic|clinical-management|counseling-pathway), origin (seeded|self-generated|pi-suggested|spawned), and parent_q_id/edge_type if it follows from an earlier question.
- save_report(markdown): at the very end, save your report structured by the 7 questions.

Work the seed question: register the questions you pursue, use run_analysis to investigate them, note any data-quality problems you find, then finish by calling save_report. Ground every claim in what the data actually shows. This is synthetic data — findings are not clinically valid; treat it as a workflow exercise."""


async def main() -> None:
    run_id = "ttrA-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = REPO / "experiments" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    ctx = RunContext(run_id=run_id, cycle=1, run_dir=run_dir)

    cap_servers, hooks = build_capture(ctx)
    tools_server = build_loop_a_tools(COHORT_DIR, COHORT, run_dir)
    mcp_servers = {**cap_servers, "scholar_tools": tools_server}

    allowed = [
        "mcp__scholar__register_question",
        "mcp__scholar_tools__run_analysis",
        "mcp__scholar_tools__save_report",
    ]

    options = ClaudeAgentOptions(
        cwd=str(REPO),
        system_prompt=SYSTEM_PROMPT,
        mcp_servers=mcp_servers,
        allowed_tools=allowed,
        disallowed_tools=BUILTIN_TOOLS,
        hooks=hooks,
        setting_sources=["project"],
        permission_mode="bypassPermissions",
        max_turns=30,
        env={"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"},
    )

    (run_dir / "meta.yaml").write_text(
        f"run_id: {run_id}\ncohort: {COHORT}\ncycle: 1\n"
        f"started: {datetime.now().isoformat()}\nseed_question: |\n  {SEED_QUESTION}\n",
        encoding="utf-8",
    )

    print(f"[loop_a] run_id={run_id}  cohort={COHORT}")
    result = None
    async for msg in capture_stream(query(prompt=SEED_QUESTION, options=options), ctx):
        if isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, TextBlock) and b.text.strip():
                    print("SCHOLAR:", b.text.strip()[:220])
        if isinstance(msg, ResultMessage):
            result = msg

    print("\n=== run complete ===")
    if result is not None:
        print("is_error:", result.is_error, " turns:", result.num_turns,
              " cost_usd:", result.total_cost_usd)
        print("result:", (result.result or "")[:300])
    print("artifacts in:", run_dir)


if __name__ == "__main__":
    asyncio.run(main())
