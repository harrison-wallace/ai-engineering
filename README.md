# ai-engineering

![Version](https://img.shields.io/badge/version-2.0.0-6366f1?style=flat-square)
![Skills](https://img.shields.io/badge/skills-27-22c55e?style=flat-square)
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
| [basic-review](skills/basic-review/SKILL.md) | Quick sanity check of the current diff for bugs, security issues, bloat, and maintainability, reported as a verdict, a severity (1–3) table with a fix per row, and a coverage line. `/basic-review staged` reviews only what the next commit holds. Flags ripples it cannot settle in one pass (infra names, shared contracts) with a pointer to `basic-impact`, and deleted or loosened guards, retries, timeouts, and tests with a pointer to `advanced-review`, and changed names that docs still mention with a pointer to `update-docs`. |
| [advanced-review](skills/advanced-review/SKILL.md) | The deep version of `basic-review`, for when you want to understand a change, not only clear it to commit. Same scopes plus `branch [<base>]`, same 1–3 scale. It explains what the change does (`basic-how`), checks the old decisions the diff deletes or loosens (`basic-why`, narrow), sweeps `~/git` for ripple (the `basic-impact` method), and runs the repo's tests and validators read-only. Sonnet lens reviewers (correctness, security and data, ripple) get a brief without the chat, so they do not inherit the author's story, and the main agent verifies every lead. The report has a 30-second top (verdict, what it does, findings with a Proof column), then details, history at risk, ripple, checks run, and leads not confirmed, and offers `/basic-teach`. `lite` uses no subagents. Report-only. |
| [basic-impact](skills/basic-impact/SKILL.md) | Find what a change could break **outside** its diff, for software, infra, or both. It sweeps every repo in `~/git`, works through a "where grep stops" checklist (pinned library source, timing, wire shapes, Terraform replace vs update, remote-state readers, shared Docker networks, DNS and IAM names, cron and backup paths), and proves the one fact the change is safe because of on a 5-level ladder with read-only scripts and commands. Anything with side effects is printed as a `!` command for you. Report-only verdict, risks table, cleared list, and checks to run before merge. `deep` adds a Sonnet second opinion. Inspired by the pstack `blast-radius` skill. |
| [check-public-ready](skills/check-public-ready/SKILL.md) | Check for material unsafe on a public repo: secrets, PII, private keys, credentials, internal URLs, and accidental dumps. `diff` (default) checks the working diff before a push. `repo` audits the whole tree plus `.gitignore` and hygiene before you open-source it, and `repo history` adds a bounded git-history scan. Same categories and severity table for both. Report-only. |
| [check-npm-supply-chain](skills/check-npm-supply-chain/SKILL.md) | Audit a repo for npm supply-chain compromise indicators (Shai-Hulud-style worms): malicious install hooks, stealer payloads, IOCs, lockfile and hardening gaps; report-only. |
| [check-ai-ui-tells](skills/check-ai-ui-tells/SKILL.md) | Scan a web UI (code and/or live URL) for 26 typical "AI-generated" design tells (purple gradients, glassmorphism, Inter-only type, pill-badge hero, three identical cards, left-border stripes, scroll fade-ins, buzzword copy), and list each one with evidence and a cluster score. Report-only. |

### AWS

Read-only, single-account, `aws` CLI. Every dollar figure they emit is labelled
as an estimate; none of them mutate infrastructure.

| Skill | Description |
|---|---|
| [aws-cost](skills/aws-cost/SKILL.md) | `mtd` (default): month-to-date spend by service and region from Cost Explorer, with run-rate, month-end forecast, and the change from last month. `optimize`: a savings sweep of Cost Optimization Hub and Compute Optimizer plus direct hunts for idle or orphaned resources and Savings Plans gaps, ranked by estimated monthly saving. |
| [aws-audit](skills/aws-audit/SKILL.md) | Per-service security and cost audit. `s3` (default, the only service so far): every bucket's public access, encryption, TLS, and versioning, then lifecycle gaps, version bloat, abandoned multipart uploads, and storage-class fit. A new service gets its own `references/<service>.md`. |

### Understand

Read-only. `basic-how` says what the code or infra does, `basic-why` says why, and `basic-teach`
runs one or both and teaches the result. `basic-research` covers what outside sources say.

| Skill | Description |
|---|---|
| [basic-how](skills/basic-how/SKILL.md) | Explain how code or infra works today (a subsystem, a runtime flow, a request path through DNS, proxy, and container, or where something should live) as a senior-engineer mental model: Overview, Key concepts, How it works, Where things live, Gotchas, with `file:line` citations and ASCII diagrams. Simple questions stay inline. Complex ones get 2–3 Haiku explorers on separate angles. `lite` uses no subagents, and `deep` adds an Opus-high explainer. Inspired by the pstack `how` skill. |
| [basic-why](skills/basic-why/SKILL.md) | Find out why code or infra is the way it is, from git history, GitHub PRs and issues (`gh`), ADRs, phase docs, CHANGELOG, `CLAUDE.md`/`AGENTS.md`, and memory, and nothing else. Every claim gets a tier (Direct, Supported, Inferred, Speculative, Unknown) and a citation, gaps are named exactly, and a guess in the question is tested, not confirmed. A Sonnet digger works the git and PR history. `lite` is inline, and `deep` adds an Opus-high synthesizer in a fresh context. Before a change, it ends with a Preserve / Change / Avoid / Risk set and points Risk rows at `basic-impact`. Inspired by the pstack `why` skill. |
| [basic-teach](skills/basic-teach/SKILL.md) | Teach a change, subsystem, or piece of infra so it actually lands: picks the takeaways from why you ask, runs `basic-how` and/or `basic-why` (subagents in one message, `why` kept narrow), and gives the smallest complete answer first in plain spoken English, deeper on request. Diagrams build up one part at a time, in ASCII, or as a frame series on an Artifact page for three or more parts. No quizzes, no "key insight" labels, and `basic-why`'s confidence words kept as found. Inspired by the pstack `teach` skill. |
| [basic-research](skills/basic-research/SKILL.md) | Research a question against outside sources: the web, official docs, changelogs, GitHub issues, and papers. Inputs: `<topic>` (default), `decision <question>` (Haiku explorers read the repo for the criteria, then options are compared with a recommendation and a pointer to `basic-architect`), `last` (fact-checks my previous reply and gives corrected statements), and `lib <name> [question]` (versions, breaking changes, and known bugs for the version the repo uses). It shows its strategy and plan, with cost and time, and waits for your approval before it searches. 2–3 Sonnet researchers work separate angles (primary, field, against) without the chat, and the main agent reads the key sources before it rates a claim Direct. `lite` is inline. `deep` adds a Grok X researcher when Grok is signed in (read-only through deny rules), an Opus-high synthesizer in a fresh context, and a Sonnet claim checker. Every claim gets `basic-why`'s confidence tier, a source, and a date. Report-only, with an offer to save Markdown or PDF to `docs/research/`. |

### Design

| Skill | Description |
|---|---|
| [basic-architect](skills/basic-architect/SKILL.md) | Design a new feature, service, or component before code, for software, infra, or both. Haiku agents ground it in the real system, two Sonnet runners sketch structurally different shapes (extend vs reshape), and the main agent screens both against software and infra red flags, merges them, and writes a `proposed` ADR in `docs/adr/`. Then it stops for sign-off and offers `/phase shape`. Optional leading level: `lite` (no subagents) or `deep` (adds one Opus-high runner). Never applies infrastructure. Inspired by the pstack `architect` skill, adapted to run cheaper and to cover infra/DevOps. |

### Fix & apply

| Skill | Description |
|---|---|
| [fix-input-overflow](skills/fix-input-overflow/SKILL.md) | Assess whether the app's native date/month/time inputs overflow on iOS Safari, and apply the global CSS reset fix if so. |
| [fix-react-doctor](skills/fix-react-doctor/SKILL.md) | Run `npx react-doctor@latest` and iteratively fix the reported React anti-patterns until the score reaches 100, verifying the build along the way. |
| [basic-unslop](skills/basic-unslop/SKILL.md) | Cut AI writing tells from the repo's prose and fix them in place: AI vocabulary, filler, hedging, em dashes, abstract metaphors, inline-header lists, title-case headings, chatbot phrases. Targets `diff` (default, changed lines only), `docs`, `readme`, `changelog` (the Unreleased section only), `repo`, or paths. `scan` reports instead. It skips code, quotes, license text, and `archive/`, and updates anchor links when a heading changes. Rules have short names (`em-dash`, `ai-vocab`, `abstract-metaphor`) in `references/rules.md`. Large `repo` and `docs` runs batch files to Sonnet agents. Never commits. Adapted from the pstack `unslop` skill. |
| [update-docs](skills/update-docs/SKILL.md) | Keep the docs true to the code. `diff` (default) searches every doc for the names the current diff changed. `repo` audits every doc for dead paths, links, and anchors, missing scripts and make targets, env vars documented but never read, stale CLI flags, counts and badges, versions, and infra values against compose and Terraform (`references/drift-checks.md`). Every fix needs proof, and it fixes in place by default, or reports with `scan`. CHANGELOG, phase docs, ADRs, and `docs/summary/` are flagged for their owning skills, `AGENTS.md` and `CLAUDE.md` get fact fixes only, and undocumented things are flagged, not written. It runs the repo's own doc checks read-only. `bump-version` hands its doc sync to it, and `basic-review` points to it. |

### Product & design

| Skill | Description |
|---|---|
| [review-dax-insights](skills/review-dax-insights/SKILL.md) | Review a product, feature, or launch plan against Dax Raad's three principles: shareable marketing, one Aha moment, primitives-first retention. |
| [review-website-design](skills/review-website-design/SKILL.md) | Review a website against the premium-psychology framework: Halo Effect hero, cognitive fluency, Peak-End micro-interactions, 2026 trends, ownership. |

### Repo workflow

| Skill | Description |
|---|---|
| [list-skills](skills/list-skills/SKILL.md) | List every skill this profile and project can run: repo skills and commands, your ai-engineering skills (by README section), plugin skills and commands, and built-in skills. Each gets a one-line summary and a "when to use, not for X" sub-bullet. `for <task>` recommends one to three skills instead, and names the near-miss. Filters: `mine`, `repo`, `plugins`, `built-in`, or a keyword. A read-only `scripts/list.py` reads the files fresh, resolves project and user plugin installs, skips disabled plugins, and flags broken links, unmanaged folders, and skills not linked into this profile. |
| [basic-alignment](skills/basic-alignment/SKILL.md) | Play back the ask before any work starts: goal, problem, scope in/out, constraints heard, what done looks like, readings of unclear or dictated words (only the ones that change the meaning), and numbered yes/no assumptions. Simplified Technical English, report-only, no tool calls. `/basic-alignment <messy ask>` restates the given text. `basic-architect` opens its grounding brief and sign-off with the same block. Inspired by the pstack `in-your-own-words` skill. |
| [basic-summary](skills/basic-summary/SKILL.md) | One summary skill, seven inputs, in Simplified Technical English with clear-reading checks (one meaning per sentence, no slashes, real names). `last` (default) reshapes the previous reply so you can scan it. `session` says where this chat stands: Decided, Built, Parked, Open. `work [since <ref> \| last <n> \| <sha>]` lists what landed: Achieved, Fixed, Implemented, then an executive summary. `commit` drafts a commit message in the repo's style, or proposes a split. `pr [<base>]` drafts a PR body (Summary, Changes, Testing, Notes for review), or fills the repo's PR template. `jira` drafts a linear ticket record (Background, What we did in order, Why, Result, Next steps, References), and `management` a 20-second update (What we did, Why it matters, Status, Needs from you). Both take `work`'s scopes, pick up ticket keys such as `ABC-123` from the branch and commits, and follow `references/jira-markdown.md` so the paste needs no editing. `plain` gives a short spoken retelling with no bullets or jargon (the pstack `bro` idea). Report-only. Replaces `summarise-work`. |
| [advanced-summary](skills/advanced-summary/SKILL.md) | The deep version of `basic-summary`, with its core inputs (`last`, `session`, `work`, `commit`, `pr`, `jira`, `plain`). `jira` adds How it works now and Risks to the ticket record. There is no `management` input, because that one stays short. It writes a technical report in plain prose: overview, what changed, how it works now (`basic-how`), why each decision was made, trade-offs and rejected options, what was verified in the session, and risks. A Sonnet decision reader recovers early decisions from the transcript digest in long or compacted chats, and a Sonnet claim checker tests every claim against git and the transcript before you see it. It never runs tests to fill Verification. It can save the report as Markdown or PDF (`scripts/md-to-pdf.sh`, Python `markdown` and headless Chrome) in `docs/summary/`. `lite` uses no subagents. Report-only. |
| [basic-reflect](skills/basic-reflect/SKILL.md) | Mine the current session, or `last <n>` sessions in this project, for durable lessons. A bundled `jq` digest (`digest.sh`, which shrinks a 77 MB transcript to about 88 KB, or about 18 KB with `-b`) feeds 2 Sonnet reviewers ("what to encode" and "what we missed"). The main agent filters for durability, decision change, and "already covered", then routes each lesson to the narrowest home: an ai-engineering skill, the repo's `AGENTS.md`/`CLAUDE.md`, `AGENTS-TEMPLATE.md`, or memory. It applies only the numbered rows you approve. Hooks, settings, scripts, and lessons about skills you do not own stay suggestions. `lite` uses no subagents; `deep` adds a third reviewer and puts "missed" on Opus high. Inspired by the pstack `reflect` skill. |
| [bump-version](skills/bump-version/SKILL.md) | Cut a release in any repo: detect where the version lives (`package.json`, `Cargo.toml`, `pyproject.toml`, `VERSION`, tags only, or a mix), bump every mirror, and write a `CHANGELOG.md` entry from the diff in the repo's own format. Defers to a repo-local release skill or script. `sonnet` splits the release in two: the main agent derives it and writes the changelog prose, a Sonnet subagent applies the edits, and the main agent verifies. |
| [delegate](skills/delegate/SKILL.md) | Implement the work just discussed through the right implementer. The main agent plans, assesses size, risk, and how mechanical the work is, recommends a route, and shows a menu with relative cost ($ to $$$) and time (# to ###): `self`, `balanced` (Sonnet), `accuracy` (Opus high), `a/b` (`grok-sonnet`, `sonnet-opus`, or `sonnet-sonnet` with extend and reshape briefs, in separate worktrees), `speed` (parallel Sonnet low), `cheap` (Haiku), `grok` (the latest Grok model, headless), `mixed` (Grok and Claude split the units), and `multi` (Haiku, Sonnet, or Opus per unit). Then it reviews, scores each implementer out of 5, fixes, and summarises. It recommends `self` when delegating would cost more than it saves. Replaces `imp-sonnet` and `imp-grok-4-7`. |

`imp-grok-4-5`, `imp-grok-4-6`, `imp-grok-4-7`, and `imp-sonnet` (all merged into `delegate`), and `summarise-work` (merged into `basic-summary work`) are archived under [archive/skills](archive/skills). They are not installed and do not trigger.

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
