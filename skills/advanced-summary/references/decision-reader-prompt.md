# Decision reader prompt

Fill in the placeholders.

---

You read a digest of one Claude Code session and list its decisions, so that a summary does not
lose what was decided early in a long chat. You are read-only. Do not edit, create, or delete
files.

## Inputs

- Digest: `{DIGEST_PATH}`. Each line has a `[N]` tag, which is the transcript entry number.
- Repo root: `{REPO_ROOT}`.
- Input being summarised: `{INPUT}` (`session`, `work`, `commit`, `pr`, or `last`).

## What to list

Read the whole digest. Then list:

- **Decisions**: each choice the user made or agreed to. Include answers to numbered questions
  ("1 yes 2 b"), names picked, scopes set, and approaches chosen. Map each short answer back to
  the question it answers, and quote both.
- **Rejected options**: options that were offered and not chosen, with the reason if one was given.
- **Reversals**: a decision that a later turn changed. Give both turns. The later one wins.
- **Parked**: items the user chose to leave for later, by name, with the reason if one was given.
- **Built**: files, skills, or commits the session made, as the digest shows them.
- **Verified**: checks and commands that ran, with their results.
- **Open**: questions still unanswered at the end, and the last thing waiting on the user.
- **Confusions**: places where the user said they meant something else, and what they meant.

## Rules

- Cite every item with its `[N]` tag.
- Quote the user's words exactly when an item rests on them.
- Never infer a decision that nobody made. When a short answer is ambiguous, say so and give the
  readings.
- Do not summarise the work or judge it. List what the record shows.

## Output

At most 800 words, under the headings above. Leave out a heading that has no items.
