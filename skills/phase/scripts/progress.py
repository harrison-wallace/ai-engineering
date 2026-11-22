#!/usr/bin/env python3
"""Print the facts a /phase status or sync report needs, counted from the files. No model, no network.

Usage: progress.py <repo> [--slice <key>]

Reads docs/plans/NOW.md, docs/plans/BOARD.md, the current phase doc, the side track's phase doc,
and git. Prints plain lines: the phase and its goal, the progress bar, the slice in focus with its
next open items (each with its doc line), the open decisions (with Blocks and any recommendation
the doc holds), the side track, the next planned phase, the last sync, the recent commits, and the
uncommitted count. --slice picks the slice in focus (default: NOW's Slice, else the first open).

The report wording is in ../references/report.md. This script only counts.
"""
import importlib.util
import os
import re
import subprocess
import sys
from datetime import date, timedelta

HERE = os.path.dirname(os.path.realpath(__file__))
spec = importlib.util.spec_from_file_location("render_board", os.path.join(HERE, "render-board.py"))
rb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rb)

def git(repo, *args):
    try:
        return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.TimeoutExpired):
        return ""


def line_of(lines, needle, start=0):
    """1-based line of the first line from `start` that holds the needle's first 40 characters."""
    key = " ".join(needle.split())[:40]
    for i in range(start, len(lines)):
        if key and key in " ".join(lines[i].split()):
            return i + 1
    return 0


def first_sentence(text, cap=140):
    t = " ".join(re.sub(r"\*\*|`", "", text).split())
    m = re.match(r"(.+?[.?!:])(\s|$)", t)
    t = m.group(1) if m and len(m.group(1)) > 20 else t
    return t if len(t) <= cap else t[:cap - 1].rsplit(" ", 1)[0] + "…"


def bar(sl, cur_key):
    return "".join("■" if s["done"] else "▣" if s["key"] == cur_key else "□" for s in sl)


def decisions(md, lines):
    """Every `- Dn: …` line in ## Open decisions, with its wrapped lines joined."""
    body = rb.find_section(rb.sections(md), "Open decisions")
    out = []
    for b in rb.bullets(body):
        m = re.match(r"^(D\d+):\s*(.+)$", b)
        if not m or "<question>" in m.group(2):
            continue
        text = m.group(2)
        blocks = re.search(r"Blocks:\s*(.+?)(?:\.\s|\.$|$)", text)
        rec = re.search(r"Recommended:\s*(.+?)(?:\.\s|\.$|$)", text)
        out.append({"id": m.group(1), "q": first_sentence(text), "blocks": blocks.group(1) if blocks else "",
                    "rec": rec.group(1) if rec else "", "line": line_of(lines, f"- {m.group(1)}:")})
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    repo = os.path.abspath(args[0])
    want = None
    if "--slice" in sys.argv:
        i = sys.argv.index("--slice")
        if i + 1 >= len(sys.argv):
            raise SystemExit(__doc__)
        want = sys.argv[i + 1]
    plans = os.path.join(repo, "docs", "plans")
    board_md = rb.read(os.path.join(plans, "BOARD.md"))
    if not board_md:
        raise SystemExit("progress: no docs/plans/BOARD.md. Run /phase init.")
    rows, _later, log = rb.parse_board(board_md)
    now = rb.parse_now(rb.read(os.path.join(plans, "NOW.md")))
    cur_id = (re.match(rf"\s*({rb.PHASE_ID})\b", now.get("Phase", "")) or [None, ""])[1]
    current = next((r for r in rows if r["id"] == cur_id), None) or next(
        (r for r in rows if r["status"] == "in progress"), None)
    in_prog = [r["id"] for r in rows if r["status"] == "in progress"]
    if len(in_prog) > 1:
        print(f"warn: {len(in_prog)} phases are in progress ({', '.join(in_prog)}). The board allows one.")
    today = date.today()

    if not current:
        print("phase: none")
    else:
        rel = os.path.normpath(os.path.join("docs", "plans", current["doc"])) if current["doc"] else ""
        md = rb.read(os.path.join(repo, rel)) if rel else ""
        lines = md.splitlines()
        ph = rb.parse_phase(md) if md else None
        print(f"phase: {current['id']} · {current['name']}")
        if rel:
            print(f"doc: {rel}")
        if ph and ph["goal"]:
            print(f"goal: {' '.join(ph['goal'].split())}")
        sl = ph["slices"] if ph else []
        if sl:
            now_key = (re.match(r"\s*([0-9]+[a-z]?)", now.get("Slice", "")) or [None, ""])[1]
            keys = [s["key"] for s in sl]
            cur_key = want if want in keys else now_key if now_key in keys else next(
                (s["key"] for s in sl if not s["done"]), None)
            done = sum(s["done"] for s in sl)
            cs = next((s for s in sl if s["key"] == cur_key), None)
            where = f"slice {cur_key}, {cs['name']}" if cs else "every slice ticked"
            items = cs["items"] if cs else []
            ticks = f": {sum(i['done'] for i in items)} of {len(items)} items done" if items else ""
            print(f"bar: {bar(sl, cur_key)}  {where}{ticks} · {done} of {len(sl)} slices done")
            print(f"slices: {done} done · {1 if cs and not cs['done'] else 0} now · "
                  f"{len(sl) - done - (1 if cs and not cs['done'] else 0)} to go")
            if cs:
                start = line_of(lines, cs["text"].split("\n")[0])
                open_items = [i for i in items if not i["done"]]
                if open_items:
                    print(f"next items ({len(open_items)} open):")
                    for i in open_items[:3]:
                        print(f"  {rel}:{line_of(lines, i['text'].split(chr(10))[0], start)}  {first_sentence(i['text'])}")
                elif items:
                    print("next items: none. Every item is ticked: suggest /phase advance slice.")
            if done == len(sl):
                print("note: every slice ticked. Check the Definition of Done: suggest /phase advance phase.")
        if ph and ph["dod"]:
            print(f"done when ({len(ph['dod'])}): {first_sentence(ph['dod'][0])}{' …' if len(ph['dod']) > 1 else ''}")
        ds = decisions(md, lines) if md else []
        print(f"decisions ({len(ds)}):")
        for d in ds:
            extra = (f" | blocks: {d['blocks']}" if d["blocks"] else " | blocks: not said") + (
                f" | doc recommends: {d['rec']}" if d["rec"] else "")
            print(f"  {d['id']} {rel}:{d['line']}  {d['q']}{extra}")

    named = re.findall(rf"\b(?:{rb.PHASE_ID})\b", re.split(r"\s[—–-]\s|[(:]", now.get("Parallel", ""))[0])
    for r in rows:
        if r is not current and (r["id"] in named or r["status"] == "in progress"):
            ph = rb.parse_phase(rb.read(os.path.join(plans, r["doc"]))) if r["doc"] else None
            n = f" · {sum(s['done'] for s in ph['slices'])} of {len(ph['slices'])} slices" if ph and ph["slices"] else ""
            print(f"beside: {r['id']} · {r['name']}{n} · NOW says: {first_sentence(now.get('Parallel', ''), 200)}")
    idx = rows.index(current) if current else -1
    nxt = next((r for r in rows[idx + 1:] if r["status"] == "shaped" and r["id"] not in named), None)
    print(f"after: {nxt['id']} · {nxt['name']}" if nxt else "after: none planned")
    if now.get("Blocked") and now["Blocked"].lower() != "none":
        print(f"blocked (NOW): {now['Blocked']}")

    upd = now.get("Updated", "")
    last = git(repo, "log", "-1", "--format=%cs").strip()
    try:
        gap = (today - date.fromisoformat(last)).days if last else None
    except ValueError:
        gap = None
    print(f"last sync: {upd or 'unknown'} · last commit: {last or 'none'}"
          + (f" ({gap} day{'s' if gap != 1 else ''} ago)" if gap is not None else ""))
    if upd:
        after = [l for l in git(repo, "log", f"--since={upd} 23:59:59", "--format=%h %cs %s").splitlines() if l]
        print(f"commits after the last sync: {len(after)}" + (" → stale, run /phase sync" if after else ""))
    # The last working stretch: commits within 3 days of the last commit, newest first, at most 8.
    if last and gap is not None:
        since = (date.fromisoformat(last) - timedelta(days=3)).isoformat()
        recent = [l for l in git(repo, "log", f"--since={since}", "--format=%h %cs %s", "-8").splitlines() if l]
        print("recent commits:")
        for l in recent:
            print(f"  {l}")
    if log:
        print("board log (last 3):")
        for d, t in log[-3:]:
            print(f"  {d} {first_sentence(t, 160)}")
    dirty = [l for l in git(repo, "status", "--porcelain").splitlines() if l]
    print(f"uncommitted: {len(dirty)} path{'s' if len(dirty) != 1 else ''}")


if __name__ == "__main__":
    main()
