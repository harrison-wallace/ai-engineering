---
name: design
description: Design the shape of a new feature, service, or component before code — software, infrastructure, or both. Ground in the real system, sketch two structurally different designs with cheap Sonnet runners, screen them against red flags, write a proposed ADR in docs/adr, then stop for sign-off and offer /phase shape. Triggers on "/design", "architect this", "design this first", or non-trivial work where jumping to code or IaC would lock in the wrong shape. Optional leading level.
argument-hint: "[lite|deep] <what to design>"
disable-model-invocation: true
---

# design

Decide the shape before writing the code or the IaC. **Ground → sketch twice → screen and
merge → write the ADR → stop for sign-off.** Implementation is not part of this skill. After
sign-off, offer `/phase shape`, and the work goes through the normal slice flow.

Inspired by the pstack `architect` skill. Same core ideas, run on cheaper models, with
infrastructure as a first-class domain.

## Level

Read the first argument:

| First argument | Level | Grounding | Runners |
|---|---|---|---|
| `lite` | lite | Main agent reads the code itself | None. The main agent sketches both candidates inline, briefly |
| none, or anything else | default | 1–2 Haiku Explore agents | 2 Sonnet runners at `medium` effort |
| `deep` | deep | 1–2 Haiku Explore agents | 2 Sonnet runners at `medium`, plus 1 Opus runner at `high` |

The main agent (this session) does the judgment work in every level: it reads the grounding,
screens and merges the candidates, and writes the ADR. Do not run `/effort` or `/model`. Set
`model` and `effort` on each Agent call only. Never go above Opus `high` anywhere.

Do not use this skill for bug fixes or "add X like the existing Y". If the request is that small,
say so in one line and offer to just do it.

## Start

Open a todo list: Ground, Sketch, Screen, ADR, Sign-off.

Classify the domain from the request and the repo, and state it in one line:

- **software**: application code, libraries, APIs, data models.
- **infra**: Terraform, compose, Helm, CI/CD, networking, IAM, backups, hosts, DNS, Cloudflare.
- **both**: anything that touches both, such as a new module that needs a new volume, backup, or
  route. Use both sets of red flags.

## 1. Ground

Build a real picture of every system the new work touches. Naming a file is not grounding.

**default and deep**: launch Haiku Explore agents in parallel, one per domain when the domain
is `both`, else one:

- `subagent_type`: `Explore`, `model`: `haiku`, `run_in_background`: `false`.
- Prompt: the request, the repo root, and this ask: *"Map what the new work touches. Return,
  with file paths: the modules, resources, or services involved; who owns (writes) each piece of
  state, resource, or config; the public interfaces, module variables and outputs, or ports
  between them; the conventions a new piece must follow (cite one existing example of the
  nearest similar thing); and anything that looks like an existing constraint. Report facts
  with paths, not recommendations. At most 400 words."*

**lite**: do the same reading yourself, limited to what the decision needs.

Then, in every level:

- Read the files the explorers name as load-bearing yourself. Their report locates. It does not
  prove.
- Read the `docs/adr/` index, or list the folder if there is no index. Note the accepted ADRs that
  bind this design, and any ADR this design would supersede.
- For infra, note what is live today if the repo records it: state files, compose files on the
  host, runbooks. The design starts from the current state, not from nothing.

Write a **grounding brief** to `<scratchpad>/design/<slug>/grounding.md`. Keep it under
one page. Every runner receives this brief. Open it with an **alignment block**, in the
`restate-ask` shape and in short plain sentences:

- **Goal:** one sentence. **Problem:** one or two. **Done looks like:** one or two.
- **Scope:** In and Out. **Constraints I heard:** where it runs, gates, and safety lines.
- **Unclear words:** only the readings that change the meaning, such as dictation slips with two
  plausible meanings.
- **Assumptions:** numbered, each answerable with yes or no.

Then: domain, systems touched with their owners, binding constraints and ADRs, the nearest
existing example, and the current live state for infra.

Skip grounding only for true greenfield work with nothing to integrate with, and say so.

## 2. Sketch twice

Need at least two **structurally different** candidates, even if the first looks fine.
Different overall shapes, not tweaks inside one shape. Runners run on the same model family, so
each gets a forced starting premise:

| Runner | Premise |
|---|---|
| **A: extend** | The smallest change that fits the current structure. Reuse the existing owners, modules, and stacks. |
| **B: reshape** | Design the touched area as if this requirement had been there from day one. Move ownership or boundaries if that gives a deeper, simpler interface. |
| **C: invert** (deep only) | Put the decision somewhere else: a different owner of the state, push and pull swapped, a managed service against self-hosting, or "an existing thing already covers most of this". |

**default and deep**: launch every runner in **one message** so they run in parallel:

- A and B: `subagent_type`: `general-purpose`, `model`: `sonnet`, `effort`: `medium`.
- C: `subagent_type`: `general-purpose`, `model`: `opus`, `effort`: `high`.
- `run_in_background`: `false`.
- Prompt: the full text of [`references/runner-prompt.md`](references/runner-prompt.md), then
  the runner's premise, the path to the grounding brief, the domain, the red-flag file path
  ([`references/red-flags.md`](references/red-flags.md)), and the output folder
  `<scratchpad>/design/<slug>/candidate-<a|b|c>/`.

Runners write only inside their output folder. They never edit the repo.

**lite**: write candidates A and B yourself in the same folders, at a fraction of the depth:
usage, core types or resources, ownership map, and three lines of rationale each.

## 3. Screen and merge (main agent)

Read every candidate in full. Then:

1. **Screen** each candidate against [`references/red-flags.md`](references/red-flags.md): the
   software section, the infra section, or both. A red flag means revise or reject. Do not trust
   a runner's self-screen.
2. **Compare** the candidates that are left:
   - Interface depth: the most capability behind the smallest public surface (functions, module
     variables, ports, env vars).
   - Ownership: one owner per piece of state and per resource.
   - The next-contributor test: the next contributor is an agent that sees only the files it
     opened and copies the nearest example. Prefer the design where a change that looks right
     from one file is right for the whole repo.
   - For infra: migration cost from the current live state, the rollback path, blast radius, and
     running cost.
3. **Merge**: pick a base, take specific parts from the others, and record what you rejected and
   why. If every candidate fails the screen, fix the best one yourself. Do not re-run the
   runners unless the grounding was wrong.
4. **Check the sketch** where it is cheap and read-only. Run these in the scratchpad copy only:
   - TypeScript: `tsc --noEmit` with the repo's config, or a nearby equivalent.
   - Terraform: `terraform fmt -check`, `terraform validate`.
   - Compose: `docker compose config`.
   - **Never** `apply`, `up`, `deploy`, or anything that changes live resources. Run `terraform
     plan` only in a directory that is already initialized, and only when the user asks.

Write the merged sketch to `<scratchpad>/design/<slug>/final/`.

## 4. Write the ADR

Write it into the repo's `docs/adr/`. Create the folder if it is missing.

- **Number**: the next free number in the folder. If no ADRs exist, start at `0001`.
- **Format**: if the folder has a template (`0000-template.md` or similar) or existing ADRs, copy
  their headings, their status line, and their prose style exactly. Add the sections from
  [`references/adr-sections.md`](references/adr-sections.md) that the template does not already
  cover, as subsections under the nearest heading. With no template, use `adr-sections.md` as it
  is.
- **Status**: `proposed`, today's date.
- **Index**: if `docs/adr/README.md` has an index table, add the row.
- If this ADR supersedes an earlier one, say so in the new ADR only. Change the old ADR's status
  only after sign-off.

Sketch files stay in the scratchpad until sign-off. The ADR states the shape in prose and in
short code or HCL excerpts. The full stubs live in `final/`.

## 5. Sign-off

Stop and report:

- **Read as**: the alignment block's Goal, Scope, and Done in three lines, plus any unclear-word
  readings. This comes first, so a misread ask is caught before the user reads the design.
- **Decision**: the shape in two or three sentences.
- **Candidates**: one line each. Say which became the base, and what was taken from or rejected
  in each.
- **Red flags**: the ones that fired, and how each was resolved.
- **Files**: the ADR path, and `<scratchpad>/design/<slug>/final/`.
- **Questions**: a numbered list, from the alignment assumptions that still matter and the ADR's
  open questions. Phrase each one so a short answer
  ("1 yes 2 no") settles it. When a question is about how a state model behaves or how a screen
  looks, and talk will not settle it, mark it `prototype`. Offer `/prototype <question>` for it.
  Its answer goes into this ADR while the ADR is still `proposed`.

Then offer, in one line: *"Sign off and I'll mark the ADR accepted and run `/phase shape <slug>`
with the sketch as slice 1. Or reply `page` to compare the candidates side by side on your LAN."*

Wait for the user.

### Page (on request)

When the user replies `page`, read `../serve-page/SKILL.md` (relative to this skill's folder, resolved with `readlink -f`) and follow its §1 to §4. Write `<scratchpad>/design/<slug>/page/index.html`.
The page shows:

- **Read as** and **Decision** at the top.
- **One column per candidate** (A extend, B reshape, and C invert on `deep`), side by side: its
  usage example, its ownership map as a diagram (who owns each piece of state or each resource),
  what its interface hides, and the red flags it raised. Mark the base candidate, and what the
  final shape took from each of the others.
- **The final shape** as one diagram, with the ADR path.
- **Questions**, numbered as in the reply.

Stop the server on sign-off, on pushback that re-runs the sketches, or when the user says they are
done. A re-run rebuilds the page in the same folder, on the same port.

### On sign-off

1. Set the ADR status to accepted in the repo's format (for example `accepted (owner,
   YYYY-MM-DD)`), add the answers to the open questions, and update the index row. Mark any
   superseded ADR now.
2. If the user accepted the offer, run `/phase shape <slug>`. Feed it the ADR and the sketch.
   Make slice 1 "land the sketch": stubs, types, module variables and outputs, with no behavior.
   Put this **design contract** into the phase doc as it stands:

   > **Design contract (ADR NNNN).** The sketch is the contract. A change it did not anticipate,
   > such as a new parameter, a new resource, or a second writer, is a signal to raise, not to
   > absorb silently. Ask whether the sketch was wrong, a requirement was missed, or the
   > implementation is overreaching. If the same shape of friction appears twice in unrelated
   > places (repeated workarounds, type escape hatches, special-case branches, a lock the sketch
   > said was unneeded, callers that need to know internals, resources managed in two places),
   > stop and re-run `/design` on the affected area. Do not bolt fixes onto a wrong
   > shape. The new sketch must be smaller than the old one before it grows.

### On pushback

If the user rejects the shape, treat the objection as new grounding. Add it to the brief, then
re-run only the steps it invalidates: usually Sketch onward, sometimes Ground. Update the same
ADR in place while it is still `proposed`.

## Rules

- Never commit. Leave the ADR uncommitted for the user.
- Never change live infrastructure, and never run commands with side effects on remote systems.
- Subagents start cold. Give them absolute paths, the grounding brief, and the exact output
  folder. Ask runners to read the brief, not to re-explore the repo.
- Keep the ADR to the length the decision needs. A small decision gets a short ADR.
