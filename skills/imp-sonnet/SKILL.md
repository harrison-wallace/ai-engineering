---
name: imp-sonnet
description: Use when asked to implement the changes just discussed via a Sonnet subagent. The main agent plans, delegates implementation to Sonnet, reviews and fixes the result, then summarizes. Triggers on "/imp-sonnet" or "have sonnet implement this".
---

# imp-sonnet

Split the work just discussed in this conversation: **you plan it, Sonnet implements it, you verify and fix it, then report.** Execute the phases in order — do not skip the review phase even if the subagent reports success.

## 1. Plan (main agent)

From the conversation so far, write a concrete implementation plan:

- The goal in one or two sentences.
- Every file to create or modify, with what changes in each.
- Constraints and conventions the code must follow (match the repo's existing style, naming, structure — cite specific files as examples where helpful).
- Acceptance criteria: how to tell it worked (commands to run, expected behavior, tests that must pass).

Show the plan to the user briefly before delegating. Do not ask for approval unless the discussed scope was genuinely ambiguous — the point of this skill is to proceed.

## 2. Implement (Sonnet subagent)

Launch a subagent with the Agent tool:

- `subagent_type`: `general-purpose`
- `model`: `sonnet`
- `run_in_background`: `false` — you need the result before continuing.
- `prompt`: the full plan from step 1, plus all context Sonnet needs. The subagent starts cold: include absolute file paths, relevant snippets or conventions it can't infer, and the acceptance criteria. Instruct it to implement exactly the plan — no scope additions — and to report which files it changed and how it verified them.

Do not commit, and instruct the subagent not to commit either.

## 3. Review (main agent)

Never trust the subagent's report alone. **Capture the handover before you touch anything** — the
scorecard in 3b grades what Sonnet delivered, not what you repaired:

```bash
git -C <repo-root> diff > <scratchpad>/sonnet-raw.diff
git -C <repo-root> status --short > <scratchpad>/sonnet-raw.status
```

Then:

- Read every change in the diff (and `sonnet-raw.status` for new files).
- Check the diff against the plan: anything missing, anything extra, anything that breaks the repo's conventions.
- Run the acceptance-criteria commands / tests yourself.

Do not fix anything yet.

## 3b. Score the implementation (main agent)

Grade **the execution of the plan** — never the plan itself. If the plan asked for a mediocre
design and Sonnet built exactly that, cleanly, it scores high. The point is to isolate one
variable: what the model does with instructions. A weak plan is a phase-1 problem and has no effect
on any number here.

Score each dimension 1–5 against the anchors below. The plan is the yardstick throughout.

| Dimension | 1 | 3 | 5 |
| --- | --- | --- | --- |
| **Fidelity** | Planned changes missing or landed somewhere else | Most of the plan landed; a file or requirement skipped or reinterpreted | Every planned change present as specified, nothing outside the plan's surface area |
| **Bloat** | Substantial code untraceable to any plan line — speculative abstraction, unrequested config, dead paths | Some unasked-for scaffolding: a wrapper with one caller, defensive handling for what cannot fail, a helper used once | Minimal diff. Every line traces to a plan line |
| **Correctness** | Does not do what the acceptance criteria describe, or breaks existing behavior | Works on the main path; edge cases, error paths, or resource handling are wrong or absent | Behavior matches the criteria including the unhappy paths |
| **Security** | Introduces an exploitable flaw (injection, path traversal, leaked secret, unsafe subprocess) | Works but handles untrusted input, secrets, or paths loosely | No new exposure; untrusted input and secrets handled correctly |
| **Maintainability** | Reads as foreign code — alien naming, structure, or comment density; hard to follow | Functional but inconsistent with the surrounding files | Indistinguishable in style and structure from code already in the repo |
| **Verification** | Acceptance criteria fail, or were never runnable | Criteria pass but nothing was added where the repo tests this kind of change | Criteria pass and tests exist to the standard the repo already keeps |

Rules that make the number mean something:

- **Evidence or it does not count.** Every score below 5 cites a `file:line` from the raw diff or
  the output of a command you ran. The subagent's report is a claim, never evidence.
- **Mark Security `N/A`** when the diff touches no input handling, secrets, paths, or subprocess
  calls. Do not manufacture a score to fill the row.
- **5 is rare** — it means there is nothing you would change. A run with fixes pending in 3c does
  not have a 5 on the dimension those fixes address.
- **The headline is the lowest scored dimension**, not the mean. A well-tested, elegant
  implementation of the wrong thing is not a 4.

Report as a compact table (dimension, score, one-line evidence), then the headline as
`**Overall: N/5**`.

Optionally append one line per run to `<repo-root>/.imp-scorecard.log` if that file already
exists — date, `sonnet`, task, the six scores, one-line failure note. The model field is what makes
the log comparable across the `imp-*` skills. Do not create the file unprompted.

## 3c. Fix (main agent)

Now repair what the review found:

- Fix problems directly with your own edits — do not send them back to the subagent unless the implementation is wrong wholesale.
- Fixes do not change the scorecard. It records the handover.

## 4. Summarize

End with a short report to the user:

- **Plan** — one-line restatement of the goal.
- **Sonnet implemented** — files changed and what was done.
- **Review** — what you checked, what you fixed (or "no fixes needed").
- **Verification** — what you ran and the result.
- **Scorecard** — the table and headline from 3b.

Then, if and only if there is something concrete to say, a trailing side note:

> **Note on the skill** — this would have gone better if the skill had X.

Rules for the note: **zero bullets is a normal outcome** — write nothing rather than manufacture a
suggestion. At most two. Only for something repeatable that belongs in the skill (a line the
subagent prompt should carry, a convention worth stating explicitly to a cold agent) — not a
one-off model mistake, which is already a score. Never rehash the scorecard, never mix in fixes to
the work, and never edit this skill or open a task off the back of it. It is a comment for the user
to act on separately.

Leave the changes uncommitted unless the user asked otherwise.
