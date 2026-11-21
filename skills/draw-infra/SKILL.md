---
name: draw-infra
description: Draw infra or software architecture as a diagram grounded in the repo's real files, on a LAN page. You write a JSON spec (parts, lanes, boundaries, edges, states, flows, modes), and a script does the layout, routing, and SVG, so no coordinate is guessed. The page has the full diagram with layer toggles, a dev/prod mode switch, a build-up stepper, one tab per flow (a packet runs along each step's hop, with its payload, and Play runs the steps), and a parts table. It writes the spec and a companion Markdown file to docs/diagrams/, and with `drawio` an editable draw.io file with AWS icons and a PNG check. Covers Docker hosts, AWS, Kubernetes, and app services (APIs, workers, queues, LLM calls, agents). Other skills (teach, phase, and any serve-page page) call its script instead of hand-drawing SVG. Never commits. Triggers on "/draw-infra", "/draw-infra <subject>", "draw the architecture", "diagram our infra", "draw how login works", or "show the request flow".
argument-hint: "[<what to draw> | <spec name>] [plain] [drawio] [from <doc>]"
---

# draw-infra

Draw what exists. **You write the spec. The script draws.** Never write an SVG coordinate by hand,
and never draw a guess as built.

Adapted from Alexey Vidanov's `aws-architecture-diagram` (layout checks, the companion file, the
render-and-look loop, the audience mode, the draw.io output with its AWS icons) and Konrad Dzbik's
`architecture-diagram` (click-through flows, the packet, the mode switch, the grounding rules).
Both are MIT.

## 1. Read the ask

| Ask | Subject |
|---|---|
| No subject | The repo's whole infra |
| A service, a subsystem, a stack, or a folder | That part, and what it talks to |
| A flow: "how login works", "what happens on upload" | The parts the flow touches, plus the flow |
| `from <doc>` | A design doc, an ADR, or a README. Its parts are `planned` unless the code has them |
| The name of a spec in `docs/diagrams/` | Refresh it: keep the ids, update the facts |

- `plain` → the audience is everyone ([spec.md](references/spec.md#audience)).
- `drawio`, or "for slides", "editable", "draw.io" → also write `docs/diagrams/<slug>.drawio`
  ([spec.md](references/spec.md#drawio)). Give AWS parts an `icon` and AWS boundaries a `kind`.
- Add [modes](references/spec.md#modes) when the ask compares shapes ("dev vs prod", "before
  and after the move"), or when the repo runs one system two ways (two compose files, a
  `docker-compose.override.yml`, per-env Terraform). Otherwise, no modes.
- Add flows when the subject is a flow, or when the user names scenarios. Otherwise, offer the
  two or three main flows in the report.
- The slug is the subject in kebab case, such as `checkout` or `infra`.

## 2. Ground it

Read [`references/spec.md`](references/spec.md) first.

- **Infra**: run `python3 -I <skill-dir>/scripts/infra-inventory.py <repo-root>`. Every built
  part comes from this list, or is `unconfirmed`.
- **App architecture**: find the entry points, routes, handlers, queues, stores, and outside calls.
  In a small repo, read them yourself. In a big one, launch 2 or 3 `Explore` agents in **one
  message**, `model: haiku`, one area each. Ask each one for parts and calls, each with
  `file:line`.
- **Flows**: read the handler for each step. A step you cannot find in the code goes in
  `assumptions`.

Ask only what you cannot default: which flows to draw, or who reads the diagram. Ask at most 3
numbered questions in one round, each with a recommended answer. Otherwise go on, and list what
you assumed in `assumptions`.

## 3. Write the spec

Write `docs/diagrams/<slug>.json` in the repo. For a refresh, edit the spec in place and keep
the ids. Follow every rule in `spec.md`: lanes and rows, one state for each part, a `source` on
each part, a flow step on a real edge, and no secrets.

## 4. Check and render

```bash
python3 -I <skill-dir>/scripts/diagram.py check docs/diagrams/<slug>.json
```

Fix every error and warning with the table in "Fix what check reports" in `spec.md`. Run it
again, up to 3 rounds. Report a warning that stays. Then:

```bash
python3 -I <skill-dir>/scripts/diagram.py page docs/diagrams/<slug>.json <scratchpad>/draw-infra/<slug>
python3 -I <skill-dir>/scripts/diagram.py md docs/diagrams/<slug>.json docs/diagrams/<slug>.md
```

For `drawio`:

```bash
python3 -I <skill-dir>/scripts/diagram.py drawio docs/diagrams/<slug>.json docs/diagrams/<slug>.drawio --png <scratchpad>/draw-infra/<slug>/drawio.png
```

**Done when** `check` prints `ok`, or only the warnings you will report, and the files exist.

## 5. Serve and look

Read `../serve-page/SKILL.md` (relative to this skill's folder, resolved with `readlink -f`), and
follow its §1 to §4 to serve `<scratchpad>/draw-infra/<slug>/index.html`.

When the Playwright MCP is loaded, open the page at 1440 and 390 wide. Screenshot the Diagram
tab and one step of each flow. Look for a label on a label, a label on a box, or an edge that is
hard to follow. Fix the spec (move a part to another row), and render again. Add `?v=<n>` to the
URL after a render, so the browser does not show the old copy. Without Playwright, skip this and
say so. With modes, look at each mode: click its switch.

For `drawio`, read each PNG the script printed. Look for an empty icon square, a label on a
line, or a box outside its group. Fix the spec and run `drawio` again. When the script printed
`warn:` instead of a PNG, say so in the report.

## 6. Report

```markdown
**<title>**: <n> parts, <e> edges, <f> flows. <url>

- Spec: `docs/diagrams/<slug>.json`. Notes: `docs/diagrams/<slug>.md`. draw.io: `docs/diagrams/<slug>.drawio`
- Modes: <the mode titles>
- Not confirmed: <parts in the unconfirmed state, each with where it was named>
- Assumed: <the spec's assumptions>
- Check: ok | <the warnings left>
```

Leave out the lines with nothing in them. If you drew no flows, end with: *"Add flows for <the
two or three main scenarios>?"* Stop the server when the user says they are done.

## Use from another skill

A skill that shows infra or architecture uses this script, and does not draw its own SVG:

1. Get the facts with `scripts/infra-inventory.py <repo>`. Write a spec by `references/spec.md`.
   A read-only skill writes the spec to its own scratchpad folder, never to the repo.
2. Run `scripts/diagram.py check <spec>`, and fix it.
3. Then do one of these:
   - **A page of its own**: `diagram.py page <spec> <dir>`.
   - **Inside the skill's own page**: `diagram.py svg <spec> --uid <unique id>` for each figure,
     and `diagram.py css` once in the page's `<style>`. `--upto N` draws the first N lanes, at
     their final positions, for a build-up frame. `--flow <id> --step <k>` draws one flow step.
     `--mode <id>` draws one mode of a spec with modes (the first by default).
     Each SVG comes in a scroll box that keeps it readable on a phone. The page defines the
     theme variables (`--bg`, `--fg`, `--muted`, `--line`, `--card`, `--accent`,
     `--accent-soft`, `--amber`, `--red`, `--ok`), as `page-rules.md` asks.

Today `teach` uses it for infra subjects and the phase page, `phase` renders `map.json` with
it (`render-board.py` imports `diagram.py`), and `serve-page`'s page rules send every page skill
here for infra and architecture figures.

## Rules

- Never commit, push, or stage. Write only `docs/diagrams/<slug>.json`, `.md`, and `.drawio`
  (on ask), and the page and PNGs in the scratchpad.
- A part that no file shows is `planned` (with its doc as the source) or `unconfirmed`. Never
  `built`.
- No secrets in the spec, the page, or the Markdown. `check` refuses the common shapes.
- The page loads nothing from a CDN. It is one file, with the serve-page `base.css`, `theme.css`,
  and `dynamic.js` inline, and the theme fonts in `fonts/` next to it.
