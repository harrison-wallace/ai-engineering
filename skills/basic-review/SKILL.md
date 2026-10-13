---
name: basic-review
description: Quick sanity check of the current diff for bugs, security issues, bloat, and maintainability, reported as a verdict plus a severity (1–3) table. Use for a fast pre-commit gut check, not a branch or pull-request review. Triggers on "/basic-review" or "sanity check the diff".
---

# basic-review

A fast, single-pass sanity check of the working diff. Report what stands out. This skill only reports. Do not run tests, and do not fix anything.

## 1. Collect the diff

```bash
git status --porcelain
git -c color.ui=false -c color.diff=false diff HEAD
git ls-files --others --exclude-standard
```

`git diff HEAD` is the staged and unstaged changes to tracked files. Read every untracked text file from `git ls-files` as well. A new file that has never been added is part of the review.

If the user names paths, limit the diff and the untracked list to those paths.

If `git status` fails because this directory is not a git repo, say so in one line and stop.

If the tree is clean, review the last commit:

- If `git rev-parse --verify -q 'HEAD^2'` succeeds, `HEAD` is a merge. Diff the first parent: `git -c color.ui=false -c color.diff=false diff 'HEAD^1' 'HEAD'`.
- Otherwise diff `'HEAD~1'` to `'HEAD'`. If `HEAD~1` does not exist, say there is no parent commit and stop.

Record `git rev-parse --short HEAD` for the coverage line when you review a commit.

Skip a line-by-line read of lockfiles, vendored trees, minified bundles, and generated dumps. Count those paths as skipped. Flag a skipped path only when it adds a real credential, a new install or script hook, or a huge accidental dump. When the diff is too large to read in one pass, review the hunks in each changed source file and skip generated files.

For each changed hunk, read the enclosing function or block. When a symbol, type, export, or route is added, deleted, or its signature changes, check the callers that the hunk does not show. Report a break there. Leave every other pre-existing issue out.

## 2. Check for exactly four things

- **Bugs** — logic errors, unhandled null, empty, or error paths, broken behavior a user would hit, and changes that contradict what the code claims to do. A missing test is a bug only when you can name the untested path and that area already has tests.
- **Security** — exploitable behavior this diff introduces: injection, an auth check removed on a reachable handler, or unsafe shell, file, or network use. A real credential added in this diff is severity 3. PII, internal URLs, and publish-hygiene belong to `check-diff-public-ready`.
- **Bloat** — dead code in the diff, a second copy of something already in the diff, a dependency added for one trivial call, or a config key nothing reads. Judge "outside the task" only from the user's message in this conversation. If they only asked for this review, skip that judgment.
- **Maintain** — the code works on today's paths, and the next edit is easy to get wrong. Name that edit. Severity 2 when the diff already edits this logic in more than one place, or this area is clearly in flux. Severity 1 when the cost is real and that edit is not imminent. Never severity 3. Use Bug when a path that exists now is already wrong. Use Bloat when the extra code can be removed.

Formatting and lint rules are not findings.

A finding needs a concrete path: a wrong result now, unused or repeated code, or a next change that gets it wrong. If you cannot write that path, drop the finding. A false finding is worse than a missed nit.

Severity:

| Sev | Meaning |
|---|---|
| 3 | Will break, corrupt, or expose something on a path you can name. |
| 2 | A real defect or risk on a path you can name. Survivable for a short time. |
| 1 | A small defect, real bloat, or a maintainability cost. Worth a fix. It does not block the commit. |

## 3. Report

Print the verdict, then the table, then the coverage line. Always, in that order.

### Verdict

One line:

| Highest sev | Line |
|---|---|
| 3 | `Fix before commit. N severity-3 findings.` |
| 2 | `No severity-3. N findings, highest severity 2.` |
| 1 | `No blockers in this pass. N severity-1 findings.` |
| none | `No findings.` |

In the severity-3 line, the number is the severity-3 count, including severity-3 rows left out of the table. In the severity-2 line, the number is every finding, including rows left out of the table. In the severity-1 line, the number is the severity-1 count, including rows left out of the table. Use `finding` when the number is 1, and `findings` otherwise.

### Table

Print the table only when there is at least one finding.

| Sev | Type | Location | Summary |
|---|---|---|---|
| 3 | Bug | `src/api.ts:42` | When `id` is empty, the handler returns the previous user. |

The header row is exactly `Sev`, `Type`, `Location`, `Summary`.

- `Sev` is `3`, `2`, or `1`. `Type` is `Bug`, `Security`, `Bloat`, or `Maintain`.
- Sort by severity descending, then `Security`, `Bug`, `Bloat`, `Maintain`, then location.
- One row per defect. When the same defect has several sites, locate the defining file and name the other sites in the summary.
- Location is `` `path:line` `` in the post-change file. For a broken caller outside the diff, cite the caller. Cite a line only after you have opened the file and seen that line. Otherwise cite `` `path` ``.
- Summary is one sentence, 25 words or fewer, with no `|` and no line break.
  - Bug and Security: `When <condition>, <wrong result>.`
  - A credential: `A real <kind of secret> was added in this file.`
  - Bloat: `<what was added> is unused.`, `<what was added> repeats <existing thing>.`, or `<dependency> is only used for <one trivial call>.`
  - Maintain: `When the next change <does this>, <this will be wrong>.`
- Print at most 8 rows. Drop severity 1 before severity 2. Drop a severity-3 row only when severity-3 rows alone exceed 8, and then keep the first 8 in location order.

The example row above shows the shape. Do not copy it into a real report.

### Coverage

One final line.

`Reviewed <count> files (<scope>).`

`<scope>` is one of `working tree`, `last commit <shortsha>`, or `merge <shortsha>, first parent`. When the user named paths, append `, paths named`. When the file count is 8 or fewer, add the paths after a colon. When you skipped generated or lockfile paths, add `Skipped <count>.` When you could not read the whole diff, add `Large diff: source hunks only.` When you leave rows out of the table, add `<count> further findings omitted.`

Shapes for that line. Do not append these samples to a real report.

```
Reviewed 2 files (working tree): src/api.ts, src/api.test.ts.
```

```
Reviewed 4 files (last commit abc1234). Skipped 1. 2 further findings omitted.
```
