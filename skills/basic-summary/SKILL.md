---
name: basic-summary
description: >
  Rewrite the previous assistant message as ASD-STE100 Simplified Technical
  English: one-sentence bullets, one longer sub-bullet each, then one summary
  paragraph. Report-only. Use when the user runs /basic-summary, or asks to
  summarize, summarise, or recap the previous message, the last reply, or
  what you just said.
user-invocable: true
---

# basic-summary

Rewrite the previous assistant message. Report only. Do not continue that task.

## 1. Source

Use the assistant message that came immediately before this request.

That message is the only source. Do not pull in earlier turns, the working tree, or files. If the user names a different message, use that message instead. If there is no previous assistant message, say so in one line and stop.

Keep the meaning. Drop greetings, tool chatter, and repeated points. Do not add advice, next steps, or new facts.

## 2. Language

Write the whole report in ASD-STE100 Simplified Technical English. These are the same rules as section 2 of `docs/AGENTS-TEMPLATE.md`:

- Use the active voice.
- Keep each sentence to 20 words or fewer.
- Give one idea in each sentence.
- Use simple tenses: present, past, and future.
- Use the same word for the same idea each time.
- Do not use idioms, slang, or unnecessary jargon.
- Keep each paragraph to 6 sentences or fewer.

Count the words in every sentence before you send the report. Rewrite any sentence that is over 20 words.

## 3. Report

```markdown
- One sentence. Twenty words or fewer.
  - The sub-bullet explains that point. It may use more than one sentence. Each sentence still follows section 2. It adds detail. It does not repeat the parent.

## Summary

One paragraph. Six sentences or fewer. Each sentence has 20 words or fewer. It restates the message as a whole. It adds no new facts.
```

Rules:

- Give every bullet exactly one sub-bullet. Do not add a second child. Do not nest further.
- The parent is exactly one sentence.
- The sub-bullet carries the detail. It may be longer than the parent.
- Cover the whole previous message. Merge small points. Prefer 3 to 7 bullets. Use no more than 8.
- Do not fix, commit, push, or keep implementing.
