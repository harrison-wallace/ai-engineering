---
name: imp-grok-4-5
description: Use when asked to implement the changes just discussed via Grok 4.5. The main agent plans, delegates implementation to the grok CLI running headless, reviews and fixes the result, then summarizes. Triggers on "/imp-grok-4-5" or "have grok implement this".
---

# imp-grok-4-5

Split the work just discussed in this conversation: **you plan it, Grok 4.5 implements it, you verify and fix it, then report.** Execute the phases in order — do not skip the review phase even if Grok reports success.

Grok is not a Claude subagent. The `Agent` tool only spawns Claude models, so delegation happens by shelling out to the `grok` CLI in headless mode via `Bash`.

## 0. Preflight

Run `command -v grok`. If it is missing, stop and tell the user to install the Grok CLI — there is no fallback. (Do not silently implement it yourself; the user asked for Grok.)

## 1. Plan (main agent)

From the conversation so far, write a concrete implementation plan:

- The goal in one or two sentences.
- Every file to create or modify, with **absolute paths** and what changes in each.
- Constraints and conventions the code must follow (match the repo's existing style, naming, structure — cite specific files as examples where helpful).
- Acceptance criteria: how to tell it worked (commands to run, expected behavior, tests that must pass).

Show the plan to the user briefly before delegating. Do not ask for approval unless the discussed scope was genuinely ambiguous — the point of this skill is to proceed.

## 2. Implement (Grok 4.5, headless)

Write the plan to a prompt file in the scratchpad directory — never inline a long prompt into the shell, quoting will corrupt it:

```
<scratchpad>/grok-prompt.md
```

The prompt file must be self-contained. Grok starts cold with **no access to this conversation**: include the goal, absolute file paths, relevant snippets and conventions it cannot infer, and the acceptance criteria. Instruct it to implement exactly the plan — no scope additions — to report which files it changed, and **not to run `git commit`, `git push`, or any other git write command**.

Then run it from the repo root:

```bash
grok --prompt-file <scratchpad>/grok-prompt.md \
     --model grok-4.5 \
     --permission-mode acceptEdits \
     --cwd <repo-root>
```

- Use a `timeout` of 600000 ms on the Bash call — Grok is a full agent loop and a real implementation task takes minutes.
- `acceptEdits` lets Grok read, edit, and run commands without prompting; it cannot prompt interactively in headless mode, so a stricter mode will stall the run.
- Do not pass `--permission-mode bypassPermissions`.
- If the run fails or times out, report exactly that to the user before doing anything else — do not quietly implement it yourself instead.

Grok's stdout is its report, not evidence. Treat it as a claim to be checked.

## 3. Review and fix (main agent)

Never trust Grok's report alone:

- `git diff` (and `git status --short` for new files) — read every change.
- Check the diff against the plan: anything missing, anything extra, anything that breaks the repo's conventions.
- Run the acceptance-criteria commands / tests yourself.
- Fix problems directly with your own edits — do not send them back to Grok unless the implementation is wrong wholesale.
- If Grok committed anything despite the instruction, say so plainly in the summary.

## 4. Summarize

End with a short report to the user:

- **Plan** — one-line restatement of the goal.
- **Grok implemented** — files changed and what was done.
- **Review** — what you checked, what you fixed (or "no fixes needed").
- **Verification** — what you ran and the result.

Leave the changes uncommitted unless the user asked otherwise.
