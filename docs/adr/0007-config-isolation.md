# ADR-0007: Config isolation — clean location + two CLAUDE.md tiers

**Status:** Accepted · 2026-07-10

## Context

Claude Code / the Agent SDK load `CLAUDE.md` by walking **up** parent directories with no boundary at the repo root, and (by default) also load the user's `~/.claude` config. Any of these leaking into experiment agents biases what the intern "knows" — invalidating the experiment. The leak is the default; isolation must be explicit.

## Decision

1. Keep the repo where **no ancestor directory has a `CLAUDE.md`** (verified: nothing above `/home/nthink/EvolvingScholar/`). Structural isolation, not a suppression flag.
2. Split memory into two tiers: `CLAUDE.md` (minimal, neutral — loads into the intern runtime) and `CLAUDE.local.md` (developer rules — the `local` tier, excluded from the runtime).
3. Run the intern with `setting_sources=["project"]` (drops `~/.claude` and the `local` tier), an explicit skills allowlist, and `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.

## Consequences

- Personal/global rules and dev notes cannot reach experiment agents.
- If the repo is ever relocated, re-verify no ancestor `CLAUDE.md` exists.
- A launch-time assertion should fail loudly if an ancestor `CLAUDE.md` is detected (todo in `runtime/`).
- Managed/org policy still loads regardless of `setting_sources` → run the experiment on the clean personal environment; treat any work gateway purely as a model endpoint.
