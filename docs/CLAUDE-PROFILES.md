# Multiple Claude Code Profiles

Claude Code keeps all of its per-user state in one config directory — `~/.claude`
by default. Pointing the `CLAUDE_CONFIG_DIR` environment variable at a different
directory gives you a completely separate **profile**: its own settings, login,
skills, agents, commands, history, and memory. Useful for separating work contexts
(e.g. personal vs. client vs. experimental) or different accounts.

## What a profile contains

Each config directory holds, among other things:

```
<config-dir>/
  settings.json    permissions, env, hooks, model preferences
  skills/          personal Agent Skills
  agents/          personal subagents
  commands/        personal slash commands
  projects/        per-project history and memory
  .credentials     login/auth state
```

Nothing is inherited between profiles — a profile that isn't `~/.claude` does
**not** fall back to `~/.claude` for skills, settings, or anything else.

## Setting up a new profile

1. Pick a directory name, conventionally a suffixed sibling of the default:

   ```bash
   mkdir -p ~/.claude-<profile>
   ```

2. Add a shell alias so launching it is one word (in `~/.bashrc` / `~/.zshrc`):

   ```bash
   alias claude-<profile>='CLAUDE_CONFIG_DIR=$HOME/.claude-<profile> claude'
   ```

3. Run `claude-<profile>` and log in. First run creates the directory structure
   and stores auth for that profile only.

4. Configure it independently: `/config`, `/permissions`, and `settings.json`
   edits all apply to the active profile's directory.

Plain `claude` (no alias) keeps using `~/.claude`.

## Checking which profile a session is using

Inside a session, the environment tells you:

```bash
echo "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
```

## Sharing skills across profiles

Because profiles don't inherit from each other, anything you want everywhere must
be installed into **each** profile's directory. Keep the canonical copy in this
repo and symlink it into every profile directly — see
[Installing (symlinks)](../README.md#installing-symlinks) in the README, including
the warning about not chaining one profile's symlink through another's.

## Gotchas

- **Logins are separate** — each new profile needs its own `/login`.
- **Settings drift** — permissions or hooks added in one profile don't propagate;
  either repeat them or keep a shared fragment you copy into each `settings.json`.
- **Skills lists load at session start** — after symlinking a new skill into a
  profile, it appears the next time that profile starts a session.
- **Scripts and CI** — anything invoking `claude` non-interactively uses whatever
  `CLAUDE_CONFIG_DIR` is (or isn't) set in that environment; export it explicitly
  if a script must run under a specific profile.
