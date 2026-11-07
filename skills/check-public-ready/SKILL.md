---
name: check-public-ready
description: Check for material that is unsafe on a public repository (secrets, PII, private keys, credentials, internal URLs, accidental dumps, and for the whole repo, a bad .gitignore). `diff` (default) checks the current changes before a push. `repo` audits the whole tree before you open-source it, and `repo history` also scans git history. Report-only severity table. Triggers on "/check-public-ready", "/check-public-ready repo", "is this diff public-ready", "safe for public repo", "is this repo public-ready", "safe to open-source", or "audit for public release".
argument-hint: "[diff | repo [history]] [<paths>]"
---

# check-public-ready

Would this be safe on a **public** GitHub or GitLab repo? **Report only.** Never fix, rewrite
history, commit, or push.

Not a general code review. For bugs and exploitable code, use `/basic-review` or
`/security-review`.

## Scope

| First argument | Scope | Follow |
|---|---|---|
| none, or `diff` | The working diff, or the last commit when the tree is clean, plus new untracked files | [`references/diff.md`](references/diff.md) |
| `repo` | The whole working tree: tracked files, and untracked files that would ship after a careless `git add` | [`references/repo.md`](references/repo.md) |
| `repo history` | The same, plus the bounded git-history pass in `references/repo.md` §7 | `references/repo.md` |

Paths after the scope narrow the focus. `repo` still runs its high-signal greps over the whole
repo.

Read the reference for the scope and follow it in full. Both use the same categories (`Secret`,
`PII`, `Internal`, `Hygiene`, `Config`) and the same severity table, so you can compare their
reports.
