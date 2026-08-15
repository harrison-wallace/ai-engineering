---
name: session-start
description: Sit-down scope for this sitting. Propose Now/Next from docs/plans, docs/phases, and git. Write only after the user confirms. Use when Now is empty or wrong, or the user runs /session-start.
user-invocable: true
---

# session-start

Read and follow `session-handshake` (sibling skill, or
`~/.claude/skills/session-handshake/SKILL.md`). Run **Start** only.

Propose, then wait. Do not write Now unless the user confirmed or named the
Now item in this message. Do not implement. Do not treat ROADMAP.md as Next.
Prefer the current in-progress phase, not the next empty one.
