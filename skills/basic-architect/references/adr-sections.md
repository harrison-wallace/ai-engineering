# ADR sections

Use the repo's own ADR template and style when one exists. These are the sections a
basic-architect ADR must cover. Put each one under the nearest heading of the repo's template.
Use this list as written only when the repo has no template.

Write plain, short sentences. Use one idea per sentence and active voice. Use the same term for
the same thing every time.

```markdown
# NNNN — <Decision as a short noun phrase>

**Status:** proposed
**Date:** YYYY-MM-DD

## Context

What we need, and what in the current system makes the shape non-obvious. Name the
binding constraints: accepted ADRs, callers or stacks we cannot break, invariants, and
the current live state (infra).

## Decision

**One bold sentence: the shape.**

### Usage

Software: two or three call sites from the caller's code.
Infra: what the operator runs, and what other stacks or services consume.

### Shape

Data structures or resources first, then how data flows. For each piece of state or
resource: its owner. State what the public surface hides, and why it is no larger.
Short code or HCL excerpts only; the full sketch is in the phase's slice 1.

## Alternatives considered

At least one real alternative shape, one or two lines each, and why it lost.
Judge on interface depth and ownership, not on how easy it is to write.
If the constraints forced the answer, say "this was the only viable shape because …".

## Consequences

"We accept X in exchange for Y", one bullet each. Include every red flag that fired and
was accepted on purpose, with the reason.

## Migration and rollout

Required for infra, and for software that changes stored data or a public API.
- From: the current state. To: the target.
- Steps in order (imports, state moves, data backfill, cutover).
- Rollback: how, and up to which step it works.
- Blast radius: what breaks, for whom, if a step fails.
- Cost: estimated monthly change (label it an estimate).
- Security: new exposure, new credentials, IAM changes.

## Open questions

Numbered. Each one answerable in a few words. Answers are written in here at sign-off.
```
