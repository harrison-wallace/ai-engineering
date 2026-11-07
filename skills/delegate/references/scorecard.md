# Scorecard

Grade **the execution of the plan** — never the plan itself. If the plan asked for a mediocre
design and the implementer built exactly that, cleanly, it scores high. The point is to isolate one variable:
what the implementer does with instructions. A weak plan is a phase-1 problem and has no effect on any number
here.

Score each dimension 1–5 against the anchors below. The plan is the yardstick throughout.

| Dimension | 1 | 3 | 5 |
| --- | --- | --- | --- |
| **Fidelity** | Planned changes missing or landed somewhere else | Most of the plan landed; a file or requirement skipped or reinterpreted | Every planned change present as specified, nothing outside the plan's surface area |
| **Bloat** | Substantial code untraceable to any plan line — speculative abstraction, unrequested config, dead paths | Some unasked-for scaffolding: a wrapper with one caller, defensive handling for what cannot fail, a helper used once | Minimal diff. Every line traces to a plan line |
| **Correctness** | Does not do what the acceptance criteria describe, or breaks existing behavior | Works on the main path; edge cases, error paths, or resource handling are wrong or absent | Behavior matches the criteria including the unhappy paths |
| **Security** | Introduces an exploitable flaw (injection, path traversal, leaked secret, unsafe subprocess) | Works but handles untrusted input, secrets, or paths loosely | No new exposure; untrusted input and secrets handled correctly |
| **Maintainability** | Reads as foreign code — alien naming, structure, or comment density; hard to follow | Functional but inconsistent with the surrounding files | Indistinguishable in style and structure from code already in the repo |
| **Verification** | Acceptance criteria fail, or were never runnable | Criteria pass but nothing was added where the repo tests this kind of change | Criteria pass and tests exist to the standard the repo already keeps |

Rules that make the number mean something:

- **Evidence or it does not count.** Every score below 5 cites a `file:line` from the raw diff or
  the output of a command you ran. The implementer's report is a claim, never evidence.
- **Mark Security `N/A`** when the diff touches no input handling, secrets, paths, or subprocess
  calls. Do not manufacture a score to fill the row.
- **5 is rare** — it means there is nothing you would change. A run with fixes pending does
  not have a 5 on the dimension those fixes address.
- **The headline is the lowest scored dimension**, not the mean. A well-tested, elegant
  implementation of the wrong thing is not a 4.

Report as a compact table (dimension, score, one-line evidence), then the headline as
`**Overall: N/5**`.

Score each implementer separately. For a split route, score each one on its own unit. For
`a/b`, score both sides, then compare them in one table with a column per side.

Optionally append one line per implementer to `<repo-root>/.imp-scorecard.log` if that file
already exists: the date, the route, the model with its effort (such as `sonnet/medium` or
`grok-4.7/high`), the task, the six scores, and a one-line failure note. The file keeps its old
name, so that runs from the `imp-*` skills stay comparable. Do not create the file unprompted.
