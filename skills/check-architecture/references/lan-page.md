# LAN page

What the `check-architecture` page shows. Build and serve it with `serve-page`: read
`../../serve-page/SKILL.md` (relative to this file, resolved with `readlink -f`) and follow its
§1 to §4. Its page rules cover the folder, the theme, the layout, and the serving. Adapted from the
HTML report in Matt Pocock's `improve-codebase-architecture`, without its CDN scripts.

## Content

Write `<scratchpad>/check-architecture/<slug>/index.html`.

- **Legend** in the header: solid box = module, dashed line = seam, red arrow = leak, thick dark
  box = deep module.
- **One card per candidate**, in report order:
  - The title, a strength badge (Strong, Worth exploring, or Speculative), and a dependency-kind
    tag.
  - The files, in a monospace list.
  - The before and after diagram, side by side. This carries the card.
  - **Problem** and **Solution**, one sentence each.
  - **Wins**, as bullets of 6 words or fewer, in vocabulary terms.
  - **Proof**, one line.
  - An amber callout when it reopens an ADR.
- **Top recommendation**: one larger card at the end, with a link to its candidate.

Pick the diagram that fits each candidate, and vary them:

| Pattern | Fits |
|---|---|
| **Boxes and arrows** | Calls and dependencies. After: one thick box with the old modules faded inside |
| **Cross-section** | Layers a call passes through. Before: 6 thin bands. After: 1 thick band |
| **Mass diagram** | An interface as wide as its implementation. Two bars per module, interface and implementation |
| **Call-graph collapse** | A tree of calls that becomes one box, with the inner calls faded |

## Stop

Stop the server when the user says they are done, when the hand-off to `design` starts, or at the
end of the run at the latest (`serve-page` §4).
