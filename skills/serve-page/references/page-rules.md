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

## Charts

Before you draw a chart, load the `dataviz` skill and follow it. Draw the chart as inline SVG, with
values in the data and not only in the colours. Label each axis and give the units.

## Sensitive pages

A page with account IDs, costs, hostnames, internal IPs, or user data carries a warning line under
the header: "This page holds <what>. Any device on your LAN can open it while the server runs."
Never put a secret, a token, or a password on a page.
