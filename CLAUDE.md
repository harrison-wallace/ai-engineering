# ai-engineering

This repo houses reusable Claude Code assets. It contains no application code.

- `skills/<name>/SKILL.md` — Agent Skills. Frontmatter needs `name` (kebab-case, matching the folder) and `description` (one line: what it does and when to use it).
- `agents/<name>.md` — subagent definitions with `name` and `description` frontmatter.
- `commands/<name>.md` — custom slash commands.
- `hooks/` — executable hook scripts.

When adding files, follow the existing structure — see README.md for the conventions.
When adding or removing a skill, update the skills-count badge and the Skills table in README.md.

Versioning is repo-level: `package.json` version + `CHANGELOG.md` + git tags. Use the
`bump-version` skill to cut a release (there is no `tsconfig.json` here, so the
TypeScript pre-flight does not apply).
