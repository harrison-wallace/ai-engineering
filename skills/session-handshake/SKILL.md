---
name: session-handshake
description: Contract for the SESSION.md handshake (path, template, commands). Not a slash command. Invoked by /session-init, /session-start, /session-check, /session-snap, /session-end, /session-prune, and /session-help.
user-invocable: false
---

# session-handshake

A repo-local `docs/plans/SESSION.md` is the only queue that survives a new chat
or a tool switch. Chat memory and in-session todos do not.

This file is the contract. The slash skills run one mode each. Do not invent
another handshake file or a board.

Template: [SESSION.template.md](SESSION.template.md).

SESSION is not the plan. Phase docs, `DECISIONS.md`, and the master plan stay
the long-horizon files. Checkboxes stay in the phase doc.

## Commands

| Command | Job |
|---|---|
| `/session-init` | Once: empty `SESSION.md`, create dirs, gitignore the two trees, migrate `STATUS.md`. Then tell the user to run `/session-start`. |
| `/session-start` | Sit down: propose Now/Next from plans + phases + git. Write only after the user confirms (or named Now in the same message). |
| `/session-check` | Read-only brief. Flags stale → `/session-snap`. |
| `/session-snap` | Mid-sitting rewrite so SESSION matches git + this chat. Does not close. |
| `/session-end` | Formal close: promote Next, prune old Parking, stop. |
| `/session-prune` | Propose archive/index tidy of `docs/plans` and `docs/phases`. Confirm each. |
| `/session-help` | Print this table. |

Do not name a command `/session` or `/status` (Grok built-ins: `/sessions`, `/session-info`, `/status`).

## Path

Always `docs/plans/SESSION.md`. Create `docs/plans/` if it does not exist.

Migrate, then continue (never keep two handshake files):

- `docs/plans/STATUS.md` → `docs/plans/SESSION.md`
- repo-root `SESSION.md` or `STATUS.md` → `docs/plans/SESSION.md`

One file. Never both.

## What belongs where

| Kind | Where | Not in SESSION |
|---|---|---|
| This sitting's queue | SESSION Now / Next | — |
| Half-formed idea | SESSION Parking | A second `THOUGHTS.md` |
| Work just done | git + Last session | A running changelog |
| Locked choice | Decision log (`DECISIONS.md` or ADRs) | Reciting the decision |
| Phase how / DoD / checkboxes | `docs/phases/` (or `docs/plans/mvp/`) | A second checklist |
| Multi-month map | Master plan / `IMPLEMENTATION-PLAN.md` / `PROGRESS.md` | Copying the roadmap |
| Not scheduled | `ROADMAP.md` | Next |

## Gitignore (init)

Init **appends** these two lines to `.gitignore` if they are not already present
(match with or without a trailing slash):

```
docs/plans/
docs/phases/
```

Do not rewrite the rest of `.gitignore`. If either path is already tracked,
warn that gitignore will not hide it until the owner runs `git rm -r --cached`.
Do not run that command.

## Modes

### Init (`/session-init`)

1. Migrate any leftover handshake file as under Path. If that produced
   `docs/plans/SESSION.md`, stop and tell the user to run `/session-start`.
2. If `docs/plans/SESSION.md` already exists, say so and stop. Tell the user
   to run `/session-check` or `/session-start`. Do not overwrite.
3. Create `docs/plans/` if needed. Write the template. Fill `Updated` (today),
   `Milestone` (from the current in-progress phase or plan if obvious, else
   `none`), and **Now** (`none` unless the next action is obvious).
4. Leave Next / Blocked / Last session / Parking empty rather than inventing.
5. Append the two gitignore lines as under Gitignore.
6. Tell the user to run `/session-start`. Do not start product work.

### Start (`/session-start`)

Sit down and scope. Do not implement.

**Read (skip `archive/` and `ROADMAP.md` as Next):**

- `docs/plans/SESSION.md`
- other files in `docs/plans/` and `docs/phases/`
- `IMPLEMENTATION-PLAN.md`, `PROGRESS.md`, `PLAN.md`, `DECISIONS.md`,
  `AGENTS.md` at repo root or under `docs/` if present
- the current **in-progress** phase doc (🟡 / 🔨 / 🟦 / "in progress"), not
  the next empty one
- last ~10 commits and the dirty tree

**Propose** one Now and 3–7 Next, each with evidence ("from PHASE-6.md",
"dirty README"). Now is one slice, not a whole phase. Milestone is a pointer
to that phase (id + path).

If there is no plan and a clean tree, leave Now as `none` and say so.

If Now is already set, ask keep or replace. Do not silently overwrite.

**Write only after the user confirms**, or if they named the Now item in the
same message as `/session-start`. Then write Now, Next, `Updated`, and one
Last-session line: `Scoped. Dirty at start: <files or none>.` Do not rewrite
the rest of Last session (that is snap). Do not tick phase checkboxes.

### Check (`/session-check`)

Read only. Do not edit the file.

1. If `docs/plans/SESSION.md` is missing, say so and tell the user to run
   `/session-init`. Stop. (Init also migrates `STATUS.md`.)
2. Read SESSION. Then only the docs the Now item needs.
3. Brief in 4–6 lines: Now, Next (headlines), Blocked, Parking count.
4. Stale: commits after `Updated`, or dirty files **not** named in Last
   session → **stale → run `/session-snap`**. Dirty files already listed
   ("Dirty at start: …") are not stale by themselves.
5. Do not start the Now item unless the user also said to continue.

### Snap (`/session-snap`)

Mid-sitting save. Rewrite the file. Do not append. Do not close.

1. If `docs/plans/SESSION.md` is missing, say so and tell the user to run
   `/session-init`. Stop.
2. Set `Updated` to today.
3. Adjust Now only if that item is actually finished; then promote the first
   Next (or `none`).
4. Replace Last session with what landed and what did not since the previous
   `Updated` (git log + working tree + this conversation).
5. Park new thoughts. Do **not** prune Parking for age (that is end).
6. Do not treat the sitting as over. Do not keep implementing unless the user
   asked for more work in the same turn.

### End (`/session-end`)

Formal close. Rewrite the file. Do not append.

1. If `docs/plans/SESSION.md` is missing, say so and tell the user to run
   `/session-init`. Stop.
2. Set `Updated` to today.
3. Move a finished Now off. Promote the first Next, or write `none`.
4. Keep Next at 3–7 ordered items (so the next start is cheap).
5. Replace Last session with what landed and what did not.
6. Park new thoughts. Delete a Parking item older than two weeks that is
   still vague.
7. Stop. Do not keep implementing.

### Prune (`/session-prune`)

Tidy **inputs start reads**. Do not edit SESSION except to fix Milestone if
the current phase doc is archived.

1. List `docs/plans/` and `docs/phases/` (and `docs/plans/mvp/` if present).
2. Flag: duplicate, superseded, orphan (not in the phase index), huge, or
   "not scheduled" (`ROADMAP.md`).
3. Propose **archive** to `docs/plans/archive/` or `docs/phases/archive/` plus
   a one-line pointer in the index. Optionally refresh a short
   `docs/plans/INDEX.md` that start should read first.
4. **Wait.** Apply only what the user confirms, file by file.
5. Do not delete. Do not merge two phase docs. Do not rewrite a master plan
   or DoD. Do not tick checkboxes. Do not touch files outside those trees.

### Help (`/session-help`)

Print the Commands table. One line: SESSION is not the plan. Stop. No edits.

## Rules

- One Now item.
- Overwrite SESSION, never append.
- Do not start Linear, GitHub issues, or a Projects board for this.
- These skills are user-scoped. They operate on whatever repo is the cwd.
  They do not live in the target repo.
