---
name: session-status
description: Contract for the STATUS.md handshake (path, template, what belongs where). Not a slash command. Invoked by /status-init, /status-check, /status-snap, and /status-end.
user-invocable: false
---

# session-status

A repo-local `STATUS.md` is the only queue that survives a new chat or a tool
switch. Chat memory and in-session todos do not.

This file is the contract. The four user skills run one mode each. Do not invent
a fifth file or a board.

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

## Modes

### Init (`/status-init`)

1. If the file exists, say so and stop. Tell the user to run `/status-check`.
   Do not overwrite.
2. If it does not: write the template. Fill `Updated` (today), `Milestone`
   (from the repo plan if obvious, else `none`), and **Now** (the next real
   action, or `none` if you must ask).
3. Leave Next / Blocked / Last session / Parking empty rather than inventing.
4. Do not start product work.

### Check (`/status-check`)

Read only. Do not edit the file.

1. If the file is missing, say so and tell the user to run `/status-init`. Stop.
2. Read STATUS. Then only the docs the Now item needs.
3. Brief in 4–6 lines: Now, Next (headlines), Blocked, Parking count.
4. Stale check: if `git log` has a commit after `Updated`, or the working tree
   has work that Last session does not mention, say **stale → run `/status-snap`**.
5. Do not start the Now item unless the user also said to continue.

### Snap (`/status-snap`)

Mid-session save. Rewrite the file. Do not append. Do not close the session.

1. If the file is missing, say so and tell the user to run `/status-init`. Stop.
2. Set `Updated` to today.
3. Adjust Now only if that item is actually finished; then promote the first Next
   (or `none`).
4. Replace Last session with what landed and what did not since the previous
   `Updated` (git log + working tree + this conversation).
5. Park new thoughts. Do **not** prune Parking for age (that is end).
6. Do not clear a claim. Do not treat the session as over. Do not keep
   implementing unless the user asked for more work in the same turn.

### End (`/status-end`)

Formal close. Rewrite the file. Do not append.

1. If the file is missing, say so and tell the user to run `/status-init`. Stop.
2. Set `Updated` to today.
3. Move a finished Now off. Promote the first Next, or write `none`.
4. Keep Next at 3–7 ordered items.
5. Replace Last session with what landed and what did not.
6. Park new thoughts. Delete a Parking item older than two weeks that is still
   vague.
7. Stop. Do not keep implementing.

## Rules

- One Now item.
- Overwrite, never append.
- Do not start Linear, GitHub issues, or a Projects board for this.
- Do not name a slash command `/status` (Grok built-in).
- These skills are user-scoped. They operate on whatever repo is the cwd.
  They do not live in the target repo.
