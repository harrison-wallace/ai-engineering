<!--
AGENTS-TEMPLATE.md — copy to <repo>/AGENTS.md and fill in.

Section order is fixed; keep it consistent across repos:
  Core Rules → Permitted → Prohibited → Infrastructure Guidelines →
  Code Conventions → Versioning → Additional Notes → Local Test-Serving Port

Rules for authors:
- "Core Rules", "Additional Notes" bullets, and "Local Test-Serving Port" are
  standardized verbatim across all repos — do not edit them per-project.
- Replace every <placeholder>. Delete any subsection that doesn't apply
  (e.g. "Database" for a DB-less app — or retitle it "No Database" and say so).
- Keep it short: most repos are 60–130 lines. Project-specific sections
  (architecture, domain rules) go between Code Conventions and Additional Notes.
- Delete these comments from the copy.
-->

## Core Rules

think before coding
state your assumptions. ask when unsure. never guess.

→ simplicity first
write the minimum code that solves the problem.
no abstractions nobody asked for.

→ surgical changes
don't touch code unrelated to the request.
every changed line must trace back to what was asked.

→ goal-driven execution
turn vague instructions into verifiable success criteria
before writing a single line.

---

This file outlines guidelines for AI coding agents interacting with this project. The purpose is to ensure collaboration is focused, prevent unintended automated actions, and maintain control over manual processes like serving, hosting, and version control.

## Permitted Actions

- Focus exclusively on generating or updating code and documentation.
- Run build commands like `<npm run build>` to verify output (you may also serve it locally to test a change, then shut it down).
- Update `README.md` with latest changes to keep it accurate and current.
- View previous commits and branches if needed for troubleshooting or recovery (but do not make changes).
- Suggest improvements or optimizations when noticed and relevant to the current task.
- <extra tool access, e.g. "You have access to `gh` / `aws` CLI commands for infrastructure tasks when explicitly requested.">

## Prohibited Actions

- **Serving/hosting**: You MAY serve or host locally to test a change (e.g. `npm run dev`), but you MUST stop the process as soon as the test is finished — never leave a server running. The owner still handles all production/permanent hosting.
- **Modifying `.md` files**: Do not create or update any `.md` files unless explicitly asked (exception: proactive updates to `README.md` as noted above, and changelog/version bumps via the release flow below).
- **Version control**: Do not run `git commit`, `git add`, `git push`, or any related operations. The owner handles all commits manually.
- <project-specific prohibitions, e.g. "Do not modify the proxy Docker network or Caddy container config without explicit instruction.">

## Infrastructure Guidelines

### CI/CD

- <pipeline: e.g. "Jenkins multibranch pipeline (`jenkins/Jenkinsfile`) builds and deploys on `main` only" or "GitHub Actions, single workflow `.github/workflows/deploy.yml`, AWS auth via OIDC — no long-lived credentials.">
- <quality gates: e.g. "CI always runs `npm run lint` + `npm run typecheck` before build.">
- Do not suggest or add any other CI system unless explicitly instructed.

### Access & Networking

- <how the app is reached: e.g. "LAN: `https://<name>.lan` via Caddy reverse proxy (`/home/h/git/proxy-local/Caddyfile`), mkcert TLS certs" or "Cloudflare Zero Trust tunnel; no open inbound ports.">
- <container/network requirements: e.g. "Container `<name>` must be on `--network proxy` with port `<port>` mapped.">

### Database

- <engine, location, backup policy — or delete/retitle "No Database" if the app has none.>

### Port Reference

| Environment | Port |
|---|---|
| Dev (`npm run dev`) | <dev port> |
| Production container | <prod port> |

## Code Conventions

- <stack and strictness: e.g. "TypeScript strict; use the existing `typecheck` and `lint` scripts.">
- <theme/design system and where tokens live: e.g. "tokens in `app/globals.css`.">
- <where state/APIs/shared UI live.>
- Prefer small surgical changes; keep the existing style and structure consistent.

## Versioning

Version lives in `package.json` and is mirrored in `README.md`. Follow **Semantic Versioning** (`MAJOR.MINOR.PATCH`):

| Increment | When to use | Examples |
|---|---|---|
| `PATCH` (x.x.**1**) | Bug fixes, performance wins, UI tweaks, error handling, dead-code removal | Fix wrong calculation, add try/catch, correct date logic |
| `MINOR` (x.**1**.0) | New features, new pages, new API endpoints, significant UI additions | New dashboard section, new endpoint, new agent |
| `MAJOR` (**1**.0.0) | Breaking architectural changes, schema migrations requiring data migration | Swap DB engine, change auth model, complete rewrites |

**To perform a version bump:**

<!-- Keep whichever flow the repo uses; delete the other. -->

```bash
./scripts/bump-version.sh (patch|minor|major) "One-sentence summary of what changed"
```

Or, if there is no local script, use the global `/bump-version` skill.

**Always** update `CHANGELOG.md` in the same session as the version bump. Each entry must include what changed, what was fixed, and why it matters (brief). Use the headers `### Added`, `### Changed`, `### Fixed`, `### Removed` — omit empty sections. Creating/updating `CHANGELOG.md` and the version line in `README.md` is **explicitly permitted** as part of the release process; all other `.md` modification rules remain in force.

<!-- Project-specific sections (architecture, domain rules, sprint workflow, etc.)
     go here, before Additional Notes. -->

## Additional Notes

- If clarification is needed on any rule, ask the owner before proceeding.
- Keep output concise — avoid wasting tokens while maintaining clarity and information density.
- Always prioritise security best practices in code, documentation, and infrastructure suggestions.
- These guidelines may be updated; always refer to the latest version in the repo.

## Local Test-Serving Port (standardized across ~/git)

- **Reserved port: `38080`.** When serving the app locally to test a change (dev server, preview, etc.), bind it to **38080** — e.g. `next dev -p 38080`, `vite --port 38080`, `PORT=38080 npm start`. Never serve on the app's default/production port (3000, 5173, 8080, …) so you don't collide with a real running instance.
- **Always shut the test server down when finished** — never leave it running.
- **Only kill the process you started.** Track its PID and `kill` that exact PID. Never broad-kill by name/pattern (e.g. `pkill -f next`, `pkill -f node`) — that can take down a real app the owner is running.
- If `38080` is already in use, it's likely a leftover of yours: check `ss -ltnp | grep 38080`, confirm it's your process, and kill that PID before restarting.
