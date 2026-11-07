# Synthesis criteria

The main agent applies every test to every finding: its own and each reviewer's.

## Tests

| Test | Accept when | Reject reason |
|---|---|---|
| Durable | Still true in six months, after paths, SHAs, versions, and code shapes change. | `drifts` |
| Specific | Broad enough to recur, and precise enough that a future agent knows when it applies. Reject platitudes ("write good code") and trivia ("the file is 175 lines"). | `vague` or `trivia` |
| Changes a decision | A future agent does something different because of it, not just reads more text. | `no-decision` |
| Used, or should have triggered | It routes to a skill or file the session used, or to `tune description` for a skill that should have run. | `not-used` |
| Not already covered | Read the target first. If clear, well-placed guidance already says it, the failure was in execution, not in the text. If the guidance exists but is buried or weak, accept it as a **rewording or move**, not as an addition. | `covered` |
| Right destination | The narrowest home that a future agent will actually load at the right moment (see the destinations table in SKILL.md). | Re-route, do not reject |
| Mechanism first | If a hook, a lint rule, a script, a settings entry, or a frontmatter flag can enforce it, it becomes a **suggestion**, not prose. | Move to Suggestions |
| One-off | It happened once, and nothing suggests it will happen again. | `one-off` |

Confidence: a finding that two or more reviewers raised is stronger. A finding raised once must be
clearly strong on every other test.

## Drop and keep

Drop facts that drift:

- "the digest of session 1a2b… is 88 KB"
- "README line 73 had the archived note"
- "phase SKILL.md was modified by another session at 08:41"

Keep the patterns underneath:

- "Pipelines under `set -o pipefail` must not end in `head`. Use jq `first()` or `|| true`."
- "Before committing in ai-engineering, check `git status` for files another session changed."
- "This user wants thoughts and numbered questions before any build."

## Output format

```markdown
## Accepted

| # | Problem | Proposal | Destination |
|---|---|---|---|
| 1 | <what went wrong or was rediscovered> | <the exact change> | <skill path + section / repo AGENTS.md / AGENTS-TEMPLATE § / memory (type) / tune description: <skill>> |

## Suggestions (you decide; nothing is written)

| # | Pattern | Mechanism | Where it would live |
|---|---|---|---|
| S1 | <what keeps happening> | <hook / settings entry / script / lint / fork as basic-*> | <path it would go in> |

## Rejected

- <principle>: `<reason>`

Approve by number: e.g. "1 yes 2 no 3 → memory S1 yes".
```

One sentence per cell. The user should read each row in about five seconds. Leave out a section
that has no rows, and write "Nothing durable this session" if all of them are empty.
