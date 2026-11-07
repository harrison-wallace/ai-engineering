# AI web UI tells — catalogue

These are the defaults models fall back on, learned from their training data:
Tailwind/shadcn templates, SaaS landing pages from 2020–2022, and Dribbble-style
mockups. One tell alone proves nothing, because human designers follow trends
too. **A cluster of 6–8 together is highly diagnostic.** The real signal is that
specific decisions are missing. The page looks finished and polished, but it
could be swapped for thousands of others.

Each tell has a stable ID. The report uses these IDs in this order.

- **Code**: grep leads for a local project. Open each hit to confirm it. A
  class in a shared `components/ui/*` primitive counts once, not once per use.
- **Rendered**: what to look for in a live page or screenshot. The fields
  [probe.js](probe.js) returns are named in `backticks`.

Tailwind hex values worth knowing: indigo-500 `#6366f1`, indigo-600 `#4f46e5`,
violet-500 `#8b5cf6`, violet-600 `#7c3aed`, purple-500 `#a855f7`,
purple-600 `#9333ea`, fuchsia-500 `#d946ef`.

---

## Colour & visual effects

### C1 — Purple/indigo → blue/cyan gradient
A diagonal gradient on the hero, or a glowing blob behind the text. This is the
loudest classic tell, because indigo was Tailwind's old default.
- **Code**: `from-(indigo|violet|purple|fuchsia)-\d+` together with
  `to-(blue|cyan|sky|indigo|pink)-\d+`; `bg-gradient-to-|bg-linear-to-`; CSS
  `linear-gradient(` that contains one of the hex values above or the words
  `indigo|violet|purple`. A blob is `absolute` + `rounded-full` + `blur-3xl`
  with a purple or indigo background.
- **Rendered**: `gradients` entries in a purple or blue hue range (roughly
  230°–290°), mainly in the first viewport.

### C2 — Gradient text
Gradient fill on headlines or on large numbers.
- **Code**: `bg-clip-text` with `text-transparent`; `background-clip:\s*text`;
  `-webkit-background-clip:\s*text`.
- **Rendered**: `gradientText` > 0.

### C3 — Glassmorphism
Frosted cards (`backdrop-blur` plus a soft border or shadow) that float on a
gradient.
- **Code**: `backdrop-blur`, `backdrop-filter:\s*blur`, `bg-white/(5|10|20)`,
  `border-white/(10|20)`.
- **Rendered**: `backdropBlur` > 0 on elements other than a sticky nav. A
  blurred sticky header alone is Partly.

### C4 — Decorative glows and halos
Radial halos, light blooms, or neon accents that do no job on the page.
- **Code**: `radial-gradient(`, `blur-(2xl|3xl)` or `blur-\[\d+px\]` on
  decorative `absolute` elements, `shadow-\[0_0_`, `drop-shadow-\[`, and a
  coloured `box-shadow:\s*0 0 \d+px`.
- **Rendered**: `radialGradients`, plus `glowShadows` (a shadow with zero
  offset and a large blur).

### C5 — Grain or noise overlay
- **Code**: `noise|grain` in class names or asset names, `feTurbulence`, and
  `mix-blend-(overlay|soft-light)` on a full-bleed layer.
- **Rendered**: a full-size `pointer-events:none` overlay with an SVG or PNG
  noise background.

### C6 — Low-contrast dark mode, or neon on black
Mid-grey text on grey, or neon text on black with no hierarchy.
- **Code** (weak evidence): `text-(gray|zinc|slate|neutral)-(500|600)` on
  `bg-(gray|zinc|slate|neutral)-(800|900|950)`; `text-(cyan|lime|fuchsia|green)-400`
  on `bg-black`.
- **Rendered**: `lowContrast` entries below 4.5:1 for body text. Without a
  rendered page this tell is usually `?`.

## Typography

### T1 — One sans for everything
Inter, Roboto, or a system sans used for all text, often at similar weights with
no real hierarchy.
- **Code**: `Inter` in `next/font/google`, `@fontsource/inter`, a Google Fonts
  URL, `font-family`, or `fontFamily` in the Tailwind config. Also check whether
  the project loads one family only.
- **Rendered**: `fonts` has one family, or one family plus a monospace font,
  and that family is Inter, Roboto, Geist, or a system sans.

### T2 — One accent word in an otherwise sans headline
A single italic serif word, or a single accent-coloured word, dropped into the
headline.
- **Code**: inside `<h1>`/`<h2>`, a `<span>`/`<em>` with `font-serif`, `italic`,
  `bg-clip-text`, or `text-(primary|indigo-|violet-|purple-)`.
- **Rendered**: `headingAccents` > 0.

### T3 — Uppercase eyebrow labels
Small uppercase labels with wide letter-spacing above almost every heading.
- **Code**: `uppercase` together with `tracking-(wide|wider|widest|\[0\.\d+em\])`
  and `text-(xs|sm)`; CSS `text-transform:\s*uppercase` together with
  `letter-spacing`. Compare the count of these labels with the count of section
  headings.
- **Rendered**: `eyebrows` compared with `headings`. Yes when there are
  eyebrows above most sections.

### T4 — Em dash overuse in the copy
- **Code**: count `—` (and `&mdash;`) in user-visible copy only: JSX/HTML text,
  MDX, and i18n JSON. Leave out code comments and README files.
- **Rendered**: `emDashes` per 100 words of `words`. More than about 1 per 100
  words, or em dashes in most taglines, is Yes.

## Layout & components

### L1 — Centred hero with a pill badge above it
"✨ AI-powered", "New", "Now with AI", "Introducing…", "Beta".
- **Code**: `rounded-full` with `px-(2|3|4)` and `py-(0.5|1)` and `text-(xs|sm)`
  near the top of the hero. Also grep the hero copy for
  `New|Introducing|Now with|Beta|✨|AI-powered`.
- **Rendered**: `heroPill` is set.

### L2 — Three (or four) identical feature cards in a row
Each card has an icon on top, a short title, and two lines of text.
- **Code**: `(sm|md|lg):grid-cols-(3|4)`; a `features = [` array whose items
  have the shape `{ icon, title, description }`.
- **Rendered**: `cardRows`, a row of 3–4 sibling boxes with the same structure.

### L3 — Coloured left-border stripe on rounded cards
Often called one of the most reliable single tells.
- **Code**: `border-l-(2|4|\[\d+px\])` with `rounded-`; CSS
  `border-left:\s*\d+px solid` on an element that also has `border-radius`.
- **Rendered**: `leftStripes` > 0.

### L4 — Nested cards ("cardocalypse")
Almost everything is boxed, often with boxes inside boxes.
- **Code**: `<Card` inside another `<Card`, or a bordered and rounded `div` that
  wraps other bordered and rounded `div`s. Read the main page components.
- **Rendered**: `nestedBoxes` > 0, and `boxes` is high compared with the
  number of sections.

### L5 — The same border, shadow, and radius on every surface
A thin border, a soft wide shadow, and a large uniform radius such as
`rounded-2xl`.
- **Code**: count the radius classes in app code. One of
  `rounded-(xl|2xl|3xl)` making up more than ~70% of them, together with
  `border` + `shadow-(sm|md|lg)` on the same elements, is Yes.
- **Rendered**: `radii` dominated by one value of 12px or more.

### L6 — Icons in pale rounded squares
Small chips with a pale background holding an icon, often a Lucide outline icon,
repeated everywhere.
- **Code**: `(h|size)-(8|10|12)` + `w-(8|10|12)` + `rounded-(md|lg|xl|full)` +
  `bg-(\w+)-(50|100)` or `bg-primary/10`, wrapping an icon component.
- **Rendered**: `iconChips` > 2.

### L7 — Emojis as icons, bullets, or heading decoration
"🚀 Fast", "🔒 Secure".
- **Code**: `rg -nP '[\x{1F300}-\x{1FAFF}\x{2600}-\x{27BF}]'` over the copy
  files. Look for hits in headings, list items, and `icon:` fields.
- **Rendered**: `emojiHeadings` > 0.

### L8 — Stock shadcn/ui with only the primary colour changed
Lucide is the only icon set.
- **Code**: a shadcn `components.json`; a `components/ui/button.tsx` that still
  has the stock variants; `lucide-react` as the only icon dependency in
  `package.json`. Diff the `:root` tokens in `globals.css` against the shadcn
  defaults (`--radius: 0.5rem`/`0.625rem`, neutral `--background`/`--foreground`).
  If only `--primary` (or nothing) has changed, this is Yes.
- **Rendered**: usually `?`, unless the stock shadcn look is unmistakable.

## Motion

### M1 — Sections fade or slide in on scroll
- **Code**: `whileInView`, `useInView`, `initial={{ opacity: 0`,
  `IntersectionObserver`, `data-aos`, `aos`, `ScrollTrigger`,
  `animate-fade-in(-up)?`.
- **Rendered**: `scrollReveal` > 0, meaning elements below the fold that start
  at `opacity: 0` or have a transform.

### M2 — Every card lifts on hover, clickable or not
- **Code**: `hover:-translate-y-`, `hover:shadow-(lg|xl|2xl)`,
  `hover:scale-10[2-5]`, `whileHover`, CSS `:hover` with `translateY(-`. Yes
  when these sit on non-interactive elements (a `div`/`Card` with no `href` or
  `onClick`).
- **Rendered**: code is the better source here. Mark `?` if you only have the
  rendered page.

### M3 — Glow that follows the cursor
- **Code**: `onMouseMove|mousemove|pointermove` used together with
  `radial-gradient` or a `--mouse-x`/`--x` CSS variable; `useMousePosition`;
  a spotlight-card component.
- **Rendered**: `?`, unless you hover and watch for it.

### M4 — Perpetual "alive" animations
Pulsing dots, numbers that count up, typing headlines, and marquees, none of
which show real state.
- **Code**: `animate-(pulse|ping|bounce)` outside loading states;
  `infinite`; `react-type-animation|typewriter-effect|typed.js`;
  `react-countup|countup.js|useCountUp`; `marquee`. A spinner on a real
  loading state does not count.
- **Rendered**: `infiniteAnims` > 0, excluding spinners.

## Copy & content

### K1 — Generic buzzwords
Words that could describe any product.
- **Code / Rendered**: `rg -niw` over the copy for
  `seamless(ly)?|empower(s|ing)?|unlock(s)?|next-gen(eration)?|elevate|supercharge|revolutioni[sz]e|cutting-edge|game-?chang\w*|effortless(ly)?|streamline|harness|unleash|reimagine|transform your|leverage|robust|world-class|state-of-the-art|built for the future`.
  Three or more distinct buzzwords is Yes.

### K2 — Everything in threes
"Fast. Simple. Powerful.", or triads like "fast, secure, and scalable".
- **Code / Rendered**: `\b[A-Z]\w+\.\s+[A-Z]\w+\.\s+[A-Z]\w+\.`, adjective
  triads in taglines, and sections with exactly three items again and again.

### K3 — Round or suspiciously precise metrics with no source
"10x", "99.9%", "500+ integrations".
- **Code / Rendered**: `\b\d+x\b`, `99\.9+%`, `\b\d[\d,]*[kKmM]?\+`. Yes when
  no source, footnote, or link sits near the figure.

### K4 — Placeholder testimonials, stock logos, fake screenshots
- **Code**: `testimonials = [` filled with generic names (Sarah Chen, John Doe,
  Alex Johnson), `Acme|Globex|Initech`, `lorem ipsum`,
  `pravatar|randomuser\.me|ui-avatars`, a logo cloud of plain-text company
  names, and "screenshots" built from divs (three traffic-light dots:
  `rounded-full` with `bg-red-`, `bg-yellow-`, and `bg-green-`).
- **Rendered**: `trafficLights` > 0, and testimonial names and quotes that read
  as invented.

---

## Counterweights (specific decisions)

These suggest someone made real decisions. List the ones you find after the
table:

- A custom palette that is not Tailwind's defaults or a single brand hue on neutrals.
- A deliberate type pairing or a display face, with a real scale and real weight contrast.
- A layout that leaves the centred hero → 3 cards → testimonials → CTA template.
- Real product screenshots or imagery, and testimonials with names and sources you can check.
- Motion that shows state, such as feedback or progress, and not decoration.
- Copy specific enough that it could only describe this one product.

Newer models (especially Claude Design-style output) sometimes move to cream or
beige with terracotta and high-contrast serif headlines. If you see that cluster
with the same generic copy and structure, note it as an **alt-cluster** after
the table. It is the same failure, without the purple.
