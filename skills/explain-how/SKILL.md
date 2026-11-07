---
name: explain-how
description: Explain how code or infrastructure works today, at the level a senior engineer needs to start working in it: a subsystem, a runtime flow, a request path, or where something should live. Read-only. Haiku explorers trace complex areas, the main agent explains. Triggers on "/explain-how", "how does X work", "walk me through X", "where should this live", or "which layer owns this". Optional leading level. Use explain-why for the reasons.
argument-hint: "[lite|deep] <question>"
disable-model-invocation: true
---

# explain-how

Answer "how does X work?" with a mental model, not annotated source. **Read-only. Never edit,
apply, or start anything.**

`explain-how` says what the code or the infra does now. `explain-why` says why it is that way.
`teach` runs one or both and turns the result into a plain explanation.

Inspired by the pstack `how` skill, adapted to run on cheaper models and to cover infra.

## Level

Read the first argument:

| First argument | Level | Exploration | Explanation |
|---|---|---|---|
| `lite` | lite | Main agent reads the code itself | Main agent |
| none, or anything else | default | None for a simple question. 2–3 Haiku explorers for a complex one | Main agent |
| `deep` | deep | 2–4 Haiku explorers | One Opus explainer at `high`. The main agent presents its answer |

Do not run `/effort` or `/model`. Set `model` and `effort` on each Agent call only. Never go above
Opus `high`.

## 1. Size the question

If the scope is unclear, state your reading in one line and continue. The user can redirect.

- **Simple**: one module, one function, one resource, a small utility, or a narrow question such
  as "how does `retryFetch` work". Read it yourself and go to step 3, at every level except
  `deep`.
- **Complex**: a subsystem across several files, services, or repos. A cross-cutting feature. A
  request path through infra (DNS → Cloudflare → proxy → container → app). A full overview. Go
  to step 2.

When in doubt, take the simple path.

## 2. Explore (complex only)

Split the question into 2–3 angles (up to 4 in `deep`). Each angle is a distinct slice, for
example:

- software: entry points and triggers, the core data flow, state and storage, error and retry
  paths, the boundary to other services.
- infra: the request path, the deploy path (CI → image → host), state and backups, networks and
  names, secrets and IAM.

Launch every explorer in **one message**:

- `subagent_type`: `Explore`, `model`: `haiku`, `run_in_background`: `false`.
- Prompt: the full text of [`references/explorer-prompt.md`](references/explorer-prompt.md),
  with the question, the angle, and the absolute repo root filled in.

**lite**: skip the explorers. Read what the question needs yourself.

After the explorers return, read the files they name as load-bearing yourself. Their report
locates. It does not prove. Where two explorers disagree, check the code and settle it.

## 3. Explain

**lite and default**: write the explanation yourself, in the format of
[`references/explainer-prompt.md`](references/explainer-prompt.md).

**deep**: launch one explainer:

- `subagent_type`: `general-purpose`, `model`: `opus`, `effort`: `high`,
  `run_in_background`: `false`.
- Prompt: the full text of `references/explainer-prompt.md`, with the question, the repo root,
  and every explorer's findings filled in. Tell it that it is read-only and must not edit files.

Present its answer. Light edits for clarity or for context from this conversation are fine. Do
not rewrite it.

## Output

The sections from `references/explainer-prompt.md`, with any that do not apply left out:
**Overview**, **Key concepts**, **How it works**, **Where things live**, **Gotchas**. End with
**Open questions** when the trace has gaps.

Diagrams are ASCII, because Mermaid does not render in the terminal. Draw one only when it lands
faster than words. When the user asks for a page, or wants it taught step by step, offer
`/teach`.

## Rules

- Read-only. Never commit, apply, deploy, or run commands with side effects on remote systems.
- Every claim about behavior points to a `file:line`, a resource address, or a command output.
- Say what the code does. Leave motivation to `explain-why`. "The retry is there because…" without
  a source is a guess.
