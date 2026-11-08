# ai-engineering

```text
           ░██                                         ░██                                          ░██

 ░██████   ░██         ░███████  ░████████   ░████████ ░██░████████   ░███████   ░███████  ░██░████ ░██░████████   ░████████
      ░██  ░██░██████ ░██    ░██ ░██    ░██ ░██    ░██ ░██░██    ░██ ░██    ░██ ░██    ░██ ░███     ░██░██    ░██ ░██    ░██
 ░███████  ░██        ░█████████ ░██    ░██ ░██    ░██ ░██░██    ░██ ░█████████ ░█████████ ░██      ░██░██    ░██ ░██    ░██
░██   ░██  ░██        ░██        ░██    ░██ ░██   ░███ ░██░██    ░██ ░██        ░██        ░██      ░██░██    ░██ ░██   ░███
 ░█████░██ ░██         ░███████  ░██    ░██  ░█████░██ ░██░██    ░██  ░███████   ░███████  ░██      ░██░██    ░██  ░█████░██
                                                   ░██                                                                   ░██
                                             ░███████                                                              ░███████
```

![Version](https://img.shields.io/badge/version-3.3.1-6366f1?style=flat-square)
![Skills](https://img.shields.io/badge/skills-37-22c55e?style=flat-square)
![Claude Code](https://img.shields.io/badge/Claude_Code-assets-d97757?style=flat-square)

A home for reusable AI agent and Claude Code files: skills, subagents, slash commands, and hooks.

## Start here

Find the stage you are in, then the skill. Each skill's `SKILL.md` holds its flags, models, and
files.

```
before work   /restate-ask → /design → /prototype → /phase shape
understand    /explain-how · /explain-why · /teach · /research → /advise · /explain-again
build         /delegate · /diagnose · /guide-setup
check         /review → /review-deep → /trace-impact
ship          /summarise commit → /update-docs → /bump-version → /reflect
```

## Skills

### Plan & design

| Skill | What it does |
|---|---|
| [restate-ask](skills/restate-ask/SKILL.md) | Play back your ask before work starts: goal, scope, what done looks like, unclear words, and numbered yes or no assumptions. Report-only. From pstack `in-your-own-words`. |
| [advise](skills/advise/SKILL.md) | Turn research or any skill's findings into the top three moves for this project, each tied to a tiered finding, with a plan-impact table, tests for the unknowns, and what not to do. `deep` adds an Opus contrarian. It edits the plan only after `apply`. |
| [design](skills/design/SKILL.md) | Shape a new feature, service, or infra change before code: ground it in the real system, sketch two structurally different designs, screen them, and write a proposed ADR for sign-off. From pstack `architect`. |
| [prototype](skills/prototype/SKILL.md) | Answer one design question that talk cannot settle with throwaway code: a clickable logic demo, or UI variants behind `?variant=`. It records the answer in an ADR, then deletes the code. From Matt Pocock's `prototype`. |
| [define-terms](skills/define-terms/SKILL.md) | Settle the project's names in `GLOSSARY.md`, report drift between the glossary and the code, and write short decision ADRs. From Matt Pocock's `domain-modeling`. |
| [check-architecture](skills/check-architecture/SKILL.md) | Find shallow modules in existing code and infra, where the interface is nearly as complex as what it hides, and report at most five proven candidates. From Matt Pocock's `improve-codebase-architecture`. |

### Understand

Read-only. `explain-how` says what the code or infra does, `explain-why` says why, and `teach`
runs one or both and teaches the result. `research` covers what outside sources say, and
`advise` (under Plan & design) turns its findings into moves.

| Skill | What it does |
|---|---|
| [explain-how](skills/explain-how/SKILL.md) | Explain how code or infra works today as a senior-engineer mental model, with `file:line` citations and ASCII diagrams. From pstack `how`. |
| [explain-why](skills/explain-why/SKILL.md) | Find why code or infra is the way it is from git history, PRs, ADRs, and docs, with a confidence tier and a source on every claim. From pstack `why`. |
| [teach](skills/teach/SKILL.md) | Run `explain-how` or `explain-why`, then teach the result in plain English: the smallest complete answer first, and diagrams built up one part at a time. From pstack `teach`. |
| [research](skills/research/SKILL.md) | Research a question against outside sources and give the answer first, with a confidence tier, a source, and a date on every claim. It waits for your approval of its plan. |
| [explain-again](skills/explain-again/SKILL.md) | Type it when a reply did not land. The agent re-pitches it with the context you were missing, in plain English and the project's glossary terms. From Matt Pocock's `wait-what`. |

### Build & fix

| Skill | What it does |
|---|---|
| [delegate](skills/delegate/SKILL.md) | Implement the work just discussed through the right implementer (self, Sonnet, Opus, Haiku, Grok, or a mix), picked from a menu with relative cost and time. It then reviews and scores the result. |
| [diagnose](skills/diagnose/SKILL.md) | Find and prove the cause of one reported failure: a loop that goes red first, ranked guesses you approve, one probe at a time, then a fix after your yes. From Matt Pocock's `diagnosing-bugs`. |
| [guide-setup](skills/guide-setup/SKILL.md) | Write a bash script that walks you through steps only you can do (dashboards, keys, CI and Jenkins credentials, SSM), for you to run in your own terminal. From Matt Pocock's `wizard`. |
| [fix-prose](skills/fix-prose/SKILL.md) | Cut AI writing tells from the repo's prose and fix them in place, or report them with `scan`. From pstack `unslop`. |
| [fix-react-doctor](skills/fix-react-doctor/SKILL.md) | Run `react-doctor` and fix the React anti-patterns it reports until the score reaches 100, checking the build along the way. |
| [fix-input-overflow](skills/fix-input-overflow/SKILL.md) | Check whether native date and time inputs overflow on iOS Safari, and apply the global CSS reset if they do. |

### Review & check

| Skill | What it does |
|---|---|
| [review](skills/review/SKILL.md) | Quick pre-commit check of the working diff for bugs, security, bloat, and maintainability, as a verdict and a severity table. Report-only. |
| [review-deep](skills/review-deep/SKILL.md) | Deep review of one change: what it does, the old decisions it undoes, what it breaks outside the diff, and the repo's own checks, with a proof for each finding. Report-only. |
| [trace-impact](skills/trace-impact/SKILL.md) | Find what a change could break outside its diff, across every repo in `~/git`, for software, infra, or both, and prove the facts that grep cannot. From pstack `blast-radius`. |
| [check-public-ready](skills/check-public-ready/SKILL.md) | Check the diff, the whole repo, or its history for material that is unsafe on a public repo: secrets, PII, keys, internal URLs, and dumps. Report-only. |
| [check-npm-supply-chain](skills/check-npm-supply-chain/SKILL.md) | Check a repo for npm supply-chain compromise: malicious install hooks, credential stealers, exfil workflows, and tampered lockfiles. Report-only. |
| [check-ui-tells](skills/check-ui-tells/SKILL.md) | Scan a web UI's code or live URL for the typical AI-generated design tells, with evidence and a cluster score. Report-only. |
| [check-primitives](skills/check-primitives/SKILL.md) | Check the diff for rules kept in `if`s and flags instead of a data structure: flags that must agree, a branch for each kind, `useState` clusters. Each finding names the primitive. Report-only. From pstack `principle-model-the-domain`. |
| [review-product](skills/review-product/SKILL.md) | Review a product or launch plan against Dax Raad's principles: shareable marketing, one Aha moment, and primitives-first retention, mapped against the real data model. `feature` judges one planned feature. |
| [review-site](skills/review-site/SKILL.md) | Review a website against the premium-website framework: the first impression, cognitive fluency, Peak-End micro-interactions, current trends, and ownership. |

### Ship & record

| Skill | What it does |
|---|---|
| [summarise](skills/summarise/SKILL.md) | Summarise the last reply, the session, or what landed, or draft a commit message, a PR body, a Jira update, or a manager update. Report-only. `plain` mode from pstack `bro`. |
| [summarise-deep](skills/summarise-deep/SKILL.md) | The deep version of `summarise`: a technical report with the mechanism, the reasons, the trade-offs, what was verified, and the risks, with every claim checked against git. |
| [update-docs](skills/update-docs/SKILL.md) | Find statements in the docs that the code has made wrong, prove each one, and fix it in place, or report with `scan`. |
| [bump-version](skills/bump-version/SKILL.md) | Cut a release in any repo: bump every version mirror and write a CHANGELOG entry from the diff. It defers to a repo-local release flow. |
| [showcase](skills/showcase/SKILL.md) | Pitch the work you just did as an X post, article, or video idea: drafts to rewrite, with proof from the session. Grok checks each hook on X when installed, and `deep` reads this project's last 7 days. It never posts. |
| [reflect](skills/reflect/SKILL.md) | Mine this session, or the last few, for durable lessons, and route each to the narrowest home: a skill, `CLAUDE.md`, the AGENTS template, or memory. From pstack `reflect`. |

### Track

| Skill | What it does |
|---|---|
| [phase](skills/phase/SKILL.md) | Long-horizon phase board for the repo you are in: `BOARD.md` for phases, `NOW.md` for the current slice, and phase docs with checkboxes and DoD. Commands and workflow are in [docs/phase.md](docs/phase.md). |

### AWS

| Skill | What it does |
|---|---|
| [aws-cost](skills/aws-cost/SKILL.md) | AWS spend for one account, read-only. `mtd` breaks down month-to-date spend with a forecast, and `optimize` ranks savings by estimated monthly amount. |
| [aws-audit](skills/aws-audit/SKILL.md) | Read-only audit of one AWS account, one service at a time. `s3` checks every bucket for security practice and cost savings. |

### Tools

| Skill | What it does |
|---|---|
| [serve-page](skills/serve-page/SKILL.md) | Serve a self-contained HTML page on your LAN, on the first free port from 38081, and stop it when you are done. Other skills build their `page` views through it. |
| [list-skills](skills/list-skills/SKILL.md) | List every skill this profile and project can run, with when to use each, or recommend the right one with `for <task>`. |

`imp-grok-4-5`, `imp-grok-4-6`, `imp-grok-4-7`, and `imp-sonnet` (merged into `delegate`), and
`summarise-work` (merged into `summarise work`) are archived under [archive/skills](archive/skills).
They are not installed and do not trigger.

## Install

This repo is the source of truth, and each Claude Code profile links to it. Run from the repo
root:

```bash
scripts/install-skill.sh <name> [<name>...]           # link into every ~/.claude* profile
scripts/install-skill.sh --remove <name> [<name>...]  # remove those links
```

- Each profile (`CLAUDE_CONFIG_DIR`, see [docs/CLAUDE-PROFILES.md](docs/CLAUDE-PROFILES.md)) gets
  its own direct link. A link never chains through another profile.
- The script skips a profile that holds a real folder by that name. `--remove` deletes only links
  that point into this repo.
- Edits here are live at once. A new skill shows up at the next session start.
- Grok and OpenCode also load `~/.claude/skills/`, so the same link serves all three.
- For agents and commands, link the single `.md` file into `~/.claude/agents/` or
  `~/.claude/commands/`.
- For a profile that needs its own variant of a skill, keep a real folder in that profile, or add
  the variant here under another name.

### README check

`scripts/check-readme.sh` fails when the skills badge does not match the number of `skills/`
folders, when a skill has no table row (or has two), when a row links a missing skill, when a row's
"What it does" cell is over 300 characters, or when a `SKILL.md` `name` does not match its folder.
The pre-commit hook runs it with `--staged`. Enable the hook once per clone:

```bash
git config core.hooksPath .githooks
```

## Adding a skill

Follow the checklist in [CLAUDE.md](CLAUDE.md): name it by a verb from the Naming table, add one
table row here, run `scripts/check-readme.sh`, link it with `scripts/install-skill.sh`, and credit
a port in its row and in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

```
skills/
  my-skill/
    SKILL.md        # required: frontmatter + instructions
    references/     # optional supporting files
```

```markdown
---
name: my-skill
description: One line saying what this does and when to use it.
---

Instructions for the skill go here.
```

## Layout

```
skills/      Agent Skills: one folder per skill, each with a SKILL.md
agents/      Subagent definitions: one .md file per agent
commands/    Custom slash commands: one .md file per command
hooks/       Hook scripts referenced from settings.json
docs/        Supporting documentation (templates, cheat sheets)
scripts/     Repo maintenance: install-skill.sh, check-readme.sh
.githooks/   Git hooks (pre-commit runs check-readme.sh)
CLAUDE.md    Instructions Claude reads when working in this repo
THIRD_PARTY_NOTICES.md  Licenses for adapted upstream work (pstack and Matt Pocock's skills, MIT)
```

These folders mirror Claude Code's own layout: `~/.claude/skills/<name>/`,
`~/.claude/agents/<name>.md`, and `~/.claude/commands/<name>.md`, or the same under a project's
`.claude/`. Agent files take `name`, `description`, and optional `tools` and `model` frontmatter.
Hooks are wired up through `settings.json` and must stay executable.

`docs/adr/` and the `phase` trees (`docs/plans/`, `docs/phases/`) are local and gitignored.

## Docs

- [docs/phase.md](docs/phase.md): the `phase` commands, a phase from start to finish, and the rules
  of the board.
- [docs/AGENTS-TEMPLATE.md](docs/AGENTS-TEMPLATE.md): the starting point for a new repo's
  `AGENTS.md`. Copy it in, fill the `REPO:` blocks, and delete what does not apply. Sections 1, 2,
  6, and 7 (Core Rules, Language Style, Definition of Done, Local Test-Serving Port) are the same
  in every repo, so edit them here. Sections 3 to 5 are per repo.
- [docs/opencode-console-models.md](docs/opencode-console-models.md): a dated chart of the models
  on OpenCode Console, with price, context, benchmarks, and best use. Check its **Updated** date,
  because the catalogue and prices move.
- [docs/CLAUDE-PROFILES.md](docs/CLAUDE-PROFILES.md): how to set up several Claude Code profiles.

## Versioning

The repo is versioned as a whole: `package.json` holds the current version, `CHANGELOG.md` records
what changed, and each release is tagged (`git tag vX.Y.Z`). **Patch** is a tweak to an existing
asset, **minor** adds a skill, agent, or command, and **major** renames or removes an asset, or
changes how it is invoked. Run `/bump-version` to cut a release.
