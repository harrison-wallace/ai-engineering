---
name: session-init
description: Create docs/plans/SESSION.md once, gitignore docs/plans and docs/phases, migrate STATUS.md. Use when setting up session tracking or the user runs /session-init.
user-invocable: true
---

# session-init

Read and follow `session-handshake` (sibling skill, or
`~/.claude/skills/session-handshake/SKILL.md`). Run **Init** only.

Do not start, check, snap, end, or prune. Do not overwrite an existing
`docs/plans/SESSION.md`. Do not create `archive/sittings.md`. After creating
or migrating SESSION, tell the user to run `/session-start`. Do not start
product work.
