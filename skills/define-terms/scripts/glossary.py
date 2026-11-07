#!/usr/bin/env python3
"""List the terms in a repo's glossaries. Read-only.

Usage: glossary.py [repo-root]
Prints TSV: glossary<TAB>term<TAB>avoid (comma-separated).
Reads GLOSSARY-MAP.md links when present, plus a root GLOSSARY.md.
Exits 1 with "no glossary" on stderr when there is none.
"""
import os
import re
import sys
from pathlib import Path

TERM = re.compile(r"^\*\*(.+?)\*\*:\s*(.*)$")
AVOID = re.compile(r"^_Avoid_:\s*(.+)$")
LINK = re.compile(r"\]\(([^)]*GLOSSARY\.md)\)")


def glossaries(root: Path) -> list[Path]:
    found: list[Path] = []
    top = root / "GLOSSARY.md"
    if top.is_file():
        found.append(top.resolve())
    gmap = root / "GLOSSARY-MAP.md"
    if gmap.is_file():
        for link in LINK.findall(gmap.read_text(encoding="utf-8")):
            path = (root / link).resolve()
            if path.is_file():
                if path not in found:
                    found.append(path)
            else:
                print(f"missing: {link} (linked from GLOSSARY-MAP.md)", file=sys.stderr)
    return found


def terms(path: Path):
    term, avoid = None, ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        t = TERM.match(line)
        if t:
            if term:
                yield term, avoid
            term, avoid = t.group(1).strip(), ""
            continue
        a = AVOID.match(line)
        if a and term:
            avoid = ", ".join(w.strip() for w in a.group(1).split(",") if w.strip())
    if term:
        yield term, avoid


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    files = glossaries(root)
    if not files:
        print("no glossary", file=sys.stderr)
        return 1
    for path in files:
        rel = os.path.relpath(path, root)
        for term, avoid in terms(path):
            print(f"{rel}\t{term}\t{avoid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
