# Diagram spec

One drawing grammar for every infra and architecture picture: self-hosted Docker hosts, AWS,
Kubernetes, and app services (APIs, workers, queues, LLM calls, agents). You write a JSON spec.
`scripts/diagram.py` does the layout, the routing, and the SVG, so no coordinate is ever guessed.
`phase`'s `docs/plans/map.json` is a spec too, with its own `slices` and `decisions` keys.

## Contents

- [Source of truth](#source-of-truth)
- [The spec](#the-spec)
- [Boundaries](#boundaries)
- [Lanes and rows](#lanes-and-rows)
- [Parts](#parts)
- [Edges](#edges)
- [States](#states)
- [Flows](#flows)
- [Modes](#modes)
- [draw.io](#drawio)
- [Audience](#audience)
- [Fix what check reports](#fix-what-check-reports)

## Source of truth

- Draw a **built** part only when a file defines it today. For infra, run
  `scripts/infra-inventory.py <repo>`. It lists compose services, `docker run` flags from
  Jenkinsfiles, Caddy routes, Terraform resources and references, k8s objects, and workflows.
  For app parts, cite the file that starts the service, defines the route, or makes the call.
- Draw a **building** or **planned** part only when a phase doc, an ADR, a design doc, or the user
  names it. Put that source in `source`.
- A part you think exists but cannot find in a file is `unconfirmed`. Never draw a guess as built.
- Terraform edges in the inventory are **references** (A reads an attribute of B). They are not
  traffic. Turn them into traffic edges only where the resource types say so: API Gateway
  integration → Lambda, event source mapping → queue → Lambda, event rule → target.
- Leave out plumbing that adds no meaning at the diagram's zoom: route table associations, public
  access blocks, ownership controls, policy attachments. Name them in `assumptions` instead.
- A flow step happens in the code. Read the handler before you write the step. A step you cannot
  find in the code goes in `assumptions`, not in the flow.
- Never put a secret, a token, or a password in the spec. `check` refuses one. Hostnames,
  internal IPs, and ports are fine, and the page warns about them.

## The spec

```json
{
  "title": "Checkout", "scope": "How an order reaches the warehouse", "updated": "2026-11-21",
  "boundaries": {"aws": {"label": "AWS · eu-west-2"}, "vpc": {"label": "VPC · 10.0.0.0/16"}},
  "parts": [
    {"id": "web", "label": "Browser", "kind": "client", "lane": "clients", "row": 0},
    {"id": "api", "label": "Orders API", "sub": "FastAPI · :8000", "kind": "compute",
     "lane": "compute", "row": 0, "boundary": ["aws", "vpc"], "state": "built",
     "caption": "Takes orders and puts them on the queue.", "source": "services/orders/main.py"}
  ],
  "edges": [{"from": "web", "to": "api", "label": "HTTPS :443", "kind": "request"}],
  "flows": [{"id": "place-order", "title": "Place an order", "note": "The happy path.",
             "steps": [{"from": "web", "to": "api", "title": "Submit the cart",
                        "label": "POST /orders", "detail": "One sentence.",
                        "payload": "{\n    \"items\": [...]\n}"}]}],
  "deploy": ["build", "test", "push", "deploy"],
  "assumptions": ["The payment provider retries webhooks. Not checked."]
}
```

Required: each part's `id`, `lane`, and `row`, and each edge's `from` and `to`. Everything else
is optional. `sub` is the second line in the box: the image, runtime, port, or engine. `caption`
shows on hover and in the parts table. `deploy` draws the pipeline stages as a strip above the
diagram.

## Boundaries

Boundaries are nested rounded rectangles. A part's `boundary` lists them from the outside in, and
`boundaries` gives each one its label. Draw only the levels the system uses.

| Stack | Nesting, outside in | Notes |
|---|---|---|
| Self-hosted Docker | LAN → host → Docker network (`proxy`, app network) → container | Host processes (a Python sidecar, a systemd service, Jenkins on the host) sit inside the host box but outside every network box. A bind mount or named volume sits under its container, in the data lane. Other LAN machines (a NAS, Pi-hole, a router) are boxes inside the LAN, outside the host. |
| AWS | account → region → VPC → AZ → subnet (public, private) → resource | S3, DynamoDB, Lambda (outside a VPC), API Gateway, SQS, SNS, EventBridge, Route 53, CloudWatch, SSM, and ECR sit in the region box, outside the VPC. Route 53 and CloudFront sit at the edge, outside the region. |
| Kubernetes | cluster → namespace → workload (Deployment, StatefulSet, CronJob) | Service and Ingress sit at the namespace's edge, in front of their workloads. ConfigMaps and Secrets go in the `sub` line or the caption, not in boxes. |
| App services | system → service or process | Use a boundary for one deployable unit (a monorepo app, a worker pool). Leave it out when every part deploys on its own. |
| Mixed | Each stack's boundary side by side, with labelled edges between them | For example, a home host that pushes backups to S3. |

Label a boundary with its kind and name: `HOST · DEV-BOX`, `NETWORK · PROXY`, `VPC · 10.0.0.0/16`.
For AWS, add `"kind"` to the boundary, and the draw.io file uses the AWS group style for it:
`aws-cloud`, `account`, `region`, `vpc`, `az`, `public-subnet`, `private-subnet`,
`security-group`, or `on-prem`. The page ignores it.
Keep the parts of one boundary in one block of lanes and rows. `check` warns when two sibling
boundaries overlap.

## Lanes and rows

Lanes run left to right, in the order a request travels. Leave a lane out when it is empty.

| Lane | Holds |
|---|---|
| `clients` | Users, browsers, phones, CLIs, other systems that call in, the internet |
| `edge` | Caddy, Cloudflare Tunnel, a load balancer, API Gateway, Ingress, CloudFront, DNS, a BFF |
| `compute` | Containers, host processes, EC2, Lambda, pods, services, workers, agents, LLM calls |
| `data` | SQLite files, Postgres, Redis, volumes, S3, DynamoDB, vector stores, queues, topics |
| `external` | Third-party APIs: a broker, a market data API, Telegram, Stripe, an LLM API, an IdP |

`row` is the order inside a lane, from 0 at the top. Parts that talk to each other sit on the same
row or the next one, so their edge is one straight line. Put read-heavy parts above and
write-heavy parts below, and one-shot jobs (seed, cron, migration) on the last row. Keep each lane
to six parts. Group more into one part with a count ("12 Lambda functions") and list them in its
caption. Keep the diagram to 20 parts. Split a bigger system into two specs.

## Parts

| `kind` | Shape | `sub` line |
|---|---|---|
| `client` | Pill | Device or app |
| `edge` | Box with a thick left bar | The hostnames or routes it serves |
| `compute` | Plain box (the default) | Image, runtime, or model, and the port |
| `data` | Box with a drum line | Engine and where the data lives (`SQLITE · /app/data`) |
| `queue` | Box with a notched right side | Queue, topic, or event bus kind |
| `schedule` | Box with a clock | The schedule (`HOURLY`, `0 2 * * *`) |
| `external` | Dashed grey box | The service |

`icon` (optional) puts the AWS icon in the part's box in the draw.io file, by its draw.io name:
`lambda`, `api_gateway`, `s3`, `dynamodb`, `sqs`, `sns`, `eventbridge`, `step_functions`, `rds`,
`aurora`, `elasticache`, `ecs`, `fargate`, `eks`, `ec2`, `cloudfront`, `route_53`, `alb`,
`cognito`, `secrets_manager`, `cloudwatch`, `bedrock`, and the rest of `drawio.py`'s `ICONS`.
Common names (`opensearch`, `msk`, `kms`, `ssm`, `dynamodb_table`) map to the right icon. `check`
warns about a name it does not know. The page ignores it.

An LLM, an embedding model, or an agent is `compute`. Say which in `sub` (`LLM · claude-sonnet-5-5`).
IAM roles, security groups, env files, and secrets are not parts. Name them in the caption, and
never print a secret's value.

## Edges

| `kind` | Line | `label` |
|---|---|---|
| `request` (default) | Solid, arrow at the receiver | Protocol and port, or the route: `HTTPS :443`, `POST /ask` |
| `data` | Thick, no arrow, ends on the store | `READ/WRITE`, `WRITE` |
| `event` | Dotted, arrow | The event: `ON FILL`, `S3 PUT` |
| `deploy` | Dashed and thin | The stage that does it: `BUILD + RUN` |
| `scrape` | Sparse dots | `SCRAPE :9100` |

Point an edge from the caller to the callee. One edge per pair is enough: a flow step can run it
backwards for a reply. Labels are short. Write them as people say them: `HTTPS :443`,
`POST /ask`, `read/write`.

## States

Every part and edge has one `state`. The page gets a toggle for each state that is used.

| `state` | Use for | Looks like |
|---|---|---|
| `built` (default) | In the files today | Solid |
| `building` | The current slice or change adds or changes it | Accent colour, light fill |
| `planned` | A later slice, phase, or design adds it | Dashed, muted |
| `removed` | A change takes it away | Built, with a red strike |
| `unconfirmed` | Named somewhere, not found in the files | Dotted grey, with `?` |

## Flows

A flow is one scenario, in order: a login, a query, an ingest, a deploy. Each flow gets its own
tab: a stepper that lights up one hop per step and sends a packet along it, dims the parts the flow does not use, and shows
the step's title, route, detail, and payload under the diagram. Play steps through the flow on
its own. A reply step runs the packet backwards. Without flows the page has no motion, so a
spec meant to explain behaviour needs at least one.

- `id`: lower case and dashes. `title`: what the user would call it, with the route when there
  is one: `Ask (POST /ask)`.
- Each step is one handoff: `from` sends something to `to`. A reply is a step from the callee
  back to the caller. A step with `from` equal to `to` is internal work (`build`, `embed`).
- Every step needs an edge between its two parts, in either direction. `check` says when one is
  missing.
- `label` replaces the edge label on that step. `detail` is one to three sentences.
- `payload` is the shape of what moves, trimmed: 4-space indent, no headers, no boring fields,
  10 lines at most. Never a real token. Write `<token>`.
- Keep a flow to 12 steps, and a spec to 6 flows. More flows means a second diagram.
- A different deployment shape (dev and prod, v1 and v2) is a mode, not a flow. See [Modes](#modes).

## Modes

Use modes when one system runs in two or more shapes that a reader compares: dev and prod, v1
and v2, before and after a migration. The page gets a switch in its header, and the draw.io file
gets one page per mode. Every part keeps its place in every mode.

```json
"modes": [{"id": "dev", "title": "Dev (laptop)"}, {"id": "prod", "title": "Prod"}],
"parts": [
  {"id": "caddy", "only": ["prod"], ...},
  {"id": "api", "sub": "FastAPI · :8000", "per_mode": {"dev": {"sub": "uvicorn --reload · :8000"}}, ...}
],
"flows": [{"id": "ask", "only": ["prod"], ...}]
```

- `modes`: 2 to 4, each with an `id` (lower case and dashes) and a `title`. The first is shown
  first.
- `only` on a part, an edge, or a flow: the modes it is in. Leave it out for every mode. An edge
  shows only where both of its ends are.
- `per_mode` on a part changes its `label`, `sub`, `caption`, or `source` in that mode. On an
  edge, it changes the `label`.
- A flow runs in every mode unless it has `only`, and each of its steps needs parts that are in
  all of the flow's modes. `check` says when a step uses a part that a mode leaves out.
- When the two shapes share less than half their parts, draw two specs instead.

## draw.io

`diagram.py drawio <spec> <out.drawio> --png <out.png>` writes an editable draw.io file with the
same layout as the page, and exports a PNG of each page when the `drawio` CLI can run.

- Each boundary is a container, so moving it moves its parts. Edges keep their routes as
  waypoints. A part's caption and source are its tooltip.
- A spec with modes gives one page per mode, and one PNG per mode (`<out>-<mode>.png`).
- Flows, the build-up, and the deploy strip are on the page only.
- A snap install of draw.io reads only its own folder, so the script copies the file through
  `~/snap/drawio/current/draw-infra/`. With no display, it uses `xvfb-run`, or it skips the PNG
  and says so.

## Audience

- **Engineers** (the default): service names, protocols, ports, routes, engines.
- **Everyone else**: action words in labels and steps ("Stores the order", "Sends the email"),
  no ports or engines, and a flow for each thing a user does.

## Fix what check reports

`diagram.py check` exits 1 on an error and prints warnings. Fix both before you serve.

| Report | Fix |
|---|---|
| Two parts share a lane and row | Give one of them the next free row |
| An edge runs through a part | Move the part in the way to another row, or put the two ends on the same row |
| Boundaries overlap | Put each boundary's parts in their own block of lanes and rows |
| A lane has more than six parts, or the spec more than 20 | Group parts into one with a count, or split the spec |
| A flow step has no edge | Add the edge, or fix the step's `from` or `to` |
| Looks like a secret | Delete the value. Name the secret by its name only |
| A flow step uses a part that a mode leaves out | Give the flow `only`, or drop the part's `only` |
| An icon is not verified | Use a name from `ICONS` in `drawio.py`, or drop `icon` |
