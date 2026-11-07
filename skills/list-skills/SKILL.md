---
name: list-skills
description: List every skill this profile and project can run (repo skills, your ai-engineering skills, plugin skills and commands, and built-in skills), each with a one-line summary and a sub-bullet on when to use it and which neighbour not to confuse it with. `for <task>` recommends the right skill for a job instead. Filters by `mine`, `repo`, `plugins`, `built-in`, or a keyword. Flags broken, unmanaged, not-installed, and disabled skills. Report-only. Triggers on "/list-skills", "/list-skills for <task>", "what skills do I have", "list my skills", "which skill should I use for X", or "is there a skill for X".
argument-hint: "[all | mine | repo | plugins | built-in | <keyword> | for <task>]"
---

# list-skills

List what can run here, and when to use each one. **Report only.** Do not run any skill you list.

## 1. Read the arguments

| Argument | Shows |
|---|---|
| none, or `all` | Every source, in the order of §4 |
| `mine` | Your ai-engineering skills only |
| `repo` | This project's `.claude/skills` and `.claude/commands` only |
| `plugins` | Plugin skills and commands only |
| `built-in` | Built-in skills only |
| `for <task>` | A recommendation, per §5 |
| anything else | A keyword: every skill whose name or description matches it, from every source |

## 2. Collect

Run the bundled script. It is read-only, and it reads the files fresh each time:

```bash
python3 -I <skill-dir>/scripts/list.py "$PWD"
```

It prints TSV: `source`, `group`, `name`, `description`, `note`.

| Source | Where it comes from |
|---|---|
| `repo` | `<project>/.claude/skills/*/SKILL.md` and `<project>/.claude/commands/*.md` |
| `mine` | `<config>/skills/*` links into `~/git/ai-engineering`. `group` is its README section |
| `local` | Anything else in `<config>/skills/` or `<config>/commands/` |
| `plugin` | Installed plugins: the entry for this project, else the user entry. `group` is the plugin |

**Built-in skills have no files on disk.** Take them from the skill list in this session's
context: each skill there that the script did not print is built-in. That covers the harness
skills (such as `code-review`, `simplify`, and `artifact-design`) and the claude.ai skills
(`anthropic-skills:*`), which sync into `<config>/skills/synced/`. Do not list a skill from
memory. Only list what the script or the session's list shows.

## 3. Condense

For each skill, write the house shape:

- **`name`**: what it does, in one sentence of 20 words or fewer.
  - When to use it, in one sentence. When a close neighbour exists, add "Not for X: use `other`."

- Take both lines from the skill's description. Do not add powers it does not claim.
- Name the neighbour for each pair that is easy to confuse: `basic-` and `advanced-` pairs, review
  and impact, summary and teach, and plugin skills that overlap yours (`code-review` and
  `advanced-review`, `code-simplifier` and `simplify`, `basic-research` and the built-in
  `deep-research`).
- Use the STE rules and the clear-reading checks from `../basic-summary/SKILL.md` §3.

## 4. Report

Leave out a section that is empty.

```markdown
**<n> skills in `<profile>` for `<project>`:** <a> repo, <b> yours, <c> plugin, <d> built-in.

## Repo: <project>
- **`release`**: …
  - …

## Yours
### <README section>
- **`basic-review`**: …
  - …

## Plugins
### <plugin>
- **`firecrawl:firecrawl`**: …
  - …

## Built-in
- **`simplify`**: …
  - …

## Flags
- …
```

- **Yours** follows the README sections, in README order. **Plugins** groups by plugin.
- A keyword filter keeps the same sections, with the matches only.
- **Flags**, one line each, only when they apply:
  - `broken`: a link in `<config>/skills/` points to a missing folder. Say where it pointed.
  - `unmanaged`: a real folder or file in `<config>/skills/` or `<config>/commands/` that no repo or
    plugin owns. Say that it will not update with `install-skill.sh`.
  - `not-installed-here`: an ai-engineering skill with no link in this profile. Give the fix:
    `scripts/install-skill.sh <name>`.
  - `disabled-plugin`: a plugin that is installed but turned off. Name the plugin and its skill
    count, and do not list its skills.

## 5. `for <task>`

Recommend instead of listing:

```markdown
**For "<task>":**

1. **`best-skill`**: why it fits, in one sentence. Run: `/best-skill <args>`.
2. **`second-skill`**: when it is the better pick instead, in one sentence.

**Not this one:** `near-miss` does <what>, which is not what you asked for.
```

- Give one to three picks, best first. Choose from every source, including built-in skills.
- Base each pick on the skill's description, not on its name only.
- When nothing fits, say so in one line, and name the closest skill.
- Do not run the skill.

## Rules

- Report only. Never run, install, remove, or edit a skill.
- List only what the script or this session's skill list shows. Never invent a skill.
