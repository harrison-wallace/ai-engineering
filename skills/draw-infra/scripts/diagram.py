#!/usr/bin/env python3
"""Render an architecture or infra diagram spec (JSON) as SVG, a LAN page, or Markdown.
No model, no network. The spec format is in ../references/spec.md.

Usage:
  diagram.py check <spec.json>                 errors and layout warnings (exit 1 on an error)
  diagram.py page  <spec.json> <out-dir>       write <out-dir>/index.html: diagram, build-up,
                                               one tab per flow, and a parts table
  diagram.py md    <spec.json> [<out.md>]      the companion Markdown (stdout when no path)
  diagram.py svg   <spec.json> [--upto N] [--flow ID --step K] [--uid ID] [--mode ID]
                                               one SVG in a <div class="dia"> scroll box, to
                                               embed in another skill's page
  diagram.py drawio <spec.json> <out.drawio> [--png <out.png>]
                                               an editable draw.io file (one page per mode), and
                                               a PNG of each page when the draw.io CLI runs
  diagram.py css                               the CSS that an embedded SVG needs (page theme
                                               variables come from the page)

--upto N shows only the first N lanes, at their final positions, for a build-up series.
--flow and --step (from 1) draw one step of a flow. --uid gives the arrow marker a unique id,
so several SVGs can share one page. --mode draws one mode of a spec with modes (default: the
first).

Other scripts import it: render_svg(), check(), page(), markdown(), SVG_CSS.
"""
import html
import json
import os
import re
import shutil
import sys
from datetime import date

HERE = os.path.dirname(os.path.realpath(__file__))
BASE_CSS = os.path.join(HERE, "..", "..", "serve-page", "assets", "base.css")
DYNAMIC_JS = os.path.join(HERE, "..", "..", "serve-page", "assets", "dynamic.js")
THEME_CSS = os.path.join(HERE, "..", "..", "serve-page", "assets", "theme.css")
FONTS = os.path.join(HERE, "..", "..", "serve-page", "assets", "fonts")

LANES = ["clients", "edge", "compute", "data", "external"]
KINDS = {"client", "edge", "compute", "data", "queue", "schedule", "external"}
STATES = {"built", "building", "planned", "removed", "unconfirmed"}
EDGE_KINDS = {"request", "data", "event", "deploy", "scrape"}
BOX_W, BOX_H, PAD, LABEL = 150, 50, 9, 15
LEVEL = PAD + LABEL
MAX_IN_LANE, MAX_PARTS, MAX_FLOWS, MAX_STEPS, MAX_MODES = 6, 20, 6, 12, 4
PER_MODE = {"part": {"label", "sub", "caption", "source"}, "edge": {"label"}}
SECRET = re.compile(r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY|gh[pousr]_[A-Za-z0-9]{30,}|"
                    r"sk-[A-Za-z0-9_-]{20,}|xox[abpr]-[A-Za-z0-9-]+|"
                    r"(password|passwd|secret|token|api_?key)\s*[:=]\s*\S{6,}|://[^/\s:@]+:[^/\s@]+@", re.I)


def esc(s):
    return html.escape(str(s), quote=True)


def read(p):
    try:
        with open(p, encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


# ---------- layout ----------
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
    "queue": lambda x, y: (f'<path class="part" d="M{x + 6},{y} H{x + BOX_W} l-10,{BOX_H / 2} l10,{BOX_H / 2} '
                           f'H{x + 6} q-6,0 -6,-6 V{y + 6} q0,-6 6,-6 z"/>'),
}


def fit(text, size, room, cls, x, y):
    """A text element, squeezed with textLength when its estimated width exceeds the room."""
    est = len(text) * size * (0.56 if cls == "lbl" else 0.5)
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


def placed(m):
    """Lay out the whole spec once: parts with x and y, edges with their paths and label spots."""
    parts, edges, bad = valid_map(m)
    if not parts:
        return None
    byid = {p["id"]: p for p in parts}
    plans = plan_routes(parts, edges, byid)
    width, height, gaps, chans = layout(parts, plans)
    slots, routed = Slots(), []
    for plan in plans:
        d, spot = route(plan, gaps, chans, slots)
        routed.append((plan[0], d, spot))
    return {"parts": parts, "byid": byid, "routed": routed, "width": width, "height": height, "bad": bad}


# ---------- SVG ----------
def step_of(m, flow, step):
    """The flow and its 1-based step, or (None, None)."""
    if not flow:
        return None, None
    f = next((f for f in m.get("flows", []) if isinstance(f, dict) and f.get("id") == flow), None)
    if not f or not isinstance(step, int) or not 1 <= step <= len(f.get("steps", [])):
        return None, None
    return f, f["steps"][step - 1]


def modes_of(m):
    """[(id, title)] from the spec's modes list, or [] when it has none."""
    out = []
    for x in m.get("modes") or []:
        if isinstance(x, str):
            out.append((x, x.title()))
        elif isinstance(x, dict) and x.get("id"):
            out.append((str(x["id"]), str(x.get("title") or x["id"])))
    return out


def in_modes(obj, ids):
    """The modes a part or edge shows in: its `only` list, or every mode."""
    only = obj.get("only")
    return [i for i in ids if i in only] if isinstance(only, list) and only else list(ids)


def val(obj, key, mode):
    """obj[key], with the mode's per_mode override when there is one."""
    over = (obj.get("per_mode") or {}).get(mode) if isinstance(obj.get("per_mode"), dict) else None
    return over[key] if isinstance(over, dict) and key in over else obj.get(key)


def variants(obj, key, ins):
    """[(value, modes)] that group the modes with the same value, in mode order."""
    groups = {}
    for md in ins:
        groups.setdefault(str(val(obj, key, md) or ""), []).append(md)
    return list(groups.items())


def render_svg(m, decisions=(), *, upto=None, flow=None, step=None, uid="arr", label="Infra map", mode=None):
    """One SVG for the spec. Returns (svg, dropped ids). The default call draws the whole map.

    In a spec with modes, `mode` picks one (the first by default). mode="*" draws every mode in
    one SVG: an element missing from a mode, or a label that differs in it, carries the class
    not-<mode>, and the page hides it with body[data-mode].
    """
    lay = placed(m)
    if not lay:
        return "", valid_map(m)[2]
    parts, byid = lay["parts"], lay["byid"]
    ids = [i for i, _ in modes_of(m)]
    one = (mode if mode in ids else ids[0]) if ids and mode != "*" else None
    cls_ids = ids if ids and mode == "*" else []

    def ins_of(obj):
        if not ids:
            return [None]
        got = in_modes(obj, ids)
        return ([one] if one in got else []) if one else got

    def hide(ins):
        return "".join(f" not-{i}" for i in cls_ids if i not in ins)

    def texts(obj, key, ins, make):
        out = []
        for value, group in variants(obj, key, ins):
            h = hide(group)
            out.append(f'<g class="{h.strip()}">{make(value)}</g>' if h else make(value))
        return "".join(out)

    shown_lanes = lane_index(parts)[0][:upto] if upto else None
    pins = {p["id"]: ins_of(p) for p in parts}
    visible = [p for p in parts if (shown_lanes is None or p["lane"] in shown_lanes) and pins[p["id"]]]
    vis = {p["id"] for p in visible}
    f, st = step_of(m, flow, step)
    used, pairs, now_pair = set(), set(), None
    if f:
        for s in f.get("steps", []):
            used.update((s.get("from"), s.get("to")))
            pairs.add(frozenset((s.get("from"), s.get("to"))))
        now_pair = frozenset((st.get("from"), st.get("to")))
    out = [f'<svg viewBox="0 0 {lay["width"]} {lay["height"]}" width="100%" role="img" aria-label="{esc(label)}">',
           f'<defs><marker id="{esc(uid)}" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="9" markerHeight="9" '
           'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="currentColor"/></marker></defs>']
    for path, (x0, y0, x1, y1), blabel in boundary_rects(visible, m.get("boundaries", {})):
        bins = [i for i in (ids or [None]) if any(i in pins[p["id"]] for p in visible
                                                  if tuple(p.get("boundary", []))[:len(path)] == path)]
        h = hide(bins)
        out.append(f'<g class="bnd-g{h}"><rect class="bnd" x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" rx="10"/>'
                   f'<text class="bnd-label" x="{x0 + 8}" y="{y0 + 12}">{esc(blabel)}</text></g>')
    newest = shown_lanes[-1] if shown_lanes and len(shown_lanes) > 1 else None
    fresh = {p["id"] for p in visible if p["lane"] == newest}
    labels = []
    for n, (e, d, (lx, ly, anchor)) in enumerate(lay["routed"]):
        if e["from"] not in vis or e["to"] not in vis:
            continue
        eins = [i for i in ins_of(e) if i in pins[e["from"]] and i in pins[e["to"]]]
        if not eins:
            continue
        st_cls = esc(e.get("state", "built"))
        fcls, packet, pid = "", "", ""
        texts_by = variants(e, "label", eins)
        marker = f' marker-end="url(#{esc(uid)})"' if e.get("kind") != "data" else ""
        if f:
            pair = frozenset((e["from"], e["to"]))
            fcls = " flow-path" if pair in pairs else " flow-off"
            if pair == now_pair:
                if st.get("label"):
                    texts_by = [(str(st["label"]), eins)]
                back = st.get("from") == e["to"] and st.get("to") == e["from"]  # a reply runs the edge backwards
                fcls = " flow-now rev" if back else " flow-now"
                if back:
                    marker = f' marker-start="url(#{esc(uid)})"'
                elif e.get("kind") == "data":
                    marker = f' marker-end="url(#{esc(uid)})"'
                pid = f"{uid}-e{n}"
                keys = ' keyPoints="1;0" keyTimes="0;1" calcMode="linear"' if back else ""
                packet = (f'<circle class="packet" r="5"><animateMotion dur="1.6s" begin="indefinite" repeatCount="2" fill="freeze"{keys}>'
                          f'<mpath href="#{esc(pid)}"/></animateMotion></circle>')
        elif fresh and (e["from"] in fresh or e["to"] in fresh):
            fcls = " fresh"
        out.append(f'<g class="edge-g {st_cls}{fcls}{hide(eins)}" data-id="{esc(e["from"])} {esc(e["to"])}">'
                   f'<path class="edge {esc(e.get("kind", "request"))} {st_cls}" d="{d}"'
                   + (f' id="{esc(pid)}"' if pid else "") + f'{marker}/>{packet}</g>')
        for text, group in texts_by:
            if text:
                labels.append((f"elabel {st_cls}{fcls}{hide(group)}", lx, ly, anchor, text, set(group)))
    for p in visible:
        x, y = p["x"], p["y"]
        ins = pins[p["id"]]
        shape = SHAPE.get(p.get("kind"), lambda x, y: f'<rect class="part" x="{x}" y="{y}" width="{BOX_W}" height="{BOX_H}" rx="6"/>')(x, y)
        strike = (f'<path class="strike" d="M{x},{y + BOX_H} L{x + BOX_W},{y}"/>'
                  if p.get("state") == "removed" else "")
        flag = (f'<circle class="flag" cx="{x + BOX_W}" cy="{y}" r="6"><title>Now in the files: mark it built?</title></circle>'
                if p.get("_found") else "")
        fcls, badge = (" fresh" if p["id"] in fresh else ""), ""
        if f:
            fcls = (" flow-to" if p["id"] == st.get("to") else " flow-from" if p["id"] == st.get("from") else
                    " flow-in" if p["id"] in used else " flow-off")
            if st.get("from") == st.get("to") == p["id"]:
                fcls += " flow-self"  # internal work: the part pulses, no packet
            if p["id"] == st.get("to"):
                badge = (f'<g class="badge"><circle cx="{x}" cy="{y}" r="9"/>'
                         f'<text x="{x}" y="{y + 3.5}">{step}</text></g>')
        room = BOX_W - (34 if p.get("kind") == "schedule" else 20)
        q = " ?" if p.get("state") == "unconfirmed" else ""
        out.append(f'<g class="part-g {esc(p.get("state", "built"))}{fcls}{hide(ins)}" data-id="{esc(p["id"])}">'
                   f'<title>{esc(val(p, "caption", ins[0]) or "")}</title>{shape}{strike}'
                   + texts(p, "label", ins, lambda v: fit((v or p["id"]) + q, 12, room, "lbl", x + 10, y + 22))
                   + texts(p, "sub", ins, lambda v: fit(v, 11, BOX_W - 20, "sub", x + 10, y + 38))
                   + f"{flag}{badge}</g>")
    out.extend(place_labels(labels))  # on top of the boxes and lines, with a halo
    per_part = {}
    for dec in decisions:
        target = next((byid[i] for i in dec.get("parts", []) if i in byid and i in vis), None)
        if not target:
            continue
        k = per_part[target["id"]] = per_part.get(target["id"], -1) + 1  # side by side on one part
        cx, cy = target["x"] + BOX_W - 4 - 24 * k, target["y"] + BOX_H
        out.append(f'<g class="decision" data-links="{esc(" ".join(dec.get("parts", [])))}">'
                   f'<path d="M{cx},{cy - 10} l10,10 l-10,10 l-10,-10 z"/>'
                   f'<text class="dlabel" x="{cx}" y="{cy + 4}">{esc(dec["id"])}</text></g>')
    out.append("</svg>")
    return "\n".join(out), lay["bad"]


def place_labels(labels):
    """Edge labels as <text>, each moved down in 11px steps until it clears the ones before it."""
    return [f'<text class="{cls}" x="{x}" y="{y}" text-anchor="{anchor}">{esc(text)}</text>'
            for cls, x, y, anchor, text in label_spots(labels)]


def label_spots(labels):
    """(cls, x, y, anchor, text) for each label, after moving it clear of the ones before it."""
    taken, out = [], []
    for cls, x, y, anchor, text, ins in labels:  # ins: the modes it shows in; others never collide
        w = len(text) * 5.8 + 4
        x0 = x - w / 2 if anchor == "middle" else x - w if anchor == "end" else x
        for _ in range(6):
            box = (x0, y - 9, x0 + w, y + 2)
            if not any(box[0] < b[2] and b[0] < box[2] and box[1] < b[3] and b[1] < box[3] and ins & m
                       for b, m in taken):
                break
            y += 11
        taken.append(((x0, y - 9, x0 + w, y + 2), ins))
        out.append((cls, x, y, anchor, text))
    return out


SVG_CSS = """svg{display:block;color:var(--fg)}
svg .bnd{fill:none;stroke:var(--line);stroke-width:1.2}
svg .bnd-label{font:600 11px var(--sans,system-ui);fill:var(--muted)}
svg .part{fill:var(--card);stroke:var(--fg);stroke-width:1.5}svg .part.ext{fill:var(--bg);stroke-dasharray:3 3;stroke:var(--muted)}
svg .drum,svg .clock{fill:none;stroke:var(--fg);stroke-width:1}svg .edgebar{stroke:var(--fg);stroke-width:4}
svg .lbl{font:600 12px var(--sans,system-ui);fill:var(--fg)}
svg .sub{font:11px var(--sans,system-ui);fill:var(--muted)}
svg .building .part{fill:var(--accent-soft);stroke:var(--accent)}svg .building .lbl{fill:var(--accent)}
svg .planned .part,svg .edge.planned{stroke-dasharray:5 4;stroke:var(--muted)}svg .planned .lbl{fill:var(--muted)}
svg .unconfirmed .part{stroke-dasharray:2 3;stroke:var(--muted);fill:var(--bg)}svg .unconfirmed .lbl{fill:var(--muted)}
svg .edge{fill:none;stroke:var(--fg);stroke-width:1.2}svg .edge.building{stroke:var(--accent)}
svg .edge.data{stroke-width:2}svg .edge.event{stroke-dasharray:1 3;stroke-width:1.6}
svg .edge.deploy{stroke-dasharray:6 4;stroke-width:1;stroke:var(--muted)}svg .edge.scrape{stroke-dasharray:1 4;stroke:var(--muted)}
svg .elabel{font:600 10px var(--sans,system-ui);fill:var(--muted);paint-order:stroke;stroke:var(--bg);stroke-width:4px;stroke-linejoin:round}
svg .elabel.building{fill:var(--accent)}
svg .strike{stroke:var(--red);stroke-width:2}svg .flag{fill:var(--ok)}
svg .decision path{fill:var(--amber);cursor:pointer}svg .dlabel{font:700 8px var(--sans,system-ui);fill:var(--on-accent,#fff);text-anchor:middle}
svg [data-id]{cursor:pointer}
svg .flow-off{opacity:.22}svg .flow-path .edge{stroke-dasharray:4 3;opacity:.7}
svg .flow-now .edge{stroke:var(--accent);stroke-width:2.6;opacity:1;color:var(--accent)}svg .elabel.flow-now{fill:var(--accent);font-size:11px}
svg .flow-to .part{stroke:var(--accent);stroke-width:2.6;fill:var(--accent-soft)}svg .flow-from .part{stroke:var(--accent)}
svg .badge circle{fill:var(--accent)}svg .badge text{font:700 10px var(--sans,system-ui);fill:var(--on-accent,#fff);text-anchor:middle}
svg .packet{fill:var(--accent);stroke:var(--bg);stroke-width:2;display:none}.js svg .packet{display:inline}
svg .flow-now .edge,svg .edge-g.hl .edge{animation:dia-hop 1.8s linear both}
svg .flow-now.rev .edge{animation-name:dia-hop-back}
svg .hl{outline:none}svg .hl .part{stroke:var(--accent);stroke-width:2.5}svg .edge-g.hl .edge{stroke:var(--accent)}
svg .decision.hl path{stroke:var(--fg);stroke-width:1.5}
svg .fresh{animation:dia-in .7s ease-out both}
@keyframes dia-hop{0%{stroke-dasharray:7 5;stroke-dashoffset:0}99%{stroke-dasharray:7 5;stroke-dashoffset:-48}100%{stroke-dasharray:none}}
@keyframes dia-hop-back{0%{stroke-dasharray:7 5;stroke-dashoffset:0}99%{stroke-dasharray:7 5;stroke-dashoffset:48}100%{stroke-dasharray:none}}
@keyframes dia-in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){svg *{animation:none!important}svg .packet,.js svg .packet{display:none}}
"""


# ---------- check ----------
def segments(d):
    """Axis-aligned segments of a path made of M x,y, H x, and V y."""
    out, x, y = [], 0.0, 0.0
    for cmd, val in re.findall(r"([MHV])\s*([-\d.]+(?:,[-\d.]+)?)", d):
        if cmd == "M":
            x, y = (float(v) for v in val.split(","))
            continue
        nx, ny = (float(val), y) if cmd == "H" else (x, float(val))
        out.append((x, y, nx, ny))
        x, y = nx, ny
    return out


def crosses(seg, box):
    x0, y0, x1, y1 = seg
    bx0, by0, bx1, by1 = box
    lo_x, hi_x, lo_y, hi_y = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
    return lo_x < bx1 - 1 and hi_x > bx0 + 1 and lo_y < by1 - 1 and hi_y > by0 + 1


def strings(v):
    if isinstance(v, dict):
        for x in v.values():
            yield from strings(x)
    elif isinstance(v, list):
        for x in v:
            yield from strings(x)
    elif isinstance(v, str):
        yield v


def check_modes(m):
    """Errors in modes, only, and per_mode."""
    errs, ids = [], [i for i, _ in modes_of(m)]
    if "modes" in m:
        if not isinstance(m["modes"], list) or not 2 <= len(ids) <= MAX_MODES:
            errs.append(f"modes: give 2 to {MAX_MODES} modes, as {{\"id\": \"prod\", \"title\": \"Prod\"}}")
        for i in ids:
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", i):
                errs.append(f"mode {i!r}: id must be lower-case letters, digits, and dashes")
        if len(set(ids)) != len(ids):
            errs.append("a mode id is used twice")
    things = [("part", p, p.get("id")) for p in m.get("parts", []) if isinstance(p, dict)]
    things += [("edge", e, f"edge {e.get('from')} -> {e.get('to')}") for e in m.get("edges", []) if isinstance(e, dict)]
    things += [("flow", f, f"flow {f.get('id')}") for f in m.get("flows", []) if isinstance(f, dict)]
    for kind, obj, name in things:
        only, per = obj.get("only"), obj.get("per_mode")
        if (only is not None or per is not None) and not ids:
            errs.append(f"{name}: only and per_mode need a top-level modes list")
            continue
        if only is not None and (not isinstance(only, list) or not only or any(x not in ids for x in only)):
            errs.append(f"{name}: only must list mode ids from {', '.join(ids)}")
        if per is not None and kind == "flow":
            errs.append(f"{name}: a flow has no per_mode. Its steps use the parts' labels for each mode")
        elif per is not None:
            if not isinstance(per, dict):
                errs.append(f"{name}: per_mode must map a mode id to the fields that change")
                continue
            for md, over in per.items():
                if md not in ids:
                    errs.append(f"{name}: per_mode has an unknown mode {md!r}")
                elif not isinstance(over, dict) or set(over) - PER_MODE[kind]:
                    errs.append(f"{name}: per_mode.{md} can change only {', '.join(sorted(PER_MODE[kind]))}")
    return errs


def check(m):
    """Return (errors, warnings) for a spec."""
    errs, warns = [], []
    if not isinstance(m, dict):
        return ["the spec is not a JSON object"], []
    for s in strings(m):
        hit = SECRET.search(s)
        if hit:
            errs.append(f"looks like a secret, remove it: {s[:hit.start()][-30:]}<hidden>")
    raw = [p for p in m.get("parts", []) if isinstance(p, dict)]
    ids, cells = set(), {}
    for p in raw:
        pid = p.get("id")
        if not pid:
            errs.append(f"a part has no id: {json.dumps(p)[:60]}")
            continue
        if pid in ids:
            errs.append(f"part id used twice: {pid}")
        ids.add(pid)
        if p.get("lane") not in LANES:
            errs.append(f"{pid}: lane must be one of {', '.join(LANES)}")
        if not isinstance(p.get("row"), int) or p.get("row", -1) < 0:
            errs.append(f"{pid}: row must be a whole number from 0")
        if p.get("kind", "compute") not in KINDS:
            warns.append(f"{pid}: unknown kind {p.get('kind')!r}, drawn as compute")
        if p.get("state", "built") not in STATES:
            warns.append(f"{pid}: unknown state {p.get('state')!r}")
        if not isinstance(p.get("boundary", []), list):
            errs.append(f"{pid}: boundary must be a list, outer first")
        cell = (p.get("lane"), p.get("row"))
        if cell in cells:
            errs.append(f"{pid} and {cells[cell]} share lane {cell[0]}, row {cell[1]}: they would overlap")
        cells[cell] = pid
        for b in p.get("boundary", []) if isinstance(p.get("boundary"), list) else []:
            if b not in m.get("boundaries", {}):
                warns.append(f"{pid}: boundary {b!r} has no entry in boundaries, so its label is the id")
    for lane in LANES:
        n = sum(1 for p in raw if p.get("lane") == lane)
        if n > MAX_IN_LANE:
            warns.append(f"lane {lane} has {n} parts: group some into one part with a count")
    if len(raw) > MAX_PARTS:
        warns.append(f"{len(raw)} parts: split the diagram, or group parts, to stay at {MAX_PARTS} or fewer")
    pairs = set()
    for e in m.get("edges", []):
        if not isinstance(e, dict):
            continue
        a, b = e.get("from"), e.get("to")
        for end in (a, b):
            if end not in ids:
                errs.append(f"edge {a} -> {b}: no part {end!r}")
        if e.get("kind", "request") not in EDGE_KINDS:
            warns.append(f"edge {a} -> {b}: unknown kind {e.get('kind')!r}")
        if (a, b) in pairs:
            warns.append(f"edge {a} -> {b} is listed twice")
        pairs.add((a, b))
    errs += check_modes(m)
    sys.path.insert(0, HERE)
    from drawio import GROUPS, icon_problem
    for p in raw:
        if p.get("icon"):
            msg = icon_problem(p["icon"])
            if msg:
                warns.append(f"{p.get('id')}: {msg}")
    for bid, b in (m.get("boundaries") or {}).items():
        if isinstance(b, dict) and b.get("kind") and b["kind"] not in GROUPS:
            warns.append(f"boundary {bid}: unknown kind {b['kind']!r}, drawn as a plain box. "
                         f"Kinds: {', '.join(GROUPS)}")
    flows = [f for f in m.get("flows", []) if isinstance(f, dict)]
    if len(flows) > MAX_FLOWS:
        warns.append(f"{len(flows)} flows: split them over two diagrams, {MAX_FLOWS} at most each")
    fids = set()
    for f in flows:
        fid = f.get("id")
        if not fid or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(fid)):
            errs.append(f"flow {fid!r}: id must be lower-case letters, digits, and dashes")
        if fid in fids:
            errs.append(f"flow id used twice: {fid}")
        fids.add(fid)
        steps = f.get("steps", [])
        if not steps:
            errs.append(f"flow {fid}: no steps")
        if len(steps) > MAX_STEPS:
            warns.append(f"flow {fid}: {len(steps)} steps, split it at {MAX_STEPS}")
        for i, s in enumerate(steps, 1):
            a, b = s.get("from"), s.get("to")
            if a not in ids or b not in ids:
                errs.append(f"flow {fid} step {i}: from and to must be part ids ({a} -> {b})")
            elif a != b and (a, b) not in pairs and (b, a) not in pairs:
                errs.append(f"flow {fid} step {i}: add an edge between {a} and {b}")
            if not s.get("title"):
                errs.append(f"flow {fid} step {i}: no title")
            mids = [x for x, _ in modes_of(m)]
            for end in sorted({a, b} & ids):
                part = next(p for p in raw if p.get("id") == end)
                missing = [x for x in in_modes(f, mids) if x not in in_modes(part, mids)]
                if missing:
                    errs.append(f"flow {fid} step {i}: {end} is not in mode {', '.join(missing)}. "
                                f"Give the flow `\"only\": [...]` with the modes it runs in")
    if errs:
        return errs, warns
    lay = placed(m)
    if lay:
        boxes = {p["id"]: (p["x"], p["y"], p["x"] + BOX_W, p["y"] + BOX_H) for p in lay["parts"]}
        for e, d, _ in lay["routed"]:
            hit = [pid for pid, box in boxes.items() if pid not in (e["from"], e["to"])
                   and any(crosses(s, box) for s in segments(d))]
            if hit:
                warns.append(f"edge {e['from']} -> {e['to']} runs through {', '.join(hit)}: "
                             "move a part to another row, or a part between them out of the way")
        rects = boundary_rects(lay["parts"], m.get("boundaries", {}))
        for i, (pa, ra, _) in enumerate(rects):
            for pb, rb, _ in rects[i + 1:]:
                nested = pa == pb[:len(pa)] or pb == pa[:len(pb)]
                if not nested and ra[0] < rb[2] and rb[0] < ra[2] and ra[1] < rb[3] and rb[1] < ra[3]:
                    warns.append(f"boundaries {'/'.join(pa)} and {'/'.join(pb)} overlap: "
                                 "keep each boundary's parts in a block of lanes and rows")
    return errs, warns


# ---------- page ----------
PAGE_CSS = """.pipe{display:flex;flex-wrap:wrap;gap:.375rem .75rem;align-items:center;font-size:.875rem;margin:.5rem 0}
.pipe span{border-bottom:1px dashed var(--muted);padding:0 .125rem}
.dia{overflow-x:auto;max-width:100%}
.stepcard{border-top:1px solid var(--line);padding:.75rem 0}.stepcard h3{margin:0 0 .25rem}
.stepcard .route{font-size:.875rem;color:var(--muted)}
ol.steps{font-size:.9375rem}
body.hide-built .part-g.built,body.hide-built .edge-g.built,body.hide-building .building,
body.hide-planned .planned,body.hide-decision .decision,body.hide-unconfirmed .unconfirmed{display:none}
body.focus svg [data-id]:not(.hl){opacity:.22}body.focus tr[data-links]:not(.hl){opacity:.45}
"""


def copy_fonts(out_dir):
    """Put the theme fonts in <out_dir>/fonts, where theme.css looks for them."""
    dest = os.path.join(out_dir, "fonts")
    os.makedirs(dest, exist_ok=True)
    for name in os.listdir(FONTS) if os.path.isdir(FONTS) else []:
        if name.endswith(".woff2"):
            shutil.copyfile(os.path.join(FONTS, name), os.path.join(dest, name))


def cls_attr(c):
    return f' class="{c}"' if c else ""


def boxed(svg, width):
    """Wrap an SVG so a phone scrolls it inside its own box at 80% size, not squeezed to fit."""
    return (f'<div class="dia">' + svg.replace("<svg ", f'<svg style="min-width:{width * 0.8 / 16:.1f}rem" ', 1)
            + "</div>")


def stepper(frames):
    """frames: list of (inner html). One .step each, with the dynamic.js buttons and counter."""
    nav = ('<div class="nav"><button data-step="-1">Back</button><span class="count"></span>'
           '<button data-step="1">Next</button><button data-play>Play</button></div>')
    return '<div class="stepper">' + nav + "".join(f'<div class="step">{f}</div>' for f in frames) + "</div>"


def page(m, out_dir):
    """Write a self-contained LAN page. Returns its path."""
    title = m.get("title") or "Architecture"
    lay = placed(m)
    if not lay:
        raise SystemExit("diagram: the spec has no part with an id, a lane, and a row")
    parts = lay["parts"]
    lanes = lane_index(parts)[0]
    states = [s for s in ("built", "building", "planned", "removed", "unconfirmed")
              if any(p.get("state", "built") == s for p in parts)]
    tabs, tab_cls = [], {}
    modes = modes_of(m)
    ids = [i for i, _ in modes]
    full = boxed(render_svg(m, uid="arr-full", label=title, mode="*")[0], lay["width"])
    toggles = ('<div class="toggles">' + "".join(
        f'<label><input type="checkbox" data-layer="{s}" checked> {s.title()}</label>' for s in states)
        + "</div>") if len(states) > 1 else ""
    deploy = m.get("deploy") or []
    pipe = ('<div class="pipe"><b>Deploy</b>' + "".join(f"<span>{esc(s)}</span>" for s in deploy) + "</div>"
            if deploy else "")
    tabs.append(("diagram", "Diagram", pipe + toggles + full +
                 '<p class="muted">Tap a part to light up what it connects to. Hover for its caption.</p>'))
    if len(lanes) >= 3:
        frames = []
        for n in range(1, len(lanes) + 1):
            names = ", ".join(p["label"] for p in parts if p["lane"] == lanes[n - 1])
            svg = boxed(render_svg(m, upto=n, uid=f"arr-b{n}", label=f"{title}, first {n} lanes", mode="*")[0],
                        lay["width"])
            frames.append(f'<p><b>{n}. {esc(lanes[n - 1].title())}</b>: {esc(names)}</p>{svg}')
        tabs.append(("build", "Build-up", stepper(frames)))
    for f in m.get("flows", []):
        steps = f.get("steps", [])
        frames = []
        for k, s in enumerate(steps, 1):
            svg = boxed(render_svg(m, flow=f["id"], step=k, uid=f"arr-{f['id']}-{k}",
                                   label=f"{f.get('title', '')}, step {k}", mode="*")[0], lay["width"])
            a = lay["byid"].get(s.get("from"), {}).get("label", s.get("from"))
            b = lay["byid"].get(s.get("to"), {}).get("label", s.get("to"))
            route_txt = f"{a} → {b}" if s.get("from") != s.get("to") else f"inside {a}"
            frames.append(svg + f'<div class="card stepcard"><h3>{k}. {esc(s.get("title", ""))}</h3>'
                          f'<div class="route">{esc(route_txt)}{" · " + esc(s["label"]) if s.get("label") else ""}</div>'
                          + (f'<p>{esc(s["detail"])}</p>' if s.get("detail") else "")
                          + (f'<pre>{esc(s["payload"])}</pre>' if s.get("payload") else "") + "</div>")
        listing = '<ol class="steps">' + "".join(f'<li>{esc(s.get("title", ""))}</li>' for s in steps) + "</ol>"
        intro = f'<p>{esc(f["note"])}</p>' if f.get("note") else ""
        fmodes = in_modes(f, ids)
        if ids and len(fmodes) < len(ids):
            names = dict(modes)
            tab_cls[f"flow-{f['id']}"] = " ".join("not-" + i for i in ids if i not in fmodes)
            intro = f'<p class="muted">{esc(", ".join(names[i] for i in fmodes))} only.</p>' + intro
        tabs.append((f"flow-{f['id']}", f.get("title") or f["id"], intro + stepper(frames)
                     + "<details><summary>Every step</summary>" + listing + "</details>"))
    def cell(p, key, wrap=lambda v: esc(v)):
        """A table cell's text, one span per distinct value across the modes."""
        ins = in_modes(p, ids) if ids else [None]
        got = [(v, g) for v, g in variants(p, key, ins) if v]
        if len(got) < 2:
            return wrap(got[0][0]) if got else ""
        return "".join(f'<span class="{" ".join("not-" + i for i in ids if i not in g)}">{wrap(v)}</span>'
                       for v, g in got)

    def only_tag(p):
        if not ids or len(in_modes(p, ids)) == len(ids):
            return ""
        names = dict(modes)
        return ' <span class="tag">' + esc(", ".join(names[i] for i in in_modes(p, ids))) + " only</span>"

    rows = "".join(
        f'<tr data-links="{esc(p["id"])}" class="{" ".join("not-" + i for i in ids if i not in in_modes(p, ids))}">'
        f'<td><b>{cell(p, "label")}</b>{only_tag(p)}<br><span class="muted">{cell(p, "sub")}</span></td>'
        f'<td>{esc(p.get("kind", "compute"))}</td><td>{esc(p.get("state", "built"))}</td>'
        f'<td>{cell(p, "caption")}</td><td>{cell(p, "source", lambda v: "<code>" + esc(v) + "</code>")}</td></tr>'
        for p in parts)
    tabs.append(("parts", "Parts", '<div class="scroll"><table><tr><th>Part</th><th>Kind</th><th>State</th>'
                 f'<th>What it does</th><th>Source</th></tr>{rows}</table></div>'))
    legend = "".join(f'<span><i class="sw {s}"></i>{s.title()}</span>' for s in states)
    switch = ('<div class="modes" role="radiogroup" aria-label="Mode"><b>Mode</b>' + "".join(
        f'<label><input type="radio" name="mode" data-choose="mode" value="{esc(i)}"{" checked" if k == 0 else ""}>'
        f'{esc(t)}</label>' for k, (i, t) in enumerate(modes)) + "</div>") if modes else ""
    mode_css = "".join(f'body[data-mode="{i}"] .not-{i}{{display:none}}' for i in ids)
    scope = m.get("scope", "")
    out = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · diagram</title>
<style>{read(BASE_CSS)}{read(THEME_CSS)}{PAGE_CSS}{SVG_CSS}{mode_css}</style></head><body{f' data-mode="{esc(ids[0])}"' if ids else ""}>
<header><h1>{esc(title)}</h1>
<div class="muted">{esc(scope) + " · " if scope else ""}updated {esc(m.get("updated") or date.today().isoformat())}</div>
<div class="warn">This page can hold host names and ports. Any device on your LAN can open it while the server runs.</div>
{switch}<div class="legend">{legend}</div>
<nav class="tabs">{"".join(f'<a href="#{i}"{cls_attr(tab_cls.get(i))}>{esc(n)}</a>' for i, n, _ in tabs)}</nav></header>
<main>{"".join(f'<section class="panel" id="{i}"><h2>{esc(n)}</h2>{body}</section>' for i, n, body in tabs)}</main>
<script>{read(DYNAMIC_JS)}</script>
</body></html>"""
    os.makedirs(out_dir, exist_ok=True)
    copy_fonts(out_dir)
    path = os.path.join(out_dir, "index.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(out)
    return path


# ---------- markdown ----------
def markdown(m):
    title = m.get("title") or "Architecture"
    parts, edges, _ = valid_map(m)
    label = {p["id"]: p["label"] for p in parts}
    out = [f"# {title}", ""]
    if m.get("scope"):
        out += [m["scope"], ""]
    out += [f"Updated {m.get('updated') or date.today().isoformat()}. "
            "Drawn with `draw-infra` from the spec next to this file.", "", "## Parts", "",
            "| Part | Kind | State | What it does | Source |", "|---|---|---|---|---|"]
    for p in parts:
        name = p["label"] + (f" ({p['sub']})" if p.get("sub") else "")
        out.append(f"| {name} | {p.get('kind', 'compute')} | {p.get('state', 'built')} | "
                   f"{p.get('caption', '')} | {('`' + p['source'] + '`') if p.get('source') else ''} |")
    if edges:
        out += ["", "## Connections", "", "| From | To | Kind | Label |", "|---|---|---|---|"]
        for e in edges:
            out.append(f"| {label[e['from']]} | {label[e['to']]} | {e.get('kind', 'request')} | {e.get('label', '')} |")
    modes = modes_of(m)
    if modes:
        ids, names = [i for i, _ in modes], dict(modes)
        out += ["", "## Modes", "", "The page has a switch for " + ", ".join(t for _, t in modes) + ".", ""]
        rows = []
        for kind, obj, name in ([("part", p, p["label"]) for p in parts] +
                                [("edge", e, f"{label[e['from']]} → {label[e['to']]}") for e in edges]):
            ins = in_modes(obj, ids)
            if len(ins) < len(ids):
                rows.append(f"| {name} | Only in {', '.join(names[i] for i in ins)} |")
            for md, over in (obj.get("per_mode") or {}).items():
                if isinstance(over, dict) and md in names:
                    rows.append(f"| {name} | {names[md]}: " + "; ".join(f"{k} `{v}`" for k, v in over.items()) + " |")
        out += ["| Part or connection | Differs |", "|---|---|"] + rows if rows else ["No part differs between them."]
    for f in m.get("flows", []):
        fm = in_modes(f, [i for i, _ in modes]) if modes else []
        only = f" ({', '.join(dict(modes)[i] for i in fm)} only)" if modes and len(fm) < len(modes) else ""
        out += ["", f"## Flow: {f.get('title') or f.get('id')}{only}", ""]
        if f.get("note"):
            out += [f["note"], ""]
        for k, s in enumerate(f.get("steps", []), 1):
            hop = (f"{label.get(s.get('from'), s.get('from'))} → {label.get(s.get('to'), s.get('to'))}"
                   if s.get("from") != s.get("to") else f"inside {label.get(s.get('from'), s.get('from'))}")
            extra = f" ({s['label']})" if s.get("label") else ""
            out.append(f"{k}. **{s.get('title', '')}**: {hop}{extra}." + (f" {s['detail']}" if s.get("detail") else ""))
    unsure = [p for p in parts if p.get("state") == "unconfirmed"]
    if unsure or m.get("assumptions"):
        out += ["", "## Not confirmed", ""]
        out += [f"- {p['label']}: drawn from {p.get('source') or 'no file'}, not found in the code." for p in unsure]
        out += [f"- {a}" for a in m.get("assumptions", [])]
    return "\n".join(out) + "\n"


# ---------- CLI ----------
def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"diagram: cannot read {path}: {e}")


def opt(args, name, cast=str):
    if name in args:
        i = args.index(name)
        if i + 1 < len(args):
            return cast(args[i + 1])
    return None


def main(argv):
    if not argv or argv[0] not in ("check", "page", "md", "svg", "css", "drawio"):
        print(__doc__, file=sys.stderr)
        return 1
    cmd = argv[0]
    if cmd == "css":
        print(SVG_CSS + ".dia{overflow-x:auto;max-width:100%}")
        return 0
    if len(argv) < 2:
        print(f"diagram {cmd}: give the spec path", file=sys.stderr)
        return 1
    m = load(argv[1])
    if cmd == "check":
        errs, warns = check(m)
        for e in errs:
            print(f"error: {e}")
        for w in warns:
            print(f"warn: {w}")
        if not errs and not warns:
            print("ok")
        return 1 if errs else 0
    errs, _ = check(m)
    if errs:
        print("diagram: the spec has errors. Run `diagram.py check` first.", file=sys.stderr)
        return 1
    if cmd == "page":
        if len(argv) < 3:
            print("diagram page: give the out dir", file=sys.stderr)
            return 1
        print(page(m, argv[2]))
    elif cmd == "drawio":
        if len(argv) < 3 or argv[2].startswith("--"):
            print("diagram drawio: give the out file", file=sys.stderr)
            return 1
        sys.path.insert(0, HERE)
        from drawio import drawio_xml, export_png, verify
        text = drawio_xml(m)
        probs = verify(text)
        if probs:
            print("diagram drawio: the file would be broken:\n  " + "\n  ".join(probs), file=sys.stderr)
            return 1
        with open(argv[2], "w", encoding="utf-8") as fh:
            fh.write(text)
        print(argv[2])
        png = opt(argv, "--png")
        if png:
            ids = [i for i, _ in modes_of(m)]
            for k, mode in enumerate(ids or [None], 1):
                out = png if not mode else re.sub(r"(\.png)?$", f"-{mode}.png", png, count=1)
                ok, msg = export_png(argv[2], out, page=k)
                print(msg if ok else f"warn: {msg}")
    elif cmd == "md":
        text = markdown(m)
        if len(argv) > 2:
            with open(argv[2], "w", encoding="utf-8") as fh:
                fh.write(text)
            print(argv[2])
        else:
            print(text, end="")
    else:
        if opt(argv, "--flow") and step_of(m, opt(argv, "--flow"), opt(argv, "--step", int))[0] is None:
            print("diagram svg: no such flow, or the step is out of range (steps count from 1)", file=sys.stderr)
            return 1
        md = opt(argv, "--mode")
        if md and md not in [i for i, _ in modes_of(m)]:
            print("diagram svg: no such mode", file=sys.stderr)
            return 1
        svg, _ = render_svg(m, upto=opt(argv, "--upto", int), flow=opt(argv, "--flow"),
                            step=opt(argv, "--step", int), uid=opt(argv, "--uid") or "arr", mode=md)
        print(boxed(svg, placed(m)["width"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
