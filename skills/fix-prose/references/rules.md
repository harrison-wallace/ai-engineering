# Rules

Each rule has a short name. Reports cite the name. Other skills can cite it too, so do not rename
a rule. To retire one, delete it and do not reuse its name.

## Content

- **`ing-phrase`**: tacked-on "-ing" phrases that claim meaning without showing it: "highlighting…",
  "ensuring…", "reflecting…", "showcasing…", "fostering…". Delete it, or state the fact it hints at.
- **`vague-attribution`**: "experts believe", "industry reports suggest", "some argue". Name the
  source or delete the claim.

## Language

- **`ai-vocab`**: additionally, crucial, delve, enduring, enhance, fostering, garner, interplay,
  intricate, landscape (abstract), pivotal, showcase, tapestry (abstract), testament, underscore,
  vibrant. Use the plain word.
- **`fancy-is`**: "serves as", "stands as", "boasts", "features". Say "is" or "has".
- **`not-just-but`**: "not just X, but Y". State the point directly.
- **`rule-of-three`**: ideas forced into groups of three. Use the real number.
- **`synonym-cycling`**: one thing called by several names in one passage ("the gate", "the
  check", "the guard"). Pick one name and repeat it.
- **`false-range`**: "from X to Y" where X and Y are not on one scale. List the items.

## Style

- **`em-dash`**: no em dashes or en dashes. Do not swap in a hyphen or parentheses. End the
  sentence, or use a comma.
- **`colon-crutch`**: a colon used as a mid-sentence connector. A colon before a list or an
  example is fine. "If you come from X: do Y" becomes a plain sentence.
- **`bold-overuse`**: bold on every name or acronym. Bold only what the reader must not miss.
- **`inline-header-list`**: a bold label and colon that restates its line: "**Performance:**
  Performance improved…". Turn it into prose. A bold lead-in that names the item and is followed by
  new detail is fine. So is a template's field label.
- **`title-case`**: headings in Title Case. Use sentence case. Keep proper nouns.
- **`emoji`**: decorative emoji in headings and bullets. Remove them.
- **`curly-quotes`**: curly quotes and apostrophes. Use straight ones.

## Communication

- **`chatbot-phrase`**: "I hope this helps!", "Let me know if…", "Of course!", "Certainly!",
  "Great catch!". Remove.
- **`sycophancy`**: "Great question!", "You're absolutely right!". Respond directly.

## Filler

- **`filler-phrase`**: "in order to" → "to". "Due to the fact that" → "because". Delete "it is
  important to note that" and "it's worth noting that".
- **`hedging`**: stacked hedges, such as "could potentially possibly be argued that it might".
  Use one hedge, such as "may", or none when the fact is known.
- **`generic-conclusion`**: "The future looks bright." "This sets us up for success." State the
  real plan or fact, or delete it.

## Jargon

- **`abstract-metaphor`**: nouns that sound technical but stand in for a plain word: substrate
  (base), wedge or wedge in (add), vector (way), locus, vantage, nexus, primitive as a noun, harness
  as a metaphor, surface as in "API surface", bedrock, scaffolding as a metaphor, modality,
  paradigm, gold-plating (more than the job needs), ratchet as a metaphor (a limit that only
  tightens), evacuate (move out), endgame (the last phase), north star, flywheel. Use the concrete
  word.

## Plain speech

- **`feeling-not-mechanism`**: text that names a feeling ("SQL you can read", "types that follow
  your schema") instead of the mechanism or a number ("`.toSQL()` returns the exact string sent to
  the database", "a column rename fails the build"). Ask what the sentence tells the reader to do
  or know, and write that. If the sentence could appear unchanged in another project's docs, it
  says nothing about this one. Cut it.
- **`dense-sentence`**: a sentence the reader must re-read to parse. Split it, or drop clauses.
- **`passive`**: "is, are, was, or were" plus a past participle, where the actor matters. "Queries
  are validated" becomes "the compiler validates queries". Passive is fine when the actor is
  unknown or does not matter.
- **`adverb-prop`**: an adverb that props up a weak verb. "Runs quickly" becomes "is fast" or the
  number. "Significantly improves" becomes the measured change.
- **`fancy-word`**: "utilize" and "leverage" → "use". "Facilitate" → "help". "Numerous" → "many".
  "In the event that" → "if".
- **`mannered-prose`**: a flourish where a literal phrase exists: aphorisms ("wire it or delete
  it"), fragments for effect, personified code ("the plan holds it"), figurative verbs ("rides
  along"), and stock framing phrases. Say what you mean.
- **`over-compression`**: dropped articles, verbless fragments, arrows, and abbreviations that make
  the reader decode. "Parser rejects bad date → exit 2, no write" becomes "The parser rejects a bad
  date, exits with code 2, and writes nothing." Exceptions: table cells, argument hints, and
  command comments may stay compact.
