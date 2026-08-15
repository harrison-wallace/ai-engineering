---
name: session-status
description: Create or rewrite the STATUS.md handshake file so work, next steps, and leftover thoughts survive across agent sessions. Use when starting or ending a multi-session effort, when the user says "track this across sessions", "set up STATUS.md", "session handshake", or runs /session-status.
---

# session-status

A repo-local `STATUS.md` is the only queue that survives a new chat or a tool
switch. Chat memory and in-session todos do not.

Template: [STATUS.template.md](STATUS.template.md).

## Path

- `docs/plans/STATUS.md` if `docs/plans/` already exists.
- Otherwise `STATUS.md` at the repo root.
- Do not create `docs/plans/` only to hold this file.

One file. Never both.

## What belongs where

| Kind | Where | Not in STATUS |
|---|---|---|
| This week's queue | STATUS Now / Next | — |
| Half-formed idea | STATUS Parking | A second `THOUGHTS.md` |
| Work just done | git + Last session | A running changelog |
| Locked choice | Decision log (`DECISIONS.md` or ADRs) | Reciting the decision |
| Multi-month map | Existing plan / roadmap | Copying the roadmap |

## Mode

Detect from the request. If unclear, ask once: **init**, **start**, or **end**.

### Init

1. If the file exists, say so and switch to **start**. Do not overwrite.
2. If it does not: write the template, fill `Updated` (today), `Milestone` (from
   the repo plan if obvious, else `none`), and **Now** (the next real action, or
   `none` if you must ask).
3. Leave Next / Blocked / Last session / Parking empty rather than inventing.

### Start

1. Read STATUS. Then only the docs the Now item needs.
2. Brief the user in 4–6 lines: Now, Next (headlines), Blocked, Parking count.
3. Do the Now item only if the user asked you to continue. Otherwise stop after
   the brief.

### End

Rewrite the file. Do not append.

1. Set `Updated` to today.
2. Move a finished Now off. Promote the first Next, or write `none`.
3. Keep Next at 3–7 ordered items.
4. Replace Last session with a short list of what landed and what did not.
5. Park new thoughts. Delete a Parking item older than two weeks that is still
   vague.
6. Commit STATUS with the work, or immediately after, if you are committing.

## Rules

- One Now item.
- Overwrite, never append.
- Do not start Linear, GitHub issues, or a Projects board for this.
- Do not implement product work while only asked to init or brief.
