# ai-engineering

![Version](https://img.shields.io/badge/version-1.2.0-6366f1?style=flat-square)
![Skills](https://img.shields.io/badge/skills-23-22c55e?style=flat-square)
![Claude Code](https://img.shields.io/badge/Claude_Code-assets-d97757?style=flat-square)

A home for reusable AI agent and Claude Code files: skills, subagents, slash commands, and hooks.

## Layout

```
skills/      Agent Skills — one folder per skill, each with a SKILL.md
agents/      Subagent definitions — one .md file per agent
commands/    Custom slash commands — one .md file per command
hooks/       Hook scripts referenced from settings.json
docs/        Supporting documentation (templates, cheat sheets)
scripts/     Repo maintenance: install-skill.sh, check-readme.sh
.githooks/   Git hooks (pre-commit runs check-readme.sh)
CLAUDE.md    Instructions Claude reads when working in this repo
THIRD_PARTY_NOTICES.md  Licenses for adapted upstream work (pstack, MIT)
```

## Skills

### Review & audit

| Skill | Description |
|---|---|
| [basic-review](skills/basic-review/SKILL.md) | Quick sanity check of the current diff for bugs, security issues, bloat, and maintainability, reported as a verdict, a severity (1–3) table with a fix per row, and a coverage line. `/basic-review staged` reviews only what the next commit holds. Flags ripples it cannot settle in one pass (infra names, shared contracts) with a pointer to `basic-impact`. |
| [basic-impact](skills/basic-impact/SKILL.md) | Find what a change could break **outside** its diff, for software, infra, or both. It sweeps every repo in `~/git`, works through a "where grep stops" checklist (pinned library source, timing, wire shapes, Terraform replace vs update, remote-state readers, shared Docker networks, DNS and IAM names, cron and backup paths), and proves the one fact the change is safe because of on a 5-level ladder with read-only scripts and commands. Anything with side effects is printed as a `!` command for you. Report-only verdict, risks table, cleared list, and checks to run before merge. `deep` adds a Sonnet second opinion. Inspired by the pstack `blast-radius` skill. |
| [check-diff-public-ready](skills/check-diff-public-ready/SKILL.md) | Pass over the working diff for secrets, PII, internal URLs, and other material unsafe to push to a public repo; report-only severity table. |
| [check-repo-public-ready](skills/check-repo-public-ready/SKILL.md) | Whole-repo audit for the same public-exposure risks (plus `.gitignore`/hygiene); report-only before open-sourcing or keeping a repo public. |
| [check-npm-supply-chain](skills/check-npm-supply-chain/SKILL.md) | Audit a repo for npm supply-chain compromise indicators (Shai-Hulud-style worms): malicious install hooks, stealer payloads, IOCs, lockfile and hardening gaps; report-only. |
| [check-ai-ui-tells](skills/check-ai-ui-tells/SKILL.md) | Scan a web UI (code and/or live URL) for 26 typical "AI-generated" design tells (purple gradients, glassmorphism, Inter-only type, pill-badge hero, three identical cards, left-border stripes, scroll fade-ins, buzzword copy), and list each one with evidence and a cluster score. Report-only. |

### AWS

Read-only, single-account, `aws` CLI. Every dollar figure they emit is labelled
as an estimate; none of them mutate infrastructure.

| Skill | Description |
|---|---|
| [aws-cost-mtd](skills/aws-cost-mtd/SKILL.md) | Month-to-date spend by service and region from Cost Explorer, with run-rate, month-end forecast, and deltas vs last month. |
| [aws-cost-optimize](skills/aws-cost-optimize/SKILL.md) | Savings sweep: Cost Optimization Hub and Compute Optimizer plus direct hunts for idle/orphaned resources and Savings Plans coverage gaps, ranked by estimated monthly saving. |
| [aws-s3-audit](skills/aws-s3-audit/SKILL.md) | Per-bucket audit of security posture (public access, encryption, TLS, versioning) and cost (lifecycle gaps, version bloat, abandoned multipart uploads, storage-class fit). |

### Design

| Skill | Description |
|---|---|
| [basic-architect](skills/basic-architect/SKILL.md) | Design a new feature, service, or component before code, for software, infra, or both. Haiku agents ground it in the real system, two Sonnet runners sketch structurally different shapes (extend vs reshape), and the main agent screens both against software and infra red flags, merges them, and writes a `proposed` ADR in `docs/adr/`. Then it stops for sign-off and offers `/phase shape`. Optional leading level: `lite` (no subagents) or `deep` (adds one Opus-high runner). Never applies infrastructure. Inspired by the pstack `architect` skill, adapted to run cheaper and to cover infra/DevOps. |

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
| [basic-alignment](skills/basic-alignment/SKILL.md) | Play back the ask before any work starts: goal, problem, scope in/out, constraints heard, what done looks like, readings of unclear or dictated words (only the ones that change the meaning), and numbered yes/no assumptions. Simplified Technical English, report-only, no tool calls. `/basic-alignment <messy ask>` restates the given text. `basic-architect` opens its grounding brief and sign-off with the same block. Inspired by the pstack `in-your-own-words` skill. |
| [basic-summary](skills/basic-summary/SKILL.md) | Rewrite the previous assistant message in ASD-STE100 Simplified Technical English: one-sentence bullets, one longer sub-bullet each, then one summary paragraph. Report-only. |
| [summarise-work](skills/summarise-work/SKILL.md) | End-of-block wrap-up: Achieved / Fixed / Implemented bullets (omit empty), one sub-bullet each, then a short executive summary. Report-only. |
| [basic-reflect](skills/basic-reflect/SKILL.md) | Mine the current session, or `last <n>` sessions in this project, for durable lessons. A bundled `jq` digest (`digest.sh`, which shrinks a 77 MB transcript to about 88 KB, or about 18 KB with `-b`) feeds 2 Sonnet reviewers ("what to encode" and "what we missed"). The main agent filters for durability, decision change, and "already covered", then routes each lesson to the narrowest home: an ai-engineering skill, the repo's `AGENTS.md`/`CLAUDE.md`, `AGENTS-TEMPLATE.md`, or memory. It applies only the numbered rows you approve. Hooks, settings, scripts, and lessons about skills you do not own stay suggestions. `lite` uses no subagents; `deep` adds a third reviewer and puts "missed" on Opus high. Inspired by the pstack `reflect` skill. |
| [bump-version](skills/bump-version/SKILL.md) | Cut a release in any repo: detect where the version lives (`package.json`, `Cargo.toml`, `pyproject.toml`, `VERSION`, tags only, or a mix), bump every mirror, and write a `CHANGELOG.md` entry from the diff in the repo's own format. Defers to a repo-local release skill or script. |
| [bump-version-sonnet](skills/bump-version-sonnet/SKILL.md) | The same release split in two: the main agent derives it from the diff and writes the changelog prose, a Sonnet subagent applies the file edits verbatim, the main agent verifies. |
| [imp-grok-4-7](skills/imp-grok-4-7/SKILL.md) | Main agent plans, a headless Grok 4.7 process implements at `--effort` (default `medium`; the session effort stays unchanged), then the main agent reviews, scores the result out of 5, fixes, and summarizes. Generic "have grok implement this" trigger. Optional leading level: `/imp-grok-4-7 high`. |
| [imp-sonnet](skills/imp-sonnet/SKILL.md) | Main agent plans the discussed changes, a Sonnet subagent implements them, then the main agent reviews, scores the result out of 5, fixes, and summarizes. |

`imp-grok-4-5` and `imp-grok-4-6` are archived under [archive/skills](archive/skills). They are not installed and do not trigger.

### Phase board (`BOARD.md` + `NOW.md`)

User-scoped. Same symlink install as every other skill. Operates on the cwd
repo; not copied into it. Do not name a command `/session` or `/status`
(Grok built-ins).

| Skill | Description |
|---|---|
| [phase](skills/phase/SKILL.md) | Long-horizon tracker: `BOARD.md` (phases) + `NOW.md` (current slice) + `docs/phases/` (how / DoD). Modes: `status` (default), `init`, `sync`, `shape`, `advance slice`, `advance phase`, `prune`, `help`. Gitignores the two trees unless already tracked. |

#### Cheatsheet

Run these from the repo you're working in — the skill reads and writes that
repo's `docs/`, never this one.

| Command | What it does |
|---|---|
| `/phase` | Read-only brief: phase, slice, blocked, next shaped row, dirty files. Never starts work. |
| `/phase init` | Once per repo: creates `NOW.md` + `BOARD.md`, migrates a leftover `SESSION.md`/`STATUS.md`, appends the two gitignore lines. |
| `/phase shape auth` | Writes `docs/phases/auth.md` from the template (goal, appetite, scope, DoD) and adds a `shaped` board row. |
| `/phase sync` | Rewrites `NOW.md` and ticks the checkboxes that actually landed, from git + this chat. Does not close anything. |
| `/phase advance slice` | Ticks the current slice and moves `NOW.md` to the next one. Bare `/phase advance` does the same. Never closes a phase. |
| `/phase advance phase` | Closes the phase if its DoD is met: row `done`, log line, next `shaped` row into `in progress`. Otherwise lists what is left. |
| `/phase prune` | Proposes archiving duplicate/superseded/orphan docs. Waits for confirmation, file by file. |
| `/phase help` | Prints the modes table. |

A phase from start to finish:

```
cd ~/git/my-app
/phase init                  # first time only
/phase shape onboarding      # → docs/phases/onboarding.md, board row `shaped`
                             #   edit the doc: slices as checkboxes, DoD at the bottom
… build the first slice …
/phase sync                  # ticks what landed, NOW points at the next slice
/phase advance slice         # slice done → tick it, move NOW on
… build the rest …
/phase advance phase         # phase DoD met → row `done`, log line, next phase in
```

Day to day:

```
/phase                       # new chat, no idea where you were → read the brief
/phase and continue          # brief, then actually start the slice
/phase sync                  # end of a working block, before closing the chat
```

Things worth knowing:

- **`NOW.md` is not the plan.** It holds one phase, one slice, one blocked line.
  Checkboxes and DoD live in the phase doc; the board holds the ordering.
- **`BOARD.md` wins.** If the two disagree, the unique `in progress` row is the
  truth and `sync` rewrites `NOW.md`.
- **`sync` never closes a phase** — that's `advance phase`, and only when the DoD is met.
- **Both trees are gitignored** by `init`, so the board is local scratch, not a
  commitment you've published. Unshaped ideas go in the board's Later section or
  a committed root `ROADMAP.md`.
- Old `/session-*` commands still route here: `session-init` → `init`,
  `session-check`/`session-start` → `status`, `session-snap`/`session-end` → `sync`.

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

## OpenCode Console models

[docs/opencode-console-models.md](docs/opencode-console-models.md) is the dated
chart of current models on OpenCode Console (API-charged Zen credits) — list
price, context, Go proxy availability + cap, benchmarks, cost reality, and best
use per model, plus a what-to-actually-run ladder. It replaces the two old Zen
sheets (open-weight + frontier). Re-check the **Updated** date at the top — the
catalog and prices move.

## AGENTS.md template

[docs/AGENTS-TEMPLATE.md](docs/AGENTS-TEMPLATE.md) is the canonical starting point
for a new repo's `AGENTS.md`: copy it in, fill the `REPO:` blocks, delete what doesn't
apply. Sections 1 (Core Rules), 2 (Language Style), 6 (Definition of Done), and
7 (Local Test-Serving Port) are standardized verbatim across repos — edit those
here, not per-project. Sections 3–5 are per-repo: permitted commands, prohibited
targets, and the version/changelog flow.

## Installing (symlinks)

This repo is the source of truth; `~/.claude` just points at it. Install a skill by
symlinking its directory — run these from the repo root, so `$PWD` resolves to it:

```bash
ln -sfn "$PWD/skills/<name>" ~/.claude/skills/<name>
```

Edits made here are live in Claude Code immediately — no copying or re-syncing —
and `git log` stays the single history of every change. The same pattern works for
agents and commands (symlink the individual `.md` file into `~/.claude/agents/` or
`~/.claude/commands/`). New skills appear in Claude's skill list at the next session
start.

Grok and OpenCode both load `~/.claude/skills/`, so that one symlink is enough
for Claude Code, Grok, and OpenCode.

### Multiple profiles

If you run Claude Code with multiple profiles (separate config directories selected
via `CLAUDE_CONFIG_DIR` — see [docs/CLAUDE-PROFILES.md](docs/CLAUDE-PROFILES.md) for
how to set them up), each profile has its own `skills/` directory and none of them
inherit from `~/.claude`. Symlink into every profile **directly** — never chain one
profile's link through another's, again from the repo root:

```bash
scripts/install-skill.sh <name> [<name>...]           # link into every ~/.claude* profile
scripts/install-skill.sh --remove <name> [<name>...]  # remove those links
```

The script does the same as this loop. It also skips a profile that holds a real directory
by that name, and `--remove` only deletes links that point into this repo:

```bash
for d in ~/.claude ~/.claude-*; do
  ln -sfn "$PWD/skills/<name>" "$d/skills/<name>"
done
```

If a profile should have its own variant of a skill, keep that variant as a real
directory in the profile (or as a differently-named skill here) instead of a symlink.

### README check

`scripts/check-readme.sh` fails when the skills badge does not match the number of
`skills/` folders, when a skill has no README table row (or has two), when a row links
a missing skill, or when a `SKILL.md` `name` does not match its folder. The pre-commit
hook runs it with `--staged`, so it checks what the commit holds, not the working tree.
Enable the hook once per clone:

```bash
git config core.hooksPath .githooks
```

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
