# OpenCode Zen — open-weight models

**Updated:** 2026-08-26

Checked today against the [Zen catalog](https://opencode.ai/docs/zen/), [Go catalog](https://opencode.ai/docs/go/), live [`/zen/v1/models`](https://opencode.ai/zen/v1/models), and live [`/zen/go/v1/models`](https://opencode.ai/zen/go/v1/models). Closed / frontier picks (Grok, Claude, GPT, Gemini) live in [opencode-zen-frontier.md](opencode-zen-frontier.md). Prices and the catalog move; re-check the date before treating a price as live.

Prices are per 1M tokens. Zen IDs are `opencode/<id>`; Go IDs are `opencode-go/<id>`.

## Quick picks (Zen PAYG)

| Priority | Model | ID | In / out | Why |
|---|---|---|---|---|
| **Best daily driver** | MiniMax M3 | `minimax-m3` | $0.30 / $1.20 | Strong agentic coding (SWE-bench Pro ~59%). **512K context on Zen** (the model can do 1M elsewhere) |
| **Best quality on Zen** | GLM 5.2 | `glm-5.2` | $1.40 / $4.40 | Best open coding model on Zen PAYG; SWE-bench Pro ~62%; 1M context. GLM-5.3 is newer but Go-only |
| **Best cheap bulk** | DeepSeek V4 Flash | `deepseek-v4-flash` | $0.22 / $0.66 off-peak | 1M context, dirt cheap. Double price in peak hours |
| **Hard agentic / long horizon** | Kimi K3 | `kimi-k3` | $3.00 / $15.00 | Top-tier open reasoning; 1M context. Priced like Sonnet 4.6, not a value pick |
| **Coding specialist mid-price** | Kimi K2.7 Code | `kimi-k2.7-code` | $0.95 / $4.00 | Code-tuned Kimi without K3’s bill. 262K context |
| **Free (limited time)** | MiMo-V2.5 Free | `mimo-v2.5-free` | $0 | Usable for light work (200K context); data may be used to train |

Skip MiniMax M2.5, Kimi K2.5, and GLM 5 — they are on the deprecation list. They still appear in the live catalog; don’t start new work on them.

## Performance vs price

**Quality, roughly:** Kimi K3 ≳ GLM 5.2 ≳ MiniMax M3 ≈ DeepSeek V4 Pro > Kimi K2.7 Code > DeepSeek V4 Flash ≈ MiMo-V2.5

**Value:** MiniMax M3 sits in the sweet spot. You keep most of GLM 5.2’s coding quality at about a quarter of the token cost. DeepSeek V4 Flash is the floor if you want volume. GLM 5.2 is still cheap versus Claude ($5 / $25 Opus 5, $2 / $10 Sonnet 5) and is the one to switch to for architecture, gnarly refactors, and multi-file bugs.

DeepSeek V4 Pro ($0.66 / $1.98 off-peak) is the other value play: closer to GLM on hard reasoning, still well under GLM’s price. Peak hours **double** it: 01:00–04:00 and 06:00–10:00 UTC, **Monday–Friday** ([DeepSeek](https://api-docs.deepseek.com/quick_start/pricing/); weekends are off-peak). US daytime is almost entirely off-peak.

Kimi K3 is the open-weight “spend money” option. Independent coding indexes put it near the closed frontier; Zen charges $3 / $15, so use it when MiniMax/GLM stall, not as the default.

Qwen 3.5 / 3.6 Plus are on Zen PAYG (closed Alibaba SKUs). **Qwen3.7 Max/Plus and Qwen3.8 Max are not in the live Zen PAYG catalog** — they are on Go (`qwen3.7-max`, `qwen3.8-max`). Qwen3.8 Max is the current open-weight leaderboard leader.

## What to actually run

1. Default: `opencode/minimax-m3`
2. Escalate: `opencode/glm-5.2`
3. Cheap / high-volume: `opencode/deepseek-v4-flash` (prefer off-peak)
4. Free scratch / titles / small edits: `opencode/mimo-v2.5-free`

## OpenCode Go — $10/month

[OpenCode Go](https://opencode.ai/docs/go/) is the open-model plan. Same Zen login, provider `opencode-go`. You get **$12 / 5 hours, $30 / week, $60 / month** of usage.

That’s where the newest open models live. Live Go catalog today includes:

- **GLM-5.3** — current GLM, **not** on Zen PAYG. ~1,080 requests/month on the $15 usage budget
- **Qwen3.8 Max** — current open-weight leaderboard leader. ~810 requests/month ($15 budget)
- MiniMax M3 (~16,000/month), DeepSeek V4 Flash (~37,800) / Pro (~5,200), MiMo-V2.5, MiMo-V2.5-Pro, Kimi K2.7 Code, Kimi K3 (~490), LongCat-2.0, Hy3, Qwen3.7 Max/Plus

On Go, MiniMax M3 still gives you thousands of requests/month. GLM-5.3, Qwen3.8 Max, and Kimi K3 are capped tighter because they’re expensive.

If you already burn Zen credits, keep MiniMax M3 + GLM 5.2. If you want a cheap always-on open stack, Go at $10 is the better deal than paying M3/GLM per token.

Go also serves Grok 4.6 and GPT 5.6 Luna (closed) on a **$15** usage budget — see the [frontier sheet](opencode-zen-frontier.md). Ox Alpha Free on Go is `opencode-go/ox-alpha-free` (different ID from Zen PAYG).

## Other open models on Zen (PAYG)

| Model | ID | In / out | Notes |
|---|---|---|---|
| MiniMax M2.7 | `minimax-m2.7` | $0.30 / $1.20 | Previous MiniMax; 205K context. Prefer M3 |
| GLM 5.1 | `glm-5.1` | $1.40 / $4.40 | Same price as 5.2; 205K context. Prefer 5.2 (1M) |
| DeepSeek V4 Pro | `deepseek-v4-pro` | $0.66 / $1.98 off-peak; $1.32 / $3.96 peak | 1M context; quality closer to GLM |
| DeepSeek V4 Flash Free | `deepseek-v4-flash-free` | Free | In the live catalog, not the docs pricing table. **200K** context vs 1M on the paid Flash |
| Kimi K2.6 | `kimi-k2.6` | $0.95 / $4.00 | 262K. Prefer K2.7 Code for coding |
| Hy3 Free | `hy3-free` | Free | Limited time; ~190K context; data may be used to train |
| Nemotron 3 Ultra Free | `nemotron-3-ultra-free` | Free | NVIDIA trial; 1M context; don’t submit confidential data |
| Nemotron 3.5 Lightning Free | `nemotron-3.5-lightning-free` | Free | Same NVIDIA trial terms; 262K |
| Ox Alpha Free | `x-preview-f-free` | Free | Stealth; 1M context; zero-retention, not used for training |
| Big Pickle | `big-pickle` | Free | Stealth; 200K; data may be used to train |
| Laguna S 2.1 Free | `laguna-s-2.1-free` | Free | In the live catalog, not the docs pricing table. 256K |
| Muse Spark 1.2 Contributor Free | `muse-spark-1.2-contributor-free` | Free | Meta; 1M context; trains on prompts/completions |

Grok, GPT, Claude, Gemini, and Qwen Plus SKUs on Zen are closed. See [opencode-zen-frontier.md](opencode-zen-frontier.md).
