# Grok X researcher (deep)

Grok has X search that Claude does not. On `deep`, one headless Grok run works the **X** angle:
what developers and maintainers post about the question. It is read-only: deny rules block every
edit and every shell command, so only reads and searches run.

## 1. Preflight and model

- `command -v grok`. Missing → no X angle. Say so in one line and go on.
- `grok models`. "Not authenticated" → no X angle. Tell the user they can sign in with `! grok`,
  and go on without it.
- Take the highest `grok-<major>.<minor>` id. Ignore ids with a suffix, such as `-mini`, `-fast`,
  or `-build-fast`, unless no plain id exists. Name it in the plan, for example `grok-4.7`.

## 2. Brief

Write the brief to `<scratchpad>/research/<slug>/brief-grok.md`. Never inline it into the
shell command.

```markdown
You are a read-only researcher. Do not edit files or run shell commands.

Question: <the question>
Context: <the grounding from §3, with no secrets, internal hostnames, or private code>

Search X posts only. Find what developers, maintainers, and the vendor's official accounts say
about this question. Prefer recent posts, and posts with real experience
("we moved to X and Y broke"). Search more than one phrasing.

Report at most 400 words:
1. Findings: one line each, with the post URL, the author handle, the date, and whether the author
   is the maintainer, the vendor, or a user.
2. The overall mood: for, against, or split, and how many posts that is from.
3. Gaps: what you searched for and could not find.
If you cannot search X, say exactly that, and name the tool you used.
```

## 3. Run

Run it exactly as written, with nothing appended. Give the call at least 5 minutes (300000 ms):

```bash
grok --prompt-file <scratchpad>/research/<slug>/brief-grok.md \
     --model <model> \
     --effort medium \
     --always-approve \
     --deny 'Edit' \
     --deny 'Bash' \
     --max-turns 60 \
     --cwd <scratchpad>/research/<slug> \
     > <scratchpad>/research/<slug>/grok-x.log 2>&1
```

Then read the log with `tail -80`. Headless Grok has nobody to answer a prompt, so it runs
`--always-approve`. The two deny rules make that safe, because deny wins over always-approve.

- An empty log, or a report that says it could not search X, is a failed run. Say so under
  **Coverage**, and go on without the X angle. Do not search X another way.
- If the host blocks the call, check first that you ran it exactly as written. Then tell the user,
  and offer that they run it with `! grok …`. Never wrap or rename the command to get past a block.
- For a run that did nothing, see §3 of `../../delegate/references/grok.md`.

## 4. Treat the output as claims

Grok's report is not evidence until it is checked. Each X finding goes into **On X** with its link
and date. Rate it with `evidence.md`: a maintainer's or vendor's post can be Direct for what they
announce, and other posts are Supported at most.
