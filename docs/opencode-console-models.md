# OpenCode Console — model chart (API-charged)

**Updated:** 2026-09-30

One chart for everything you can run through [OpenCode Console](https://opencode.ai/auth) on API-charged (Zen pay-as-you-go) credits. The **Go proxy** column shows whether the model is also served on the [Go subscription](https://opencode.ai/docs/go/) (`opencode-go/<id>`) and its per-model monthly usage cap.

Checked against the [Zen pricing](https://opencode.ai/docs/zen/) and [Go catalog](https://opencode.ai/docs/go/) (both last updated 2026-09-29). Prices move and the catalog moves; re-check the date before treating a price as live.

Prices are per 1M tokens: **input / output / cached read**. Zen IDs are `opencode/<id>`; Go IDs are `opencode-go/<id>`. Benchmark figures are from the Bito coding-agent run (score /60 with a $ total) plus DeepSWE / AA Index where noted.

## The chart

| Model | List (per 1M: in / out / cache) | Context | Go proxy | Benchmarks | Cost reality | Best use in v2 |
|---|---|---|---|---|---|---|
| Claude Fable 5.1 (`claude-fable-5-1`) | $10 / $50 / $0.25 | 1M | No | 52.5/60 Bito — fewer steps than Opus 5 | List price is brutal; real session cost often beats Opus because it calls less and writes ~⅓ the tokens ($85 vs $136 on the same 60-job run) | Hard architecture, messy multi-file refactors, “figure this out” work. Default plan agent, not daily grind. |
| Claude Opus 5.5 (`claude-opus-5-5`) | $4 / $20 / $0.20 | 1M | No | Newer than Opus 5 (54.5/60). Slightly cheaper list than Opus 5 | Best reliable frontier if you want Opus-class without Fable’s $10/$50 sticker | Complex builds, reviews, long sessions with cache hits. Better daily flagship than Fable. |
| Claude Sonnet 5.5 (`claude-sonnet-5-5`) | $2 / $10 / $0.20 | 1M | No | Sonnet 5 was 46/60 / $16 on Bito; 5.5 is the current mid Claude | Sweet spot for most OpenCode sessions | Default build model. Frontend polish, iterative edits, 80% of repo work. |
| GPT 6 Astra (`gpt-6-astra`) | $10 / $50 / $1.00 (doubles >272K) | 1.05M | No | 54/60 Bito; DeepSWE ~74%; AA Index ~53 | Same list band as Fable. Burns tokens on science/automation | When you need max agentic coding + computer-use. Not the default — Sol 6.1 is close enough cheaper. |
| GPT 6.1 Sol (`gpt-6.1-sol`) | $2 / $10 / $0.10 (doubles >272K) | 1.05M | No | DeepSWE 75.2% at $0.65/task vs Astra 74.1% at $4.43; AA Index 52 vs Astra 53 | Best $ per coding point on the closed side | Daily OpenAI path. Long agent loops, tests, multi-step tools. Prefer this over Astra unless you are stuck on science/OSWorld. |
| Grok 4.7 (`grok-4.7`) | $2 / $6 / $0.50 (doubles >200K) | 500K | Yes ($15/mo cap) | Strong reasoning + tools; not in Bito 29 | Mid list, high cache-read, smaller window than Claude/GPT | Fast “think + edit” in OpenCode. Good second brain next to Sonnet/Sol. Watch the 500K window and Go cap. |
| Kimi K3 (`kimi-k3`) | $3 / $15 / $0.30 | 1M | Yes ($15/mo cap) | 45.5/60 Bito / $22 run | Priced like a mini-Sonnet, scores below GLM and DS Flash | Long-context Chinese + code, research dumps. Not the value pick vs GLM-5.3 or DS V4.1 Flash. |
| GLM 5.3 (`glm-5.3`) | $1.40 / $4.40 / $0.26 | 1M | Yes ($15/mo cap) | 49/60 Bito / $21 run | Solid mid-open. Memory was weak on Bito (4.5/10) | Cheap Opus-adjacent coding if you stay in one session. Pair with a better “memory” model for multi-day work. |
| DeepSeek V4 Pro (`deepseek-v4-pro`) | $1.74 / $3.48 / $0.145 | 1M | Yes ($15/mo cap) | 44/60 Bito / $7.30 | Better list than Flash, worse score/$ | When Flash fails a hard reasoning pass. Not the default DeepSeek. |
| DeepSeek V4.1 Flash (`deepseek-v4.1-flash`) | $0.30 / $1.20 / $0.006 | 1M | Yes ($60/mo cap) | 50.5/60 Bito / $2.67 — 93% of Opus 5 score at ~2% of the bill | Best value on the whole list | Bulk agent work, parallel v2 sessions, scaffolding, test loops. Expect tail latency. Escalate misses to Sol / Opus / Fable. |
| MiniMax M3 (`minimax-m3`) | $0.30 / $1.20 / $0.06 | ~1M | Yes ($60/mo cap) | 41/60 Bito / $3.69 | Cheap, wasteful (high retry %) | High-volume grunt: boilerplate, translations of existing patterns. Not architecture. |
| Muse Spark 1.3 (`muse-spark-1.3`) | $1.25 / $4.25 / $0.15 | 1M | Contributor cheaper/free on Go (training opt-in, region-locked) | Not in Bito | Mid-cheap Meta coding model | Extra cheap capacity. Use paid Spark if you care about retention; Contributor trains on prompts. |
| Jev 1.13 (`jev-1.13`) | $0.042 in / free out (also a Free SKU) | 64K | No | Not a coding model | Almost free | Structured Q&A / TypeSafe forms only. Do not set as `/models` default for build/plan. |

## What to actually run

1. **Default build:** `opencode/claude-sonnet-5-5` — most of the Claude feel at $2/$10; 80% of repo work.
2. **Plan / hard architecture:** `opencode/claude-fable-5-1` — real session cost often beats Opus despite the sticker. `opencode/claude-opus-5-5` if you want the cheaper daily flagship.
3. **Daily OpenAI path:** `opencode/gpt-6.1-sol` — best $ per coding point on the closed side.
4. **Fast think + edit / second brain:** `opencode/grok-4.7` — mid list, high cache-read; watch the 500K window.
5. **Bulk / parallel v2 sessions:** `opencode/deepseek-v4.1-flash` — 93% of Opus 5 score at ~2% of the bill. Escalate misses to Sol / Opus / Fable.
6. **Cheap Opus-adjacent:** `opencode/glm-5.3` — pair with a better "memory" model for multi-day work.
7. **Never a default:** `opencode/jev-1.13` — structured decisions only, not a build/plan model.

## Notes

- **Go proxy caps** are per-model monthly usage limits on the $10 Go / $40 Go Plus plans; each model also gets 20% of its limit per 5 hours and 50% per week. Enable **Use balance** in the console to fall back to Zen credits past a cap instead of blocking.
- **Fable's cost reality:** it calls less and writes ~⅓ the tokens of Opus — $85 vs $136 on the same 60-job run — so judge it by session cost, not the $10/$50 list.
- **Muse Spark 1.3 Contributor** on Go is $0.10/$0.20 in exchange for Meta training on your prompts, in permitted regions only. The paid Spark above is zero-retention.
- **Jev** is a TypeSafe AI System One model (typed yes/no / choice / score questions), not a text coder.
- **Out of scope here:** older generations (Opus 4.x and 5, Grok 4.6/4.5, GPT 5.x and 6 Sol/Luna, Sonnet 5 and 4.6, GLM 5.2, Kimi K2.x, DeepSeek V4 Flash), Gemini, Qwen, and the free limited-time SKUs are all still in the [Zen catalog](https://opencode.ai/docs/zen/) — check it before paying for any of them.
