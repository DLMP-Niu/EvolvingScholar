"""Portable Loop A tools (Build 1, SDK arm): run_analysis + save_report.

`run_cohort_analysis` is the runtime-neutral core (reusable by the raw-API arm
later); the `@tool` wrappers are the SDK adapter. register_question lives in
runtime/capture.py. Method-encoding tools are deliberately absent (ADR-0011).
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool  # type: ignore

COHORT_TABLES = {
    "A": {
        "dx": "dataset_A_diagnosis.tsv",
        "appt": "dataset_A_appointments.tsv",
        "glucose": "dataset_A_glucose_labs.tsv",
        "dob": "dataset_A_id_date_of_birth.tsv",
    },
    "B": {
        "dx": "dataset_B_diagnosis.tsv",
        "appt": "dataset_B_appointments.tsv",
        "glucose": "dataset_B_glucose_labs.tsv",
        "dob": "dataset_B_id_date_of_birth.tsv",
    },
}
OUTPUT_CAP = 4000


def run_cohort_analysis(cohort_dir: Path, cohort: str, code: str, timeout: int = 30) -> str:
    """Runtime-neutral core: exec `code` in a subprocess with the cohort's tables
    preloaded as pandas DataFrames (dx, appt, glucose, dob) and `pd`. Returns
    captured stdout, capped. Aggregates only — never print raw patient rows."""
    cohort_dir = Path(cohort_dir)
    preamble = "import pandas as pd\n"
    for name, fname in COHORT_TABLES[cohort].items():
        preamble += f"{name} = pd.read_csv(r'{cohort_dir / fname}', sep='\\t')\n"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(preamble + "\n" + code)
        path = f.name
    try:
        proc = subprocess.run(
            [sys.executable, path], capture_output=True, text=True, timeout=timeout
        )
        out = proc.stdout
        if proc.returncode != 0:
            out += "\n[stderr]\n" + proc.stderr
    except subprocess.TimeoutExpired:
        out = f"[error] analysis timed out after {timeout}s"
    finally:
        os.unlink(path)
    if len(out) > OUTPUT_CAP:
        out = out[:OUTPUT_CAP] + f"\n[...truncated at {OUTPUT_CAP} chars — return aggregates, not raw rows]"
    return out or "[no output — did you print()?]"


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
        "Save your final cycle report as Markdown, structured by the 7 questions: "
        "1 What am I studying? 2 Where do I find information? 3 What EMR data do I have? "
        "4 Does EMR confirm literature? 5 Does EMR suggest anything new? 6 What did I build? "
        "7 What did this teach me for the next project?",
        {"markdown": str},
    )
    async def save_report(args: dict[str, Any]) -> dict[str, Any]:
        (Path(run_dir) / "report.md").write_text(args.get("markdown", ""), encoding="utf-8")
        return {"content": [{"type": "text", "text": "report saved"}]}

    return create_sdk_mcp_server("scholar_tools", "0.1.0", tools=[run_analysis, save_report])
