"""Research-project registry (ADR-0014) — one entry per gene/disease container.

A run targets a project + a cohort; the project fixes the disease label and the
seed focus. This is what lets a run pick cohort A *or* B (both TTR/ATTR here —
A is deep EMR, B is registry-sparse) instead of the old hardwired seed. Pure — no
SDK, so both scholars share it.

PMP22-CMT is a stub: a real second research project would be added here once its
synthetic cohort exists.
"""
from __future__ import annotations

PROJECTS: dict[str, dict] = {
    "TTR-ATTR": {
        "disease": "TTR / hereditary ATTR amyloidosis",
        "cohorts": ["A", "B"],
        "default_cohort": "A",
        "seed_focus": (
            "how many patients there are, the most frequent diagnoses, and whether the "
            "expected cardiac vs. neuropathic phenotype is present among amyloidosis "
            "(ICD E85.x) patients"
        ),
    },
    # "PMP22-CMT": future project — no synthetic cohort yet (stub).
}
DEFAULT_PROJECT = "TTR-ATTR"


def get_project(project_id: str) -> dict:
    if project_id not in PROJECTS:
        raise SystemExit(f"unknown project {project_id!r}; known: {list(PROJECTS)}")
    return PROJECTS[project_id]


def resolve_cohort(project_id: str, cohort: str | None) -> str:
    """Cohort for this run: the requested one (must belong to the project) or the
    project default."""
    proj = get_project(project_id)
    if cohort is None:
        return proj["default_cohort"]
    if cohort not in proj["cohorts"]:
        raise SystemExit(
            f"cohort {cohort!r} is not part of project {project_id!r} "
            f"(cohorts: {proj['cohorts']})"
        )
    return cohort
