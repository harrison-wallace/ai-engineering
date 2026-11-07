---
name: basic-review
description: Quick sanity check of the current diff for bugs, security issues, bloat, and maintainability, reported as a verdict, a severity (1–3) table with a fix per row, and a coverage line. Use for a fast pre-commit gut check, not a branch or pull-request review. Triggers on "/basic-review", "/basic-review staged", or "sanity check the diff".
---

# basic-review

A fast, single-pass sanity check of the working diff. Report what stands out. This skill only reports. Do not run tests, and do not fix anything. For a branch or pull-request review, use `/code-review`.

## 1. Collect the diff

```bash
git status --porcelain
git rev-parse -q --verify HEAD
git -c color.ui=false -c color.diff=false diff HEAD
git ls-files --others --exclude-standard
```

`git diff HEAD` holds the staged and unstaged changes to tracked files. Read every untracked text file from `git ls-files` as well. A new file that was never added is part of the review.

Scope rules:

- If `git status` fails because this directory is not a git repo, say so in one line and stop.
- `/basic-review staged` → review only `git diff --cached`. Leave out unstaged and untracked files. This is exactly what the next commit holds.
- If the user names paths, limit the diff and the untracked list to those paths.
- No `HEAD` (no commits yet) → use `git diff --cached` plus the untracked files.
- If the tree is clean, review the last commit:
  - If `git rev-parse --verify -q 'HEAD^2'` succeeds, `HEAD` is a merge. Diff the first parent: `git -c color.ui=false -c color.diff=false diff 'HEAD^1' 'HEAD'`.
  - Otherwise diff `'HEAD~1'` to `'HEAD'`. If `HEAD~1` does not exist, review `HEAD` as a root commit: `git show --format= HEAD`.
  - Record `git rev-parse --short HEAD` for the coverage line.

Skip a line-by-line read of lockfiles, vendored trees, minified bundles, generated dumps, binary files, and untracked files over about 200 KB. Count those paths as skipped. Flag a skipped path only when it adds a real credential, a new install or script hook, or a huge accidental dump. When the diff is too large to read in one pass, review the hunks in each changed source file and skip generated files.

## 2. Find issues

Work through these passes in order. Passes A and B produce leads. Passes C and D confirm them. Pass E removes the false ones.

### A. Intent

Write down in one sentence what the change is trying to do. Take it from the user's message, the branch name, the commit message (for a commit scope), or the diff itself. A change that contradicts its own intent is a Bug.

### B. Mechanical sweep

These checks are cheap and high-signal. Run them on added lines only. A hit is a lead to read, not a finding yet.

```bash
git diff HEAD --check                 # conflict markers (ignore whitespace-only warnings)
git diff HEAD -U0 | grep -nE '^\+' | grep -nE \
  'console\.(log|debug)|debugger;|\bdbg!|breakpoint\(\)|pdb\.set_trace|\.only\(|\bfit\(|\bfdescribe\(|binding\.pry'
git diff HEAD -U0 | grep -nE '^\+' | grep -niE \
  'AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9_-]{20,}|xox[abpr]-|(password|secret|token|api_?key)\s*[:=]\s*["'\'']?[^"'\'' ]{8,}'
```

Use the same base as the scope in §1 (`--cached`, or the commit range). Untracked files are not in `git diff`, so grep them directly. Leftover debug output is Bloat. A focused test (`.only`, `fit`) that silently skips the rest of the suite is a Bug. A conflict marker is a severity-3 Bug.

### C. Hunk read

For each changed hunk, read the whole enclosing function or block, not only the changed lines. Check it against the lists in §3.

### D. Ripple check

The diff may add, delete, or rename something other code depends on, or change its signature. That includes a function, type, export, route, CLI flag, env var, config key, DB column, or event name. It also includes infra names: a compose network, volume, or container name, a hostname, a bucket, a Terraform resource address or output, an IAM ARN, a secret name, a cron or backup path, or an image tag. Then search for every user the hunk does not show:

```bash
git grep -nw '<symbol>'
```

Include tests, docs examples, `.env.example`, fixtures, and migrations. Report a user that now breaks. Leave every other pre-existing issue out.

This pass stays inside the current repo. Note a ripple you could not settle in one pass for the coverage line. That includes a changed infra name, a shared contract (route, schema, wire format, Terraform output), or a symbol that other repos may use. Do not chase it further. That is `/basic-impact`'s job.

### E. Verify every candidate

Before a candidate becomes a row:

1. Reopen the file and read the exact line you will cite.
2. Write the failure path. That is the input or state, then the wrong result. For Bloat, write what is unused or repeated. For Maintain, write the next edit and how it goes wrong.
3. Check the path is not already handled: a guard upstream, a type that rules it out, a test that covers it, or a comment that explains it.

If any step fails, drop the candidate. A false finding is worse than a missed nit.

## 3. What counts

Check for exactly four types.

**Bug** — the change breaks something on a path that exists now. Look for:

- An inverted or wrong condition. An off-by-one or boundary error. `<` where `<=` is meant.
- An unhandled null, undefined, empty collection, or empty string. An unchecked error return.
- A missing `await`, or an unhandled promise or rejection. A swallowed error (an empty `catch`, `except: pass`, an ignored `err`).
- The wrong variable, often from copy-paste. A changed default value. Changed units, a time zone, or string-versus-number comparison.
- Shared state that is mutated, or a race on it. A resource that is opened but never closed.
- A stale closure or a missing dependency in a hook array. A cache key that misses a new input.
- A schema or migration change with no backfill, or out of step with the code that reads it.
- A test that no longer tests anything. A missing test counts only when you can name the untested path and that area already has tests.

**Security** — exploitable behavior this diff introduces:

- Injection: SQL, shell, template, or a path built from input. Path traversal. SSRF from a URL the user controls.
- An auth or permission check that is removed, bypassed, or moved after the action on a reachable handler.
- `eval` or unsafe deserialization of input. Raw HTML from input (`innerHTML`, `dangerouslySetInnerHTML`, `v-html`, `|safe`).
- CORS `*` with credentials. TLS verification turned off. Non-crypto random used for tokens. Secrets written to logs.
- A real credential added in this diff is always severity 3.
- PII, internal URLs, and publish-hygiene belong to `check-diff-public-ready`.

**Bloat** — code that can be removed:

- Dead code, unused imports or parameters, and commented-out blocks the diff adds.
- A second copy of something already in the diff or in the codebase, when you have found the original.
- A dependency added for one trivial call. A config key nothing reads. Leftover debug output.
- Judge "outside the task" only from the user's message in this conversation. If they only asked for this review, skip that judgment.

**Maintain** — the code works on today's paths, but the next edit is easy to get wrong. Name that edit. Typical cases:

- The same logic repeated in sites that must stay in sync.
- A magic value that must match another file.
- Hidden ordering or coupling.

Severity 2 when the diff already edits this logic in more than one place, or the area is clearly in flux. Severity 1 when the cost is real and that edit is not imminent. Never severity 3. Use Bug when a path that exists now is already wrong. Use Bloat when the extra code can be removed.

Formatting and lint rules are not findings.

| Sev | Meaning |
|---|---|
| 3 | Will break, corrupt, or expose something on a path you can name. |
| 2 | A real defect or risk on a path you can name. Survivable for a short time. |
| 1 | A small defect, real bloat, or a maintainability cost. Worth a fix. It does not block the commit. |

## 4. Report

Print the verdict, the table, and the coverage line, in that order. Print nothing else: no preamble, no recap, and no list of things that look fine.

### Verdict

One line: the call, then the counts.

| Highest sev | Call |
|---|---|
| 3 | `**Fix before commit.**` |
| 2 | `**OK to commit; fix soon.**` |
| 1 | `**OK to commit.**` |
| none | `**No findings.**` |

After the call, add the counts: `N findings: X sev-3, Y sev-2, Z sev-1.` The counts include rows left out of the table. Drop a severity group with a count of 0. Use `finding` when N is 1. With no findings, the line is just the call.

```
**Fix before commit.** 3 findings: 1 sev-3, 2 sev-2.
```

### Table

Print the table only when there is at least one finding.

| Sev | Type | Location | Problem | Fix |
|---|---|---|---|---|
| 3 | Bug | `src/api.ts:42` | When `id` is empty, the handler returns the previous user. | Return 400 before the lookup when `id` is empty. |

The header row is exactly `Sev`, `Type`, `Location`, `Problem`, `Fix`.

- `Sev` is `3`, `2`, or `1`. `Type` is `Bug`, `Security`, `Bloat`, or `Maintain`.
- Sort by severity descending, then `Security`, `Bug`, `Bloat`, `Maintain`, then location.
- One row per defect. When the same defect has several sites, cite the defining file and name the other sites in the Problem cell.
- Location is `` `path:line` `` in the post-change file.
  - For a broken caller outside the diff, cite the caller.
  - For removed code, cite the nearest line that still exists.
  - For a deleted file, cite `` `path` ``.
  - Cite a line only after you have opened the file and seen that line. Otherwise cite `` `path` ``.
- Problem is one sentence, 25 words or fewer, with no `|` and no line break.
  - Bug and Security: `When <condition>, <wrong result>.`
  - A credential: `A real <kind of secret> was added in this file.`
  - Bloat: `<what was added> is unused.`, `<what was added> repeats <existing thing>.`, or `<dependency> is only used for <one trivial call>.`
  - Maintain: `When the next change <does this>, <this will be wrong>.`
- Fix is one imperative sentence, 15 words or fewer, with no `|`. It names the smallest change that removes the problem: `Await the save before redirecting.`, `Delete the unused helper.`, or `Rotate the key, then load it from the env.` If no short fix exists, write what to decide: `Choose one owner for the retry logic.`
- Print at most 8 rows. Drop severity 1 before severity 2. Drop a severity-3 row only when severity-3 rows alone exceed 8, and then keep the first 8 in location order.

The example row above shows the shape. Do not copy it into a real report.

### Coverage

One final line, in plain text.

`Reviewed <count> files (<scope>).`

`<scope>` is one of:

- `working tree` — add `: staged + unstaged` when both are present.
- `staged`
- `no commits yet`
- `last commit <shortsha>`
- `root commit <shortsha>`
- `merge <shortsha>, first parent`

Then add these, in order, only when they apply:

- `, paths named` — inside the parentheses, when the user named paths.
- `: <paths>` — the reviewed paths, when the file count is 8 or fewer.
- `Callers checked for <n> changed symbols.` — when pass D ran.
- `Skipped <count>.` — when you skipped generated, lockfile, binary, or oversized paths.
- `Large diff: source hunks only.` — when you could not read the whole diff.
- `<count> further findings omitted.` — when you left rows out of the table.
- `Unverified ripple: <names>. Run /basic-impact.` — when pass D noted a ripple it could not settle in this repo. List at most 3 names.

Shapes for that line. Do not append these samples to a real report.

```
Reviewed 2 files (working tree: staged + unstaged): src/api.ts, src/api.test.ts. Callers checked for 2 changed symbols.
```

```
Reviewed 4 files (last commit abc1234). Skipped 1. 2 further findings omitted.
```

```
Reviewed 3 files (staged): terraform/network.tf, compose.yml, README.md. Callers checked for 2 changed symbols. Unverified ripple: proxy, app_url. Run /basic-impact.
```
