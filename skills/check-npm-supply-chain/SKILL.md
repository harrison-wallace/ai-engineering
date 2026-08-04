---
name: check-npm-supply-chain
description: Audit a repository for npm supply chain compromise indicators (Shai-Hulud-style worms) — malicious install hooks, credential-stealer payloads, exfil workflows, tampered lockfiles, and missing script-hardening. Report-only severity table. Triggers on "/check-npm-supply-chain", "check for npm supply chain attack", "am I hit by shai-hulud", or "audit dependencies for compromise".
---

# check-npm-supply-chain

A focused, report-only audit asking: **does this repo (and its installed
dependency tree) show indicators of an npm supply-chain compromise**, of the
kind used by the Shai-Hulud worm — a `preinstall`/`postinstall` hook that drops
a stealer, sweeps npm/GitHub/AWS/Kubernetes/Vault secrets, and self-propagates
by publishing to packages the victim maintains?

Not a general dependency-freshness or CVE review — `npm audit` covers that.
This skill hunts active-compromise indicators and hardening gaps.

## 1. Establish scope

```bash
git rev-parse --show-toplevel
ls package.json pnpm-lock.yaml package-lock.json yarn.lock bun.lockb 2>/dev/null
ls -d node_modules 2>/dev/null && du -sh node_modules
```

If there is no `package.json` anywhere (`git ls-files '*package.json'`), say so
and stop — nothing to audit. Monorepos: audit every workspace `package.json`
and the root lockfile. If `node_modules` exists, include it in the scans below
(the payload lives in installed packages, not your source).

## 2. Lifecycle-script audit (the entry point)

The attack fires from install hooks. Enumerate every one:

```bash
# Your own manifests
git ls-files '*package.json' | xargs -I{} sh -c \
  'jq -r "select(.scripts != null) | .scripts | to_entries[] | select(.key|test(\"^(pre|post)?(install|prepare|prepack)$\")) | \"{}: \(.key)=\(.value)\"" {} 2>/dev/null'

# Installed dependencies (the usual carrier)
find node_modules -name package.json -maxdepth 3 2>/dev/null | xargs -I{} sh -c \
  'jq -r "select(.scripts.preinstall or .scripts.postinstall or .scripts.install) | \"\(input_filename): pre=\(.scripts.preinstall // \"-\") post=\(.scripts.postinstall // \"-\") install=\(.scripts.install // \"-\")\"" {} 2>/dev/null'
```

Legitimate install scripts exist (native builds: `node-gyp`, `prebuild-install`,
`esbuild`, `sharp`, husky's `prepare`). Suspicious ones:

- `node bundle.js`, `node setup_bun.js`, `node bun_environment.js`, or any
  hook running a large opaque `.js` shipped in the package (known Shai-Hulud
  droppers)
- `curl`/`wget` piped to `sh`/`node`, base64 decode-and-eval, `powershell -enc`
- Hooks in packages that have no native code and no plausible reason to run
  anything at install time (pure-JS utility libs)

Open every suspicious hook target and read it. Severity 3 if it's a real
dropper; severity 2 if opaque/obfuscated and unexplainable.

## 3. Known IOC sweep

```bash
rg -n --hidden -g '!.git' -i -l \
  'shai-?hulud|webhook\.site|trufflehog|bun_environment' . node_modules 2>/dev/null | head -50

# Worm-dropped exfil workflows (it commits these to victims' repos)
ls .github/workflows/ 2>/dev/null
rg -n -i 'shai|hulud|secrets\.\w+\s*\|\s*(base64|curl)|toJSON\(secrets\)' .github/workflows/ 2>/dev/null
```

Also check for the worm's footprint outside the tree:

- Unexpected branches or recent commits you didn't make: `git log --all --oneline -20`,
  `git branch -a`
- New public repos / repos named `shai-hulud` (or migration-themed descriptions)
  on the user's GitHub account: `gh repo list --limit 30` if `gh` is available
- Unexpected GitHub Actions workflow files, self-hosted runner registrations,
  or modified `.github/` content in recent history: `git log --oneline -10 -- .github/`

Any confirmed IOC is severity 3 and means **assume all credentials on this
machine are stolen** — say so plainly in the report.

## 4. Stealer-pattern grep (payload behavior)

Look for code that sweeps the secret stores this class of worm targets:

```bash
rg -n -g '!.git' -g '!*.md' -e '\.npmrc' -e '_authToken' \
  -e '\.aws/credentials' -e 'AWS_SECRET_ACCESS_KEY' \
  -e '\.kube/config|KUBECONFIG' -e 'VAULT_TOKEN' \
  -e 'gh auth token|GITHUB_TOKEN|hosts\.yml' \
  node_modules 2>/dev/null | rg -v 'node_modules/[^/]+/(README|CHANGELOG|docs/)' | head -40
```

Plus generic dropper tells inside dependencies: `child_process` +
`https.request`/`fetch` in the same install-hook file, `os.homedir()` walks,
minified single-line files > 500 KB, `eval(Buffer.from(...,'base64'))`.

Every hit is a lead, not a finding — open the file, decide whether it's a
credential *manager* doing its job (e.g. an AWS SDK) or exfiltration. Report
only what you confirmed or genuinely can't explain.

## 5. Lockfile & registry hygiene

- **Lockfile present and committed?** No lockfile = floating versions = one
  `npm install` away from whatever was published last night (sev 2).
- **Recent lockfile churn**: `git log -5 --stat -- package-lock.json pnpm-lock.yaml yarn.lock`
  — flag unexplained mass version bumps.
- **`resolved` URLs** in the lockfile pointing anywhere other than the expected
  registry (sev 3 if a lookalike host).
- **Known-compromised packages**: the compromised list is large (hundreds of
  packages, e.g. the `keyv` wave) and changes per incident — grep the lockfile
  for names from the current advisory if the user has one, and otherwise run
  `npm audit` / point to the vendor IOC list rather than guessing from memory.

## 6. Hardening gaps (report even if clean)

| Check | Why |
|---|---|
| `ignore-scripts=true` in `.npmrc` (or `npm ci --ignore-scripts` in CI) | Neuters the entire install-hook entry point |
| Pinned exact versions / lockfile enforced in CI (`npm ci`, `--frozen-lockfile`) | Blocks silently pulling a freshly-poisoned patch release |
| Publish tokens: granular, short-lived, 2FA on npm + GitHub | Limits blast radius and worm propagation |
| A cooldown/minimum-age policy for new versions (e.g. pnpm `minimumReleaseAge`) | Compromised versions are usually pulled within hours |

Missing hardening is sev 1 each — worth a row, not an alarm.

## 7. Report

Single table, highest severity first:

| Sev | Type | Location | Summary |
|---|---|---|---|
| 3 | IOC | `node_modules/foo/setup_bun.js` | Shai-Hulud dropper; treat all local credentials as stolen. |

| Sev | Meaning |
|---|---|
| 3 | Active compromise indicator — confirmed IOC, dropper, or exfil workflow |
| 2 | Strong risk — unexplained install hook, obfuscated payload, no lockfile |
| 1 | Hardening gap — missing `ignore-scripts`, unpinned deps, token hygiene |
| 0 | Observation — legitimate-but-notable install scripts, low confidence |

Rules:

- **Report-only.** Do not delete `node_modules`, edit lockfiles, rotate
  tokens, or push anything — the user decides remediation.
- If sev 3 is found, the closing line must state the response order: stop
  installs, rotate npm/GitHub/AWS/K8s/Vault credentials from a clean machine,
  audit the user's own published packages and GitHub repos for worm
  propagation, then clean and reinstall.
- Clean result: one line, e.g. "No compromise indicators — N install hooks
  reviewed (all legitimate native builds), IOC greps clean; hardening gaps
  listed above."
- Prefer few confirmed rows over a dump of raw grep hits.
