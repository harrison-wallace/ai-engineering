# Phase board cheatsheet

`phase` keeps a long-horizon plan for the repo you are working in: `docs/plans/BOARD.md` (the
phases), `docs/plans/NOW.md` (the current slice), and `docs/phases/<id>.md` (goal, appetite,
checkboxes, and DoD). The skill is installed per user, like every other skill, and works on the
current repo. It is never copied into it. Do not name a command `/session` or `/status`, because
those are Grok built-ins.

## Commands

Run these from the repo you're working in — the skill reads and writes that
repo's `docs/`, never this one.

| Command | What it does |
|---|---|
| `/phase` | Read-only brief: phase, slice, blocked, next shaped row, dirty files. Never starts work. |
| `/phase init` | Once per repo: creates `NOW.md` + `BOARD.md`, migrates a leftover `SESSION.md`/`STATUS.md`, appends the two gitignore lines. |
| `/phase shape auth` | Writes `docs/phases/auth.md` from the template (goal, appetite, scope, DoD) and adds a `shaped` board row. |
| `/phase sync` | Rewrites `NOW.md` and ticks the checkboxes that actually landed, from git + this chat. Does not close anything. |
| `/phase advance slice` | Ticks the current slice and moves `NOW.md` to the next one. Bare `/phase advance` does the same. Never closes a phase. |
| `/phase advance phase` | Closes the phase if its DoD is met: row `done`, log line, next `shaped` row into `in progress`. Otherwise lists what is left. |
| `/phase map` | Writes `docs/plans/map.json` (the infra parts and edges, linked to slices and decisions) and renders the live board. |
| `/phase prune` | Proposes archiving duplicate/superseded/orphan docs. Waits for confirmation, file by file. |
| `/phase help` | Prints the modes table. |

A phase from start to finish:

```
cd ~/git/my-app
/phase init                  # first time only
/phase shape onboarding      # → docs/phases/onboarding.md, board row `shaped`
                             #   edit the doc: slices as checkboxes, DoD at the bottom
… build the first slice …
/phase sync                  # ticks what landed, NOW points at the next slice
/phase advance slice         # slice done → tick it, move NOW on
… build the rest …
/phase advance phase         # phase DoD met → row `done`, log line, next phase in
```

Day to day:

```
/phase                       # new chat, no idea where you were → read the brief
/phase and continue          # brief, then actually start the slice
/phase sync                  # end of a working block, before closing the chat
```

Things worth knowing:

- **`NOW.md` is not the plan.** It holds one phase, one slice, one blocked line.
  Checkboxes and DoD live in the phase doc; the board holds the ordering.
- **`BOARD.md` wins.** If the two disagree, the unique `in progress` row is the
  truth and `sync` rewrites `NOW.md`.
- **Open decisions live in the phase doc**, under `## Open decisions`: the question, the options,
  and what it blocks. `/phase` shows the count, `sync` drops the ones that an ADR or
  `DECISIONS.md` settled, and `/teach where are we` draws them on the infra diagram.
- **`sync` never closes a phase** — that's `advance phase`, and only when the DoD is met.
- **Both trees are gitignored** by `init`, so the board is local scratch, not a
  commitment you've published. Unshaped ideas go in the board's Later section or
  a committed root `ROADMAP.md`.
- Old `/session-*` commands still route here: `session-init` → `init`,
  `session-check`/`session-start` → `status`, `session-snap`/`session-end` → `sync`.

## The live board

`/phase map` adds a picture of the infra to the plan. A script then renders one LAN page with
five tabs: Now, Roadmap, Phase, Infra, and Decisions. No model runs to render it. Click a slice or
a decision, and the map lights up the parts it touches.

```bash
S=~/.claude/skills/phase/scripts
$S/board-server.py add ~/git/my-app      # once per repo
$S/board-server.py serve                 # http://<lan-ip>:38090/my-app/
```

The server takes the first free port from 38090 to 38099, so several can run side by side. It
renders a board again when the phase docs, `map.json`, the infra files, or git HEAD change, and
open pages reload by themselves. `sync`, `advance`, and `shape` also update the map's states and
render the page, so the board is current even when no server runs.

To keep it up without a Claude session, install the systemd user unit:

```bash
$S/board-server.py unit > ~/.config/systemd/user/phase-board.service
systemctl --user daemon-reload && systemctl --user enable --now phase-board
loginctl enable-linger "$USER"
```

A Docker one-liner is in `skills/phase/references/map.md` §4. `map.json` sits in `docs/plans/`,
so it stays gitignored with the rest of the board. `/teach where are we` uses the same renderer
when a map exists.
