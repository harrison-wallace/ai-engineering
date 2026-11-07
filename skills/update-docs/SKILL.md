---
name: update-docs
description: Keep the docs true to the code. It finds statements in the README, docs, CONTRIBUTING, AGENTS.md, CLAUDE.md, and .env.example that the code has made wrong (renamed flags, removed scripts, dead paths and links, moved ports, stale counts and versions, undocumented env vars), proves each one, and fixes it in place by default. `diff` (default) checks only what the current changes broke, `repo` audits every doc, and `scan` reports without editing. Docs that other skills own (CHANGELOG, phase docs, ADRs, summaries) are flagged, not rewritten. Undocumented things are flagged, not written. Triggers on "/update-docs", "/update-docs repo", "/update-docs scan", "are the docs up to date", "update the docs", or "fix stale docs".
argument-hint: "[diff | repo | <paths>] [scan]"
---

# update-docs

Find what the docs say that the code no longer does, prove it, and fix it. **Fix by default.**
`scan` reports only. Never commit.

This skill fixes facts, not style. For AI writing tells, use `/basic-unslop`. For how to write the
new text, follow §5.

## 1. Read the arguments

- `scan` anywhere → report only. Otherwise, fix.
- The scope, default `diff`:

| Scope | Checks |
|---|---|
| `diff` | The names the current diff changed, searched for in every doc. Fix only what the diff made wrong |
| `repo` | Every doc, against the code as it is now |
| `<paths>` | `repo` checks, limited to the named docs |

## 2. Find the docs

The docs are:

- `README*` and `CONTRIBUTING*` anywhere in the repo.
- Everything under `docs/`.
- `AGENTS.md` and `CLAUDE.md`, at the root and in subfolders.
- Other root-level `.md` files.
- `.env.example`, `.env.sample`, and `.env.template`.

Use `git ls-files` so that ignored files stay out. Skip `node_modules/`, vendored folders,
`archive/`, and license files. Markdown inside source folders (such as a skill's `SKILL.md`) is
source, not docs, unless the user names it.

## 3. Who owns which docs

| Doc | Owner | Do |
|---|---|---|
| `README*`, `docs/**` guides, `CONTRIBUTING*`, `.env.example` | This skill | Fix |
| `AGENTS.md`, `CLAUDE.md` | The user (rules) and `basic-reflect` (lessons) | Fix facts only, such as a path, a command, or a count. Flag anything that would change a rule |
| `CHANGELOG.md` | `bump-version` | Flag a change that has no `[Unreleased]` entry. Never edit it |
| `docs/plans/NOW.md`, `docs/plans/BOARD.md`, `docs/phases/*`, `docs/plans/mvp/*` | `phase` | Flag, and point to `/phase sync` |
| `docs/adr/*` | `basic-architect` | Never rewrite it. An ADR is a historical record. Flag "possibly superseded by <change>" |
| `docs/summary/*` | `advanced-summary` | Skip. A summary is a snapshot of its day |

## 4. Check

### `diff`

1. Collect the diff the way `basic-review` §1 does (`git diff HEAD` plus untracked files, `staged`,
   or the last commit when the tree is clean). Read `../basic-review/SKILL.md` for the rules.
2. List the **changed names** from the removed and added lines: symbols, CLI flags, env vars,
   config keys, scripts and make targets, routes, file paths, and infra names (compose services,
   ports, volumes, hostnames, Terraform outputs and variables, cron and backup paths).
3. Search every doc for each **old** name and value with `rg -n -F -w`. Each hit is a lead.
4. Read each hit in context. It is a finding when the diff made the statement wrong.
5. For each **new** name that a user or operator would need (a flag, an env var, a script, a port),
   check that some doc mentions it. If none does, it is a gap (§6).

### `repo`

Work through [`references/drift-checks.md`](references/drift-checks.md) for every doc: paths and
links, commands, env vars, CLI flags, counts and badges, versions, and infra values. Each check
says how to prove the finding.

For more than 15 docs, batch them, about 8 to a batch, and launch one Haiku agent per batch in
**one message**: `subagent_type: Explore`, `model: haiku`, `run_in_background: false`. Give each
one its doc list and the "Claims to extract" section of `references/drift-checks.md`. The agents
only extract claims. You run the checks and make every edit yourself.

### The repo's own doc checks

When the repo has its own doc checks, run them read-only: `scripts/check-readme.sh`, a
markdownlint config with the tool already installed, or a link checker such as `lychee` already on
`PATH`. Do not install anything. Record each command and its result.

## 5. Fix (default)

- A finding needs **proof**: a missing file, a grep with no hits, a command that fails, a count that
  differs, or the diff line that changed it. No proof, no edit. It goes under **Not changed**.
- Make the smallest edit that makes the statement true. Keep the doc's format, tables, and links.
- When the right new text is unclear, such as a removed feature whose replacement you cannot name,
  do not guess. List it under **Not changed**.
- Never delete a whole section. Flag it instead.
- When a heading changes, update links to its anchor, or leave the heading alone.
- Write new text in the repo's style: the STE rules and clear-reading checks in
  `docs/AGENTS-TEMPLATE.md` §2 where the repo uses them, and otherwise the doc's own voice.
- Use the Edit tool. Never commit, stage, or push.

## 6. Gaps

A gap is a thing the code has that no doc mentions: a new flag, env var, script, port, or service.
**Flag gaps. Do not write them.** For each one, give where the code defines it and the nearest
place a doc would mention it, for example "the Configuration table in `README.md`".

## 7. Report

### After a fix

```markdown
**Fixed <n> statements in <m> docs.** Review with `git diff`.

| Doc | Location | Was | Now | Proof |
|---|---|---|---|---|
| `README.md` | `:42` | `npm run dev:all` | `npm run dev` | `package.json` has no `dev:all` script |
```

At most 20 rows. Then: `<n> more rows omitted.`

Then these sections, each left out when empty:

- **Not changed**: each finding that needs your judgment, with the location and the reason.
- **Owned elsewhere**: the flags from §3, one line each, with the skill to run.
- **Gaps**: each undocumented thing from §6.
- **Checks run**: each command from §4, with `pass`, `fail`, or `not run: <reason>`.
- **Coverage**: `Checked <m> docs (<scope>). <k> claims checked.`

End with one line: *"Run `/basic-unslop diff` to check the new wording?"*

### After `scan`

The same report, headed `**<n> stale statements in <m> docs.** Run /update-docs to fix them.` The
`Now` column holds the proposed text.

## Rules

- Fix facts only. Never change what a doc recommends or decides.
- Never edit a doc that §3 gives to another owner, apart from facts in `AGENTS.md` and `CLAUDE.md`.
- Never commit, push, or stage.
- Never invent a command, a flag, or a value. Every new value comes from the code or a command
  output.
