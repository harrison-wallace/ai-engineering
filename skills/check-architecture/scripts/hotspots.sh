#!/usr/bin/env bash
# Rank the files and folders that changed most in recent history. Read-only.
# Usage: hotspots.sh [-n <commits>] [<path>...]   (paths are relative to the repo root)
# Prints two TSV sections, "## files" and "## folders": changes<TAB>path, top 25 each.
# Skips merges, deleted files, lockfiles, manifests, generated and vendored files, and docs.
set -euo pipefail

n=200
if [ "${1:-}" = "-n" ]; then n=${2:?usage: hotspots.sh [-n <commits>] [<path>...]}; shift 2; fi
cd "$(git rev-parse --show-toplevel)"

skip='(^|/)(node_modules|vendor|dist|build|\.next|target|archive|coverage)/|(\.lock|-lock\.json|-lock\.yaml|\.min\.(js|css)|\.snap|\.map|\.md|\.svg|\.png|\.jpg)$|\.(gen|generated)\.[a-z]+$|_pb2\.py$|(^|/)(go\.sum|LICENSE[^/]*|package\.json|Cargo\.toml|pyproject\.toml|VERSION)$'

files=$(git log -n "$n" --no-merges --format= --name-only -- "$@" \
  | grep -v -E '^$' | grep -v -E "$skip" \
  | while IFS= read -r f; do [ -e "$f" ] && printf '%s\n' "$f"; done || true)

[ -n "$files" ] || { echo "hotspots: no source changes in the last $n commits" >&2; exit 1; }

echo "## files"
printf '%s\n' "$files" | sort | uniq -c | sort -rn | sed -n "1,25p" | sed -E 's/^ *([0-9]+) /\1\t/'
echo "## folders"
printf '%s\n' "$files" | while IFS= read -r f; do d=$(dirname "$f"); printf '%s\n' "$d"; done \
  | sort | uniq -c | sort -rn | sed -n "1,25p" | sed -E 's/^ *([0-9]+) /\1\t/'
