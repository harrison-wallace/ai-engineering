---
name: serve-page
description: Serve a self-contained HTML page on your LAN, so it opens on a phone or another machine with no login, on the first free port from 38081 to 38089, and stop it when you are done. Other skills (check-architecture, design, improve, trace-impact, aws-cost, teach, review-deep, check-ui-tells, research, phase, prototype) read it in place to build and serve their pages, and its page rules keep every page free of CDN scripts. Run it directly to serve any HTML file. Triggers on "/serve-page <file>", "/serve-page stop", "serve this page on the LAN", or "open this on my phone".
argument-hint: "[<file.html> | stop]"
---

# serve-page

Build a page to one set of rules, serve only its own folder on the LAN, and always stop it.

Other skills read this file in place (`../serve-page/SKILL.md`, relative to their folder, resolved
with `readlink -f`) and follow §1 to §4. Run directly, it serves a file you name (§5).

## 1. Build

Follow [`references/page-rules.md`](references/page-rules.md), then add what the calling skill's
page shows. Write it to `<scratchpad>/<skill>/<slug>/index.html`.

## 2. Serve

`<script>` is `scripts/serve-page.sh` in this skill's folder, as an absolute path.

1. **Plan**: run `<script> plan <dir>`. It prints `ip=`, `port=`, `url=`, and `path=`, and starts
   nothing. It takes the first free port from 38081 to 38089.
   - Exit 2 (every port is in use) or 3 (no LAN address): give the user the `path=` only, and say
     why.
2. **Start**: run `<script> start <dir> <port> <ip>` with the Bash tool's `run_in_background:
   true`, so the server keeps running. Note the background task.
3. **Check**: run `<script> check <port>`. Exit 0 means the server listens. Otherwise read the
   background task's output, report the error, and give the path only.

## 3. Tell the user

- `<url>`, for any device on the LAN.
- The full `path=`, to open on this machine.
- One line: "Any device on your LAN can open the page while the server runs. It serves only that
  folder."
- For a sensitive page (`references/page-rules.md`), add what it holds: "This page holds your AWS
  account ID and spend figures."

## 4. Stop

Stop the server when the user says they are done, when the calling skill moves to a step that
does not need the page, or at the end of the session's task at the latest:

- Stop the background task you started, or run `<script> stop <port> <dir>`. The script stops the
  process only when it is an `http.server` for that folder.
- Never use `pkill`, and never kill a process by name.
- Say that the server is stopped. A page that stays up is something the user must know about.

## 5. Run directly

- **`/serve-page <file.html>`**: copy the file into a new folder,
  `<scratchpad>/serve-page/<slug>/index.html`, with any images it links by a relative path. Then
  serve that folder (§2 and §3). Never serve the file's own folder, because it may hold other
  files.
- **`/serve-page stop`**: stop every page server this session started (§4), and list what was
  stopped.

## Rules

- Serve only a page folder in the scratchpad. Never a repo, a home folder, or a folder with
  other files.
- One server per page. Reuse its port for a rebuilt page in the same folder. Do not start a second
  server.
- Never put a secret on a page.
- Always stop what you start. Kill only your own server.
