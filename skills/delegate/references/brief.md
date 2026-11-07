# Implementer brief

Every implementer starts cold, with no access to this conversation. Build each brief from the
plan and these parts. Write it to `<scratchpad>/delegate/<slug>/brief-<implementer>.md`. For Grok,
the brief is the prompt file. Never inline a long brief into a shell command, because quoting
corrupts it.

## Contents

- **The goal**, in one or two sentences.
- **The work unit**: every file to create or change, with absolute paths and what changes in each.
  For a split route, only this implementer's unit, plus the files it must not touch.
- **The working directory**: the repo root, or the worktree path for `a/b`. Tell it to work only
  there.
- **Conventions** it cannot infer, with one existing file cited as an example.
- **Acceptance criteria**: the commands to run and the behavior to expect.
- **For `a/b sonnet-sonnet`**: this side's premise (§ Premises).

## Standing instructions

Include all of these in every brief:

- **You are the implementer.** Do the work yourself. Do not load `delegate` or any other
  delegation skill, do not spawn a subagent, and do not shell out to `grok` or `claude`.
- **Implement exactly the plan.** No scope additions. If the plan is wrong or impossible, stop and
  say why instead of improvising.
- **No git writes.** Do not run `git commit`, `push`, `add`, `tag`, `reset`, `checkout`, or
  `stash`.
- **Discover the toolchain. Do not assume it.** A test or build command in the acceptance criteria
  is a guess until verified. A plan can say `python -m pytest` while the repo only has
  `venv/bin/python`. Find the real interpreter and test runner (a venv folder, lockfile,
  `Makefile`, CI config, or `package.json` scripts), use it, and report the command you settled on.
- **Look for an existing helper before you write a new one.** Grep the directories named in the
  brief first. A duplicate written cold is usually worse than the original, because the original
  was hardened by a bug the newcomer has not hit yet. List the existing helpers you reused.
- **Give every style constraint a command that checks it**, and run it before you report. For
  example, check a line-length rule with `awk '{print length}' <file> | sort -n | tail -1`.
- **Report**: the files you changed, the commands you ran with their results, and anything you
  could not do.

Include this one only when component lifecycle or in-flight async work is in scope:

- **An async call started before unmount keeps running.** State whether the in-flight call is
  cancelled or allowed to complete on abort, retry, or remount. Left unstated, the implementer
  guesses, and the guess is where the defects land.

## Premises

For `a/b sonnet-sonnet`, unless the user gave their own two briefs:

| Side | Premise |
|---|---|
| **A: extend** | The smallest change that fits the current structure. Reuse what exists. |
| **B: reshape** | Build the touched area as if this requirement had been there from day one. Move boundaries if that gives a simpler result. |
