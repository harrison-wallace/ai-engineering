---
name: bump-version-sonnet
description: Use when asked to cut a release with a Sonnet subagent applying the edits. The main agent derives the release from the diff and writes the changelog prose, a Sonnet subagent makes the file edits, the main agent verifies. Triggers on "/bump-version-sonnet" or "bump the version with sonnet".
---

# bump-version-sonnet

The same release as [`bump-version`](../bump-version/SKILL.md), split in two: **you decide what
the release is, a Sonnet subagent edits the files, you verify.** The judgement stays with you
because it depends on this conversation; the edits go to Sonnet because they are mechanical,
repetitive, and token-heavy.

Reach for plain `bump-version` on a small release — one subagent round-trip costs more than the
three edits it saves. This skill earns its keep when the release also drags a pile of docs behind
it.

## 1. Derive the release (main agent)

Follow [`bump-version`](../bump-version/SKILL.md) exactly for everything before the edits. All of
it stays with you — do not delegate any of these:

- **Decide the bump type** from the argument, or infer it from the diff against the SemVer table
  and state the choice before applying.
- **Derive the release from the diff (MANDATORY)** — working tree first, commits since the last
  version bump if the tree is clean. **Never ask the user for a summary.**
- **Idempotency.** If `package.json`, `CHANGELOG.md`, and `README.md` already carry the new
  version for this exact work, stop here. Verify, expand any stub, report — do not delegate a
  second bump.
- **Pre-flight.** Run the typecheck yourself (`npx tsc --noEmit --project tsconfig.json`, from
  wherever `tsconfig.json` lives). If it fails, **abort — do not delegate.** A subagent must never
  be the one that decides a failing pre-flight is acceptable. If the repo has no `tsconfig.json`,
  skip the check and say so.

Then write the plan down concretely, because it becomes the subagent prompt: current version → new
version, the **full CHANGELOG block already written out** (dated, sectioned, final prose), the
exact README version strings to change, and the specific doc files the diff has made stale with
what is wrong in each.

Save that CHANGELOG block to `<scratchpad>/expected-block.md` as you draft it, then paste the same
text into the prompt. Phase 3 diffs against that file — a block that exists only inside the prompt
cannot be compared to what actually landed.

## 2. Apply (Sonnet subagent)

Launch a subagent with the Agent tool:

- `subagent_type`: `general-purpose`
- `model`: `sonnet`
- `run_in_background`: `false` — you need the result before you can verify it.
- `prompt`: the plan from step 1, self-contained. Absolute repo path, both version numbers, the
  CHANGELOG block verbatim, and the doc edits with enough context to land them.

**Sonnet writes no prose.** Every word that reaches `CHANGELOG.md` or `README.md` comes from your
plan verbatim — the subagent is transcribing, not authoring. This is the rule the whole skill rests
on: it is what keeps release notes accurate despite the delegation, and it turns your verification
into a cheap string match instead of a re-read. A subagent that "improves" a bullet has failed the
task even if the bullet is better.

The prompt must also carry:

- **The exact insertion point** for the CHANGELOG block: directly under `## [Unreleased]`, above
  the previous version block. Never below an existing version.
- **Replace, don't append**, if a local script already left a `### Changed - <summary>` stub.
- **Change only the version number** in `package.json` — no reformatting, no other fields.
- **Discover the toolchain; do not assume it.** `node -p "require('./package.json').version"` is
  the reference command, not a guarantee — the repo may have no `node` on `PATH`. Tell the
  subagent to read and edit `package.json` as text if so, and to report what it used.
- **No git writes** — no `git add`, `git commit`, `git push`, `git tag`. The owner handles version
  control manually.
- **Report** the files changed and the old → new version it wrote.

## 3. Verify (main agent)

Never trust the subagent's report. The release notes are the deliverable and they are now
second-hand:

```bash
git -C <repo-root> diff
grep -rnE "v?[0-9]+\.[0-9]+\.[0-9]+" README.md package.json | head
```

Check, in order:

- **Version consistency** — `package.json`, the README version line (`**vX.Y.Z**`), and the README
  shields.io badge (`version-X.Y.Z-`) all read the new version. No stale old version survives
  anywhere in the README.
- **CHANGELOG prose is yours, unaltered** — establish this with a diff, never by re-reading it.
  Extract what landed and compare it to the file you saved in step 1:

  ```bash
  # NEW = the version just written, PREV = the version block below it, e.g. [0.8.0] and [0.7.2]
  awk '/^## \[NEW\]/{f=1} /^## \[PREV\]/{f=0} f' CHANGELOG.md > <scratchpad>/actual-block.md
  diff <scratchpad>/expected-block.md <scratchpad>/actual-block.md
  ```

  One trailing blank line is the expected difference — the separator before the previous version
  block, which the extraction picks up. Anything else is a defect: silent edits, dropped bullets,
  and re-worded "improvements" all count.
- **Block placement** — directly under `## [Unreleased]`, today's date, empty sections omitted, no
  leftover stub.
- **Nothing extra** — the diff contains the planned edits and nothing else. Doc syncs you did not
  ask for get reverted.

Fix anything wrong with your own edits. Do not send it back to the subagent unless the whole pass
is wrong.

## 4. Report

- Pre-flight result (passed, or skipped because the repo has no `tsconfig.json`).
- One-sentence release headline derived from the diff.
- Which docs were updated, and which were checked and left alone.
- What you had to fix in the subagent's pass, or "no fixes needed".

Close with the one-liner:

```
Bumped 0.9.4 → 0.9.5 · Pre-flight passed · CHANGELOG entry added · README updated
```

Do NOT run `git add`, `git commit`, or `git push` — the owner handles all version control manually.
