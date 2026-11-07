# Drift checks

Each check pairs a kind of claim in a doc with a way to prove it against the code. Run the proof.
A claim you could not prove either way goes under **Not changed**, with what you tried.

## Claims to extract

For each doc, list every claim of these kinds, one per line, as
`<doc>:<line>	<kind>	<claim>`:

- `path`: a file or folder path in code font, or a relative link target.
- `anchor`: a link to a heading, such as `#install` or `other.md#setup`.
- `command`: a command in a code block or in code font, such as `npm run build`, `make deploy`, or
  `scripts/install-skill.sh <name>`.
- `env`: an environment variable name, in code font or in `.env.example`.
- `flag`: a CLI flag such as `--dry-run`, with the command it belongs to.
- `count`: a number that describes the tree, such as a badge (`skills-25`) or "12 endpoints".
- `version`: a version string for this project.
- `infra`: a service name, port, hostname, volume, backup path, or Terraform output.

Report claims only. Do not judge them.

## Proofs

| Kind | Proof |
|---|---|
| `path` | `test -e` from the doc's folder, then from the repo root. Missing in both → stale. Search with `git ls-files \| rg <basename>` for where it moved |
| `anchor` | The target file has a heading whose GitHub slug matches. The slug is the heading in lower case, punctuation removed except `-` and spaces, and spaces changed to `-` |
| `command` | `npm run x` → `scripts.x` in `package.json`. `make y` → a `y:` target in the `Makefile`. `just z` → a recipe in the `justfile`. A script path → the file exists. `python -m m` → the module exists. A missing target → stale |
| `env` | Search the code for the name: `process.env.X`, `os.environ`, `getenv`, `${X}` in compose files, Terraform, and shell. Documented but never read → stale. Read but never documented → a gap |
| `flag` | Find the flag in the argument parser (`argparse`, `commander`, `yargs`, `clap`, `cobra`, `getopts`, or a `case` on `$1`). Run `<cli> --help` only for this repo's own CLI, and only when help is read-only, with a 10-second timeout. Missing → stale |
| `count` | Compute the real number with a command, such as `ls skills \| wc -l`, and name the command in the Proof column. A different number → stale |
| `version` | Compare with the manifest that owns the version (`package.json`, `Cargo.toml`, `pyproject.toml`, `VERSION`, or the latest tag), as `bump-version` §3 finds it |
| `infra` | Compose: `docker compose config` (read-only), or the compose file itself. Terraform: the variable and output blocks in `.tf` files. Hostnames and paths: search compose, Terraform, Caddy, nginx, Traefik, and cron files. Never query live systems for this skill |

## Common false positives

- A path in a "before" example, a migration note, or a changelog-style section that describes the
  past on purpose.
- A command for another tool or another repo, such as an upstream install step.
- An env var that a platform sets, such as `HOME`, `PATH`, `CI`, `NODE_ENV`, or `GITHUB_TOKEN`.
- A placeholder such as `<name>` or `YOUR_API_KEY`.
- Text in quotes, in an example of bad output, or in a rule that lists patterns to avoid.
