# Phase map

`/phase map` writes `docs/plans/map.json`: the infra picture of the repo, and its links to slices
and open decisions. `scripts/render-board.py` turns the board, NOW, the current phase doc, and the
map into one LAN page with the tabs Now, Roadmap, Phase, Infra, and Decisions. The render needs no
model. `scripts/board-server.py` serves the pages and renders them again when the files change.

The markdown stays the source of truth for the board, NOW, slices, DoD, and open decisions. The
map never repeats them. It holds only what the markdown cannot: parts, edges, and links.

## Contents

- [1. Write the map](#1-write-the-map)
- [2. The schema](#2-the-schema)
- [3. Keep it current](#3-keep-it-current)
- [4. Serve the boards](#4-serve-the-boards)

## 1. Write the map

1. If BOARD is missing, tell the user to run `/phase init`. Stop.
2. Run `../../teach/scripts/infra-inventory.py <repo>` (relative to this skill's folder, resolved
   with `readlink -f`). It lists the services, ports, networks, volumes, deploy stages, and proxy
   routes it can see.
3. Read NOW, BOARD, and the current phase doc, plus the other `in progress` or `Parallel` phase
   docs that NOW names. Read the ADRs that those docs name, titles only.
4. Draw the parts with the grammar in `../../serve-page/references/infra-diagrams.md`: lanes left
   to right (clients, edge, compute, data, external), nested boundaries, one state per part.
   A part that the inventory cannot see (a host process, a table, an outside API) is still a part
   when a doc names it. Put the doc path in its `caption` or `source`.
5. Link each slice of the current and parallel phases to the parts it touches, and each open
   decision to the parts it changes. Link only what a doc says.
6. When `map.json` exists, update it in place. Keep the ids, so the links stay valid.
7. Run `scripts/board-server.py render <repo>`. When no server runs (`board-server.py list`), offer
   the setup in §4 in one line.

Keep 20 parts or fewer. Group the rest (for example "Module databases"). Never put a secret, a
token, or a password in the map. Hostnames and internal IPs are fine, but the page says so.

## 2. The schema

```json
{
  "version": 1, "title": "MyApp", "updated": "YYYY-MM-DD",
  "boundaries": {"host": {"label": "LAN host"}, "app": {"label": "Container · app"}},
  "parts": [{"id": "api", "label": "API", "sub": ":3000", "kind": "compute", "lane": "compute",
             "row": 1, "boundary": ["host", "app"], "state": "built",
             "caption": "One line a reader needs.", "source": "compose.yml", "match": ["api"]}],
  "edges": [{"from": "web", "to": "api", "label": "HTTPS", "kind": "request", "state": "built"}],
  "slices": {"P3:2": ["api", "db"]},
  "decisions": [{"id": "D1", "question": "...", "options": ["..."], "blocks": "...",
                 "parts": ["api"], "source": "P3-auth.md, slice 2"}]
}
```

- `kind`: client, edge, compute, data, schedule, or external.
- `lane`: clients, edge, compute, data, or external. `row` is the order in the lane, from 0.
  Parts that talk to each other sit on the same row or the next one.
- `boundary`: the outer boundary first. Several parts share a boundary path.
- `state`: built, building, planned, removed, or decision. `building` means the current slice
  adds or changes it.
- Edge `kind`: request, data, or event. Edge labels are short and upper case.
- `slices` keys are `<phase id>:<slice key>`, as the phase doc numbers them (`P13:7`, `P13:6b`).
- `match` lists strings that find the part in the inventory. When a `planned` part's string
  shows up there, the Now tab says the part has landed and suggests `/phase sync`.
- `decisions` is a fallback. When the phase doc has `## Open decisions`, the page takes the
  decisions from there and only the `parts` from here.

## 3. Keep it current

`sync`, `advance slice`, `advance phase`, and `shape` end with these steps when `map.json`
exists:

1. Move the states that the change settled: a part or edge that the closed slice built goes from
   `building` to `built`. The new current slice's parts go to `building`. A shaped phase adds its
   parts as `planned`.
2. Add the links for new slices and new decisions. Remove the links of decisions that were
   settled.
3. Set `updated` to today.
4. Run `scripts/board-server.py render <repo>`, even when no server runs. A server that starts
   later serves the new page.

When `map.json` does not exist, skip all of this. Do not write a map that the user did not ask
for. Suggest `/phase map` once.

## 4. Serve the boards

All commands are in `scripts/board-server.py`. It needs only Python 3.

```bash
board-server.py add ~/git/my-app          # register a repo (once)
board-server.py serve                     # http://<lan-ip>:38090/my-app/
board-server.py list                      # the repos, and the running servers
```

`serve` takes the first free port from 38090 to 38099 (`--ports` to change), and names the other
board servers that it finds. It renders a board again when its docs, `map.json`, infra files, or
git HEAD change. Open pages reload within about 5 seconds.

**At boot, with systemd:**

```bash
board-server.py unit > ~/.config/systemd/user/phase-board.service
systemctl --user daemon-reload && systemctl --user enable --now phase-board
loginctl enable-linger "$USER"            # keep it running when you are logged out
```

**In a container.** The registry holds host paths, so mount the repos at the same path:

```bash
docker run -d --name phase-board --restart unless-stopped --network host \
  --user "$(id -u):$(id -g)" -e HOME=/tmp -e XDG_CONFIG_HOME=/cfg \
  -v "$HOME/.config/phase-board:/cfg/phase-board:ro" -v "$HOME/git:$HOME/git:ro" \
  -v "$(readlink -f <skills-dir>):/skills:ro" \
  python:3-alpine python /skills/phase/scripts/board-server.py serve --bind 0.0.0.0
```

`<skills-dir>` is the folder that holds `phase`, `teach`, and `serve-page`. The image has no git,
so the page skips its stale check.

The pages show hostnames and internal IPs. Serve them on a trusted LAN only. There is no login.
