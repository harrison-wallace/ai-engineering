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
