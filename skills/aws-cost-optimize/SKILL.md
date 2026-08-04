---
name: aws-cost-optimize
description: Find AWS cost savings — Cost Optimization Hub and Compute Optimizer recommendations plus direct sweeps for idle/orphaned resources (unattached EBS, unused EIPs, idle NAT gateways and load balancers, gp2 volumes, unretained log groups) and Savings Plans coverage gaps. Single account, report-only table ranked by estimated monthly saving. Triggers on "/aws-cost-optimize", "reduce my AWS bill", "AWS cost savings", "cost optimisation", or "what can I turn off".
---

# aws-cost-optimize

A read-only sweep for **actionable AWS savings** in one account, ranked by
estimated monthly dollars, each with the effort and risk of acting on it.

Two sources, both needed:

1. **AWS's own recommendations** — accurate, but require opt-in enrolment and
   only cover rightsizing and commitments.
2. **Direct sweeps** — orphaned and idle resources that no recommender flags
   well, found by querying the services directly. This is where the surprise
   money usually is.

For "what am I spending", use `aws-cost-mtd`. For S3 specifically, use
`aws-s3-audit` — this skill defers to it rather than duplicating those checks.

**Scope: one account per run.** Do not assume-role into other accounts. If the
profile is an Organizations management account, note that these findings cover
the payer account only.

## 0. Confirm the cost before spending anything

Most of this skill is free, but the Cost Explorer calls are not — **$0.01 per
request**, on the user's bill. That's the region-spend query in step 1 plus the
four commitment-coverage calls and rightsizing in step 4: roughly 6 requests,
about $0.06. Get explicit approval before any of them.

Everything else here — `ec2`, `elbv2`, `rds`, `logs`, `cloudwatch`,
`compute-optimizer`, `cost-optimization-hub`, `sts` — is free and needs no
approval.

1. Run the free identity calls in step 1 first.
2. **Ask, then stop and wait**, naming the account and the total:

   > Ready to sweep **acme-prod (1234-5678-9012)** via profile `default`. The
   > resource sweeps are free; the Cost Explorer queries (region spend, Savings
   > Plans and RI coverage, rightsizing) are 6 requests at $0.01 — **about
   > $0.06**. Go ahead?

3. If the user declines the Cost Explorer portion but wants the rest, that's a
   perfectly good run: sweep every region for orphans instead of narrowing by
   spend, skip section 4 entirely, and say in the report that commitment
   coverage was not assessed.

Same rules as `aws-cost-mtd`: the gate is blocking, prior approval in the
original request counts, re-runs bill again and re-ask, and once approved stay
inside the approved request count rather than retrying speculatively.

## 1. Establish the account and regions

```bash
aws sts get-caller-identity --output json
aws ec2 describe-regions --query 'Regions[].RegionName' --output text
```

Confirm the profile with the user if ambiguous (see `aws-cost-mtd` step 1).

**Region strategy matters for runtime.** Sweeping 30+ regions is slow. Ask Cost
Explorer which regions actually have spend (one $0.01 call) and sweep those in
depth — but still check *every* enabled region for unattached volumes and
unassociated Elastic IPs, because orphans hide in regions you forgot you used:

```bash
aws ce get-cost-and-usage --region us-east-1 \
  --time-period Start=$(date -u -d '30 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) \
  --granularity MONTHLY --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=REGION --output json
```

## 2. AWS-native recommendations (fast, if enrolled)

```bash
# Cost Optimization Hub — aggregates everything, needs opt-in
aws cost-optimization-hub list-recommendations --region us-east-1 \
  --include-all-recommendations --output json 2>&1 | head -100

# Compute Optimizer — needs opt-in, needs ~14 days of CloudWatch history
aws compute-optimizer get-ec2-instance-recommendations --output json 2>&1 | head -60
aws compute-optimizer get-ebs-volume-recommendations   --output json 2>&1 | head -40
aws compute-optimizer get-lambda-function-recommendations --output json 2>&1 | head -40
aws compute-optimizer get-auto-scaling-group-recommendations --output json 2>&1 | head -40

# Cost Explorer rightsizing (no enrolment needed)
aws ce get-rightsizing-recommendation --region us-east-1 \
  --service AmazonEC2 --output json

# Trusted Advisor cost checks — Business/Enterprise support only
aws support describe-trusted-advisor-checks --language en --region us-east-1 \
  --query 'checks[?category==`cost_optimizing`].[id,name]' --output text 2>&1 | head -20
```

Handle non-enrolment gracefully: `OptInRequired`, `AccessDeniedException`, and
`SubscriptionRequiredException` are **not** failures to report as errors. Note
once, in a short "not available" line at the end of the report, that enabling
Cost Optimization Hub and Compute Optimizer (both free) would add coverage —
then carry on with the direct sweeps, which need no enrolment.

Where AWS supplies its own savings figure, use it and attribute it — it beats
anything derived here.

## 3. Direct sweeps (where the surprise money is)

Run per region. Each is read-only.

**Unattached EBS volumes** — billed in full while detached:

```bash
aws ec2 describe-volumes --region $R \
  --filters Name=status,Values=available \
  --query 'Volumes[].[VolumeId,Size,VolumeType,CreateTime]' --output text
```

**gp2 volumes** — gp3 is ~20% cheaper at equal or better baseline performance:

```bash
aws ec2 describe-volumes --region $R --filters Name=volume-type,Values=gp2 \
  --query 'Volumes[].[VolumeId,Size,State]' --output text
```

**Unassociated Elastic IPs** — since Feb 2024 *every* public IPv4 is charged
(~$3.60/mo each), and idle ones are charged too:

```bash
aws ec2 describe-addresses --region $R \
  --query 'Addresses[?AssociationId==`null`].[PublicIp,AllocationId]' --output text
```

**Stopped EC2 instances** — compute is free, attached EBS is not:

```bash
aws ec2 describe-instances --region $R \
  --filters Name=instance-state-name,Values=stopped \
  --query 'Reservations[].Instances[].[InstanceId,InstanceType,LaunchTime,StateTransitionReason]' \
  --output text
```

Stopped for months is a strong signal; stopped yesterday is not.

**Idle NAT gateways** (~$32/mo each before data charges) — enumerate, then check
`BytesOutToDestination` in CloudWatch over 14 days; near-zero means idle:

```bash
aws ec2 describe-nat-gateways --region $R \
  --query 'NatGateways[?State==`available`].[NatGatewayId,VpcId]' --output text
aws cloudwatch get-metric-statistics --region $R \
  --namespace AWS/NATGateway --metric-name BytesOutToDestination \
  --dimensions Name=NatGatewayId,Value=$NAT \
  --start-time $(date -u -d '14 days ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 86400 --statistics Sum --output json
```

**Load balancers with no healthy targets** (~$16–22/mo each):

```bash
aws elbv2 describe-load-balancers --region $R \
  --query 'LoadBalancers[].[LoadBalancerArn,LoadBalancerName,Type]' --output text
aws elbv2 describe-target-health --region $R --target-group-arn $TG --output json
```

**Old EBS snapshots** — cheap each, expensive in aggregate:

```bash
aws ec2 describe-snapshots --region $R --owner-ids self \
  --query 'Snapshots[].[SnapshotId,VolumeSize,StartTime,Description]' --output text
```

Flag snapshots older than ~1 year with no matching AMI or live volume. **Never
recommend deleting something that might be a backup** without saying exactly
that.

**Idle RDS instances** — check `DatabaseConnections` over 14 days:

```bash
aws rds describe-db-instances --region $R \
  --query 'DBInstances[].[DBInstanceIdentifier,DBInstanceClass,Engine,MultiAZ]' --output text
```

Also flag `MultiAZ` on obviously non-production instances (doubles the cost) and
manual snapshots belonging to long-deleted instances.

**CloudWatch log groups with no retention** — infinite retention, growing forever:

```bash
aws logs describe-log-groups --region $R \
  --query 'logGroups[?retentionInDays==`null`].[logGroupName,storedBytes]' --output text
```

**Idle or oversized ECS, EKS, ElastiCache, Redshift, OpenSearch** — enumerate
only if step 1's region spend shows them; look for provisioned-but-idle capacity.

## 4. Commitment coverage (usually the biggest single lever)

```bash
aws ce get-savings-plans-coverage --region us-east-1 \
  --time-period Start=$(date -u -d '30 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) --output json
aws ce get-savings-plans-purchase-recommendation --region us-east-1 \
  --savings-plans-type COMPUTE_SP --term-in-years ONE_YEAR \
  --payment-option NO_UPFRONT --lookback-period-in-days SIXTY_DAYS --output json
aws ce get-reservation-coverage --region us-east-1 \
  --time-period Start=$(date -u -d '30 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) --output json
aws ce get-reservation-utilization --region us-east-1 \
  --time-period Start=$(date -u -d '30 days ago' +%Y-%m-%d),End=$(date -u +%Y-%m-%d) --output json
```

Low **utilisation** is a problem (paying for unused commitment); low **coverage**
is an opportunity — opposite failure modes, report them differently.

Never present a commitment purchase as a confident action: it is a 1–3 year
financial lock-in. Give the figure, the break-even, and the assumption it rests
on (steady-state usage continuing), and leave the decision with the user.

## 5. Report

One table, descending by estimated monthly saving:

| Est. $/mo | Finding | Resource | Region | Effort | Risk |
|---:|---|---|---|---|---|
| ~$128 | 4 idle NAT gateways, <1 MB egress in 14d | `nat-0a1…`, +3 | eu-west-1 | Low | Med — verify no private-subnet egress needed |
| ~$64 | 8 unattached EBS volumes, 640 GB total | `vol-0f2…`, +7 | eu-west-1 | Low | Low — snapshot first |
| ~$41 | 21 gp2 volumes → gp3 | — | multi | Low | Low — live modification, no downtime |
| ~$38 | Savings Plan coverage 12% on steady EC2 | — | — | Med | **High — 1yr lock-in** |

Follow with a totals line and a short "not available" note for anything not
enrolled or not permitted.

Rules:

- **Report-only.** Never delete a volume, release an EIP, modify a volume type,
  delete a snapshot, set a retention policy, or buy a Savings Plan. Not when
  it's obviously right, and not when asked mid-run — any change needs a separate
  explicit instruction, one resource at a time.
- **Every dollar figure is an estimate and must read as one.** Prefix with `~`,
  head the column "Est. $/mo", and state the basis once under the table (e.g.
  "derived from published on-demand pricing for the resource's region; excludes
  data-transfer and request charges"). Where AWS itself supplied the number,
  say so — those are better. Never present a computed saving as guaranteed, and
  never total them into a headline "you will save $X".
- **The risk column is mandatory and honest.** "Idle" from a 14-day metric
  window can mean quarterly batch, DR standby, or a compliance retention
  requirement. Say what you checked and over what window.
- **Scale the noise floor to the size of the bill.** Group findings into a
  single "small items" row when each is below **~1% of monthly spend**, or below
  ~$5/mo once the bill is over ~$500/month. A flat dollar floor is wrong on
  small accounts — on a $20/month bill a $5 floor buries findings worth a
  quarter of the spend. Exception either way: keep a row of its own if it is
  trivially safe to remove.
- If a sweep found nothing, say so — a clean region is a real result.
