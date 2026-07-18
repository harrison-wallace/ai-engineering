---
name: fix-react-doctor
description: Run react-doctor on a React project and iteratively fix the reported issues until the score reaches 100. Use to clean up React patterns and anti-patterns automatically. Triggers on "/fix-react-doctor", "run react-doctor", or "get the react-doctor score to 100".
---

# fix-react-doctor

Drive `react-doctor` — a diagnostics tool that scans a React project for
anti-patterns and assigns a 0–100 quality score — in a fix/verify loop until
the score is 100 (or nothing actionable remains).

## 1. Baseline

From the project root (locate it if the repo has multiple apps — where
`package.json` declares `react`):

```bash
npx react-doctor@latest
```

Record the starting score and the full issue list. If the tool fails to run
(not a React project, unsupported setup), report why and stop.

Note the state of the working tree first (`git status --short`). If there are
unrelated uncommitted changes, proceed but keep your edits reviewable — don't
mix them with a reformat of untouched files.

## 2. Fix loop

Repeat until the score is 100:

1. Group the reported issues and fix them in order of impact — many at a time
   is fine, but keep each fix minimal and behavior-preserving.
2. Apply fixes yourself with targeted edits. If react-doctor offers an
   auto-fix flag, you may use it, then review its diff.
3. Re-run `npx react-doctor@latest` and compare the score and issue list.

Rules for the loop:

- **Behavior is sacred.** These are refactors, not rewrites — never change
  what a component renders or does to satisfy a lint rule. If a fix would
  require a behavior change or a large architectural rework, skip it and
  record why.
- **Verify as you go.** After each iteration, make sure the project still
  builds / typechecks (use the project's own scripts, e.g. `npm run build`,
  `tsc --noEmit`, or the test suite if it's fast).
- **No score chasing by suppression.** Don't disable rules, add ignore
  comments, or delete code just to raise the score, unless the code is
  genuinely dead.
- **Stop conditions.** Stop early if: the score stops improving for two
  consecutive iterations, the only remaining issues are ones you've
  deliberately skipped, or fixes start conflicting with each other. A justified
  95 beats a broken 100.

## 3. Report

- Final score vs. starting score, and the number of iterations.
- Bullet list of what was fixed, grouped by pattern (e.g. "removed 4 unstable
  hook dependencies", "converted 3 class components").
- Any issues deliberately skipped, each with a one-line reason.
- Confirmation that the build/typecheck (and tests, if run) still pass.
- Do not commit — leave the changes in the working tree for review unless the
  user asks for a commit.
