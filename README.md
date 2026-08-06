# ai-engineering

![Version](https://img.shields.io/badge/version-0.7.1-6366f1?style=flat-square)
![Skills](https://img.shields.io/badge/skills-14-22c55e?style=flat-square)
![Claude Code](https://img.shields.io/badge/Claude_Code-assets-d97757?style=flat-square)

A home for reusable AI agent and Claude Code files: skills, subagents, slash commands, and hooks.

## Layout

```
skills/      Agent Skills — one folder per skill, each with a SKILL.md
agents/      Subagent definitions — one .md file per agent
commands/    Custom slash commands — one .md file per command
hooks/       Hook scripts referenced from settings.json
docs/        Supporting documentation
CLAUDE.md    Instructions Claude reads when working in this repo
```

## Skills

### Review & audit

| Skill | Description |
|---|---|
| [basic-review](skills/basic-review/SKILL.md) | Quick sanity check of the current diff for bugs, security issues, and over-engineering, reported as a severity (0–3) table. |
| [check-diff-public-ready](skills/check-diff-public-ready/SKILL.md) | Pass over the working diff for secrets, PII, internal URLs, and other material unsafe to push to a public repo; report-only severity table. |
| [check-repo-public-ready](skills/check-repo-public-ready/SKILL.md) | Whole-repo audit for the same public-exposure risks (plus `.gitignore`/hygiene); report-only before open-sourcing or keeping a repo public. |
| [check-npm-supply-chain](skills/check-npm-supply-chain/SKILL.md) | Audit a repo for npm supply-chain compromise indicators (Shai-Hulud-style worms): malicious install hooks, stealer payloads, IOCs, lockfile and hardening gaps; report-only. |

### AWS

Read-only, single-account, `aws` CLI. Every dollar figure they emit is labelled
as an estimate; none of them mutate infrastructure.

| Skill | Description |
|---|---|
| [aws-cost-mtd](skills/aws-cost-mtd/SKILL.md) | Month-to-date spend by service and region from Cost Explorer, with run-rate, month-end forecast, and deltas vs last month. |
| [aws-cost-optimize](skills/aws-cost-optimize/SKILL.md) | Savings sweep: Cost Optimization Hub and Compute Optimizer plus direct hunts for idle/orphaned resources and Savings Plans coverage gaps, ranked by estimated monthly saving. |
| [aws-s3-audit](skills/aws-s3-audit/SKILL.md) | Per-bucket audit of security posture (public access, encryption, TLS, versioning) and cost (lifecycle gaps, version bloat, abandoned multipart uploads, storage-class fit). |

### Fix & apply

| Skill | Description |
|---|---|
| [fix-input-overflow](skills/fix-input-overflow/SKILL.md) | Assess whether the app's native date/month/time inputs overflow on iOS Safari, and apply the global CSS reset fix if so. |
| [fix-react-doctor](skills/fix-react-doctor/SKILL.md) | Run `npx react-doctor@latest` and iteratively fix the reported React anti-patterns until the score reaches 100, verifying the build along the way. |

### Product & design

| Skill | Description |
|---|---|
| [review-dax-insights](skills/review-dax-insights/SKILL.md) | Review a product, feature, or launch plan against Dax Raad's three principles: shareable marketing, one Aha moment, primitives-first retention. |
| [review-website-design](skills/review-website-design/SKILL.md) | Review a website against the premium-psychology framework: Halo Effect hero, cognitive fluency, Peak-End micro-interactions, 2026 trends, ownership. |

### Repo workflow

| Skill | Description |
|---|---|
| [bump-version](skills/bump-version/SKILL.md) | Cut a release: bump the version, sync it into `README.md`, and write a `CHANGELOG.md` entry derived from the git diff. |
| [imp-grok-4-5](skills/imp-grok-4-5/SKILL.md) | Main agent plans the discussed changes, the headless `grok` CLI (Grok 4.5) implements them, then the main agent reviews, fixes, and summarizes. |
| [imp-sonnet](skills/imp-sonnet/SKILL.md) | Main agent plans the discussed changes, a Sonnet subagent implements them, then the main agent reviews, fixes, and summarizes. |

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

## AGENTS.md template

[docs/AGENTS-TEMPLATE.md](docs/AGENTS-TEMPLATE.md) is the canonical starting point
for a new repo's `AGENTS.md`: copy it in, fill the placeholders, delete what doesn't
apply. Its Core Rules, Additional Notes, and Local Test-Serving Port sections are
standardized verbatim across repos — edit those here, not per-project.

## Installing (symlinks)

This repo is the source of truth; `~/.claude` just points at it. Install a skill by
symlinking its directory:

```bash
ln -sfn ~/git/ai-engineering/skills/<name> ~/.claude/skills/<name>
```

Edits made here are live in Claude Code immediately — no copying or re-syncing —
and `git log` stays the single history of every change. The same pattern works for
agents and commands (symlink the individual `.md` file into `~/.claude/agents/` or
`~/.claude/commands/`). New skills appear in Claude's skill list at the next session
start.

### Multiple profiles

If you run Claude Code with multiple profiles (separate config directories selected
via `CLAUDE_CONFIG_DIR` — see [docs/CLAUDE-PROFILES.md](docs/CLAUDE-PROFILES.md) for
how to set them up), each profile has its own `skills/` directory and none of them
inherit from `~/.claude`. Symlink into every profile **directly** — never chain one
profile's link through another's:

```bash
for d in ~/.claude ~/.claude-*; do
  ln -sfn ~/git/ai-engineering/skills/<name> "$d/skills/<name>"
done
```

If a profile should have its own variant of a skill, keep that variant as a real
directory in the profile (or as a differently-named skill here) instead of a symlink.

## Versioning

The repo is versioned as a whole: `package.json` holds the current version,
`CHANGELOG.md` records what changed, and each release is tagged (`git tag vX.Y.Z`).
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
