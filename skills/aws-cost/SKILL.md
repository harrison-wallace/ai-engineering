---
name: aws-cost
description: AWS cost for one account, read-only. `mtd` (default) breaks down month-to-date spend by service and region from Cost Explorer, with run-rate, month-end forecast, and the change from last month. `optimize` finds savings from Cost Optimization Hub and Compute Optimizer plus direct sweeps for idle or orphaned resources (unattached EBS, unused EIPs, idle NAT gateways and load balancers, gp2 volumes, unretained log groups) and Savings Plans gaps, ranked by estimated monthly saving. Report-only tables. Triggers on "/aws-cost", "/aws-cost optimize", "what am I spending on AWS", "AWS cost breakdown", "month to date AWS bill", "reduce my AWS bill", "AWS cost savings", "cost optimisation", or "what can I turn off".
argument-hint: "[mtd | optimize]"
---

# aws-cost

Read-only AWS cost reports for **one account**. Every dollar figure is an estimate, and nothing
here changes infrastructure.

| First argument | Answers | Follow |
|---|---|---|
| none, or `mtd` | What am I spending, how does it compare to last month, and where is the month heading? | [`references/mtd.md`](references/mtd.md) |
| `optimize` | What can I change to spend less, ranked by monthly saving? | [`references/optimize.md`](references/optimize.md) |

Read the reference for the mode and follow it in full, including its step 0 cost gate. Cost
Explorer API calls cost money, so the gate always runs first.

For per-bucket S3 security and cost, use `/aws-audit s3`.

## Page (on request)

End each report with one line: *"Reply `page` for charts of this report, served on your LAN."*
When the user replies `page`, read `../serve-page/SKILL.md` (relative to this skill's folder, resolved with `readlink -f`) and follow its §1 to §4. Load the `dataviz` skill before you draw a chart. Write
`<scratchpad>/aws-cost/<mode>-<date>/index.html`.

- **`mtd`**: spend by service as a ranked bar chart, spend by region, this month against last
  month, and the run-rate with the month-end forecast. Each figure is labelled as an estimate.
- **`optimize`**: the savings as a ranked bar chart by estimated monthly saving, with each
  resource, its action, and its risk in a table below.

The page holds the account ID, spend figures, and resource IDs, so it carries the sensitive-page
warning. Stop the server when the user says they are done.
