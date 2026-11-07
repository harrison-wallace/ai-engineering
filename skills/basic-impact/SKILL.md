---
name: basic-impact
description: Find what a change could break outside its own diff, for software, infra, or both — across every repo in ~/git — and prove the one fact it is safe because of by running real, read-only code or commands instead of asserting it. Report-only. Use for a change you don't trust, or before making one. Triggers on "/basic-impact", "/basic-impact staged", "blast radius of X", "what could this break", or "impact of renaming X". Optional leading level.
argument-hint: "[deep] [staged | <commit or range> | <paths> | <planned change>]"
disable-model-invocation: true
---

# basic-impact

Find what a change breaks **somewhere else**, then prove the one fact that makes it safe.
**Report only. Never fix, apply, or start anything.**

Listing callers is not the job, because grep does that in a second. The job is the breakage
grep does not show. A write-up that sounds right is worth nothing, since it reads as convincing
whether it is true or not. So find the one or two facts the change depends on, and **prove them
by running something**.

Inspired by the pstack `blast-radius` skill, with infrastructure, a sweep across all repos, and
read-only live checks added.

Use `/basic-review` for an everyday check of the diff. Use this skill when a change touches
shared things (a contract, a schema, a network, state, a hostname) or when you do not trust it.

## Level

| First argument | Level |
|---|---|
| none | Inline. The main agent does all of it. A single Haiku Explore agent triages the sweep only when it returns a large number of hits. |
| `deep` | Also run one Sonnet second opinion in parallel: [`references/second-opinion.md`](references/second-opinion.md), with `subagent_type: Explore`, `model: sonnet`, `effort: medium`, `run_in_background: true`. |

Never go above Sonnet in this skill. Do not run `/effort` or `/model`.

## 1. Read the change

Choose the scope, in this order:

- `staged` → `git diff --cached`.
- A commit or range → `git diff <range>`.
- Named paths → the working diff for those paths.
- A pasted `terraform plan` → the plan itself, plus the `.tf` files it names.
- A planned change in words ("rename the proxy network") → no diff exists. Find the current
  definition and treat the change as the hypothesis.
- Otherwise → the working tree, `git diff HEAD` plus untracked files, as `/basic-review` does.

Write down three things:

- **What it does**, including the part the diff does not spell out: a changed default, new
  ordering or timing, a widened type, a renamed resource that Terraform will destroy and recreate.
- **Changed names**: every symbol, route, env var, config key, column, event, file path, and
  every infra name (network, volume, container, hostname, bucket, Terraform resource address and
  output, IAM ARN, secret name, cron path, image tag).
- **Domain**: software, infra, or both.

**deep**: launch the second opinion now, in the background, with the scope and the changed names
only. Do not send your own conclusions, so that it cannot anchor on them.

## 2. Find the one fact it is safe because of

Most changes that look risky are safe because of **one fact**. For example: "the old route has
no callers outside this repo", "Terraform updates this in place and does not replace it", or "no
other compose project joins this network". If that fact holds, most of the risky cases clear at
once. Spend your time here, not on a long list of maybes. If no single fact makes it safe, say
so. That is a finding too.

## 3. Look where grep stops

**Sweep every repo.** Run `rg` once over `~/git` for each changed name (fixed-string, whole word
where it makes sense):

```bash
cd ~/git && rg -n -F -w --hidden -g '!.git' -g '!node_modules' -g '!dist' -g '!build' \
   -g '!.terraform' -g '!*.lock' -g '!*-lock.*' -g '!*.min.*' -g '!/plugins/**' '<name>' .
```

Run it from `~/git` with `.` as the path. The leading `/` in `!/plugins/**` anchors it to
`~/git/plugins`, which holds clones of upstream code, not your repos. With an absolute search
path the exclude does not match. Read every hit outside the changed repo.
If the hits are many (about 30 or more across five or more repos), send the hit list to one Haiku
Explore agent (`model: haiku`). Ask it to sort each hit as `consumer`, `mention only`, or
`unrelated`, citing `file:line`. Read the consumers yourself.

Then work through [`references/where-grep-stops.md`](references/where-grep-stops.md) for the
domain: the software list, the infra list, or both. Only the items that apply.

## 4. Rate each risk honestly

For each risk, state how it breaks, a real `file:line` (or a resource address, or a command
output), how **likely** it is, and how **bad** it would be. Keep the ones you confirmed. List the
ones you checked and cleared separately. Rules:

- Cite only lines you opened. A search that finds nothing is still an answer: say what you
  searched for and where.
- Never invent a caller, a consumer, an API, or a resource.

## 5. Prove the fact

Push each safety fact as far down this ladder as is cheap, and say where it stopped:

| Level | Software | Infra |
|---|---|---|
| 1. Said so | Worthless on its own. | Worthless on its own. |
| 2. Pointed at it | A real `file:line`, or the library's own source at the pinned version. | The `.tf`, compose, or pipeline line, or the provider docs for the pinned version. |
| 3. Walked it | You traced the bad case step by step, and it does not reach. | The plan logic: update or replace, `lifecycle`, `prevent_destroy`, `depends_on`, and what reads the output. |
| 4. Ran it | A small script in the scratchpad that imports the real module and fails loudly if you are wrong. | A read-only check: `terraform validate`, `terraform plan -lock=false -input=false`, `docker compose config`, `nginx -t`, `promtool check`. |
| 5. Saw it live | Reproduced in the running app. **Print the command for the user.** Do not start or serve anything. | Read-only live state: `docker network inspect`, `docker ps`, `aws … describe/list/get`, `curl -fsS` on a health URL, `dig`, `crontab -l`. |

### Running rules

- **Read-only only.** Allowed: `validate`, `fmt -check`, `plan -lock=false` (only in an already
  initialized directory, with no `-out` inside the repo), `state list/show`, `inspect`, `ps`,
  `ls`, `logs --tail`, `describe`, `list`, `get`, `GET` requests, `dig`, `status`.
- **Never** run any of these: `apply`, `destroy`, `init`, `import`, `state mv/rm`, `refresh`, `up`,
  `down`, `restart`, `rm`, `run`, `exec` with side effects, `put`, `delete`, `create`, `POST`, a
  deploy, or a crontab edit. If proof needs one of them, print it for the user as a `! <command>`
  line instead.
- **The repo's `AGENTS.md` wins.** If its permitted or prohibited actions forbid a command,
  even a read-only one, print it for the user instead of running it.
- Write proof scripts to `<scratchpad>/basic-impact/`, never into the repo. Paste the command and
  the relevant output.
- A permission denial is not a failure. Print the command for the user and mark the fact
  unproven at the level you reached.

**deep**: when the second opinion returns, merge it. A risk it found that you did not is a lead:
verify it under step 4 rules before it becomes a row. Note in the coverage line where you and
the second opinion disagreed on the safety fact.

## 6. Report

Print exactly these parts, in order. No preamble, and no recap.

**Verdict** (one line):

| Situation | Call |
|---|---|
| A confirmed sev-3 risk | `**Will break.**` |
| A confirmed sev-2 risk | `**Risky: check before merge.**` |
| Safety fact at level 4 or 5, no sev-2 or sev-3 risk | `**Safe: proven (level N).**` |
| Safety fact at level 2 or 3 | `**Likely safe: unproven (level N).**` |
| No single fact makes it safe | `**No safety fact: see risks.**` |

**What it does**: two sentences at most, including the part that is not obvious.

**Safe because**: the fact in one sentence, the level it reached, then the proof (the command and
its output, or the script and its output), in a code block.

**Risks** (only confirmed ones, and only when there is at least one):

| Sev | Where | How it breaks | Likelihood | Check |
|---|---|---|---|---|
| 3 | `other-repo/compose.yml:14` | When the network is renamed, this stack's proxy joins nothing and its site goes down. | High | `! docker network inspect proxy` |

- Sev uses `/basic-review`'s scale: 3 will break, 2 real risk, 1 small cost.
- Where is a `path:line` (other repos included), a resource address, or a host.
- How it breaks is one sentence: `When <condition>, <wrong result>.`
- Likelihood is `High`, `Medium`, or `Low`, with a reason when it is not obvious.
- Check is the cheapest command or test that would confirm it.
- At most 8 rows. Drop sev-1 rows first.

**Cleared**: one line each. What you checked, and why it is fine (the `file:line` or the
command output).

**Before you merge**: the cheapest checks that would catch the real bug, as commands. Use
`! <command>` for anything the user must run. Include the path to any proof script you wrote.

**Coverage**: one plain line, `Scope: <scope>. Swept <n> repos for <m> names. Proof: level <N>.`
Add `Second opinion: agreed`, or `Second opinion: disagreed on <x>`, for `deep`.

Write in short, plain sentences. Never fix, commit, push, or apply anything.
