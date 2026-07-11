"""Launch-time isolation + completeness guard (ADR-0007).

`run_project` must not start unless the environment is (a) isolated — no ancestor
`CLAUDE.md` bleeding into the Scholar's context, no `~/.claude` config loading — and
(b) complete — the SDK is importable and the cohort data is unpacked. Fails LOUDLY
(SystemExit with a precise message) rather than crashing opaquely mid-run, and logs
the effective launch config into the run dir for the experiment record (ADR-0004).
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any

import yaml


def _ancestor_claude_md(repo: Path) -> list[Path]:
    """`CLAUDE.md` files in directories strictly ABOVE the repo root — these would
    bleed into the agent's context even with setting_sources=['project']."""
    return [p / "CLAUDE.md" for p in repo.resolve().parents if (p / "CLAUDE.md").exists()]


def assert_isolated_and_ready(
    repo: Path, cohort_dir: Path, *, require_data: bool = True
) -> list[str]:
    """Raise SystemExit if the run environment isn't isolated/complete. Returns a
    list of non-fatal warnings (e.g. ~/.claude present but excluded by config)."""
    repo = Path(repo).resolve()
    problems: list[str] = []
    warnings: list[str] = []

    ancestors = _ancestor_claude_md(repo)
    if ancestors:
        problems.append(
            "ancestor CLAUDE.md would bleed into the Scholar's context (ADR-0007): "
            + ", ".join(str(p) for p in ancestors)
        )

    if importlib.util.find_spec("claude_agent_sdk") is None:
        problems.append(
            "claude_agent_sdk not importable — create the env first: "
            "conda env create -f environment.yml && conda activate evolving-scholar"
        )

    if require_data and not Path(cohort_dir).is_dir():
        problems.append(
            f"cohort data not unpacked at {cohort_dir} — unzip "
            "data/synthetic_ttr_REACTSP_tsv_datasets.zip into data/ first"
        )

    dot_claude = Path(os.path.expanduser("~/.claude"))
    if dot_claude.exists():
        warnings.append(
            f"{dot_claude} exists but is excluded (setting_sources=['project'] + "
            "CLAUDE_CODE_DISABLE_AUTO_MEMORY=1)"
        )

    if problems:
        raise SystemExit("[preflight] REFUSING TO RUN:\n  - " + "\n  - ".join(problems))
    return warnings


def log_effective_config(run_dir: Path, config: dict[str, Any]) -> Path:
    """Write the effective launch config to run_dir for the experiment record (ADR-0007)."""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "effective_config.yaml"
    path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return path
