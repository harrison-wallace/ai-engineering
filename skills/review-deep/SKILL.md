---
name: review-deep
description: Deep technical review of a change, for when you want to understand it, not only clear it to commit. It explains what the change does (explain-how), checks the history it undoes (explain-why), sweeps what it breaks outside the diff (the trace-impact method), runs the repo's tests and validators read-only, and has Sonnet lens reviewers (correctness, security and data, ripple) look with fresh eyes. The main agent verifies every lead. Report-only, on review's 1–3 scale. Triggers on "/review-deep", "/review-deep staged", "/review-deep branch", "review this properly", or "deep review of this change". Optional leading level. Use review for a quick pre-commit check.
argument-hint: "[lite] [staged | branch [<base>] | <paths>]"
disable-model-invocation: true
---

# review-deep

A deep, technical review of one change. It explains what the change does, why the old code was
the way it was, and what the change could break. Each finding comes with how it was proven.
**Report only. Never fix, commit, or start anything.**

`review` answers "can I commit this?" in one quick pass. `review-deep` answers "what
does this change really do, and what could it break?" Both use the same severity scale, so you
can compare their verdicts.

## Level

| First argument | Level | Lenses | `explain-how` and `explain-why` |
|---|---|---|---|
| `lite` | lite | The main agent runs each lens itself, one after another | At `lite` |
| none, or anything else | default | 2–3 Sonnet lens reviewers in parallel | At their own default |

Do not run `/effort` or `/model`. Set `model` and `effort` on each Agent call only. Never go above
Sonnet for a lens reviewer.

## Sibling skills

This skill reuses four sibling skills. They have `disable-model-invocation`, so do not call them
with the Skill tool. Read their files and follow the named parts in place. The paths are relative
to this skill's folder. Resolve the folder with `readlink -f` if it is a symlink.

| File | Parts used |
|---|---|
| `../review/SKILL.md` | §1 scope rules, §2 B mechanical sweep, §2 E verify, §3 what counts and the severity table |
| `../explain-how/SKILL.md` | The whole skill, on the changed area |
| `../explain-why/SKILL.md` | The whole skill, on one narrow question per old decision |
| `../trace-impact/SKILL.md` | §2–§5, with `references/where-grep-stops.md` and the running rules |

## 1. Scope

Use `review` §1, with these additions:

- `branch` → everything since the branch left `<base>` (default `main`), committed or not:
  `git diff $(git merge-base <base> HEAD)`, plus untracked files. If `<base>` does not exist, use
  the remote's default branch, and say so.
- A leading `lite` is the level, not a path.

Write the diff to `<scratchpad>/review-deep/<slug>/diff.patch`.

## 2. Brief (main agent)

Before any subagent starts:

1. **Intent**: one sentence, per `review` §2 A.
2. **Mechanical sweep**: `review` §2 B on the added lines.
3. **Changed names**: every symbol, route, env var, config key, column, event, file path, and infra
   name that the diff adds, removes, or renames.
4. **Old decisions it undoes**: each place where the diff deletes or loosens something that was
   there on purpose. That includes a guard, a retry, a timeout, a threshold, a test, an
   `ignore_changes`, a health check, a limit, or a permission check. Write one narrow `why`
   question for each, for example "why was the retry on `fetchRoster` added?". Keep at most 3. If
   there are more, keep the 3 with the most to lose.
5. **Domain**: software, infra, or both.

Write the brief to `<scratchpad>/review-deep/<slug>/brief.md`: intent, scope, changed names,
domain, and the diff path. Leave out the chat, the author's reasons, and your own guesses. The lens
reviewers get only this, so that they do not inherit the author's story.

## 3. Fan out

**default**: launch everything that applies in **one message**:

| Agent | When | Call |
|---|---|---|
| **Correctness lens** | Always | `Explore`, `model: sonnet`, `effort: medium` |
| **Security and data lens** | Always | `Explore`, `model: sonnet`, `effort: medium` |
| **Ripple lens** | The diff changes a shared name: a contract, route, schema, env var, network, volume, hostname, Terraform output, or a symbol other repos may use | `Explore`, `model: sonnet`, `effort: medium` |
| `explain-how` explorers | The change spans more than one module or service | Per `explain-how` §2 |
| `explain-why` digger | Step 2 found an old decision it undoes. One digger for each question | Per `explain-why` §3 |

Set `run_in_background: false` on every call. Each lens prompt is the full text of
[`references/lens-prompt.md`](references/lens-prompt.md), with its lens section, the brief path,
the diff path, the repo root, and the resolved skills folder (`{SKILLS_DIR}`, the parent of this
skill's folder) filled in. Do each sibling skill's main-agent steps (the
`explain-why` anchor and in-repo sweep) before this message.

When the diff changes no shared names, run the ripple check yourself, per `review` §2 D.

**lite**: run no subagents. Work through the three lens sections of `references/lens-prompt.md`
yourself, one after another, and run `explain-how` and `explain-why` at `lite`.

## 4. Run the checks

While the agents work, or after them, run the repo's own checks. Find them in `AGENTS.md`,
`CLAUDE.md`, `package.json` scripts, a `Makefile`, `justfile`, or CI config:

- Tests, typecheck, and lint that the repo already defines.
- Infra: `terraform fmt -check` and `terraform validate` in an initialized directory only,
  `docker compose config`, `shellcheck`, `nginx -t`, or `promtool check`.

Follow `trace-impact` §5 running rules: read-only, never `apply`, `init`, `up`, a deploy, or a
migration against a real database. The repo's `AGENTS.md` wins. Do not install dependencies. If a
check needs them, record "not run: dependencies not installed". Record each command, its result,
and the lines of output that matter. A check that fails on code the diff did not touch is a note,
not a finding.

## 5. Verify and merge (main agent)

Lens reports hold **candidates**, not findings. For each one:

1. Run `review` §2 E: reopen the line, write the failure path, and check that nothing
   already handles it.
2. Push the proof as far as is cheap, on `trace-impact`'s ladder: pointed at it, walked it, or ran
   it.
3. Rate it with `review` §3. Use the same types and the same 1–3 scale.

A candidate that passes becomes a finding. A candidate you could neither prove nor disprove goes
under **Leads not confirmed**. A candidate you disproved is dropped. Count it in the coverage line.

Merge the `explain-why` answers into **History at risk**. When the history shows that the deleted
thing guarded a real case, and the diff does not cover that case another way, it is also a finding.

## 6. Report

Print these sections in order. Leave out a section that is empty. The first three sections must
read in 30 seconds.

### Verdict

The same call and counts as `review` §4, for example:
`**Fix before commit.** 3 findings: 1 sev-3, 2 sev-2.`

### What the change does

Two to five sentences from `explain-how`: what the code did before, what it does now, and the
mechanism. Add an ASCII diagram when the change alters a flow, with "before" and "after" side by
side or one after the other.

### Findings

| Sev | Type | Location | Problem | Fix | Proof |
|---|---|---|---|---|---|

The first five columns follow `review` §4. `Proof` is one of `read`, `walked`, `ran <check>`,
`grep`, or `git`. Print at most 15 rows. Drop severity 1 first.

### Details

For each severity-3 and severity-2 finding, a short block:

- **Failure path**: the input or state, each step, then the wrong result.
- **Evidence**: the lines, the command output, or the history.
- **What would prove this wrong**: the one fact that would clear it.

### History at risk

For each old decision from step 2: what it was, the `explain-why` finding with its tier and citation,
and a **Preserve / Change / Avoid / Risk** row. Keep `explain-why`'s confidence words as they are.

### Ripple

What breaks outside the diff, with `file:line` in the other repo, and the safety fact with the
ladder level it reached. Then the names you checked and cleared, in one line.

### Checks run

One line for each check: the command, then `pass`, `fail`, or `not run: <reason>`.

### Leads not confirmed

One line each: the lead, and what would settle it.

### Coverage

`review`'s coverage line, plus: the lenses that ran, the number of candidates dropped, and
the sibling skills used.

Then one line: *"Want to understand it properly? `/teach` this change. Or reply `page` for the
report with before and after diagrams, served on your LAN."*

### Page (on request)

When the user replies `page`, read `../serve-page/SKILL.md` (relative to this skill's folder, resolved with `readlink -f`) and follow its §1 to §4. Write `<scratchpad>/review-deep/<slug>/index.html`.
The page shows the verdict, **What the change does** with its before and after flow as a
diagram, one card per finding with its proof, the history at risk, the ripple as a small map, and
the checks run. Stop the server when the user says they are done.

## Rules

- Report only. Never fix, commit, push, apply, or deploy.
- Cite only lines you opened. Never invent a caller, an API, a resource, or a test result.
- A false finding is worse than a missed one. Leads you cannot prove go under Leads not confirmed,
  not in the table.
- Subagents start cold. Give them absolute paths and the brief, not the chat.
