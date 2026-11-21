#!/usr/bin/env python3
"""Render a repo's phase board as one self-contained HTML page. No model, no network.

Usage: render-board.py <repo> [<out-dir>] [--live]

Reads   docs/plans/BOARD.md, docs/plans/NOW.md, the current phase doc, docs/plans/map.json,
        and the infra inventory (../../draw-infra/scripts/infra-inventory.py). The SVG comes
        from ../../draw-infra/scripts/diagram.py.
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
BASE_CSS = os.path.join(HERE, "..", "..", "serve-page", "assets", "base.css")
THEME_CSS = os.path.join(HERE, "..", "..", "serve-page", "assets", "theme.css")
DRAW = os.path.join(HERE, "..", "..", "draw-infra", "scripts")
INVENTORY = os.path.join(DRAW, "infra-inventory.py")
sys.path.insert(0, DRAW)
from diagram import LANES, SVG_CSS, copy_fonts, render_svg, valid_map  # noqa: E402  the shared renderer


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
def infra_svg(m, decisions):
    svg, bad = render_svg(m, decisions)
    warn = (f'<div class="card">Left off the map (needs an id, a lane from {", ".join(LANES)}, and a whole-number row): '
            f'{esc(", ".join(bad))}. Run <code>/phase map</code>.</div>' if bad else "")
    if not svg:
        return warn + '<p class="muted">No <code>docs/plans/map.json</code> yet. Run <code>/phase map</code>.</p>'
    return warn + svg


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
.kv{display:grid;grid-template-columns:7rem 1fr;gap:.375rem .75rem}.kv b{color:var(--muted);font-weight:600}
.bar{height:.375rem;background:var(--line);overflow:hidden}.bar i{display:block;height:100%;background:var(--accent)}
.flow{display:flex;flex-wrap:wrap;gap:.75rem 1rem}
.slice{flex:1 1 9.375rem;max-width:13.75rem;border-top:2px solid var(--fg);padding:.375rem 0;cursor:pointer;font-size:.9375rem}
.slice .k{font-size:.8125rem;font-style:italic;color:var(--muted)}
.slice.done{border-top-color:var(--line);color:var(--muted)}.slice.current{border-top-color:var(--accent);background:var(--accent-soft);padding:.375rem .5rem}
.slice.open{border-top-style:dashed}.slice.waiting{border-top:2px dashed var(--amber)}
.here{font-size:.875rem;font-style:italic;font-weight:600;color:var(--accent)}.here.side{color:var(--amber)}
.ghead{font:600 1.125rem var(--serif);color:var(--fg);margin:1.75rem 0 .375rem}
.rail{border-left:1px solid var(--line);margin-left:.4375rem}
.rrow{display:flex;gap:.75rem;padding:.625rem .75rem .625rem 0;color:var(--fg);text-decoration:none;position:relative}
a.rrow:hover .rbody{background:var(--accent-soft)}
.rrow .dot{flex:0 0 .875rem;height:.875rem;border-radius:50%;margin:.3125rem 0 0 -.5rem;background:var(--bg);border:2px solid var(--muted)}
.rrow.k-here .dot{background:var(--accent);border-color:var(--accent)}.rrow.k-side .dot{background:var(--amber);border-color:var(--amber)}
.rrow.k-done .dot{background:var(--muted)}.rrow.k-done{padding:.25rem .75rem .25rem 0;color:var(--muted);font-size:.9375rem}
.rbody{flex:1;padding:2px .5rem}
.rrow.k-here .rbody{background:var(--accent-soft);padding:.75rem 1rem}
.rrow.k-side .rbody{border-top:1px dashed var(--amber);padding:.625rem .5rem}
.rtop{display:flex;flex-wrap:wrap;align-items:baseline;gap:.375rem .75rem}
.note{font-size:.9375rem;color:var(--muted);margin-top:2px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.prog{display:flex;align-items:center;gap:.5rem;font-size:.875rem;color:var(--muted);margin-top:.375rem}.prog .bar{width:8.75rem}
.later,.log{font-size:.9375rem}
.pick{display:flex;flex-wrap:wrap;gap:.25rem;margin:.75rem 0}
.pchip.k-here{color:var(--accent);border-bottom-color:var(--accent)}.pchip.k-side{color:var(--amber);border-bottom-color:var(--amber)}
.pchip.k-done{color:var(--muted);border-bottom-color:var(--line)}
.phead .rtop{font:600 1.25rem var(--serif)}.phead p{margin:.375rem 0}
.spot .stop{font:600 1.125rem var(--serif)}.spot .sdetail{font-size:1rem}
.srow.done .sdetail{display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.srow.done.open .sdetail{display:block}.srow.done .chk{display:none}.srow.done.open .chk{display:block}
.srow.done .stop::after{content:"tap to read";font-size:.8125rem;font-style:italic;color:var(--muted)}.srow.done.open .stop::after{content:""}
.pgrid{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:2rem;align-items:start}
@media (max-width:47.5rem){.pgrid{grid-template-columns:1fr}}
.pgrid aside h3{margin:0 0 .375rem}.pgrid aside{margin-top:2.125rem}.dod{padding-left:1.125rem;margin:0;font-size:.9375rem}
ol.slices{list-style:none;padding:0;margin:.625rem 0 .625rem .5625rem;border-left:1px solid var(--line)}
.srow{display:flex;gap:.75rem;padding:.5rem 0;cursor:pointer}
.srow .mark{flex:0 0 1.125rem;height:1.125rem;border-radius:50%;margin:.25rem 0 0 -.625rem;background:var(--bg);border:2px solid var(--muted);
display:flex;align-items:center;justify-content:center;font-size:.6875rem;color:var(--on-accent)}
.srow.done .mark{background:var(--ok);border-color:var(--ok)}.srow.done .mark::after{content:"✓"}
.srow.current .mark{background:var(--accent);border-color:var(--accent);box-shadow:0 0 0 .25rem var(--accent-soft)}
.srow.waiting .mark{border-color:var(--amber)}
.sbody{flex:1;min-width:0;padding:.25rem .625rem}
.srow.current .sbody{background:var(--accent-soft);padding:.625rem 1rem}
.srow.done .sbody{color:var(--muted)}.srow.done .sdetail{font-size:.9375rem}
.stop{display:flex;flex-wrap:wrap;align-items:baseline;gap:.375rem .75rem}
.skey{font-weight:600;color:var(--muted);min-width:1.375rem}
.sdetail{margin:.25rem 0;font-size:.9375rem}.srow.current .sdetail{font-size:1rem}
ul.chk{list-style:none;padding:0;margin:.375rem 0;font-size:.9375rem}ul.chk li{margin:2px 0}ul.chk li.ok{color:var(--muted)}
.dcard .id{font:600 1.0625rem var(--serif);color:var(--amber)}
.map{font-size:.875rem;display:inline-block;margin-top:.25rem}
.pipe{display:flex;flex-wrap:wrap;gap:.375rem .75rem;align-items:center;font-size:.875rem}.pipe span{border-bottom:1px dashed var(--muted)}
body.hide-built .part-g.built,body.hide-built .edge-g.built,body.hide-building .building,
body.hide-planned .planned,body.hide-decision .decision{display:none}
body.focus svg [data-id]:not(.hl){opacity:.22}body.focus .slice:not(.hl),body.focus .dcard:not(.hl){opacity:.45}
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
<style>{read(BASE_CSS)}{read(THEME_CSS)}{CSS}{SVG_CSS}</style></head><body>
<header><h1>{esc(title)} · phase board</h1>
<div class="muted">{esc(current["id"] + " · " + current["name"] if current else "No phase in progress")} · rendered {date.today().isoformat()}{" · live" if live else ""}</div>
<div class="warn">This page holds host names and the plan. Any device on your LAN can open it while the server runs.</div>
<div class="legend"><span><i class="sw"></i>Built</span><span><i class="sw building"></i>Building</span><span><i class="sw planned"></i>Planned</span><span><i class="sw decision"></i>Open decision</span></div>
<nav class="tabs">{"".join(f'<a href="#{i}">{n}</a>' for i, n, _ in tabs)}</nav></header>
<main>{"".join(f'<section class="panel" id="{i}"><h2>{n}</h2>{"".join(body)}</section>' for i, n, body in tabs)}</main>
<script>{dynamic}</script><script>{PICK_JS}</script>{f"<script>{LIVE_JS}</script>" if live else ""}
</body></html>"""
    os.makedirs(out_dir, exist_ok=True)
    copy_fonts(out_dir)
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
