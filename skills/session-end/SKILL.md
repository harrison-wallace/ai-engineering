---
name: session-end
description: Formal end-of-sitting rewrite of SESSION.md and one stanza on docs/plans/archive/sittings.md. Use when closing a sitting, "end SESSION", or the user runs /session-end.
user-invocable: true
---

# session-end

Read and follow `session-handshake` (sibling skill, or
`~/.claude/skills/session-handshake/SKILL.md`). Run **End** only.

Rewrite SESSION. Do not append SESSION. Append one stanza to
`docs/plans/archive/sittings.md`. Prune vague Parking older than two weeks.
Then stop. Do not keep implementing. If SESSION is missing, tell the user
to run `/session-init`.
