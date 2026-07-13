#!/usr/bin/env python3
"""Replay a captured EvolvingScholar run as a paced terminal "simulation".

Reads the on-disk capture only (no live agent, no API calls, no tokens) and
renders the A -> B -> C story: the research narrative + tool calls, the report,
the PI review + entrustment, and the EPAs the scholar earned.

Usage:
  python scripts/replay_run.py <run_dir>                  # play live in the terminal
  python scripts/replay_run.py <run_dir> --cast out.cast  # write an asciinema v2 cast
  python scripts/replay_run.py <run_dir> --speed 1.6      # faster (live and cast)

The .cast is turned into a GIF with:  agg out.cast out.gif   (or fed to VHS).

Data sources under <run_dir>: effective_config.yaml, questions.jsonl,
transcript.jsonl, report.md, feedback_project.yaml. EPAs + entrustment come
from the scholar's core/ (inferred as <run_dir>/../../core, or --scholar-core).
"""
import argparse, glob, json, os, re, sys, time

# ---------- palette ----------
def _c(code): return f"\033[{code}m"
RESET = _c(0); BOLD = _c(1); DIM = _c(2)
BLUE = _c("38;5;75"); GREEN = _c("38;5;78"); AMBER = _c("38;5;179")
CYAN = _c("38;5;80"); GREY = _c("38;5;245"); RED = _c("38;5;168")

ARM_LABEL = {"sdk": "Scholar 1 (SDK)", "api": "Scholar 2 (API)"}
ARM_ENDOW = {"sdk": "Claude Agent SDK · rich tools",
             "api": "raw Messages API · minimal tools"}


# ---------- pacing engine (drives live stdout OR an asciinema cast) ----------
class Stage:
    def __init__(self, cast=False, speed=1.0, cols=100, rows=32):
        self.cast = cast; self.speed = max(0.05, speed)
        self.cols = cols; self.rows = rows
        self.t = 0.0; self.events = []

    def _out(self, s):
        if self.cast:
            self.events.append([round(self.t, 3), "o", s])
        else:
            sys.stdout.write(s); sys.stdout.flush()

    def wait(self, dt):
        self.t += dt
        if not self.cast:
            time.sleep(dt / self.speed)

    def line(self, s="", pause=0.32):
        self._out(s + "\r\n"); self.wait(pause)

    def type(self, text, color="", cps=48, pause=0.4):
        if color: self._out(color)
        step = 1.0 / cps
        for ch in text:
            self._out(ch); self.wait(step)
        if color: self._out(RESET)
        self._out("\r\n"); self.wait(pause)

    def save(self, path):
        header = {"version": 2, "width": self.cols, "height": self.rows,
                  "env": {"TERM": "xterm-256color"}}
        with open(path, "w") as f:
            f.write(json.dumps(header) + "\n")
            for t, ch, data in self.events:
                f.write(json.dumps([round(t / self.speed, 3), ch, data]) + "\n")


# ---------- readers ----------
def read_jsonl(p):
    out = []
    if os.path.exists(p):
        for ln in open(p):
            ln = ln.strip()
            if ln:
                try: out.append(json.loads(ln))
                except Exception: pass
    return out

def flat_yaml(p):
    d = {}
    if os.path.exists(p):
        for ln in open(p):
            m = re.match(r"^([A-Za-z0-9_]+):\s*(.*)$", ln.rstrip())
            if m: d[m.group(1)] = m.group(2).strip().strip("'\"")
    return d

def trunc(s, n):
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"

def arm_from_path(run_dir):
    parts = os.path.normpath(run_dir).split(os.sep)
    if "scholars" in parts:
        i = parts.index("scholars")
        if i + 1 < len(parts):
            return parts[i + 1]
    return "?"


def pi_scores(run_dir):
    """Return [(dimension, score)] from feedback_project.yaml. Uses PyYAML if
    present; degrades gracefully if not."""
    p = os.path.join(run_dir, "feedback_project.yaml")
    if not os.path.exists(p):
        return []
    try:
        import yaml
        fb = yaml.safe_load(open(p)) or {}
        sc = ((fb.get("review") or {}).get("scores") or {})
        return [(k, v.get("score")) for k, v in sc.items() if v.get("score") is not None]
    except Exception:
        return []

def entrustment_level(run_dir, core_dir):
    # Prefer this run's own PI feedback; fall back to the scholar's current level.
    try:
        import yaml
        fb = yaml.safe_load(open(os.path.join(run_dir, "feedback_project.yaml"))) or {}
        lvl = (((fb.get("review") or {}).get("development") or {})
               .get("entrustment") or {}).get("overall_level")
        if lvl is not None:
            return lvl
    except Exception:
        pass
    for rec in reversed(read_jsonl(os.path.join(core_dir, "entrustment.jsonl"))):
        if rec.get("overall_level") is not None:
            return rec["overall_level"]
    return None

def epa_summary(path):
    heads, gist = [], ""
    lines = [l.rstrip() for l in open(path)]
    for l in lines:
        s = l.strip()
        if s.startswith("# "):
            heads.append(s[2:].strip())
        if not gist and ("Validated instance" in s or s.startswith("**When:**")):
            gist = re.sub(r"\*\*|`", "", s).split(":", 1)[-1].strip()
    if not gist:
        for l in lines:
            s = re.sub(r"\*\*|`", "", l).strip()
            if s and not s.startswith("#") and len(s) > 15:
                gist = s
                break
    title = heads[-1] if heads else os.path.basename(path)[:-3]
    if "-" in title and " " not in title:
        title = title.replace("-", " ").capitalize()
    return title, gist


def render_tool(st, name, inp):
    inp = inp or {}
    base = (name or "").split("__")[-1]          # strip MCP prefix (SDK arm)
    if base == "register_question":
        st.line(f"{GREEN}  ✎ register_question{RESET} "
                f"{DIM}L{inp.get('cognitive_level','?')} {inp.get('origin','')}{RESET} "
                f"{trunc(inp.get('text',''), 84)}", pause=0.5)
    elif base == "run_analysis":
        code = [c.strip() for c in (inp.get("code", "") or "").splitlines() if c.strip()]
        first = next((c for c in code if not c.startswith("#")), "")
        st.line(f"{BLUE}  ⚙ run_analysis{RESET} {GREY}{trunc(first, 78)}{RESET}", pause=0.5)
    elif base in ("save_report", "save_final_report"):
        st.line(f"{BLUE}  \U0001f4be save_report{RESET} {GREY}→ report.md{RESET}", pause=0.4)
    elif base in ("WebSearch", "web_search"):
        st.line(f"{CYAN}  \U0001f50d web_search{RESET} "
                f"{GREY}{trunc(inp.get('query',''), 70)}{RESET}", pause=0.5)
    else:
        detail = inp.get("query") or inp.get("command") or inp.get("path") or ""
        st.line(f"{BLUE}  ▸ {base}{RESET} {GREY}{trunc(str(detail), 72)}{RESET}", pause=0.4)


# ---------- storyboard ----------
def replay(run_dir, core_dir, st):
    cfg = flat_yaml(os.path.join(run_dir, "meta.yaml"))
    for k, v in flat_yaml(os.path.join(run_dir, "effective_config.yaml")).items():
        if v:
            cfg[k] = v
    arm = arm_from_path(run_dir)                 # dir name is authoritative (sdk/api)
    label = ARM_LABEL.get(arm, arm)
    web = str(cfg.get("web", "")).lower() == "true"

    st.line()
    st.line(f"{DIM}evolving-scholar · guided self-evolution loop{RESET}")
    st.type(f"▮ {label}   {ARM_ENDOW.get(arm,'')}", color=BOLD + BLUE, cps=55, pause=0.2)
    run_no = cfg.get("run") or cfg.get("cycle")
    bits = [cfg.get("model"), cfg.get("project"),
            f"cohort {cfg.get('cohort')}" if cfg.get("cohort") else None,
            f"run {run_no}" if run_no else None,
            "web on" if web else None]
    st.line(f"{GREY}  {' · '.join(b for b in bits if b)}{RESET}", pause=0.55)
    st.line()

    # ---- Loop A ----
    st.line(f"{AMBER}── Loop A · Research ────────────────{RESET}", pause=0.4)
    qs = read_jsonl(os.path.join(run_dir, "questions.jsonl"))
    seed = next((q for q in qs if q.get("origin") == "seeded"), qs[0] if qs else None)
    if seed:
        st._out(f"{GREY}seed ▸ {RESET}")
        st.type(trunc(seed.get("text", ""), 92), color=RESET, cps=52, pause=0.5)

    for msg in read_jsonl(os.path.join(run_dir, "transcript.jsonl")):
        for blk in (msg.get("content") or []):
            bt = blk.get("type")
            if bt in ("text", "TextBlock"):
                txt = (blk.get("text") or "").strip()
                if txt:
                    st.line(f"{RESET}{trunc(txt, 92)}", pause=0.55)
            elif bt in ("tool_use", "ToolUseBlock"):
                render_tool(st, blk.get("name"), blk.get("input"))
            elif bt == "server_tool_use":
                st.line(f"{CYAN}  \U0001f50d web_search{RESET} "
                        f"{GREY}{trunc((blk.get('input') or {}).get('query',''), 70)}{RESET}", pause=0.5)

    if qs:
        st.line()
        st.line(f"{DIM}questions raised: {RESET}"
                + "  ".join(f"L{q.get('cognitive_level')}({q.get('origin')})" for q in qs), pause=0.5)

    # ---- Report ----
    rep = os.path.join(run_dir, "report.md")
    if os.path.exists(rep):
        st.line()
        st.line(f"{AMBER}── Report ────────────────────{RESET}", pause=0.3)
        body = [l.rstrip() for l in open(rep) if l.strip()]
        for l in body[:5]:
            st.line(f"{GREY}{trunc(l, 88)}{RESET}", pause=0.28)

    # ---- Loop B ----
    st.line()
    st.line(f"{AMBER}── Loop B · PI review ─────────────{RESET}", pause=0.3)
    for dim, sc in pi_scores(run_dir):
        n = int(sc) if isinstance(sc, (int, float)) else 0
        dots = "●" * min(n, 5) + "○" * max(0, 5 - n)
        col = GREEN if n >= 4 else (AMBER if n >= 3 else RED)
        st.line(f"{GREY}  {dim:<26}{col}{dots}{RESET} {DIM}{sc}{RESET}", pause=0.14)
    ent = entrustment_level(run_dir, core_dir)
    if ent is not None:
        st.line(f"{BOLD}{GREEN}  ⇧ entrustment level: {ent}{RESET}", pause=0.6)

    # ---- Loop C ----
    caps = sorted(glob.glob(os.path.join(core_dir, "capabilities", "*.md")))
    st.line()
    st.line(f"{AMBER}── Loop C · Evolve ──────────────{RESET}", pause=0.3)
    st.type(f"{label} earned {len(caps)} EPAs → core/capabilities/", color=BOLD + GREEN, cps=52, pause=0.45)
    for c in caps:
        title, gist = epa_summary(c)
        st.line(f"{GREEN}  ✦ {BOLD}{title}{RESET}", pause=0.22)
        if gist:
            st.line(f"{GREY}     {trunc(gist, 82)}{RESET}", pause=0.38)
    st.line()
    st.line(f"{DIM}growth = a diff to core/capabilities/ — not a bigger prompt.{RESET}", pause=0.9)
    st.line()


def main():
    ap = argparse.ArgumentParser(description="Replay a captured EvolvingScholar run.")
    ap.add_argument("run_dir")
    ap.add_argument("--cast", metavar="FILE", help="write an asciinema v2 cast instead of playing live")
    ap.add_argument("--scholar-core", metavar="DIR", help="override the scholar core/ dir")
    ap.add_argument("--speed", type=float, default=1.0, help="playback speed multiplier (default 1.0)")
    ap.add_argument("--cols", type=int, default=100)
    ap.add_argument("--rows", type=int, default=32)
    args = ap.parse_args()

    run_dir = args.run_dir.rstrip("/")
    if not os.path.isdir(run_dir):
        sys.exit(f"run_dir not found: {run_dir}")
    core_dir = args.scholar_core or os.path.join(os.path.dirname(os.path.dirname(run_dir)), "core")

    st = Stage(cast=bool(args.cast), speed=args.speed, cols=args.cols, rows=args.rows)
    replay(run_dir, core_dir, st)
    if args.cast:
        st.save(args.cast)
        print(f"wrote {args.cast}  ({len(st.events)} events, ~{st.t/st.speed:.1f}s)  ->  agg {args.cast} out.gif")


if __name__ == "__main__":
    main()
