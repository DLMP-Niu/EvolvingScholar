"""Loop C — system update (the evolution mechanism). Build 3.

Consumes a completed cycle (run + the PI's feedback) and makes ONE model call to
distill them into proposed artifact updates (judgment — Rule 5), then writes them
DETERMINISTICALLY to scholar_core/ as versioned diffs: skills/EPAs, strategy,
knowledge, an error-ledger, and a revision-map entry.

Growth goes to versioned artifacts, retrieved by relevance — never a growing
prompt (ADR-0001). The git diff of scholar_core/ IS the evolution record.
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from claude_agent_sdk import (  # type: ignore
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    query,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pi import load_feedback, load_final_feedback  # noqa: E402
from reconcile import reconcile  # noqa: E402

REPO = Path(__file__).resolve().parent.parent

# No tools needed — this is a single structured-completion call.
BUILTIN_TOOLS = [
    "Bash", "Read", "Write", "Edit", "NotebookEdit", "Glob", "Grep",
    "WebSearch", "WebFetch", "Task", "ToolSearch", "TodoWrite", "BashOutput",
    "KillShell", "Skill", "ExitPlanMode",
]

PROPOSAL_SCHEMA = """{
  "revision_summary": "one sentence: what changed and why",
  "capability_updates": [{"name": "kebab-skill-name", "action": "create|append", "content": "markdown — a reusable method/EPA the Scholar demonstrated or was told to adopt"}],
  "strategy_updates":   [{"name": "research-taste", "action": "append", "content": "a principle of good question/method design learned this cycle"}],
  "knowledge_updates":  [{"name": "ttr-attr", "action": "append", "content": "a validated fact or data caveat"}],
  "concept_model_updates": [{"name": "ttr-attr-model", "action": "append", "content": "how the disease concept-model changed this cycle (entities/links/corrections)"}],
  "goal_updates":          [{"name": "research-goals", "action": "append", "content": "how the research goal/direction advanced (goal autonomy)"}],
  "ledger_entries":     [{"error_type": "...", "detected_by": "PI|self|data", "root_cause": "...", "correction": "...", "artifact_change": "which skill/strategy this maps to"}],
  "next_questions":     ["a seed question for the next cycle"]
}"""

LOOP_C_SYSTEM = (
    "You are the Loop C updater for an AI research intern (the Scholar). You do NOT do research. "
    "You read one completed research cycle plus the PI's feedback, and distill them into concrete, "
    "reusable updates to the Scholar's external artifacts, so it starts the next cycle better. "
    "Prefer small, specific, reusable items (a method the Scholar can re-run; a principle; a data caveat). "
    "Turn each PI critique into a ledger entry with a correction. "
    "The feedback includes a 'development' section (growth dimensions + an entrustment level) — "
    "use it to update the Scholar's concept-model, strategy/taste, and goals, not only its skills. "
    "Respond with ONLY a JSON object matching this schema, no prose:\n" + PROPOSAL_SCHEMA
)


def _extract_json(text: str) -> dict[str, Any]:
    m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    raw = m.group(1) if m else None
    if raw is None:
        i, j = text.find("{"), text.rfind("}")
        raw = text[i : j + 1] if (i != -1 and j != -1) else None
    if raw is None:
        raise ValueError("no JSON object found in Loop C model response")
    return json.loads(raw)


def _build_prompt(run_dir: Path, core: Path, feedback: dict[str, Any]) -> str:
    report = (run_dir / "report.md").read_text()[:6000] if (run_dir / "report.md").exists() else "(none)"
    traj = reconcile(run_dir)
    q_lines = [f"- {n['q_id']} L{n.get('cognitive_level')} {n.get('medical_purpose')} "
               f"{n.get('origin')}: {n.get('text', '')[:120]}" for n in traj["nodes"]]
    existing = sorted(p.stem for p in (core / "capabilities").glob("*.md"))
    return (
        f"## Current Scholar capabilities (skill files that already exist)\n"
        f"{existing or '(none yet — this is early training)'}\n\n"
        f"## This cycle's registered questions\n" + "\n".join(q_lines) + "\n\n"
        f"## This cycle's report\n{report}\n\n"
        f"## PI feedback (rubric scores + directives)\n"
        f"{yaml.safe_dump(feedback['review'], sort_keys=False)}\n\n"
        f"Now emit the JSON proposal."
    )


async def _propose(prompt: str) -> dict[str, Any]:
    options = ClaudeAgentOptions(
        cwd=str(REPO),
        system_prompt=LOOP_C_SYSTEM,
        allowed_tools=[],
        disallowed_tools=BUILTIN_TOOLS,
        setting_sources=["project"],
        permission_mode="bypassPermissions",
        max_turns=6,  # headroom for one JSON completion; no tools, so no runaway (max_turns=1 was too tight)
        env={"CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"},
    )
    text: list[str] = []
    async for msg in query(prompt=prompt, options=options):
        if isinstance(msg, AssistantMessage):
            for b in msg.content:
                if isinstance(b, TextBlock):
                    text.append(b.text)
    return _extract_json("".join(text))


def _append_section(path: Path, cycle: int, run_id: str, content: str) -> None:
    stamp = f"\n\n## cycle {cycle} · {run_id} · {datetime.now().date()}\n{content.strip()}\n"
    if path.exists():
        path.write_text(path.read_text() + stamp, encoding="utf-8")
    else:
        path.write_text(f"# {path.stem}\n{stamp}", encoding="utf-8")


def apply_updates(proposal: dict[str, Any], core: Path, cycle: int, run_id: str,
                  entrustment: dict[str, Any] | None = None) -> list[str]:
    changed: list[str] = []

    def write(kind: str, items: list[dict[str, Any]]) -> None:
        for it in items or []:
            name = it.get("name", "misc").strip() or "misc"
            path = core / kind / f"{name}.md"
            if it.get("action") == "create" and not path.exists():
                path.write_text(f"# {name}\n\n{it.get('content','').strip()}\n", encoding="utf-8")
            else:
                _append_section(path, cycle, run_id, it.get("content", ""))
            changed.append(str(path.relative_to(core.parent)))

    write("capabilities", proposal.get("capability_updates", []))
    write("strategy", proposal.get("strategy_updates", []))
    write("knowledge", proposal.get("knowledge_updates", []))
    write("concept_model", proposal.get("concept_model_updates", []))
    write("goals", proposal.get("goal_updates", []))

    # error ledger (append-only jsonl)
    ledger = core / "ledger" / "error_ledger.jsonl"
    with ledger.open("a", encoding="utf-8") as f:
        for e in proposal.get("ledger_entries", []) or []:
            f.write(json.dumps({**e, "cycle": cycle, "run_id": run_id, "recurred_next_cycle": None}) + "\n")
    if proposal.get("ledger_entries"):
        changed.append(str(ledger.relative_to(core.parent)))

    # next-cycle question seeds
    if proposal.get("next_questions"):
        _append_section(core / "strategy" / "next_questions.md", cycle, run_id,
                        "\n".join(f"- {q}" for q in proposal["next_questions"]))
        changed.append("scholar_core/strategy/next_questions.md")

    # entrustment progression — the intern->PI ladder recorded across cycles
    if entrustment and entrustment.get("overall_level") is not None:
        ent = core / "entrustment.jsonl"
        with ent.open("a", encoding="utf-8") as f:
            f.write(json.dumps({
                "cycle": cycle, "run_id": run_id, "ts": time.time(),
                "overall_level": entrustment.get("overall_level"),
                "per_capability": entrustment.get("per_capability", {}),
            }) + "\n")
        changed.append(str(ent.relative_to(core.parent)))

    # revision map (the changelog that proves Loop C acted)
    rev = core / "revision_map.jsonl"
    with rev.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "revision_id": f"rev-{run_id}",
            "cycle": cycle, "run_id": run_id, "ts": time.time(),
            "trigger": "pi_feedback",
            "summary": proposal.get("revision_summary", ""),
            "targets": sorted(set(changed)),
        }) + "\n")
    changed.append(str(rev.relative_to(core.parent)))
    return sorted(set(changed))


async def run_loop_c(run_dir: str | Path, core: Path = REPO / "scholar_core") -> list[str]:
    run_dir = Path(run_dir)
    feedback = load_final_feedback(run_dir)  # gate: status complete + entrustment set
    meta = yaml.safe_load((run_dir / "meta.yaml").read_text())
    cycle = int(meta.get("cycle", 1))
    run_id = meta.get("run_id", run_dir.name)
    proposal = await _propose(_build_prompt(run_dir, core, feedback))
    entrustment = feedback["review"].get("development", {}).get("entrustment")
    changed = apply_updates(proposal, Path(core), cycle, run_id, entrustment)
    print(f"[loop_c] revision: {proposal.get('revision_summary','')}")
    print("[loop_c] wrote:")
    for c in changed:
        print("  -", c)
    return changed


if __name__ == "__main__":
    asyncio.run(run_loop_c(sys.argv[1]))
