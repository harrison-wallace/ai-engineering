---
name: check-primitives
description: Check code for missing primitives, where the domain lives in conditionals instead of in a data structure. It finds flags that must agree, phase checks spread across files, a branch added for each new kind, the same switch in two files, optional fields that depend on each other, loose shapes repeated, step-named modules, two writers of one state, and in React, `useState` clusters, stored derived state, state with two owners, and boolean props that exclude each other. Each finding names the invalid state or the repeated rule, and the primitive that removes it (a union, a state machine, a reducer, a registry, a typed model). `diff` (default) checks only what the current changes add or grow, and paths check those files in full. Report-only. Then it offers `/design` for a shape change. Triggers on "/check-primitives", "/check-primitives <paths>", "is this missing a state machine", "should this be a union", or "check the data shape of this diff".
argument-hint: "[diff | staged | <paths>]"
---

# check-primitives

Find code where the rules of the domain live in `if`, `switch`, and flags instead of in a data
structure. A structure that matches the domain makes invalid states impossible to write and
deletes branches. It is cheap to choose when the code is new. Later it reads as a refactor and
gets put off. So the default scope is the diff.

**Report only.** Never edit code, and never commit.

The full list of signs, with leads and primitives, is in
[`references/signs.md`](references/signs.md). Read it before you scan. Each sign has a stable ID
(S1–S3, D1–D5, M1–M2, R1–R4), and the report uses those IDs.

Adapted from pstack `principle-model-the-domain` and `principle-foundational-thinking`.

Not for: bugs on a path that exists today (`/review`), modules whose interface is nearly as large
as what they hide (`/check-architecture`), or the names of things (`/define-terms`).

## 1. Scope

| First argument | Scope |
|---|---|
| none, or `diff` | The working diff, or the last commit when the tree is clean, plus untracked files. Collect it as `../review/SKILL.md` §1 does (relative to this skill's folder, resolved with `readlink -f`) |
| `staged`, or `diff staged` | Only `git diff --cached`, which is what the next commit holds. Leave out unstaged and untracked files |
| one or more paths | Every source file under those paths, in full |

In `diff` scope, a sign counts only when the diff **adds or grows** it: a new flag, a new branch,
a new site of the same switch, a new optional field, a new `useState`. A pattern the diff does not
touch is not a finding. Count it for the coverage line.

Skip lockfiles, generated files, vendored trees, minified bundles, and test fixtures.

## 2. Find leads

Read `references/signs.md`. For each sign, search the scope for its lead. In `diff` scope, search
the added lines (`git diff HEAD -U0 | grep '^+'`, with the same base as §1), then open each
enclosing function or component. Useful searches:

```bash
git diff HEAD -U0 | grep -nE '^\+.*\b(is|has|should)[A-Z][A-Za-z]*\b'           # S1, R4
git diff HEAD -U0 | grep -nE '^\+.*(case |else if|\? .* : .* \? )'               # D1
git diff HEAD -U0 | grep -nE '^\+.*\?: '                                         # D3
git diff HEAD -U0 | grep -nE '^\+.*(useState|useReducer|useEffect|useSearchParams)\(' # R1–R3
```

For D2, S2, M2, and R3, take each discriminant, status name, or state key the lead found, and
search the whole repo: `git grep -nw '<name>'`. The sign is the second site, which is often
outside the diff.

## 3. Prove each lead

A lead becomes a finding only when you can write all three of these:

1. **The rule the code fails to hold.** For a state sign, write one invalid state that the type
   or the code allows, as a concrete value: `{ isLoading: true, error: "timeout" }`. For a branch
   sign, write the edit that the next kind needs: "a new plan adds a `case` in `pricing.ts`,
   `limits.ts`, and `PlanBadge.tsx`".
2. **The sites.** Every file and line that holds a copy of the rule or a branch on the kind.
   Open each one and read the line you cite.
3. **The primitive.** The structure from `signs.md` that removes it, shaped for this code: the
   union members, the states and transitions, the registry key, or the typed model's fields.

Then apply the "Do not flag" list in `signs.md`. If the primitive removes no branch, no repeated
rule, no invalid state, and no lifecycle risk, drop the lead. A false finding costs more than a
missed one.

When the invalid state is reachable today and gives a wrong result, it is a bug. Say so in the
finding, and offer `/review` or `/diagnose` for it.

## 4. Report

Print the verdict, the table, the primitive sketches, and the coverage line, in that order.

### Verdict

One line: `**No missing primitives.**`, or `**<n> missing primitives.** <s> strong, <w> worth a
look.`

| Strength | When |
|---|---|
| **Strong** | An invalid state is reachable, or the diff adds the second or a later site of the same rule |
| **Worth a look** | The sign is real and local, but the payoff depends on whether the area grows |

### Table

| Strength | Sign | Location | Rule the code fails to hold | Primitive |
|---|---|---|---|---|
| Strong | S1 | `app/upload/page.tsx:14` | `{ uploading: false, error: null, done: false, file: null }` after a cancel shows the empty form with a spinner. | Union `status: "idle" \| "uploading" \| "done" \| "error"`. |

- Sort by strength, then by sign ID, then by location. One row per rule. Name the other sites in
  the rule cell.
- Rule and Primitive cells are one sentence each, 25 words or fewer, with no line break.
- At most 8 rows. Drop "Worth a look" rows first.

The example row shows the shape. Do not copy it into a real report.

### Primitive sketches

For each Strong row, a short code block, at most 12 lines, that shows the primitive in the
repo's language: the type, and one call site rewritten. It is a sketch, not a patch.

### Coverage

One line: `Checked <count> files (<scope>). Signs searched: S1–S3, D1–D5, M1–M2[, R1–R4].` Add
`R1–R4` only when the scope has React code. Then, when they apply:

- `<n> leads dropped by the do-not-flag list.`
- `<n> untouched patterns seen outside the diff.` In `diff` scope only.
- `Bugs: <IDs>. Run /review.` When §3 found a reachable invalid state.

## 5. Next steps

Offer, in one line each, only what fits the findings:

- A finding inside one file or component: "Fix it in place, or `/delegate` it."
- A finding that spans modules, owners, or a public type: "`/design lite <rule>` to shape the
  primitive and record it in an ADR."
- A primitive whose behaviour talk cannot settle, such as a state machine with many transitions:
  "`/prototype logic <question>` to click through it."

Then stop.

## Rules

- Never edit code, never commit, and never run the code under check.
- Cite only lines you have opened. Every finding names a concrete invalid state or a concrete
  next edit, not a style preference.
- Do not report a finding of `/review` or `/check-architecture` here. Point to the skill instead.
