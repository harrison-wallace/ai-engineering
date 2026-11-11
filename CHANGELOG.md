# Changelog

All notable changes to this repo are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html):
**patch** = tweaks to an existing skill/agent/command, **minor** = new asset added,
**major** = an asset renamed, removed, or changed in a way that breaks how it's invoked.

## [Unreleased]

## [3.4.2] - 2026-11-11

### Added
- `teach` routes the ask with no flags. "Where are we", the phase, slices, or pending decisions
  get a tabbed LAN page (`references/phase-page.md`): Now, Roadmap, Phase (slices as a flow, with
  their checklists and the DoD), Infra (the diagram as built, building, and planned, with a
  stepper), and Decisions. Clicking a decision or a slice lights up the infra parts it touches.
  It reads both phase-doc shapes (`## Slices` lists and numbered `### N.M` slices) and says when
  the board is stale.
- `teach/scripts/infra-inventory.py`: lists the infra a repo's files define today (compose
  services, `docker run` flags in Jenkinsfiles, Caddy routes, Terraform resources and their
  references, k8s objects, and workflows), so every built box on a diagram comes from a file.
  Infra subjects in `teach` run it first.
- `serve-page/references/infra-diagrams.md`: one drawing grammar for infra pages. It covers
  boundaries for Docker hosts, AWS, and k8s, fixed lanes, part shapes, edge labels, the built,
  building, planned, and decision overlay, and fixed geometry so hand-written SVG does not
  overlap.
- `serve-page` dynamic pages: `assets/dynamic.js` drives tabs, layer toggles, click-to-highlight,
  and steppers, with no fetch and no external code. `page-rules.md` gains a Dynamic pages section.
- `phase` open decisions: `PHASE.template.md` has `## Open decisions` (question, options, what it
  blocks). `/phase` shows the count, `sync` adds new ones and drops the ones an ADR or
  `DECISIONS.md` settled, and the status page points to `/teach where are we`.

### Security
- The inventory never prints env values whose names hold a secret (KEY, SECRET, TOKEN, PASS,
  PWD, CRED, AUTH), and it strips `user:password@` from URLs.

## [3.4.1] - 2026-11-11

### Added
- Fable tier: set `CLAUDE_FABLE_TIER=1` in a profile's `env` block and each skill's one
  fresh-context judge runs on Fable `medium` in place of Opus `high`, with a re-run on Opus `high`
  if the Fable call fails. Unset, nothing changes. `scripts/fable-tier.sh` prints the pair, and
  skills call it at load time through `${CLAUDE_SKILL_DIR}`.
- README section **Fable tier**: how to turn it on per profile, what it changes, and its cost.

### Changed
- The judge roles in `advise`, `check-architecture`, `design`, `explain-how`, `explain-why`,
  `improve`, `reflect`, and `research` read the Fable tier, and each skill allows the tier script
  in `allowed-tools`. Their level tables, the README row, and the descriptions name the judge
  tier, not Opus. The `advise` coverage line reports the model the contrarian ran on.
- `docs/AGENTS-TEMPLATE.md` §8 and `CLAUDE.md` **Model routing** add the Fable-tier rule and how
  a new judge role uses the script.

## [3.4.0] - 2026-11-10

### Added
- `improve` skill: look at one feature, service, or infra stack from first principles. It grounds
  in the area's job, runs five lenses (simplify, deepen, data shape, ops and cost, docs drift), and
  proves each finding. Then it sends each finding to its next skill: `research`, `trace-impact`,
  `design`, `prototype`, `delegate`, or `advise`. `auto` runs `research lite` and `trace-impact`
  without asking. `aws` adds the AWS sweeps. It never edits code before your yes. New verb
  `improve` in the Naming table.
- `docs/AGENTS-TEMPLATE.md` §8 Subagent Model Routing: a routing table by job (Haiku for reads,
  Sonnet `medium` for repeated review and research, Opus `high` for one fresh-context judgement,
  the main session for edits and judgement calls), the escalation order, and the Explore and
  cloud-alias notes.
- `CLAUDE.md` sections **Skill structure** and **Model routing**: the rules for new skills, from
  the Claude 5 model-choice research. They cover the 500-line `SKILL.md` limit, a `## Contents`
  list in each reference file over 100 lines, self-contained subagent prompts, `model` and
  `effort` on every Agent call, no `model` in skill frontmatter, and fan-out only after a test.

### Changed
- `delegate` `speed` route: each unit runs its own acceptance check, and only the failed units
  re-run at `effort: medium`.
- `bump-version` `sonnet` mode sets `effort: medium` on its Sonnet subagent.
- The 11 reference files over 100 lines now start with a `## Contents` list of their headings
  (`aws-audit`, `aws-cost`, `bump-version`, `check-public-ready`, `delegate`, `explain-why`,
  `prototype`).
- `.gitignore` excludes `docs/research/` and `docs/improve/`, which hold local reports.

## [3.3.2] - 2026-11-09

### Changed
- `review` reports severity as `High`, `Medium`, or `Low` instead of `3`, `2`, or `1`. The `Sev`
  column uses the words, and the verdict counts read `1 high, 2 medium`. What each level means
  and how findings are ranked are unchanged.
- `review-deep` and `trace-impact` use the same words, because both share `review`'s scale. In
  `trace-impact` this covers the verdict rules, the risk table, and the page's colour key.
- `docs/AGENTS-TEMPLATE.md` completion check: run only the checks that cover what changed during
  a task, say which checks ran, and run the full set once at the end when shared code, a root
  config, or the lockfile changed.

## [3.3.1] - 2026-11-08

### Fixed
- `bump-version` prints an annotated tag (`git tag -a vX.Y.Z -m "Release X.Y.Z"`) and
  `git push --follow-tags` under **Next**. The old lightweight `git tag vX.Y.Z` was skipped by
  `--follow-tags`, so a release reached the remote without its tag.

## [3.3.0] - 2026-11-08

### Added
- `advise` skill: turns findings into the top three moves for the project you are in. Input is a
  `/research` report, saved reports in `docs/research/` (`<path>...` or `all`), another skill's
  report, a pasted document, and/or a free-text question. It reads the plan docs (product doc,
  phases, `BOARD.md`/`NOW.md`, ADRs, `CLAUDE.md`/`AGENTS.md`), builds a ledger of tiered findings,
  and labels each move by evidence (strong, mixed, thin), cost, and door (one-way or two-way). The
  report adds a plan-impact table with `path:line`, what a newer report overturns, tests for the
  unknowns, Don't do, and Watch. `deep` adds an Opus contrarian at `high`
  (`references/contrarian-prompt.md`) that argues against the top move in a fresh context. `apply`
  edits the picked plan docs only; phase shape goes to `/phase shape`, and a move against an
  accepted ADR goes to `/design`. It never edits input reports, ADRs, or code, never takes its own
  saved `*-advice-*.md` files as findings, and does no web search.
- `advise` row in the `CLAUDE.md` Naming table (not `recommend`, `suggest`, or `consult`).

### Changed
- `research` reports hold evidence only: no "What this means for <project>" sections and no offer
  to edit plan docs. Every report now ends with *"Or reply `advise`"* to hand the report to
  `/advise`. A bare "yes" answers the save offer only.
- `list-skills` names `research` and `advise` as neighbours that are easy to confuse.

## [3.2.0] - 2026-11-08

### Added
- `showcase` skill: pitches the work just done as at most 3 X post, article, or video ideas,
  each with a draft and the proof from the session. Grok checks the hooks on X when it is
  installed, and `deep` reads this project's sessions from the last 7 days, and asks before it
  reads other projects. Kept pitches go to `~/showcase/capture-<yy-mm-dd-hh-mm>-<repo>-<topic>.md`
  through `scripts/showcase.sh`, the only writer. It refuses secret-like hooks before they reach
  Grok, and secret-like lines in a kept pitch (X post URLs are masked first). `list`, `used`, and
  `drop` track each pitch. It never posts.
- `showcase` row in the `CLAUDE.md` Naming table (not `promote` or `market`).

### Changed
- `bump-version`, `diagnose`, `prototype`, `research`, and `teach` end with a one-line
  `/showcase` offer when the work has a concrete result, at most once a session.

## [3.1.0] - 2026-11-07

### Added
- `check-primitives` checks code for missing primitives, where the domain lives in conditionals instead of in a data structure, after pstack `principle-model-the-domain` and `principle-foundational-thinking`. `references/signs.md` lists 14 signs with stable IDs: state (flags that must agree, phase checks spread out, ad hoc mutation), data shape (a branch for each kind, the same switch twice, dependent optional fields, loose shapes, the wrong collection), modules (split by time, two writers), and React (`useState` clusters, stored derived state, state with two owners, boolean props that exclude each other), plus a do-not-flag list. `diff` (default) counts only signs the diff adds or grows, `staged` checks only the index, and paths check files in full. Each finding names a concrete invalid state or next edit, every site, and the primitive, with a short sketch for strong ones. Report-only, and it offers `/design lite`, `/delegate`, or `/prototype logic`.

### Changed
- `review-product` grounds Retention in the repo. A primitives map names at most 7 primitives with the model or type that holds each (Prisma, Drizzle, SQL migrations, Zod, core types), maps each feature onto one, marks one-offs (a table that repeats a primitive's fields, a column for one feature, a hardcoded list, a route that skips the primitive's module), and names a power-user unlock for each. It offers `/check-primitives` for one-offs that come from code shape. `feature <idea>` judges one planned feature as Extends, Exposes more, New primitive, or One-off, with the smallest data change that keeps it off One-off. Marketing and Aha moment are unchanged.
- `design` screens candidates for three more software red flags (invalid states can be written, a branch for each kind, two owners of client state), and runner step 2 asks for the primitives, states, and transitions before any logic.

## [3.0.0] - 2026-11-07

### Added
- `diagnose` finds the cause of one reported failure through gated phases, after Matt Pocock's `diagnosing-bugs`. No theory is allowed until one command goes red on this bug and has been run. `references/loops.md` lists app, UI, infra (`curl` per hop, `dig`, `docker compose logs`, read-only `aws` and Logs Insights), `git bisect run`, flaky-rate, and performance loops. It then shrinks the repro, shows 3–5 ranked falsifiable guesses and stops for the user, probes one variable at a time with `[DEBUG-xxxx]` tagged logs, and fixes only after a yes, with a regression test at a correct seam. A missing seam is a finding for `check-architecture`. `lite` is read-only guesses. `deep` adds a Sonnet guesser (`references/guesser-prompt.md`) that never sees the main agent's theory. A diagnosis log in the scratchpad survives compaction. `scripts/hitl-loop.template.sh` runs a human step in the user's own terminal and saves the answers to a `.out` file. Shared systems stay read-only. User-invoked only.
- `prototype` builds throwaway code that answers one design question that talk cannot settle, after Matt Pocock's `prototype`. `logic` writes a self-contained HTML demo in `docs/prototypes/<slug>/` around a pure state module, with a state panel, free-play buttons, and walkthrough tabs (`references/logic.md`). `ui` builds 3–5 structurally different variants from written briefs on an existing route behind `?variant=`, with a floating switcher hidden in production, on a `prototype/<slug>` branch (`references/ui.md`, Next.js first). `page` serves the demo, or desktop and phone screenshots of the variants. The answer goes into a short ADR in the `define-terms` format, or into the proposed ADR of the `design` run that asked. Cleanup works from a manifest, file backups, and a `git status` baseline, then deletes the branch with `git branch -d`. It offers `/delegate` for the proper rewrite. User-invoked only.
- `guide-setup` writes an interactive bash script that walks the user through steps only a human can do, after Matt Pocock's `wizard`. It scopes the stages from `.env*`, compose, workflow `secrets.*` and `vars.*`, Jenkinsfile credential IDs, and SSM names, and confirms them as a table. `template.sh` keeps the upstream library and adds a terminal check, a stop when git does not ignore `.env`, `set_ssm` behind a y/N with the account and region, and `jenkins_credential` as a manual step with the exact ID. The user runs it in their own terminal, so typed values never reach the chat. It saves to the scratchpad, or to `scripts/setup-<slug>.sh` with `keep`. The model may offer it when a task hits three or more manual steps, and builds it only after a yes.
- `explain-again` re-pitches a message that did not land, with the missing context, in Simplified Technical English and the `GLOSSARY.md` terms, after Matt Pocock's `wait-what`. The body stays two sentences on purpose. User-invoked only.
- `serve-page` serves a self-contained HTML page on the LAN, on the first free port from 38081 to 38089, and stops it. `scripts/serve-page.sh` has `plan` (the URL, starting nothing), `start` (run in a background task), `check`, and `stop`, which stops a server only when it serves that exact folder. `references/page-rules.md` holds the shared rules: inline CSS and SVG with no CDN scripts, light and dark themes, phone width, the same facts as the reply, `dataviz` for charts, and a warning line on pages with account IDs, costs, or hosts. `/serve-page <file.html>` copies a page into a fresh scratchpad folder and serves it, and `/serve-page stop` stops this session's servers.
- `check-architecture` surveys existing code and infra for deepening opportunities, after Matt Pocock's `improve-codebase-architecture` and `codebase-design`. Scope is the hot spots from `scripts/hotspots.sh` (churn in the last 200 commits, skipping lockfiles, manifests, and generated files), a named area, or `for <plan>`. Sonnet explorers (`references/explorer-prompt.md`) use the vocabulary in `references/vocabulary.md`, which adds infra signs and infra dependency kinds. The main agent proves every candidate (callers, interface size, the deletion test, tests today) and runs a narrow `explain-why` on old decisions. `deep` adds an Opus-high judge (`references/judge-prompt.md`). The terminal report has at most 5 candidates with ASCII before/after diagrams. `page` builds a self-contained HTML page and serves only its folder on the LAN at port 38081 (`references/lan-page.md`). One round of at most 6 questions follows, then a hand-off to `design`. Upstream's open-ended grilling and automatic glossary writes are replaced by the bounded round and approved rows.
- `define-terms` owns `GLOSSARY.md` and short decision and rejection ADRs, after Matt Pocock's `domain-modeling`. Inputs are `init`, `<topic>`, `check` (report-only drift), and `adr <decision>` (only when it is hard to reverse, surprising, and a real trade-off, in `references/adr-format.md`). `init` uses Haiku term extractors (`references/term-extractor-prompt.md`) on larger repos. Questions come in at most 2 rounds with recommended answers, and only approved rows are written. `scripts/glossary.py` prints the terms as TSV for `check-architecture`.

### Changed
- `design`, `trace-impact`, `aws-cost`, `review-deep`, `check-ui-tells`, `research` (for a `decision` or a wide comparison), and `phase` status offer `page`, built and served through `serve-page`: candidates side by side, a risk map, cost charts, before and after flows, tells with screenshots, the comparison table, and the board. `teach` serves its frame series as a LAN page instead of an Artifact. `check-architecture`'s page now uses `serve-page`, so it takes the first free port instead of a fixed 38081.
- **Breaking:** skills are named `<verb>-<object>` after the action they do, from one verb set where each verb has one meaning and no synonyms (`CLAUDE.md` Naming, which now includes `diagnose`, `prototype`, and `guide`). `-deep` marks a deep partner, and `basic-` and `advanced-` are gone. 16 skills are renamed: `basic-review` → `review`, `advanced-review` → `review-deep`, `review-dax-insights` → `review-product`, `review-website-design` → `review-site`, `check-ai-ui-tells` → `check-ui-tells`, `basic-impact` → `trace-impact`, `basic-how` → `explain-how`, `basic-why` → `explain-why`, `basic-teach` → `teach`, `basic-architect` → `design`, `basic-research` → `research`, `basic-summary` → `summarise`, `advanced-summary` → `summarise-deep`, `basic-alignment` → `restate-ask`, `basic-reflect` → `reflect`, `basic-unslop` → `fix-prose`. Every reference between skills, the README, the notices, and the profile links follow. Invoke the new names, such as `/review` and `/explain-why`.
- `update-docs` leaves `GLOSSARY.md` and `GLOSSARY-MAP.md` to `define-terms`. `list-skills` names `check-architecture` and `design` as neighbours.
- `design` tags a sign-off question `prototype` when it is about how a state model behaves or how a screen looks, and offers `/prototype` for it. `summarise` names `explain-again` as the skill for a reply that did not land.
- `README.md` is a short index: the banner, a Start here map of the workflow, and eight groups ordered by when you reach for a skill (Plan & design, Understand, Build & fix, Review & check, Ship & record, Track, AWS, Tools). Each row is one or two sentences and ends with the credit for a port. Install leads with `scripts/install-skill.sh`, the `phase` cheatsheet moved to `docs/phase.md`, and the file shrank from 31 KB to 13 KB. `list-skills` shows the new group names.
- `scripts/check-readme.sh` fails when a row's description is over 300 characters, and `CLAUDE.md` states the row rule.
- A new `.gitignore` keeps `docs/adr/` and the `phase` trees (`docs/plans/`, `docs/phases/`) out of git.
- `THIRD_PARTY_NOTICES.md` adds a Matt Pocock section with the MIT license, for `check-architecture`, `define-terms`, `diagnose`, `prototype`, `guide-setup`, and `explain-again`.

### Fixed
- `serve-page.sh plan` with no folder prints the usage text instead of failing on an unbound variable.

### Removed
- The 16 old skill names above. Their profile links are removed, and they no longer trigger.

## [2.0.0] - 2026-11-07

### Added
- `basic-research` researches a question against outside sources and gives the answer first. Inputs are `<topic>`, `decision <question>` (options against criteria that Haiku explorers take from the repo), `last` (a fact check of the previous reply, with corrected statements), and `lib <name>` (versions, breaking changes, and known bugs for the version in use). It stops for approval of its strategy and plan before it searches. 2–3 Sonnet researchers work the primary, field, and against angles from `references/researcher-prompt.md`. `deep` adds a read-only Grok X researcher (`references/grok-x.md`, skipped when Grok is not signed in), an Opus-high synthesizer, and a Sonnet claim checker. Claims use `basic-why`'s five tiers, adapted in `references/evidence.md`, with a source and a date each. It can save Markdown or PDF to `docs/research/` through `advanced-summary`'s `md-to-pdf.sh`.
- `update-docs` keeps the docs true to the code, and fixes in place by default, or reports with `scan`. `diff` (default) searches every doc for the names the current diff changed. `repo` audits every doc with the proofs in `references/drift-checks.md`: paths, links, and anchors, commands, env vars in both directions, CLI flags, counts and badges, versions, and infra values against compose and Terraform. Every edit needs proof. Docs owned by other skills (CHANGELOG, phase docs, ADRs, `docs/summary/`) are flagged, `AGENTS.md` and `CLAUDE.md` get fact fixes only, and gaps are flagged, not written. Runs over 15 docs batch claim extraction to Haiku agents.
- `delegate` replaces `imp-sonnet` and `imp-grok-4-7`. The main agent plans, splits the work into units that touch separate files, assesses size, risk, how mechanical it is, and how much it leans on the chat, and recommends a route from a menu with relative cost ($ to $$$) and time (# to ###) for this task. The routes are `self`, `balanced` (Sonnet medium), `accuracy` (Opus high), `a/b` (`grok-sonnet`, `sonnet-opus`, or `sonnet-sonnet` with extend and reshape briefs, each side in a seeded detached worktree), `speed` (parallel Sonnet low), `cheap` (Haiku), `grok`, `mixed` (Grok and Claude split the units), and `multi` (Haiku, Sonnet, or Opus per unit). It recommends `self` when delegation would cost more than it saves. Grok routes pick the latest `grok-<major>.<minor>` from `grok models` on every run. Shared parts are in `references/brief.md`, `references/grok.md` (the invocation, deny rules, and troubleshooting from `imp-grok-4-7`), and `references/scorecard.md` (the six-dimension score, per implementer, with `a/b` compared side by side). Under a Grok host, Claude implementers run through `claude -p`.
- `check-public-ready [diff | repo [history]]` replaces `check-diff-public-ready` and `check-repo-public-ready`. Their bodies moved to `references/diff.md` and `references/repo.md`.
- `aws-cost [mtd | optimize]` replaces `aws-cost-mtd` and `aws-cost-optimize`, and `aws-audit [s3]` replaces `aws-s3-audit`, with room for more services. Their bodies moved to `references/`.
- `list-skills` lists every skill this profile and project can run, with a one-line summary and a "when to use, not for X" sub-bullet. It groups repo skills, your skills (by README section), plugins, and built-ins. `for <task>` recommends one to three skills and names the near-miss. Filters are `mine`, `repo`, `plugins`, `built-in`, or a keyword. A read-only `scripts/list.py` reads the frontmatter fresh from `<project>/.claude/`, `<config>/skills` and `commands`, and installed plugins (the project entry first, then the user entry, honouring `enabledPlugins`). It skips the claude.ai `synced/` folder and flags broken links, unmanaged folders, skills not linked into the profile, and disabled plugins.
- `basic-how` explains how code or infra works today, read-only, as a senior-engineer mental model with `file:line` citations and ASCII diagrams. Simple questions stay inline. Complex ones get 2–3 Haiku Explore agents on separate angles (`references/explorer-prompt.md`), and the main agent checks the load-bearing files and explains in the `references/explainer-prompt.md` format. `lite` uses no subagents, and `deep` adds an Opus-high explainer.
- `basic-why` finds why code or infra is the way it is, from git history, GitHub PRs and issues, ADRs, phase docs, CHANGELOG, `CLAUDE.md`/`AGENTS.md`, and memory only. The main agent builds the anchor and sweeps the in-repo docs and memory, a Sonnet digger works git and `gh` (`references/investigator-prompt.md`, with a defensive-code section), and the answer follows a five-tier confidence framework (`references/epistemics.md`) with exact gaps and one Sources consulted line per source. `lite` is inline, and `deep` moves synthesis to an Opus-high agent in a fresh context. Before a change it ends with a Preserve / Change / Avoid / Risk set and offers `/basic-impact` or `/basic-architect`.
- `basic-teach` runs `basic-how` and/or `basic-why` by reading their files in place, then teaches the result in plain spoken English: takeaways picked from why the user asks, the smallest complete answer first, layers on request, and no quizzes or framing labels. Diagrams build up one part at a time, in ASCII, or as a frame series on an Artifact page for three or more parts. It keeps `basic-why`'s confidence language as found.
- `advanced-review` is the deep version of `basic-review`: the same scopes plus `branch [<base>]`, the same 1–3 scale, and report-only. The main agent writes a brief without the chat (intent, changed names, and up to 3 old decisions the diff deletes or loosens). Two or three Sonnet lens reviewers (correctness, security and data, and ripple when shared names change, from `references/lens-prompt.md`) launch in one message with `basic-how` explorers and narrow `basic-why` diggers. It runs the repo's tests and validators under `basic-impact`'s read-only running rules, verifies every candidate with `basic-review` pass E, and reports findings with a Proof column, details, history at risk, ripple, checks run, and leads not confirmed. It reuses the sibling skills by reading their files in place. `lite` uses no subagents.
- `advanced-summary` is the deep version of `basic-summary`, with the same inputs and scopes. It reads `basic-summary` §1 and §2 in place, then writes a plain technical prose report with these sections: overview, what changed, how it works now, why, trade-offs and rejected options, verification, and risks. `session` adds Decided, Parked, and Open. A Sonnet decision reader (`references/decision-reader-prompt.md`) reads the `basic-reflect` digest of long or compacted chats, and `basic-how` and narrow `basic-why` run where they apply. A Sonnet claim checker (`references/claim-check-prompt.md`) tests each claim against git and the transcript before the report prints. Verification reports only what ran in the session. On request it saves Markdown, or PDF through `scripts/md-to-pdf.sh`, to `docs/summary/`. `lite` uses no subagents.
- `CLAUDE.md` naming rule: `basic-` is for ports and quick skills, and `advanced-` marks the deep partner of a `basic-` skill, with the same inputs.
- `basic-unslop` cuts AI writing tells from prose and fixes them in place by default, or reports with `scan`. Targets: `diff` (changed lines only, the default), `docs`, `readme`, `changelog` (the Unreleased section only, `changelog all` to widen), `repo`, or paths. It skips code, quotes, license text, `archive/`, and its own folder, and updates anchor links when it changes a heading. The 28 rules have short names in `references/rules.md`. `repo` and `docs` runs over 15 files batch to Sonnet agents.

### Changed
- `bump-version` §8 hands doc sync to `update-docs diff`, with the old inline rule as a fallback. `basic-review` pass D also notes changed names that docs still mention, and the coverage line ends with `Docs mention changed names: <names>. Run /update-docs.` `delegate` uses the main Grok model on every route and skips `-build-fast`.
- `bump-version` takes `sonnet`, which replaces `bump-version-sonnet`. Its body moved to `bump-version/references/sonnet.md`, and it replaces §7 when `sonnet` is given.
- `basic-summary` adds `jira` (a linear ticket record: Background, What we did in order, Why, Result, Next steps, and References) and `management` (a 20-second update: What we did, Why it matters, Status, and Needs from you). Both take `work`'s scopes, write "Reason not recorded" instead of guessing, and pick up ticket keys such as `ABC-123` from the branch name and commits. Both print one fenced block that follows the new `references/jira-markdown.md`: bold labels instead of `#` headings, flat lists, no tables, inner fences, or rules, and no characters that Jira wiki markup reads as formatting.
- `advanced-summary` adds `jira`, the basic sections plus How it works now and Risks, at about 600 words. It has no `management` input. The `CLAUDE.md` naming rule now says "the same core inputs".
- `basic-review` points to `/advanced-review` in its intro. Pass D also notes each deleted or loosened guard, retry, timeout, threshold, limit, test, health check, permission check, or `ignore_changes`, without digging into why, and the coverage line ends with `Undoes old decisions: <names>. Run /advanced-review.`
- `basic-summary` takes an input: `last` (the default, unchanged behavior), `session` (this chat so far as Decided, Built, Parked, and Open, checked against `git status`), or `work` (the old `summarise-work`: Achieved, Fixed, and Implemented from git and the chat, with `since <ref>`, `last <n>`, or `<sha>` scopes). Every input uses one bullet shape and STE. `plain` swaps the bullets for a short spoken retelling with no jargon, hashes, or paths, after the pstack `bro` skill. Natural-language triggers pick the input their words name.
- `basic-summary` adds `commit` (a message in the repo's subject style from the staged diff or the working tree, or one message per commit when the work should split, with the `git` order printed for the user) and `pr [<base>]` (Summary, Changes, Testing, and Notes for review, or the repo's PR template). Both print text only.
- `basic-summary`, `basic-alignment`, and `AGENTS-TEMPLATE.md` section 2 add clear-reading checks from the pstack `technical-writing` skill: one referent per pronoun, "only" and "not" next to their word, no slashes, semicolons, or em dashes, no long noun strings, real names in code font, specific over vague, and a rule to fix a sentence another way when a rule makes it worse.

### Removed
- `check-diff-public-ready`, `check-repo-public-ready`, `aws-cost-mtd`, `aws-cost-optimize`, `aws-s3-audit`, and `bump-version-sonnet` are merged into the skills above, and their links are removed from every profile. `imp-sonnet` and `imp-grok-4-7` moved to `archive/skills/`.
- `summarise-work` moved to `archive/skills/`. Use `/basic-summary work`. Its links are removed from every profile.

## [1.2.0] - 2026-11-07

### Added
- `basic-architect` designs a new feature, service, or component before code, for software, infra, or both. Haiku Explore agents ground it in the real system. Two Sonnet runners sketch structurally different shapes from forced premises (extend the current structure, or reshape it as if the requirement had been there from day one). The main agent screens both against software and infra red flags (`references/red-flags.md`), merges them, and writes a `proposed` ADR in the repo's `docs/adr/` format, then stops for sign-off and offers `/phase shape` with a design contract for the slices. `lite` uses no subagents, and `deep` adds one Opus-high runner. Sketch checks are read-only (`tsc --noEmit`, `terraform validate`, `docker compose config`), and it never applies infrastructure.
- `basic-alignment` plays back an ask before any work starts: goal, problem, scope in and out, constraints heard, what done looks like, meaning-changing readings of unclear or dictated words, and numbered yes/no assumptions, in Simplified Technical English. It is report-only and makes no tool calls. `basic-architect` opens its grounding brief and its sign-off with the same block.
- `basic-reflect` mines the current session, or `last <n>` sessions in the same project, for durable lessons. A bundled `digest.sh` (`jq`, read-only) shrinks a transcript to its user messages, commands, skill and agent calls, errors, and clipped replies, with `-b` for a brief multi-session digest. Two Sonnet reviewers ("what to encode", "what we missed") feed a main-agent filter for durability, decision change, and "already covered". Each lesson routes to an ai-engineering skill, the repo's `AGENTS.md`/`CLAUDE.md`, `AGENTS-TEMPLATE.md`, or memory, and only the numbered rows the user approves are applied. Hooks, settings, scripts, and lessons about skills the user does not own stay suggestions.
- `basic-impact` finds what a change could break outside its diff, for software, infra, or both. It sweeps every repo in `~/git` with `rg`, works through a "where grep stops" checklist (`references/where-grep-stops.md`), and proves the one fact the change is safe because of on a 5-level ladder with read-only scripts and commands. Anything with side effects is printed as a `!` command for the user, and the repo's `AGENTS.md` overrides the allowed list. `deep` adds a Sonnet second opinion that runs without the main agent's conclusions.
- `scripts/check-readme.sh` fails when the skills badge disagrees with the `skills/` folders, a skill has no README row or two, a row links a missing skill, or a `SKILL.md` `name` does not match its folder. `--staged` checks the index, and `.githooks/pre-commit` runs it that way (enable with `git config core.hooksPath .githooks`).
- `scripts/install-skill.sh <name>... [--remove]` links skills into every `~/.claude*` profile. It skips a profile that holds a real directory, and `--remove` deletes only links that point into this repo.
- `THIRD_PARTY_NOTICES.md` records the MIT license of pstack, which `basic-architect`, `basic-alignment`, `basic-reflect`, and `basic-impact` adapt.

### Changed
- `basic-review` ripple pass also checks infra names (compose networks, volumes, and containers, hostnames, buckets, Terraform addresses and outputs, IAM ARNs, secret names, cron paths, and image tags) in the current repo. A ripple it cannot settle in one pass ends the coverage line with `Unverified ripple: <names>. Run /basic-impact.`
- `phase` splits `advance` into `advance slice` (the default for a bare `advance`, never closes a phase) and `advance phase` (closes the phase when its DoD is met). Suggestions always name the full form. The README cheatsheet and `AGENTS-TEMPLATE.md` follow.
- `AGENTS-TEMPLATE.md` Core Rules: questions are asked as a numbered list, each answerable in a few words.
- `CLAUDE.md`: adding or removing a skill also runs `check-readme.sh` and `install-skill.sh`. A new "Porting an upstream skill" section covers summarizing first, asking before building, `basic-<name>` naming, credit, the notices file, and never editing the upstream clone.

### Fixed
- README Repo workflow table: the `imp-sonnet` row sat below the archived-skills note, so it rendered outside the table.

## [1.1.0] - 2026-11-07

### Added
- `check-ai-ui-tells`, a report-only scan of a web UI for 26 typical AI/template design tells. They cover colour and effects, typography, layout, motion, and copy. It reads the code with greps, and the rendered page with a read-only Playwright `probe.js`. The report is a fixed-order table with evidence for each tell, then a cluster score, the loudest tells with fixes, counterweights, and coverage. The catalogue is in `tells.md`.

## [1.0.2] - 2026-10-16

### Changed
- `bump-version` works in any repo, not only this one and the `web/` app it was copied from. It reads the repo's `AGENTS.md`, `CLAUDE.md`, and CHANGELOG header first; their SemVer table, changelog format, and git policy override the defaults. It defers to a repo-local release skill (but not to a copy of itself), a `scripts/bump-version.sh`, or CI release tooling (semantic-release, release-please, changesets). It finds every version mirror (`package.json`, `Cargo.toml` workspaces, `pyproject.toml`, `VERSION`, `tauri.conf.json`, source constants, and lockfile self-entries) and leaves independent sub-packages and `0.0.0` placeholders alone. Tag-only repos get a changelog and a tag command, with no manifest edit. When the tag and the files disagree, it asks.
- `bump-version` pre-flight runs the repo's documented check, or `tsc`, `cargo check`, or `go build` by ecosystem, and skips with a note when none applies. Text under `## [Unreleased]` moves into the new block. The changelog heading and section style match the existing file. Pre-1.0 and pre-release bumps have explicit rules. The stale-version grep searches for the old version across tracked files. The report prints commit and tag commands in the repo's own style. It still makes no git writes.
- `bump-version-sonnet` follows the generic `bump-version`: the main agent finds the mirrors and hands the subagent an explicit file list. The idempotency check runs after the mirrors are found, so it no longer reads `package.json` in a Cargo-only or tag-only repo. Verification reuses the `bump-version` old-version sweep rather than keeping its own copy. Pre-flight is no longer TypeScript-only.
- `basic-review` searches in five passes: intent, a mechanical sweep of added lines (conflict markers, debug leftovers, focused tests, and credential patterns that ignore case and accept unquoted `.env` values), a hunk read against per-type checklists, a ripple check on changed symbols, env vars, config keys, and columns, and a verify step that drops any candidate without a failure path.
- `basic-review` report: a `Fix` column on each row, and a verdict that gives the call (`Fix before commit` / `OK to commit; fix soon` / `OK to commit` / `No findings`) and then the counts by severity. The coverage line says when staged and unstaged changes are mixed, and how many changed symbols had their callers checked. `/basic-review staged` reviews only the index. Repos with no commits, root commits, binary files, and oversized untracked files are handled. Removed code cites the nearest surviving line.

## [1.0.1] - 2026-10-13

### Added
- `basic-review` `Maintain` type — a fourth finding for code that works on today's paths when the next edit is easy to get wrong. The row has to name that edit. Severity 2 only when the diff already edits that logic in more than one place, or the area is in flux; otherwise severity 1. Never severity 3. A path that is already wrong stays a Bug, and extra code that can be removed stays Bloat.

### Changed
- `basic-review` report is a verdict line, then a severity 1–3 table of at most 8 rows, then a coverage line. The verdict is one of four closed sentences, so the pass no longer ends with a free-form "safe to commit". Each summary is one sentence in a fixed shape, and a line number is cited only after that file has been opened.
- `basic-review` reads untracked text files, turns diff color off, and limits the diff when the user names paths. A clean tree reviews the last commit: the first parent when `HEAD` is a merge, and a stop when there is no parent. Callers are checked when a signature changes. Lockfiles, vendored trees, minified bundles, and generated dumps are skipped unless they add a credential, a script hook, or a huge dump.
- `basic-review` security is exploitable behavior in the diff, plus a real credential. PII, internal URLs, and publish-hygiene stay with `check-diff-public-ready`. A finding without a concrete path is dropped. Branch and pull-request reviews are pointed at the review skill. `/basic-review` is unchanged.
- README skills table: `basic-review` describes the verdict plus a severity 1–3 table, including maintainability.

### Removed
- `basic-review` severity 0. Formatting and lint rules are not findings.

## [1.0.0] - 2026-10-03

### Added
- `imp-grok-4-7` skill — the main agent plans the discussed changes, a headless `grok-4.7` process implements them, then the main agent reviews, scores the result out of 5, fixes, and summarizes. Owns the generic "have grok implement this" trigger. An optional leading level (`/imp-grok-4-7 high`, `--effort high`, or `effort: high`; also `none`, `minimal`, `low`, `medium`, `xhigh`, `max`) is passed only to that process via `--effort`. When the invocation names no level, the implementer runs at `medium`. This session's effort is left unchanged: a native subagent inherits it and has no effort argument, so the implementer is always the headless CLI.

### Removed
- `imp-grok-4-5` and `imp-grok-4-6` from the live skill set. Moved to `archive/skills` with `user-invocable: false` and `disable-model-invocation: true`. `/imp-grok-4-5`, `/imp-grok-4-6`, "have grok 4.5 implement this", and "have grok 4.6 implement this" no longer run. Breaking for those invoke names, which is why this is 1.0.0.

### Changed
- README: skills badge 18 → 17, the Repo workflow table lists `imp-grok-4-7` and points at the archive for 4.5 and 4.6.

## [0.11.0] - 2026-09-30

### Added
- `docs/opencode-console-models.md` — one dated chart of current models on OpenCode Console (API-charged Zen credits): list price (in/out/cached read), context, Go proxy availability + per-model monthly cap, benchmarks (Bito / DeepSWE / AA Index), cost reality, and best use in v2, plus a what-to-actually-run ladder. Replaces the two old Zen sheets.

### Changed
- README section retitled "OpenCode Console models" and now links the single chart instead of the two-sheet table.

### Removed
- `docs/opencode-zen-models.md` and `docs/opencode-zen-frontier.md` — superseded by `docs/opencode-console-models.md`.

## [0.10.0] - 2026-08-27

### Added
- `summarise-work` skill — report-only wrap-up of the current sitting: git + this chat classified into Achieved / Fixed / Implemented (omit empty categories; one item, one bucket), each a one-sentence bullet plus one-sentence sub-bullet, then a short executive summary of how the work solves the original problem. Does not write BOARD.md, commit, or keep implementing. Complementary to `/phase sync` (ticks the board) and `/bump-version` (writes the changelog).
- `docs/opencode-zen-models.md` — dated cheat sheet of current open-weight models on OpenCode Zen and Go (picks, prices, what to actually run). Linked from the README.
- `docs/opencode-zen-frontier.md` — matching dated cheat sheet for closed / frontier models (Grok 4.6 daily, Opus 5 quality, Fable 5 ceiling, GPT 5.6 Sol / Luna). Cross-linked from the open-weight sheet and the README.

### Changed
- Both Zen cheat sheets re-checked against the live `/zen/v1/models` and `/zen/go/v1/models` catalogs on 2026-08-26. Corrections: MiniMax M3 is 512K context on Zen (not 1M); DeepSeek peak hours are weekday-only; Qwen 3.7 Max/Plus are on Go, not live Zen PAYG; Sonnet 5 comparison price is $2/$10; added live-only free IDs (`deepseek-v4-flash-free`, `laguna-s-2.1-free`); Go usage numbers taken from the official estimate table.
- README: skills badge 17 → 18, and `summarise-work` added to the Repo workflow table.

## [0.9.0] - 2026-08-24

### Added
- `imp-grok-4-6` skill — same plan/delegate/review/score/fix split as `imp-grok-4-5`, with Grok 4.6 as the implementer. Takes the generic "have grok implement this" trigger (4.6 is now the default Grok model). Inside Grok it spawns a native `general-purpose` subagent with `model: grok-4.6`; from Claude Code or OpenCode it shells out to the headless `grok` CLI. The implementer prompt forbids re-loading `imp-grok-*` or nesting another `grok` process.
- `phase` skill — one slash command with modes (`status` default, `init`, `sync`, `shape`, `advance`, `prune`, `help`). Working files: `docs/plans/BOARD.md` (phase table + close log) and `docs/plans/NOW.md` (current slice). Checkboxes, appetite (stop conditions, not calendar), and DoD stay in `docs/phases/`. Init gitignores those two trees unless they are already tracked, and migrates leftover `SESSION.md` / `STATUS.md`.
- `README.md`: a `/phase` cheatsheet under the Phase board section — a mode-by-mode command table, a worked example of one phase from `init` through `shape` / `sync` / two `advance` calls, the three day-to-day invocations, and the gotchas that are easy to get wrong from the skill doc alone (NOW is not the plan, BOARD wins a conflict, `sync` never closes a phase, both trees are gitignored, old `/session-*` aliases still route). The skill file is written for the agent executing it; the README needed the version a person reads before typing.

### Changed
- `imp-grok-4-5`: implement phase is now host-aware. Inside Grok it uses `spawn_subagent` (`model: grok-4.5`) instead of nesting a `grok` CLI process. Claude Code and OpenCode still use the headless CLI. Generic "have grok implement this" moved to `imp-grok-4-6` so the two skills no longer collide; 4.5 keeps `/imp-grok-4-5` and "have grok 4.5 implement this".
- Replaced the sitting handshake (`SESSION.md` / `/session-*`, and the earlier `/status-*`) with `/phase`. Breaking for invoke names. Same `~/.claude/skills/<name>` symlink install. No sittings log.
- `docs/AGENTS-TEMPLATE.md`: Core Rules "Session handshake" replaced with "Phase board".

### Removed
- `session-handshake`, `session-init`, `session-start`, `session-check`, `session-snap`, `session-end`, `session-prune`, `session-help`.
- `session-status`, `status-init`, `status-check`, `status-snap`, `status-end`.

None of the removed skills appeared in a tagged release — they were added and
replaced between 0.8.1 and 0.9.0 — so this is a minor, not a major. Anyone who
installed from `main` during that window should re-point their symlinks at
`skills/phase`.

## [0.8.1] - 2026-08-07

### Changed
- `imp-grok-4-5`: phase 2 standing instructions now tell Grok to look for an existing helper before writing a new one — name likely directories, grep them first, and report which helpers were reused. A cold agent otherwise reimplements a hardened sibling (e.g. a full-file read next to a bounded tail-read) that already exists a module away.
- `imp-grok-4-5`: the headless invocation must be run exactly as written — appending `; echo "exit: $?"` or any other chain turns the call into a multi-segment command that Claude Code's classifier can block before it reaches a shell. The worktree check is the real evidence of success.
- `imp-grok-4-5`: the "Blocked by classifier" footgun now opens with "did you change the command?" as the first check, notes that a skill working all day is evidence *for* a local deviation not against it, and points at a Bash permission rule for `grok` in `.claude/settings.json` as the durable fix.

## [0.8.0] - 2026-08-07

### Added
- `bump-version-sonnet` skill — the same release as `bump-version` split in two: the main agent decides the bump type, derives the release from the diff, and writes the finished `CHANGELOG.md` prose, a Sonnet subagent transcribes it into `package.json` / `README.md` / `CHANGELOG.md` and any stale docs, then the main agent verifies. The judgement cannot be delegated because deriving the release depends on the conversation, and a cold subagent seeing only `git diff` writes worse release notes than the agent that did the work. Three rules carry the split: **the subagent writes no prose** — every word is the main agent's, verbatim, which is what keeps release notes accurate despite delegating and turns verification into a string match rather than a re-read; pre-flight and the idempotency check stay with the main agent, and a failing pre-flight aborts **before** delegation so a subagent is never the thing that decides a failing typecheck is acceptable; and the skill is a thin layer over `bump-version` rather than a fork, so the SemVer table and derivation steps keep one home. Deliberately carries no `imp-*` scorecard — that rubric measures open-ended implementation, and this work is transcription.
- `imp-grok-4-5`, `imp-sonnet`: a standing-instructions block in phase 2 listing what every delegation prompt must carry. **Discover the toolchain; do not assume it** — an interpreter or test runner written into the acceptance criteria is a guess until verified (a plan can say `python -m pytest` where the repo only has `venv/bin/python`), so the cold agent finds the real one and reports the command it settled on. **An async call started before unmount keeps running** — unmounting does not cancel work already in flight, so any plan involving aborting, retrying, or resuming on remount must state explicitly whether the original in-flight call is cancelled or allowed to complete; left unstated the cold agent guesses, and the guess is where the defects land. **Give every style constraint a command that checks it** — a constraint stated as an adjective ("wrap at roughly 100 columns") is not something a cold agent can confirm, and it drifts, so the check ships next to the constraint.
- `docs/AGENTS-TEMPLATE.md`: an authoring rule that machine-specific values — absolute paths, hostnames, usernames — stay as `<placeholders>` in the template and are filled in only in the copy.

### Changed
- `docs/AGENTS-TEMPLATE.md`: the Caddy example path is now `<path to Caddyfile>` instead of a real absolute path, and the port section heading reads "standardized across all repos" rather than naming a personal `~/git` directory. That heading is copied verbatim into every generated `AGENTS.md`, so it propagated one machine's filesystem layout into every repo built from the template.
- `imp-grok-4-5`: the percent-encoding worked example is now `/home/you/git/my-project` → `%2Fhome%2Fyou%2Fgit%2Fmy-project`, which teaches the encoding identically without shipping a real username and private project name from a public repo.
- README: the install snippets use `"$PWD/skills/<name>"` run from the repo root instead of a hardcoded clone path, so they work wherever the repo is cloned rather than assuming one layout.
- README: skills badge 14 → 15, and `bump-version-sonnet` added to the Repo workflow table.

## [0.7.2] - 2026-08-07

### Added
- `imp-grok-4-5`, `imp-sonnet`: a scoring phase (3b) that grades the delegated implementation 1–5 across six dimensions — Fidelity, Bloat, Correctness, Security, Maintainability, Verification — each with written 1/3/5 behavioural anchors, because an unanchored "rate out of 5" returns a 4 every run and cannot be compared across runs. Scores grade **the execution of the plan only, never the plan itself**: a clean build of a mediocre plan scores high, which isolates the one variable being measured. Rules that keep the number meaningful: every score below 5 cites a `file:line` or command output (the model's own report is a claim, not evidence), Security is `N/A` when the diff touches no input/secrets/paths/subprocess, 5 means nothing to change, and the headline is the **lowest** dimension rather than the mean so an elegant implementation of the wrong thing cannot average its way to a 4. The rubric is deliberately identical in both skills so runs stay comparable across models.
- `imp-grok-4-5`, `imp-sonnet`: an optional `<repo-root>/.imp-scorecard.log` — one line per run (date, model, task, six scores, failure note) appended only if the file already exists, never created unprompted. The model field is what makes Grok and Sonnet runs comparable in one file.
- `imp-grok-4-5`, `imp-sonnet`: a trailing "Note on the skill" in the summary for the one-line "this would have gone better if the skill had X" observation. Capped at two bullets with zero as an explicitly normal outcome, restricted to repeatable skill-level fixes rather than one-off model mistakes, and barred from editing the skill or opening follow-up work — it is a comment for the user to act on separately.

### Changed
- `imp-grok-4-5`, `imp-sonnet`: phase 3 split into Review (3) → Score (3b) → Fix (3c). Review now dumps the diff and status to `<scratchpad>/{grok,sonnet}-raw.{diff,status}` and ends with "do not fix anything yet", because the previous single phase fixed problems before any grading and would have scored the repaired code rather than the handover. Fixes explicitly do not revise the scorecard.
- README: the `imp-grok-4-5` and `imp-sonnet` rows now mention scoring the result out of 5.
- `imp-sonnet`: corrected the stale "four phases" line in the intro.

## [0.7.1] - 2026-08-06

### Changed
- `imp-grok-4-5`: the delegation command now runs Grok under `--always-approve` with explicit `--deny` rules (`git commit/push/add/tag/reset/checkout/stash`, `rm -rf`) instead of `--permission-mode acceptEdits`. In headless mode a permission prompt has nobody to answer it — it resolves as `cancelled`, ends the turn, and the process still exits 0, so `acceptEdits` silently killed runs on the first `search_replace`. Deny rules beat always-approve and are checked against every segment of a chained command, so "don't commit" becomes enforced rather than a request in the prompt.
- `imp-grok-4-5`: the run is now capped with `--max-turns 300` and redirected to `<scratchpad>/grok-run.log` (read back with `tail`) rather than piped, so evidence survives a bad run.
- `imp-grok-4-5`: added a mandatory post-run check that `git status --short` / `git diff --stat` is non-empty before reading Grok's report — exit 0 and confident stdout narration are not evidence that anything was written.

### Added
- `imp-grok-4-5`: a "Troubleshooting a run that did nothing" section — how to locate and parse the session trace at `~/.grok/sessions/<url-encoded-cwd>/<session-id>/events.jsonl`, a table mapping trace outcomes (permission `cancelled`, max-turns exhausted, no edit-tool call, no tool call at all) to causes and fixes, and two footguns: a leading `~/` in a Grok permission rule is literal glob text (so `Edit(~/git/**)` matches nothing, which is why a `/tmp` smoke test can pass while a run under `~/git` fails), and a `Blocked by classifier` denial comes from Claude Code's own permission layer — report it and offer the `! grok …` escape hatch rather than working around it. Caps escalation at two attempts before reporting.

## [0.7.0] - 2026-08-06

### Added
- `imp-grok-4-5` skill — same plan/delegate/review/summarize split as `imp-sonnet`, but the implementation phase runs Grok 4.5 instead of a Claude subagent. Because the `Agent` tool can only spawn Claude models, delegation shells out to the `grok` CLI in headless mode (`grok --prompt-file … --model grok-4.5 --permission-mode acceptEdits --cwd <repo>`) via `Bash`. The plan goes through `--prompt-file` rather than an inline argument so long prompts survive shell quoting, and the prompt must be self-contained since Grok starts with no access to the conversation. Adds a `command -v grok` preflight that aborts rather than silently falling back to a Claude implementation, pins the Bash timeout to 600 s for the agent loop, and instructs Grok not to run git write commands — with the review phase checking `git log` in case it does anyway. Verified end to end against `grok 0.2.118`: file edits, shell commands, and test runs all work headless under `acceptEdits`, which is used deliberately because `bypassPermissions` is blocked by Claude Code's auto-mode classifier and stricter modes stall with no way to prompt.

### Changed
- README: skills badge 13 → 14, and `imp-grok-4-5` added to the Repo workflow table.

## [0.6.0] - 2026-08-04

### Added
- `aws-cost-mtd` skill — read-only month-to-date spend report for a single AWS account via Cost Explorer: breakdown by service (and region on demand), delta against the same days of the previous month, daily trend to catch step changes, and a month-end forecast. Picks `UnblendedCost` vs `AmortizedCost` deliberately by first checking whether Savings Plans or RIs exist, and filters credits/refunds out of service attribution. Opens with a **blocking cost gate**: the free identity calls run first so the account can be named, then it states the request count and dollar total ($0.01 per Cost Explorer request) and waits for approval before any billable call.
- `aws-cost-optimize` skill — read-only savings sweep for a single account, ranked by estimated monthly saving with effort and risk columns. Combines AWS's own recommenders (Cost Optimization Hub, Compute Optimizer, Cost Explorer rightsizing, Trusted Advisor) with direct sweeps that need no enrolment: unattached EBS volumes, gp2→gp3 candidates, unassociated Elastic IPs, long-stopped instances, idle NAT gateways and load balancers (verified against 14 days of CloudWatch), stale snapshots, idle RDS, and log groups with no retention. Also reports Savings Plans/RI coverage and utilisation as opposite failure modes. Gates only the Cost Explorer portion (~$0.06) and degrades gracefully if declined or if the account is not enrolled in the optional recommenders.
- `aws-s3-audit` skill — per-bucket audit of one account producing two tables: security by 0–3 severity (public access block, policy/ACL exposure, encryption, TLS-only enforcement, object ownership, versioning, logging, KMS bucket keys) and cost by estimated monthly saving (missing multipart-abort rules, noncurrent-version bloat, absent lifecycle transitions, storage-class fit). Measures bucket size from free CloudWatch storage metrics rather than recursive `s3 ls`, which is billed per request and can run for hours on a large bucket.

### Changed
- README: skills badge 10 → 13, and the single flat Skills table split into five category tables (Review & audit, AWS, Fix & apply, Product & design, Repo workflow) so related skills group together as the list grows.

## [0.5.0] - 2026-08-04

### Added
- `check-npm-supply-chain` skill — report-only audit for npm supply-chain compromise indicators of the Shai-Hulud-worm class: enumerates `preinstall`/`postinstall`/`prepare` hooks in the project and across `node_modules`, sweeps known IOCs (dropper filenames, exfil workflows, worm-created branches/repos), greps dependencies for credential-stealer patterns (npm/GitHub/AWS/Kubernetes/Vault secret stores), checks lockfile integrity, and reports hardening gaps (`ignore-scripts`, frozen lockfiles, token hygiene) in the standard 0–3 severity table.
- `check-diff-public-ready` skill — report-only pass on the working diff (or last commit if clean) for material unsafe on a public repo: secrets/credentials, PII, internal infra, accidental dumps, dangerous committed config; severity table; no fixes applied.
- `check-repo-public-ready` skill — same public-exposure checklist for the whole tree, plus high-risk path inventory, `.gitignore`/LICENSE hygiene, and an optional bounded history pass; report-only.

### Changed
- README: skills badge 7 → 10 and Skills table rows for the three new skills.

## [0.4.0] - 2026-07-18

### Added
- `review-dax-insights` skill — reviews a product, feature, or launch plan against Dax Raad's three product principles (shareable "cool" marketing, one singular Aha moment reached in <60 s, primitives-first retention); reports a ✅/⚠️/❌/❓ table with the highest-leverage action per gap. Assess-only, no changes applied. Source doc kept verbatim as `dax-insights.md` alongside the skill.
- `review-website-design` skill — reviews a website or design against the premium-website psychology framework (Halo Effect first impression, cognitive fluency, Peak-End micro-interactions, 2026 trends layer, client delivery & ownership); same status-table report format, assess-only. Full framework with the trends table kept as `premium-website-framework.md`.
- `fix-react-doctor` skill — runs `npx react-doctor@latest` and iteratively fixes reported React anti-patterns until the score reaches 100, with guardrails: behavior-preserving edits only, build/typecheck verification each iteration, no rule suppression to chase the score, and early-stop when the score plateaus. Leaves changes uncommitted for review.

### Changed
- README: skills badge 4 → 7 and Skills table rows for the three new skills.

## [0.3.0] - 2026-07-17

### Added
- `fix-input-overflow` skill — assesses whether the current app's native `date`/`month`/`time`/`datetime-local` inputs suffer the iOS Safari intrinsic-width overflow (greps for usage, checks for an existing reset), applies the global CSS `appearance: none` + `min-width: 0` + `::-webkit-date-and-time-value` fix to the root stylesheet if so, then verifies with the project build.

## [0.2.0] - 2026-07-17

### Added
- `imp-sonnet` skill — main agent plans the discussed changes, delegates implementation to a Sonnet subagent, then reviews, fixes, and summarizes; keeps heavy implementation off the main model while retaining oversight.
- `basic-review` skill — single-pass sanity check of the working diff for bugs, security issues, and over-engineering, reported as a severity (0–3) table; report-only, no fixes applied.
- `docs/CLAUDE-PROFILES.md` — how to set up multiple Claude Code profiles via `CLAUDE_CONFIG_DIR`, what each profile contains, and gotchas (separate logins, no inheritance between profiles).
- `docs/AGENTS-TEMPLATE.md` — canonical `AGENTS.md` template derived from the common structure of the `~/git` repos (Core Rules → Permitted/Prohibited → Infrastructure → Conventions → Versioning → standardized 38080 test-port footer), with placeholders and authoring notes.
- README: Skills table linking each skill to its `SKILL.md` with a brief description.
- README: shields.io badges (version, skills count, Claude Code) replacing the plain version line.

### Changed
- README: new "Installing (symlinks)" section — this repo is the source of truth and `~/.claude` symlinks into it — plus a "Multiple profiles" subsection covering direct (non-chained) linking into every profile's config directory.
- CLAUDE.md: maintenance notes to update the skills badge and Skills table when skills change, and that the bump-version TypeScript pre-flight doesn't apply here.

## [0.1.0] - 2026-07-17

### Added
- Initial repo layout: `skills/`, `agents/`, `commands/`, `hooks/`, plus `README.md` and `CLAUDE.md` documenting the conventions.
- `bump-version` skill — bumps the version, syncs it into `README.md`, and writes a CHANGELOG entry derived from the git diff.
- Repo-level versioning: minimal `package.json`, this changelog, and git tags per release.
