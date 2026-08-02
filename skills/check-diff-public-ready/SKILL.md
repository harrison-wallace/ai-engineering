---
name: check-diff-public-ready
description: Pass over the current git diff for material that is unsafe to push to a public repository (secrets, PII, internal URLs, private keys, credentials, accidental dumps). Report-only severity table. Triggers on "/check-diff-public-ready", "is this diff public-ready", or "safe for public repo" (diff scope).
---

# check-diff-public-ready

A focused, report-only pass on the **working diff** (or last commit if clean) asking:
would this be safe to land on a **public** GitHub/GitLab/etc. repo?

Not a general code review. Only flag public-exposure risk introduced or touched by
the diff. For a whole-tree audit, use `check-repo-public-ready`.

## 1. Collect the diff

```bash
git status --short
git diff HEAD            # staged + unstaged
```

If the tree is clean, review the last commit instead (`git diff HEAD~1..HEAD`) and
say so. Also list any **new untracked files** that look like they might be staged
soon (`git status -u`) — untracked secrets are a common miss before the first add.

Read enough of each changed/new file to judge content; do not audit untouched code.

## 2. Scan for public-exposure risks

Check only what the diff adds or modifies. Categories:

### Secrets & credentials
- API keys, tokens, passwords, private keys (PEM/SSH), client secrets
- Connection strings with passwords, DB URLs with credentials
- Cloud access keys (AWS `AKIA…`, GCP service-account JSON, Azure keys)
- OAuth client secrets, webhook signing secrets, JWT signing keys
- `.env`, `.env.*`, `credentials.json`, `*.pem`, `*.p12`, `id_rsa`, etc. added or
  filled with real values (placeholder/`CHANGE_ME`/`xxx` is fine)
- Hard-coded auth headers, Basic auth, bearer tokens in source or examples

### PII & personal data
- Real names + contact info, personal emails/phones, home addresses
- Customer lists, user dumps, production exports, session logs with identities
- Personal notes, private calendar details, medical/financial data

### Internal / non-public infrastructure
- Internal hostnames, VPN-only URLs, private IP ranges used as "real" config
- Internal package registries, private monorepo paths that leak org structure
  *and* credentials together
- Staging/prod admin URLs, internal dashboards, runbooks with access steps

### Repo hygiene that leaks on public
- Real secrets in comments, TODOs, or test fixtures ("// password is hunter2")
- Screenshots or fixtures embedding tokens/emails
- Large accidental dumps (DB dumps, heap dumps, full `.env` copies) in the diff
- License-incompatible third-party code newly vendored without attribution
- References to private tickets/docs that include tokens in the URL

### Config & debug left dangerous for public consumers
- Debug flags, verbose auth logging, or `dangerouslyAllow…`-style toggles
  **defaulted on** in committed config
- Overly permissive CORS/`0.0.0.0` binds with real credentials nearby
- CI/CD config that prints secrets or uses unmasked secret variables incorrectly
  (flag only if the diff shows the leak pattern)

**Do not flag** (unless clearly real secrets):
- Example values that are obviously fake (`sk-test-…`, `your-api-key-here`,
  `xxxx`, `REDACTED`, local `localhost` without passwords)
- Public keys, public URLs, open-source license text
- `.env.example` with empty or placeholder values
- Pre-existing issues outside the diff (note severity-3 only if the diff
  *spreads* or *copies* an existing secret into a new public path)

## 3. Heuristic greps (optional, on the diff)

When helpful, run targeted searches over the diff or changed files, e.g.:

```bash
git diff HEAD | rg -i 'api[_-]?key|secret|password|token|private[_-]?key|BEGIN (RSA |OPENSSH |EC )?PRIVATE|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-'
git status -u --short | rg -i '\.env|credentials|\.pem|\.p12|id_rsa|service.account|\.key$'
```

Treat hits as leads, not automatic findings — confirm they are real and new.

## 4. Report

Output a single table, highest severity first:

| Sev | Type | Location | Summary |
|---|---|---|---|
| 3 | Secret | `path/file.ts:42` | One sentence: what would leak and why it matters publicly. |

**Type** values: `Secret`, `PII`, `Internal`, `Hygiene`, `Config`.

Severity scale:

| Sev | Meaning |
|---|---|
| 3 | Blocker — real secret/PII/credential; do not push until removed/rotated |
| 2 | Should fix — likely leak or strong smell (internal URL + auth, prod dump) |
| 1 | Worth noting — placeholder risk, example that looks too real, hygiene |
| 0 | Observation — low confidence; worth a human glance |

Rules:

- One row per finding. Be sure before flagging — false positives on secrets
  waste trust. Prefer severity 1 + "looks fake?" over inventing sev-3.
- If a real secret is present, say **rotate after purge** in the summary (history
  may already be dirty once committed).
- If nothing is wrong: one line, e.g. "Diff looks public-ready — N files reviewed,
  no findings."
- Closing line: overall verdict (`Safe to push publicly`, `Fix sev-3 before push`,
  etc.). No essay.
- **Do not fix, redact, commit, or push** — report only. The user decides next steps.
