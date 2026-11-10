# Grok runbook

## Contents

- [1. Preflight and model](#1-preflight-and-model)
- [2. Run](#2-run)
- [3. Troubleshooting a run that did nothing](#3-troubleshooting-a-run-that-did-nothing)

How `delegate` runs the headless `grok` CLI for the `grok`, `mixed`, and `a/b grok-sonnet` routes.
The main agent still plans, reviews, scores, and fixes. The child process is the implementer.

- Do not use the host's Agent, Task, or `general` tool with a Grok model id. That is the host
  implementing, not Grok.
- The implementer is the headless `grok` CLI even when this session itself runs under Grok. A
  native subagent inherits this session's effort, so it cannot take its own level.

## 1. Preflight and model

Run `command -v grok`. If it is missing, stop the Grok route and say so. Offer the other routes.
Never implement it yourself in Grok's place without the user saying so.

Pick the latest model every run. Do not hardcode a version:

```bash
grok models
```

- If the output says the CLI is not authenticated, stop the Grok route. Tell the user to sign in,
  in a terminal or with `! grok` in Claude Code, and offer the other routes.
- Take the highest `grok-<major>.<minor>` id in the list, on every route, including `speed` and
  `mixed`. Ignore ids with a suffix (such as `-mini`, `-fast`, or `-build-fast`) unless no plain id
  exists.
- If the list cannot be read, omit `--model` so the CLI uses its default, and say so.
- Name the model and the effort in the plan and in the summary, for example `grok-4.7/medium`.

**Effort**: `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, or `max`. The default is
`medium`. The level goes only to the child process through `--effort`. Do not run `/effort`, and
do not change this session's effort.

## 2. Run

Run it from the repo root, or with `--cwd` set to the worktree for `a/b`. Substitute the model from §1 for `<model>` and the effort for `<level>`, and change nothing else:

```bash
grok --prompt-file <scratchpad>/delegate/<slug>/brief-grok.md \
     --model <model> \
     --effort <level> \
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
     > <scratchpad>/delegate/<slug>/grok-run.log 2>&1
```

Then read the log with `tail -60 <scratchpad>/delegate/<slug>/grok-run.log`.

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

An empty result is a **failed run**, however confident the stdout narration sounds. Go to §3 rather than accepting it.

Grok's stdout is its report, not evidence. Treat it as a claim to be checked.

## 3. Troubleshooting a run that did nothing

An empty worktree after a confident report is a failed run.

Re-run the same command at most once, with a more imperative prompt file. If the worktree is still
unchanged, stop and report. Do not implement it yourself.

A run that narrates a plan ("Implementing the backend first, then the frontend") and
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
  (`! grok …` in Claude Code) so its output lands in the conversation — then pick up at the review step of `delegate`.
  A durable fix is a shell allow-rule for `grok` in the host's project settings
  (Claude Code: `.claude/settings.json`; OpenCode: `permission.bash` in `opencode.json`).

Escalate at most twice, then stop and report. Never substitute your own implementation for Grok's
without the user saying so.
