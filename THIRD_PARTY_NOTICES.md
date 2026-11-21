# Third-party notices

## pstack

These skills adapt structure and passages from the pstack skills in
[cursor/plugins](https://github.com/cursor/plugins/tree/main/pstack). They were rewritten for
Claude Code, cheaper models, and infrastructure work.

| Skill here | Adapted from |
|---|---|
| [design](skills/design/SKILL.md) | `pstack/skills/architect` |
| [restate-ask](skills/restate-ask/SKILL.md) | `pstack/skills/in-your-own-words` |
| [reflect](skills/reflect/SKILL.md) | `pstack/skills/reflect` |
| [trace-impact](skills/trace-impact/SKILL.md) | `pstack/skills/blast-radius` |
| [explain-how](skills/explain-how/SKILL.md) | `pstack/skills/how` |
| [explain-why](skills/explain-why/SKILL.md) | `pstack/skills/why` |
| [teach](skills/teach/SKILL.md) | `pstack/skills/teach` |
| [fix-prose](skills/fix-prose/SKILL.md) | `pstack/skills/unslop` |
| [summarise](skills/summarise/SKILL.md) (`plain` mode) | `pstack/skills/bro` |
| [check-primitives](skills/check-primitives/SKILL.md), [design](skills/design/SKILL.md) (the data-shape red flags and runner step 2) | `pstack/skills/principle-model-the-domain` and `pstack/skills/principle-foundational-thinking` |
| [summarise](skills/summarise/SKILL.md), [restate-ask](skills/restate-ask/SKILL.md) (clear-reading checks), [summarise-deep](skills/summarise-deep/SKILL.md) (voice) | `pstack/skills/technical-writing` |

pstack is distributed under the MIT License:

```
MIT License

Copyright (c) 2026 Lauren Tan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Matt Pocock's skills

These skills adapt structure and passages from
[mattpocock/skills](https://github.com/mattpocock/skills). They were rewritten for this setup:
bounded question rounds, approved writes, infra coverage, and cheaper models.

| Skill here | Adapted from |
|---|---|
| [check-architecture](skills/check-architecture/SKILL.md) | `skills/engineering/improve-codebase-architecture`, and the vocabulary, `DEEPENING.md`, and `DESIGN-IT-TWICE.md` ideas of `skills/engineering/codebase-design` |
| [define-terms](skills/define-terms/SKILL.md) | `skills/engineering/domain-modeling` |
| [prototype](skills/prototype/SKILL.md) | `skills/engineering/prototype`, with its `LOGIC.md` and `UI.md` |
| [diagnose](skills/diagnose/SKILL.md) | `skills/engineering/diagnosing-bugs`, including `scripts/hitl-loop.template.sh` |
| [guide-setup](skills/guide-setup/SKILL.md) | `skills/engineering/wizard`, including the library in `template.sh` |
| [explain-again](skills/explain-again/SKILL.md) | `skills/productivity/wait-what` |

[fix-comments](skills/fix-comments/SKILL.md) adapts a comment-sorting prompt that Matt Pocock
shared (tautology, excuse, stale, and decision record). The prompt is not part of
mattpocock/skills, and it was published with no license file.

mattpocock/skills is distributed under the MIT License:

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Diagram skills

[draw-infra](skills/draw-infra/SKILL.md) adapts ideas from two MIT-licensed skills:

| Source | Adapted |
|---|---|
| [vidanov/aws-architecture-diagram-skill](https://github.com/vidanov/aws-architecture-diagram-skill) | The layout checks (no edge through a box, straight edges), the companion Markdown file, the render-and-look loop, the audience mode, and for the draw.io output: the verified AWS icon names and colours, the broken-icon list, the group styles, and the export-to-PNG check |
| [konraddzbik/architecture-diagram-skill](https://github.com/konraddzbik/architecture-diagram-skill) | Click-through flows with one hop lit per step and the rest dimmed, the packet that runs along each hop, payloads per step, the mode switch (dev and prod), and the grounding rules |

Both are distributed under the MIT License, with the same text below the copyright line:
Copyright (c) 2026 Alexey Vidanov, and Copyright (c) 2026 Konrad Dzbik.

```
MIT License

Copyright (c) 2026 Alexey Vidanov
Copyright (c) 2026 Konrad Dzbik

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Page theme fonts

The serve-page theme ([`skills/serve-page/assets/theme.css`](skills/serve-page/assets/theme.css))
ships two fonts as `.woff2` files in `skills/serve-page/assets/fonts/`, and copies them next to
each served page.

| Font | Source | License |
|---|---|---|
| Source Serif 4 | Adobe, via [Fontsource](https://fontsource.org/fonts/source-serif-4) (latin subset) | SIL Open Font License 1.1 |
| Source Sans 3 | Adobe, via [Fontsource](https://fontsource.org/fonts/source-sans-3) (latin subset) | SIL Open Font License 1.1 |

The full license text is in
[`skills/serve-page/assets/fonts/OFL.txt`](skills/serve-page/assets/fonts/OFL.txt).

The theme's look follows the editorial patterns in
[VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) (MIT). No file from
it is copied.
