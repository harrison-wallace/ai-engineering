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

The prompt file must be self-contained. Grok starts cold with **no access to this conversation**: include the goal, absolute file paths, relevant snippets and conventions it cannot infer, and the acceptance criteria. Instruct it to implement exactly the plan — no scope additions — to report which files it changed, and **not to run `git commit`, `git push`, or any other git write command** (the `--deny` rules below enforce this, but saying it in the prompt stops Grok wasting a turn on a blocked call).

Then run it from the repo root:

```bash
grok --prompt-file <scratchpad>/grok-prompt.md \
     --model grok-4.5 \
     --always-approve \
     --deny 'Bash(git commit*)' \
     --deny 'Bash(git push*)' \
     --deny 'Bash(git add*)' \
     --deny 'Bash(git tag*)' \
     --deny 'Bash(git reset*)' \
     --deny 'Bash(git checkout*)' \
     --deny 'Bash(git stash*)' \
     --deny 'Bash(rm -rf *)' \
     --max-turns 300 \
     --cwd <repo-root> \
     > <scratchpad>/grok-run.log 2>&1
```

Then read the log with `tail -60 <scratchpad>/grok-run.log`.

**Why always-approve, and why the deny rules are not optional.** Headless Grok has nobody to
answer a permission prompt. A prompt in headless does not block — it resolves as `cancelled`, the
turn ends immediately with `cancellation_category: permission_cancelled`, **and the process still
exits 0**. Grok's own docs (`~/.grok/docs/user-guide/22-permissions-and-safety.md`) name
always-approve as the mode for "Scripts, SDKs, CI", and `acceptEdits` / `auto` as interactive
modes. `acceptEdits` is specifically known to prompt on the first `search_replace` and silently
kill the run. The `--deny` rules are what makes this safe: deny beats always-approve, is checked
against *every* segment of a chained command, and turns "please don't commit" from a polite
request in the prompt file into an enforced block.

- Use a `timeout` of 600000 ms on the Bash call — Grok is a full agent loop and a real
  implementation task takes minutes.
- Redirect to a log file rather than piping into `tail`. When a run misbehaves the evidence has to
  survive.
- Do not `cd` into the repo *and* pass `--cwd`; `--cwd` alone is enough.
- If the run fails, times out, or produces no diff, report exactly that to the user before doing
  anything else — do not quietly implement it yourself instead.

**Exit 0 means nothing.** Before reading Grok's report, check that it actually changed files:

```bash
git -C <repo-root> status --short && git -C <repo-root> diff --stat
```

An empty result is a **failed run**, however confident the stdout narration sounds. Go to
[Troubleshooting](#troubleshooting-a-run-that-did-nothing) rather than accepting it.

Grok's stdout is its report, not evidence. Treat it as a claim to be checked.

## 2b. Troubleshooting a run that did nothing

A run that narrates a plan ("Implementing the backend first, then the frontend") and then exits
with a clean worktree has almost always been killed by a permission prompt. Do not guess — Grok
writes a machine-readable trace of every tool call and permission decision:

```
~/.grok/sessions/<url-encoded-cwd>/<session-id>/events.jsonl
```

The directory name is the working directory with `/` percent-encoded as `%2F` (so
`/home/h/git/AgentLens` → `%2Fhome%2Fh%2Fgit%2FAgentLens`); take the newest session directory
inside it. Filter for the decisions:

```bash
python3 -c "
import json,sys
for line in open(sys.argv[1]):
    d = json.loads(line)
    if d['type'] in ('tool_started','permission_resolved','turn_ended'):
        print(json.dumps(d))
" <session-dir>/events.jsonl | tail -20
```

Read the outcome:

| What the trace shows | Cause | Fix |
| --- | --- | --- |
| `permission_resolved … "decision": "cancelled"` then `turn_ended … permission_cancelled` | A prompt with nobody to answer it | You are not on `--always-approve`. Use the invocation above. |
| `turn_ended` with a max-turns/limit outcome | Turn budget exhausted | Raise `--max-turns`, or split the plan into two smaller runs. |
| Reads only, no `tool_started` for an edit tool (`search_replace`, `write_file`) | Grok never attempted the work | The prompt file was too vague or read as a question. Make the plan imperative and concrete. |
| No `tool_started` at all | Never got going | Check folder trust in `~/.grok/trusted_folders.toml`, and that `--cwd` is the repo root. |

Two footguns worth knowing before they cost an hour:

- **Tilde in a permission rule is literal.** Per the rule-matching reference, "a leading `//` or
  `~/` in a pattern is treated as literal glob text". A rule like `Edit(~/git/**)` in
  `~/.grok/config.toml` matches nothing, while `Edit(/tmp/**)` works — which is why a scratchpad
  smoke test can pass while the same run fails inside a repo under `~/git`. Path rules must be
  written with absolute paths or `**/` patterns.
- **Claude Code's own permission classifier may block the `grok` call.** That is a denial on *this*
  side, not a Grok failure, and it reads `Blocked by classifier`. Do not try to work around it.
  Tell the user, and offer that they run the exact command themselves by typing `! grok …` in the
  prompt so its output lands in the conversation — then pick up at phase 3.

Escalate at most twice, then stop and report. Never substitute your own implementation for Grok's
without the user saying so.

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
