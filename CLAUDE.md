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
| `advise` | Turn findings into ranked moves for this project, and change the plan on approval | recommend, suggest, consult |
| `summarise` | Restate work or a chat | recap |
| `restate` | Play back an ask before work starts | |
| `reflect` | Find lessons to encode | |
| `fix` | Change code to remove a known problem | repair, clean |
| `improve` | Find what to fix, simplify, or deepen in one existing area, and drive the chosen change | refactor, optimise, enhance |
| `update` | Bring something into line with its source | sync, refresh |
| `serve` | Make a page open on the LAN | host, publish |
| `showcase` | Pitch work just done as a post, article, or video idea | promote, market |
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

## Skill structure

- Keep a `SKILL.md` body under 500 lines. Move detail into `references/`, and link each reference
  from `SKILL.md`, one level deep.
- A reference file over 100 lines starts with a `## Contents` list that links to its `##` headings.
  Update the list when you add, rename, or remove a heading.
- Keep the `description` under 1,024 characters. Say what the skill does and when to use it.
- Put a repeatable step in a script under the skill's folder. Only the script's output costs
  tokens, but prose instructions cost tokens on every load.
- Write each subagent prompt so that it stands alone. A subagent starts with a fresh context. It
  does not see this chat, the skills in use, or the files already read.

## Model routing

Every Agent call in a skill, and every `agents/<name>.md` definition, follows the table in
`docs/AGENTS-TEMPLATE.md` §8. These rules add to it:

- Name the `model` on every call. Set `effort` on every call, except a Haiku read, which runs at
  the model default (`medium`).
- Name the `model` on each `Explore` call, usually `haiku`. The built-in Explore runs on the main
  model otherwise.
- Never go above Opus `high`. Do not use `xhigh` or `max`. Past `high`, one more effort level
  costs about as much as a bigger model, for a small gain.
- Keep code edits and judgement calls that need the chat on the main session. Send reading,
  search, and repeated review to subagents.
- Use parallel subagents to read and to judge. Do not let two of them write the same files.
- Escalate in this order: a self-check, then one effort level up, then one model size up at a
  lower effort. In a retry, re-run only the failed units.
- Do not set `model` in a skill's frontmatter. A model switch makes the session write its whole
  prompt cache again. Set the model on the Agent call.
- Do not rely on `CLAUDE_CODE_SUBAGENT_MODEL`. The per-call `model` wins, and the variable does
  not change Explore.
- Add a fan-out stage, or move a role to a cheaper model, only when a test on saved inputs shows
  that it keeps the result. Compare it with one main-session run that uses no subagents.

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
