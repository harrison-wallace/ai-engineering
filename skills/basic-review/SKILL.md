---
name: basic-review
description: Quick sanity check of the current diff for bugs, security issues, and over-engineering/bloat, reported as a severity table. Use for a fast pre-commit gut check, not a deep review. Triggers on "/basic-review" or "sanity check the diff".
---

# basic-review

A fast, single-pass sanity check of the working diff. Not a deep review — flag
what stands out, don't hunt exhaustively.

## 1. Collect the diff

```bash
git status --short
git diff HEAD            # staged + unstaged
```

If the tree is clean, review the last commit instead (`git diff HEAD~1..HEAD`) and
say so. Read enough surrounding context of each changed file to judge the change,
but do not audit untouched code.

## 2. Check for exactly three things

- **Bugs** — logic errors, unhandled edge cases (null/empty/error paths), broken
  behavior a user would hit, changes that contradict what the code claims to do.
- **Security** — injection, secrets in code, unsafe input handling, permission or
  auth gaps, unsafe file/network operations introduced by the diff.
- **Over-engineering / bloat** — needless abstractions or indirection, dead or
  duplicated code, dependencies added for something trivial, config/flexibility
  nothing uses, changes outside the task's scope.

Only report findings **introduced or touched by the diff**. Pre-existing issues are
out of scope unless severity 3.

## 3. Report

Output a single table, highest severity first:

| Sev | Type | Location | Summary |
|---|---|---|---|
| 3 | Bug | `path/file.py:42` | One sentence: what's wrong and when it bites. |

Severity scale:

| Sev | Meaning |
|---|---|
| 3 | Blocker — will break, corrupt, or expose something; fix before commit |
| 2 | Should fix — real defect or risk, but survivable short-term |
| 1 | Worth noting — minor issue or cleanup, fix opportunistically |
| 0 | Observation — style/nit, no action required |

Rules:

- One row per finding; `Type` is `Bug`, `Security`, or `Bloat`.
- Be sure before flagging — a sanity check with false positives is worse than none.
  Skip anything you'd hedge with "might" unless it's severity 2+.
- If nothing is wrong, say so in one line ("Diff looks clean — N files reviewed, no
  findings.") instead of an empty table.
- After the table, one short closing line with the overall verdict (e.g. "Safe to
  commit once the sev-3 is fixed."). No essay.
- **Do not fix anything** — this skill only reports. The user decides what to act on.
