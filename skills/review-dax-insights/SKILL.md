---
name: review-dax-insights
description: Review a product, feature, or launch plan against Dax Raad's three product principles — shareable marketing, a single Aha moment, and primitives-first retention. Use at kick-off, before major feature decisions, during onboarding design, or pre-launch. Triggers on "/review-dax-insights" or "review this against the Dax principles".
---

# review-dax-insights

Evaluate the current project (or a described product/feature/launch plan) against
the three things AI can't do for you — from Dax Raad's OpenCode talk (March 2026).
Full source principles: [dax-insights.md](dax-insights.md).

## 1. Establish what's being reviewed

Identify the subject from the conversation or the repo (README, landing copy,
onboarding flow, data model). If it's genuinely unclear what the product or
feature is, ask before reviewing. Otherwise state your understanding in one
sentence and proceed.

## 2. Score each principle

Assess the subject against each of the three principles. For each, answer the
checklist honestly — "unknown" is a valid and important answer.

### Marketing — Shareable Cool

No one wakes up caring about the product. Something must be surprising, funny,
useful, or relatable enough that people actively show it to others.

- Is there a defined viral hook / shareable asset? Would *you* forward it to a
  friend in the niche?
- Does it avoid reading like a "new feature announcement"?
- Is it designed to reach people who have never heard of the product?
- Pitfalls to flag: boring blog posts, feature drops, influencer reviews,
  AI-brainstormed hooks (they end up corny).

### Aha Moment — One Singular Moment

There must be one exact moment where the user thinks "this is why this exists,"
reached in under 60 seconds.

- Is the Aha moment defined in one sentence? What's the time from first click
  to Aha?
- Onboarding is 2–3 taps max before Aha; no company-size/title/qualifying
  questions before value.
- Has it been tested with 5+ real target users, with times recorded?
- Pitfalls to flag: showing "all the good features" too early; resistance to
  killing darlings; every extra screen must be justified with data or removed.

### Retention — Primitives First, Simple UX on Top

Powerful, flexible primitives under the hood; the simplest possible experience
wrapped on top for 99% of users. Never build something people outgrow.

- Are the core primitives (data model / building blocks) identified? Is the
  schema designed for future complexity today?
- Do starter users never feel "this is a toy," while power users can flex
  without leaving?
- Can the product grow with the user without needing a new product?
- Pitfalls to flag: "simple but incapable" (the Apple fallacy); bolting on
  features instead of extending primitives.

## 3. Report

Output one table, then a short verdict:

| Principle | Status | Finding |
|---|---|---|
| Marketing | ✅ / ⚠️ / ❌ / ❓ | One or two sentences: what's strong or missing. |
| Aha Moment | … | … |
| Retention | … | … |

- ✅ solid, ⚠️ partially addressed, ❌ missing or violates the principle,
  ❓ not enough information to judge (say what's needed to judge it).
- After the table: the single highest-leverage action for each ⚠️/❌ row — a
  concrete next step, not a restatement of the principle.
- Close with one line of overall verdict. Do not pad; if all three are solid,
  say so and stop.
- **Do not implement anything** — this skill assesses and recommends. The user
  decides what to act on.
