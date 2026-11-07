---
name: basic-why
description: Find out why code or infrastructure is the way it is (a design choice, a threshold, a workaround, or a regression) from git history, GitHub PRs and issues, ADRs, phase docs, CHANGELOG, CLAUDE.md/AGENTS.md, and memory, and report each claim at a stated confidence (found, inferred, unknown) with a citation. Read-only. A Sonnet digger works the git and PR history. Before a change, it ends with a Preserve / Change / Avoid / Risk set. Triggers on "/basic-why", "why does X work this way", "why did we pick Y", "where did this number come from", or "is it safe to remove this". Optional leading level. Use basic-how for runtime behavior.
argument-hint: "[lite|deep] <question>"
disable-model-invocation: true
---

# basic-why

Find the forces that shaped a piece of code or infra, and say honestly how sure each finding is.
**Read-only. Never edit, apply, or start anything.**

`basic-how` says what the code does now. `basic-why` says why. `basic-teach` runs one or both and
turns the result into a plain explanation.

Inspired by the pstack `why` skill. Same confidence discipline, narrowed to the sources this setup
has, and run on cheaper models.

## Level

Read the first argument:

| First argument | Level | Git and PR digging | Synthesis |
|---|---|---|---|
| `lite` | lite | Main agent, inline | Main agent |
| none, or anything else | default | One Sonnet digger | Main agent |
| `deep` | deep | One Sonnet digger | One Opus synthesizer at `high`, in a fresh context. The main agent presents its answer |

`deep` puts the synthesis in a fresh context on purpose. The main agent has read the user's
framing and is the most likely to confirm it. Do not run `/effort` or `/model`. Set `model` and
`effort` on each Agent call only. Never go above Opus `high`.

Read [`references/epistemics.md`](references/epistemics.md) before you write the answer, at every
level.

## Sources

These, and only these:

| Source | Where |
|---|---|
| **Git history** | Commits, blame, pickaxe, renames, co-changed files, code comments, TODOs, and tests in the repo |
| **GitHub** | PR bodies, reviews, and comments, and linked issues, through `gh`. Only when the repo has a GitHub remote and `gh` is authenticated |
| **ADRs** | `docs/adr/` |
| **Phase docs** | `docs/plans/BOARD.md` (with its close log), `docs/plans/NOW.md`, `docs/phases/*.md`, `docs/plans/mvp/*.md`. They are often gitignored, so read the working tree |
| **CHANGELOG** | `CHANGELOG.md` and release notes in the repo |
| **Repo instructions** | `CLAUDE.md` and `AGENTS.md`, at the root and in subfolders |
| **Memory** | This project's memory folder, per the memory rules in the system prompt. `MEMORY.md` first, then the files that match |

Do not search Drive, Gmail, Claude Docs, Slack, or the web, even when they are connected. When the
answer probably lives in another repo in `~/git` (a shared network, a module, a contract), say so
under **What we don't know**, and name the repo.

## 1. Target and question

The **target** is a chunk of code, a resource, a pattern, a value, or a named decision. The
**question** is a rationale, a tradeoff, an edge case, an outside constraint, dead code, or a
history sweep.

If the target is vague, take your best reading from the conversation (recent edits, open files,
what was just discussed), state it in one line, and continue.

If the question carries a guess ("I assume it's for performance?"), write it down as one
hypothesis to test. Do not adopt it.

## 2. Anchor and in-repo sweep (main agent)

Build the **anchor**:

- File paths with line ranges, key symbols, or resource addresses.
- `git blame -L <start>,<end> <file>` for the last-touch commits.
- `git log --oneline -20 --follow -- <file>` for recent history with PR numbers.
- PR numbers from subjects (`(#123)`) and ticket or issue IDs from bodies.

Then sweep the in-repo docs yourself. It is cheap and it gives the digger leads:

- `rg -n -i '<symbol>|<value>|<topic>'` over `docs/adr/`, the phase docs, `CHANGELOG.md`, and every
  `CLAUDE.md`/`AGENTS.md`.
- Read each hit in full: the ADR, the phase doc section, the changelog entry.
- Read the memory index and the memory files that match.

**lite**: also do step 3 yourself, using the search list in
[`references/investigator-prompt.md`](references/investigator-prompt.md).

## 3. Dig the history (default and deep)

Launch one digger:

- `subagent_type`: `Explore`, `model`: `sonnet`, `effort`: `medium`,
  `run_in_background`: `false`.
- Prompt: the full text of
  [`references/investigator-prompt.md`](references/investigator-prompt.md), with the question,
  the anchor, the repo root, and the leads from your sweep filled in. Add its **Defensive code**
  section when the target looks defensive: null guards, retries, timeouts, rate limits, feature
  flags, `ignore_changes`, health checks, restart policies, or OOM limits.

## 4. Synthesize

**lite and default**: write the answer yourself, in the format of
[`references/synthesizer-prompt.md`](references/synthesizer-prompt.md).

**deep**: launch one synthesizer:

- `subagent_type`: `general-purpose`, `model`: `opus`, `effort`: `high`,
  `run_in_background`: `false`.
- Prompt: the full text of `references/synthesizer-prompt.md`, with the question, the anchor, the
  repo root, your sweep findings (with paths and quotes), the digger's report, and the path to
  `references/epistemics.md` filled in. Tell it that it is read-only and that it can spot-check
  citations with `git` and `gh`.

Present the answer. You may edit for clarity or add context from the conversation. **Do not change
the confidence language.**

## 5. Before a change

When the question comes before a change ("can I remove this", "I want to swap X for Y", or a plan
in this conversation), end with a constraint set:

| | Item | From |
|---|---|---|
| **Preserve** | What the evidence says must stay true | The finding, with its tier |
| **Change** | What the evidence says is free to change | The finding, with its tier |
| **Avoid** | Approaches the history shows were tried and failed, or rejected | The finding, with its tier |
| **Risk** | What nobody could confirm and could break | The gap |

Then offer the next step in one line:

- Risk rows that touch shared things (a contract, a network, state, a hostname, another repo) →
  `/basic-impact <the change>` to prove them.
- A change that reshapes the area → `/basic-architect <the change>`, with this table as grounding.

## Rules

- Read-only. Never commit, edit, or run commands with side effects. `gh` calls are reads only.
- Code shows mechanics, not motivation. Never cite code as evidence of its own intent.
- An honest "we don't know" is a valid answer. A confident guess is the failure this skill exists
  to prevent.
