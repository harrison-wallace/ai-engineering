---
name: delegate
description: Implement the changes just discussed by routing the work to the right implementer. The main agent plans, assesses the task, recommends a route, and shows a menu with relative cost and time for each one (self, balanced, accuracy, a/b, speed, cheap, grok, mixed, multi). You pick, and then the main agent reviews, scores, fixes, and summarises. Grok routes use the latest Grok model through the headless CLI. Triggers on "/delegate", "/delegate <route>", "have sonnet implement this", "have grok implement this", "delegate this", or "implement this cheaply". Replaces imp-sonnet and imp-grok-4-7.
argument-hint: "[self|balanced|accuracy|a/b [grok-sonnet|sonnet-opus|sonnet-sonnet]|speed|cheap|grok|mixed|multi] [grok effort]"
allowed-tools: Bash(bash *scripts/grok-tier.sh)
---

# delegate

**You plan, an implementer you route to builds it, you review, score, and fix it, then report.**
Run the phases in order. Never skip the review, even when an implementer reports success.

## 1. Plan (main agent)

From the conversation so far, write a concrete plan:

- The goal in one or two sentences.
- Every file to create or change, with absolute paths and what changes in each.
- Conventions the code must follow, with one existing file cited as an example.
- Acceptance criteria: the commands to run, the behavior to expect, and the tests that must pass.
- **Units**: split the work into units that touch separate files, when it splits cleanly. A split
  route needs this. Units that share a file are one unit.

## 2. Assess and recommend

Judge the task on five points: its size, the risk if it is wrong, how mechanical it is, how much
it depends on this chat's context, and whether it splits into independent units. Then pick the
route that fits best.

**If the user named a route**, use it. Say in one line if you think another route fits better,
then go ahead with theirs.

**Otherwise**, show the plan briefly, then the menu, with your pick first and marked. Rate cost and
time **for this task**, relative to the other routes. The baseline below is a starting point, not a
rule. Then stop and wait for the user to pick a number or a name.

```markdown
**Recommended: 2. balanced**: <one line: why it fits this task>.

| # | Route | Who implements | Cost | Time | Fits when |
|---|---|---|---|---|---|
| 1 | self | The main agent, no subagent | $$ | ## | Small, or leans on this chat |
| 2 | balanced | Sonnet `medium` | $$ | ## | Most features |
| 3 | accuracy | Opus `high` subagent | $$$ | ### | Risky or core logic |
| 4 | a/b | Two implementers in separate worktrees | $$$ | ### | The best approach is unclear |
| 5 | speed | Parallel Sonnet `low`, one per unit | $$ | # | Many independent, mechanical units |
| 6 | cheap | Haiku with a tight brief | $ | ## | Well-specified, mechanical work |
| 7 | grok | Grok, latest model, headless | $ | ## | You want Grok, or a non-Claude implementer |
| 8 | mixed | Grok and Claude split the units, in parallel | $$ | # | A split task, using both families |
| 9 | multi | A Claude agent per unit, by type: Haiku, Sonnet, or Opus | $$ | # | Units of very different difficulty |
```

- **Cost** ($ to $$$) is the token cost to this account. Grok runs on its own account, so its cost
  here is only the plan and the review.
- **Time** (# to ###) is wall-clock time to a reviewed result.
- !`bash "${CLAUDE_SKILL_DIR}/../../scripts/grok-tier.sh"` When it is off, leave the Grok routes out of the menu and never recommend one. A Grok route the user names still runs.
- Leave out a route that cannot run: Grok routes when `grok` is missing or not signed in, and
  split routes when the work does not split. Say why in one line under the table.
- **Be honest about small tasks.** Writing the plan and reviewing the diff costs main-agent tokens
  too. When those cost about as much as doing the work, recommend `self` and say so. Never route
  away a task only to use a route.

## 3. Run the route

Build each implementer's brief from [`references/brief.md`](references/brief.md). For any Grok
implementer, follow [`references/grok.md`](references/grok.md) exactly. It covers the model, the
effort, the invocation, and what to do when a run does nothing.

Claude implementers use the Agent tool: `subagent_type: general-purpose`, the `model` and `effort`
in the table below, and `run_in_background: false`. Launch parallel implementers in **one
message**. Do not run `/effort` or `/model`.

| Route | How |
|---|---|
| **self** | Implement it yourself. Then check your own diff against the plan, and run the acceptance criteria. |
| **balanced** | One Sonnet agent, `effort: medium`. |
| **accuracy** | One Opus agent, `effort: high`. |
| **speed** | One Sonnet agent per unit, `effort: low`, all in parallel. Each unit runs its own acceptance check. Re-run only the failed units at `effort: medium`. |
| **cheap** | One Haiku agent. Make the brief tight: exact edits, exact paths, and exact checks. |
| **grok** | One headless Grok run, per `references/grok.md`. The effort argument goes to Grok (default `medium`). |
| **mixed** | Grok takes the units that are well specified, and one Sonnet agent (`medium`) takes the rest. Take a unit yourself instead when it leans on this chat's context. Run Grok and the Claude side in parallel. Each touches only its own files. |
| **multi** | Route each unit to the Claude agent that fits it: Haiku for mechanical edits, Sonnet `medium` for normal logic, and Opus `high` for the hardest unit. All in parallel. |
| **a/b** | See below. |

### a/b

Two implementers build the same plan in two separate worktrees. Then you compare them.

| Pair | Side A | Side B |
|---|---|---|
| `grok-sonnet` (default) | Grok, latest model | Sonnet `medium` |
| `sonnet-opus` | Sonnet `medium` | Opus `high` |
| `sonnet-sonnet` | Sonnet `medium`, premise **extend** | Sonnet `medium`, premise **reshape** (or the user's two briefs) |

When the Grok tier is off and the user names no pair, the default is `sonnet-opus`. Run
`grok-sonnet` only when the user names it.

1. **Make two worktrees** from the current state, so that both sides start from what the user sees:

   ```bash
   git -C <repo-root> worktree add --detach <scratchpad>/delegate/<slug>/wt-a HEAD
   git -C <repo-root> diff HEAD --binary > <scratchpad>/delegate/<slug>/base.patch
   ```

   Apply `base.patch` in each worktree with `git -C <wt> apply` (skip this when the patch is
   empty), and copy in the untracked files from
   `git -C <repo-root> ls-files --others --exclude-standard`. Then record the seed with
   `git -C <wt> add -A` and `git -C <wt> commit -qm seed`. This commit lives only in the temporary
   detached worktree, so it never touches the user's branch. Do the same for `wt-b`.
2. **Run both sides in parallel**, each with the worktree as its only working directory.
3. **Compare** `git -C <wt> diff HEAD` for each side, and run the acceptance criteria in each.
4. **Pick**: score both sides (§5), then choose the winner, or take the winner and port specific
   hunks from the loser. Say what you took from each side.
5. **Apply** the winner's diff to the user's tree with `git -C <repo-root> apply`. Then remove both
   worktrees with `git worktree remove --force`.

### Host

When this session runs under the Grok CLI instead of Claude Code, the Agent tool does not exist.
Run each Claude implementer as a headless process instead:

```bash
claude -p --model <sonnet|opus|haiku> --effort <level> \
  --permission-mode acceptEdits \
  --disallowedTools 'Bash(git commit*)' 'Bash(git push*)' 'Bash(git add*)' \
  < <scratchpad>/delegate/<slug>/brief-<implementer>.md \
  > <scratchpad>/delegate/<slug>/claude-<implementer>.log 2>&1
```

If `claude` is missing, offer only `self` and `grok`. Under the Grok host, `self` is the host
itself.

## 4. Review (main agent)

Never trust an implementer's report alone. **Capture the handover before you touch anything**,
because the scorecard grades what the implementer delivered, not what you repaired:

```bash
git -C <repo-root> diff > <scratchpad>/delegate/<slug>/raw.diff
git -C <repo-root> status --short > <scratchpad>/delegate/<slug>/raw.status
```

For a split route, sort the raw diff by unit, so that each implementer is graded on its own files.

- Read every change in the diff, and read the new files.
- Check it against the plan: anything missing, anything extra, and anything that breaks the repo's
  conventions.
- Run the acceptance criteria yourself.
- If an implementer committed despite the brief, say so plainly.

Do not fix anything yet. For `self`, skip the capture and do a careful self-review instead.

## 5. Score (main agent)

Score each implementer with [`references/scorecard.md`](references/scorecard.md). Skip this for
`self`, because grading your own work tells the user nothing.

## 6. Fix (main agent)

Fix what the review found with your own edits. Send work back to an implementer only when its part
is wrong as a whole. Fixes do not change the scorecard, because it records the handover.

## 7. Summarise

- **Plan**: the goal, in one line.
- **Route**: the route, each implementer with its model and effort, and why this route.
- **Implemented**: the files changed, by implementer.
- **Review**: what you checked, and what you fixed, or "no fixes needed".
- **Verification**: what you ran, and the result.
- **Scorecard**: the table and the headline for each implementer. For `a/b`, the side-by-side
  table and the winner.

Then, only if there is something concrete to say, one or two lines:

> **Note on the skill**: this would have gone better if the skill had X.

Zero notes is normal. A note is for something repeatable that belongs in the skill, such as a line
the brief should carry or a route rule. Never use it for a one-off model mistake, which is already
a score. Never edit this skill because of a note.

## Rules

- Leave the changes uncommitted unless the user asks otherwise.
- If a route fails (a run does nothing, times out, or is blocked), report exactly that before
  anything else. Never quietly implement it yourself in the route's place. Offer another route.
- Implementers never commit, push, or run other git writes. The only commits are the `seed`
  commits inside the temporary `a/b` worktrees.
