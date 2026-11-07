---
name: define-terms
description: Build and sharpen a project's domain language in GLOSSARY.md, and record short decision and rejection ADRs. `init` drafts a first glossary from the code, docs, and infra names, `<topic>` challenges fuzzy or clashing terms in one area with edge-case examples and checks them against the code, `check` reports drift between the glossary and the code (avoid-words still used, missing terms, dead terms), and `adr <decision>` writes a short ADR only when the decision is hard to reverse, surprising, and a real trade-off. At most 2 rounds of numbered questions with recommended answers. It writes only the rows you approve, and never commits. Triggers on "/define-terms", "/define-terms init", "/define-terms check", "start a glossary", "what do we call X", "is the glossary up to date", or "record this decision".
argument-hint: "[init | <topic> | check | adr <decision>]"
disable-model-invocation: true
---

# define-terms

Give the project one name for each domain concept, and write down the decisions a future reader
would otherwise undo. **It writes only the rows you approve. Never commit.**

This skill owns `GLOSSARY.md` (and `GLOSSARY-MAP.md`) and short decision ADRs. `design`
writes the long design ADRs. `check-architecture` reads the glossary to name its candidates,
and sends its new terms and rejected candidates here.

Adapted from Matt Pocock's `domain-modeling` skill.

## 1. Read the arguments

| Argument | Does |
|---|---|
| `init` | Draft a first glossary from the repo (§3) |
| `<topic>` | Sharpen the terms for one area or concept (§4) |
| `check` | Report drift between the glossary and the code (§5). Report-only |
| `adr <decision>` | Test the decision, then draft a short ADR (§6) |
| none | `check` when a glossary exists. Otherwise say there is none, and offer `init` |

From the user's words: "start a glossary" → `init`. "What do we call X" or "X or Y?" → `<topic>`.
"Is the glossary up to date" → `check`. "Record this decision" → `adr`.

## 2. Find the glossary and the ADRs

Run the bundled script from the repo root. It is read-only:

```bash
python3 -I <skill-dir>/scripts/glossary.py "$(git rev-parse --show-toplevel)"
```

It prints TSV: `glossary`, `term`, `avoid` (comma-separated). It exits 1 with `no glossary` when
there is none.

- **Single context**: one `GLOSSARY.md` at the root. This is most repos.
- **Several contexts**: `GLOSSARY-MAP.md` at the root links one `GLOSSARY.md` per context. Infer
  which context a topic belongs to. Ask only when it is unclear.
- **ADRs**: list `docs/adr/*.md` with each title and status. Read the ones the topic touches.

Follow [`references/glossary-format.md`](references/glossary-format.md) for every glossary edit.

## 3. `init`

If a glossary exists, say so in one line, run `check`, and offer `<topic>` for the gaps.

1. **Collect terms.** For a small repo (about 50 source files or fewer), do it yourself. Otherwise
   launch 2–3 Haiku explorers in **one message**: `subagent_type: Explore`, `model: haiku`,
   `run_in_background: false`, each with the full text of
   [`references/term-extractor-prompt.md`](references/term-extractor-prompt.md) and one angle:
   - **Code**: type and class names, database tables, enums, routes, events, and queue names.
   - **Words**: `README*`, `docs/`, ADRs, UI text, and error messages.
   - **Infra**: compose services, Terraform resources and modules, hostnames, and stack names.
     Use this angle only when the repo has infra.
2. **Filter.** Keep only terms specific to this project. Drop general programming words, such as
   timeout, retry, handler, or cache, even when the code uses them often.
3. **Find the problems.** One word for two meanings ("account" for both the Customer and the User).
   Two words for one meaning ("booking" and "reservation"). A term the docs use that the code calls
   something else.
4. **Ask** one round (§7). A second round only when the answers open new clashes.
5. **Propose** the glossary as rows (§8), then write the approved rows.

## 4. `<topic>`

Read the glossary terms for the topic, and the code that implements it.

- **Challenge clashes.** "The glossary defines Cancellation as X, but this code means Y. Which is
  it?"
- **Sharpen fuzzy terms.** "You say 'account'. Do you mean the Customer or the User?"
- **Test with examples.** Write two or three concrete edge cases that force a precise line between
  concepts, for example "a Booking is half paid and the Guest cancels one night".
- **Check the code.** When the user says how something works, check that the code agrees, with
  `file:line`. Say so when it does not: "Your code cancels whole Orders, but you said partial
  cancellation is possible."

Finding facts is your job. Look them up. Do not ask the user for anything you can read. The
decisions are the user's. At most 2 rounds (§7). Then propose rows (§8). When a decision in the
session passes the three tests in §6, offer an ADR.

## 5. `check`

Report-only. No glossary → say so and offer `init`.

| Drift | How to find it |
|---|---|
| **Avoid-word used** | `rg -n -w -i '<word>'` for each avoid-word, over code and docs. Skip `GLOSSARY*.md`, `CHANGELOG.md`, `archive/`, ADRs, and vendored folders. Skip an avoid-word that is a glossary term or part of one (`task` when **AI task** exists). It would match the right uses too |
| **Bad avoid-word** | An avoid-word with a note in brackets, such as "task (by itself)". Do not search for it. Report it as a glossary format problem, and propose the rewrite in `references/glossary-format.md` |
| **Bare-word rule** | A definition that says "never bare 'channel'". Count the hits, read the first 5, and report them as leads to read, not as drift |
| **Dead term** | `rg -n -w -i '<term>'` finds the term only in glossaries and ADRs |
| **Missing term** | A domain noun in type names, tables, routes, or the README in 3 or more places, with no glossary entry. Use the Code angle of §3 step 1, inline |

```markdown
**<n> drift items in <m> glossaries.**

| # | Kind | Term | Where | Suggestion |
|---|---|---|---|---|
| 1 | Avoid-word used | `reservation` (use **Booking**) | `src/api/routes.ts:42` | Rename in code, or add as a separate term |
```

At most 20 rows. Then `<n> more rows omitted.` Never edit code from `check`. Renaming code is a
change for the user to plan. End with: *"Run `/define-terms <topic>` to settle any of
these?"*

## 6. `adr <decision>`

Offer or write an ADR only when **all three** are true:

1. **Hard to reverse**: changing your mind later costs real work.
2. **Surprising without context**: a future reader would ask "why did they do it this way?"
3. **A real trade-off**: there were real alternatives, and this one won for stated reasons.

If any test fails, name the test, say why, and stop. A rejected candidate from
`check-architecture` is a decision too ("we will not merge X and Y, because Z"), with
status `rejected`.

Draft it in [`references/adr-format.md`](references/adr-format.md). Show the draft and its file
name, and write it after the user approves.

## 7. Questions

One round asks every question whose answer does not depend on another open question. Number each
one, and give your recommended answer. Word it so "yes" accepts the recommendation:

```markdown
**Q1. <Title>**: <the question, with the options when there are some>.
→ Recommended: <the answer, and why in one sentence>.
```

- At most 8 questions in a round, and at most 2 rounds per run.
- After round 2, list what is still open under **Not settled**, and stop asking.
- Use the STE rules and the clear-reading checks in `../summarise/SKILL.md` §3 (relative to
  this skill's folder, resolved with `readlink -f`).

## 8. Approve, then write

Show the changes as numbered rows:

```markdown
| # | Do | File | Term | Text |
|---|---|---|---|---|
| 1 | add | `GLOSSARY.md` | **Booking** | A confirmed reservation of one or more nights for one Guest. _Avoid_: reservation, order |
| 2 | sharpen | `GLOSSARY.md` | **Guest** | … |
```

`Do` is `add`, `sharpen`, `rename`, `remove`, or `adr`.

**Over 15 rows**, a wide table renders badly in a terminal. Print a numbered list instead, under one
heading for each file and group, with the action only when it is not `add`:

```markdown
### `packages/core/GLOSSARY.md` › Request and access
12. **User**: A person who logs in. A user is an admin or a member. _Avoid_: account
13. (sharpen) **Owner**: …
```

**At most 30 rows** in one approval. When a run has more, split it by context or by group, and ask
for each batch in turn. Number the rows straight through, and give the count correctly.

Ask: *"Reply with the numbers to apply, `all`, or changes."* Then:

- Apply only the approved rows, with the Edit tool. Create `GLOSSARY.md`, `GLOSSARY-MAP.md`, or
  `docs/adr/` only when an approved row needs it.
- Report the files changed. Never commit, stage, or push.

## Rules

- Write only approved rows. Never edit code.
- `GLOSSARY.md` holds domain terms only. No implementation details, plans, or decisions. A
  decision goes in an ADR.
- Never rewrite an accepted ADR. A new decision supersedes it: a new ADR, plus a
  `superseded by NNNN` status line on the old one, as an approved row.
- Never invent a term's meaning. Take it from the user, the docs, or the code, and cite it.
- A finding outside the glossary, such as a port that differs between two files, gets one line
  with the skill that owns it, for example `/update-docs repo`. Do not chase it.
