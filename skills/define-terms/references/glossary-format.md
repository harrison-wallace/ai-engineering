# GLOSSARY.md format

Adapted from Matt Pocock's `domain-modeling` skill.

## One context

One `GLOSSARY.md` at the repo root:

```markdown
# <Context name>

<One or two sentences: what this context is, and why it exists.>

## Language

**Booking**:
A confirmed reservation of one or more nights for one Guest.
_Avoid_: reservation, order

**Guest**:
A person who stays at a property under a Booking.
_Avoid_: customer, user
```

## Several contexts

`GLOSSARY-MAP.md` at the repo root lists the contexts and how they relate. Each context keeps its
own `GLOSSARY.md` next to its code:

```markdown
# Glossary map

## Contexts

- [Bookings](./src/bookings/GLOSSARY.md): takes and tracks Bookings
- [Billing](./src/billing/GLOSSARY.md): raises Invoices and takes payments

## Relationships

- **Bookings → Billing**: Bookings emits `BookingConfirmed`. Billing consumes it to raise an Invoice.
```

Use a map only when the repo already has separate contexts with their own language. Most repos
have one.

## Rules

- **Pick one word.** When several words name one concept, choose the best one, and list the others
  under `_Avoid_`.
- **Avoid-words are plain words only.** List a word under `_Avoid_` only when it is wrong for this
  concept everywhere in the context. Put no notes in brackets after it. `check` searches for every
  avoid-word as a whole word, so a word that is fine in other senses or inside other terms (task,
  owner, channel, action) gives hundreds of false hits. Put that rule in the definition instead:
  "Say Request channel, never bare 'channel'."
- **Keep definitions tight.** One or two sentences. Say what the thing is, not what it does or how
  the code does it.
- **Domain terms only.** Leave out general programming words (timeout, retry, cache, handler),
  even when the code uses them often. Ask: is this a concept of this project, or of programming?
- **Infra counts when it is specific.** "Edge proxy", "tenant stack", or "media node" belong when
  they mean one thing in this setup. "Container" and "VPC" do not.
- **Group terms** under `###` subheadings when clusters appear. A flat list is fine for one area.
- **No implementation details.** No file names, class names, tables, UI paths ("Settings →
  Connections"), numbers that can change ("the last 14 days"), string formats, or decisions. A
  glossary is not a spec or a scratch pad.
- **Keep the order stable.** Add a term in its group, in the order a reader meets the concepts.
