#!/usr/bin/env bash
# Symlink skills from this repo into every Claude Code profile (~/.claude, ~/.claude-*).
# Usage: scripts/install-skill.sh <name>...            install (or refresh) links
#        scripts/install-skill.sh --remove <name>...   remove links
# Only touches symlinks that point into this repo; a real directory is left alone.
set -euo pipefail
repo=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)

remove=0
if [ "${1:-}" = "--remove" ]; then remove=1; shift; fi
[ $# -ge 1 ] || { echo "usage: $0 [--remove] <skill>..." >&2; exit 1; }

profiles=()
for d in "$HOME/.claude" "$HOME"/.claude-*; do
  [ -d "$d" ] && profiles+=("$d")
done
[ ${#profiles[@]} -gt 0 ] || { echo "install-skill: no ~/.claude* profiles found" >&2; exit 1; }

for name in "$@"; do
  src="$repo/skills/$name"
  if [ "$remove" = 0 ] && [ ! -f "$src/SKILL.md" ]; then
    echo "install-skill: $src/SKILL.md not found, skipping" >&2; continue
  fi
  for d in "${profiles[@]}"; do
    link="$d/skills/$name"
    if [ -e "$link" ] && [ ! -L "$link" ]; then
      echo "skip   $link (real directory, not a symlink)"; continue
    fi
    if [ "$remove" = 1 ]; then
      if [ -L "$link" ]; then
        case "$(readlink "$link")" in
          "$repo"/*) rm "$link"; echo "remove $link" ;;
          *) echo "skip   $link (points outside this repo)" ;;
        esac
      fi
    else
      mkdir -p "$d/skills"
      ln -sfn "$src" "$link"; echo "link   $link -> $src"
    fi
  done
done
