---
name: prototype
description: Build throwaway code that answers one design question that talk cannot settle. `logic` builds a self-contained HTML demo in docs/prototypes/ that drives a pure state module through free-play buttons and guided walkthroughs. `ui` builds 3–5 structurally different variants on an existing route behind `?variant=`, with a floating switcher, on a `prototype/<slug>` branch. `page` serves the demo, or a desktop and phone screenshot comparison of the variants, on the LAN. The answer goes into a short ADR (or into the proposed ADR of the `design` run that asked), the UI variants are deleted, and it offers `/delegate` for the proper build. Never commits. User-invoked only, through "/prototype".
argument-hint: "[logic|ui] [page] <question>"
disable-model-invocation: true
---

# prototype

Build **throwaway code that answers one question**, record the answer, then throw the code away.
**Never commit.**

Adapted from Matt Pocock's `prototype`.

Not for: the shape of a system (who owns the state, the interfaces, the modules, `design`), a
design that is already settled (`delegate`), or a demo of a whole app. A whole app is not one
question.

## Where it sits next to `design`

`design` decides a shape by reading the code and judging sketches. `prototype` settles one question
about behaviour or look by running it. When a `design` run has a question that talk cannot settle,
it offers `/prototype`, and the answer goes back into its proposed ADR (§5).

## 1. Question and branch

Read the arguments. `logic` or `ui` picks the branch. `page` turns on the page (§4). The rest is
the question.

1. **State the question in one sentence.** For example: "Can a booking be cancelled after a
   partial refund?" or "Does the settings page read better as tabs or as one long form?"
2. **Check that talk cannot settle it.** If one message can answer it, answer it, and stop.
3. **Pick the branch** when no argument names it. A state model, a reducer, a data shape, or
   rules between events → `logic`. A page, a component, or a flow on screen → `ui`. Say which, and
   why, in one line.
4. **Find where the answer goes.** When this chat has a `design` run with a `proposed` ADR, or the
   user names one, the answer goes into that ADR. Otherwise, a new short ADR.
5. **Record the baseline.** Save `git status --short` to `<scratchpad>/prototype/<slug>/baseline.txt`
   before you write anything. §6 compares against it.

**Done when** the question, the branch, and the ADR target are each one line, and the user saw
them.

## 2. Build

- `logic`: follow [`references/logic.md`](references/logic.md).
- `ui`: follow [`references/ui.md`](references/ui.md).

Both branches keep these rules:

- **No polish.** No tests, no error handling beyond what makes it run, and no abstractions. It
  answers one question.
- **No persistence.** State lives in memory. If the question is about persistence, use a scratch
  database or a local file named `PROTOTYPE-wipe-me`.
- **Show the state.** After every action or every variant switch, show the full state that the
  question depends on.
- **One sitting.** If it is not answered in one sitting, the question was too big. Stop and split
  it.

## 3. Hand over

Give the user the way to run it: the file path for `logic`, or the URL and the `?variant=` keys
for `ui`. Then stop.

The useful feedback is "wait, that should not be possible", "I assumed X", or "the header from B
with the list from C". For a new action, scenario, or variant, add it and hand over again.

**Done when** the user states the answer.

## 4. Page (with `page`)

Read `../serve-page/SKILL.md` (relative to this skill's folder, resolved with `readlink -f`) and
follow it.

- `logic`: serve `docs/prototypes/<slug>/index.html` with `/serve-page <file>`.
- `ui`: build the screenshot comparison in [`references/ui.md`](references/ui.md) §6, and serve
  it.

Stop the server when the user states the answer.

## 5. Record the answer

**Into a `design` ADR** that is still `proposed`: add the question and the answer under its open
questions or its decision, in its own style. Do not write a second ADR.

**Otherwise**, draft a short ADR in the format of `../define-terms/references/adr-format.md`:

- The title is the answer, as a short phrase.
- The body gives the question, the answer, and why.
- **Considered options** names the variants or the models that lost, with one line each on why.
- For `logic`, link `docs/prototypes/<slug>/index.html` as the evidence.

Show the draft and its file name. Write it after the user says yes.

## 6. Clean up

- `logic`: keep `docs/prototypes/<slug>/index.html`. Delete nothing else, because nothing else was
  written.
- `ui`: follow [`references/ui.md`](references/ui.md) §7. Every variant, the switcher, and the
  branch go. Main keeps only the ADR.

**Done when** `git status --short`, compared with `baseline.txt`, adds only the ADR and the logic
demo. Show any other new or changed path, and stop.

## 7. Next

- From a `design` run: go back to its sign-off. The fold-in goes through `/phase shape`.
- Otherwise: offer `/delegate` to build the winner properly. Prototype code was written with no
  tests and minimal error handling, so the fold-in is a rewrite, not a copy. For `ui`, offer
  `/check-ui-tells` on the result after it lands.

## Rules

- Never commit, push, or merge. Never commit on the `prototype/<slug>` branch.
- Never point a prototype at a real mutation, a shared database, or a live service. Use stubs.
- Write the reports and the ADR in ASD-STE100 Simplified Technical English: short active
  sentences, one idea in each, the same word for the same thing. Use the terms from `GLOSSARY.md`
  when the repo has one.
