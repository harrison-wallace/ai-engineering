---
name: guide-setup
description: Write an interactive bash script that walks you through steps only a human can do (dashboards, API keys, CI and Jenkins credentials, SSM parameters, a one-off migration or cutover), then hand it over for you to run in your own terminal. It scopes the stages from the repo (.env files, compose, GitHub Actions secrets, Jenkinsfile credential IDs, SSM names) and confirms them first, never invents UI steps, and checks the script statically. The values you type go to .env, gh secret, gh variable, or SSM, and never into the chat. Offer it in one line when a task hits three or more manual steps, and build it only after a yes. Never runs the script, never commits. Triggers on "/guide-setup", "/guide-setup keep", "walk me through setting this up", or "write me a setup script for the keys".
argument-hint: "[keep] <what to set up>"
---

# guide-setup

Write a **guide**: a bash script that walks a human through a manual procedure, one stage at a
time. It opens each URL, says what to click and copy, captures each value, writes it where it
belongs, and gates every irreversible step. **You write it. The user runs it. Never run it, and
never commit.**

The library in [`template.sh`](template.sh) already gives the experience: one screen per stage
with progress, browser opening on Linux, macOS, and WSL, hidden input for secrets, `.env` writes
that are safe to repeat, `gh secret`, `gh variable`, `set_ssm`, `jenkins_credential`, and a closing
summary. Your job is to scope the procedure and write its stages.

Adapted from Matt Pocock's `wizard`.

Not for: steps the agent can do itself, or deciding what to build (`design`).

## When to offer it

When a task reaches three or more steps that only the user can do, offer it in one line instead of
listing the steps in the chat:

> This needs <n> manual steps (<short list>). Want a `/guide-setup` script for them instead of a
> list here?

Build it only after a yes. For one or two manual steps, just say them.

## 1. Scope

Read the repo first. Do not ask cold.

- **Setup**: `.env`, `.env.example`, `.env.*`, `.gitignore`, `README*`, `docker-compose*` and
  `compose*`, and the framework config.
- **GitHub Actions**: every `secrets.*` and `vars.*` reference in `.github/workflows/*`.
- **Jenkins**: every `credentials('<id>')` and `credentialsId: '<id>'` in each `Jenkinsfile`, with
  its kind (`string()` is Secret text, `usernamePassword()` is Username with password). Find the
  Jenkins URL in the repo's docs or compose. If it is not there, ask.
- **SSM**: every parameter name the code or Terraform reads (`aws_ssm_parameter`,
  `ssm get-parameter`).
- **A migration or cutover**: the current state, the target state, and the irreversible actions
  between them.

Show the stages as a table, then wait for the user to add, drop, or reorder:

| # | Stage | Value | From | Written to | Secret |
|---|---|---|---|---|---|
| 1 | Stripe: API keys | `STRIPE_SECRET_KEY` | Dashboard → Developers → API keys | `.env`, GitHub secret | yes |

"Written to" is one or more of `.env`, GitHub secret, GitHub variable, SSM, Jenkins credential, or
nowhere (a pure action). When a value goes to `.env` and git does not ignore `.env`
(`git check-ignore -q .env` fails), say so under the table. The script stops before it writes, so
the user must fix `.gitignore` first.

**Done when** every stage is named in order, and each value has a source, a destination, and a
secret flag.

## 2. Map each stage

For each stage, write the exact path a human follows: the URL, what to do there, where the value
shows, and which variable it fills. Where you do not know the current UI or the exact command,
read the provider's current docs, or ask. Never invent a step.

**Done when** every stage traces to steps a stranger could follow.

## 3. Write the script

Copy [`template.sh`](template.sh) to `<scratchpad>/guide-setup/<slug>.sh`. With `keep`, copy it to
`scripts/setup-<slug>.sh` in the repo instead. Replace the example stage with one `stage` for each
row, in dependency order. Do not edit anything above the `STAGES` marker.

| Helper | Use |
|---|---|
| `stage`, `say`, `step`, `note`, `warn` | Show one stage and its instructions |
| `open_url` | Open the page before you ask for a value from it |
| `ask`, `ask_secret` | Capture a value. Use `ask_secret` for anything secret |
| `write_env` | Every value that persists locally |
| `set_secret`, `set_var` | Only the values that GitHub Actions reads |
| `set_ssm` | A SecureString in SSM. It asks y/N with the account and region first |
| `jenkins_credential <id> "<kind>"` | One Jenkins credential, as a manual step with the exact ID. Set `JENKINS_URL` at the top of the stages |
| `pause`, `confirm` | Wait for the user. `confirm` before every irreversible action |

- Set `TOTAL_STAGES` to the number of stages.
- Keep each stage to one task that fits one screen. Each stage clears the screen.
- Write the on-screen text in short, plain sentences, one action in each.

## 4. Check it

- `bash -n <script>`, and `shellcheck <script>` when it is installed. Say when it is not.
- `chmod +x <script>`.
- Trace it statically. Every value from §1 is captured and lands where the table says. Every
  `set_secret` name matches a `secrets.*` reference. Every `jenkins_credential` ID matches a
  Jenkinsfile ID. Every `set_ssm` name matches the name the code reads.
- Never run it yourself. It opens browsers and waits for the user.

## 5. Hand over

Tell the user:

- **Run it in your own terminal**: `bash <path>`. Not through the `!` prefix, which gives no
  interactive input. The script stops with a message when it has no terminal.
- **Keep the values out of this chat.** The script writes them straight to their destinations. Do
  not paste them here.
- **Ctrl-C is safe.** A re-run offers the values already in `.env` as defaults.
- **At the end**, the summary lists what it wrote and what is still to do by hand.

Then, for a scratchpad script, offer to delete it when the user is done. For `keep`, say it is in
`scripts/` and uncommitted, and offer one README line that points to it.

## Rules

- Never run the script, never commit, and never ask the user to paste a secret into the chat.
- Never write to AWS, GitHub, or Jenkins yourself. The script does it, run by the user.
- Never edit the library above the `STAGES` marker. Change `template.sh` in this repo instead.
