# Logic prototype

One self-contained HTML file that lets anyone drive a state model by clicking. Use it when the
question is about rules, state changes, or the shape of data: the kind of thing that looks right on
paper and feels wrong after real cases go through it.

It is one file with nothing to install, so a non-developer can drive it. Its labels use the
domain's words, not the code's.

## 1. Write the question at the top

Put the question from `SKILL.md` §1 in a visible intro on the page, not only in a comment. When the
branch was inferred, add the reason in one line under it.

## 2. Isolate the logic in a pure module

Put the logic that answers the question in one `<script>` block, as a small pure module. Pick the
shape the question needs, not the one that is easiest to wire to buttons:

| Shape | When |
|---|---|
| A reducer: `(state, action) => state` | Actions are separate events, and the state is one value |
| A state machine: named states and transitions | "Which actions are legal now" is part of the question |
| Pure functions over a plain data type | There is no current state, only transformations |
| A class with a clear method surface | The logic owns state that changes over time |

Keep it pure: no `document`, no DOM, and no button handlers inside it. The page calls the module.
Nothing flows the other way. Add JSDoc types, so the module moves into a TypeScript repo with
little change.

## 3. Build the page

Write `docs/prototypes/<slug>/index.html` in the repo. Create the folder if it is missing.

Follow the **page** and **theme** sections of `../serve-page/references/page-rules.md`, relative to
the skill folder: inline CSS and JS, no external scripts or fonts, light and dark themes, one
accent colour, and phone width with no sideways scroll. No framework, no bundler, no server. It
must open with a double-click.

Top to bottom:

1. **Title and question.** One line on what the demo lets you explore.
2. **Current state.** A panel of labelled fields, not a raw JSON dump. Render it again after every
   click. Mark the fields that the last action changed.
3. **Free-play buttons.** One button for each action, always available, in domain words. A button
   for an action that is illegal now stays visible, and clicking it shows why it was refused.
4. **Walkthroughs.** One tab for each scenario. Each tab has a plain description (the situation,
   and what to watch for), then the ordered buttons for that scenario. Each step is a real button
   that does the action and moves to the next step. Starting a tab resets to a known state, so it
   runs the same way each time.

Pick scenarios for the awkward cases: the happy path, a hard edge case, and an attempt at something
that must be illegal.

Keep it calm: clear type, space, one accent colour, and no animation.

## 4. Hand over

Give the path. With `page`, serve it (`SKILL.md` §4). Add an action or a scenario when the user
asks for one.

## Not this

- Tests. A prototype that needs tests is not a prototype.
- The real database or API.
- Generalising for a case nobody asked about.
- Logic mixed into the page. If the module touches the DOM, it cannot move into the real code.
