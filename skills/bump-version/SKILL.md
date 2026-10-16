---
name: bump-version
description: Cut a release in any repo — detect where the version lives (package.json, Cargo.toml, pyproject.toml, VERSION, tags only, or a mix), bump it everywhere it is mirrored, and write a CHANGELOG entry derived from the diff in the repo's own format. Defers to a repo-local release skill or script. Triggers on "bump version", "update changelog", "release", or "bump patch/minor/major".
---

# bump-version

Cut a release in whatever repo you are in: bump the version in every file that mirrors it, add a
`CHANGELOG.md` entry, and sync stale docs — all derived from the diff. The repo's own rules win
over anything here; this skill fills the gaps.

## Usage

```
/bump-version                 # infer the increment from the diff
/bump-version patch|minor|major
/bump-version prerelease      # 1.2.0-beta.1 → 1.2.0-beta.2
/bump-version 2.0.0           # explicit version
```

**Never ask the user for a summary.** Derive everything from the diff. Ask only when a step below
says to.

## 1. Orient

```bash
git rev-parse --show-toplevel        # work from the repo root
git status --short
git tag --sort=-creatordate | head -5
```

Not a git repo → say so in one line and stop.

Read the repo's rules before deciding anything: `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, and
the header of `CHANGELOG.md`. Look for a SemVer table, a changelog format, a release flow, a
pre-flight command, and a git policy. **Every rule found there overrides the defaults below.**
A rule like "do not bump a version on your own" is satisfied by the user invoking this skill; a
rule that routes releases through a specific tool or skill is not — follow §2.

## 2. Defer to the repo's own release flow

Check in this order. The first hit wins.

| Found | Do |
|---|---|
| A repo-local skill: `.claude/skills/*/SKILL.md` named `release`, `bump*`, or `*version*` — except a copy of `bump-version` or `bump-version-sonnet` itself | Stop and tell the user to run that skill (`/release` etc.). It knows things this one doesn't, and may carry git authorisation this one never has. |
| `scripts/bump-version.sh` (or `scripts/release*.sh` documented as the bump flow) | Read it first. Run it with the bump type and a one-line summary you wrote. Then expand the stub it leaves (§7) and do §8–§10. Skip any step the script already did. |
| CI-driven release tooling: `.releaserc*` / `release.config.*` (semantic-release), `release-please-config.json`, `.changeset/` | Do not bump by hand — CI owns the version. For changesets, offer to write a `.changeset/*.md` instead. Otherwise explain and stop. |
| None | Continue. |

`cliff.toml` (git-cliff) only generates changelog text. It does not own the version, so it is not a stop — but match the changelog format it produces.

## 3. Find the version

**Locate every candidate.** Tracked files only:

```bash
git ls-files | grep -E '(^|/)(package\.json|Cargo\.toml|pyproject\.toml|setup\.(py|cfg)|VERSION|version\.txt|tauri\.conf\.json|Chart\.yaml|pubspec\.yaml|composer\.json|manifest\.json|.*\.csproj)$' | grep -v -e node_modules -e vendor/
```

Read the version field in each. Also note these:

- The latest release heading in `CHANGELOG.md`.
- The latest SemVer tag (`git describe --tags --abbrev=0`). Note its prefix, `v` or none.
- Source constants: `__version__` in `__init__.py`, `version.ts` / `version.go` exports.

**Pick the release version.** It is the version the changelog and tags agree on. Then classify each
file:

- **Mirror** — it carries the same version as the release and describes this project. Examples:
  root `package.json`, `src-tauri/tauri.conf.json`, root `Cargo.toml` `[workspace.package]`, and a
  `web/package.json` that tracks the app. Bump all mirrors together.
- **Independent** — a sub-package with its own number, such as `0.0.0` fuzz crates, a
  `packages/*` library, or a `pyproject.toml` that stays at `0.1.0` while `web/package.json` is at
  `2.40.1`. Leave it alone and list it in the report.
- **Placeholder** — `"version": "0.0.0"` or `"private": true` with a version the release flow
  does not use, as the repo docs say. Leave it alone.

**Tag-only repos.** No manifest carries the version: Go modules, a `0.0.0` placeholder, or a docs
or config repo with only a CHANGELOG. The version lives in the tags and the changelog. Make no
manifest edits. Write the changelog, then print the tag command (§10).

**Disagreement.** Example: `VERSION` says `3.0.20` and the latest tag is `v3.0.21`. Do not guess.
Show the candidates and ask which one is current.

**No version anywhere** (no manifest version, no tags, no changelog). Ask whether to start at
`0.1.0`, and where the version should live.

## 4. Derive the release from the diff (MANDATORY)

Do this before you write any changelog prose.

Find the last release point. Use the first of these that exists:

```bash
git rev-parse -q --verify "refs/tags/${PREFIX}${OLD}"                    # the release tag
git log -1 --format=%H -S"$OLD" -- <primary-version-file> CHANGELOG.md   # the commit that set OLD
```

Collect everything since that point:

```bash
git log --oneline <base>..HEAD
git diff <base> --stat          # base → working tree: committed AND uncommitted release work
git diff <base>
git ls-files --others --exclude-standard
```

Skip generated files and lockfiles when you read. Classify each change as Added, Changed, Fixed,
Removed, or Security, or into the repo's own categories (§7).

**Idempotency.** The new version may already be on disk for this exact work, from an earlier pass.
Then do not bump again. Verify the mirrors, expand any stub, sync the docs, and report.

## 5. Decide the increment

1. An argument was given → use it.
2. Otherwise use the repo's SemVer table (§1).
3. Otherwise use the default:

| Increment | When |
|---|---|
| `PATCH` | Bug and security fixes, performance, copy, docs, dead-code removal, internal refactors |
| `MINOR` | New features, endpoints, commands, pages, or assets; non-breaking additions |
| `MAJOR` | A removed or renamed public interface (CLI flags, API, config keys, file formats, invoke names); a data migration users must run |

Rules:

- **Pre-1.0** (`0.y.z`) — a breaking change bumps MINOR unless the repo says otherwise. Never
  jump to `1.0.0` yourself; ask.
- **Pre-release** (`1.2.0-beta.1`) — `prerelease` increments the last numeric identifier. A plain
  `patch`, `minor`, or `major` on a pre-release asks first: should it graduate to `1.2.0`, or start
  a new pre-release line?
- State the choice and a one-line reason before you edit. Ask only when the evidence is truly split,
  for example a change that could be breaking or not.

Compute the new version by hand: split, increment, and reset the lower parts to 0. Keep the
original string shape. Never add or drop a prefix.

## 6. Pre-flight

Run the repo's documented check first. That is a release checklist in AGENTS.md or CLAUDE.md, a
`typecheck` / `check` / `lint` script in `package.json`, or a `Makefile` target. If none is
documented, use the fast default for each ecosystem present:

| Present | Check |
|---|---|
| `tsconfig.json` (root or app dir) | `npx tsc --noEmit -p <dir>` |
| `Cargo.toml` | `cargo check --workspace --quiet` |
| `go.mod` | `go build ./...` |
| none of the above | skip, and say so |

Failure → **abort the bump.** Print the errors and stop. Run checks from the directory that owns
the config. Do not run full test suites or builds unless the repo's release checklist says to.

## 7. Apply the edits

**Mirrors.** Change only the version value. Use an anchored, first-match edit so a dependency
pinned to the same number is never touched:

- `package.json` / `*.json` — the top-level `"version"`.
- `Cargo.toml` — `version` under `[package]`, or `[workspace.package]` in a workspace. Members with
  `version.workspace = true` follow along.
- `pyproject.toml` — `[project].version` or `[tool.poetry].version`. Skip it when `dynamic =
  ["version"]` is set; then the source is the tag or `__version__`.
- `VERSION` / `version.txt` — the whole file. Keep the trailing newline exactly as it was.
- Source constants that held the old version.

**Lockfiles** that record the project's own version. Update them so the next install leaves no
diff:

- `package-lock.json` — the root `"version"` and `packages[""].version` only.
- `Cargo.lock` — `cargo update --workspace --offline`. If that fails, edit the
  `[[package]]` entries for the workspace's own crates by hand.
- `uv.lock` / `poetry.lock` — the project's own entry only, if it has one.

**README.** Look for a shields badge (`badge/version-X.Y.Z-<color>`) and for `**vX.Y.Z**` lines.
Change only the number.

**Sweep for stragglers.** Search tracked files for the old version:

```bash
git grep -nF "$OLD" -- ':!CHANGELOG*' ':!*.lock' ':!*-lock.json' ':!*lock.yaml'
```

Triage every hit. Is it this project's version (update it), or something that only shares the
number, such as a dependency, a historical note, or an unrelated schema (leave it)?

**CHANGELOG.md.** Match the file as it is. Copy these from the existing entries:

- **Heading shape** — `## [X.Y.Z] - DATE`, `## [X.Y.Z] — DATE`, or `## X.Y.Z (DATE)`.
- **Section names** — Keep a Changelog `### Added` / `Changed` / `Fixed` / `Removed` / `Security`, or the repo's own keywords.
- **Bullet style** and the date format.

Placement:

- The block goes directly under `## [Unreleased]` when that heading exists. Otherwise it goes above
  the newest release.
- If `## [Unreleased]` already has content, **move it into the new block** and merge it with what
  the diff adds. Leave `## [Unreleased]` empty.
- If the release script left a stub (`### Changed` + one line), expand it in place. Do not append
  a second block.
- Use today's date (`date +%Y-%m-%d`). Include only sections that have content.
- Each bullet is concrete: what changed, where, and what effect a user sees. Never write "various
  improvements". Never leave a placeholder.
- If the changelog keeps link references at the bottom (`[1.2.0]: https://…/compare/…`), add one
  for the new version and update `[Unreleased]`.

No `CHANGELOG.md` → create one with a Keep a Changelog header and say so in the report. In a repo
that keeps release notes somewhere else (GitHub Releases only), ask first.

**Two releases in one tree.** One uncommitted tree may hold two separable releases, such as
feature A and then a follow-up fix B. You may write two sequential blocks and set the mirrors to
the tip version. Prefer one block.

## 8. Sync the docs

Use the same diff:

- Update `README.md` and any `docs/` or root `.md` file that the diff has made wrong: a feature
  list, a config table, a usage example, a CLI flag.
- Update counts that come from the tree, such as a "skills: N" or "N endpoints" badge.
- Touch only what the diff makes wrong. Nothing stale → skip this step and say so.

## 9. Verify

- Re-read every mirror. Each one holds the new version.
- `git grep -nF "$OLD"` (with the §7 exclusions) shows only the hits you chose to leave.
- The changelog block sits in the right place, has today's date, matches the heading format, and
  has no empty sections or leftover stub.
- `git diff --stat` holds only the files you meant to change.

## 10. Report

- **Pre-flight**: the command and its result, or why it was skipped.
- **Version**: `OLD → NEW`, the increment, and a one-line reason.
- **Files**: every mirror bumped; every file left independent or as a placeholder.
- **Headline**: one sentence on the release, from the diff.
- **Docs**: which docs were updated, and which were checked and left alone.
- **Next**: the git commands, shaped like this repo's past releases. Copy the commit subject from
  earlier release commits (`git log --format=%s` around the old tag), and the tag prefix from
  existing tags:

  ```
  git add -A && git commit -m "Release 1.4.0: <headline>"
  git tag v1.4.0
  ```

Close with:

```
Bumped 0.9.4 → 0.9.5 · Pre-flight passed · CHANGELOG entry added · 3 files mirrored
```

**No git writes.** Do not run `git add`, `git commit`, `git push`, or `git tag`. Print them under
**Next** for the owner. A repo-local release skill (§2) may carry that authorisation; this skill
never does.
