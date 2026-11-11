# Phase page

The "where are we" view: one LAN page with the roadmap, the current phase and its slices, the
infra as it is and as planned, and the open decisions. `teach` uses it when the ask is about the
plan (SKILL.md §0). It is read-only. It never ticks a box, moves a slice, or edits a phase doc.
That is `/phase`.

## Contents

- [1. Read the plan](#1-read-the-plan)
- [2. Read the infra](#2-read-the-infra)
- [3. Build the page](#3-build-the-page)
- [4. Reply](#4-reply)
- [Sources and limits](#sources-and-limits)

## 1. Read the plan

Read in this order. Stop at what is missing, and say so on the page and in the reply.

1. `docs/plans/BOARD.md`. Missing → no board. Say "No phase board here. Run `/phase init`." Then
   teach the infra only, if the ask allows it, and stop the phase part.
2. `docs/plans/NOW.md`: the current phase, the slice in focus, and Blocked. When NOW and BOARD
   disagree, BOARD wins (the unique `in progress` row). Note the disagreement on the page.
3. The current phase doc, from the board's `Doc` link: `docs/phases/<id>.md`, or
   `docs/plans/mvp/*.md` where the repo keeps them. Read only this one phase doc in full. For the
   other board rows, use the row itself (name, status, note).
4. ADRs and `DECISIONS.md`, but only the ones that the phase doc links or names, and only their
   titles and status.
5. `git log --oneline -15` and `git status --short`, to see what landed after NOW's `Updated`
   date. A commit after that date, or a checkbox that disagrees with git, means the board is
   stale. Say so, and suggest `/phase sync`. Do not fix it.

**Slices come in two shapes.** Read both:

- Template shape: a `## Slices` list of `- [ ] Slice N: ...` lines.
- Numbered shape: `### N.M <name>` headings, each with its own checkbox list. Each heading is a
  slice. A slice is done when all of its boxes are ticked, in progress when some are, and next
  when none are.

**Open decisions** come from the phase doc's `## Open decisions` section. Each line gives the
question, the options, and what it blocks. When the section is missing, look for unticked items
that start with "Decide", "Choose", or "TBD", and lines marked `?` or "open question". Label those
"found in the text", not "recorded". Never invent a decision.

## 2. Read the infra

Run `../scripts/infra-inventory.py <repo-root>` (relative to this file, resolved with
`readlink -f`). Then follow `../../serve-page/references/infra-diagrams.md` to draw it.

Mark each part with one state:

- **built**: in the inventory today.
- **building**: the current slice adds or changes it. Quote the slice line that says so.
- **planned**: a later slice in this phase, or a later board row, adds it.
- **removed**: a slice deletes it.

A part that a slice touches but the inventory cannot see (a host process, a table inside a
database, an external API) is still a part. Draw it from the phase doc's text, and cite the line.

## 3. Build the page

Follow `../../serve-page/SKILL.md` §1 to §4, with the dynamic-page rules in its
`references/page-rules.md`. Write `<scratchpad>/teach/<repo>-phase/index.html`.

**Header**: the repo, today's date, the current phase and slice, a stale warning when §1 found
one, and the legend (built, building, planned, decision).

**Tabs**, in this order:

1. **Now** (`#now`): three lines and one figure. The phase goal in one sentence. The slice in
   focus and its progress (`3 of 5 items`). Blocked, or "nothing blocked". The figure is the
   slice flow from the Phase tab, scaled down. Then the open-decision count, which links to the
   Decisions tab.
2. **Roadmap** (`#roadmap`): the board rows as a horizontal timeline. Done rows in the
   muted colour, the in-progress row in the accent colour with a "you are here" marker, shaped
   rows dashed, Later rows grey at the end. Under it, the close log as a short list.
3. **Phase** (`#phase`): the slices as a left-to-right flow of boxes (done, current, next), each
   with its tick count. Click a slice to expand its checklist below the flow (a `<details>` per
   slice). Beside the flow, the Definition of Done as a checklist and the appetite's no-gos.
   Each slice box carries `data-links` with the ids of the infra parts it touches.
4. **Infra** (`#infra`): the overlay diagram, with layer toggles for built, building, planned,
   and decisions. Under it, a stepper that teaches the system one lane at a time (the frame
   series from SKILL.md §5), ending with the overlay.
5. **Decisions** (`#decisions`): one card per open decision: the question, each option with what
   it changes in the diagram, what it blocks, and where it is recorded. Each card carries
   `data-links` with the parts it affects, and its diagram diamond has the same number. Below the
   open cards, the decisions this phase already settled, one line each, linking the ADR.

When a tab has nothing to show, keep the tab and say why in one line ("No open decisions are
recorded in this phase doc").

## 4. Reply

The reply holds what the page holds, short:

- Where you are: phase, slice, and progress, in one or two sentences.
- What the current slice changes in the infra, in plain words.
- The open decisions, one line each, with what each one blocks.
- The URL and the full path (serve-page §3).
- When stale: "The board looks stale. Run `/phase sync`."

Then the usual offer to go deeper. A good next step is often one decision: "Want me to teach the
options for D1?"

## Sources and limits

- The page never shows more than the files say. A slice's infra effect that the phase doc does
  not state is not drawn.
- Phase docs and the board are gitignored in most repos. Read them from disk, not from git.
- The page shows hostnames and container names, and often internal IPs. Add the sensitive-page
  warning.
