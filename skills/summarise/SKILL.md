---
name: summarise
description: >
  Summarise the last reply (default), this session so far (Decided, Built,
  Parked, Open), or the work that landed (Achieved, Fixed, Implemented) in
  Simplified Technical English bullets. It can also draft a commit message, a
  PR body, a Jira update that colleagues can reference later, or a short
  update for management, as Markdown that pastes into Jira cleanly. Add `plain`
  for a short spoken-English retelling with no bullets or jargon. Report-only:
  it never commits, opens a PR, or posts to Jira. Triggers on "/summarise",
  "/summarise session", "/summarise work since main", "/summarise
  commit", "/summarise pr", "/summarise jira", "/summarise
  management", "/summarise plain", "summarise that", "recap your last
  reply", "where are we in this chat", "what did we do", "what landed", "write
  a commit message", "draft the PR description", "write this up for Jira",
  "update for my manager", or "say that in plain English".
argument-hint: "[last|session|work|commit|pr|jira|management] [since <ref> | last <n> | <sha> | <base>] [plain]"
user-invocable: true
---

# summarise

One skill, seven inputs. Report only. Do not continue the task, fix, commit, push, open a PR, or post
anywhere.

| Input | You want | Source | Sections |
|---|---|---|---|
| `last` (default) | My last reply, in a shape you can scan | The previous assistant message only | Bullets in reply order, then **Summary** |
| `session` | Where this chat stands, before `/clear` or a handoff | This conversation so far | **Decided**, **Built**, **Parked**, **Open**, then **Summary** |
| `work` | What actually landed | This chat plus git | **Achieved**, **Fixed**, **Implemented**, then **Executive summary** |
| `commit` | A commit message to paste | The staged diff, or the working tree, plus this chat | A subject line and a body, or one message per commit when the work should split |
| `pr` | A PR body to paste | The branch against its base, plus this chat | A title, then **Summary**, **Changes**, **Testing**, **Notes for review** |
| `jira` | A record for the ticket, that colleagues and management can look up later | Same as `work` | A headline, then **Background**, **What we did** (in order), **Why**, **Result**, **Next steps**, **References** |
| `management` | A no-fuss update for a manager, read in 20 seconds | Same as `work` | A headline, then **What we did**, **Why it matters**, **Status**, **Needs from you** |

`plain` works with `last`, `session`, and `work`. `jira` and `management` are already plain, so
they ignore it. It swaps the bullets for a short spoken retelling
(§4).

Not for: a deep technical report with the mechanism, the reasons, and the risks
(`summarise-deep`, same inputs), playing back your ask before work starts (`restate-ask`),
a re-pitch with the context you were missing when a reply did not land (`explain-again`),
understanding the code itself (`teach`), or lessons to encode (`reflect`).

## 1. Read the arguments

- The first word picks the input: `last`, `session`, `work`, `commit`, `pr`, `jira`, or
  `management`. With none, use `last`.
- For `work`, `jira`, and `management`, the words after it pick the scope (§2.3). For `pr`, a word after it names the base
  branch (§2.5).
- `plain` anywhere in the arguments turns on plain mode.

When the skill loads from the user's words rather than a slash command, take the input their words
name: "what did we do" or "what landed" → `work`. "Where are we" or "recap this chat" → `session`.
"Write a commit message" → `commit`. "Draft the PR description" → `pr`. "Write this up for Jira" or
"a Jira comment" → `jira`. "Update for my manager" or "for management" → `management`. Anything
else → `last`.

## 2. Collect

### 2.1 `last`

Use the assistant message immediately before this request. It is the only source. Do not pull in
earlier turns, the working tree, or files. If the user names a different message, use that one. If
there is no previous assistant message, say so in one line and stop.

Keep the meaning. Drop greetings, tool chatter, and repeated points. Add no advice, next steps, or
new facts.

### 2.2 `session`

Use the whole conversation so far, including any compaction summary at the top. Check what was
built against `git status --short` so the report does not claim a file that does not exist.

Sort each item into exactly one bucket:

| Bucket | When | Not |
|---|---|---|
| **Decided** | A choice the user made or agreed to: an answer to a question, a name, a scope, an approach | A suggestion nobody took up |
| **Built** | A file, skill, commit, or other artefact made or changed in this session | A plan for one |
| **Parked** | Something the user chose to leave for later, by name | Something simply not reached |
| **Open** | A question still unanswered, uncommitted work, or the next step waiting on the user | A new idea you add now |

Merge related items. Prefer 3–8 bullets across all buckets.

### 2.3 `work`

Default scope is this sitting: this conversation plus the working tree.

```bash
git status --short
git diff HEAD --stat
git log -8 --oneline
```

Then read the diffs that matter (`git diff HEAD`). If the tree is clean, use the last commit
(`git diff HEAD~1..HEAD`) and say so.

| They said | Scope |
|---|---|
| `since main`, `since vX.Y.Z`, or `since <sha>` | That range, git only |
| `last <n>` | Those commits, git only |
| `<sha>` | That commit, git only |
| nothing, or `this sitting` | Conversation plus working tree |

If there is no git repo, use the conversation only and say so. Do not invent work that is not in the
diff or this chat. Plans, suggestions, and "we should" items are out.

Sort each item into exactly one bucket. The most specific wins:

| Bucket | When | Not |
|---|---|---|
| **Fixed** | Something existed and was wrong. It is now correct | New work that happens to prevent a future bug |
| **Implemented** | New capability, code, skill, or docs that did not exist before | A one-line tweak to something that existed (Fixed if it was broken, else Achieved or skip) |
| **Achieved** | An outcome that is not a new artefact and not a fix: a decision, an investigation, a migration, a verification, a DoD met | A restatement of an Implemented or Fixed bullet |

Merge related file changes into one bullet. Prefer 3–7 bullets across all buckets, and never more
than 8 in one. Drop test runs, "looked at the code", next-step ideas, leftover TODOs, and process
("ran typecheck").

If nothing landed, print one line ("Nothing landed this sitting: tree clean, no outcomes in chat.")
and stop.

### 2.4 `commit`

```bash
git status --short
git diff --cached --stat
git diff HEAD --stat
git log -10 --format=%s
```

If anything is staged, the staged diff is the source. Otherwise use the working tree, and say that
nothing is staged. Read the diffs that matter. Use this chat for the why, because the diff only
shows the what.

Match the repo's subject style from `git log`, for example a `feat:` or `docs:` prefix, or a
`Release x.y.z:` subject. Follow the repo's `AGENTS.md` or `CLAUDE.md` when they set commit rules.

When the changes are separate concerns that a reviewer would want apart (two features, a feature
and an unrelated fix), propose one commit for each. Name the files in each commit. When they belong
together, say so in one line and write one message.

### 2.5 `pr`

The base is the word after `pr`, or else `main`. If no `main` exists, use the remote's default
branch.

```bash
git log --oneline <base>..HEAD
git diff --stat <base>...HEAD
```

Read the diffs that matter, and use this chat for the why. If the repo has a PR template
(`.github/pull_request_template.md`, or a file in `.github/PULL_REQUEST_TEMPLATE/`), use its
headings instead of the ones in §4.

### 2.6 `jira` and `management`

Collect as for `work` (§2.3), with the same scopes. Do not sort into buckets. Then add:

- **Order.** List what was done in the order it happened: the order of this chat for this sitting,
  or oldest commit first for a git-only scope.
- **The why.** Take the reasons from this chat. For a git-only scope (`since <ref>`, `last <n>`, or
  a SHA), take them from commit messages and PR bodies only. When no reason is on record, write
  "Reason not recorded". Do not guess.
- **Status.** Done, partly done, or blocked. Uncommitted work is "done locally, not yet merged".
- **Ticket keys.** Find keys such as `ABC-123`:

  ```bash
  git branch --show-current
  git log --format='%s%n%b' <the scope's range>
  ```

  Match `\b[A-Z][A-Z0-9]{1,9}-[0-9]+\b`. Drop matches that are not tickets, such as `UTF-8`,
  `SHA-256`, `ISO-8601`, `CVE-…`, `RFC-…`, and `TLS-…`. A key in the branch name comes first. Add any
  key the user named in this chat. Never invent a key.

## 3. Language

Write the whole report in ASD-STE100 Simplified Technical English. These are the same rules as
section 2 of `docs/AGENTS-TEMPLATE.md`:

- Use the active voice.
- Keep each sentence to 20 words or fewer.
- Give one idea in each sentence.
- Use simple tenses: present, past, and future.
- Use the same word for the same idea each time.
- Do not use idioms, slang, or unnecessary jargon.
- Keep each paragraph to 6 sentences or fewer.

Then check that each sentence reads one way only:

- Make each "it", "they", and "this" point to one clear thing. If you are not sure, repeat the noun.
- Keep "only" and "not" next to the word they change.
- Do not use slashes. Write "a, b, or both", not "a/b".
- Break up long noun strings. "The proto import budget check script" becomes "the script that checks the proto-import budget".
- Use periods, not semicolons. Do not use em dashes.
- Use the real name of a file, command, flag, or skill, in code font.
- Be specific. Write "a column rename fails the build", not "schema changes can cause issues".
- If a rule makes a sentence worse, fix the sentence another way. Mix short and long sentences inside the 20-word limit, so the text does not read as if a machine wrote it.

Count the words in every sentence before you send the report. Rewrite any sentence that is over 20
words.

## 4. Report

`last`, `session`, and `work` use the same bullet shape:

```markdown
## <Section>
- One sentence. Twenty words or fewer.
  - The sub-bullet adds the detail or the "so what". One or two sentences. It does not repeat the parent.
```

- Give every bullet exactly one sub-bullet. Do not nest further.
- The parent is exactly one sentence. It states the outcome, not a file path. A path may go in the
  sub-bullet when it locates the change.
- Leave out a section that is empty. Do not pad.

Then the closing paragraph:

- `last` and `session`: `## Summary`. One paragraph of six sentences or fewer that restates the
  whole. No new facts.
- `work`: `## Executive summary`. Two to four sentences: the original problem, then how this work
  solves it. No new facts.

For `last`, the bullets have no section headings. They follow the reply's order. Prefer 3–7 bullets,
and use no more than 8.

### `commit`

Print each message in a fenced block, ready to paste:

```text
<type>: <subject in the imperative, 72 characters or fewer>

<Body: what changed and why, in short paragraphs or a few bullets.
Wrap at 72 characters. No SHA lists, logs, or file inventories.>

<Any trailer lines the repo or the session requires>
```

For a split, print each block under a line that names its files. Then give the `git add` and
`git commit` order as text for the user to run. Do not run them.

### `pr`

Print the body in a fenced block. A reviewer reads it in under a minute.

```markdown
<Title, 72 characters or fewer>

## Summary
Two to four sentences: the problem, then how this change solves it.

## Changes
- One bullet per change a reviewer must know about. Group by area.

## Testing
What was verified, and how. If nothing was tested, say "Not tested".

## Notes for review
Risks, follow-ups, and anything a reviewer must check by hand. Leave out when empty.

<Any closing lines the repo or the session requires>
```

Do not paste logs, SHA lists, or metric tables. Link to them.

### `jira`

Follow [`references/jira-markdown.md`](references/jira-markdown.md), so that the text pastes into
Jira with no editing. Print it in one fenced block, so that the raw Markdown copies:

````markdown
**<KEY-123>: <What was done, 80 characters or fewer>**

**Background**
One or two sentences: the problem or the request.

**What we did**
1. One step per line, in the order the work happened.
2. Each step says what changed, in words a colleague outside the work understands.

**Why**
- One bullet per key decision: the choice, the reason, and what was ruled out.

**Result**
Done, partly done, or blocked. What was checked, or "Not tested".

**Next steps**
- What remains, and who owns it if known. Leave out when empty.

**References**
- KEY-123, the branch name, the PR link, and doc paths.
````

- Leave out the key and its colon when there is none.
- Use names (files, skills, commands) only where a colleague needs them to find the work.
- Keep it to about 250 words.

### `management`

Follow `references/jira-markdown.md` too, so that the update pastes into Jira, email, or chat.
Print it in one fenced block:

````markdown
**<KEY-123>: <The outcome, in one line>**

**What we did:** One to three sentences.

**Why it matters:** One or two sentences in business terms, such as time saved, a risk removed,
or what it unblocks.

**Status:** Done, in progress, or blocked, and what comes next.

**Needs from you:** A decision or an approval, or "Nothing".
````

- About 120 words at most.
- Use the plain-mode rules below: no jargon, no file names, hashes, commands, or counts, and names
  the reader knows.
- Leave out the key when there is none.

### Plain mode

With `plain`, drop §3 and the bullet shape. Retell the same input like one person talking to
another:

- Short paragraphs of prose. No headings, no bullets, no tables.
- Shorter than the source. About a third of its length is a good target.
- Plain words. No jargon. When a technical term is the point, say what it means in the same
  sentence.
- Say what changed for the user, not how it was done.
- Leave out hashes, paths, commands, and counts unless the user needs one to act.
- Call each thing by a name the user would know, not a label invented in the chat.
- For `session` and `work`, keep the bucket order (decided, built, parked, open, or achieved, fixed,
  implemented), but as sentences, not headings.

## Rules

- Report only. Do not fix, commit, push, open a PR, post to Jira, or keep implementing. `commit`,
  `pr`, `jira`, and `management` print text for the user to use.
- Do not write `BOARD.md`, `NOW.md`, `CHANGELOG.md`, or a phase doc. `/phase sync` updates the
  board, and `/bump-version` writes the changelog.
- Past tense and concrete for `work`. No "various improvements", no hedging.
