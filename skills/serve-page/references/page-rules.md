# Page rules

Every skill that offers a page builds it to these rules, then adds what its own page shows. The
rules come from the HTML report in Matt Pocock's `improve-codebase-architecture`, with the CDN
scripts removed: a page that loads Tailwind or Mermaid from a CDN breaks silently when the CDN is
blocked, and the agent never sees it break.

## The folder

- Write `<scratchpad>/<skill>/<slug>/index.html`. Put nothing else in the folder, apart from the
  page's own images (for example the screenshots of `check-ui-tells`).
- The server serves the whole folder. Never serve a repo, a home folder, or a folder with other
  files in it.

## The page

- **Self-contained**: inline `<style>`, inline `<svg>`, and no external scripts, fonts, or
  stylesheets. Images are files in the same folder, linked by a relative path.
- **Theme**: colours as CSS variables on `:root`, redefined under
  `@media (prefers-color-scheme: dark)`. Give `body` an explicit background. One accent colour,
  red for problems, and amber for warnings.
- **Layout**: works at phone width, with a 16px side gutter and no sideways scroll. Columns that
  sit side by side on a wide screen stack on a narrow one.
- **Header**: the repo or subject, the date, the scope, and a legend when the diagrams use
  symbols. No introduction paragraph.
- **Same facts as the reply.** The page shows the report the skill already wrote. It adds
  nothing new, so the reply and the page never disagree.
- **Plain words**: the STE rules and clear-reading checks from `../../summarise/SKILL.md` §3.

## Diagrams

Draw them as inline SVG. Pick the pattern that fits, and vary them:

| Pattern | Fits |
|---|---|
| **Boxes and arrows** | Calls, dependencies, and request paths |
| **Side by side** | Before and after, or two candidates |
| **Cross-section** | Layers that a call passes through |
| **Mass diagram** | An interface as wide as its implementation |
| **Radial map** | One change in the middle, and what it touches around it |
| **Frame series** | One part added per frame, each with a one-line caption |

Label boxes in small upper-case text, so they read as a schematic. Keep each diagram about 320px
tall.

For infra (hosts, containers, networks, cloud resources, clusters), follow
[`infra-diagrams.md`](infra-diagrams.md) instead of free-drawing boxes.

## Dynamic pages

A page can be more than one scroll. Use these when the page has more than one view, or when a
diagram has layers or steps:

- **Tabs**: one `<section class="panel" id="...">` per view, and a `<nav class="tabs">` of
  `#id` links. The URL hash picks the tab, so a tab can be linked and reloads stay on it.
- **Layer toggles**: a checkbox with `data-layer="planned"` hides every element with
  `class="planned"`. Use one per state or concern (built, building, planned, decisions).
- **Click to highlight**: give each SVG part `data-id`. An element with `data-links="a b"` (a
  decision card, a slice row) lights up those parts on click, and dims the rest.
- **Steppers**: a frame series as `<div class="stepper">`, one `.step` per frame, with previous
  and next buttons (`data-step="-1"`, `data-step="1"`) and a `.count`.

Paste [`../assets/dynamic.js`](../assets/dynamic.js) whole into one inline `<script>` at the end
of `<body>`. Do not write your own version. Add this CSS:

```css
.js section.panel[hidden], .js .step[hidden] { display: none; }
.tabs a[aria-current="page"] { border-bottom: 2px solid var(--accent); }
body.hide-built .built, body.hide-building .building, body.hide-planned .planned,
body.hide-decision .decision { display: none; }
body.focus [data-id]:not(.hl) { opacity: .25; }
.hl { outline: 2px solid var(--accent); }
svg .hl { outline: none; filter: drop-shadow(0 0 3px var(--accent)); }
```

- Every fact is in the HTML. JS only shows, hides, and highlights. It never builds content, fetches,
  or stores anything.
- Without JS, every panel and every step shows, stacked. The page still reads.

## Charts

Before you draw a chart, load the `dataviz` skill and follow it. Draw the chart as inline SVG, with
values in the data and not only in the colours. Label each axis and give the units.

## Sensitive pages

A page with account IDs, costs, hostnames, internal IPs, or user data carries a warning line under
the header: "This page holds <what>. Any device on your LAN can open it while the server runs."
Never put a secret, a token, or a password on a page.
