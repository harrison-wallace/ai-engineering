# ai-engineering

This repo houses reusable Claude Code assets. It contains no application code.

- `skills/<name>/SKILL.md` — Agent Skills. Frontmatter needs `name` (kebab-case, matching the folder) and `description` (one line: what it does and when to use it).
- `agents/<name>.md` — subagent definitions with `name` and `description` frontmatter.
- `commands/<name>.md` — custom slash commands.
- `hooks/` — executable hook scripts.

Naming: `basic-` is the default prefix for ported skills and quick skills. `advanced-` marks the
deep partner of a `basic-` skill, with the same core inputs (`basic-review` and `advanced-review`,
`basic-summary` and `advanced-summary`). An input that only makes sense short, such as
`basic-summary management`, can stay on the `basic-` side.

When adding files, follow the existing structure — see README.md for the conventions.
When adding or removing a skill, update the skills-count badge and the Skills table in README.md,
then run `scripts/check-readme.sh`. Install it into every profile with
`scripts/install-skill.sh <name>`, or remove the links with `scripts/install-skill.sh --remove <name>`.

## Porting an upstream skill

For a skill from pstack (`~/git/plugins/pstack`, a clone of `cursor/plugins`) or another plugin:

1. Summarize what it does, then check how it fits the user's sessions and setup.
2. Give your thoughts and numbered questions. Build nothing until the user answers.
3. Name the port `basic-<name>` unless the user picks a name. Credit the source in its README row,
   and add it to `THIRD_PARTY_NOTICES.md` with the upstream license.
4. Never edit the upstream clone or `plugins/cache`.

## Versioning

Versioning is repo-level: `package.json` version + `CHANGELOG.md` + git tags. Use the
`bump-version` skill to cut a release (there is no `tsconfig.json` here, so the
TypeScript pre-flight does not apply).
