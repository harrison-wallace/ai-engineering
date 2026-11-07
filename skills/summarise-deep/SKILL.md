---
name: summarise-deep
description: The deep version of summarise, with its core inputs (last, session, work, commit, pr, jira, and plain). It writes a technical report in plain prose that you can actually learn from. It covers what was built or said, how it works now (explain-how), why each decision was made and what was rejected, what was verified, and what is still risky. A Sonnet agent checks every claim against git and the transcript before you see it. Report-only, and it can save the report as Markdown or PDF in docs/summary/. Triggers on "/summarise-deep", "/summarise-deep session", "/summarise-deep work since main", "write me a proper handoff", "deep summary of this work", or "explain everything we did". Optional leading level. Use summarise for a quick scan.
argument-hint: "[lite] [last|session|work|commit|pr|jira] [since <ref> | last <n> | <sha> | <base>] [plain]"
disable-model-invocation: true
---

# summarise-deep

A deep technical summary, for when you want to understand the work and not only scan it.
**Report only. Do not continue the task, fix, commit, push, or open a PR.**

`summarise` is quick and high-level, in Simplified Technical English bullets. `summarise-deep`
takes the same core inputs and writes a longer report in plain technical prose. It has no
`management` input, because a manager wants the short version: use `/summarise management`. It explains the
mechanism, the reasons, the trade-offs, and what is still uncertain.

## Level

| First argument | Level | Subagents |
|---|---|---|
| `lite` | lite | None. The main agent writes it and checks its own claims against git |
| none, or anything else | default | The ones in §3 that apply, plus the claim check in §5 |

Do not run `/effort` or `/model`. Set `model` and `effort` on each Agent call only. Never go above
Sonnet.

## 1. Read the arguments

The arguments are the same as `summarise` §1. Read `../summarise/SKILL.md` (relative to
this skill's folder, resolved with `readlink -f`) and use its §1 and §2 for the inputs, scopes, and
sources. Strip a leading `lite` first.

| Input | Report |
|---|---|
| `last` (default) | The previous reply, explained in depth: each point with its mechanism, its reason, and what it implies |
| `session` | A handoff of this chat: each decision with who made it and why, the options rejected, what was built, what was parked and why, and what is open |
| `work [scope]` | A technical write-up of what landed, grouped by area |
| `commit` | A full commit message, or one per commit when the work should split, each with a body that gives the why |
| `pr [<base>]` | A long-form PR description for a big branch |
| `jira [scope]` | A full ticket write-up that colleagues can follow later, including how it works and the risks |
| `plain` | With any input: the same depth, written for a reader who is not technical, such as a client |

## 2. Collect (main agent)

Gather the input exactly as `summarise` §2 says. For `jira`, that is §2.6, with its order,
reasons, status, and ticket keys. Then add:

- **The decisions.** For `session`, `work`, `commit`, `pr`, and `jira`, list every choice made in this chat,
  with the user's answer quoted where there was one, and the options that were rejected.
- **What was verified.** List the tests, checks, and commands that actually ran in this session,
  with their results. Do not run tests now. A change with no check in the session is "not
  verified in this session".
- **Changed areas.** List the modules, skills, services, or stacks the work touched.

## 3. Fan out (default)

Launch the agents that apply in **one message**, with `run_in_background: false`:

| Agent | When | Call and prompt |
|---|---|---|
| **Decision reader** | `session`, or any input when this chat was compacted or is long (about 100 turns or more) | `Explore`, `model: sonnet`, `effort: medium`. Prompt: [`references/decision-reader-prompt.md`](references/decision-reader-prompt.md) |
| `explain-how` explorers | The work changed how something runs, across more than one module or service | Per `../explain-how/SKILL.md` §2. For a single module, read it yourself at `lite` |
| `explain-why` digger | The work undid or loosened an older decision: a deleted guard, a changed threshold, a removed test | Per `../explain-why/SKILL.md` §3, one narrow question each, at most 3 |

For the decision reader, find this session's transcript the same way `reflect` §1 does. Run
`../reflect/digest.sh <session.jsonl> > <scratchpad>/summarise-deep/digest.md` and give the
agent the digest path. If the transcript cannot be found, skip the agent and say so in the
coverage line.

`explain-how` and `explain-why` have `disable-model-invocation`. Read their files and follow them in
place. Do not call them with the Skill tool.

**lite**: run no subagents. Read the changed areas yourself, and take the decisions from the
conversation as you have it.

## 4. Write the draft

Write the draft to `<scratchpad>/summarise-deep/<slug>/draft.md` in the shape of §6, in the voice
of §7.

## 5. Check the claims

**default**: launch one claim checker. Use `Explore`, `model: sonnet`, `effort: medium`,
`run_in_background: false`, with [`references/claim-check-prompt.md`](references/claim-check-prompt.md),
the draft path, the digest path if there is one, and the repo root.

**lite**: check the claims yourself against `git status`, `git diff`, and `git log`.

For each claim the checker flags, fix the draft. Correct the claim, soften it to what the
evidence shows, or delete it. Never keep a claim that the checker refuted. When the checker and
the conversation disagree, the record (git, the transcript) wins. Say so in the report.

## 6. Report

Print the report in the terminal. Leave out a section that is empty. The first section must read
in 30 seconds.

### `work` and `pr`

```markdown
# <What this work is, as a short noun phrase>

## Overview
Three to five sentences: the problem, what was done, and the state it is in now.

## What changed
Grouped by area. For each area, a short paragraph and the real names (files, skills, commands)
in code font.

## How it works now
From `explain-how`. The mechanism, in prose. An ASCII diagram, before and after, when a flow changed.

## Why it was done this way
Each decision, with the reason, and the user's answer where there was one. Keep `explain-why`'s
confidence words as they are.

## Trade-offs and rejected options
What was weighed, what lost, and why. Say what you make of the trade-off.

## Verification
What ran and the result. "Not verified in this session" for the rest.

## Risks and open questions
What could still go wrong, what nobody confirmed, and what is waiting on a decision.
```

For `pr`, put a title line of 72 characters or fewer first. Use the repo's PR template headings
when it has one, and fit these sections under them.

### `session`

The same shape. Rename **What changed** to **What was built**, and add **Decided** (each choice,
who made it, and why) and **Parked** (each item, and the reason it was left) after the overview.
End with **Open**: questions not answered, uncommitted work, and the next step waiting on the user.

### `last`

Follow the order of the previous reply. For each of its points, write a short section with the
point, the mechanism behind it, the reason for it, and what it means for the user. End with
**Open questions** if the reply left any.

### `jira`

Follow `../summarise/references/jira-markdown.md`, so that the text pastes into Jira with no
editing. Print it in one fenced block. Use `summarise`'s `jira` sections in the same order, with
two more after **Why**:

- **How it works now**: from `explain-how`, in two to five sentences of prose. No diagram, because a
  diagram needs a code block and the paste rules forbid one.
- **Risks and open questions**: what could still go wrong, and what nobody confirmed.

Write **What we did** as numbered steps in the order the work happened, each with one or two
sentences of detail. Keep it to about 600 words.

### `commit`

Use `summarise`'s commit format and split rules. Give each body three short parts: **Why**
(the problem), **What** (the change, by area), and **Notes** (trade-offs, verification, follow-ups).
Wrap at 72 characters. Keep each message under about 30 lines. Print the `git` order for a split
as text for the user. Do not run it.

### After the report

Add a coverage line: the input and scope, the subagents that ran, and the number of claims the
checker corrected.

Then offer in one line: *"Save this as Markdown or PDF in `docs/summary/`? Or `/teach` any
part of it."*

## 7. Voice

Write plain technical prose for an engineer, like a senior engineer's handoff note.

- Longer sentences are fine when they carry one thought with its condition or consequence. Split a
  sentence that carries two. Mix lengths, so that the text does not read as if a machine wrote it.
- Paragraphs, not bullet stacks. Use bullets only for real lists, and tables only for real
  comparisons.
- Use the real name of each file, command, flag, or skill, in code font. Give each concept one
  name and keep it.
- Be specific. Write "removing a skill makes the next release 2.0.0", not "this has versioning
  implications".
- Have a view in **Trade-offs** and **Risks**. Stay factual everywhere else.
- Keep the clear-reading checks from `summarise` §3: each pronoun points at one thing, "only"
  and "not" sit next to their word, no slashes, semicolons, or em dashes, and no long noun strings.
  The 20-word limit does not apply.
- With `plain`: no jargon. Explain each technical term in the same sentence the first time it
  appears. Say what changed for the reader, not how it was built. Leave out hashes and paths unless
  the reader needs one to act.

## 8. Save (only when the user asks)

- **Markdown**: write `docs/summary/YYYY-MM-DD-<input>-<slug>.md` in the current repo. Create the
  folder if needed. Add no frontmatter. The first line is the `#` title.
- **PDF**: write the Markdown file first, then run `scripts/md-to-pdf.sh <file.md>`. It writes the
  PDF next to the Markdown file and prints its path. It needs the Python `markdown` package and
  Chrome or Chromium. If it fails, say why and keep the Markdown file.
- Do not commit or stage the files. Do not change `.gitignore`. Say once that `docs/summary/` is
  not ignored, if that is true, so the user can decide.

## Rules

- Report only, apart from the files in §8 when the user asks for them.
- Do not run tests or checks to fill **Verification**. Report what ran in the session.
- Never invent a decision, a test result, or a reason. A claim with no evidence moves to **Risks and
  open questions**, or it goes.
- Do not write `BOARD.md`, `NOW.md`, `CHANGELOG.md`, or a phase doc.
