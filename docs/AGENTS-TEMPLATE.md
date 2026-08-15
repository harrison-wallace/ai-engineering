# AGENTS.md

<!--
AGENTS-TEMPLATE.md — AI agent instructions for a repository.

1. Copy this file to the repository root as AGENTS.md.
2. Fill every "REPO:" block below.
3. Delete these comments when you are done.

Sections 1, 2, 6, and 7 are standardized across repos. They work as they are.
Edit them here, not per-project. Sections 3, 4, and 5 need real values.
Machine-specific values — absolute paths, hostnames, usernames — belong in the
copy, not here. Keep them as <placeholders> in this template.
Project-specific sections (architecture, domain rules) go between 5 and 6.
-->

This file gives the rules for AI coding agents that work on this project. The
purpose is to keep collaboration focused, to prevent unwanted automated actions,
and to keep manual control of deployment and version control.

If a rule is not clear, ask the owner before you continue. These rules can
change. Always use the version in the repository.

---

## 1. Core Rules

- **Think before you code.** State your assumptions. Ask when you are not sure.
  Never guess.
- **Goal-driven execution.** Change a vague instruction into a success criterion
  that you can verify. Do this before you write code.
- **Simplicity first.** Write the minimum code that solves the problem. Do not
  add an abstraction that nobody asked for. Choose the simplest implementation
  that fully meets the current requirement.
- **Surgical changes.** Do not touch code that the request does not cover. Each
  changed line must trace back to the request.
- **Long-term architecture.** Make architectural decisions for the long term. Do
  not accept a temporary fix that only works now and that someone must replace
  later.
- **Prefer established libraries.** Use a well-maintained library instead of a
  custom implementation, if a suitable library exists.
- **Security first.** Apply security best practice in code, in documentation,
  and in infrastructure suggestions. Never write a credential, an account
  number, or customer data into the repository.
- **Session handshake.** Read `STATUS.md` or `docs/plans/STATUS.md` first, if
  the file exists. Rewrite it at the end of a tracking session. Do not append.
  Keep one Now item. Delete a Parking item that is older than two weeks and
  still vague. Do not put a locked decision or the roadmap in STATUS.

<!--
REPO: backward compatibility. Keep one of the two lines below. Delete the other.
- **Do not preserve backward compatibility** unless the owner asks for it. This
  is an internal tool. A clean design is more important than an old interface.
- **Preserve backward compatibility.** External clients depend on this
  interface. A breaking change needs owner approval and a MAJOR version bump.
-->

---

## 2. Language Style

Write all replies and all documentation in ASD-STE100 Simplified Technical
English. Use these rules:

- Use the active voice.
- Keep each sentence to 20 words or fewer.
- Give one idea in each sentence.
- Use simple tenses: present, past, and future.
- Use the same word for the same idea each time.
- Do not use idioms, slang, or unnecessary jargon.
- Keep each paragraph to 6 sentences or fewer.

Keep output short. Do not waste tokens. Keep clarity and information density.

---

## 3. Permitted Actions

<!--
REPO: replace this whole list with the real commands and paths for this
repository. Name the source directories, the exact test commands, the linters,
and the read-only CLI tools. The examples below are a starting point.
-->

- Generate or update code in `<SOURCE_DIRS>`.
- Run the tests to verify a change, for example `<TEST_COMMAND>`.
- Run a linter or a syntax check, for example `<LINT_COMMAND>`.
- Validate infrastructure templates in `<IAC_DIR>` with `<IAC_LINT_COMMAND>`.
- Update `README.md` and `<OTHER_DOCS>` when a code change makes them incorrect.
- Add or update a plan document in `<PLANS_DIR>`.
- Read previous commits, branches, and pull requests for troubleshooting. Do not
  change them.
- Suggest an improvement or an optimisation when you see one, if it is relevant
  to the current task.
- Use `<READ_ONLY_CLI_TOOLS>` for **read-only** tasks. Examples: describe a
  resource, read a log, read a pull request.
  - Ask the user to log in to the correct profile or account when you need to
    read a protected resource.

---

## 4. Prohibited Actions

<!--
REPO: these are cautious defaults. Replace the <PLACEHOLDER> values with the
real names for this repository. Keep a rule unless it gets in your way. If you
loosen one, do it on purpose and not because the agent asked you to.
-->

- **Version control.** Do not run `git add`, `git commit`, `git push`,
  `git rebase`, `git reset`, or any similar operation. The owner does all
  commits manually.
- **Deployment.** Do not run `<DEPLOY_SCRIPT>`, do not update an infrastructure
  stack, and do not publish a release artifact. The owner controls all
  deployments.
- **Production writes.** Do not run any write action against
  `<PRODUCTION_TARGET>`. The owner must give explicit permission first. Where a
  script or a skill keeps a write behind a confirmation flag, do not remove that
  flag.
- **Long-running processes.** You can start a local process to test a change.
  You must stop the process when the test is complete. Never leave a process
  running. Section 7 gives the rules for a local test server.
- **Markdown files.** Do not create or update a `.md` file unless the owner asks
  for it. The exceptions are a correction to `README.md` after a code change, a
  correction to a component `README.md` after a code change, and the release
  flow in section 5.
- **Secrets.** Do not read, print, or copy a value from a secret store, from a
  parameter store, or from any credential file.
- **Destructive actions.** Do not delete, terminate, or modify any deployed
  resource in any environment.

---

## 5. Version and Changelog Flow

<!--
REPO: name the files that hold the version and the release tool for this
repository. Delete this section only if the repository has no version at all.
-->

`<VERSION_FILES>` hold the version. `CHANGELOG.md` contains the full rules. Use
`<RELEASE_TOOL>` when the owner asks for a release. Do not bump a version on
your own.

| Increment | When to use | Example |
| --- | --- | --- |
| **PATCH** (x.y.+1) | Bug fix, security fix, performance improvement, documentation, or pipeline change. | `<PATCH_EXAMPLE>` |
| **MINOR** (x.+1.0) | New feature or non-breaking enhancement. | `<MINOR_EXAMPLE>` |
| **MAJOR** (+1.0.0) | Breaking change that affects an existing client. | `<MAJOR_EXAMPLE>` |

Each changelog entry starts with a keyword: `ADDED`, `CHANGED`, `FIXED`,
`SECURITY`, `PERFORMANCE`, `DOCUMENTATION`, or `PIPELINE`. Each entry names the
Jira ticket, for example `<TICKET_EXAMPLE>`.

<!-- Project-specific sections (architecture, domain rules, sprint workflow,
     etc.) go here, before section 6. -->

---

## 6. Definition of Done

Before you report a task as complete, confirm each point:

1. The change meets the success criterion that you stated at the start.
2. You did not change unrelated code.
3. The tests pass, or you report the failure with the output.
4. The documentation is correct, if the change made it incorrect.
5. You state what you did not do, and you give the reason.

---

## 7. Local Test-Serving Port (standardized across all repos)

- **Reserved port: `38080`.** When serving the app locally to test a change (dev server, preview, etc.), bind it to **38080** — e.g. `next dev -p 38080`, `vite --port 38080`, `PORT=38080 npm start`. Never serve on the app's default/production port (3000, 5173, 8080, …) so you don't collide with a real running instance.
- **Always shut the test server down when finished** — never leave it running.
- **Only kill the process you started.** Track its PID and `kill` that exact PID. Never broad-kill by name/pattern (e.g. `pkill -f next`, `pkill -f node`) — that can take down a real app the owner is running.
- If `38080` is already in use, it's likely a leftover of yours: check `ss -ltnp | grep 38080`, confirm it's your process, and kill that PID before restarting.
