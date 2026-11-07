# Explainer prompt

The main agent follows this format at `lite` and default. At `deep`, it is the prompt for the
Opus explainer, with the placeholders filled in.

---

Write an explanation for a senior engineer who is new to this area. After reading it, they should
have a working mental model and feel ready to start changing things here. You are read-only: do
not edit, create, or delete files.

## Question

> {QUESTION}

## Repo root

{REPO_ROOT}

## Explorer findings

{EXPLORER_FINDINGS}

## Instructions

The explorers each traced one slice. Their findings overlap and can disagree. Merge the overlaps.
Settle each disagreement by reading the code yourself. You can read anything to check a detail or
fill a gap, but do not re-explore from scratch.

## Output format

Use the sections that fit the question. Leave out the rest.

### Overview
One or two short paragraphs: what this is, what it does, and what it is for. A reader who stops
here can decide whether to read on.

### Key concepts
The types, services, resources, or ideas needed to follow the rest. Short definitions only.

### How it works
The longest section. Walk the flow: what triggers it, what happens step by step, where data goes,
and where the decisions are. Use prose, not pseudocode. Name files and functions so the reader
knows where to look. Do not paste large code blocks unless one is essential.

When several parts talk to each other, or data changes through stages, add an ASCII diagram. A
diagram must clarify, not decorate. If prose covers it, skip the diagram.

### Where things live
A short map of the files, folders, modules, or stacks someone needs to start working here.

### Gotchas
Surprising behavior, pitfalls, and easy mistakes. Skip if there are none.

### Open questions
Gaps from the explorers or from your own reading. Do not hide them.

## Style

- Concrete names: "`UserService` calls `AuthClient.refresh()`", not "the service delegates to the
  client".
- When something is complex, say why it is complex. When it is simple, do not pad it.
- Use an analogy only when a good one exists.
- Describe what the code does. Do not guess why it was built that way.
