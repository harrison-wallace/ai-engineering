---
name: aws-s3-audit
description: Audit every S3 bucket in an account for security best practices (public access, encryption, TLS-only, versioning, logging, ownership) and cost savings (lifecycle gaps, noncurrent-version bloat, incomplete multipart uploads, storage-class fit). Two report-only tables — security by severity, savings by estimated monthly cost. Triggers on "/aws-s3-audit", "audit my S3 buckets", "are my buckets public", or "S3 cost savings".
---

# aws-s3-audit

A read-only, per-bucket audit of **one AWS account**, answering two questions in
a single pass:

1. **Is this bucket configured safely?** — public exposure, encryption, TLS,
   ownership, versioning, logging.
2. **Is it costing more than it should?** — lifecycle gaps, version bloat,
   abandoned multipart uploads, wrong storage class.

Both are per bucket and share the same enumeration, so they run together.

## 0. Never list objects to measure size

`aws s3 ls --recursive --summarize` on a large bucket makes millions of LIST
requests, is billed, and can take hours. **Use CloudWatch daily storage metrics
instead** — free, instant, accurate to within a day (step 4).

Only fall back to listing when CloudWatch shows the bucket is small (< ~10k
objects) *and* the user asked for object-level detail. Cap it with `--max-items`.

## 1. Enumerate

```bash
aws sts get-caller-identity --output json
aws s3api list-buckets --query 'Buckets[].[Name,CreationDate]' --output text
aws s3control get-public-access-block --account-id $ACCOUNT_ID --output json 2>&1
```

The **account-level** public access block is the single highest-value setting —
check it first. If all four flags are true account-wide, per-bucket public
exposure drops to informational; say so and re-rank accordingly.

Get each bucket's region (calls fail against the wrong regional endpoint):

```bash
aws s3api get-bucket-location --bucket $B --output text
```

If there are more than ~50 buckets, say so and confirm scope before proceeding —
each bucket costs roughly ten API calls.

## 2. Security checks (per bucket)

Every one of these returns an error when unconfigured.
`NoSuchPublicAccessBlockConfiguration`,
`ServerSideEncryptionConfigurationNotFoundError`, `NoSuchLifecycleConfiguration`,
and `NoSuchBucketPolicy` mean **"not set"**, which is usually the finding — do
not report them as tool errors.

```bash
aws s3api get-public-access-block --bucket $B --output json 2>&1
aws s3api get-bucket-policy-status --bucket $B --output json 2>&1   # IsPublic
aws s3api get-bucket-policy --bucket $B --output json 2>&1
aws s3api get-bucket-acl --bucket $B --output json
aws s3api get-bucket-ownership-controls --bucket $B --output json 2>&1
aws s3api get-bucket-encryption --bucket $B --output json 2>&1
aws s3api get-bucket-versioning --bucket $B --output json
aws s3api get-bucket-logging --bucket $B --output json
aws s3api get-bucket-replication --bucket $B --output json 2>&1
```

| Check | Severity if failing | Why |
|---|---|---|
| Public access block — any of 4 flags off | 3 if `IsPublic` also true, else 2 | The mechanism that prevents accidental exposure |
| Bucket policy grants `Principal: "*"` | 3 | Verify intent — a static-site or public-assets bucket is legitimate; say which you assumed |
| ACL grants to `AllUsers` / `AuthenticatedUsers` | 3 | `AuthenticatedUsers` means *any* AWS account, not just yours |
| Object Ownership ≠ `BucketOwnerEnforced` | 1 | Leaves ACLs live; enforced mode disables them entirely |
| No default encryption | 2 | SSE-S3 is free and on by default for new buckets; absence means an old bucket |
| No `aws:SecureTransport: false` deny in policy | 2 | Nothing blocks plaintext HTTP access |
| Versioning off | 1 (2 if it holds backups or state) | No recovery from overwrite, delete, or ransomware |
| No server access logging / CloudTrail data events | 1 | No forensic trail |
| No MFA delete on critical buckets | 0–1 | Informational; rarely worth the operational cost |
| SSE-KMS without `BucketKeyEnabled` | 1 (also a cost finding) | Up to 99% fewer KMS requests — fixes cost and throttling together |

For any bucket that is genuinely public, state it in plain words at the top of
the report — not buried in a table row.

## 3. Cost checks (per bucket)

```bash
aws s3api get-bucket-lifecycle-configuration --bucket $B --output json 2>&1
aws s3api list-multipart-uploads --bucket $B --output json 2>&1 | head -40
aws s3api get-bucket-intelligent-tiering-configuration --bucket $B --id default --output json 2>&1
```

| Finding | Why it costs |
|---|---|
| No lifecycle rule aborting incomplete multipart uploads | Orphaned parts are billed **forever** and are invisible in the console object list. The most common silent S3 cost. |
| Versioning on, no noncurrent-version expiry | Every overwrite keeps the old copy at full price, indefinitely |
| No transition rules on a large, cold bucket | Standard costs ~4.5× Glacier Instant Retrieval |
| Logs or backups sitting in Standard | Textbook Standard-IA or Glacier candidates |
| Intelligent-Tiering not enabled on unpredictable access | Auto-tiering with no retrieval fee; ~$0.0025/1k objects monitoring, so a bad fit for many tiny objects |
| Many objects < 128 KB | Standard-IA and Glacier bill a 128 KB minimum per object — transitioning these *increases* cost |
| Cross-region replication with no lifecycle on the target | Pays twice, forever |

## 4. Size and storage-class distribution (CloudWatch, free)

```bash
for T in StandardStorage StandardIAStorage IntelligentTieringFAStorage \
         GlacierInstantRetrievalStorage GlacierStorage DeepArchiveStorage; do
  aws cloudwatch get-metric-statistics --region $BUCKET_REGION \
    --namespace AWS/S3 --metric-name BucketSizeBytes \
    --dimensions Name=BucketName,Value=$B Name=StorageType,Value=$T \
    --start-time $(date -u -d '3 days ago' +%Y-%m-%dT%H:%M:%SZ) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
    --period 86400 --statistics Average --output json
done

aws cloudwatch get-metric-statistics --region $BUCKET_REGION \
  --namespace AWS/S3 --metric-name NumberOfObjects \
  --dimensions Name=BucketName,Value=$B Name=StorageType,Value=AllStorageTypes \
  --start-time $(date -u -d '3 days ago' +%Y-%m-%dT%H:%M:%SZ) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
  --period 86400 --statistics Average --output json
```

Empty metrics mean an empty bucket or one under ~24h old — say which. Compute
average object size from these two; it decides whether a storage-class
transition helps or hurts (128 KB minimum billing, above).

If S3 Storage Lens is enabled, point at its dashboard as the better ongoing
view rather than re-deriving everything here.

## 5. Report

Open with a one-line verdict, naming any publicly-accessible bucket explicitly.

**Security** — highest severity first, one row per finding:

| Sev | Bucket | Finding | Detail |
|---|---|---|---|
| 3 | `assets-prod` | Publicly readable | Policy allows `s3:GetObject` to `*`; assumed intentional (static site) — confirm |
| 2 | `db-backups` | No default encryption | Bucket predates the 2023 default |

| Sev | Meaning |
|---|---|
| 3 | Data exposed or exposable now — public access, world-writable policy |
| 2 | Materially weakens security — no encryption, no TLS enforcement, PAB off |
| 1 | Hardening gap — versioning, logging, ownership mode |
| 0 | Observation |

**Cost** — descending by estimated monthly saving:

| Est. $/mo | Bucket | Finding | Suggested action |
|---:|---|---|---|
| ~$47 | `media-uploads` | 1.9 TB incomplete multipart uploads, no abort rule | 7-day `AbortIncompleteMultipartUpload` rule |
| ~$31 | `db-backups` | 840 GB noncurrent versions, no expiry | Noncurrent expiry after 30d |
| ~$12 | `logs-archive` | 400 GB Standard, avg object 4 MB, cold | Transition to Glacier IR at 90d |

Rules:

- **Report-only.** Never put, modify, or delete a bucket policy, lifecycle rule,
  encryption config, public access block, or any object. An audit that changes
  configuration is not an audit.
- **Every saving is an estimate and must read as one.** Prefix with `~`, head
  the column "Est. $/mo", and state the basis under the table (storage class
  list price for the bucket's region, from CloudWatch-reported bytes; excludes
  request and retrieval charges). Never total them into a promised figure.
- A public bucket may be entirely correct. Say what the bucket appears to be for
  and ask the user to confirm — don't flag it as a breach.
- Storage-class recommendations must state the average object size they assume;
  transitioning many small objects costs more, not less.
- Never recommend expiring noncurrent versions or old backups without noting
  that it is irreversible and that retention requirements may apply.
- If a check fails on permissions (`AccessDenied` on `get-bucket-policy`), list
  the bucket as **not fully audited** rather than passing it. Incomplete
  coverage reported as clean is the worst possible outcome.
- Clean result: one line stating buckets checked, checks per bucket, and that
  nothing above sev 0 was found.
