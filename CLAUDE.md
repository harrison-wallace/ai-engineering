# ai-engineering

This repo houses reusable Claude Code assets. It contains no application code.

- `skills/<name>/SKILL.md` — Agent Skills. Frontmatter needs `name` (kebab-case, matching the folder) and `description` (one line: what it does and when to use it).
- `agents/<name>.md` — subagent definitions with `name` and `description` frontmatter.
- `commands/<name>.md` — custom slash commands.
- `hooks/` — executable hook scripts.

Naming: a skill is named `<verb>-<object>`, or a bare verb, after the action it does. Each verb has
one meaning, and its synonyms are never used:

| Verb | Means | Not |
|---|---|---|
| `review` | Judge a change or a plan against criteria | assess, critique |
| `check` | Scan for a known class of problem and report it, then offer next steps | audit, scan, verify |
| `trace` | Follow what a change touches outside its diff | |
| `explain` | Say how or why something is the way it is | describe |
| `diagnose` | Find and prove the cause of a reported failure | debug, troubleshoot |
| `design` | Shape something new, and write the ADR | architect |
| `prototype` | Build throwaway code that answers one design question | mock, spike |
| `guide` | Walk a human through steps only they can do | walkthrough, howto |
| `define` | Settle the names of things | |
| `research` | Find what outside sources say | |
| `summarise` | Restate work or a chat | recap |
| `restate` | Play back an ask before work starts | |
| `reflect` | Find lessons to encode | |
| `fix` | Change code to remove a known problem | repair, clean |
| `update` | Bring something into line with its source | sync, refresh |
| `serve` | Make a page open on the LAN | host, publish |
| `list`, `bump`, `delegate`, `teach` | As the word says | |

A domain group may lead with its noun (`aws-cost`, `aws-audit`), and `phase` stays a noun with
modes. `-deep` marks the deep partner of a skill, with the same core inputs (`review` and
`review-deep`, `summarise` and `summarise-deep`). An input that only makes sense short, such as
`summarise management`, can stay on the quick side. Elsewhere, depth is a `lite` or `deep`
argument. A new verb needs a row in this table first.

When adding files, follow the existing structure — see README.md for the conventions.
Each README row is a hook of one or two sentences, 300 characters at most, that ends with the
credit for a port. The detail lives in the skill's `SKILL.md`.

When adding or removing a skill, update the skills-count badge and the Skills table in README.md,
then run `scripts/check-readme.sh`. Install it into every profile with
`scripts/install-skill.sh <name>`, or remove the links with `scripts/install-skill.sh --remove <name>`.

## Porting an upstream skill

For a skill from pstack (`~/git/plugins/pstack`, a clone of `cursor/plugins`) or another plugin:

1. Summarize what it does, then check how it fits the user's sessions and setup.
2. Give your thoughts and numbered questions. Build nothing until the user answers.
3. Name the port by its verb from the Naming table, unless the user picks a name. Credit the source in its README row,
   and add it to `THIRD_PARTY_NOTICES.md` with the upstream license.
4. Never edit the upstream clone or `plugins/cache`.

## Versioning

Versioning is repo-level: `package.json` version + `CHANGELOG.md` + git tags. Use the
`bump-version` skill to cut a release (there is no `tsconfig.json` here, so the
TypeScript pre-flight does not apply).
