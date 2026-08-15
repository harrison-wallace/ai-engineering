---
name: status-check
description: Brief the repo STATUS.md when entering a repo or starting a session. Read-only. Use on session start, "check STATUS", or /status-check.
user-invocable: true
---

# status-check

Read and follow `session-status` (sibling skill, or `~/.claude/skills/session-status/SKILL.md`).
Run **Check** only.

Read-only. Do not edit STATUS. If the file is missing, tell the user to run
`/status-init`. If it is stale, tell the user to run `/status-snap`.
Do not start the Now item unless the user also said to continue.
