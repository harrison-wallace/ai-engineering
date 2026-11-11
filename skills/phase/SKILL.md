---
name: phase
description: Long-horizon phase board for the cwd repo. BOARD.md tracks phases, NOW.md points at the current slice, phase docs hold checkboxes and DoD. Modes: status (default), init, sync, shape, advance slice|phase, map, prune, help. `map` writes docs/plans/map.json, the infra picture behind a live LAN board that re-renders as the plan changes. Use when the user runs /phase, asks where we are on the plan, or names BOARD.md / NOW.md. Replaces session-* / SESSION.md.
user-invocable: true
argument-hint: "[status|init|sync|shape|advance [slice|phase]|map|prune|help]"
---

# phase

A repo-local board that survives a new chat or a tool switch. Chat memory and
in-session todos do not.

Templates: [NOW.template.md](NOW.template.md), [BOARD.template.md](BOARD.template.md),
[PHASE.template.md](PHASE.template.md).

The board is the tracker. `NOW.md` is not the plan. Checkboxes stay in the phase
doc. Do not invent a sitting file.

This skill is user-scoped. It operates on the cwd repo. It is not copied into it.
Do not name a command `/session` or `/status` (Grok built-ins).
Do not start Linear, GitHub issues, or a Projects board for this.

## Modes

| Mode | Job |
|---|---|
| `status` (default) | Read-only brief from NOW + current phase + git. |
| `init` | Once: `NOW.md`, `BOARD.md`, dirs, gitignore the two trees. Migrate `SESSION.md` / `STATUS.md`. |
| `sync` | Rewrite NOW and the active phase checkboxes from git + this chat. Does not close a phase. |
| `shape` | Write or sharpen the next phase doc. Board row → `shaped`. |
| `advance slice` | Close the current slice. Bare `advance` means this. Never closes a phase. |
| `advance phase` | Close the phase when its DoD is met. Pull the next `shaped` row in. |
| `map` | Write or refresh `docs/plans/map.json` (infra parts, edges, slice and decision links), then render the live board. |
| `prune` | Propose archive of done/superseded docs. Confirm each. |
| `help` | Print this table. One line: the board is the tracker; NOW is not the plan. |

Parse the first mode word after `/phase` or `phase`. Bare `/phase` is `status`.
Old names: `session-init` → `init`; `session-check` / `session-start` → `status`;
`session-snap` / `session-end` → `sync`; `session-prune` → `prune`;
`session-help` → `help`. Say the new name once. `session-end` does not close a
phase; that is `advance phase`.

When you suggest the next command, write the full form: `/phase advance slice`
when the current slice's items are all ticked, `/phase advance phase` when the
phase DoD looks met. Never suggest bare `/phase advance`.

## Paths

| File | Owns |
|---|---|
| `docs/plans/NOW.md` | Current phase id + path, the one slice in focus, one-line blocked, `Updated`, and optionally one `Parallel:` line |
| `docs/plans/BOARD.md` | Ordered phase rows, status, doc link, close log |
| `docs/phases/<id>.md` | Goal, appetite, checkboxes, DoD, deferred |
| `docs/plans/map.json` | Optional. Infra parts and edges, and their links to slices and decisions. Never the plan itself |
| `docs/plans/mvp/*.md` | Phase docs if that is where the repo already keeps them |

If NOW and BOARD disagree, BOARD wins (the unique `in progress` row). Rewrite NOW.

Phase how / DoD / checkboxes never live on the board. Locked choices live in
`DECISIONS.md` or ADRs. Unshaped work is Later on the board, or a committed
root `ROADMAP.md` (outside these trees). Git + the close log are history.
Do not write landed/did-not, Parking, or dirty-file lists into NOW.

At most one `in progress` row. Next is the first `shaped` row after it.
A side track that runs beside the current phase goes on NOW's optional `Parallel: <id> — <one line>`
line. Its row may stay `shaped`. `status` names it, `sync` ticks its checkboxes too, and the board
draws its slices.

Appetite is a stop condition on the phase doc: DoD, slice count, no-gos.
Do not put days, weeks, or sprints on the board or in a phase doc.

Create `docs/plans/` and `docs/phases/` as needed. Do not create `archive/`
until prune applies an archive. Skip `archive/` on reads.

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

## Init

1. If `docs/plans/BOARD.md` already exists, say so. Do not overwrite BOARD or
   NOW. Still migrate leftover `SESSION.md` / `STATUS.md` as below, ensure the
   gitignore lines, then tell the user to run `/phase status`. Stop.
2. Migrate, then delete the leftover (never keep two pointer files):
   - `docs/plans/SESSION.md` or `docs/plans/STATUS.md`
   - repo-root `SESSION.md` or `STATUS.md`
   Create NOW from the template if it is missing. Copy Milestone → `Phase`,
   Now → `Slice`, Blocked → `Blocked`. Add one board row `in progress` only if
   BOARD has none and a phase is identifiable. Do not copy Last session,
   Parking, or Next.
3. Create `docs/plans/` and `docs/phases/` if needed. Write NOW and BOARD from
   the templates if they do not exist. Fill `Updated` (today). Leave the table
   empty rather than inventing rows, except the migrated in-progress row.
4. Append the two gitignore lines.
5. If a master plan already exists (`IMPLEMENTATION-PLAN.md`, `PROGRESS.md`,
   `PLAN.md` at repo root or under `docs/`), name the path. Do not copy it into
   BOARD. Do not start product work.

## Status

Read only.

1. If BOARD is missing, tell the user to run `/phase init`. Stop.
2. Read NOW (if present), then BOARD, then **only** the current phase doc, then
   last ~10 commits and the dirty tree. Do not read `archive/` or every phase
   doc. Do not treat `ROADMAP.md` as Next.
3. Brief in a few lines: Phase, Slice, Blocked, open decisions (the count from
   the phase doc's `## Open decisions`, with their ids), next `shaped` row (or
   `none`). Mention dirty files in the **reply** only.
4. Stale: commits after NOW `Updated`, or checkboxes that disagree with git →
   **stale → run `/phase sync`**. Two `in progress` rows → say so; do not pick.
5. Do not start the slice unless the user also said to continue.
6. End with one line: the live board URL when `scripts/board-server.py list` shows this repo and
   a running server. Otherwise: *"Reply `page` for the board on your LAN."* When the user replies
   `page`, run `scripts/render-board.py <repo> <scratchpad>/phase/<repo>`, then serve that folder
   with `../serve-page/SKILL.md` §3 (relative to this skill's folder, resolved with `readlink -f`).
   Without `map.json` the Infra tab says to run `/phase map`. Stop the server when the user says
   they are done. For a live board that stays up, point to [references/map.md](references/map.md) §4.

## Sync

Rewrite NOW and the active phase checkboxes. Do not append. Do not close a phase.

1. If BOARD is missing, tell the user to run `/phase init`. Stop.
2. Set NOW and BOARD `Updated` to today.
3. Tick checkboxes that actually landed (git + this conversation). Do not tick
   the rest. Adjust NOW `Slice` to the first remaining unchecked slice (or
   `none`). Refresh NOW `Blocked` and the in-progress board `Note`.
   In `## Open decisions`, add a decision this chat raised and left open, and
   delete one that an ADR, `DECISIONS.md`, or this chat settled. Say where it
   was recorded. If it was settled but not recorded, keep the line and say so.
   Before you keep or list an open decision (here, in `status`, or on a page), check the board
   log, every phase doc's `## Decisions`, and the ADRs for an owner decision dated after it. A
   later decision settles it, even when an unticked item still says "the owner decides". When
   that decision contradicts an unticked item or the DoD of the current phase, report the
   conflict and suggest `/phase shape`. Do not leave the item blocked.
4. Do not change a row's status to `done` (that is `advance phase`). Do not
   append the log. Do not prune Later. Do not keep implementing unless the user asked.
5. Refresh the map ([references/map.md](references/map.md) §3).

## Shape

Write or sharpen a phase doc. Do not implement.

1. If the id or name is missing, ask. Default path: `docs/phases/<slug>.md`.
   If the repo already keeps phase docs only under `docs/plans/mvp/`, write
   the next one there.
2. If that file exists, sharpen in place. Do not overwrite a filled DoD with
   the empty template.
3. New file: write from [PHASE.template.md](PHASE.template.md). Fill Goal,
   Appetite, In/Out of scope, and Open decisions from what the user already said. Leave empty
   slices rather than inventing a full breakdown. If the file is not under
   `docs/phases/`, fix the `Board:` relative link.
4. Add or flip the board row to `shaped`. Do not set `in progress` unless
   nothing is in progress **and** the user asked to start it.
5. Do not tick checkboxes. Do not start product work.
6. Refresh the map ([references/map.md](references/map.md) §3).

## Advance

Close work whose DoD is met. Do not invent remaining work as done. The second
word picks the target: `slice` (default) or `phase`. Bare `advance` is
`advance slice`. Do not infer `phase` from a bare `advance`.

1. If BOARD is missing, tell the user to run `/phase init`. Stop.

### `advance slice`

2. If every item of the **current slice** is ticked, or the user confirms the
   rest are done: tick the slice, point NOW at the next unchecked slice (or
   `none`). Optionally append one log line for the slice. Board status stays
   `in progress`. Do not close the phase, even if this was the last slice.
3. Else list what is left in the slice. Do not write.
4. If no unchecked slice is left, say so and suggest `/phase advance phase`.

### `advance phase`

5. If the **phase** DoD is met (deferred items do not block): set the row to
   `done`, flip a **Status:** line on the phase doc if present, append one log
   line (`YYYY-MM-DD`, phase id, version if any), pull the next `shaped` row
   into `in progress` (or `none`). Rewrite NOW to that phase's first unchecked
   slice, or `Phase: none`.
6. Else list the DoD lines that are not met. Do not write.

7. After a write in step 2 or 5, refresh the map ([references/map.md](references/map.md) §3).
8. Stop. Do not keep implementing.

## Map

Write or refresh `docs/plans/map.json`, and render the board. Follow
[references/map.md](references/map.md) §1. Do not edit NOW, BOARD, or a phase doc here. When a doc
and the code disagree, draw the code, and say so in the reply. Reply with the parts count, the
links count, the board URL (or the setup line from §4), and the parts you could not place.

## Prune

Tidy the two trees so status stays cheap. Do not edit NOW or BOARD except to
fix a `Doc` path or `in progress` row whose file was archived.

1. List `docs/plans/` and `docs/phases/` (and `docs/plans/mvp/` if present).
2. Flag: duplicate, superseded, orphan (not on the board), huge, leftover
   sitting files (`SESSION.md`, `archive/sittings.md`), or `ROADMAP.md` under
   `docs/plans/` (Later belongs on the board or at repo-root `ROADMAP.md`).
3. Propose **archive** to `docs/plans/archive/` or `docs/phases/archive/` plus
   a one-line pointer on the board or in `docs/phases/README.md` if that index
   exists. Do not delete. Do not merge two phase docs. Do not rewrite a DoD.
   Do not tick checkboxes. Do not touch files outside those trees.
4. **Wait.** Apply only what the user confirms, file by file.

## Help

Print the Modes table. One line: the board is the tracker; NOW is not the plan.
Stop. No edits.
