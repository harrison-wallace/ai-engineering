---
name: diagnose
description: Find the cause of one reported failure (a bug, a flake, a regression, a slow path, or a broken infra hop) through gated phases. Build a tight loop that goes red on this bug, shrink the repro, show 3–5 ranked falsifiable guesses before testing any, probe one variable at a time with tagged logs, then fix only after your yes, with a regression test at a correct seam. `lite` gives ranked guesses and the loop it would build, read-only. `deep` adds a Sonnet guesser that never sees the main agent's theory. Keeps a diagnosis log in the scratchpad so the work survives compaction. User-invoked only, through "/diagnose".
argument-hint: "[lite|deep] <symptom>"
disable-model-invocation: true
---

# diagnose

Find the cause of one reported failure, prove it, then fix it after the user says yes. **Never
commit.**

The skill exists for one gate: **no tight loop, no theory.** Without a command that goes red on
this bug, an agent reads code and guesses. With one, bisection, guesses, and probes are mechanical.

Adapted from Matt Pocock's `diagnosing-bugs`.

Not for: a codebase-wide hunt for slow spots with no symptom (`check-architecture`), why code was
written this way (`explain-why`), or how it works (`explain-how`).

## Level

| First argument | Level | Does |
|---|---|---|
| `lite` | lite | §1, then read the code path and recent history. Report ranked guesses, the loop you would build, and the first probe. Read-only. No harness, no edits |
| none, or anything else | default | Every phase. The main agent works alone |
| `deep` | deep | Every phase. At §4, one Sonnet guesser writes guesses in a fresh context (§4.2) |

Do not run `/effort` or `/model`. Set `model` and `effort` on the Agent call only.

## Rules that hold in every phase

- **Redact.** Write `<REDACTED>` in place of every secret, token, or personal datum in a command,
  an output, a log, or a captured file. Build loops on environment variables, so the secret stays in
  the environment. If redacted output is not enough to diagnose, say so and ask.
- **Shared systems are read-only.** On production, shared, or AWS systems, run reads only. A
  deploy, a restart, an `aws` write, a database write, or a cache flush needs the user's yes first.
  Local dev services are yours to restart.
- **Throwaway files go in the scratchpad.** Harnesses, repro scripts, captures, and the log live
  there. Only the regression test and the fix go in the repo.
- **Language.** Write every report, table, and log line in ASD-STE100 Simplified Technical
  English: active voice, one idea in each sentence, 20 words or fewer, the same word for the same
  thing. Use the terms from `GLOSSARY.md` (through `GLOSSARY-MAP.md` when there are several).

## 0. Diagnosis log

At the start (not at `lite`), create `<scratchpad>/diagnose-<slug>.md`. Update it at the end of
each phase:

```markdown
# diagnose: <symptom in one line>
Phase: <n>
Loop: `<command>` (red: <exact symptom line>)
Repro: <minimal case>
Guesses: <#, guess, status: open | ruled out by <probe> | confirmed>
Probes: <probe, result, one line each>
Debug tag: [DEBUG-xxxx]
Open: <what waits on the user>
```

After compaction or a `/clear`, read this log first and continue from its phase.

## 1. Symptom

State the symptom in one line: what was expected, what happened, where, and since when. If the
user's words carry a guess ("I think it's the cache"), record it as one guess for §4. Do not adopt
it.

Read `GLOSSARY.md` and the ADRs in `docs/adr/` that touch the area. When the bug appeared between
two known states, list them (commits, versions, deploys). That makes it a regression, and §2 can use
`git bisect run`. When old code in the path looks deliberate, run a narrow `explain-why` on those
lines before you change them.

**Done when** the symptom line is specific enough that a loop can assert it.

**lite**: read the code path and `git log -15 --oneline -- <paths>`, then report:

1. The symptom line.
2. The guess table from §4.3, ranked.
3. The loop you would build, as one command, from [`references/loops.md`](references/loops.md).
4. The first probe, and what each result would mean.

End with one line that offers `/diagnose <symptom>` for the full run. Stop.

## 2. Build the loop

This phase gets the most effort. Pick the loop from [`references/loops.md`](references/loops.md):
app loops, infra loops, UI loops, flaky bugs, performance, bisection, and the human-in-the-loop
script. Prefer a loop higher in its list.

Then make it **tight**: faster (cache setup, narrow the scope), sharper (assert the exact symptom,
not "did not crash"), and deterministic (pin time, seed random values, isolate the file system,
stub the network).

**Done when** you can name one command that meets all four, and you ran it and showed the output:

- [ ] **Red**: it drives the real bug path and asserts the user's exact symptom.
- [ ] **Deterministic**: the same verdict every run. For a flaky bug, a pinned reproduction rate.
- [ ] **Fast**: seconds, not minutes.
- [ ] **Agent-runnable**: it runs with no human, or it is the human-in-the-loop script.

If you read code to build a theory before this command exists, stop. That is the failure this
skill prevents.

**If you cannot build a loop**, stop and say so. List what you tried. Ask for one of: access to the
environment that shows the bug, a redacted capture (a HAR file, a log dump, a screen recording with
times), or a yes to add temporary instrumentation in that environment. Do not go on to §4.

## 3. Reproduce and shrink

Run the loop and watch it go red. Check that it shows the user's failure, not a different failure
near it, and that it repeats.

Then shrink the repro. Cut inputs, callers, config, data, and steps one at a time. Run the loop
after each cut. Keep a cut when the loop stays red.

**Done when** every remaining part is needed: removing any one of them turns the loop green.

## 4. Guess

### 4.1 Your guesses

Write 3–5 guesses before you test any. Each guess states its prediction: "If X is the cause, then
changing Y makes the bug go away, and changing Z makes it worse." A guess with no prediction is not
a guess. Sharpen it or drop it.

### 4.2 deep: the blind guesser

Launch it in the same response as your own §4.1 work, so it cannot see your theory:

- `subagent_type`: `Explore`, `model`: `sonnet`, `effort`: `medium`, `run_in_background`: `false`.
- Prompt: the full text of [`references/guesser-prompt.md`](references/guesser-prompt.md), with the
  symptom, the loop command, the minimal repro, the repo root, and the relevant paths filled in.
  Do not include your guesses, the user's guess, or your reading of the code.

Merge its guesses with yours. Drop duplicates. Mark each merged row with its source (`main`,
`blind`, or `both`). A guess that both sources reached independently ranks higher.

### 4.3 The checkpoint

Show the table and stop. The user often knows something that re-ranks it at once.

| # | Guess | Prediction | Probe | Likely |
|---|---|---|---|---|
| 1 | <cause> | If so, <change> fixes it and <change> makes it worse | <what you will run or log> | high, medium, or low |

Then: "Yes runs the probes in this order. Or re-rank, add, or rule out by number."

**Done when** the user answers.

## 5. Probe

Each probe tests one prediction from §4. Change one variable at a time.

- Prefer a debugger or a REPL. One breakpoint beats ten logs.
- Otherwise, put targeted logs at the boundaries that tell the guesses apart. Never log everything
  and grep.
- Tag every debug log with one prefix for this run, such as `[DEBUG-a4f2]`, and record it in the
  log. Clean-up is then one grep.
- For a performance bug, logs are usually wrong. Use the performance section of
  [`references/loops.md`](references/loops.md): measure a baseline, then bisect.

After each probe, mark the guess confirmed, ruled out, or open, with the evidence. When every guess
is ruled out, go back to §4 with what the probes showed.

**Done when** one guess is confirmed by a probe whose result its prediction called.

## 6. Confirm, then fix

Report the root cause: the confirmed guess, the probe, and its output. Then ask for a yes before
you change code. When the fix is large or touches many files, offer `/delegate` for it.

On a yes:

1. **Find a correct seam** for the regression test: one where the test drives the real bug
   pattern as it happens at the call site. A seam that is too shallow (one caller when the bug needs
   two, a unit test that cannot reach the trigger) gives false confidence.
2. **With a correct seam**: turn the minimal repro into a test there. Watch it fail. If you forced
   the red by changing code or a fixture, `diff` against a clean copy to prove the change landed.
   Apply the fix. Watch the test pass.
3. **With no correct seam**: say so. That is a finding, because the code's shape stops this bug
   from being locked down. Offer `/check-architecture` on the area.
4. Run the §2 loop against the original, unshrunk scenario. It must be green.

## 7. Clean up

**Done when** every box holds:

- [ ] The §2 loop is green on the original scenario.
- [ ] The regression test passes, or the missing seam is in the report.
- [ ] `rg -n '\[DEBUG-xxxx\]'` over the repo finds nothing.
- [ ] Scratchpad harnesses stay out of the repo. Anything written in the repo for the hunt is gone.

## 8. Report

```markdown
## Root cause
<One or two sentences.> Proof: <probe> showed <output>.

## Loop
`<command>`. It was red with <symptom>. It is green now.

## Guesses
| # | Guess | Source | Result |
|---|---|---|---|
| 1 | ... | main, blind, or both | confirmed, ruled out by <probe>, or not tested |

## Fix
<What changed, with `file:line`.> Regression test: `<path>`, or "No correct seam: <why>".

## Next
<One line for each that applies.>
```

For **Next**, pick from: `/summarise commit` for the message (it names the confirmed guess, so the
next person learns), `/check-architecture <area>` when no seam existed, and `/reflect` to ask what
would have stopped this bug.
