"""Runtime-neutral EMR analysis core — reusable by any build arm. NO SDK dependency.

The `@tool` SDK wrappers live in `scholars/sdk/engine.py`; the raw-API arm will
wrap `run_cohort_analysis` its own way. Method-encoding tools are deliberately
absent (ADR-0011).
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

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
