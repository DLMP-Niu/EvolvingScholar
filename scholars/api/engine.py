"""scholars/api/engine.py — the raw Anthropic Messages API adapter for scholar_API.

The arm-2 counterpart to scholars/sdk/engine.py. Same Loop A research engine and
the same four-layer capture, but driven by a hand-written tool-use loop over
`client.messages.stream(...)` instead of the Claude Agent SDK. This is the
"basic agent that grows" (ADR-0014): a deliberately minimal endowment —
run_analysis + register_question + save_report, and NO literature-search tool.

Reuses the SDK-free cores in `common/` unchanged (capture writers, EMR analysis,
prompts, scholar_io, preflight, project registry). The SDK arm's server-side
session/resume has no raw-API equivalent, so a --continue run REPLAYS the
persisted message history (`messages.jsonl`) instead of resuming a session id.
"""
from __future__ import annotations

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import anthropic  # type: ignore
import yaml

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "common"))
sys.path.insert(0, str(REPO / "harness"))
from capture import RunContext, _clean  # noqa: E402
from emr_tools import run_cohort_analysis  # noqa: E402
from preflight import assert_isolated_and_ready, log_effective_config  # noqa: E402
from projects import DEFAULT_PROJECT, resolve_cohort  # noqa: E402
from prompts import API_TOOLSET, API_TOOLSET_WEB, resume_prompt, seed_question, system_prompt  # noqa: E402
from scholar_io import load_scholar_core, next_run_no  # noqa: E402

SCHOLAR = "api"
CORE = REPO / "scholars" / "api" / "core"
RUNS_DIR = REPO / "scholars" / "api" / "runs"
COHORT_DIR = REPO / "data" / "synthetic_ttr_REACTSP_tsv_datasets"

# Opus 4.8 default (per Anthropic guidance); overridable so the owner can run a
# cheaper tier for the pilot without editing code. The SDK arm rides on Claude
# Code's model — set SCHOLAR_API_MODEL to match it when comparing arms directly.
MODEL = os.getenv("SCHOLAR_API_MODEL", "claude-opus-4-8")
MAX_TOKENS = int(os.getenv("SCHOLAR_API_MAX_TOKENS", "16000"))
MAX_TURNS = 30
# Opt-in web endowment (ADR-0014 default is OFF — the minimal arm). SCHOLAR_API_WEB=1
# adds server-side web_search/web_fetch; use only for labelled comparison runs.
WEB_DEFAULT = os.getenv("SCHOLAR_API_WEB", "").strip().lower() in ("1", "true", "yes", "on")

# JSON-Schema mirror of common/capture.REGISTER_QUESTION_SCHEMA (which is in the
# SDK's name->type dict form). Kept in sync by hand — the raw API needs real schema.
_REGISTER_QUESTION_JSONSCHEMA = {
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "cognitive_level": {"type": "integer", "description": "1-9 ladder; you self-tag"},
        "medical_purpose": {"type": "string",
                            "description": "research-mechanistic | clinical-management | counseling-pathway"},
        "origin": {"type": "string", "description": "seeded | self-generated | pi-suggested | spawned"},
        "parent_q_id": {"type": "string", "description": "'' if none"},
        "edge_type": {"type": "string", "description": "refines | spawns | blocks | ''"},
        "evidence_source": {"type": "string", "description": "literature | emr | both | ''"},
    },
    "required": ["text", "cognitive_level", "medical_purpose", "origin"],
}


def _tool_defs(web: bool = False) -> list[dict[str, Any]]:
    """scholar_API's cycle-0 toolset. Minimal by default (no literature search — see
    API_TOOLSET); `web=True` adds Anthropic's server-side web_search/web_fetch tools
    (run server-side; no client dispatch), for the opt-in comparison variant."""
    defs: list[dict[str, Any]] = [
        {
            "name": "run_analysis",
            "description": (
                "Run Python (pandas) over the cohort EMR and get printed output back. "
                "Preloaded DataFrames: dx(ID, 'dx ICD code', 'dx ICD name', 'Dx date'); "
                "appt(ID, 'appointment description', 'appointment date'); "
                "glucose(ID, 'lab glucose testing result', 'value', 'unit', 'date'); "
                "dob(ID, 'date_of_birth'). `pd` is available. print() AGGREGATES only — never raw patient rows."
            ),
            "input_schema": {"type": "object",
                             "properties": {"code": {"type": "string"}}, "required": ["code"]},
        },
        {
            "name": "register_question",
            "description": (
                "Log a research question you are actively pursuing, the moment you form it. "
                "Call for every genuine research question you decide to pursue — not rhetorical asides."
            ),
            "input_schema": _REGISTER_QUESTION_JSONSCHEMA,
        },
        {
            "name": "save_report",
            "description": (
                "Save your final run report as Markdown, structured by the 7 questions: "
                "1 What am I studying? 2 Where do I find information? 3 What EMR data do I have? "
                "4 Does EMR confirm literature? 5 Does EMR suggest anything new? 6 What did I build? "
                "7 What did this teach me for the next project?"
            ),
            "input_schema": {"type": "object",
                             "properties": {"markdown": {"type": "string"}}, "required": ["markdown"]},
        },
    ]
    if web:  # server-side tools: Anthropic runs them, results return inline (no client dispatch)
        defs += [
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ]
    return defs


# ---- tool dispatch (pure cores live in common/) --------------------------------

def _dispatch(name: str, args: dict[str, Any], ctx: RunContext, cohort: str, run_dir: Path) -> str:
    if name == "run_analysis":
        return run_cohort_analysis(COHORT_DIR, cohort, args.get("code", ""))
    if name == "save_report":
        (run_dir / "report.md").write_text(args.get("markdown", ""), encoding="utf-8")
        return "report saved"
    if name == "register_question":
        qid = ctx.next_qid()
        ctx.questions.append({
            "q_id": qid, "run_id": ctx.run_id, "run": ctx.run_no, "ts": time.time(), "asker": "ai",
            "text": args.get("text", ""), "cognitive_level": args.get("cognitive_level"),
            "medical_purpose": args.get("medical_purpose"), "origin": args.get("origin"),
            "parent_q_id": _clean(args.get("parent_q_id")), "edge_type": _clean(args.get("edge_type")),
            "evidence_source": _clean(args.get("evidence_source")),
            "status": "open", "result_summary": None, "quality": None,
        })
        return f"registered {qid}"
    return f"unknown tool {name!r}"


# ---- content-block (de)serialization -------------------------------------------

def _block_dump(b: Any) -> dict[str, Any]:
    """Full serialization of a response content block for the transcript log (layer 1).
    Includes SDK output-only fields; NOT safe to replay as request input — use
    `_to_param` for anything sent back to the API."""
    if hasattr(b, "model_dump"):
        return b.model_dump()
    keys = ("type", "id", "name", "input", "text", "thinking", "signature")
    return {k: getattr(b, k) for k in keys if getattr(b, k, None) is not None}


def _to_param(b: Any) -> dict[str, Any]:
    """Convert a RESPONSE content block into a clean request-input param dict — only
    the fields the API accepts on the way back in. A naive model_dump() carries
    output-only fields (e.g. text.parsed_output) that the API rejects with a 400.
    Thinking blocks keep `signature`, which must be replayed unchanged on the same model."""
    t = getattr(b, "type", None)
    if t == "text":
        return {"type": "text", "text": b.text}
    if t == "thinking":
        p = {"type": "thinking", "thinking": getattr(b, "thinking", "") or ""}
        sig = getattr(b, "signature", None)
        if sig is not None:
            p["signature"] = sig
        return p
    if t == "redacted_thinking":
        return {"type": "redacted_thinking", "data": getattr(b, "data", "")}
    if t == "tool_use":
        return {"type": "tool_use", "id": b.id, "name": b.name, "input": b.input}
    if t == "server_tool_use":  # web_search/web_fetch invocation (server-run)
        return {"type": "server_tool_use", "id": b.id, "name": b.name, "input": b.input}
    if t in ("web_search_tool_result", "web_fetch_tool_result"):  # server-tool results, echoed for context
        d = _block_dump(b)
        return {k: d[k] for k in ("type", "tool_use_id", "content") if k in d}
    return _block_dump(b)  # unknown block: best effort


def _capture_thinking(resp: Any, ctx: RunContext) -> None:
    for b in getattr(resp, "content", []):
        if getattr(b, "type", None) == "thinking":
            ctx.thinking.append({
                "ts": time.time(),
                "text": getattr(b, "thinking", "") or "",  # empty unless display=summarized
                "signature": getattr(b, "signature", None),
            })


def _dump_messages(run_dir: Path, messages: list[dict[str, Any]]) -> None:
    import json
    (run_dir / "messages.jsonl").write_text(
        "\n".join(json.dumps(m, default=str, ensure_ascii=False) for m in messages) + "\n",
        encoding="utf-8")


def _load_messages(run_dir: Path) -> list[dict[str, Any]]:
    import json
    p = run_dir / "messages.jsonl"
    if not p.exists():
        raise SystemExit(f"no messages.jsonl in {run_dir} — cannot resume the API arm")
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


# ---- Loop A run ----------------------------------------------------------------

def run_project(prompt: str, run_dir: Path | None = None, project: str = DEFAULT_PROJECT,
                cohort: str | None = None, run_no: int | None = None, resume: bool = False,
                web: bool | None = None, client: Any = None) -> Path:
    """Run (new) or continue (replay) one experiment run. Returns run_dir.

    A NEW run (run_dir=None) is numbered as this scholar's next feedback-gated run
    (`next_run_no`) unless `run_no` is given; a --continue run (resume=True) reloads
    the persisted message history from run_dir and appends the PI's tasks. `web`
    (default from SCHOLAR_API_WEB) opts into server-side web_search/web_fetch."""
    client = client or anthropic.Anthropic()
    web = WEB_DEFAULT if web is None else web
    cohort = resolve_cohort(project, cohort)
    if run_dir is None:
        run_id = f"ttr{cohort}-api{'-web' if web else ''}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
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

    toolset = API_TOOLSET_WEB if web else API_TOOLSET
    system = system_prompt(project, cohort, toolset=toolset) + load_scholar_core(CORE)
    tools = _tool_defs(web)
    messages: list[dict[str, Any]] = _load_messages(run_dir) if resume else []
    messages.append({"role": "user", "content": prompt})

    endowment = ("raw-messages-api + web (variant: run_analysis/web_search/web_fetch/"
                 "register_question/save_report)" if web else
                 "raw-messages-api (minimal: run_analysis/register_question/save_report; no web)")
    log_effective_config(run_dir, {  # experiment record (ADR-0004/0007)
        "run_id": run_id, "scholar": SCHOLAR, "project": project, "cohort": cohort, "run": run_no,
        "repo": str(REPO), "cohort_dir": str(COHORT_DIR), "model": MODEL, "max_tokens": MAX_TOKENS,
        "endowment": endowment, "web": web, "thinking": "adaptive", "resumed": resume,
    })

    meta_path = run_dir / "meta.yaml"
    meta = yaml.safe_load(meta_path.read_text()) if meta_path.exists() else {
        "run_id": run_id, "scholar": SCHOLAR, "project": project, "cohort": cohort, "run": run_no,
        "model": MODEL, "web": web, "started": datetime.now().isoformat(),
        "seed_question": seed_question(project, cohort), "turns": [],
    }
    meta.setdefault("turns", []).append(
        {"resumed": resume, "prompt": prompt[:200], "at": datetime.now().isoformat()})
    meta_path.write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")

    print(f"[engine] {'continue' if resume else 'new'} run={run_id} "
          f"project={project} cohort={cohort} run_no={run_no} model={MODEL} web={web}")

    in_tok = out_tok = 0
    stop_reason = None
    for _turn in range(MAX_TURNS):
        with client.messages.stream(  # stream so large max_tokens doesn't hit HTTP timeouts
            model=MODEL, max_tokens=MAX_TOKENS, system=system, tools=tools, messages=messages,
            thinking={"type": "adaptive", "display": "summarized"},
        ) as stream:
            resp = stream.get_final_message()

        ctx.transcript.append({  # layer 1
            "type": "message", "model": getattr(resp, "model", None),
            "stop_reason": getattr(resp, "stop_reason", None),
            "content": [_block_dump(b) for b in resp.content],
        })
        _capture_thinking(resp, ctx)  # layer 2
        usage = getattr(resp, "usage", None)
        if usage is not None:
            in_tok += getattr(usage, "input_tokens", 0) or 0
            out_tok += getattr(usage, "output_tokens", 0) or 0
        for b in resp.content:
            if getattr(b, "type", None) == "text" and (b.text or "").strip():
                print("SCHOLAR:", b.text.strip()[:200])

        messages.append({"role": "assistant", "content": [_to_param(b) for b in resp.content]})
        stop_reason = getattr(resp, "stop_reason", None)

        if stop_reason == "tool_use":
            results = []
            for b in resp.content:
                if getattr(b, "type", None) == "tool_use":
                    ctx.actions.append({  # layer 3
                        "ts": time.time(), "tool_use_id": b.id, "tool_name": b.name, "tool_input": b.input,
                    })
                    out = _dispatch(b.name, b.input, ctx, cohort, run_dir)
                    results.append({"type": "tool_result", "tool_use_id": b.id, "content": out})
            messages.append({"role": "user", "content": results})
            continue
        if stop_reason == "pause_turn":  # server-tool pause: resend to resume (no new user msg)
            continue
        break  # end_turn | refusal | max_tokens | stop_sequence

    _dump_messages(run_dir, messages)
    meta["stop_reason"] = stop_reason
    meta_path.write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")
    print(f"\n[engine] done — stop_reason={stop_reason} in_tok={in_tok} out_tok={out_tok}")
    if stop_reason == "refusal":
        print("[engine] WARNING: run ended on a safety refusal — report may be absent.")
    print("artifacts in:", run_dir)
    return run_dir


def _continue(run_dir: str) -> None:
    from pi import pending_tasks  # noqa: E402

    rd = Path(run_dir)
    meta = yaml.safe_load((rd / "meta.yaml").read_text())
    tasks = pending_tasks(rd)
    if not tasks:
        raise SystemExit("no pending tasks (feedback status != 'needs_more' or new_tasks empty)")
    run_project(resume_prompt(tasks), run_dir=rd, resume=True, web=meta.get("web"),
                project=meta.get("project", DEFAULT_PROJECT), cohort=meta.get("cohort"),
                run_no=int(meta.get("run", 1)))


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="scholar_API Loop A — run or continue an experiment run.")
    ap.add_argument("--continue", dest="cont", metavar="RUN_DIR",
                    help="resume this run with the PI's pending tasks (replays messages.jsonl; ADR-0013)")
    ap.add_argument("--project", default=DEFAULT_PROJECT, help="research project id (see common/projects.py)")
    ap.add_argument("--cohort", default=None, help="cohort within the project (default: project default)")
    args = ap.parse_args()
    if args.cont:
        _continue(args.cont)
    else:
        cohort = resolve_cohort(args.project, args.cohort)
        run_project(seed_question(args.project, cohort), project=args.project, cohort=cohort)
