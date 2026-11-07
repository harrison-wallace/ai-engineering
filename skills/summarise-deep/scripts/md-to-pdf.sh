#!/usr/bin/env bash
# Render a Markdown file to PDF next to it: Python `markdown` builds the HTML,
# headless Chrome or Chromium prints it.
# Usage: md-to-pdf.sh <file.md>   → writes <file>.pdf, prints its path.
set -euo pipefail
[ $# -eq 1 ] && [ -f "$1" ] || { echo "usage: md-to-pdf.sh <file.md>" >&2; exit 1; }
src=$(realpath "$1")
out="${src%.*}.pdf"

browser=""
for b in google-chrome chromium-browser chromium; do
  command -v "$b" >/dev/null && { browser=$b; break; }
done
[ -n "$browser" ] || { echo "md-to-pdf: needs google-chrome or chromium" >&2; exit 1; }
python3 -c 'import markdown' 2>/dev/null || { echo "md-to-pdf: needs the Python markdown package (pip install markdown)" >&2; exit 1; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
python3 -I - "$src" "$tmp/page.html" <<'PY'
import sys, html, markdown
src, dst = sys.argv[1], sys.argv[2]
text = open(src, encoding="utf-8").read()
body = markdown.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])
title = next((l.lstrip("# ").strip() for l in text.splitlines() if l.startswith("# ")), "Summary")
css = """
body { font: 11pt/1.5 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; color: #1c1c1c; max-width: 46em; margin: 0 auto; }
h1 { font-size: 20pt; margin: 0 0 .4em; } h2 { font-size: 14pt; margin: 1.4em 0 .4em; border-bottom: 1px solid #ddd; }
h3 { font-size: 12pt; margin: 1.2em 0 .3em; }
code { font: 9.5pt ui-monospace, Menlo, Consolas, monospace; background: #f3f3f3; padding: 0 .2em; border-radius: 3px; }
pre { background: #f6f6f6; padding: .7em; border-radius: 4px; overflow-x: auto; page-break-inside: avoid; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; font-size: 10pt; page-break-inside: avoid; }
th, td { border: 1px solid #ccc; padding: .3em .5em; text-align: left; vertical-align: top; }
th { background: #f1f1f1; }
@page { margin: 18mm 16mm; }
"""
with open(dst, "w", encoding="utf-8") as f:
    f.write(f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
            f"<style>{css}</style></head><body>{body}</body></html>")
PY
"$browser" --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$out" "file://$tmp/page.html" >/dev/null 2>&1
[ -s "$out" ] || { echo "md-to-pdf: $browser did not write $out" >&2; exit 1; }
echo "$out"
