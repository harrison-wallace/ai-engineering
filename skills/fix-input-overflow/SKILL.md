---
name: fix-input-overflow
description: Assess whether the current app suffers from native date/month/time input overflow on iOS Safari (intrinsic width ignoring w-full/width:100%), and apply the global CSS reset fix if so. Triggers on "/fix-input-overflow", "date input overflows", or "input spills out of its container on iPhone".
---

# fix-input-overflow

iOS Safari gives native `date`, `month`, `time`, and `datetime-local` inputs an
intrinsic width and a centred value, ignoring `w-full` / `width: 100%`. On small
screens they overflow their containers (spill past modal edges, overlap
neighbouring grid cells). This skill checks whether the current app is affected
and, if so, applies a known-good global CSS reset.

## 1. Assess

Determine whether the app is exposed. All three must be true to proceed:

1. **The app uses native date-ish inputs.** Search the codebase:
   ```bash
   grep -rn 'type="date"\|type="month"\|type="time"\|type="datetime-local"' \
     --include="*.tsx" --include="*.jsx" --include="*.html" --include="*.vue" --include="*.svelte" \
     . | grep -v node_modules
   ```
   No hits → report "no native date/time inputs; not applicable" and stop.

2. **The fix isn't already present.** Search stylesheets for an existing reset:
   ```bash
   grep -rn 'webkit-date-and-time-value' --include="*.css" --include="*.scss" . | grep -v node_modules
   ```
   Also check whether the date-input selectors already get `appearance: none`
   globally (e.g. a CSS reset like Tailwind Preflight does **not** cover this —
   Preflight leaves date inputs native). If a real fix is already there, report
   that and stop.

3. **The inputs rely on container-driven width** — they use `w-full`,
   `width: 100%`, or sit inside grid/flex cells. This is almost always true in
   form UIs; skim one or two of the grep hits from step 1 to confirm.

Report the assessment (which inputs are affected, in which components) before
editing anything.

## 2. Fix

Find the app's **global stylesheet** — the one imported at the root
(`app/globals.css`, `src/index.css`, `styles/global.scss`, etc.). Append this
block, matching the file's existing section-comment style:

```css
/* Date/month input width fix (iOS Safari):
   iOS Safari gives date/month/time inputs an intrinsic width and a centred
   value, ignoring w-full — they overflow their containers on small screens.
   Reset the native appearance so layout width wins, and left-align the value
   to match text inputs. min-width:0 lets them shrink inside grid/flex cells. */
input[type="date"],
input[type="month"],
input[type="time"],
input[type="datetime-local"] {
  -webkit-appearance: none;
  appearance: none;
  min-width: 0;
}
input::-webkit-date-and-time-value {
  text-align: left;
  min-height: 1.25rem; /* iOS collapses the shadow value when empty; match text-sm line-height */
}
```

Notes:

- Keep the full selector list even if the app only uses `type="date"` today —
  the extra selectors are harmless and future-proof.
- If the app's base font sizing differs from Tailwind's `text-sm`, adjust the
  `min-height` to match the line-height of the app's other text inputs.
- This is a **global** fix — do not duplicate it per-component, and remove any
  per-component workarounds (fixed widths, `overflow: hidden` wrappers) it
  supersedes only if they were clearly added for this bug.

## 3. Verify

- Run the project's build (`npx next build`, `npm run build`, etc.) to confirm
  the stylesheet still compiles.
- If a quick visual check is feasible, serve the app locally (respect the
  repo's test-port conventions) and confirm date inputs render left-aligned and
  contained; desktop browsers can't reproduce the iOS overflow itself, so treat
  the build passing + rule present as sufficient when no iOS device/simulator
  is available.

## 4. Report

State: whether the app was affected, which components had the vulnerable
inputs, the file the fix was added to, and the verification result. Do not
commit — leave the change in the working tree.
