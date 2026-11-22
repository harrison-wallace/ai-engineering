# Status and sync reports

The user runs `status` or `sync` after a gap, or at the end of a long session. The report gets
them back into the work: where they are, what happened, what needs them, and what is next. Take
every count from `scripts/progress.py <repo>`. Never estimate a count.

## Contents

- [Wording](#wording)
- [Status](#status)
- [Sync](#sync)
- [Waiting on you](#waiting-on-you)
- [Decisions](#decisions)
- [NOW.md stays short](#nowmd-stays-short)

## Wording

- **An id always has its name**: "P3 · MVP on AWS", "slice 2, Runner and sandbox", "D14 Lambda
  limit". Never a bare "PF Slice 5" or "D1 to D5".
- **No skill words in a reply.** Say "planned" for `shaped`, "now" for `in progress`, "running
  beside it" for a `Parallel:` side track, "done when" for DoD, and "the board" or "the phase
  doc" for BOARD.md, NOW.md, and section names. Never explain how the skill works.
- **One idea a line, about 20 words.** Commit hashes, case numbers, ARNs, and long paths stay in
  the docs. Give a `path:line` link to the detail instead.
- **Say what changed, not what you checked.** A check that found nothing is not a line.
- **End with exactly one next step**: a full command (`/phase advance slice`), or the words the
  user can say ("test production").

## Status

Print the sections in this order. Leave out a section with nothing in it.

```markdown
## <Repo> · <phase id> <phase name>
**Goal:** <the phase goal, one sentence>

<bar>  Slice <key>, <name>: <n> of <m> items done
Last sync <date> · last commit <date> · <"the board matches the code" | "stale: run /phase sync">

**Since you were last here**
- <up to 3 bullets: what landed in the last working stretch, from the recent commits and the
  board log, in plain words, with the date>

**Waiting on you: <n> tasks, <what they block>**
<one block per task or decision that needs the user now: see Waiting on you>

**Open decisions: <n>, <"none blocks this phase" | "<k> block this phase">**
<the table in Decisions, then the detail link>

**Then**
- **I do next:** <the first open item of the slice, in plain words>
- **Running beside it:** <side track: id, name, its state, what closes it>
- **After this phase:** <next planned phase: id, name, and what it makes true>

<n> files are not committed.
→ <one next step>
```

- **The bar**: copy the `bar:` line from `progress.py`. ■ is done, ▣ is now, □ is to do.
- **Since you were last here**: show it in the first status of a chat, or when commits landed
  after the last sync. Leave it out when status already ran in this chat and nothing changed.
- **Two phases are in progress**: say so on the second line, and do not pick one.
- **Every slice ticked**: put "every slice is done" on the bar line. The next step is
  `/phase advance phase` when the done-when list looks met. Otherwise, name the unmet lines.

## Sync

```markdown
## Synced · <phase id> <phase name>
<bar>  Slice <key>, <name>: <n> of <m> items done

**This session did**
- <up to 3 bullets, for a long session or one with commits: what the work made true>

**Board changes**
- ✓ Ticked <n> items: <the ones that matter, a few words each>
- → Moved to slice <key>, <name>
- \+ New decision <id> <short name>: <"needs you before …" | "can wait until …">
- − Settled <id> <short name>: recorded in <ADR | DECISIONS.md | not yet recorded>
- NOW.md trimmed: <what moved, and where>

**Waiting on you**
<the same blocks as status>

→ <one next step>
```

When nothing changed, the whole report is one line: *"The board was already up to date. Nothing
changed since <date, time>."* Add a `Waiting on you` block only if something needs the user now.

## Waiting on you

A task only the user can do (a console step, a key, an approval, a release), or a decision that
blocks the current slice or phase, gets a full block. Take the owner tasks from NOW's `Blocked`
and from unticked items that name the owner.

```markdown
**<Task or question, in plain words>.** <one or two sentences of context: what it is and where it
came from>
1. <step>
2. <step>
- **Why now:** <what it unblocks, by name>
- **Options:** <a>, <its cost or effect>, or <b>, <its cost or effect>   (decisions only)
- **My pick:** <the pick>. <why, in one or two sentences: the trade-off, and how easy it is to undo>
- **Detail:** `<path>:<line>`
```

- Say **"The doc already recommends"** when the phase doc holds the pick (`progress.py` prints
  `doc recommends:`). Say **"My pick"** when it is yours. Always give the why.
- A pick needs evidence from the docs, the code, or this chat. When you have none, say what
  would settle it, and do not invent a pick.
- Order the blocks by what they unblock: the current slice first.

## Decisions

Open decisions that do not block this phase get one table row each:

```markdown
| | Question | Blocks | My pick | Why |
|---|---|---|---|---|
| D14 | <the question, short> | <phase or "nothing"> | <pick, or "wait"> | <one clause> |
```

Sort the rows by the urgency of the pick: "ask now" or "do now" first, then "wait". A decision the
user already parked shows "You parked it". Then link the section: `<doc>` § Open decisions.

## NOW.md stays short

`sync` rewrites NOW.md to these lines only:

- `Updated:` today.
- `Phase:` id, name, and the doc link.
- `Slice:` key and name, then "next:" and the first open item in at most 12 words.
- `Blocked:` one sentence. It names who or what, and the item it blocks. The detail goes into
  that item in the phase doc.
- `Parallel:` (optional) id, name, and what closes it, in one sentence.

Any other line (`Live:`, `Priorities:`, `Hosts:`, a long history) moves out. The phase's state
goes to the in-progress board row's `Note`, at most about 25 words. Facts that hold across phases
(hosts, the live version, owner priorities) go to the board's `## Notes` section, one short line
each; create it under the table when it is missing. Facts about a slice go into that
slice in the phase doc. Settled owner choices go to the phase doc's `## Decisions`. Say in the report what moved,
and where. Write the Note and the Notes lines with the same wording rules.
