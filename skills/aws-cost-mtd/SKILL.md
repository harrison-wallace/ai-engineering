---
name: aws-cost-mtd
description: Month-to-date AWS cost breakdown by service and region via Cost Explorer, with run-rate, month-end forecast, and deltas vs last month. Single account, report-only tables. Triggers on "/aws-cost-mtd", "what am I spending on AWS", "AWS cost breakdown", or "month to date AWS bill".
---

# aws-cost-mtd

A read-only month-to-date spend report for **one AWS account**, rendered as
tables: where the money went, how it compares to last month, and where the
month is heading.

Not an optimisation pass — for "what should I change to spend less", use
`aws-cost-optimize`. Not a per-bucket S3 breakdown — that's `aws-s3-audit`.

**Scope: one account per run.** If the profile turns out to be an
Organizations management account, say so and report the payer total, then ask
which member account the user wants before going further. Do not assume-role
into member accounts.

## 0. Confirm the cost before spending anything

Cost Explorer charges **$0.01 per API request**, so running this skill costs
real money on the user's bill. Get explicit approval first.

Order of operations — the identity checks in step 1 are free, so do them
**before** asking, and fold the account into the question. Nobody can approve a
spend without knowing which account it's for.

1. Run the free calls in step 1 (`sts get-caller-identity`,
   `list-account-aliases`, `configure list-profiles`).
2. Decide the full set of Cost Explorer queries you intend to make (step 4), so
   the count is real rather than a guess.
3. **Ask, then stop and wait.** State the account, the profile, the number of
   requests, and the dollar total:

   > Ready to query Cost Explorer for **acme-prod (1234-5678-9012)** via profile
   > `default`. That's 7 requests at $0.01 each — **about $0.07** on this
   > account's bill. Go ahead?

4. Only after the user agrees, run the queries.

Rules for this gate:

- **It is blocking.** Do not run a single `ce` command before approval, not even
  a "quick check" to make the estimate more accurate.
- If the user's original request already said something like "yes, run it, I
  don't care about the cents", treat that as approval — state the cost in one
  line and proceed without a second prompt.
- Re-running in the same session bills again. If the user asks for another
  breakdown (a different grouping, another month), say what the extra calls cost
  and confirm again — cheaply, one line, but confirm.
- Once approved, **stay inside the approved budget**. Do not loop, retry
  speculatively, or re-run a query with tweaked parameters "to check" — decide
  the query first, then run it once. If a call fails, read the error rather than
  retrying blind. If you genuinely need queries beyond what was approved, go
  back and ask.
- The free calls stay free: `sts`, `iam list-account-aliases`, and
  `configure list-profiles` are not billed and need no approval.

## 1. Establish the account

Never report numbers without saying which account they're for.

```bash
aws configure list-profiles
aws sts get-caller-identity --output json          # add --profile <name> as needed
aws iam list-account-aliases --output text 2>/dev/null
```

- If the user named a profile, use it. If not and more than one profile exists,
  **ask which** before spending API calls — a report for the wrong account is
  worse than no report.
- Cost Explorer is a global service. Always pass `--region us-east-1`.
- If Cost Explorer has never been enabled, the first call fails with
  `DataUnavailableException`. Say so and stop — it takes ~24h to populate.

## 2. Fix the date window

```bash
START=$(date -u +%Y-%m-01)
END=$(date -u -d tomorrow +%Y-%m-%d)        # End is EXCLUSIVE
PREV_START=$(date -u -d "$START -1 month" +%Y-%m-%d)
PREV_END=$START
DAY_OF_MONTH=$(date -u +%-d)
```

Two caveats to state in the report, not to silently absorb:

- Cost Explorer data lags **up to 24h**, so "today" is usually partial or zero.
- Usage-based charges post throughout the day; MTD is an estimate, not an invoice.

## 3. Pick the metric deliberately

| Metric | Use when |
|---|---|
| `UnblendedCost` | Default. What the account is actually charged, line by line. |
| `AmortizedCost` | The account has Savings Plans or Reserved Instances — spreads upfront fees across the term instead of spiking on the purchase day. |
| `NetAmortizedCost` | As above, but after discounts/credits — closest to the real invoice. |

Check for commitments first:

```bash
aws ce get-savings-plans-utilization --region us-east-1 \
  --time-period Start=$START,End=$END --output json 2>/dev/null
```

If Savings Plans or RIs exist, run the main breakdown with **both**
`UnblendedCost` and `AmortizedCost` in a single `--metrics` call (same request,
no extra charge) and report amortized as the headline. Say which you used.

Exclude credits and refunds from the "what am I spending" view — they distort
service attribution:

```bash
--filter '{"Not":{"Dimensions":{"Key":"RECORD_TYPE","Values":["Credit","Refund"]}}}'
```

Report total credits applied as a separate line, not folded into services.

## 4. The breakdowns

**By service (the headline table):**

```bash
aws ce get-cost-and-usage --region us-east-1 \
  --time-period Start=$START,End=$END \
  --granularity MONTHLY \
  --metrics UnblendedCost AmortizedCost \
  --group-by Type=DIMENSION,Key=SERVICE \
  --filter '{"Not":{"Dimensions":{"Key":"RECORD_TYPE","Values":["Credit","Refund"]}}}' \
  --output json
```

**Same window, previous month** (for the delta column) — reuse the call with
`Start=$PREV_START,End=$PREV_END` and `--granularity MONTHLY`. To compare like
for like, prorate: previous month's same-day-count, not its full total. State
which comparison you used.

**Daily trend** — one call, `--granularity DAILY`, no grouping. Use it to spot
a step change (a resource left running) rather than to fill a table. Call out
any day more than ~40% above the MTD daily median.

**By region** — only if the service table shows meaningful EC2/data-transfer
spend, or the user asked. Group `Type=DIMENSION,Key=REGION`.

**By tag or usage type** — only when the user asks "what is X costing me".
Group `Type=TAG,Key=<tag>` or `Type=DIMENSION,Key=USAGE_TYPE`. Untagged spend
is itself worth reporting if a cost-allocation tag is in use.

**Forecast:**

```bash
aws ce get-cost-forecast --region us-east-1 \
  --time-period Start=$(date -u +%Y-%m-%d),End=$(date -u -d "$(date -u +%Y-%m-01) +1 month" +%Y-%m-%d) \
  --metric UNBLENDED_COST --granularity MONTHLY --output json
```

Forecast fails on accounts with under ~a month of history — degrade to a simple
run-rate (`MTD / days_elapsed * days_in_month`) and label it as such.

## 5. Report

Header line: account alias + ID, profile used, window, metric, data-as-of date.

**Spend by service** — descending, top 10–15 rows, everything else as "Other":

| Service | MTD | % of total | Prev month (same days) | Δ |
|---|---:|---:|---:|---:|
| Amazon EC2 | $412.80 | 38% | $377.10 | +9% |
| Amazon RDS | $190.22 | 18% | $188.90 | +1% |

**Summary:**

| | |
|---|---:|
| MTD total (actual) | $1,082.45 |
| Daily run-rate | $38.66 |
| Forecast month-end (**estimate**) | $1,198.00 |
| Last month, full | $1,141.30 |
| Credits applied | −$50.00 |

Rules:

- **Report-only.** No purchases, no Savings Plan commitments, no budget
  creation, no resource changes. Ever.
- **Label estimates as estimates.** MTD and previous-month figures are actuals
  from Cost Explorer; the forecast and run-rate are not. Mark them in the table
  and never present a forecast as what the bill will be.
- Round to cents; use the account's billing currency, don't convert.
- **Scale the noise floor to the size of the bill.** Fold a service into "Other"
  when it is below **0.5% of the MTD total**, or below $1.00 once the bill is
  over ~$500/month. A flat dollar floor is wrong on small accounts — on a $7
  bill it collapses everything but the top two or three rows and hides the whole
  long tail, which is exactly where an unexpected new service shows up. Say how
  many services "Other" covers and what they total.
- Close with 1–3 plain-language observations (a step change, a service that
  jumped, an unexpected region), **not** recommendations. If the user wants
  recommendations, point them at `aws-cost-optimize`.
- If a query returns nothing, say the query and why it might be empty. Never
  present a zero as a fact without checking the account is right.
