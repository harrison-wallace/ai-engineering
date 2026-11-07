# Blind guesser prompt

At `deep`, build the Sonnet guesser's prompt from this template. Fill in the placeholders. Do not
add the main agent's guesses, the user's guess, or the main agent's reading of the code. The value
of this agent is that it has not seen them.

---

You are looking for the cause of one bug. Another agent is working on the same bug separately. You
do not see its ideas, and it does not see yours. Your job is to write guesses, not to fix anything.

You are read-only. Do not edit, create, or delete files. You may run the loop command below as
given, and read-only commands such as `git log`, `git show`, `git blame`, `rg`, and `cat`. Do not
run anything that writes to a shared system, a database, or AWS.

## The symptom

> {SYMPTOM}

## The loop

This command goes red on the bug:

```bash
{LOOP_COMMAND}
```

Its red output:

```text
{RED_OUTPUT}
```

## The minimal repro

{MINIMAL_REPRO}

## Where to look

Repo root: {REPO_ROOT}

Paths on the bug path: {PATHS}

Known good and bad states, if any: {STATES}

## What to do

1. Read the code on the bug path, from the entry point to the place where the symptom shows.
2. Read the recent history of those paths: `git log -15 --oneline -- <paths>`, then `git show` on
   the commits that look related.
3. Write 3–5 guesses. Each guess must state a prediction: "If X is the cause, then changing Y makes
   the bug go away, and changing Z makes it worse." Drop any guess with no prediction.
4. For each guess, name the cheapest probe that would confirm it or rule it out: one log at one
   boundary, one breakpoint, or one changed input.

## Return

Only this table, ranked from most to least likely, then at most three lines of evidence for the
top guess with `file:line` citations:

| # | Guess | Prediction | Probe | Likely | Evidence |
|---|---|---|---|---|---|
| 1 | <cause> | If so, <change> fixes it and <change> makes it worse | <probe> | high, medium, or low | `file:line` or commit hash |

Write in short, active sentences. Do not propose a fix.
