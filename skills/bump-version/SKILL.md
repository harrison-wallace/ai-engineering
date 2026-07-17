---
name: bump-version
description: Use when asked to bump the version, update the changelog, or release a new version. Triggers on "bump version", "update changelog", "release", or "bump patch/minor/major".
---

# bump-version

Bump the version, mirror it in `README.md`, and add a `CHANGELOG.md` entry — all in one step.

## Usage

```
/bump-version
/bump-version patch
/bump-version minor
/bump-version major
```

Optional type only. **Never ask the user for a summary** — derive everything from the git history / working-tree diff (see below).

### Decide bump type

| Input | Action |
|---|---|
| User passed `patch` / `minor` / `major` | Use that type |
| No type given | Infer from the diff against AGENTS.md SemVer rules, then state the choice briefly before applying. Only ask if genuinely ambiguous (e.g. equal case for minor vs major) |

SemVer quick reference (from AGENTS.md):

| Increment | When |
|---|---|
| `PATCH` | Bug fixes, performance, UI tweaks, error handling, copy, dead-code removal |
| `MINOR` | New features, pages, endpoints, agents, significant UI redesigns |
| `MAJOR` | Breaking architecture, schema migrations needing data migration, rewrites |

## Project detection

```bash
test -f ./scripts/bump-version.sh && echo "local" || echo "manual"
```

- **If `./scripts/bump-version.sh` exists** — after writing the summary yourself, run:
  `./scripts/bump-version.sh (patch|minor|major) "one-line summary"`.
  The script handles pre-flight, version bump, README badge, and a CHANGELOG stub. Then expand the stub (step 5) and do doc sync (step 6).
- **If no local script** — follow all steps below manually, including pre-flight.

## Derive the release from the diff (MANDATORY)

Do this **before** writing any CHANGELOG prose. The point of the skill is that the agent decides; the user should not have to narrate the release.

1. **Find the previous released version** — read `web/package.json` (or root `package.json`) version field, and the latest `## [X.Y.Z]` block under `CHANGELOG.md`.
2. **Collect what changed since that version**:
   ```bash
   # Working-tree + index (uncommitted release work is the common case)
   git status --short
   git diff HEAD --stat
   git diff HEAD

   # If the branch is ahead of main / last tag, also:
   git log --oneline <last-version-commit>..HEAD
   git diff <last-version-commit>..HEAD --stat
   ```
   Prefer the uncommitted working-tree diff when it contains the release work. If the tree is clean, use commits since the last version bump commit (the one that last touched `web/package.json` / CHANGELOG).
3. **Classify** each change into Added / Changed / Fixed / Removed.
4. **Write the summary** yourself:
   - One-line summary for the script (if used): short, imperative, covers the headline.
   - Full CHANGELOG body: what / why, only sections with content. Be concrete (files, behaviours, user-visible effects) — not "various improvements".
5. **Idempotency**: if `package.json` / CHANGELOG / README already reflect the new version for this exact work (e.g. a prior agent pass), do **not** bump again. Verify pre-flight + docs, expand any stub, and report. Only bump when the version on disk still matches the *previous* release.

## Pre-flight Checks (MANDATORY — skip only if local script ran them)

From the project root (or `web/` if that is where `tsconfig.json` lives):

```bash
npx tsc --noEmit --project tsconfig.json
# this repo: ( cd web && npx tsc --noEmit --project tsconfig.json )
```

If this fails → **abort the bump immediately**. Print the errors and tell the user they must be fixed before any version bump is allowed.

## Steps (execute in order)

### 1. Read current version

```bash
node -p "require('./package.json').version"
# or, if the project lives under web/:
node -p "require('./web/package.json').version"
```

### 2. Calculate new version

Split `MAJOR.MINOR.PATCH`, increment the right segment, reset lower segments to 0.

### 3. Update `package.json`

Change the `"version"` field only. Do not touch anything else.

### 4. Update `README.md`

Update the version everywhere it appears near the top (a project may use one, both, or neither form — replace the number in-place and leave the rest of each line unchanged):

- **Standalone version line** of the form `**vX.Y.Z**`.
- **Shields.io version badge** of the form `version-X.Y.Z-` inside a badge URL, e.g.
  `![Version](https://img.shields.io/badge/version-1.2.0-6366f1?style=flat-square)`.
  Update only the `X.Y.Z` between `version-` and the trailing `-<color>`; keep the colour/style query intact.

After editing, grep to confirm no stale version remains in the README:

```bash
grep -nE "v?[0-9]+\.[0-9]+\.[0-9]+" README.md | grep -v "NEW_VERSION"   # eyeball for any old version left behind
```

### 5. Update `CHANGELOG.md`

Insert a new block **between** `## [Unreleased]` and the previous latest version block. Format:

```markdown
## [NEW_VERSION] - YYYY-MM-DD

### Added
- (omit section if nothing added)

### Changed
- (omit section if nothing changed)

### Fixed
- (omit section if nothing fixed)

### Removed
- (omit section if nothing removed)
```

- Use today's date (`date +%Y-%m-%d`).
- Only include sections that have content — omit empty ones.
- Each bullet: what changed, what was fixed, and why it matters (brief). Derived from the diff — never a placeholder the user must fill in.
- Never push the new block below an existing version — it always goes directly under `## [Unreleased]`.
- If the local script already inserted a stub `### Changed - <summary>`, **replace/expand** that stub into the full multi-section entry in the same pass.

When one uncommitted tree clearly contains two separable releases (e.g. feature A then follow-up feature B), you may emit two sequential blocks (minor then patch, etc.) and set `package.json` to the tip version. Prefer one block when the work is a single coherent release.

### 6. Sync docs with what shipped

Using the same diff as step "Derive the release":

- Update `README.md` if any feature description, config table, or usage example it contains is now out of date.
- Update any other `.md` files in the repo root or `docs/` that describe behaviour this release changed — stale docs are bugs. Only touch sections that the diff actually makes wrong; leave everything else alone.
- If nothing in the diff contradicts an existing doc, skip this step entirely.

### 7. Confirm

- State that pre-flight TypeScript check passed (or that the local script ran it).
- One-sentence release headline derived from the diff.
- List which docs were updated (and confirm any that were skipped as unaffected).
- Print a one-line summary:

```
Bumped 0.9.4 → 0.9.5 · Pre-flight passed · CHANGELOG entry added · README updated
```

Do NOT run `git add`, `git commit`, or `git push` — the owner handles all version control manually (per AGENTS.md).
