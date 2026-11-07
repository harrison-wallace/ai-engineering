---
name: basic-unslop
description: Cut AI writing tells from the repo's prose (AI vocabulary, filler, hedging, em dashes, abstract metaphors, inline-header lists, title-case headings, and chatbot phrases) and fix them in place by default. Targets the diff (default), docs, the README, the CHANGELOG's Unreleased section, the whole repo, or named paths. `scan` reports instead of fixing. Each hit cites a short rule name from references/rules.md. Triggers on "/basic-unslop", "/basic-unslop scan", "/basic-unslop repo", "unslop this", or "remove the AI tells from the docs".
argument-hint: "[scan] [diff | docs | readme | changelog | repo | <paths>]"
disable-model-invocation: true
---

# basic-unslop

Find the patterns that make prose read as machine-written, and rewrite them. **Fix by default.**
`scan` reports only. Keep the meaning and the tone. Never commit.

Adapted from the pstack `unslop` skill. The rules use short names instead of numbers, so a report
row reads at a glance.

## 1. Read the arguments

- `scan` anywhere → report only. Otherwise, fix.
- The target, default `diff`:

| Target | Files | Lines in scope |
|---|---|---|
| `diff` | Changed and untracked prose files: `git diff HEAD --name-only` plus `git ls-files --others --exclude-standard` | Only the added or changed lines. Leave untouched paragraphs alone |
| `docs` | `git ls-files 'docs/**'` prose files | All |
| `readme` | Every tracked `README.md` | All |
| `changelog` | `CHANGELOG.md` | The `[Unreleased]` section only. Released entries are history. `changelog all` widens it |
| `repo` | `git ls-files` prose files | All |
| `<paths>` | The named files or folders | All |

Prose files are `.md`, `.mdx`, and `.txt`. If the target matches no files, say so in one line and
stop.

## 2. Leave these alone

- Code blocks, inline code, frontmatter keys, URLs, and link targets.
- Quoted text: block quotes of a source, trigger phrases in quotes, and example sentences. A rule
  file or a style guide quotes bad patterns on purpose, and that is not a hit.
- License text, `THIRD_PARTY_NOTICES.md` license blocks, `archive/`, vendored folders, and
  `node_modules`.
- This skill's own folder.
- Released CHANGELOG entries, unless the target is `changelog all`.

## 3. Find the hits

Read [`references/rules.md`](references/rules.md) first.

Start with a mechanical sweep. Each match is a lead, not yet a hit:

```bash
rg -n '—|–' <files>                                     # em-dash
rg -n '[“”‘’]' <files>                                  # curly-quotes
rg -n -i '\b(additionally|crucial|delve|enduring|enhance|fostering|garner|interplay|intricate|pivotal|showcase|tapestry|testament|underscore|vibrant)\b' <files>   # ai-vocab
rg -n -i '\b(in order to|due to the fact that|it is important to note|it.s worth noting)\b' <files>   # filler-phrase
rg -n -i '\b(serves as|stands as|boasts)\b' <files>     # fancy-is
rg -n -i '\b(utili[sz]e|leverage|facilitate|numerous|in the event that)\b' <files>   # fancy-word
rg -n -i '\b(substrate|locus|nexus|north star|flywheel|paradigm|modality|endgame)\b' <files>   # abstract-metaphor
rg -n '^\s*[-*] \*\*[^*]+:\*\*' <files>                 # inline-header-list
rg -n '^#{1,6} .*\b[A-Z][a-z]+ [A-Z][a-z]+' <files>     # title-case
```

For `diff`, keep only matches on added lines (`git diff HEAD -U0`, lines starting with `+`), plus
untracked files.

Then read the in-scope text for the rules no grep catches: `feeling-not-mechanism`,
`mannered-prose`, `rule-of-three`, `synonym-cycling`, `dense-sentence`, `over-compression`,
`generic-conclusion`, `hedging`, and `passive`.

## 4. Fix (default)

For each hit, rewrite the smallest span that removes it. Then:

- Keep the meaning, the facts, the Markdown structure, the links, and the tables.
- Keep the author's tone. Do not shorten text that has no hit.
- When a rewrite would change the meaning, or you are not sure, do not apply it. List it under
  **Not changed**.
- When a heading changes, search for links to its anchor (`#old-heading`) and update them. If you
  cannot find them all, leave the heading.
- Use the Edit tool, one file at a time.

For `repo` or `docs` with more than 15 files, batch the files, about 8 to a batch, and launch one
Sonnet agent per batch in **one message**: `subagent_type: general-purpose`, `model: sonnet`,
`effort: medium`, `run_in_background: false`. Give each agent its file list, the path to
`references/rules.md`, and §2 and §4 of this skill. Each agent edits only its own files. After they
return, read `git diff --stat` and spot-check at least one file per batch.

## 5. Report

### After a fix

```markdown
**Fixed <n> hits in <m> files.** Review with `git diff`.

| Rule | Location | Before | After |
|---|---|---|---|
| `em-dash` | `README.md:42` | the cache — when warm — skips | the cache skips the read when it is warm |
```

- One row per hit, at most 20 rows. Then: `<n> more rows omitted.`
- **Not changed**: one line each, with the location and the reason.
- Coverage line: `Checked <m> files (<target>). Skipped <k> by §2.`

### After `scan`

The same table, with the heading `**<n> hits in <m> files.** Run /basic-unslop to fix them.`
Change the `After` column to a proposed rewrite.

## Rules

- Never commit, push, or stage.
- Never touch code, only prose.
- A fix that makes the sentence worse is not a fix. Leave the sentence, or rewrite it another way.
