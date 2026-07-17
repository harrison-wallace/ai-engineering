# ai-engineering

**v0.1.0**

A home for reusable AI agent and Claude Code files: skills, subagents, slash commands, and hooks.

## Layout

```
skills/      Agent Skills — one folder per skill, each with a SKILL.md
agents/      Subagent definitions — one .md file per agent
commands/    Custom slash commands — one .md file per command
hooks/       Hook scripts referenced from settings.json
CLAUDE.md    Instructions Claude reads when working in this repo
```

## Conventions

These directories mirror Claude Code's own layout, so contents can be copied or
symlinked into place:

- **Skills** → `~/.claude/skills/<name>/` (personal) or `.claude/skills/<name>/` (project).
  Each skill is a directory containing a `SKILL.md` with `name` and `description`
  frontmatter, plus any supporting files.
- **Agents** → `~/.claude/agents/<name>.md` or `.claude/agents/<name>.md`.
  Markdown files with frontmatter (`name`, `description`, optional `tools`, `model`).
- **Commands** → `~/.claude/commands/<name>.md` or `.claude/commands/<name>.md`.
  Invoked as `/<name>`.
- **Hooks** → scripts wired up via `settings.json`; keep them executable.

## Versioning

The repo is versioned as a whole: `package.json` holds the current version,
`CHANGELOG.md` records what changed, and each release is tagged (`git tag v0.1.0`).
SemVer semantics: **patch** = tweaks to an existing asset, **minor** = new
skill/agent/command added, **major** = an asset renamed, removed, or changed in a
way that breaks how it's invoked. Run `/bump-version` to cut a release.

## Adding a skill

```
skills/
  my-skill/
    SKILL.md        # required: frontmatter + instructions
    reference.md    # optional supporting files
```

Minimal `SKILL.md`:

```markdown
---
name: my-skill
description: One line saying what this does and when to use it.
---

Instructions for the skill go here.
```
