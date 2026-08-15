---
name: status-snap
description: Mid-session rewrite of STATUS.md so it matches git and this conversation, without ending the session. Use after a chunk of work, before compact or a tool switch, when check says stale, or /status-snap.
user-invocable: true
---

# status-snap

Read and follow `session-status` (sibling skill, or `~/.claude/skills/session-status/SKILL.md`).
Run **Snap** only.

Rewrite STATUS. Do not append. Do not close the session. Do not prune Parking
for age. If the file is missing, tell the user to run `/status-init`.
