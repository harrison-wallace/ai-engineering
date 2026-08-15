---
name: session-end
description: Formal end-of-sitting rewrite of SESSION.md. Use when closing a sitting, "end SESSION", or the user runs /session-end.
user-invocable: true
---

# session-end

Read and follow `session-handshake` (sibling skill, or
`~/.claude/skills/session-handshake/SKILL.md`). Run **End** only.

Rewrite SESSION. Do not append. Prune vague Parking older than two weeks.
Then stop. Do not keep implementing. If the file is missing, tell the user
to run `/session-init`.
