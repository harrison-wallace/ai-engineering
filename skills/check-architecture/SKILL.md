---
name: check-architecture
description: Survey existing code and infra for deepening opportunities, places where a shallow module (an interface nearly as complex as what it hides) should become a deep one, so changes, bugs, and tests concentrate in one place. It scans the hot spots from git history, the area you name, or what a plan will touch (`for <plan>`), including pass-through Terraform modules, copied stacks, and scripts with hidden ordering. Sonnet explorers find candidates, the main agent proves each one (callers, interface size, the deletion test, and narrow `explain-why` on old decisions), and `deep` adds an Opus judge. The terminal report has at most 5 candidates with strength badges and ASCII before/after diagrams, and it can serve an HTML page on the LAN. Then one round of questions on the candidate you pick, and a hand-off to `design`. Never edits code. Triggers on "/check-architecture", "where should we refactor", "find shallow modules", "how can we make this change easy", or "architecture review of this repo".
argument-hint: "[lite|deep] [<path or area> | for <plan or phase doc>]"
disable-model-invocation: true
---

# check-architecture

Find where existing code or infra should be deepened, prove each case, and help you pick one.
**It never edits code.** It writes only a report page in the scratchpad, and glossary or ADR rows
through `define-terms` when you approve them.

`design` designs something new, and this skill finds what to restructure. `review-deep`
and `trace-impact` judge one change. This skill surveys the code that keeps changing.

Adapted from Matt Pocock's `improve-codebase-architecture` and `codebase-design` skills.

## Level

| First argument | Level | Explore | Judge |
|---|---|---|---|
| `lite` | lite | Main agent, inline | Main agent |
| none, or anything else | default | 2–3 Sonnet explorers, one per area | Main agent |
| `deep` | deep | 2–3 Sonnet explorers | One Opus judge at `high`, in a fresh context |

The main agent proves every candidate at every level (§5). Do not run `/effort` or `/model`. Set
`model` and `effort` on each Agent call only.

## 1. Read the arguments

| Target | Scope |
|---|---|
| none | The hot spots in git history (§3) |
| `<path or area>` | That path, or the code that implements the named area |
| `for <plan or phase doc>` | What the plan will touch. The question becomes "what would make this change easy?" |

`for` takes a file (`docs/phases/<id>.md`, a spec), a phase id, or "the plan" from this chat.

## 2. Context

- Read [`references/vocabulary.md`](references/vocabulary.md). Use its terms exactly, in every
  candidate and every question.
- **Glossary**: run `python3 -I ../define-terms/scripts/glossary.py <repo-root>` (relative to
  this skill's folder, resolved with `readlink -f`). Name candidates with the glossary's terms. No
  glossary → say so in one line, offer `/define-terms init` first, and go on with the names
  in the code unless the user takes the offer.
- **ADRs**: list `docs/adr/*.md` with each title and status. Read every ADR in scope. A `rejected`
  ADR is a candidate that must not come back.

## 3. Scope

- **Hot spots** (no target): run `<skill-dir>/scripts/hotspots.sh` from the repo root. It ranks the
  files and folders that changed most in the last 200 commits, skipping lockfiles, generated
  files, and docs. Take the 2–3 folders at the top. When the changes are scattered with no clear
  top, take the largest source folders, and say so.
- **`for <plan>`**: read the plan, list the modules and stacks it will touch (search for the
  names it uses), and scope to those.
- Not a git repo, with no target → ask for a path.

State the scope in one line before you explore.

## 4. Explore

**lite**: work through the checklist in
[`references/explorer-prompt.md`](references/explorer-prompt.md) yourself.

**default and deep**: launch one explorer per area in **one message**: `subagent_type: Explore`,
`model: sonnet`, `effort: medium`, `run_in_background: false`. Each one gets the full text of
`references/explorer-prompt.md`, with its area, the repo root, the vocabulary path, the glossary
terms, the ADR titles and statuses, and for `for <plan>` the plan's goal. It gets no chat history.

## 5. Prove (main agent, every level)

An explorer's candidate is a lead. Keep it only when you have proved it yourself:

1. **Read the files.** Confirm the interface: count what a caller must know (exports, parameters,
   variables and outputs, env vars, ordering rules).
2. **Count the callers** with `rg`. A module with one caller is rarely worth deepening.
3. **Run the deletion test.** Name where the complexity goes if the module is deleted: into one
   place (it was a pass-through, so merge it), or across N callers (it earns its keep, so leave it).
4. **Name the dependency kind** from the vocabulary. It decides how the deepened module is tested.
5. **Check the tests.** Which tests exist today, and which would cross the new interface.
6. **Check old decisions.** When an ADR explains the shape, read it and cite it. When a structure
   looks deliberate (a split that seems odd, a guard, a duplicate kept on purpose) and no ADR
   explains it, run a narrow `explain-why` on it: read `../explain-why/SKILL.md` and follow it at its
   default level, with one question, "why is <module> shaped this way?". Then:
   - It contradicts an `accepted` ADR → keep it only when the friction is real, and mark it
     `Reopens ADR-NNNN because <reason>`.
   - A `rejected` ADR covers it → drop it, and list it under **Already rejected**.
   - `explain-why` finds a reason that still holds → drop it, and say why under **Checked and left**.

Rate what survives:

| Strength | When |
|---|---|
| **Strong** | The deletion test clearly passes, the area is a hot spot or in the plan, and the friction has proof |
| **Worth exploring** | The deletion test passes, but the payoff depends on where the code goes next |
| **Speculative** | Plausible, with thin proof. List it in the table only |

**deep**: give the proved candidates and their proof to one judge: `subagent_type:
general-purpose`, `model: opus`, `effort: high`, with the full text of
[`references/judge-prompt.md`](references/judge-prompt.md). Apply its cuts and order. Do not raise
a strength it lowered.

## 6. Report (terminal)

At most 5 candidates. **Finding nothing is a valid result.** Never pad the list.

```markdown
**<n> deepening candidates in <scope>.** Top: <candidate>.

| # | Candidate | Strength | Dependency |
|---|---|---|---|
| 1 | Merge the Booking intake modules | Strong | in-process |
```

Keep the table to these 4 columns. A wider table renders as stacked cards in a terminal. Files and
wins go in each candidate's section.

Then, for each **Strong** candidate:

````markdown
### 1. <Candidate>

**Files:** `src/booking/{validate,price,save}.ts`
**Problem:** <one sentence: what hurts.>
**Solution:** <one sentence: what changes. No interface design yet.>

```text
BEFORE                                   AFTER
┌──────────┐  ┌──────────┐  ┌────────┐   ┌─────────────────────────┐
│ validate │→ │  price   │→ │  save  │   │ Booking intake          │
└──────────┘  └──────────┘  └────────┘   │  (validate, price, save │
  3 interfaces, 9 call sites              │   are internal)         │
                                          └─────────────────────────┘
                                            1 interface, 9 call sites
```

**Proof:** <callers counted, interface size, changes in the last 200 commits, tests today.>
**Wins:** <two or three, in vocabulary terms: locality, leverage, tests at the interface.>
**ADR:** <only when it reopens one: "Reopens ADR-0004 because …".>
````

Keep each diagram to 12 lines or fewer, and 100 columns or fewer. **Draw the shape**: the callers,
the copies, and where the rule lives, before and after. Do not draw a list of `file:line`
references. Those go in **Proof**. Then:

- **Worth exploring**: a short section each, with **Files**, the problem, and the proof, but no
  diagram.
- **Speculative**: one line each, with its files.
- **Already rejected**: candidates a `rejected` ADR covers, one line each.
- **Checked and left**: modules that looked shallow but passed the deletion test, or whose reason
  still holds, one line each. This shows what was covered.
- **Top recommendation**: the candidate to do first, and why, in one sentence.
- **Coverage**: `Scope: <scope>. <k> commits read. <n> explorers (<model>). <m> files read. ADRs read: <numbers>. explain-why: <n> runs.`

If every candidate is Speculative, say so: "Nothing strong enough to act on in <scope>."

Use the STE rules and the clear-reading checks in `../summarise/SKILL.md` §3.

End with: *"Which one do you want to explore? Reply `page` for an HTML page with before and after
diagrams, served on your LAN."*

## 7. LAN page (on request)

Follow [`references/lan-page.md`](references/lan-page.md) for what the page shows. It is built and
served by `serve-page`, on the first free port from 38081 to 38089. Stop the server when the user
says they are done, and at the end of the run at the latest.

## 8. One round, then `design`

When the user picks a candidate:

1. **Look up the facts first**: callers, tests, deploy units, and state that would move. Finding
   facts is your job. Do not ask the user for anything you can read.
2. **Ask one round** of at most 6 numbered questions, each with a recommended answer, in the format
   of `../define-terms/SKILL.md` §7. Cover what fits: the constraints, what goes behind the
   seam, the dependency kind and how many adapters it needs, which tests survive and which are
   replaced, what stays out of scope, and for infra how state moves (`moved` blocks, a
   `terraform state mv`, renamed containers or networks).
3. **Hand off.** Write a brief: the candidate, the files, the proof, the dependency kind, and the
   answers. A behaviour change found during the round, such as a missing audit entry, becomes its
   own slice in the brief, apart from the restructure, so a regression traces to one change. Then read `../design/SKILL.md` and follow it with this brief as the thing to
   design. It sketches the deepened module in two shapes and writes the `proposed` ADR.

Along the way:

- **A new term** came up, or a fuzzy one was sharpened → offer the glossary rows through
  `define-terms` (its §8).
- **The user rejects the candidate** for a lasting reason → apply the three tests in
  `../define-terms/SKILL.md` §6. When they pass, offer a `rejected` ADR, so the next run does
  not suggest it again. Skip short-term reasons such as "not now".

## Rules

- Never edit code, config, or infra. Never commit, stage, or push.
- Never propose an interface in the report. Interface design starts in `design`.
- Use the vocabulary exactly. Do not drift into "component", "service", "layer", or "boundary".
- Never keep a candidate you did not prove in §5.
- Always stop the LAN server you started. Kill only its own process.
