---
name: aws-audit
description: Read-only audit of one AWS account, one service at a time. `s3` (default, and the only service so far) audits every bucket for security practice (public access, encryption, TLS-only, versioning, logging, ownership) and cost savings (lifecycle gaps, noncurrent-version bloat, incomplete multipart uploads, storage-class fit), as two report-only tables. Triggers on "/aws-audit", "/aws-audit s3", "audit my S3 buckets", "are my buckets public", or "S3 cost savings".
argument-hint: "[s3]"
---

# aws-audit

Read-only security and cost audits for **one AWS account**, one service per run. Nothing here
changes infrastructure, and every dollar figure is an estimate.

| First argument | Audits | Follow |
|---|---|---|
| none, or `s3` | Every S3 bucket: security posture, then cost | [`references/s3.md`](references/s3.md) |

Read the reference for the service and follow it in full.

If the user names a service that has no reference yet (for example `iam` or `ec2`), say so in one
line and stop. Do not improvise an audit. A new service gets its own `references/<service>.md`,
built the same way as `s3.md`.

For account-wide spend or savings, use `/aws-cost`.
