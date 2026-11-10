# Epistemics

## Contents

- [Confidence tiers](#confidence-tiers)
- [Wording](#wording)
- [Memory and repo instructions](#memory-and-repo-instructions)
- [Do not rationalize](#do-not-rationalize)
- [The leading question](#the-leading-question)
- [When sources disagree](#when-sources-disagree)
- [When evidence is missing](#when-evidence-is-missing)
- [Before you finish](#before-you-finish)

How to rate confidence when the evidence is old, partial, and sometimes contradictory, and how to
say it without turning it into false certainty. Code shows what it does, not why it exists. The
why lives in commits, PRs, issues, ADRs, phase docs, changelogs, and notes. All of them are
incomplete, and some are missing.

## Confidence tiers

Every claim sits in exactly one tier. The tier sets its section and its wording.

### 1. Direct

Someone **wrote** the reason down. Examples: a PR body "this fixes pagination for users with more
than 1000 items". An ADR "we chose option A over B because we need persistence across restarts". A
code comment "clamp to 100 because the upstream API rejects larger values". A memory note that
quotes the user's reason.

Wording: plain, present tense, cited. "This exists because X (PR #123)."

### 2. Supported

Several pieces of indirect evidence point the same way. None says it outright. Example: the PR
title says "improve performance", the changelog entry says "faster startup", and the commits
around it all touch the same hot path.

Wording: confident but visibly derived, citing each piece. "The evidence points to X: A, B, C."

### 3. Inferred

A reasonable reading that nothing states. It is your interpretation, not a record. Example: the PR
gives no reason, but it merged the same day as a revert of the old approach, so it was likely a
quick fix.

Wording: hedged, with the chain shown. "Given A and B, C seems likely, because D."

### 4. Speculative

A plausible idea on thin evidence, where other ideas fit as well. Worth showing, since the user may
know which is right. Mark it as a guess.

Wording: "One possibility is X, but we found no direct evidence." It usually goes under Competing
hypotheses.

### 5. Unknown

You looked and could not find out. This is a valid and important result.

Wording: "We searched X, Y, and Z and found no reason." Say exactly what you searched: "We read the
6 commits that touched this file since 2025, the 2 PRs they link, and `docs/adr/`, and grepped the
repo for `100`. None gave a reason."

## Wording

**Confidence words** claim Direct or Supported evidence and need a citation right next to them:
"because", "the reason is", "was designed to", "fixes", "solves", "we decided".

**Hedges** mark interpretation. Use them in What we can infer: "appears to", "seems to", "likely",
"suggests", "is consistent with", "may have been".

**Do not use**: "obviously", "clearly", "of course", "just" (as in "it's just for performance"),
"I think", "I believe". Say "the evidence suggests" instead.

## Memory and repo instructions

Memory files and `CLAUDE.md`/`AGENTS.md` record what was true when someone wrote them. Treat a
reason they quote as Direct for the time it was written. Check it against git when you can. When
the code has moved on since the note, say so, and do not carry the old reason forward as current.

## Do not rationalize

Code that makes sense today may exist for reasons that no longer apply, or that were wrong at the
time. Do not fit a clean reason onto messy history. Do not assume the author did the right thing
and work back from it. Do not assume a repeated pattern was a choice. It may be copy-paste. No
mention of a concern is not evidence that there was no concern.

## The leading question

Users often put a guess in the question: "Why do we do it this way? I assume it's for
performance." Do not just confirm it. Treat it as one candidate and test it against the evidence.
If the evidence supports it, say so with citations. If it does not, say so, and show what the
evidence does support.

## When sources disagree

Show both, with citations. Do not pick the one that makes the tidier story. Both may be true (the
issue gave the motivation, the PR gave the author's framing), or one may be wrong. Let the user
decide.

## When evidence is missing

Say so plainly. The user then knows the answer is not in the obvious places, and can ask a person
or drop the question. Filling a gap with a confident guess harms the user, because they act on it.
Name each gap: the question, the sources searched, what you searched for in each, and what you
found.

## Before you finish

Check every claim in What we found and What we can infer:

- It has a citation, or it moves down a tier.
- Its wording matches its tier.
- It does not use the code as evidence of its own intent.

The answer has a What we don't know section. If it names no gaps, be suspicious. Either the
evidence was unusually complete, or something is being hidden.
