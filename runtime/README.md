# runtime/ — orchestration entrypoint(s)

Drives Loop A (the intern's research activity) and sequences the A → B → C cycle. Single runtime for the feasibility pilot; a second build arm (SDK vs. raw API) is deferred (ADR-0006).

**Must enforce config isolation at launch** (ADR-0007):
- `setting_sources=["project"]`, explicit skills allowlist, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.
- A launch-time assertion should **fail loudly** if any ancestor `CLAUDE.md` is detected above the repo root, or if `~/.claude` config would load.
- Log the effective config at run start for the experiment record.

_Entrypoint to be created once module design is frozen._
