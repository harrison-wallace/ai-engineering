---
name: session-check
description: Brief docs/plans/SESSION.md when entering a repo. Read-only. Use on session start when Now is already set, "check SESSION", or /session-check.
user-invocable: true
---

# session-check

Read and follow `session-handshake` (sibling skill, or
`~/.claude/skills/session-handshake/SKILL.md`). Run **Check** only.

Read-only. Do not edit SESSION. Do not read `archive/sittings.md`. If
SESSION is missing, tell the user to run `/session-init`. If it is stale,
tell the user to run `/session-snap`. Do not start the Now item unless the
user also said to continue.
