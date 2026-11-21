---
name: fix-comments
description: Sort every code comment in scope as a tautology, stale, an excuse, or a decision record, and act on each. Tautologies, stale comments (false now, history, or commented-out code), and excuses (TODO, HACK, "for now") are deleted in place. Each excuse also lands in a Hacks to fix list, with the proper fix. A decision that is hard to reverse, surprising, and a real trade-off goes into a short ADR after your approval, and a pointer replaces the comment. A true, local why stays. Targets the diff (default), the whole repo, or named paths. `scan` reports without editing. Directives, license headers, and generated files are never touched. Triggers on "/fix-comments", "/fix-comments scan", "/fix-comments repo", "clean up the comments", "remove useless comments", or "which comments are excuses".
argument-hint: "[scan] [diff | repo | <paths>]"
disable-model-invocation: true
---

# fix-comments

Comments that repeat the code, tell its history, or excuse a shortcut teach the next agent to
copy the shortcut. Delete them. Move real decisions into ADRs. **Fix by default.** `scan` reports
only. Never commit.

Adapted from a prompt by Matt Pocock.

## 1. Read the arguments

- `scan` anywhere → report only. Otherwise, fix.
- The target, default `diff`:

| Target | Comments in scope |
|---|---|
| `diff` | Comments on lines added or changed since `HEAD`, and every comment in untracked files |
| `repo` | Every comment in tracked and untracked files |
| `<paths>` | Every comment in the named files or folders |

## 2. List the comments

Shell variables do not last from one Bash call to the next. Pick one work folder,
`<scratchpad>/fix-comments/<repo-name>`, and write its literal path in every command. Below it is
`<work>`.

```bash
mkdir -p <work>
python3 -I <skill-dir>/scripts/comments.py list <target> > <work>/comments.tsv
```

Each row is `loc`, `kind`, `tag`, `text`. The summary line goes to stderr. The script already
leaves out directives, shebangs, modelines, license headers, and generated or vendored files.

- No rows → say so in one line and stop.
- `repo` or `<paths>` with more than 400 rows → show the count for each top-level folder
  (`cut -f1 <work>/comments.tsv | cut -d/ -f1 | sort | uniq -c`), and ask which folders to do
  first. Go on with the folders the user names.

## 3. Sort the comments

Read [`references/categories.md`](references/categories.md) first. Each row gets one category:
`stale`, `excuse`, `tautology`, `adr`, `keep`, or `unsure`.

- **60 rows or fewer**: sort them yourself, in this session. Read each comment with the code
  around it, and follow "How to sort".
- **More than 60 rows**: split the rows into batches of about 60. Keep each file in one batch.
  Launch one agent per batch in **one message**: `subagent_type: general-purpose`,
  `model: sonnet`, `effort: medium`. Fill in
  [`references/sort-prompt.md`](references/sort-prompt.md) for each one. The agents do not edit.
  When they return, check 3 rows from each batch yourself, and pick `stale`, `excuse`, and `adr`
  rows first. If 2 or more of the 3 are wrong, re-run that batch at `effort: high`.

Save the sorted rows to `<work>/sorted.tsv`: `loc`, `category`, `why`, `extra`.

**Done when** every listed row has one category, and each `stale` row has its proof.

## 4. Act on the comments (skip for `scan`)

### Delete

Delete the `tautology`, `stale`, and `excuse` rows in **one** call, before any other edit. The
script deletes bottom-up, so the locs stay valid only for that one call:

```bash
awk -F'\t' '$2=="tautology"||$2=="stale"||$2=="excuse"{print $1}' <work>/sorted.tsv \
  | python3 -I <skill-dir>/scripts/comments.py delete -
```

A `not found` line means the file changed after the list. Run `list` again for that file, sort
the new rows, and delete them in one more call.

Then read `git diff` for the changed files. Fix what a deletion left behind, such as an empty
`{}` from a JSX comment or a dangling blank line. If the repo has a fast lint or type check, run
it on the changed files.

### Draft the ADRs

Group the `adr` rows by the decision phrase in `extra`. Write one short ADR for each decision,
in the format of
[`../define-terms/references/adr-format.md`](../define-terms/references/adr-format.md). Use the
repo's ADR folder and number them from its highest number. The comment is the source. Do not add
claims that the comment and the code do not support.

Show each draft and its file name. Do not write them yet.

### After approval

For each approved ADR:

1. Write it.
2. Replace each of its comments with a one-line pointer in that file's comment style, at the
   same indent: `// See docs/adr/0007-retry-cold-gateway.md`.

A declined ADR leaves its comments as they are.

## 5. Report

### After a fix

```markdown
**Deleted <n> comments in <m> files**: <t> tautology, <s> stale, <e> excuse. Review with `git diff`.

| Category | Location | Comment | Why |
|---|---|---|---|
| stale | `src/api.ts:41` | const old = legacyFetch(url) | commented-out code |
| tautology | `src/count.ts:4-5` | increment the counter by one | restates `count += 1` |

### Hacks to fix

| Location | Shortcut | Proper fix |
|---|---|---|
| `src/api.ts:12` | paging is faked by fetching every page | use the API's cursor paging |

### ADR drafts (waiting for your approval)

<each draft, with its file name and the comment locations it replaces>
```

- The deletions table holds at most 20 rows, excuses first, then stale, then tautology. Then:
  `<n> more rows omitted.`
- **Hacks to fix** lists every excuse, with no limit. It is the only record of the shortcut.
  The location is where the comment was.
- **Kept**: one line with the count of `keep` rows.
- **Not changed**: one line for each `unsure` row, with what would settle it.
- Coverage line: `Checked <c> comments in <m> files (<target>). Skipped <k> directives and
  headers.`
- End with: *"Approve the ADR drafts? For the hacks, `/delegate` or `/improve` can take them
  on."* Leave out the parts that have no rows.

### After `scan`

The same report, with the heading `**<n> comments to delete in <m> files.** Run /fix-comments
to fix them.` Add an `Action` column to the table: `delete`, `move to ADR`, or `keep`.

## Rules

- Never commit, push, or stage.
- Change only comments: delete them, or swap one for an ADR pointer. Never fix the hack
  itself, and never change code.
- Never delete a directive, a license header, or a comment in a generated or vendored file.
- Write ADRs only after the user approves them.
