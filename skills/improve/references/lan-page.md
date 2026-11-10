# LAN page

What the `improve` page shows. Build and serve it with `serve-page`: read
`../../serve-page/SKILL.md` (relative to this file, resolved with `readlink -f`) and follow its
§1 to §4. Its page rules cover the folder, the theme, the layout, and the serving.

## Content

Write `<scratchpad>/improve/<slug>/index.html`.

- **Header**: the scope, the job sentence, and the answer to the question, if there was one.
- **One card per finding**, in report order:
  - The title, a strength badge (Strong, Worth exploring, or Speculative), and a kind tag.
  - The files, in a monospace list.
  - For a structural change, the before-and-after diagram, side by side. For other kinds, the
    problem and the change as two short blocks.
  - **Proof**, one line.
  - **Next**: the skill, and its gate (`auto`, approval, or user-run).
  - An amber callout when it reopens an ADR.
- **Chain results**: when `auto` ran research or trace-impact, a short block per link with its
  result and how it changed the finding.
- **Checked and left**, and **Already rejected**, as short lists at the end.

## Stop

Stop the server when the user says they are done, when a chain link starts, or at the end of the
run at the latest (`serve-page` §4).
