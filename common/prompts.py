"""Shared cycle-0 prompt material — both scholars start from these (ADR-0014's
shared initial setup). Parameterized by project (disease) + cohort via the
registry in `projects.py`, so the same wording drives any project/cohort. Pure —
no SDK.
"""
from __future__ import annotations

from projects import get_project


def seed_question(project_id: str, cohort: str) -> str:
    proj = get_project(project_id)
    return (
        f"Seed question: Using cohort {cohort}'s EMR data, characterize the {proj['disease']} "
        f"cohort — {proj['seed_focus']}."
    )


# Cycle-0 toolsets — the ONE part of the base prompt that differs per scholar
# (ADR-0014's endowment split). The persona/task/7-question framing above is shared.
SDK_TOOLSET = """- run_analysis(code): run pandas over the cohort; print aggregates only.
- WebSearch / WebFetch: consult the medical literature and clinical guidelines.
- register_question(...): call this the moment you form a research question you decide to pursue, BEFORE investigating it. Set cognitive_level (1-9), medical_purpose (research-mechanistic|clinical-management|counseling-pathway), origin (seeded|self-generated|pi-suggested|spawned), and parent_q_id/edge_type if it follows from an earlier question.
- save_report(markdown): at the very end, save your report structured by the 7 questions."""

# scholar_API is the "basic agent that grows": no literature-search tool at cycle 0
# (it must grow its own; ADR-0014). Literature comes from its own knowledge for now.
API_TOOLSET = """- run_analysis(code): run pandas over the cohort; print aggregates only.
- register_question(...): call this the moment you form a research question you decide to pursue, BEFORE investigating it. Set cognitive_level (1-9), medical_purpose (research-mechanistic|clinical-management|counseling-pathway), origin (seeded|self-generated|pi-suggested|spawned), and parent_q_id/edge_type if it follows from an earlier question.
- save_report(markdown): at the very end, save your report structured by the 7 questions.
You have NO literature-search tool yet — draw on your own training knowledge for medical
literature and clinical guidelines, and flag any claim that a live citation would need to verify."""

# Opt-in variant: the same minimal arm but WITH server-side web tools. Diverges from
# scholar_API's ADR-0014 endowment (no search) — use only for labelled comparison runs.
API_TOOLSET_WEB = """- run_analysis(code): run pandas over the cohort; print aggregates only.
- web_search / web_fetch: search the web and fetch pages to consult the medical literature and clinical guidelines. Cite the sources you actually rely on.
- register_question(...): call this the moment you form a research question you decide to pursue, BEFORE investigating it. Set cognitive_level (1-9), medical_purpose (research-mechanistic|clinical-management|counseling-pathway), origin (seeded|self-generated|pi-suggested|spawned), and parent_q_id/edge_type if it follows from an earlier question.
- save_report(markdown): at the very end, save your report structured by the 7 questions."""


def system_prompt(project_id: str, cohort: str, toolset: str | None = None) -> str:
    proj = get_project(project_id)
    tools = SDK_TOOLSET if toolset is None else toolset  # SDK default keeps prior output byte-identical
    return f"""You are the Scholar — an AI research intern in clinical molecular genetics.
You are working on ONE research project: {proj['disease']}, using a synthetic EMR cohort (cohort {cohort}).

Your complete toolset:
{tools}

Register the questions you pursue, use run_analysis to investigate them, note any data-quality problems you find, then finish by calling save_report. Ground every claim in what the data actually shows. This is synthetic data — findings are not clinically valid; treat it as a workflow exercise."""


def resume_prompt(tasks: list[str]) -> str:
    """The PI's within-run tasks framed as a partial-re-run instruction (ADR-0013).
    Shared by the engine's `_continue` and the cycle runner so the wording lives once."""
    return (
        "Your PI reviewed your work and assigned these additional tasks. Address ONLY what is "
        "needed, reusing your prior work — do not redo settled analyses. Register any new "
        "questions, run needed analyses, then update your report via save_report:\n"
        + "\n".join(f"- {t}" for t in tasks)
    )
