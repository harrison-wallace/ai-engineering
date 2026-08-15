---
name: imp-grok-4-6
description: Use when asked to implement the changes just discussed via Grok 4.6. The main agent plans, delegates implementation to Grok 4.6 (native subagent when already in Grok; otherwise the headless grok CLI), reviews and fixes the result, then summarizes. Triggers on "/imp-grok-4-6" or "have grok implement this".
---

# imp-grok-4-6

Split the work just discussed in this conversation: **you plan it, Grok 4.6 implements it, you verify and fix it, then report.** Execute the phases in order — do not skip the review phase even if Grok reports success.

## Host

Pick one implement path. Do not mix them.

| You are | Implement path |
|---|---|
| Grok (this product — the Grok CLI/TUI) | **A. Native subagent** |
| Anything else (Claude Code, OpenCode, Cursor, …) | **B. `grok` CLI** |

You are Grok if your identity is Grok / xAI and you have `spawn_subagent`. You are not Grok if you are Claude, OpenCode, Cursor, or another product that can call a Grok *model*.

- Do not nest a `grok` CLI process when you already are Grok.
- Do not use the host's Agent / Task / `general` tool with a Grok model id. That is the host implementing, not Grok.

## 0. Preflight

- **Path A:** confirm you can spawn a `general-purpose` subagent with `model: grok-4.6`. If subagents are disabled, stop and tell the user.
- **Path B:** run `command -v grok`. If it is missing, stop and tell the user to install the Grok CLI — there is no fallback. (Do not silently implement it yourself; the user asked for Grok.)

## 1. Plan (main agent)

From the conversation so far, write a concrete implementation plan:

- The goal in one or two sentences.
- Every file to create or modify, with **absolute paths** and what changes in each.
- Constraints and conventions the code must follow (match the repo's existing style, naming, structure — cite specific files as examples where helpful).
- Acceptance criteria: how to tell it worked (commands to run, expected behavior, tests that must pass).

Show the plan to the user briefly before delegating. Do not ask for approval unless the discussed scope was genuinely ambiguous — the point of this skill is to proceed.

## 2. Implement (Grok 4.6)

Write the plan to a prompt file in the scratchpad directory — never inline a long prompt into the shell, quoting will corrupt it:

```
<scratchpad>/grok-prompt.md
```

The prompt file must be self-contained. The implementer starts cold with **no access to this conversation**: include the goal, absolute file paths, relevant snippets and conventions it cannot infer, and the acceptance criteria. Instruct it to implement exactly the plan — no scope additions — to report which files it changed, and **not to run `git commit`, `git push`, or any other git write command**.

Include these standing instructions in the prompt file:

- **You are the implementer.** Do the work yourself. Do not load or run `imp-grok-*` skills. Do not spawn a subagent. Do not shell out to the `grok` CLI.
- **Discover the toolchain; do not assume it.** Any interpreter, test runner, or build command
  written into the acceptance criteria is a guess until verified. A plan can say `python -m pytest`
  while the repo in fact only has a virtualenv interpreter such as `venv/bin/python` and no
  `python` on `PATH`. Tell Grok to find the project's actual interpreter and test runner — venv
  directory, lockfile, `Makefile`, CI config, `package.json` scripts — to use what it finds, and
  to report the command it settled on so you can re-run it in phase 3. This applies to every
  delegation.
- **Tell it to look for an existing helper before writing a new one.** A cold agent cannot know
  what the repo already has, so it writes its own version of things that already exist a module
  away — and the duplicate is usually the worse one, because the original was hardened by a bug
  the newcomer has not hit yet. A provider that reads the whole of a growing append-only file
  will pass every test and fall over after an hour of real use, next to a sibling module with a
  bounded tail-read helper it never looked for. Name the directories most likely to hold prior
  art, tell Grok to grep them before adding any helper, and to list in its report which existing
  helpers it reused. This applies to every delegation.
- **An async call started before unmount keeps running.** Unmounting a component does not cancel
  work already in flight. Whenever the plan involves aborting, retrying, or resuming on remount,
  the prompt file must state explicitly whether the original in-flight call is cancelled or
  allowed to complete. Left unstated, Grok guesses, and the guess is where the defects land.
  Include this only when component lifecycle or in-flight async work is in scope.
- **Give every style constraint a command that checks it.** A constraint stated as an adjective —
  "wrap at roughly 100 columns", "match the surrounding indentation" — is not something a cold
  agent can confirm, and it drifts. Write the check next to the constraint
  (`awk '{print length}' <file> | sort -n | tail -1`) and tell Grok to run it before reporting.

Then follow the path from Host.

### Path A — native Grok subagent

Spawn a child with `spawn_subagent`:

- `subagent_type`: `general-purpose`
- `model`: `grok-4.6` — pass it explicitly; do not inherit
- `background`: `false` — you need the result before review
- `isolation`: omit (shared worktree so you can review)
- `prompt`: the full contents of `<scratchpad>/grok-prompt.md`
- `description`: a 3–5 word label for the task

Do not also run the `grok` CLI.

If spawn fails, report that and stop. Do not implement it yourself. Do not fall back to Path B.

### Path B — grok CLI

Then run it from the repo root:

```bash
grok --prompt-file <scratchpad>/grok-prompt.md \
     --model grok-4.6 \
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

- Give the shell call at least 10 minutes (600000 ms where the host takes a timeout). Grok is a
  full agent loop and a real implementation task takes minutes.
- Redirect to a log file rather than piping into `tail`. When a run misbehaves the evidence has to
  survive.
- Do not `cd` into the repo *and* pass `--cwd`; `--cwd` alone is enough.
- **Run the invocation exactly as written and append nothing to it.** Adding even
  `; echo "exit: $?"` turns it into a chained command, and chained commands are classified
  segment by segment — which can get the entire call blocked before it reaches a shell. The exit
  code is not worth it; the worktree check below is the real evidence anyway.
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

An empty worktree after a confident report is a failed run on either path.

**Path A.** Re-spawn at most once with a more imperative prompt. If the worktree is still
unchanged, stop and report. Do not implement it yourself.

**Path B.** A run that narrates a plan ("Implementing the backend first, then the frontend") and
then exits with a clean worktree has almost always been killed by a permission prompt. Do not
guess — Grok writes a machine-readable trace of every tool call and permission decision:

```
~/.grok/sessions/<url-encoded-cwd>/<session-id>/events.jsonl
```

The directory name is the working directory with `/` percent-encoded as `%2F` (so
`/home/you/git/my-project` → `%2Fhome%2Fyou%2Fgit%2Fmy-project`); take the newest session directory
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
- **The host may block the `grok` CLI call.** That is a denial on *this* side, not a Grok
  failure. On Claude Code it reads `Blocked by classifier`. **First check whether you changed
  the command.** Appending anything — `; echo "exit: $?"`, an `&&` chain, a pipe — makes it a
  chained command and is the most common trigger, so retry the invocation verbatim before
  concluding anything else. Note that a user reporting the skill has worked all day is evidence
  *for* this cause, not against it: the template is fine and the deviation is yours. If the
  verbatim call is still blocked, do not try to work around it — renaming the binary, wrapping it
  in a script, or routing it through another tool all circumvent the check rather than satisfy it.
  Tell the user, and offer that they run the exact command themselves in the host's shell escape
  (`! grok …` in Claude Code) so its output lands in the conversation — then pick up at phase 3.
  A durable fix is a shell allow-rule for `grok` in the host's project settings
  (Claude Code: `.claude/settings.json`; OpenCode: `permission.bash` in `opencode.json`).

Escalate at most twice, then stop and report. Never substitute your own implementation for Grok's
without the user saying so.

## 3. Review (main agent)

Never trust Grok's report alone. **Capture the handover before you touch anything** — the
scorecard in 3b grades what Grok delivered, not what you repaired:

```bash
git -C <repo-root> diff > <scratchpad>/grok-raw.diff
git -C <repo-root> status --short > <scratchpad>/grok-raw.status
```

Then:

- Read every change in the diff (and `grok-raw.status` for new files).
- Check the diff against the plan: anything missing, anything extra, anything that breaks the repo's conventions.
- Run the acceptance-criteria commands / tests yourself.
- If Grok committed anything despite the instruction, say so plainly in the summary.

Do not fix anything yet.

## 3b. Score the implementation (main agent)

Grade **the execution of the plan** — never the plan itself. If the plan asked for a mediocre
design and Grok built exactly that, cleanly, it scores high. The point is to isolate one variable:
what Grok does with instructions. A weak plan is a phase-1 problem and has no effect on any number
here.

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
  the output of a command you ran. Grok's stdout is a claim, never evidence.
- **Mark Security `N/A`** when the diff touches no input handling, secrets, paths, or subprocess
  calls. Do not manufacture a score to fill the row.
- **5 is rare** — it means there is nothing you would change. A run with fixes pending in 3c does
  not have a 5 on the dimension those fixes address.
- **The headline is the lowest scored dimension**, not the mean. A well-tested, elegant
  implementation of the wrong thing is not a 4.

Report as a compact table (dimension, score, one-line evidence), then the headline as
`**Overall: N/5**`.

Optionally append one line per run to `<repo-root>/.imp-scorecard.log` if that file already
exists — date, `grok-4.6`, task, the six scores, one-line failure note. The model field is what
makes the log comparable across the `imp-*` skills. Do not create the file unprompted.

## 3c. Fix (main agent)

Now repair what the review found:

- Fix problems directly with your own edits — do not send them back to Grok unless the implementation is wrong wholesale.
- Fixes do not change the scorecard. It records the handover.

## 4. Summarize

End with a short report to the user:

- **Plan** — one-line restatement of the goal.
- **Grok implemented** — files changed and what was done.
- **Review** — what you checked, what you fixed (or "no fixes needed").
- **Verification** — what you ran and the result.
- **Scorecard** — the table and headline from 3b.

Then, if and only if there is something concrete to say, a trailing side note:

> **Note on the skill** — this would have gone better if the skill had X.

Rules for the note: **zero bullets is a normal outcome** — write nothing rather than manufacture a
suggestion. At most two. Only for something repeatable that belongs in the skill (a line the
prompt-file template should carry, a deny rule, a turn budget, a convention worth stating
explicitly to a cold agent) — not a one-off Grok mistake, which is already a score. Never rehash
the scorecard, never mix in fixes to the work, and never edit this skill or open a task off the
back of it. It is a comment for the user to act on separately.

Leave the changes uncommitted unless the user asked otherwise.
