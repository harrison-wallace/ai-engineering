---
name: status-end
description: Formal end-of-session rewrite of STATUS.md. Use when closing a session, "end STATUS", or the user runs /status-end.
user-invocable: true
---

# status-end

Read and follow `session-status` (sibling skill, or `~/.claude/skills/session-status/SKILL.md`).
Run **End** only.

Rewrite STATUS. Do not append. Prune vague Parking older than two weeks.
Then stop. Do not keep implementing. If the file is missing, tell the user
to run `/status-init`.
