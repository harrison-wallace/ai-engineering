---
name: check-ai-ui-tells
description: Scan a web UI (local project code and/or a live URL) for the typical "AI-generated" design tells — purple gradients, gradient text, glassmorphism, Inter-only type, eyebrow labels, pill-badge heroes, three identical feature cards, left-border stripes, nested cards, Lucide/shadcn defaults, scroll fade-ins, hover lifts, buzzword copy, unsourced metrics — and list every tell in one evidence table with a cluster score. Report-only. Triggers on "/check-ai-ui-tells", "does this look AI-generated", "find the AI tells", or "how generic does this site look".
---

# check-ai-ui-tells

A report-only scan for the statistical defaults that make a page look like it
came from a template. The full catalogue, with detection signals per tell, is in
[tells.md](tells.md). Read it before you scan. Each tell has a stable ID (C1–C6,
T1–T4, L1–L8, M1–M4, K1–K4), and the report uses those IDs in the same order.

One tell proves nothing. The score is the **cluster**: 6–8 present together is
highly diagnostic.

This skill is not a design critique. For a judgement against a design framework,
use `review-website-design`.

## 1. Establish the subject

Work out what you have, and use every source that is available:

- **Local project**: frontend files exist (`package.json` with a web framework,
  or `*.html`/`*.tsx`/`*.vue`/`*.svelte`/`*.astro`). Scan the code.
- **URL**: the user gave one, or a dev server is already running. Probe the
  rendered page.
- **Both**: a local project you can run. Scan the code, then probe the page if a
  server is already up or the user asks. Do not start long-running servers
  without saying so.
- **Neither**: if the subject is unclear, ask for a path or URL.

If the user named a page or route, such as "the landing page", limit the scan to
that route and the components it uses. Otherwise, start from the homepage or
landing route.

## 2. Code scan

Build the file set and leave out generated and vendored trees:

```bash
rg --files -g '*.{html,css,scss,js,jsx,ts,tsx,vue,svelte,astro,mdx,md,json}' \
  -g '!node_modules' -g '!dist' -g '!build' -g '!.next' -g '!.nuxt' -g '!.svelte-kit' \
  -g '!*.lock' -g '!package-lock.json' -g '!*.min.*'
```

Read these first, because they settle several tells at once:

- `package.json`: icon libraries (L8), motion, count-up, and typing libraries (M1, M4), and fonts (T1).
- `components.json`, `components/ui/*`, `globals.css`/`app.css`, and the Tailwind config: shadcn tokens (L8), fonts (T1), radius (L5), and the palette (C1).
- The landing page or route component, and the hero, features, testimonials, and CTA sections it renders.

Then run the **Code** greps from `tells.md`, one tell at a time. Rules:

- **Open each hit** before you count it. A grep match is a lead, not a finding.
- Count usage in **app code**. A stock `components/ui/*` file with
  `hover:shadow-md` is evidence for L8. It is not evidence for M2 unless the app
  applies that component to non-interactive cards.
- Copy tells (T4, K1–K4) apply only to **user-visible text**. Leave out code
  comments, READMEs, and test fixtures.
- For each tell, record a status, the strongest 1–3 `file:line` citations, and
  a count when the tell is about frequency (eyebrows, em dashes, radius share).

## 3. Rendered probe (when a URL is available)

Use the Playwright MCP tools when they are available:

1. `browser_navigate` to the URL, then `browser_resize` to 1440×900.
2. `browser_take_screenshot` of the first viewport, and a full-page screenshot.
   Look at them yourself. Several tells are visual (C1 blob, C6, L2, L4).
3. `browser_evaluate` with the function in [probe.js](probe.js). It is
   read-only and returns counts and example selectors. The field names are
   listed in `tells.md`.
4. For M1 and M3: scroll once through the page and hover two cards. Note what
   animates.
5. Optional: `browser_resize` to 390×844 and take one more screenshot to check
   that the mobile layout matches the desktop layout.

Without Playwright, fetch the HTML and grep it as code, then mark the visual-only
tells (C6, M1–M3) `?`.

When code and rendered evidence disagree, trust the **rendered** result. Code
can be dead, or hidden behind a flag.

## 4. Status per tell

| Status | Meaning | Score |
|---|---|---|
| **Yes** | Clearly present, and the evidence is cited | 1 |
| **Partly** | Present but limited or defensible (one instance, functional, a blurred sticky header alone) | 0.5 |
| **No** | Looked, not present | 0 |
| **?** | Can't judge from the sources available. Say what is needed (usually "rendered page") | — |

Base every **Yes** and **Partly** on evidence you opened. When in doubt, mark
**Partly**, not Yes.

## 5. Report

Output **one table with every tell** (26 rows) in catalogue order, so you can
diff runs against each other:

| ID | Category | Tell | Status | Evidence |
|---|---|---|---|---|
| C1 | Colour | Purple/indigo → blue gradient | Yes | `app/page.tsx:14` `from-indigo-500 to-cyan-400` on hero bg; blurred violet blob `:9` |
| C2 | Colour | Gradient text | No | — |
| T3 | Type | Uppercase eyebrow labels | Yes | 7 eyebrows over 8 section headings (`components/Section.tsx:5`) |
| M2 | Motion | Hover lift on non-clickable cards | ? | Code shows `hover:-translate-y-1` on `FeatureCard`; check if it links |
| … | … | … | … | … |

Evidence column: at most ~20 words. Cite `file:line` for code, and a selector or
"screenshot, first viewport" for rendered evidence. Put a count where it is the
point. Use `—` for **No**.

After the table:

1. **Cluster score**: `X / N` where N is the tells that were judged (not `?`),
   with the band:
   - **0–3**: few tells. The page reads as deliberate.
   - **4–5**: some template defaults are showing.
   - **6–8**: a strong cluster. The page likely reads as AI- or template-generated.
   - **9+**: textbook. The page could pass for an unmodified starter template.
2. **Loudest tells**: the 3 Yes rows that do the most to make the page look
   generic, each with a one-line concrete change (for example, "replace the
   indigo→cyan hero gradient with the brand's own hue on a neutral").
3. **Counterweights**: the specific decisions you found (see `tells.md`). If
   there are none, write: "None found: no specific decisions stand out."
4. **Alt-cluster**: add this line only when the cream/terracotta/serif variant
   is present.
5. **Coverage**: one line naming the sources scanned (code paths and route, URL
   and viewport) and the tells marked `?`, with the reason.

Rules:

- **Report only.** Do not change styles, copy, or components. The user decides
  what to change. For a redesign, point them to the `frontend-design` skill.
- Do not label the page "AI-generated". Report the tells and the score. Humans
  follow these trends too.
- A clean result is still the full table, with the score line and the
  counterweights.
