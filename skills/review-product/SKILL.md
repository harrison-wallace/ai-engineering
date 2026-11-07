---
name: review-product
description: Review a product, feature, or launch plan against Dax Raad's three product principles — shareable marketing, a single Aha moment, and primitives-first retention. Retention maps the product's primitives (core building blocks) against the real data model in the repo, and marks features built as one-offs instead of extending a primitive. `feature <idea>` judges one planned feature: does it extend a primitive, expose more of one, need a new one, or add a one-off. Use at kick-off, before major feature decisions, during onboarding design, or pre-launch. Report-only. Triggers on "/review-product", "/review-product feature <idea>", "review this against the Dax principles", or "does this feature extend a primitive".
argument-hint: "[feature <idea>]"
---

# review-product

Evaluate the current project (or a described product/feature/launch plan) against
the three things AI can't do for you — from Dax Raad's OpenCode talk (March 2026).
Full source principles: [dax-insights.md](dax-insights.md).

| First argument | Mode |
|---|---|
| none | Review the whole product against all three principles (§1–§3) |
| `feature <idea>` | Judge one planned feature against the primitives only (§4) |

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

Answer the checklist from the **primitives map** below, not from the README.

#### The primitives map

A primitive is a building block that users combine: a project, a document, a
block, a member, a trigger, a view. A feature is the simple experience on top
of one or more primitives.

1. **Find the data model.** Read what the repo actually stores and passes:
   `prisma/schema.prisma`, a Drizzle `schema.ts`, `supabase/migrations/` or other
   SQL migrations, Zod schemas, and the core TypeScript types (`types/`,
   `lib/**/types.ts`). Then read the routes and server actions that write them
   (`app/api/**/route.ts`, `actions.ts`). With no repo, map from the plan and
   mark every row "not in code yet".
2. **Name the primitives.** At most 7. For each one, cite the model or type
   (`file:line`). A primitive the product needs but the code does not have is
   a row with status **missing**.
3. **Map the features onto them.** For each user-facing feature (from the
   routes, the navigation, and the README), name the primitive it sits on.
4. **Mark each one-off.** A feature is a one-off when it does not extend a
   primitive. Signs, each with the cited line:
   - Its own model or table that repeats fields of a primitive and links to
     nothing.
   - A boolean or nullable column added for one feature (`isPinned`,
     `customLogoUrl`) where a field on the primitive would cover the general
     case.
   - A hardcoded list in code where users will want data: plans, roles,
     statuses, templates.
   - A route or action that writes a primitive's table directly and skips that
     primitive's own module.
5. **Name the power-user unlocks.** For each primitive, one or two things power
   users would do with the same primitive exposed more (an API, filters,
   automation, bulk actions, custom fields). If an unlock needs a new primitive,
   the schema is not ready for it. Say so.

A one-off that comes from conditionals in the code (a branch for each plan, flags
that must agree) is also a `check-primitives` finding. Offer
`/check-primitives <path>` for it. Do not repeat its full analysis here.

## 3. Report

Output two tables, the scores and then the primitives map, then a short verdict.
The scores:

| Principle | Status | Finding |
|---|---|---|
| Marketing | ✅ / ⚠️ / ❌ / ❓ | One or two sentences: what's strong or missing. |
| Aha Moment | … | … |
| Retention | … | … |

- ✅ solid, ⚠️ partially addressed, ❌ missing or violates the principle,
  ❓ not enough information to judge (say what's needed to judge it).
- After the table: the single highest-leverage action for each ⚠️/❌ row — a
  concrete next step, not a restatement of the principle.

Then the primitives map:

| Primitive | In code | Features on it | One-offs | Power-user unlock |
|---|---|---|---|---|
| Project | `prisma/schema.prisma:12` | Dashboard, sharing | `ProjectArchive` table repeats `Project` fields (`schema.prisma:88`) | Custom fields on projects |

- "In code" is a `file:line`, **partial** with the line and what is missing, or
  **missing**.
- One cell per fact. Keep each cell to one short sentence.
- The example row shows the shape. Do not copy it into a real report.

- Close with one line of overall verdict. Do not pad; if all three are solid,
  say so and stop.
- **Do not implement anything** — this skill assesses and recommends. The user
  decides what to act on. Offer `/check-primitives <path>` for one-offs that come
  from code shape, and `/design lite` for a missing primitive.

## 4. Feature mode

`/review-product feature <idea>` judges one planned feature before it is built.
Marketing and the Aha moment are out of scope here.

1. State the feature in one sentence, and who it is for.
2. Build the primitives map (§2) for the primitives the feature touches only.
3. Give one verdict:

| Verdict | Means |
|---|---|
| **Extends** | It is a new use of existing primitives. No new model, at most a field that is general |
| **Exposes more** | It shows power users more of an existing primitive, such as an API, filters, or bulk actions |
| **New primitive** | It needs a new building block that later features will also use. Name two of them |
| **One-off** | It adds a model, a column, or a branch that only this feature uses |

4. Report, in this order:
   - **Verdict**, and one sentence of reason.
   - **Builds on**: each primitive, with its `file:line`.
   - **Shape**: the smallest data change that keeps it in the first three
     verdicts: the field, the relation, or the new primitive, as a short type or
     schema excerpt of at most 10 lines.
   - **One-off risk**: what the one-off version would add, and the next feature
     it would block or duplicate.
   - **Next**: for a new primitive, offer `/design lite <feature>`. For a
     one-off, the shape above is the fix. Offer `/delegate` once the user picks.

Do not implement anything.
