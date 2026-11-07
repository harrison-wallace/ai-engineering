#!/usr/bin/env bash
# Check that README.md agrees with skills/: the badge count, one table row per
# skill, no rows for missing skills, and frontmatter names that match folders.
# Usage: scripts/check-readme.sh [--staged]   (exit 1 on any mismatch). Read-only.
#   --staged  check what the next commit holds (the index), not the working tree.
#             The pre-commit hook uses this.
set -uo pipefail
cd "$(git -C "$(dirname "$0")" rev-parse --show-toplevel)" || exit 1

staged=0
[ "${1:-}" = "--staged" ] && staged=1
# readf <path>: print a file from the index (--staged) or the working tree.
readf() { if [ "$staged" = 1 ]; then git show ":$1" 2>/dev/null; else cat "$1" 2>/dev/null; fi; }

fail=0
err() { echo "check-readme: $*" >&2; fail=1; }

if [ "$staged" = 1 ]; then
  skills=$(git ls-files 'skills/*/SKILL.md' | grep -E '^skills/[^/]+/SKILL\.md$' | sed -E 's|^skills/([^/]+)/SKILL\.md$|\1|' | sort)
else
  skills=$(find skills -mindepth 2 -maxdepth 2 -name SKILL.md -printf '%h\n' | sed 's|^skills/||' | sort)
fi
readme=$(readf README.md)
[ -n "$readme" ] || { echo "check-readme: README.md not found" >&2; exit 1; }
count=$(printf '%s\n' "$skills" | grep -c .)

badge=$(printf '%s\n' "$readme" | grep -oE 'badge/skills-[0-9]+-' | grep -oE '[0-9]+' || true)
[ -n "$badge" ] || err "no skills badge found in README.md"
[ -z "$badge" ] || [ "$badge" = "$count" ] || err "badge says $badge skills, skills/ has $count"

rows=$(printf '%s\n' "$readme" | grep -oE '^\| \[[^]]+\]\(skills/[^/)]+/SKILL\.md\)' | sed -E 's|.*\(skills/([^/]+)/.*|\1|' | sort)
for s in $(comm -23 <(printf '%s\n' "$skills") <(printf '%s\n' "$rows" | sort -u)); do
  err "skills/$s has no README table row"
done
for s in $(comm -13 <(printf '%s\n' "$skills") <(printf '%s\n' "$rows" | sort -u)); do
  err "README row links skills/$s, which does not exist$([ "$staged" = 1 ] && echo " in the index (not staged?)")"
done
for s in $(printf '%s\n' "$rows" | uniq -d); do
  err "skills/$s has more than one README table row"
done

for s in $skills; do
  name=$(readf "skills/$s/SKILL.md" | sed -n '2,/^---$/{s/^name:[[:space:]]*//p}' | head -n 1 || true)
  [ "$name" = "$s" ] || err "skills/$s/SKILL.md has name '${name:-<missing>}', expected '$s'"
done

[ "$fail" = 0 ] && echo "check-readme: ok ($count skills$([ "$staged" = 1 ] && echo ", staged"))"
exit "$fail"
