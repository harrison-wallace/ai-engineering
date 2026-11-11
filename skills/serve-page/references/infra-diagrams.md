# Infra diagrams

One drawing grammar for every page that shows infra: self-hosted Docker hosts, AWS, and
Kubernetes. Pages that follow it look the same across skills, and hand-written SVG stays legible.

## Contents

- [Source of truth](#source-of-truth)
- [Boundaries](#boundaries)
- [Lanes](#lanes)
- [Parts](#parts)
- [Edges](#edges)
- [State overlay](#state-overlay)
- [Geometry](#geometry)
- [SVG skeleton](#svg-skeleton)
- [Check before you serve](#check-before-you-serve)

## Source of truth

- Draw a **built** part only when the repo defines it today. For a repo, run
  `../../teach/scripts/infra-inventory.py <repo>` (relative to this file, resolved with
  `readlink -f`). It lists compose services, `docker run` flags from Jenkinsfiles, Caddy routes,
  Terraform resources and references, k8s objects, and workflows.
- Draw a **building** or **planned** part only when a phase doc, an ADR, or the user names it.
  Cite where it comes from in the caption.
- A part you think exists but cannot find in a file gets a grey box with `?` and the word
  "unconfirmed". Never draw a guess as built.
- Terraform edges in the inventory are **references** (A reads an attribute of B). They are not
  traffic. Turn them into traffic edges only where the resource types say so: API Gateway
  integration → Lambda, event source mapping → queue → Lambda, event rule → target.
- Leave out plumbing that adds no meaning at the page's zoom: route table associations, public
  access blocks, ownership controls, policy attachments. Name them in one caption line instead.

## Boundaries

Boundaries are nested rounded rectangles. Draw only the levels the repo uses.

| Stack | Nesting, outside in | Notes |
|---|---|---|
| Self-hosted Docker | LAN → host → Docker network (`proxy`, app network) → container | Host processes (a Python sidecar, a systemd service, Jenkins on the host) sit inside the host box but outside every network box. A bind mount or named volume sits under its container, in the data lane. Other LAN machines (a NAS, Pi-hole, a router) are boxes inside the LAN, outside the host. |
| AWS | account → region → VPC → AZ → subnet (public, private) → resource | S3, DynamoDB, Lambda (outside a VPC), API Gateway, SQS, SNS, EventBridge, Route 53, CloudWatch, SSM, and ECR sit in the region box, outside the VPC. Route 53 and CloudFront sit at the edge, outside the region. |
| Kubernetes | cluster → namespace → workload (Deployment, StatefulSet, CronJob) | Service and Ingress sit at the namespace's edge, in front of their workloads. ConfigMaps and Secrets are badges on the workload, not boxes. |
| Mixed | Draw each stack's boundary side by side, and cross between them with labelled edges | For example, a home host that pushes backups to S3. |

Label a boundary in its top-left corner: upper case, its kind and name (`HOST · DEV-BOX`,
`NETWORK · PROXY`, `VPC · 10.0.0.0/16`).

## Lanes

Inside the outermost boundary, place parts in fixed lanes from left to right, in the order a
request travels:

| Lane | Holds |
|---|---|
| **Clients** | Users, browsers, phones, other services that call in, the internet |
| **Edge** | Caddy, Cloudflare Tunnel (`cloudflared`), a load balancer, API Gateway, Ingress, CloudFront, DNS |
| **Compute** | Containers, host processes, EC2, Lambda, pods |
| **Data** | SQLite files, Postgres, Redis, volumes, S3, DynamoDB, queues |
| **External** | Third-party APIs (a broker, a market data API, Telegram, an LLM API) |

Two horizontal bands sit outside the lanes:

- **Deploy** (top): the CI pipeline (Jenkins, GitHub Actions) as a short flow of stages, with a
  dashed arrow down to what each deploy replaces.
- **Observe** (bottom): Prometheus, Grafana, exporters, cAdvisor, CloudWatch, alarms, SNS alerts.

Leave a lane out when it is empty. Keep each lane to six parts or fewer. Group more into one box
with a count ("12 Lambda functions") and list them in a caption or a table below.

## Parts

| Kind | Shape | Label |
|---|---|---|
| Edge (proxy, gateway, tunnel, DNS) | Box with a thick left border | `CADDY` + the hostnames it routes, smaller |
| Compute (container, process, function, pod) | Plain box | Name, then image or runtime, smaller |
| Data store (database, file, volume, bucket) | Box with a rounded bottom, like a drum | Name, then engine and where it lives (`SQLITE · /app/data`) |
| Queue, topic, event bus | Box with a notched right side | Name, then kind |
| Schedule (cron, EventBridge rule, CronJob) | Small circle with a clock mark | The schedule (`HOURLY`, `0 2 * * *`) |
| External service | Box with a dashed border and a grey fill | The service name |
| Client | Small rounded pill | `BROWSER`, `PHONE`, `INTERNET` |

- IAM roles, security groups, env files, ConfigMaps, and secrets are **badges**: a small tag on
  the corner of the part that uses them. Never draw them as boxes. Never print a secret's value.
- Ports go on the box edge where traffic enters (`:3012`). Host-published ports show both sides
  (`3012→3012`).

## Edges

| Edge | Line | Label |
|---|---|---|
| Request or call | Solid, arrow at the receiver | Protocol and port: `HTTPS :443`, `HTTP :8765` |
| Data read or write | Solid, no arrow head, ends on the store | `READ/WRITE` or `WRITE` |
| Event or message | Solid, open arrow head | The event (`ON FILL`, `S3 PUT`) |
| Deploy | Dashed, thin, from the deploy band | The stage that does it (`BUILD + RUN`) |
| Scrape or metrics | Dotted, from the scraper to the target | `SCRAPE :9100` |

Route edges in straight segments with right-angle bends. Do not cross a box. When two edges
would overlap, offset them by 6px. Label each edge once, near its middle.

## State overlay

One diagram can show the past, the present, and the plan. Give each part and each edge exactly
one state class, so the page's layer toggles work (`page-rules.md`, Dynamic pages).

| State | Class | Style |
|---|---|---|
| Built (exists in the repo today) | `built` | Solid stroke in the text colour |
| Building (the current slice changes or adds it) | `building` | Solid stroke and a light fill in the accent colour |
| Planned (a later slice or phase adds it) | `planned` | Dashed stroke, no fill, muted text |
| Going away (a slice removes it) | `built removed` | Built style with a red diagonal strike |
| Open decision | `decision` | An amber diamond with its number, pinned to the part it affects |

- A decision diamond carries `data-links` with the ids of every part the decision changes, so a
  click lights them up.
- Put the legend in the page header (`page-rules.md`): one swatch for each state the diagram uses.

## Geometry

- `viewBox="0 0 960 H"`, `width="100%"`, and the height from the content. Keep H at 540 or less.
  A taller picture becomes two diagrams or a stepper.
- Parts: 128 × 48. Gap between parts in a lane: 20. Gap between lanes: 56. Boundary padding: 16,
  plus 18 at the top for its label.
- Text: labels at 11px, upper case, letter spacing 0.04em. Second lines at 10px, normal case.
  No text under 10px.
- Lay parts out on the grid first (lane x, row y), then draw boundaries around them, then edges.
  Compute every coordinate from the grid. Do not eyeball positions.
- On a phone the SVG scales down with the page. When a diagram has more than four lanes, also give
  a stepper version that adds one lane per frame.

## SVG skeleton

Copy this shape. It defines the arrow heads and the classes the overlay needs. It reads the
theme variables `--bg`, `--fg`, `--muted`, `--accent`, `--accent-soft`, and `--amber`, so define
all six on `:root` and again for dark mode.

```html
<svg viewBox="0 0 960 420" width="100%" role="img" aria-label="Infra: built, building, planned">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
            orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker>
  </defs>
  <style>
    .bnd { fill: none; stroke: var(--muted); stroke-width: 1; rx: 10; }
    .bnd-label, .lbl { font: 600 11px system-ui; letter-spacing: .04em; text-transform: uppercase; }
    .sub { font: 10px system-ui; fill: var(--muted); }
    .part { fill: var(--bg); stroke: var(--fg); stroke-width: 1.5; rx: 6; }
    .building .part { fill: var(--accent-soft); stroke: var(--accent); }
    .planned .part, .edge.planned { stroke-dasharray: 5 4; }
    .planned text { fill: var(--muted); }
    .edge { fill: none; stroke: var(--fg); stroke-width: 1.25; }
    .decision path { fill: var(--amber); }
  </style>
  <rect class="bnd" x="8" y="8" width="944" height="404"/>
  <text class="bnd-label" x="20" y="24">HOST · HOME-SERVER</text>
  <g class="built" data-id="caddy">
    <rect class="part" x="200" y="80" width="128" height="48"/>
    <text class="lbl" x="212" y="100">CADDY</text><text class="sub" x="212" y="116">*.lan → :443</text>
  </g>
  <g class="building" data-id="ledger">...</g>
  <path class="edge built" d="M328,104 H384" marker-end="url(#arr)"/>
  <g class="decision" data-links="ledger caddy"><path d="M520,60 l10,10 l-10,10 l-10,-10 z"/>
    <text class="lbl" x="534" y="74">D1</text></g>
</svg>
```

## Check before you serve

- Every built part appears in the inventory output, or is marked "unconfirmed".
- Every building or planned part cites its phase doc or ADR in a caption.
- No box overlaps another, and no edge crosses a box.
- Each edge has a protocol or a verb. Each data store says where its data lives.
- The legend matches the states used. The decision numbers match the decision cards.
- Hostnames, internal IPs, and account IDs on the page → add the sensitive-page warning
  (`page-rules.md`).
