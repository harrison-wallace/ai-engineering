---
name: check-repo-public-ready
description: Audit the whole repository for material that is unsafe on a public repo (secrets, PII, private keys, credentials, internal URLs, accidental dumps, bad .gitignore). Report-only severity table. Triggers on "/check-repo-public-ready", "is this repo public-ready", "safe to open-source", or "audit for public release".
---

# check-repo-public-ready

A focused, report-only audit of the **entire working tree** (tracked files, and
untracked files that would ship if someone `git add`s carelessly) asking: is this
repo safe to make **public** (or keep public)?

Not a general security review of application logic. For a change-only pass before
push, use `check-diff-public-ready`.

## 1. Establish scope

```bash
git rev-parse --show-toplevel
git status --short -u
# Prefer a tracked-file inventory; fall back if no ripgrep
git ls-files
```

Note the default branch and whether a remote already looks public (`git remote -v`).
If the user named paths or packages to focus on, prioritize those but still run
the high-signal whole-repo greps below.

Skip heavy scans of vendored third-party trees when obvious (`node_modules/`,
`vendor/`, `.git/`) unless the user asked for a full deep scan — still check that
those dirs are ignored and not tracked.

## 2. Inventory high-risk paths

Look for files that should almost never be public with real content:

| Pattern / path | Why |
|---|---|
| `.env`, `.env.*` (not `.env.example`) | Live secrets |
| `*credentials*`, `*secret*`, `*service-account*.json` | Cloud/API creds |
| `*.pem`, `*.p12`, `*.pfx`, `id_rsa*`, `*.key` (non-public) | Private keys |
| `*.sql.gz`, `*.dump`, `*.sqlite`, large `*.csv` exports | Data dumps |
| `.npmrc` / `.pypirc` with `_auth` / tokens | Registry tokens |
| CI secret files committed under `.github/`, `.gitlab-ci*`, etc. | Pipeline leaks |

```bash
git ls-files | rg -i '\.env$|\.env\.|credentials|service.account|\.pem$|\.p12$|\.pfx$|id_rsa|\.key$|\.dump$|\.sqlite'
# Untracked that might get added
git status -u --short | rg -i '\.env|credentials|\.pem|id_rsa|secret|\.key'
```

Read any hits. Empty or clearly placeholder files can be severity 0/1; real
values are severity 3.

## 3. Content greps (high-signal)

Run across tracked source (exclude lockfiles and huge generated assets if noisy):

```bash
rg -n --hidden --glob '!.git' -i \
  'api[_-]?key|secret[_-]?key|begin (rsa |openssh |ec )?private|akia[0-9a-z]{16}|ghp_[a-za-z0-9]{20,}|github_pat_|xox[baprs]-|-----begin' \
  || true
```

Also spot-check for:

- Hard-coded passwords / bearer tokens in config and examples
- Production connection strings with embedded credentials
- Personal emails that look like real individuals (not `noreply@` / project mail)
- Internal hostnames (`*.internal`, `*.corp`, `*.local` used as real endpoints
  with auth material)
- Private package feed URLs that embed tokens (`//user:token@…`)

Treat every hit as a lead: open the file, confirm it is real and would ship
publicly. Ignore docs that only describe patterns, and obvious fakes
(`your-api-key-here`, `xxxx`, `REDACTED`, test fixtures with clearly synthetic IDs).

## 4. Hygiene & policy checks

- **`.gitignore`**: are `.env`, key material, local overrides, and OS junk ignored?
  Missing ignores are findings even if no secret file is present yet (sev 1–2).
- **History note**: this skill audits the **current tree**, not full git history.
  If you find a live secret in the tree, warn that it may also exist in history
  and needs rotation + history purge (`git filter-repo` / BFG) before public.
  Do not rewrite history unless the user asks.
- **License**: is there a `LICENSE` (or clear license statement)? Missing license
  on an intended open-source repo is sev 1 (policy), not a secret — still report.
- **Large / binary dumps**: flag tracked archives or DB dumps that look accidental.
- **Docs & screenshots**: READMEs or assets that paste real tokens, invite URLs
  with secrets, or customer data.

## 5. Categories (same as the diff skill)

| Type | Covers |
|---|---|
| `Secret` | Keys, tokens, passwords, private keys, credential files |
| `PII` | Real personal/customer data, identity dumps |
| `Internal` | Non-public infra, VPN-only URLs + access material |
| `Hygiene` | Accidental dumps, bad ignores, license gap, history risk note |
| `Config` | Debug/auth defaults unsafe if the repo is public and runnable |

## 6. Report

Output a single table, highest severity first:

| Sev | Type | Location | Summary |
|---|---|---|---|
| 3 | Secret | `config/prod.env:3` | Live API key; remove, gitignore, rotate. |

Severity scale:

| Sev | Meaning |
|---|---|
| 3 | Blocker — real secret/PII/credential in the tree; not public-ready |
| 2 | Should fix — strong leak risk, missing ignore for secret class, prod dump |
| 1 | Worth noting — hygiene, missing LICENSE, weak examples, process gaps |
| 0 | Observation — low confidence or informational |

Rules:

- One row per finding. Prefer fewer, confident rows over a laundry list of
  false-positive `rg` hits.
- Group only if the same issue spans many files of one class (e.g. "12 `.env`
  copies under `deploys/`") — still list representative paths.
- If a real secret is present: state **rotate after purge** (public or soon-public
  history is hostile).
- Clean result: one line, e.g. "Repo looks public-ready — high-signal paths and
  greps clean; N tracked files considered."
- Closing line: overall verdict (`Public-ready`, `Not public-ready — N blockers`,
  etc.). Mention that git **history** was not fully audited unless you did a
  deeper history search.
- **Do not fix, redact, commit, push, or rewrite history** — report only. The
  user decides remediation.

## 7. Optional deeper history pass

Only if the user asks, or if you already found secrets in the tree:

```bash
git log --all --full-history -- .env '*credentials*' '*.pem' 2>/dev/null | head
git rev-list --all | head -5000 | while read c; do git grep -a -E 'AKIA[0-9A-Z]{16}|BEGIN RSA PRIVATE' $c 2>/dev/null; done | head
```

Keep this bounded; summarize hits rather than dumping history. Flag history
contamination as sev 3 with remediation pointer (rotate + history rewrite + force
push coordination), still without performing the rewrite.
