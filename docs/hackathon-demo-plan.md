# EvolvingScholar — Hackathon Demo Plan & Talking Points

_Working doc for a 3–5 minute hackathon demo (HTML slides + live/recorded run). Living — expect reiterations. Captured 2026-07-12._

## Deliverable
A **3–5 minute demo**: HTML slides + a short demo (live or screen-recorded) of one A→B→C run and the resulting evolution diff. Two **design styles** for two **target audiences** (see §3).

---

## 1. Talking points (owner's raw options — pick a subset per audience)

Numbered as the owner listed them. These are *candidate* points, not all will fit 3–5 min.

1. **Credibility / motivation.** Clinical molecular geneticist building AI medical applications across all three frontier model families. More testing → conviction that we need better understanding of *AI model behavior* for medicine — from basic memorization up to clinical reasoning.
2. **Design premise.** Built on a *human learner's* experience: a classic clinical-genetics disease study that combines literature summarization with a real-world patient-cohort study.
3. **What works so far.** The two-arm design demonstrates a working workflow that mimics the human learning experience. _(NAMING UNRESOLVED — "loop" vs "harness" vs "scholar"; see §4.1.)_
4. **Novelty.** Designing **EPAs as eventual medical capability** — the foundation for *trust* in medicine — and beginning to explore AI **discovery-type exploration** with human feedback and iteration.
5. **Momentum (July).** Onboarding students, residents, and fellows to share experience for further development; **Scholar 2 (API)** enables continued experiments in a **secure environment**.
6. **The framing question / goal.** The question posed to a real intern: *"If you review all relevant literature from the past 5 years on gene A / disease B and study the largest US real-world cohort, would you become a true expert?"* With EvolvingScholar this can be run quickly across many classic clinical-genetics diseases, and eventually aligned against MD / PhD / genetics-specialty development trajectories. _(CLAIM CAUTION — see §4.2.)_
7. **The thesis.** Using this project to explore AI-based clinical molecular-genetics applications where we must address **knowledge + EPAs** — the things humans acquire through *experience and failure*.

---

## 2. Demo arc (shared skeleton, two skins)

~3.5 min target; each beat has a slide.

| # | Beat | ~Time | Content |
|---|---|---|---|
| 1 | Hook | 0:20 | One line: *"An AI research intern that learns the way a trainee does — not by growing its prompt."* |
| 2 | The premise | 0:30 | Human-learner analogy; the intern framing question (point 2/6). |
| 3 | How it works | 0:50 | Three loops (research → PI review → evolve) + two arms (SDK vs raw API). |
| 4 | Demo | 1:20 | Recorded run: Loop A on TTR cohort → PI review → **evolution diff** (run 0: 0 EPAs → run 1: 4 EPAs, entrustment L2). `git show 230e36b -- scholars/api/core/`. |
| 5 | Payoff finding | 0:30 | The concrete catch: 41 amyloidosis patients coded legacy ICD-9 `277.3x` not `E85.x` → naive filter under-counts. |
| 6 | Why it matters / next | 0:30 | EPA = capability = trust; July cohort of trainees; secure Scholar 2 (API). |

---

## 3. Two audiences × two design styles

| | **Style A — Builders / AI track** | **Style B — Clinical / medical track** |
|---|---|---|
| Audience | Engineers, AI researchers, hackathon tech judges | Clinicians, medical-education judges, general |
| Hook | "Learns like an intern, not by growing its prompt" | The intern question: "would you become an expert?" |
| Emphasis | Two arms (SDK vs raw API), typed/versioned artifacts, **git diff = the agent grew**, harness, EPA evolution | EPA→capability→**trust**, literature→real-cohort workflow, the ICD-9 finding, path to clinical genetics |
| Aesthetic | Dark, technical, diagram/code-forward | Clean, clinical, warm; human-learning analogy forward |
| Downplay | Clinical nuance | Runtime/engineering internals |

Both styles reuse the §2 skeleton; only framing, emphasis, and visual language change.

---

## 4. Domain-modeling review notes (feeds glossary/ADRs)

### 4.1 Naming the workflow (point 3) — RESOLVED
Canonical term = **Guided self-evolution loop** (added to `CONTEXT.md`). The three A/B/C loops are its parts; distinct from **Scholar** (agent) and **harness** (code). "loop / harness / scholar" as names for the whole workflow are deprecated.

### Decisions (2026-07-12)
- **Workflow name:** Guided self-evolution loop.
- **Audiences / two styles:** Style A = AI/builders; Style B = clinical/medical.
- **Demo format:** Hybrid — recorded run embedded, slides driven live.

### 4.2 "True expert" (point 6) — CONFLICT with existing scope
The glossary + ADR-0002 + design-notes.md:82 explicitly rule out claiming **human-equivalent expertise** via a human learning path; PI-level is a *measurement coordinate, not a destination*. Talking point 6 as phrased ("become a true expert") overclaims against the project's own framing.
**Resolution for the demo:** keep it as the intern's *motivating question*, not a claim — frame as *"can we measure how far up the expertise trajectory an AI intern climbs?"* not *"the AI becomes an expert."* This preserves the honest, descriptive stance (complementary windows, not a scoreboard).
