---
name: summarise-work
description: Bullet wrap-up of the current sitting as Achieved / Fixed / Implemented plus a short executive summary. Use at the end of a block of work, or when asked what landed. Triggers on "/summarise-work", "summarise the work", "summarize the work", "what did we do". Report-only.
user-invocable: true
---

# summarise-work

A short wrap-up of what actually landed. Not a changelog, not a status board,
not a plan for next.

## 1. Collect

Default scope is **this sitting**: the current conversation plus the working tree.

```bash
git status --short
git diff HEAD --stat
git log -8 --oneline
```

Then read the diffs that matter (`git diff HEAD`). If the tree is clean, use the
last commit (`git diff HEAD~1..HEAD`) and say so.

Overrides — only if the user named one:

| They said | Scope |
|---|---|
| `since main` / `since vX.Y.Z` / a SHA | That range, git only |
| `last N commits` | Those commits, git only |
| `this sitting` / bare `/summarise-work` | Conversation + working tree (default) |

If there is no git repo, summarise the conversation only and say so.

Do not invent work that is not in the diff or this chat. Plans, suggestions,
and "we should" items are out.

## 2. Classify

Put each item in **exactly one** bucket. Most specific wins:

| Bucket | When | Not |
|---|---|---|
| **Fixed** | Something existed and was wrong; it is now correct | New work that happens to prevent a future bug |
| **Implemented** | New capability, code, skill, or docs that did not exist before this work | A one-line tweak to something that already existed (Fixed if it was broken, else Achieved or skip) |
| **Achieved** | An outcome that is not a new artefact and not a bugfix: a decision, investigation, migration, verification, DoD met, end-to-end "it works" | A restatement of an Implemented or Fixed bullet |

Omit a heading if that bucket is empty. Do not pad.

Merge related file changes into **one** bullet. Prefer 3–7 bullets across all
buckets. Never more than 8 in one bucket — merge harder.

Drop: test runs, "looked at the code", next-step ideas, leftover TODOs, process
("ran typecheck").

## 3. Report

```markdown
## Achieved
- One-sentence headline
  - One-sentence so-what (why it matters, or what it replaced)

## Fixed
- One-sentence headline
  - One-sentence so-what (what was wrong before)

## Implemented
- One-sentence headline
  - One-sentence so-what (what this adds)

## Summary
Two to four sentences. Original problem, then how this work solves it. No new
facts that were not in the bullets.
```

Rules:

- Parent and child are each **one sentence**. No second child. No nested lists.
- Headline is the outcome, not a file path. A path may appear in the sub-bullet
  if it locates the change.
- Sub-bullet answers "so what" — never restates the parent in different words.
- Past tense, concrete. No "various improvements", no hedging, no "also considered".
- If nothing landed: one line ("Nothing landed this sitting — tree clean, no
  in-chat outcomes.") and stop. No empty headings.
- **Do not fix, commit, push, or keep implementing.** This skill only reports.
- **Do not write** `BOARD.md`, `NOW.md`, `CHANGELOG.md`, or a phase doc.
  `/phase sync` ticks the board; `/bump-version` writes the changelog.

## Example

```markdown
## Fixed
- Headless Grok runs no longer die on the first Edit call
  - `--always-approve` with explicit `--deny` rules replaced `acceptEdits`, which cancelled unattended prompts.

## Implemented
- `imp-grok-4-6` skill for the default Grok implementer
  - Generic "have grok implement this" now routes here so 4.5 and 4.6 no longer collide.

## Summary
Delegation to Grok was stalling in headless mode and the 4.5/4.6 skills were
fighting over the same trigger. The deny-rules fix makes unattended Edit calls
actually land, and 4.6 now owns the generic "have grok implement this" path.
```
