---
name: improve
description: Look at one existing area (a feature, a service, or an infra stack) from first principles and find what to fix, simplify, or deepen, then drive the chosen change through the other skills. It grounds in what the area is for, runs five lenses (simplify, deepen, data shape, ops and cost, docs drift), proves every finding, and routes each one to its next skill (research, trace-impact, design, prototype, delegate, or advise). A question after the area narrows the lenses to it. `auto` also runs `research lite` and `trace-impact` without asking. It never edits code before your yes. Report in the terminal, a LAN page on request, and a save to docs/improve/. Triggers on "/improve <area>", "/improve <area> <question>", "what would you change in X", "how could X be simpler", or "improve this service".
argument-hint: "[lite|deep] <area> [<question>] [auto] [aws]"
disable-model-invocation: true
---

# improve

Look at one area that exists today and ask what it is for. Then find what to fix, cut, or
reshape, prove each finding, and hand each one to the skill that resolves it. **It never edits
code itself.** Only `delegate` edits code, and only after your yes.

Not for: one reported failure (`/diagnose`), a change or a diff (`/review`, `/review-deep`),
something new (`/design`), how the area works with no judgement (`/explain-how`), or one lens on
its own (`/check-architecture` for deepening, `/check-primitives` for data shape).

## Level

| First argument | Level | Lenses | Judge |
|---|---|---|---|
| `lite` | lite | The main agent runs each lens itself | Main agent |
| none, or anything else | default | 2–3 Sonnet lens readers in parallel | Main agent |
| `deep` | deep | 2–3 Sonnet lens readers | One Opus judge at `high`, in a fresh context |

The main agent proves every finding at every level (§5). Follow the Model routing rules in this
repo's `CLAUDE.md`. Do not run `/effort` or `/model`. Never go above Opus `high`.

## Sibling skills

Most siblings have `disable-model-invocation`, so do not call them with the Skill tool. Read their
files and follow the named parts in place. The paths are relative to this skill's folder. Resolve
the folder with `readlink -f` if it is a symlink.

| File | Parts used |
|---|---|
| `../explain-how/SKILL.md` | The whole skill at `lite`, on the area (§2) |
| `../explain-why/SKILL.md` | The whole skill, on one narrow question per old decision (§5) |
| `../check-architecture/references/vocabulary.md` and `explorer-prompt.md` | The deepen lens |
| `../check-primitives/references/signs.md` | The data-shape lens |
| `../update-docs/SKILL.md` | `<paths> scan` on the area's docs: the docs-drift lens |
| `../aws-audit/SKILL.md`, `../aws-cost/SKILL.md` | Only with `aws`, behind their own cost gates |
| `../research/SKILL.md`, `../trace-impact/SKILL.md`, `../design/SKILL.md`, `../delegate/SKILL.md` | The chain (§7) |

## 1. Read the arguments

- **Area**: a path, a service or a feature name, or an infra stack. Resolve a name to its paths
  with `rg` and the repo layout. State the scope in one line. Not found → ask for a path.
- **Question**: any free text after the area. Answer it first in the report, and run only the
  lenses that bear on it. Say which lenses you dropped, in one line.
- `auto`: run the read-only links of the chain without asking (§7).
- `aws`: add the AWS sweeps to the ops-and-cost lens. Without `aws`, never call AWS.

## 2. Ground (main agent)

1. **What it is for.** Follow `explain-how` at `lite` on the area. Write the area's job in one
   sentence, its inputs and outputs, and who calls it. Every finding is judged against this job.
2. **Old decisions.** List `docs/adr/*.md` with titles and statuses, and read the ones in scope. A
   `rejected` ADR is a finding that must not come back. Read `CLAUDE.md` and `AGENTS.md` for the
   rules.
3. **Churn.** Run `git log --format= --name-only -200 -- <paths> | sort | uniq -c | sort -rn | head`.
   Files that change often are where a finding pays off.

## 3. Lenses

| # | Lens | Asks | Method |
|---|---|---|---|
| 1 | **Simplify** | What is the least that does this job? What can go? | Dead code, flags and config nobody sets, an abstraction with one implementation, a layer that only passes calls on, two paths that do one thing. The deletion test |
| 2 | **Deepen** | Is an interface nearly as complex as what it hides? | `check-architecture` vocabulary and explorer checklist |
| 3 | **Data shape** | Do rules live in `if`s and flags instead of in a structure? | `check-primitives` signs, on the area's files in full |
| 4 | **Ops and cost** | How does it fail, and what does it cost? | Timeouts, retries, limits, single points, alarms, growth with no bound, the cost drivers. With `aws`: `aws-audit` and `aws-cost optimize` |
| 5 | **Docs drift** | Do the docs still tell the truth? | `update-docs <the area's doc paths> scan` |

Skip lens 4 for a pure library with no runtime, and say so.

**lite**: run each lens yourself, with [`references/lens-prompt.md`](references/lens-prompt.md) as
your checklist.

**default and deep**: launch the lens readers in **one message**: `subagent_type: Explore`,
`model: sonnet`, `effort: medium`, `run_in_background: false`.

- Reader A: lenses 1 and 2. Reader B: lens 3. Reader C: lens 4, only when it applies.
- Each reader gets the full text of `references/lens-prompt.md`, with its lens sections, the
  scope, the job sentence, the repo root, the ADR titles and statuses, the question, and the
  skills folder (this skill's parent folder, resolved with `readlink -f`). It gets no chat history.
- Run lens 5 yourself while they work.

## 4. AWS (only with `aws`)

Read `../aws-audit/SKILL.md` and `../aws-cost/SKILL.md`. Follow their gates exactly: the profile
check, and the cost notice before any Cost Explorer call. Limit the sweep to the resources the
area owns. A finding from them joins lens 4.

## 5. Prove (main agent, every level)

A reader's lead is not a finding. Keep it only when you prove it yourself:

1. **Read the files** and cite `path:line`.
2. **Count the callers** with `rg`. Name what breaks, or what goes away.
3. **Run the deletion test** for a simplify or deepen lead: where does the complexity go if this
   part is deleted?
4. **Check the tests**: which exist today, and which would cover the change.
5. **Check old decisions.** When a shape looks deliberate and no ADR explains it, read
   `../explain-why/SKILL.md` and follow it with one question, "why is <part> this way?". A reason
   that still holds drops the lead, under **Checked and left**. A `rejected` ADR drops it, under
   **Already rejected**. An `accepted` ADR keeps it only with `Reopens ADR-NNNN because <reason>`.

Give each finding a **kind** (Fix, Simplify, Deepen, Reshape, Harden, Cut cost, or Docs) and a
**strength**:

| Strength | When |
|---|---|
| **Strong** | Proved, in a file with churn or on the area's main path, and the payoff is clear |
| **Worth exploring** | Proved, but the payoff depends on where the area goes next |
| **Speculative** | Plausible, with thin proof. One line in the report only |

Then give each finding its **next skill** from the table in §7.

**deep**: give the proved findings and their proof to one judge: `subagent_type:
general-purpose`, `model: opus`, `effort: high`, with the full text of
[`references/judge-prompt.md`](references/judge-prompt.md). Apply its cuts and its order. Never
raise a strength that it lowered.

## 6. Report

At most 5 findings, Strong first. **Finding nothing is a valid result.** Never pad the list.

```markdown
**Area:** <scope>. **Job:** <the one sentence from §2>.

**Answer:** <only with a question: the direct answer in two to four sentences, with `path:line`.>

| # | Finding | Strength | Next |
|---|---|---|---|
| 1 | Merge the two retry wrappers | Strong | `delegate` |
```

Keep the table to these 4 columns. Then, for each Strong finding:

```markdown
### 1. <Finding, as an action>
**Kind:** Simplify · **Files:** `src/net/{retry,fetch}.ts`
**Problem:** <one sentence: what hurts, against the job.>
**Change:** <one sentence: what changes. No interface design yet.>
**Proof:** <callers, the deletion test, churn, the tests today.>
**Next:** <the skill, and why it is the right one, in one sentence.>
```

Add a before-and-after diagram of 12 lines or fewer for a structural change, in the style of
`../check-architecture/SKILL.md` §6. Then, one line each: **Worth exploring**, **Speculative**,
**Already rejected**, and **Checked and left**. End with:

```markdown
**Coverage:** <level>. Lenses: <run> (<dropped, and why>). <n> readers (<model>). <m> files read. ADRs read: <numbers>. explain-why: <n> runs. AWS: <used | not asked>. Auto: <links run | off>.
```

Use the STE rules and the clear-reading checks in `../summarise/SKILL.md` §3.

Then the offers, each on its own line:

- *"Reply with the numbers to run their next skill, for example `run 1 3`."*
- *"Reply `page` for the findings on your LAN."*
- *"Save this as Markdown in `docs/improve/`?"*

## 7. Chain

Each finding goes to one next skill:

| The finding needs | Next | Gate |
|---|---|---|
| An outside fact: a library limit, a price, a known bug | `research lite <the question>` | Runs with `auto`. Else on approval |
| Proof that a change is safe outside its files | `trace-impact` on the planned change | Runs with `auto`. Else on approval |
| A choice of shape between two or more ways | `design`, with the finding as its brief | On approval |
| A question that only running code can settle | Offer `/prototype <the question>`. It is user-invoked | The user runs it |
| A clear change, with its proof | `delegate`, with the finding as its plan. Then offer `/review-deep` | On approval |
| A rank against the project's plan | `advise`, with this report as its input | On approval |

- **`auto`**: run the research and trace-impact links before you show the report. Feed their
  results back into §5. A link can change a strength, a next skill, or cut a finding. For
  research, the user's `auto` approves the §4 plan of a `lite` run. Show the plan in one line,
  then go.
- **On approval**: read the next skill's `SKILL.md` and follow it, with the finding, its files,
  and its proof as the input. Run one finding at a time, in the user's order.
- Stop at every gate that the next skill has. Never skip one.

## 8. Page and save

- **Page**: follow [`references/lan-page.md`](references/lan-page.md). Stop the server when the
  user is done, and at the end of the run at the latest.
- **Save**: on a yes, write `docs/improve/YYYY-MM-DD-<slug>.md` in the current repo. The first
  line is the `#` title. Add no frontmatter. Do not commit or stage it.

## Rules

- Never edit code, config, or infra in this skill. Only `delegate` edits code, after a yes.
- Never keep a finding that you did not prove in §5.
- Judge every finding against the job sentence from §2. A change that does not serve the job is
  not an improvement.
- Never call AWS without `aws`. Never skip a sibling skill's own gate. The one exception is the
  research plan gate under `auto` (§7).
- Always stop the LAN server that you started. Kill only its own process.
