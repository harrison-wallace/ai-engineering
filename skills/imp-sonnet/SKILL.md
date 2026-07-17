---
name: imp-sonnet
description: Use when asked to implement the changes just discussed via a Sonnet subagent. The main agent plans, delegates implementation to Sonnet, reviews and fixes the result, then summarizes. Triggers on "/imp-sonnet" or "have sonnet implement this".
---

# imp-sonnet

Split the work just discussed in this conversation: **you plan it, Sonnet implements it, you verify and fix it, then report.** Execute the four phases in order — do not skip the review phase even if the subagent reports success.

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

## 3. Review and fix (main agent)

Never trust the subagent's report alone:

- `git diff` (and `git status --short` for new files) — read every change.
- Check the diff against the plan: anything missing, anything extra, anything that breaks the repo's conventions.
- Run the acceptance-criteria commands / tests yourself.
- Fix problems directly with your own edits — do not send them back to the subagent unless the implementation is wrong wholesale.

## 4. Summarize

End with a short report to the user:

- **Plan** — one-line restatement of the goal.
- **Sonnet implemented** — files changed and what was done.
- **Review** — what you checked, what you fixed (or "no fixes needed").
- **Verification** — what you ran and the result.

Leave the changes uncommitted unless the user asked otherwise.
