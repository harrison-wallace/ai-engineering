# UI prototype

## Contents

- [1. Branch and manifest](#1-branch-and-manifest)
- [2. Pick the host page](#2-pick-the-host-page)
- [3. Write the briefs, then the variants](#3-write-the-briefs-then-the-variants)
- [4. Wire the switcher](#4-wire-the-switcher)
- [5. Build the floating switcher](#5-build-the-floating-switcher)
- [6. Page (with `page`)](#6-page-with-page)
- [7. Clean up](#7-clean-up)

Build several **structurally different** variants of one screen, switchable from a floating bar.
The user flips between them, picks one or takes parts from each, and the rest is deleted.

## 1. Branch and manifest

1. Record the current branch. Run `git switch -c prototype/<slug>`. Uncommitted work that was
   there before the run comes with it, and that is fine. Nothing is committed on this branch.
2. Create `<scratchpad>/prototype/<slug>/manifest.md` with two lists:
   - **Created**: every file the prototype adds.
   - **Edited**: every existing file it changes. Before the first edit, copy the file to
     `<scratchpad>/prototype/<slug>/backup/<same path>`.
3. Add each file to the manifest before you write it. §7 cleans up from the manifest, not from
   `git restore`, so the user's own uncommitted changes survive.

## 2. Pick the host page

Strongly prefer an **existing page**. A variant on an empty route looks fine every time. On a real
page, with the real header, data, and density, its problems show.

- **Existing page** (the default): the variants render on the same route behind `?variant=`. The
  data fetching, params, and auth stay. Only the rendered subtree changes. A new section of an
  existing page counts as an existing page.
- **New route** (the last resort): only when nothing existing could host it. Follow the repo's
  routing convention, and put `prototype` in the path, for example `app/prototype/<slug>/page.tsx`.

## 3. Write the briefs, then the variants

Default to 3 variants. Never more than 5.

First write one **structural brief** for each variant, two lines long: its layout, its information
hierarchy, and its primary action. The briefs must disagree about structure, for example "sidebar
list with a detail pane", "one column, step by step", and "dense table with inline edit". Colour
and copy are not structure. Show the briefs in one line each, then write the variants.

Each variant:

- Uses the page's data and purpose, and the repo's styling (Tailwind, shadcn, or what is there).
- Is one component, `VariantA`, `VariantB`, and so on, in a file next to the host page, named
  `<page>.prototype-variant-a.tsx`.
- Shares small parts only (a header is fine). A shared layout defeats the point.
- Points any mutation at a stub.
- Avoids the AI tells from `../check-ui-tells/tells.md` (relative to the skill folder, resolved
  with `readlink -f`): purple or indigo gradients, gradient text,
  glassmorphism, a pill badge over the hero, three identical cards, left-border stripes, nested
  cards, scroll fade-ins, and hover lifts. Two variants that land on the same tells are one
  variant. Rewrite one from its brief.

## 4. Wire the switcher

In the host page, pick the variant from the search param. Keep the data fetching above it.

Next.js App Router, in a client component (wrap the reader of `useSearchParams` in `<Suspense>`):

```tsx
'use client';
import { useSearchParams } from 'next/navigation';

const variants = { A: VariantA, B: VariantB, C: VariantC };

export function PrototypeVariants(props: Props) {
  const key = (useSearchParams().get('variant') ?? 'A') as keyof typeof variants;
  const Variant = variants[key] ?? VariantA;
  return (
    <>
      <Variant {...props} />
      <PrototypeSwitcher keys={Object.keys(variants)} current={key} />
    </>
  );
}
```

On the Pages Router, read `useRouter().query.variant`. On Vite with React Router, use
`useSearchParams()` from `react-router-dom`.

## 5. Build the floating switcher

One `PrototypeSwitcher` component, in the folder where the repo keeps shared UI. It is a small pill
fixed at the bottom centre:

- **←** goes to the previous variant and **→** to the next, wrapping round.
- **Label**: the variant key and its brief's name, for example `B (sidebar list)`.
- **Keys**: the left and right arrow keys cycle too, except when an `input`, a `textarea`, or a
  `[contenteditable]` element has focus.
- **URL**: each change updates `?variant=` through the router (`router.replace` on Next.js), so a
  reload or a shared link keeps the variant.
- **Look**: high contrast, so it is clearly not part of the design under review.
- **Production**: render nothing when `process.env.NODE_ENV === 'production'`.

Start the dev server the repo uses (`npm run dev`, or the script in `package.json`) in the
background, if it is not already up. Open each variant once, and fix anything that does not
render.

## 6. Page (with `page`)

Shoot each `?variant=` with the Playwright MCP at 1440 px and 390 px wide, full page. Save the
shots in `<scratchpad>/prototype/<slug>/page/`. Build `index.html` there to the `serve-page` page
rules: one column per variant on a wide screen, stacked on a phone, each with its brief and its two
shots. Then serve it.

## 7. Clean up

After the answer is recorded (`SKILL.md` §5):

1. Delete every file under **Created** in the manifest.
2. Copy every file under **Edited** back from `backup/`.
3. Run `git status --short` and compare it with `<scratchpad>/prototype/<slug>/baseline.txt` from
   `SKILL.md` §1. Only the ADR may be new. Show any other new or changed path, and stop.
4. Check that the prototype branch has no commits of its own: `git log <start-branch>..HEAD`. If it
   has any, show them, and stop.
5. Switch back to the start branch, then delete the prototype branch with `git branch -d
   prototype/<slug>`. Use `-d`, never `-D`.
6. Stop the dev server if this run started it.
