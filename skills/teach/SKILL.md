---
name: teach
description: Explain a change, a subsystem, or a piece of infra so the user actually understands what it is, how it works, and why it is built that way, at their pace, in plain spoken English. Runs explain-how and explain-why and weaves the result into one account, small answer first, deeper on request. Diagrams build up one part at a time, in ASCII, or on a LAN page for three or more parts. Read-only. Triggers on "/teach", "teach me this", "help me really understand X", "explain this change to me", or "teach me what Sonnet just built". Optional leading level.
argument-hint: "[lite|deep] <what to teach>"
disable-model-invocation: true
---

# teach

Explain what a thing is, how it works, and why it is that way, in one plain account at the
user's pace. **The goal is that they understand it. Do not change anything.**

`teach` sits on top of `explain-how` (how it works) and `explain-why` (why it is that way). They
do the digging. This skill picks what matters, blends the two, and teaches it.

Inspired by the pstack `teach` skill.

## Level

Read the first argument: `lite`, `deep`, or neither (default). Pass the same level to `explain-how`
and `explain-why`. Their own Level tables say what each level spends. Do not run `/effort` or
`/model`.

## 1. Pick the takeaways

Decide the two to four things the user should come away understanding. Do not print them. Choose
from the conversation, not from a quiz:

- **Why they ask**: about to change it, reviewing it, debugging it, or new to it.
- **What they already know**: skip that. Put the depth where their question is.

## 2. Get the material

Read the code yourself first, enough to get your bearings: what the work is and what it touches.
For a change, read the diff (`git diff`, a commit, or what was just built in this session).

Then run the sibling skills. They have `disable-model-invocation`, so do not call them with the
Skill tool. Read their files and follow them in place:

- `../explain-how/SKILL.md` and `../explain-why/SKILL.md`, relative to this skill's folder. Resolve
  the folder with `readlink -f` if it is a symlink.

Size the work to the question:

| Question | Run |
|---|---|
| A small change or one function | `explain-how` only, often at `lite` |
| A subsystem, a flow, or infra with several parts | Both |
| "Why is it like this?" is the point | `explain-why` at full level, and `explain-how` at `lite` for context |

Keep `explain-why` narrow by default, since its digging is the slow part. Put the narrowing in the
question you hand it: one decision, one value, or one symbol, not the whole history. When the
reasons are only a side note, run it at `lite`. Its Sources consulted line then records what was
skipped.

When both run, launch their subagents in **one message**: the `explain-how` explorers and the
`explain-why` digger together. Do each skill's main-agent steps (the anchor, the in-repo sweep) before
that message.

Do not redo their work. Reword freely for teaching, with one exception: **keep `explain-why`'s
confidence words and tiers as they are.** Its hedges are findings, not style.

## 3. Teach

**Start with a plain definition.** Name the thing and say what it is in general terms, the way a
senior engineer would say it out loud, with its common name if it has one. Then tie it to the case
in front of you ("here, we use this to…"). Build from there: how it works, then the reasons, then
the edge cases.

For each part, explain the idea so it clicks: the problem it solves and how it actually works.
When it helps, walk through what happens as the user does the thing (sends a request, runs the
deploy, opens a long chat). A list of functions and constants is reference, not teaching.

**Give the smallest complete answer first**: a sentence or two, not a dense paragraph, plus the
first diagram if one helps. Then stop. Add layers when the user asks. Never a wall of text.

When the user is about to change the thing and `explain-why` produced a Preserve / Change / Avoid /
Risk set, end the first answer with it, in its table form.

## 4. Keep it a conversation

Offer to go deeper or move on, in one line, and follow the user's lead.

No quizzes. No pacing theatre. Do not print "Pause". Do not ask them to say it back. Do not flag a
part as important or hard ("this is the tricky part", "here is where it gets interesting"). Just
say it. Where you would pause, stop and let them reply.

When no one is live (a one-shot or unattended run), deliver it cleanly and put the offer to go
deeper at the end.

## 5. Show, and build the picture up

Open the diff, the code, or a command's output when that is the fastest way to land a point. Draw
when a picture lands faster than words. A single simple point needs no figure.

**Build diagrams up one part at a time.** For anything with three or more moving parts, do not draw
one diagram with everything at once. Draw a short series. Each diagram redraws the last and adds one
part, so the user watches the system assemble. To teach a flow from A to B to C: first A to B, then
redraw and add C, then redraw and add the return edge or the next piece. One all-at-once diagram,
especially one saved for the end, is a reference, not teaching.

Where the diagrams go:

- **One or two parts**: ASCII in the reply.
- **Three or more parts, or when the user asks for a page**: a LAN page holding the whole series,
  one frame per step, each with a one-line caption. Read `../serve-page/SKILL.md` (relative to
  this skill's folder, resolved with `readlink -f`) and follow its §1 to §4. Write the page to
  `<scratchpad>/teach/<slug>/index.html`. When the user asks to go deeper, add frames to the same
  file, and the same server shows them on reload. The reply still holds the plain answer, the
  first frame in ASCII, and the URL. Stop the server when the user says they are done.

## Voice

Plain spoken English, the way you would explain it to a colleague. Tight, not terse. Cut filler and
hedging, but keep the part that makes it click.

- State the concrete mechanism, not a metaphor, a framing, or a preview of what is coming. Target
  density: "Virtualization runs in two parts, one for rendering and one for loading from disk.
  When an item scrolls out past the buffer, both its DOM node and its in-memory data are evicted."
- Sentence case. No em dashes. Prefer periods to commas. One or two commas per sentence at most.
  When clauses pile up, split them.
- One name per concept, kept all the way through.
- No mirror sentences ("A without B, or B without A"). No tidy closers ("the rest follows", "it all
  falls out").
- No framing labels: "the key insight", "the one idea to hold onto", "the thing to walk away with",
  "at its core", "TL;DR".
- The words in these steps are directions to you. Do not echo them as headers or stock phrases.

## Reply

The explanation itself, never a report about what you did. Lead with the main point. Then the plain
account of what it is, how it works, and why. Then, in one line, the threads worth chasing with
`/explain-how` or `/explain-why`, and the offer to go deeper.

When the work has a concrete result (a number, a before-and-after, a proved cause, a release),
end with one line, at most once a session: `> Postable: <the specific>. Want /showcase pitches?`

## Rules

- Read-only, apart from the LAN page in the scratchpad. Never edit the repo, commit, apply, or
  deploy.
- Every claim about behavior traces to `explain-how`'s citations. Every claim about reasons keeps
  `explain-why`'s tier.
