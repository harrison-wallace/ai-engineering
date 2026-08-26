# OpenCode Zen — frontier / closed models

**Updated:** 2026-08-26

Checked today against the [Zen catalog](https://opencode.ai/docs/zen/), [Go catalog](https://opencode.ai/docs/go/), live [`/zen/v1/models`](https://opencode.ai/zen/v1/models), and live [`/zen/go/v1/models`](https://opencode.ai/zen/go/v1/models). Open-weight picks live in [opencode-zen-models.md](opencode-zen-models.md). Prices and the catalog move; re-check the date before treating a price as live.

Prices are per 1M tokens. Zen IDs are `opencode/<id>`. Context is 1M unless noted.

## Quick picks (Zen PAYG)

| Priority | Model | ID | In / out | Why |
|---|---|---|---|---|
| **Best daily driver** | Grok 4.6 | `grok-4.6` | $2.00 / $6.00 (≤200K) | Real frontier quality at MiniMax-adjacent money. AA Coding Index 76.8 (25 Aug). **500K context** |
| **Best quality** | Claude Opus 5 | `claude-opus-5` | $5.00 / $25.00 | Default frontier. SWE-bench Pro ~79%, AA Coding 78.0. Same price as Opus 4.8, better |
| **Ceiling** | Claude Fable 5 | `claude-fable-5` | $10.00 / $50.00 | Slim SWE-bench lead over Opus 5 at 2× the price. Escalate, don’t default |
| **Best GPT** | GPT 5.6 Sol | `gpt-5.6-sol` | $2.00 / $10.00 (≤272K) | Terminal / CLI agents. AA Coding 77.4. **50% off through 2026-09-18**. ~1.05M context |
| **Claude at volume** | Claude Sonnet 5 | `claude-sonnet-5` | $2.00 / $10.00 | Most of the Claude feel without Opus’s bill |
| **Cheap closed bulk** | GPT 5.6 Luna | `gpt-5.6-luna` | $0.20 / $1.20 (≤272K) | Same 5.6 family, ~10× cheaper than Sol on input. Not the quality pick |

Grok 4.6 above 200K is $4 / $12. Sol above 272K is $4 / $15. Zen’s listed Sol prices **include** the 50% discount through 18 Sep 2026; expect them to rise when it ends.

Skip older Opus 4.x, Grok 4.5, GPT 5.1/5.2 Codex (deprecation date 23 Jul 2026), Gemini 3 Pro, and Claude Sonnet 4. Several of those still appear in the live catalog — don’t start new work on them.

## Performance vs price

**Quality, roughly:** Fable 5 ≈ Opus 5 > GPT 5.6 Sol ≈ Grok 4.6 ≈ GPT 5.6 Terra > Sonnet 5 ≈ Gemini 3.7 Flash > Grok 4.5 > Luna / Haiku / Flash Lite

AA Coding Index snapshot (25 Aug 2026): Opus 5 **78.0**, Sol **77.4**, Grok 4.6 **76.8**, Terra **76.7**, Fable 5 **76.5**, Gemini 3.7 Flash **76.1**, Grok 4.5 **72.5**. SWE-bench Pro is more spread: Fable ~80%, Opus 5 ~79%, Sol ~65%, Sonnet 5 ~63%. Grok has no published SWE-bench figure; treat it as “frontier on agentic coding indexes, unproven on the SWE harness.”

**Value:** Grok 4.6 is the closed-model MiniMax M3. At $2 / $6 it undercuts Opus 5 by ~4× on output and sits next to Sol on the coding index. Sonnet 5 at $2 / $10 is the Claude-shaped daily if you want that stack. Sol at the current 50% Zen discount is the GPT daily until 18 Sep.

Opus 5 is still the one to switch to for architecture, long agent loops, and multi-file bugs where a wrong patch is expensive. Fable 5 is the “this one has to be right” button — twice Opus, not twice as good.

GPT 5.5 / 5.5 Pro ($5 / $30 and $30 / $180) are not the current GPT pick. Sol/Terra/Luna replaced them. Pro is a research tax.

Gemini 3.7 Flash ($1.50 / $7.50) punches above its price on coding indexes; Gemini 3.1 Pro ($2 / $12 ≤200K; $4 / $18 above) is the long-context / multimodal closed option (~1.05M).

**Qwen 3.7 Max/Plus are not in the live Zen PAYG catalog today.** They are on Go (`opencode-go/qwen3.7-max`, `qwen3.7-plus`), along with open-weight **Qwen3.8 Max**. See the [open-weight sheet](opencode-zen-models.md).

## What to actually run

1. Default: `opencode/grok-4.6`
2. Escalate: `opencode/claude-opus-5`
3. Ceiling: `opencode/claude-fable-5`
4. GPT / terminal: `opencode/gpt-5.6-sol` (while the 50% discount lasts)
5. Cheap closed volume: `opencode/gpt-5.6-luna` or `opencode/gemini-3.7-flash`

Pair with the open-weight default (`opencode/minimax-m3`) if the task doesn’t need a closed model.

## Grok

| Model | ID | In / out | Context | Notes |
|---|---|---|---|---|
| **Grok 4.6** | `grok-4.6` | $2 / $6 ≤200K; $4 / $12 above | 500K | Current Grok. Daily closed default. Cached read $0.50 |
| Grok 4.5 | `grok-4.5` | Same in/out as 4.6 | 500K | Prefer 4.6. Cached read $0.30. Still in live Zen and Go catalogs |
| Grok Build 0.1 | `grok-build-0.1` | $1 / $2 | 256K | Cheaper, not frontier. Fine for titles / small edits |

Grok 4.6 is also on [OpenCode Go](https://opencode.ai/docs/go/) (`opencode-go/grok-4.6`) but the $10 plan only budgets **$15 of Grok usage** (**845** requests/month on Go’s estimate). Heavy Grok belongs on Zen PAYG, not Go. Live Go catalog also still serves `grok-4.5`.

Privacy: Go documents Grok as **not used for training, 30-day retention**. Zen’s privacy page lists ZDR as the default and does **not** name Grok as an exception. Don’t pick Grok for whole-repo dumps that need >500K context (Opus 5 / Sol / Gemini are ~1M).

## Other closed models on Zen (PAYG)

| Model | ID | In / out | Notes |
|---|---|---|---|
| GPT 5.6 Terra | `gpt-5.6-terra` | $2.00 / $12.00 (≤272K); $4 / $18 above | Sol’s sibling; slightly dearer, similar quality. ~1.05M context |
| GPT 5.6 Luna | `gpt-5.6-luna` | $0.20 / $1.20 (≤272K); $0.40 / $1.80 above | Cheap 5.6. Also on Go ($15 budget) |
| GPT 5.4 Mini | `gpt-5.4-mini` | $0.75 / $4.50 | 400K context. Mid-cheap GPT if Luna is too thin |
| GPT 5.4 Nano | `gpt-5.4-nano` | $0.20 / $1.25 | 400K. Titles / routing, not coding |
| GPT 5.3 Codex | `gpt-5.3-codex` | $1.75 / $14.00 | 400K. Coding-tuned; Sol is the current GPT |
| GPT 5.5 Pro | `gpt-5.5-pro` | $30.00 / $180.00 | Don’t |
| Claude Opus 4.8 | `claude-opus-4-8` | $5.00 / $25.00 | Same price as Opus 5; prefer 5. 1M context |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | $3.00 / $15.00 | Prefer Sonnet 5 at $2 / $10 |
| Claude Haiku 4.5 | `claude-haiku-4-5` | $1.00 / $5.00 | **200K** context. Fast Claude; Luna is cheaper |
| Gemini 3.7 Flash | `gemini-3.7-flash` | $1.50 / $7.50 | Strong coding index for the price. ~1.05M |
| Gemini 3.6 Flash | `gemini-3.6-flash` | $1.50 / $7.50 | Prefer 3.7 |
| Gemini 3.5 Flash | `gemini-3.5-flash` | $1.50 / $9.00 | Older Flash; 3.7 is the same input, cheaper output |
| Gemini 3.5 Flash Lite | `gemini-3.5-flash-lite` | $0.30 / $2.50 | Cheap Gemini volume |
| Gemini 3.1 Pro | `gemini-3.1-pro` | $2.00 / $12.00 (≤200K); $4 / $18 above | Long-context / multimodal |
| Gemini 3 Flash | `gemini-3-flash` | $0.50 / $3.00 | Older Flash |
| Qwen3.6 Plus | `qwen3.6-plus` | $0.50 / $3.00 | Closed Alibaba SKU. **On Zen PAYG today** |
| Qwen3.5 Plus | `qwen3.5-plus` | $0.20 / $1.20 | Closed, cheap Qwen. On Zen PAYG |
| Muse Spark 1.2 | `muse-spark-1.2` | $1.25 / $4.25 | Meta, ~1.05M. Contributor-free variant trains on your data |

OpenAI and Anthropic APIs on Zen retain requests 30 days. Muse Spark Contributor Free is the one that trains on prompts.

Qwen3.7 Max ($2.50 / $7.50) and Qwen3.7 Plus ($0.40 / $1.60) are in the **docs** and on **Go**, but they are **not** in live `/zen/v1/models` today.

## OpenCode Go

Go is the **open-weight** $10/month plan. Closed models on it are the exception: **Grok 4.6** and **GPT 5.6 Luna**, both on a **$15** usage budget (Luna estimate ~10,250 requests/month; Grok ~845). Live Go also still lists `grok-4.5`.

Use Go for MiniMax / GLM-5.3 / DeepSeek / Qwen3.8 Max; use Zen credits for Opus, Fable, Sol, and heavy Grok.
