---
name: basic-alignment
description: Play back the user's ask before any work starts — goal, problem, scope, constraints, what done looks like, meaning-changing readings of unclear or dictated words, and numbered yes/no assumptions — in Simplified Technical English. Report-only. Triggers on "/basic-alignment", "/basic-alignment <messy ask>", "play back what I want", "restate my ask", or "do you understand what I'm asking".
argument-hint: "[ask to restate]"
user-invocable: true
---

# basic-alignment

Restate what the user wants, then stop. **Report only. Do not start the work.** A misreading
that shows up here costs one message to correct. The same misreading found after the build
costs a wrong build.

Inspired by the pstack `in-your-own-words` skill, with a fixed shape that is quick to check.

## 1. Source

- If text follows the command, restate that text.
- Otherwise, restate the user's last message before the command.
- Read it in the light of the conversation so far: earlier asks, answers, and decisions. Do not
  restate the history, only the ask.
- Do not call tools. Do not read files, run commands, or launch agents. This is a playback of the
  ask, not research. If the ask cannot be understood without a file, say so as an assumption.

If there is no ask to restate, say so in one line and stop.

## 2. Language

Write in ASD-STE100 Simplified Technical English. These are the same rules as `basic-summary`:

- Use the active voice.
- Keep each sentence to 20 words or fewer.
- Give one idea in each sentence.
- Use simple tenses: present, past, and future.
- Use the same word for the same idea each time.
- Do not use idioms, slang, or unnecessary jargon.

Then check that each sentence reads one way only:

- Make each "it", "they", and "this" point to one clear thing. If you are not sure, repeat the noun.
- Keep "only" and "not" next to the word they change.
- Do not use slashes. Write "a, b, or both", not "a/b".
- Break up long noun strings. "The proto import budget check script" becomes "the script that checks the proto-import budget".
- Use periods, not semicolons. Do not use em dashes.
- Use the real name of a file, command, flag, or skill, in code font.
- Be specific. Write "a column rename fails the build", not "schema changes can cause issues".
- If a rule makes a sentence worse, fix the sentence another way. Mix short and long sentences inside the 20-word limit, so the text does not read as if a machine wrote it.

Use your own words. Do not copy the user's sentences back. Copied wording hides a misreading,
and new wording shows it.

## 3. Report

```markdown
**Goal:** one sentence. The outcome the user wants, not the task list.

**Problem:** one or two sentences. What is wrong or missing today that makes this worth doing.

**Scope**
- In: what this covers.
- Out: what the user excluded, or what you will not touch unless asked.

**Constraints I heard**
- Where it runs and what it must not touch (repo, worktree, branch, environment, host).
- Order and gates ("thoughts first", "don't build yet", "plan before code").
- Safety lines ("never apply", "don't push", "don't touch main").

**Done looks like:** one or two sentences. How the user can tell it is finished.

**How I read unclear words**
- "<word as written>" → <your reading>. <One line: why this reading.>

**Assumptions**
1. <An assumption that changes what gets built. Answerable with yes or no.>
2. …

Correct by number, or say go.
```

Rules:

- **Leave out any section that has nothing in it.** Never write "none". Keep Goal and Done
  always.
- **Unclear words: only the ones that change the meaning.** A typo or dictation slip with only
  one sensible reading ("inveatigation") passes silently. List a word only when a different
  reading would give different work. Examples: "Clawed sessions" → Claude Code sessions;
  "infrared flags" → infra red flags; "usage tier, sorry, effort tier" → the user corrected
  this to effort tier. Never fix a meaning-changing word silently.
- **Assumptions: only the ones that change what gets built.** Number them. Phrase each one so
  "yes" or "no" settles it. Prefer 0 to 5. Zero is a normal result: then end with "Say go, or
  correct me."
- **Multi-part asks:** if the ask holds several requests, list each request as a Scope "In"
  bullet, so a missing request is obvious.
- **No advice and no plan.** Do not suggest approaches, raise concerns, or list next steps. If
  something looks like a bad idea, write it as an assumption ("3. You accept that X is public").
- Stop after the report. Do not fix, build, commit, or continue the task. Wait for the user.
