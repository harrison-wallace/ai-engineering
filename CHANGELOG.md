# Changelog

All notable changes to this repo are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html):
**patch** = tweaks to an existing skill/agent/command, **minor** = new asset added,
**major** = an asset renamed, removed, or changed in a way that breaks how it's invoked.

## [Unreleased]

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
- `imp-grok-4-5`: the delegation command now runs Grok under `--always-approve` with explicit `--deny` rules (`git commit/push/add/tag/reset/checkout/stash`, `rm -rf`) instead of `--permission-mode acceptEdits`. In headless mode a permission prompt has nobody to answer it — it resolves as `cancelled`, ends the turn, and the process still exits 0, so `acceptEdits` silently killed runs on the first `search_replace`. Deny rules beat always-approve and are checked against every segment of a chained command, so "don't commit" becomes enforced rather than a request in the prompt file.
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
