#!/usr/bin/env python3
"""Render a repo's phase board as one self-contained HTML page. No model, no network.

Usage: render-board.py <repo> [<out-dir>] [--live]

Reads   docs/plans/BOARD.md, docs/plans/NOW.md, the current phase doc, docs/plans/map.json,
        and the infra inventory (../../teach/scripts/infra-inventory.py).
Writes  <out-dir>/index.html and <out-dir>/stamp.txt (default out-dir: <repo>/docs/plans/board).
--live  adds a poll of stamp.txt, so an open page reloads when the board changes.

Markdown stays the source of truth for the board, NOW, slices, DoD, and open decisions.
map.json holds only the infra picture and its links to slices and decisions.
"""
import hashlib
import html
import json
import os
import re
import subprocess
import sys
from datetime import date

HERE = os.path.dirname(os.path.realpath(__file__))
DYNAMIC_JS = os.path.join(HERE, "..", "..", "serve-page", "assets", "dynamic.js")
INVENTORY = os.path.join(HERE, "..", "..", "teach", "scripts", "infra-inventory.py")


def esc(s):
    return html.escape(str(s), quote=True)


def inline(s):
    """Escape, then render **bold**, `code`, and [text](link) as text."""
    s = esc(s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    return s


def read(p):
    try:
        with open(p, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def sections(md):
    """Map each '## Heading' to its body text."""
    out, cur = {}, None
    for line in md.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            cur = m.group(1)
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def find_section(secs, *names):
    for k, v in secs.items():
        if any(k.lower().startswith(n.lower()) for n in names):
            return v
    return ""


# ---------- board and NOW ----------
PHASE_ID = r"[A-Za-z]+\d*[A-Za-z]?|\d+[a-z]?"  # P1, P13b, P2B, PF, 3


def parse_board(md):
    rows = []
    for line in md.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and re.fullmatch(PHASE_ID, cells[0]) and cells[2].lower() != "status":
            link = re.search(r"\]\(([^)]+)\)", cells[3]) or re.search(r"`([^`]+\.md)`", cells[3])
            rows.append({"id": cells[0], "name": cells[1], "status": cells[2].lower(),
                         "doc": link.group(1) if link else "", "note": cells[4] if len(cells) > 4 else ""})
    secs = sections(md)
    later = [l[2:] for l in find_section(secs, "Later").splitlines() if l.startswith("- ")]
    log = []
    for line in find_section(secs, "Log").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 2 and re.match(r"\d{4}-\d{2}-\d{2}", cells[0]):
            log.append((cells[0], cells[1]))
    return rows, later, log


def parse_now(md):
    now = {}
    for line in md.splitlines():
        m = re.match(r"^([A-Z][A-Za-z ]{1,20}):\s+(.+)$", line)
        if m:
            now[m.group(1).strip()] = m.group(2).strip()
    return now


# ---------- phase doc ----------
def parse_items(body):
    """Top-level checklist items, with their continuation lines joined, and nested checkboxes as `sub`."""
    items, cur, tail = [], None, None
    for line in body.splitlines():
        m = re.match(r"^- \[([ xX])\]\s+(.*)$", line)
        n = re.match(r"^\s{2,}[-*] \[([ xX])\]\s+(.*)$", line)
        if m:
            cur = tail = {"done": m.group(1) != " ", "text": m.group(2), "sub": []}
            items.append(cur)
        elif cur and n:
            tail = {"done": n.group(1) != " ", "text": n.group(2)}
            cur["sub"].append(tail)
        elif cur and line.startswith("  ") and line.strip():
            t = line.strip()
            tail["text"] += ("\n• " + t[2:]) if t[:2] in ("- ", "* ") else " " + t  # a nested bullet keeps its line
        elif line.strip() and not line.startswith(" "):
            cur = tail = None
    return items


def bullets(body):
    """Top-level '- ' list items with their wrapped lines joined. A checkbox shows as ☑ or ☐."""
    out = []
    for line in body.splitlines():
        if line.startswith("- "):
            out.append(line[2:].strip())
        elif out and line.startswith("  ") and line.strip():
            out[-1] += " " + line.strip()
        elif line.strip():
            out.append(None)  # a paragraph ends the list item
    out = [re.sub(r"^\[[xX]\]\s*", "☑ ", re.sub(r"^\[ \]\s*", "☐ ", x)) for x in out if x]
    return out


def slice_key(text, n):
    m = re.search(r"\bSlice\s+([0-9]+[a-z]?)\b", text)
    if m:
        return m.group(1)
    b = re.search(r"\*\*(.+?)\*\*", text)
    return (b.group(1).strip(" .:") if b else f"#{n}")[:24]


def slice_name(text):
    b = re.search(r"\*\*(.+?)\*\*", text)
    name = b.group(1) if b else " ".join(text.split()[:6])
    return re.sub(r"^Slice\s+[0-9]+[a-z]?:\s*", "", name).strip(" .:")


def parse_phase(md):
    secs = sections(md)
    title = (re.search(r"^#\s+(.+)$", md, re.M) or [None, ""])[1]
    status = (re.search(r"^\*\*Status:\*\*\s*(.+)$", md, re.M) or [None, ""])[1]
    goal = find_section(secs, "Goal").split("\n\n")[0].replace("\n", " ")
    slices = []
    body = find_section(secs, "Slices")
    if body:
        for n, it in enumerate(parse_items(body), 1):
            slices.append({"key": slice_key(it["text"], n), "name": slice_name(it["text"]),
                           "named": not re.search(r"\bSlice\s+[0-9]", it["text"]),
                           "done": it["done"], "text": it["text"], "items": it["sub"]})
    else:  # numbered shape: ### N.M headings with their own checklists
        for m in re.finditer(r"^###\s+(\d+\.\d+[a-z]?)\s+(.+?)\n(.*?)(?=^###\s|^##\s|\Z)", md, re.M | re.S):
            its = parse_items(m.group(3))
            slices.append({"key": m.group(1), "name": m.group(2).strip(), "text": "",
                           "done": bool(its) and all(i["done"] for i in its), "items": its})
    dod = bullets(find_section(secs, "Definition of Done"))
    nogo = re.search(r"No-gos:\s*(.+?)(?:\n- |\Z)", find_section(secs, "Appetite"), re.S)
    decisions = []
    for l in find_section(secs, "Open decisions").splitlines():
        m = re.match(r"^- (D\d+):\s*(.+)$", l)
        if m and "<question>" not in m.group(2):
            decisions.append({"id": m.group(1), "text": m.group(2), "recorded": True})
    adrs = sorted(set(re.findall(r"ADRs? (\d{4})", md)))
    return {"title": title, "status": status, "goal": goal, "slices": slices, "dod": dod,
            "nogo": " ".join(nogo.group(1).split()) if nogo else "", "decisions": decisions, "adrs": adrs}


# ---------- infra ----------
LANES = ["clients", "edge", "compute", "data", "external"]
BOX_W, BOX_H, PAD, LABEL = 150, 50, 9, 15
LEVEL = PAD + LABEL


def lane_index(parts):
    lanes = [l for l in LANES if any(p["lane"] == l for p in parts)]
    return lanes, {l: i for i, l in enumerate(lanes)}


def plan_routes(parts, edges, byid):
    """Pick the gaps (between lanes) and channels (between rows) each edge runs through."""
    lanes, li = lane_index(parts)
    last = len(lanes) - 1
    rows = sorted({p["row"] for p in parts})
    plans = []
    for e in edges:
        a, b = byid.get(e["from"]), byid.get(e["to"])
        if not a or not b:
            continue
        ia, ib = li[a["lane"]], li[b["lane"]]
        if ia == ib:
            lo, hi = sorted((a["row"], b["row"]))
            blocked = any(p["lane"] == a["lane"] and lo < p["row"] < hi for p in parts)
            if not blocked:
                plans.append((e, a, b, "vertical", None, None))
            else:
                g = ia if ia < last else ia - 1
                plans.append((e, a, b, "side", g, None))
        elif abs(ia - ib) == 1 or a["row"] == b["row"] and not any(
                p["row"] == a["row"] and min(ia, ib) < li[p["lane"]] < max(ia, ib) for p in parts):
            plans.append((e, a, b, "one-gap", min(ia, ib) if abs(ia - ib) == 1 else None, None))
        else:
            g1 = ia if ib > ia else ia - 1
            g2 = ib - 1 if ib > ia else ib
            ri = rows.index(b["row"])
            ch = ri if ri > 0 else 1  # the channel above b's row, or below the first row (route() falls back)
            plans.append((e, a, b, "channel", (g1, g2), ch))
    return plans


def layout(parts, plans):
    """Grid positions. Gaps grow with boundary levels and with the edges that run through them."""
    lanes, li = lane_index(parts)
    by_lane = {l: [p for p in parts if p["lane"] == l] for l in lanes}
    in_gap = {}
    for _, _, _, kind, g, _ in plans:
        for x in (g if isinstance(g, tuple) else (g,)):
            if x is not None:
                in_gap[x] = in_gap.get(x, 0) + 1

    def change(a, b):
        ca, cb = a.get("boundary", []), b.get("boundary", [])
        common = 0
        while common < min(len(ca), len(cb)) and ca[common] == cb[common]:
            common += 1
        return (len(ca) - common) + (len(cb) - common)

    xs, x = {}, 20 + LEVEL
    for i, l in enumerate(lanes):
        if i:
            need = max((change(a, b) for a in by_lane[lanes[i - 1]] for b in by_lane[l]), default=0)
            x += BOX_W + max(need * PAD + 2 * PAD + 10 * in_gap.get(i - 1, 0), 40)
        xs[l] = x
    side_gap = 10 * in_gap.get(len(lanes) - 1, 0)
    width = x + BOX_W + 20 + LEVEL + side_gap
    rows = sorted({p["row"] for p in parts})
    in_ch = {}
    for _, _, _, kind, _, ch in plans:
        if ch is not None:
            in_ch[ch] = in_ch.get(ch, 0) + 1
    ys, y = {}, 20 + 2 * LEVEL
    for i, r in enumerate(rows):
        if i:
            a_row = [p for p in parts if p["row"] == rows[i - 1]]
            b_row = [p for p in parts if p["row"] == r]
            need = max((change(a, b) for a in a_row for b in b_row), default=0)
            y += BOX_H + max(30, need * LEVEL + 16 + 8 * in_ch.get(i, 0))
        ys[r] = y
    for p in parts:
        p["x"], p["y"] = xs[p["lane"]], ys[p["row"]]
    gaps = {i: (xs[lanes[i]] + BOX_W, xs[lanes[i + 1]]) for i in range(len(lanes) - 1)}
    gaps[len(lanes) - 1] = (xs[lanes[-1]] + BOX_W, xs[lanes[-1]] + BOX_W + 2 * PAD + side_gap + 10)
    chans = {i: (ys[rows[i - 1]] + BOX_H, ys[rows[i]]) for i in range(1, len(rows))}
    return width, y + BOX_H + 20 + 2 * LEVEL, gaps, chans


def boundary_rects(parts, meta):
    paths = set()
    for p in parts:
        b = p.get("boundary", [])
        for i in range(1, len(b) + 1):
            paths.add(tuple(b[:i]))
    rects = {}
    for path in sorted(paths, key=lambda q: (-len(q), q)):
        boxes = [(p["x"], p["y"], p["x"] + BOX_W, p["y"] + BOX_H) for p in parts
                 if tuple(p.get("boundary", [])) == path]
        boxes += [rects[c] for c in rects if len(c) == len(path) + 1 and c[:len(path)] == path]
        x0 = min(b[0] for b in boxes) - PAD
        y0 = min(b[1] for b in boxes) - PAD - LABEL
        x1 = max(b[2] for b in boxes) + PAD
        y1 = max(b[3] for b in boxes) + PAD
        rects[path] = (x0, y0, x1, y1)
    return [(path, r, meta.get(path[-1], {}).get("label", path[-1])) for path, r in
            sorted(rects.items(), key=lambda kv: (len(kv[0]), kv[0]))]


SHAPE = {
    "data": lambda x, y: (f'<rect class="part" x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="6"/>'
                          f'<path class="drum" d="M{x},{y + 7} q{BOX_W / 2},10 {BOX_W},0"/>'),
    "external": lambda x, y: f'<rect class="part ext" x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="6"/>',
    "client": lambda x, y: f'<rect class="part" x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="25"/>',
    "edge": lambda x, y: (f'<rect class="part" x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="6"/>'
                          f'<path class="edgebar" d="M{x + 2},{y + 6} V{y + BOX_H - 6}"/>'),
    "schedule": lambda x, y: (f'<rect class="part" x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="6"/>'
                              f'<circle class="clock" cx="{x + BOX_W - 13}" cy="{y + 13}" r="6"/>'
                              f'<path class="clock" d="M{x + BOX_W - 13},{y + 9} v4 h3"/>'),
}


def fit(text, size, room, cls, x, y):
    """A text element, squeezed with textLength when its estimated width exceeds the room."""
    est = len(text) * size * (0.66 if cls == "lbl" else 0.52)
    squeeze = f' textLength="{room}" lengthAdjust="spacingAndGlyphs"' if est > room else ""
    return f'<text class="{cls}" x="{x}" y="{y}"{squeeze}>{esc(text)}</text>'


class Slots:
    """Spread parallel lines in one gap or channel 8px apart, around its centre."""
    def __init__(self):
        self.n = {}

    def take(self, key, lo, hi):
        k = self.n.get(key, 0)
        self.n[key] = k + 1
        step = (k + 1) // 2 * 8 * (1 if k % 2 else -1)
        return (lo + hi) / 2 + step


def route(plan, gaps, chans, slots):
    e, a, b, kind, g, ch = plan
    ay, by_ = a["y"] + BOX_H / 2, b["y"] + BOX_H / 2
    if kind == "vertical":
        x = a["x"] + BOX_W / 2 + slots.take(("v", a["lane"]), -4, 4)
        y0, y1 = (a["y"] + BOX_H, b["y"]) if a["y"] < b["y"] else (a["y"], b["y"] + BOX_H)
        return f"M{x},{y0} V{y1}", (x + 5, (y0 + y1) / 2 + 3, "start")
    if kind == "side":
        gx = slots.take(("g", g), *gaps[g])
        right = gx > a["x"]
        sx = a["x"] + BOX_W if right else a["x"]
        return f"M{sx},{ay} H{gx} V{by_} H{sx}", (gx + 4, (ay + by_) / 2, "start")
    l2r = a["x"] < b["x"]
    x0 = a["x"] + BOX_W if l2r else a["x"]
    x1 = b["x"] if l2r else b["x"] + BOX_W
    if kind == "one-gap":
        if abs(ay - by_) < 1:
            return f"M{x0},{ay} H{x1}", ((x0 + x1) / 2, ay - 5, "middle")
        gx = slots.take(("g", g), *gaps[g])
        return f"M{x0},{ay} H{gx} V{by_} H{x1}", (gx + 4, (ay + by_) / 2, "start")
    g1, g2 = g
    gx1 = slots.take(("g", g1), *gaps[g1])
    gx2 = slots.take(("g", g2), *gaps[g2])
    lo_hi = chans.get(ch) or (b["y"] + BOX_H + 4, b["y"] + BOX_H + 20)  # one row only: run just below it
    cy = slots.take(("c", ch), *lo_hi)
    return (f"M{x0},{ay} H{gx1} V{cy} H{gx2} V{by_} H{x1}", ((gx1 + gx2) / 2, cy - 4, "middle"))


def valid_map(m):
    """The parts and edges the layout can place, and the ids it had to drop."""
    parts, bad = [], []
    for p in m.get("parts", []):
        ok = isinstance(p, dict) and p.get("id") and p.get("lane") in LANES and isinstance(p.get("row"), int)
        if ok:
            parts.append(dict(p, label=str(p.get("label", p["id"]))))
        else:
            bad.append(str(p.get("id", "?")) if isinstance(p, dict) else "?")
    ids = {p["id"] for p in parts}
    edges = [e for e in m.get("edges", []) if isinstance(e, dict) and e.get("from") in ids and e.get("to") in ids]
    return parts, edges, bad


def infra_svg(m, decisions):
    parts, edges, bad = valid_map(m)
    warn = (f'<div class="card">Left off the map (needs an id, a lane from {", ".join(LANES)}, and a whole-number row): '
            f'{esc(", ".join(bad))}. Run <code>/phase map</code>.</div>' if bad else "")
    if not parts:
        return warn + '<p class="muted">No <code>docs/plans/map.json</code> yet. Run <code>/phase map</code>.</p>'
    byid = {p["id"]: p for p in parts}
    plans = plan_routes(parts, edges, byid)
    width, height, gaps, chans = layout(parts, plans)
    out = [warn + f'<svg viewBox="0 0 {width} {height}" width="100%" role="img" aria-label="Infra map">',
           '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
           'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>']
    for path, (x0, y0, x1, y1), label in boundary_rects(parts, m.get("boundaries", {})):
        out.append(f'<rect class="bnd" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="10"/>'
                   f'<text class="bnd-label" x="{x0 + 8}" y="{y0 + 12}">{esc(label)}</text>')
    slots, labels = Slots(), []
    for plan in plans:
        e = plan[0]
        d, (lx, ly, anchor) = route(plan, gaps, chans, slots)
        st = esc(e.get("state", "built"))
        marker = ' marker-end="url(#arr)"' if e.get("kind") != "data" else ""
        out.append(f'<g class="edge-g {st}" data-id="{esc(e["from"])} {esc(e["to"])}">'
                   f'<path class="edge {esc(e.get("kind", "request"))} {st}" d="{d}"{marker}/></g>')
        if e.get("label"):
            labels.append(f'<text class="elabel {st}" x="{lx}" y="{ly}" text-anchor="{anchor}">{esc(e["label"])}</text>')
    for p in parts:
        x, y = p["x"], p["y"]
        shape = SHAPE.get(p.get("kind"), lambda x, y: f'<rect class="part" x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="6"/>')(x, y)
        strike = (f'<path class="strike" d="M{x},{y + BOX_H} L{x + BOX_W},{y}"/>'
                  if p.get("state") == "removed" else "")
        flag = (f'<circle class="flag" cx="{x + BOX_W}" cy="{y}" r="6"><title>Now in the files: mark it built?</title></circle>'
                if p.get("_found") else "")
        room = BOX_W - (34 if p.get("kind") == "schedule" else 20)
        out.append(f'<g class="part-g {esc(p.get("state", "built"))}" data-id="{esc(p["id"])}">'
                   f'<title>{esc(p.get("caption", ""))}</title>{shape}{strike}'
                   + fit(p["label"].upper(), 11, room, "lbl", x + 10, y + 22)
                   + fit(p.get("sub", ""), 10, BOX_W - 20, "sub", x + 10, y + 38) + f"{flag}</g>")
    out.extend(labels)  # on top of the boxes and lines, with a halo
    per_part = {}
    for d in decisions:
        target = next((byid[i] for i in d.get("parts", []) if i in byid), None)
        if not target:
            continue
        k = per_part[target["id"]] = per_part.get(target["id"], -1) + 1  # side by side on one part
        cx, cy = target["x"] + BOX_W - 4 - 24 * k, target["y"] + BOX_H
        out.append(f'<g class="decision" data-links="{esc(" ".join(d.get("parts", [])))}">'
                   f'<path d="M{cx},{cy - 10} l10,10 l-10,10 l-10,-10 z"/>'
                   f'<text class="dlabel" x="{cx}" y="{cy + 4}">{esc(d["id"])}</text></g>')
    out.append("</svg>")
    return "\n".join(out)


def inventory_check(repo, m):
    """Flag planned parts whose `match` strings now appear in the inventory."""
    try:
        inv = subprocess.run([sys.executable, INVENTORY, repo], capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.TimeoutExpired):
        return "", []
    found = []
    for p in m.get("parts", []):
        if p.get("state") in ("planned",) and any(s in inv for s in p.get("match", [])):
            p["_found"] = True
            found.append(p["label"])
    stages = re.search(r"- stages: (.+)", inv)
    return stages.group(1) if stages else "", found


# ---------- page ----------
CSS = """
:root{--bg:#fbfaf7;--fg:#1d1d1f;--muted:#6b6b70;--line:#d9d6cf;--card:#fff;--accent:#2563eb;
--accent-soft:#e3ecfd;--amber:#d97706;--red:#dc2626;--ok:#15803d}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--fg:#ececef;--muted:#9a9aa2;--line:#34343a;
--card:#1c1c20;--accent:#7aa2ff;--accent-soft:#1e2a44;--amber:#f59e0b;--red:#f87171;--ok:#4ade80}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif}
header,main{max-width:1100px;margin:0 auto;padding:0 16px}header{padding-top:18px}
h1{font-size:20px;margin:0}h2{font-size:16px;margin:22px 0 8px}.muted{color:var(--muted)}
.warn{font-size:12px;color:var(--muted);margin:6px 0}
.legend{display:flex;flex-wrap:wrap;gap:12px;font-size:12px;margin:8px 0}.legend span{display:inline-flex;align-items:center;gap:5px}
.sw{width:18px;height:11px;border:1.5px solid var(--fg);border-radius:3px;display:inline-block}
.sw.building{border-color:var(--accent);background:var(--accent-soft)}.sw.planned{border-style:dashed;border-color:var(--muted)}
.sw.decision{border:0;background:var(--amber);transform:rotate(45deg);width:10px;height:10px}
.tabs{display:flex;gap:4px;overflow-x:auto;border-bottom:1px solid var(--line);margin-top:10px}
.tabs a{padding:8px 12px;color:var(--fg);text-decoration:none;white-space:nowrap;border-bottom:2px solid transparent}
.tabs a[aria-current="page"]{border-bottom-color:var(--accent);font-weight:600}
.js section.panel[hidden],.js .step[hidden]{display:none}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:10px 0}
.kv{display:grid;grid-template-columns:110px 1fr;gap:6px 12px}.kv b{color:var(--muted);font-weight:600}
.bar{height:8px;background:var(--line);border-radius:4px;overflow:hidden}.bar i{display:block;height:100%;background:var(--accent)}
.flow{display:flex;flex-wrap:wrap;gap:8px}.slice{flex:1 1 150px;max-width:220px;border:1.5px solid var(--fg);border-radius:8px;
padding:8px 10px;background:var(--card);cursor:pointer;font-size:13px}.slice .k{font-size:11px;font-weight:700;letter-spacing:.04em;text-transform:uppercase}
.slice.done{border-color:var(--line);color:var(--muted)}.slice.current{border-color:var(--accent);background:var(--accent-soft)}
.slice.open{border-style:dashed}.slice.waiting{border-color:var(--amber);border-style:dashed}
details{margin:6px 0}summary{cursor:pointer}
.here{font-size:11px;font-weight:700;color:var(--accent);text-transform:uppercase;letter-spacing:.04em}.here.side{color:var(--amber)}
.ghead{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:22px 0 6px}
.rail{border-left:2px solid var(--line);margin-left:7px}
.rrow{display:flex;gap:12px;padding:10px 12px 10px 0;color:var(--fg);text-decoration:none;position:relative}
a.rrow:hover .rbody{background:var(--accent-soft)}
.rrow .dot{flex:0 0 14px;height:14px;border-radius:50%;margin:4px 0 0 -8px;background:var(--bg);border:2px solid var(--muted)}
.rrow.k-here .dot{background:var(--accent);border-color:var(--accent)}.rrow.k-side .dot{background:var(--amber);border-color:var(--amber)}
.rrow.k-done .dot{background:var(--muted)}.rrow.k-done{padding:4px 12px 4px 0;color:var(--muted);font-size:14px}
.rbody{flex:1;border-radius:8px;padding:2px 8px}
.rrow.k-here .rbody{background:var(--accent-soft);border:1.5px solid var(--accent);padding:10px 12px}
.rrow.k-side .rbody{border:1.5px dashed var(--amber);padding:10px 12px}
.rtop{display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px}
.note{font-size:13px;color:var(--muted);margin-top:2px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.prog{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--muted);margin-top:6px}.prog .bar{width:140px}
.chip{font-size:11px;border-radius:10px;padding:1px 8px;border:1px solid var(--line);color:var(--muted);white-space:nowrap}
.chip.inprogress,.chip.current{background:var(--accent);border-color:var(--accent);color:#fff}
.chip.done{color:var(--ok);border-color:var(--ok)}.chip.waiting,.chip.parked{color:var(--amber);border-color:var(--amber)}
.small{font-size:13px}.later,.log{font-size:14px;padding-left:20px}.log li,.later li{margin:3px 0}
.pick{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}
.pchip{font:600 13px system-ui;padding:5px 12px;border-radius:16px;border:1.5px solid var(--line);background:var(--card);color:var(--fg);cursor:pointer}
.pchip.k-here{border-color:var(--accent)}.pchip.k-side{border-color:var(--amber)}.pchip.k-done{color:var(--muted)}
.pchip[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}
.phead .rtop{font-size:17px}.phead p{margin:6px 0}
.spot{background:var(--accent-soft);border:2px solid var(--accent);border-radius:10px;padding:14px 16px;margin:12px 0}
.spot .stop{font-size:17px}.spot .sdetail{font-size:15px}
.srow.done .sdetail{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.srow.done.open .sdetail{display:block}.srow.done .chk{display:none}.srow.done.open .chk{display:block}
.srow.done .stop::after{content:"tap to read";font-size:11px;color:var(--muted)}.srow.done.open .stop::after{content:""}
.pgrid{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:20px;align-items:start}
@media (max-width:760px){.pgrid{grid-template-columns:1fr}}
.pgrid aside h3{font-size:14px;margin:0 0 6px}.pgrid aside{margin-top:34px}.dod{padding-left:18px;margin:0;font-size:14px}
ol.slices{list-style:none;padding:0;margin:10px 0;border-left:2px solid var(--line);margin-left:9px}
.srow{display:flex;gap:12px;padding:8px 0;cursor:pointer}
.srow .mark{flex:0 0 18px;height:18px;border-radius:50%;margin:3px 0 0 -10px;background:var(--bg);border:2px solid var(--muted);
display:flex;align-items:center;justify-content:center;font-size:11px;color:#fff}
.srow.done .mark{background:var(--ok);border-color:var(--ok)}.srow.done .mark::after{content:"✓"}
.srow.current .mark{background:var(--accent);border-color:var(--accent);box-shadow:0 0 0 4px var(--accent-soft)}
.srow.waiting .mark{border-color:var(--amber)}
.sbody{flex:1;min-width:0;border-radius:8px;padding:4px 10px}
.srow.current .sbody{border:1.5px solid var(--accent);padding:8px 12px}
.srow.done .sbody{color:var(--muted)}.srow.done .sdetail{font-size:13px}
.stop{display:flex;flex-wrap:wrap;align-items:center;gap:6px 8px}
.skey{font:700 11px system-ui;color:var(--muted);min-width:22px}
.sdetail{margin:4px 0;font-size:14px}.srow.current .sdetail{font-size:15px}
ul.chk{list-style:none;padding:0;margin:6px 0;font-size:14px}ul.chk li{margin:2px 0}ul.chk li.ok{color:var(--muted)}
.dcard{border-left:4px solid var(--amber)}.dcard .id{font-weight:700;color:var(--amber)}
.map{font-size:12px;display:inline-block;margin-top:4px}
.tag{font-size:11px;border:1px solid var(--line);border-radius:10px;padding:1px 7px;color:var(--muted)}
.toggles{display:flex;flex-wrap:wrap;gap:12px;font-size:13px;margin:8px 0}
.pipe{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:12px}.pipe span{border:1px dashed var(--muted);border-radius:6px;padding:2px 8px}
svg{display:block;color:var(--fg)}
svg .bnd{fill:none;stroke:var(--line);stroke-width:1.2}
svg .bnd-label{font:600 10px system-ui;letter-spacing:.05em;text-transform:uppercase;fill:var(--muted)}
svg .part{fill:var(--card);stroke:var(--fg);stroke-width:1.5}svg .part.ext{fill:var(--bg);stroke-dasharray:3 3;stroke:var(--muted)}
svg .drum,svg .clock{fill:none;stroke:var(--fg);stroke-width:1}svg .edgebar{stroke:var(--fg);stroke-width:4}
svg .lbl{font:600 11px system-ui;letter-spacing:.04em;text-transform:uppercase;fill:var(--fg)}
svg .sub{font:10px system-ui;fill:var(--muted)}
svg .building .part{fill:var(--accent-soft);stroke:var(--accent)}svg .building .lbl{fill:var(--accent)}
svg .planned .part,svg .edge.planned{stroke-dasharray:5 4;stroke:var(--muted)}svg .planned .lbl{fill:var(--muted)}
svg .edge{fill:none;stroke:var(--fg);stroke-width:1.2}svg .edge.building{stroke:var(--accent)}
svg .edge.data{stroke-width:2}svg .edge.event{stroke-dasharray:1 3;stroke-width:1.6}
svg .elabel{font:600 9px system-ui;fill:var(--muted);paint-order:stroke;stroke:var(--bg);stroke-width:4px;stroke-linejoin:round}
svg .elabel.building{fill:var(--accent)}
svg .strike{stroke:var(--red);stroke-width:2}svg .flag{fill:var(--ok)}
svg .decision path{fill:var(--amber);cursor:pointer}svg .dlabel{font:700 8px system-ui;fill:#fff;text-anchor:middle}
svg [data-id]{cursor:pointer}
body.hide-built .part-g.built,body.hide-built .edge-g.built,body.hide-building .building,
body.hide-planned .planned,body.hide-decision .decision{display:none}
body.focus svg [data-id]:not(.hl){opacity:.22}body.focus .slice:not(.hl),body.focus .dcard:not(.hl){opacity:.45}
.hl{outline:2px solid var(--accent);outline-offset:2px}svg .hl{outline:none;filter:drop-shadow(0 0 4px var(--accent))}
code{font-size:.9em;background:var(--line);padding:0 4px;border-radius:4px}
"""

PICK_JS = """(function(){var d=document;function pick(id,keep){var v=[].slice.call(d.querySelectorAll('.pview'));
if(!v.some(function(e){return e.dataset.phase===id}))return false;
v.forEach(function(e){e.hidden=e.dataset.phase!==id});d.querySelectorAll('.pchip').forEach(function(c){
c.setAttribute('aria-pressed',c.dataset.phaseGo===id?'true':'false')});
if(keep){var u=new URL(location.href);u.searchParams.set('phase',id);history.replaceState(null,'',u)}return true}
d.addEventListener('click',function(e){var t=e.target.closest('[data-phase-go]');if(t)pick(t.dataset.phaseGo,true);
var r=e.target.closest('.srow.done');if(r&&!e.target.closest('a'))r.classList.toggle('open')});
var f=d.querySelector('.pview');if(f&&!pick(new URLSearchParams(location.search).get('phase')))
pick((d.querySelector('.pview.cur')||f).dataset.phase)})();"""

LIVE_JS = """(function(){var s=null;function poll(){fetch('stamp.txt',{cache:'no-store'}).then(function(r){return r.text()})
.then(function(t){t=t.trim();if(s===null)s=t;else if(t!==s)location.reload()}).catch(function(){})}
poll();setInterval(poll,4000)})();"""


def render(repo, out_dir, live=False):
    plans = os.path.join(repo, "docs", "plans")
    board_md = read(os.path.join(plans, "BOARD.md"))
    if not board_md:
        raise SystemExit(f"render-board: no docs/plans/BOARD.md in {repo}. Run /phase init.")
    rows, later, log = parse_board(board_md)
    now = parse_now(read(os.path.join(plans, "NOW.md")))
    try:
        m = json.loads(read(os.path.join(plans, "map.json")) or "{}")
    except json.JSONDecodeError as e:
        m = {"_error": str(e)}
    cur_id = (re.match(rf"\s*({PHASE_ID})\b", now.get("Phase", "")) or [None, ""])[1]
    current = next((r for r in rows if r["id"] == cur_id), None) or next(
        (r for r in rows if r["status"] == "in progress"), None)
    phase = parse_phase(read(os.path.join(plans, current["doc"]))) if current and current["doc"] else None
    now_slice = (re.match(r"\s*([0-9]+[a-z]?)", now.get("Slice", "")) or [None, ""])[1]
    # Side tracks: in-progress rows besides the current one, and the phases NOW's Parallel line names
    # first (a side track's row may stay shaped). Only the ids before the first dash, colon, or bracket.
    named = re.findall(rf"\b(?:{PHASE_ID})\b", re.split(r"\s[—–-]\s|[(:]", now.get("Parallel", ""))[0])
    side = [r for r in rows if r is not current and (r["status"] == "in progress" or r["id"] in named)]
    stages, found = inventory_check(repo, m)
    slice_links = m.get("slices", {})
    title = m.get("title") or os.path.basename(os.path.abspath(repo))
    adr_dir = os.path.join(repo, "docs", "adr")

    def adr_title(num):
        for f in sorted(os.listdir(adr_dir)) if os.path.isdir(adr_dir) else []:
            if f.startswith(num):
                t = re.search(r"^#\s+(.+)$", read(os.path.join(adr_dir, f)), re.M)
                return t.group(1) if t else f
        return f"ADR {num}"

    # Slices
    blocked = now.get("Blocked", "")
    waiting = set()
    for grp in re.findall(r"\b[Ss]lices?\s+((?:[0-9]+[a-z]?(?:,\s*|\s+and\s+|\s+to\s+)?)+)", blocked):
        waiting.update(re.findall(r"[0-9]+[a-z]?", grp))

    def slice_cards(sl, pid, blocked_keys=()):
        """The compact slice strip on the Now tab."""
        cards = []
        for s in sl:
            state = "done" if s["done"] else "current" if s["key"] == now_slice else (
                "waiting" if s["key"] in blocked_keys or re.search(r"\bwaits? on\b|\bblocked\b", s["text"], re.I) else "open")
            links = " ".join(slice_links.get(f"{pid}:{s['key']}", []))
            ticks = ""
            if s["items"]:
                ticks = f' · {sum(i["done"] for i in s["items"])}/{len(s["items"])}'
            attr = f' data-links="{esc(links)}"' if links else ""
            cards.append(f'<div class="slice {state}"{attr}><div class="k">'
                         f'{esc(s["key"])} · {state}{ticks}</div>{inline(s["name"])}</div>')
        return '<div class="flow">' + "".join(cards) + "</div>"

    pid = current["id"] if current else ""
    sl = phase["slices"] if phase else []
    done_n = sum(s["done"] for s in sl)

    # Decisions
    decisions = []
    if phase and phase["decisions"]:
        mdec = {d["id"]: d for d in m.get("decisions", [])}
        for d in phase["decisions"]:
            decisions.append({"id": d["id"], "question": d["text"], "options": [], "blocks": "",
                              "parts": mdec.get(d["id"], {}).get("parts", []), "source": "Open decisions", "recorded": True})
    else:
        decisions = [dict(d, recorded=False) for d in m.get("decisions", [])
                     if isinstance(d, dict) and d.get("id") and d.get("question")]

    # ---- tabs
    stale = ""
    updated = now.get("Updated", "")
    try:
        last = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%cs"], capture_output=True,
                              text=True, timeout=10).stdout.strip()
        if updated and last and last > updated:
            stale = f'<div class="card" style="border-color:var(--amber)">The board may be stale: a commit on {esc(last)} is newer than NOW ({esc(updated)}). Run <code>/phase sync</code>.</div>'
    except (OSError, subprocess.TimeoutExpired):
        pass

    now_tab = [stale, '<div class="card kv">']
    for k in ("Phase", "Slice", "Blocked", "Parallel", "Live"):
        if now.get(k):
            now_tab.append(f"<b>{k}</b><div>{inline(now[k])}</div>")
    now_tab.append("</div>")
    if phase:
        pct = int(100 * done_n / len(sl)) if sl else 0
        now_tab.append(f'<div class="card"><b>{inline(phase["title"])}</b><p>{inline(phase["goal"])}</p>'
                       f'<div class="muted">{done_n} of {len(sl)} slices done</div><div class="bar"><i style="width:{pct}%"></i></div></div>')
        now_tab.append(slice_cards(sl, pid, blocked_keys=waiting))
    now_tab.append(f'<p><a href="#decisions">{len(decisions)} open decision{"s" if len(decisions) != 1 else ""}</a>'
                   + ("" if all(d["recorded"] for d in decisions) else ' <span class="tag">found in the text</span>') + "</p>")
    if found:
        now_tab.append(f'<div class="card">Now in the files, still marked planned: {esc(", ".join(found))}. Run <code>/phase sync</code>.</div>')

    # Every phase doc on the board, parsed once: the Roadmap counts its slices, the Phase tab shows it.
    docs = {}
    for r in rows:
        if current and r["id"] == current["id"]:
            docs[r["id"]] = phase
        elif r["doc"]:
            docs[r["id"]] = parse_phase(read(os.path.join(plans, r["doc"]))) or None
    role = {r["id"]: ("here" if current and r["id"] == current["id"] else "side" if r in side else
                      "done" if r["status"] == "done" else "next" if r["status"] == "shaped" else "other")
            for r in rows}

    def progress(rid):
        ph = docs.get(rid)
        if not ph or not ph["slices"]:
            return ""
        n, t = sum(x["done"] for x in ph["slices"]), len(ph["slices"])
        return (f'<span class="prog"><span class="bar"><i style="width:{int(100 * n / t)}%"></i></span>'
                f'{n} of {t} slices</span>')

    def road_row(r):
        k = role[r["id"]]
        flag = {"here": '<span class="here">You are here</span>', "side": '<span class="here side">Side track</span>'}.get(k, "")
        go = f' href="#phase" data-phase-go="{esc(r["id"])}"' if docs.get(r["id"]) else ""
        tagname = "a" if go else "div"
        note = f'<div class="note">{inline(r["note"])}</div>' if r["note"] and k != "done" else ""
        return (f'<{tagname} class="rrow k-{k}"{go}><span class="dot"></span><div class="rbody">'
                f'<div class="rtop"><span><b>{esc(r["id"])}</b> {inline(r["name"])}</span> {flag}'
                f'<span class="chip {status_cls(r["status"])}">{esc(r["status"])}</span></div>'
                f'{note}{progress(r["id"]) if k != "done" else ""}</div></{tagname}>')

    status_cls = lambda s: re.sub(r"[^a-z]", "", s)
    groups = [("Now", [r for r in rows if role[r["id"]] == "here"] + [r for r in rows if role[r["id"]] == "side"]),
              ("Up next", [r for r in rows if role[r["id"]] == "next"]),
              ("Other", [r for r in rows if role[r["id"]] == "other"]),
              ("Done", [r for r in rows if role[r["id"]] == "done"])]
    road = []
    for name, grp in groups:
        if grp:
            road.append(f'<h3 class="ghead">{name}</h3><div class="rail">' + "".join(road_row(r) for r in grp) + "</div>")
    if later:
        road.append('<h3 class="ghead">Later</h3><ul class="later">' + "".join(f"<li>{inline(l)}</li>" for l in later) + "</ul>")
    if log:
        road.append('<h3 class="ghead">Recent log</h3><ul class="log">' + "".join(
            f"<li><b>{esc(d)}</b> {inline(t)}</li>" for d, t in log[-10:][::-1]) + "</ul>")

    def slice_detail(text):
        """The slice's prose without its 'Slice N: **Name.**' lead."""
        return re.sub(r"^(Slice\s+\S+:\s*)?(\*\*.+?\*\*)?[\s.:]*", "", text, count=1)

    def phase_view(r, ph):
        k = role[r["id"]]
        sl_ = ph["slices"]
        first_open = next((x["key"] for x in sl_ if not x["done"]), None)
        cur_key = now_slice if k == "here" and now_slice else first_open if k in ("here", "side") else None
        blocked_keys = waiting if k == "here" else ()
        out = [f'<div class="pview k-{k}{" cur" if k == "here" else ""}" data-phase="{esc(r["id"])}">',
               f'<div class="card phead"><div class="rtop"><span><b>{esc(r["id"])}</b> {inline(r["name"])}</span>'
               f'<span class="chip {status_cls(r["status"])}">{esc(r["status"])}</span></div>']
        if ph["goal"]:
            out.append(f'<p>{inline(ph["goal"])}</p>')
        out.append(progress(r["id"]))
        def body(x, state, full=True):
            label = {"done": "Done", "current": "You are here", "waiting": "Waiting", "open": "To do"}[state]
            links = " ".join(slice_links.get(f'{r["id"]}:{x["key"]}', []))
            ticks = (f' · {sum(i["done"] for i in x["items"])} of {len(x["items"])}' if x["items"] else "")
            detail = slice_detail(x["text"])
            items = "".join(f'<li class="{"ok" if i["done"] else "todo"}">{"☑" if i["done"] else "☐"} {inline(i["text"]).replace(chr(10), "<br>")}</li>'
                            for i in x["items"])
            key = "" if x.get("named") else esc(x["key"])  # the key is the name: say it once
            top = (f'<div class="stop"><span class="skey">{key}</span><b>{inline(x["name"])}</b>'
                   f'<span class="chip {state}">{label}{ticks}</span></div>')
            if not full:
                return top + '<div class="muted small">In full at the top of this phase.</div>'
            return (top + (f'<p class="sdetail">{inline(detail).replace(chr(10), "<br>")}</p>' if detail else "")
                    + (f'<ul class="chk">{items}</ul>' if items else "")
                    + (f'<a class="map" href="#infra" data-links="{esc(links)}">Show on the map</a>' if links else ""))

        states = {x["key"]: ("done" if x["done"] else "current" if x["key"] == cur_key else
                             "waiting" if x["key"] in blocked_keys or re.search(r"\bwaits? on\b|\bblocked\b", x["text"], re.I)
                             else "open") for x in sl_}
        cs = next((x for x in sl_ if x["key"] == cur_key), None)
        out.append("</div>")
        if cs:  # the slice in focus, in full, before the list
            out.append(f'<div class="spot">{body(cs, "current")}</div>')
        out.append('<div class="pgrid"><div><h3 class="ghead">Every slice</h3><ol class="slices">')
        for x in sl_:
            out.append(f'<li class="srow {states[x["key"]]}"><span class="mark"></span>'
                       f'<div class="sbody">{body(x, states[x["key"]], full=x is not cs)}</div></li>')
        out.append('</ol></div><aside>')
        if ph["dod"]:
            out.append('<div class="card"><h3>Definition of Done</h3><ul class="dod">'
                       + "".join(f"<li>{inline(x)}</li>" for x in ph["dod"]) + "</ul></div>")
        if ph["nogo"]:
            out.append(f'<div class="card"><h3>No-gos</h3><p>{inline(ph["nogo"])}</p></div>')
        out.append("</aside></div></div>")
        return "".join(out)

    shown = [r for r in rows if docs.get(r["id"])]
    order = sorted(shown, key=lambda r: ["here", "side", "next", "other", "done"].index(role[r["id"]]))
    phase_tab = []
    if order:
        phase_tab.append('<div class="pick">' + "".join(
            f'<button class="pchip k-{role[r["id"]]}" data-phase-go="{esc(r["id"])}">{esc(r["id"])}'
            f'{" · now" if role[r["id"]] == "here" else " · side" if role[r["id"]] == "side" else ""}</button>'
            for r in order) + "</div>")
        phase_tab.extend(phase_view(r, docs[r["id"]]) for r in order)
    else:
        phase_tab.append('<p class="muted">No phase doc found from the board. Run <code>/phase shape</code>.</p>')

    infra = []
    if m.get("_error"):
        infra.append(f'<div class="card">map.json does not parse: {esc(m["_error"])}</div>')
    if stages:
        infra.append('<div class="pipe"><b>Deploy</b>' + "".join(f"<span>{esc(s)}</span>" for s in stages.split(" → ")) + "</div>")
    infra.append('<div class="toggles">' + "".join(
        f'<label><input type="checkbox" data-layer="{k}" checked> {k.title()}</label>'
        for k in ("built", "building", "planned", "decision")) + "</div>")
    infra.append(infra_svg(m, decisions))
    infra.append('<p class="muted">Tap a part for its caption. Tap a slice or a decision to light up what it touches.</p>')
    caps = [p for p in valid_map(m)[0] if p.get("caption")]
    if caps:
        infra.append("<details><summary>Every part</summary><ul>" + "".join(
            f'<li data-links="{esc(p["id"])}"><b>{esc(p["label"])}</b> <span class="tag">{esc(p.get("state", ""))}</span> {inline(p["caption"])}</li>'
            for p in caps) + "</ul></details>")

    dec = []
    if decisions and not all(d["recorded"] for d in decisions):
        dec.append('<p class="muted">No <code>## Open decisions</code> section in the phase doc yet. These were found in the text. <code>/phase sync</code> records them.</p>')
    for d in decisions:
        opts = "".join(f"<li>{inline(o)}</li>" for o in d.get("options", []))
        dlinks = f' data-links="{esc(" ".join(d["parts"]))}"' if d.get("parts") else ""
        dec.append(f'<div class="card dcard"{dlinks}><span class="id">{esc(d["id"])}</span> '
                   f'{inline(d["question"])}' + (f"<ul>{opts}</ul>" if opts else "")
                   + (f'<div><b>Blocks:</b> {inline(d["blocks"])}</div>' if d.get("blocks") else "")
                   + f'<div class="muted">{inline(d.get("source", ""))}</div>'
                   + ('<a class="map" href="#infra">Show on the map</a>' if d.get("parts") else "") + "</div>")
    if not decisions:
        dec.append('<p class="muted">No open decisions recorded in this phase doc.</p>')
    if phase and phase["adrs"]:
        dec.append("<h2>Settled in ADRs</h2><ul>" + "".join(f"<li>{inline(adr_title(n))}</li>" for n in phase["adrs"]) + "</ul>")

    tabs = [("now", "Now", now_tab), ("roadmap", "Roadmap", road), ("phase", "Phase", phase_tab),
            ("infra", "Infra", infra), ("decisions", "Decisions", dec)]
    dynamic = read(DYNAMIC_JS)
    page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · phase board</title>
<style>{CSS}</style></head><body>
<header><h1>{esc(title)} · phase board</h1>
<div class="muted">{esc(current["id"] + " · " + current["name"] if current else "No phase in progress")} · rendered {date.today().isoformat()}{" · live" if live else ""}</div>
<div class="warn">This page holds host names and the plan. Any device on your LAN can open it while the server runs.</div>
<div class="legend"><span><i class="sw"></i>Built</span><span><i class="sw building"></i>Building</span><span><i class="sw planned"></i>Planned</span><span><i class="sw decision"></i>Open decision</span></div>
<nav class="tabs">{"".join(f'<a href="#{i}">{n}</a>' for i, n, _ in tabs)}</nav></header>
<main>{"".join(f'<section class="panel" id="{i}"><h2>{n}</h2>{"".join(body)}</section>' for i, n, body in tabs)}</main>
<script>{dynamic}</script><script>{PICK_JS}</script>{f"<script>{LIVE_JS}</script>" if live else ""}
</body></html>"""
    os.makedirs(out_dir, exist_ok=True)
    stamp = hashlib.sha1(page.replace(f"rendered {date.today().isoformat()}", "").encode()).hexdigest()[:12]
    old = read(os.path.join(out_dir, "stamp.txt")).strip()
    if old != stamp:
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(page)
        with open(os.path.join(out_dir, "stamp.txt"), "w") as fh:
            fh.write(stamp + "\n")
    return os.path.join(out_dir, "index.html"), old != stamp


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    repo = os.path.abspath(args[0])
    out = os.path.abspath(args[1]) if len(args) > 1 else os.path.join(repo, "docs", "plans", "board")
    path, changed = render(repo, out, live="--live" in sys.argv)
    print(f"{'wrote' if changed else 'unchanged'} {path}")
