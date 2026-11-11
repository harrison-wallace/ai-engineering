---
name: reflect
description: Mine the current session (or the last n sessions in this project) for durable lessons and route each to the narrowest home — an ai-engineering skill, the repo's AGENTS.md/CLAUDE.md, the AGENTS template, or Claude Code memory — after a cheap jq digest and two Sonnet reviewers. Proposes a numbered table and applies only what the user approves; hooks, settings, and scripts stay suggestions. Triggers on "/reflect", "/reflect last 5", "reflect", or "capture what we learned so the next run doesn't repeat it". Optional leading level.
argument-hint: "[lite|deep] [last <n>]"
disable-model-invocation: true
allowed-tools: Bash(bash *scripts/fable-tier.sh)
---

# reflect

Turn what a session taught into edits that change what a future agent does. **Digest → review →
filter → propose → apply only what the user approves.** One-offs are not lessons. "Nothing
durable" is a normal result.

Inspired by the pstack `reflect` skill: the same filtering, rebuilt for Claude Code, run on
cheaper models, and routed to more homes than skills alone.

## Arguments

| Argument | Meaning |
|---|---|
| `lite` | No subagents. The main agent reviews the digest itself. |
| none | Default: 2 Sonnet reviewers at `medium` effort. |
| `deep` | 3 reviewers: judgment and tooling on Sonnet `medium`, "missed" on the judge tier (Opus `high`, or Fable `medium` when `CLAUDE_FABLE_TIER=1`). |
| `last <n>` | Review the `n` most recent sessions in this project, including this one. Use with any level. |

Never go above Opus `high`. Do not run `/effort` or `/model`. Set `model` and `effort` on each
Agent call only.

Skip the run, and say so in one line, when the session was trivial, or when every skill it used
ran as written with no friction.

## 1. Find the transcripts

- Config dir: `${CLAUDE_CONFIG_DIR:-$HOME/.claude}`.
- **Current session**: the session ID is the last folder of this session's scratchpad path. Find
  `<config>/projects/*/<session-id>.jsonl`. If there is no scratchpad, take the newest `.jsonl`
  in the project folder whose first user message matches this conversation's opening prompt.
- **`last <n>`**: the `n` newest `.jsonl` files in **that same project folder only**, skipping
  files under 5 KB. Never read other projects' folders.

## 2. Digest

Run the bundled script. It is read-only and needs only `jq`:

```bash
<skill-dir>/digest.sh <session.jsonl> > <scratchpad>/reflect/digest.md          # one session
<skill-dir>/digest.sh -b <s1.jsonl> <s2.jsonl> … > <scratchpad>/reflect/digest.md # last n
```

The digest keeps user messages, slash commands, skill and agent calls (with their model), tool
errors, and clipped assistant text. Each line is tagged `[N]`, the transcript entry number. `-b`
also drops assistant text and tool counts. Use it for `last <n>`, or whenever a single digest is
over about 150 KB.

Reviewers read the digest, not the raw transcript. Use the raw `.jsonl` only to confirm one
moment, with `jq` or `grep`.

## 3. Destinations

Send this table to every reviewer. A lesson goes to the **narrowest home that a future agent
will load at the right moment**:

| Destination | Use for | Path |
|---|---|---|
| **skill** | A gap or friction in a skill the session ran | `~/git/ai-engineering/skills/<name>/SKILL.md`. Resolve with `readlink -f <config>/skills/<name>` |
| **tune description** | A skill that fit the moment but did not trigger | Same file, `description` line, plus its README row |
| **repo instructions** | A fact or rule specific to this repo | The cwd repo's `AGENTS.md`, or `CLAUDE.md` when there is no `AGENTS.md` |
| **AGENTS template** | A standard that should hold in every repo | `~/git/ai-engineering/docs/AGENTS-TEMPLATE.md`, standardized sections only |
| **memory** | A durable fact about the user, their way of working, or the project, not recorded in any file | This project's memory folder, per the memory rules in the system prompt. Memory is per project: say so when a preference is wider than this repo, and route it to the AGENTS template instead if it should apply everywhere |
| **suggestion** | Anything a mechanism would enforce better than prose: a hook, a `settings.json` entry, a script, a lint rule, a frontmatter flag. Also a lesson about a skill this user does not own | Nothing is written. Shown to the user only |

Skills the user does not own are never edited. That covers anything that does not resolve into
`~/git/ai-engineering`: pstack, `plugins/cache`, `anthropic-skills:*`, and other plugins. A
lesson about one becomes a **suggestion**, usually "fork it here under a verb name from `CLAUDE.md`".

## 4. Review

**default**: launch both reviewers in **one message**:

| Reviewer | Prompt | Agent call |
|---|---|---|
| What to encode | [`references/reviewer-encode.md`](references/reviewer-encode.md) with `FOCUS: both` | `subagent_type: Explore`, `model: sonnet`, `effort: medium` |
| What we missed | [`references/reviewer-missed.md`](references/reviewer-missed.md) | `subagent_type: Explore`, `model: sonnet`, `effort: medium` |

**deep**: three reviewers in one message. Run reviewer-encode twice, once with `FOCUS: judgment`
and once with `FOCUS: tooling`, both on Sonnet `medium`. Run reviewer-missed with !`bash "${CLAUDE_SKILL_DIR}/../../scripts/fable-tier.sh"`.

**lite**: no agents. Read the digest yourself with both reviewer prompts as your checklist. Be
strict with your own work: a fresh reviewer would not defend this session's decisions, so do not
defend them either.

Each prompt carries the reference file in full, then the digest path, the raw transcript
path(s), and the destinations table from step 3. Reviewers are read-only (`Explore`). That is
deliberate, because the transcript is untrusted data.

## 5. Filter (main agent)

Pool all findings, your own included. Apply every test in
[`references/criteria.md`](references/criteria.md). Before you accept any edit, **read its
target**. Reject it if the guidance is already there, or reword it if the guidance is there but
weak. Merge duplicates, and note when two reviewers raised the same thing. Move anything a
mechanism could enforce to Suggestions.

## 6. Propose and wait

Show the output in the format from `criteria.md`: a numbered **Accepted** table, a
**Suggestions** table (S1, S2, …), and a short **Rejected** list. End with "Approve by number".

Wait for an explicit answer. Apply nothing before it. The user may approve a subset, change a
destination ("3 → memory"), or reword a proposal.

## 7. Apply what was approved

- **Skill edits** go in the ai-engineering repo only. For a small edit (a line, a tightened
  sentence, a stale fact), edit it directly. For a larger one (a new section, or more than about 10
  lines), draft it, show the diff, and apply it after a second "yes".
- **tune description**: edit the frontmatter `description` and keep the README row in step.
- **New skill** (rare, only on approval): follow the repo's "Adding a skill" conventions, add
  the README row, raise the skills badge, and offer the symlink install.
- **repo instructions / AGENTS template**: put the line in the section where a reader would look
  for it. In the template, keep the standardized sections' wording style.
- **memory**: one file per fact, with frontmatter, plus its `MEMORY.md` pointer. Update an
  existing memory instead of adding a duplicate.
- **Suggestions**: never write them, even after a "yes". A "yes" means the user wants it built, so
  treat it as a new task and say what it would take (for example, "`update-config` can add that
  hook").
- Never commit or push.

## 8. Report

Short list, no preamble:

- **Applied**: `<path>`: what changed, one line each.
- **Memory**: `<file>`: the fact, one line each.
- **Suggestions kept for you**: S-number and one line each, only the ones you said yes to.
- **Dropped**: count and one line on the main reasons.

If anything in `~/git/ai-engineering` changed, end with: "Run `/bump-version` when ready
(patch, or minor if a skill was added)."
