# Short ADR format

Adapted from Matt Pocock's `domain-modeling` skill. This is for decision and rejection records.
`design` writes the long design ADRs, in its own `references/adr-sections.md`.

## Where and how numbered

- `docs/adr/`, or the folder the repo already uses for ADRs.
- File name: the next number after the highest one in the folder, and a slug, in the pattern the
  folder already uses (`0007-no-shared-booking-cache.md`). An empty folder starts at `0001`.
- **The repo's template wins.** Copy the heading shape, the status line, and the sections of the
  newest ADR in the folder. Use the form below only when the folder is empty or missing.

## Form

```markdown
# NNNN — <The decision, as a short phrase>

**Status:** accepted
**Date:** YYYY-MM-DD

<One to three sentences: the context, what we decided, and why.>
```

That is the whole ADR in most cases. The value is the record that a decision was made, and why.

**Status** is one of `proposed`, `accepted`, `rejected`, or `superseded by NNNN`. A rejection says
what was considered and why it lost:

```markdown
# 0007 — Do not merge the Booking and Payment modules

**Status:** rejected
**Date:** 2026-11-07

We considered merging them into one deep module. We kept them apart, because Payment must deploy
on its own for PCI audits. Do not suggest the merge again unless that audit rule changes.
```

## Optional sections

Add one only when it earns its place:

- **Considered options**: when the losing options are worth remembering.
- **Consequences**: when a downstream effect is not obvious.

## What qualifies

- The shape of the system: a monorepo, an event-sourced write model.
- How contexts talk: events, not synchronous HTTP.
- Technology with lock-in: the database, the auth provider, the deployment target.
- Ownership and scope: "Billing owns Invoices. Others refer to them by ID only."
- A deliberate move away from the obvious path: "raw SQL, not an ORM, because X".
- Constraints the code does not show: compliance, a partner's latency limit.
- A non-obvious rejection: otherwise someone suggests it again in six months.
