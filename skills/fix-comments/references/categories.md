# Comment categories

## Contents

- [How to sort](#how-to-sort)
- [stale](#stale)
- [excuse](#excuse)
- [tautology](#tautology)
- [adr](#adr)
- [keep](#keep)
- [unsure](#unsure)
- [Never delete](#never-delete)

## How to sort

Read each comment with the code around it: the whole function, or 15 lines each side. Ask the
questions in this order, and stop at the first yes. Each category name is the value you write
in the `category` column.

1. Is it false now, or does it only tell history? → `stale`
2. Does it excuse a shortcut in the code? → `excuse`
3. Would a reader lose nothing if it were gone? → `tautology`
4. Does it record a decision that passes all three ADR tests? → `adr`
5. Does it say a true, local *why* that the code cannot show? → `keep`
6. None of these, or you cannot prove one → `unsure`

## stale

The comment is not true of the code now, or it tells the past instead of the present.

- It names a function, file, flag, env var, table, or endpoint that no longer exists. Prove it:
  `rg -n -w '<name>'` finds no definition.
- It describes behaviour the code next to it does not have ("returns null", and it throws).
- It is commented-out code. Git keeps the old version.
- It is history: when or why the code arrived, not what is true now. "Phase 6: extracted
  modules", "added in 2.10.0", "per ticket ABC-123", "moved from utils.py", "new approach".

A stale comment whose *why* is still true is not stale. Sort it on that *why* (`adr` or
`keep`), and say in the reason column what part is out of date.

**Action:** delete.

## excuse

The comment lets a shortcut stand: it names the problem but does not fix it.

- `TODO`, `FIXME`, `HACK`, `XXX`, "temporary", "for now", "quick fix", "workaround", "not
  ideal", "should never happen", "ignore this for now".
- A comment that explains away a cast, a swallowed error, a magic number, a copy-paste, a
  sleep, a retry loop, or a disabled check, when the code could be made right instead.

Test: if the shortcut were fixed, would the comment still be needed? No → `excuse`.

Not an excuse: a warning about a real trap the code must live with ("not thread-safe: call only
from the main loop"). That is `keep`. A workaround for a bug in a dependency, with a link to
the upstream issue, is also `keep`.

**Action:** delete. The report lists the shortcut under **Hacks to fix**, with the location,
what the shortcut is, and the proper fix in one line. That list is the only record, so word it
so that someone can act on it without the comment.

## tautology

The comment says what the code already says. A reader loses nothing if it is gone.

- It restates the next line: `// increment i`, `# set x to 1`, `// return the user`.
- It repeats a name: `// constructor`, `# imports`, `// User type`.
- A section banner over code whose names already say what it is: `# helpers ---------`.
- A doc comment that only repeats the signature: `@param id the id`.

If the comment says *why*, even in a few words, it is not a tautology. Go on to `adr` or `keep`.

**Action:** delete.

## adr

The comment records a decision, and the decision passes **all three** tests:

1. **Hard to reverse**: changing it later costs real work (a data format, a protocol, a
   dependency, a security or compliance rule, a public contract).
2. **Surprising without context**: a new reader would ask "why did they do it this way?"
3. **A real trade-off**: there were real alternatives, and this one won for stated reasons.

Fill the `extra` column with the decision as one short phrase. Comments that record the same
decision get the same phrase, so they become one ADR.

**Action:** after the user approves the ADR draft, write the ADR and replace the comment with a
one-line pointer to it.

## keep

A true, local *why* that fails at least one ADR test. It stays as it is.

- A constraint the code cannot show: "the gateway drops the first request after a cold start,
  so retry once".
- A warning about a trap: an ordering rule, a thread-safety limit, a unit, a side effect.
- A workaround for a dependency bug, with a link.
- A doc comment on an exported or public API that says more than the signature.

**Action:** none.

## unsure

You cannot prove the comment is stale, or you cannot tell whether a *why* is still true.

**Action:** none. The report lists it under **Not changed**, with what would settle it.

## Never delete

The script skips most of these. If one reaches you, sort it as `keep`:

- Tool directives: `eslint-disable`, `@ts-expect-error`, `# noqa`, `# type: ignore`, `//go:`,
  `# shellcheck`, `// prettier-ignore`, `#region`, coverage and lint ignores.
- Shebangs, encoding lines, modelines, license and copyright headers.
- Comments in generated or vendored files.
- Text inside a string, a template, or a test fixture or snapshot.
