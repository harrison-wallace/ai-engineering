#!/usr/bin/env bash
# Condense Claude Code session transcripts (.jsonl) into a reviewable digest.
# Usage: digest.sh [-b] <session.jsonl> [more.jsonl ...] > digest.md
#   -b  brief: drop assistant text and tool counts (for multi-session runs)
# Keeps: user messages, slash commands, skill and agent calls, tool errors and
# denials, short assistant text. Drops: tool output, thinking, injected skill
# bodies, system reminders. Read-only; needs jq.
set -euo pipefail
command -v jq >/dev/null || { echo "digest.sh: jq is required" >&2; exit 1; }
brief=0
if [ "${1:-}" = "-b" ]; then brief=1; shift; fi
[ $# -ge 1 ] || { echo "usage: digest.sh [-b] <session.jsonl> [...]" >&2; exit 1; }

for f in "$@"; do
  [ -f "$f" ] || { echo "digest.sh: not a file: $f" >&2; continue; }
  echo "# Session $(basename "$f" .jsonl)"
  jq -rn 'first(inputs | [.cwd, .gitBranch] | select(.[0] != null)) | "cwd: \(.[0])  branch: \(.[1] // "-")"' "$f"
  echo
  jq -rn '
    def clip($n): if length > $n then .[0:$n] + " …[+\(length - $n)]" else . end;
    def oneline: gsub("\\s+"; " ");
    foreach (inputs | select(.isSidechain != true)) as $e (0; . + 1;
      . as $i
      | if $e.type == "user" and ($e.message.content | type) == "string" then
          ($e.message.content) as $c
          | if ($c | test("<command-name>")) then
              "[\($i)] CMD " + (($c | capture("<command-name>(?<n>[^<]*)</command-name>").n) // "?")
              + " " + ((($c | capture("<command-args>(?<a>[^<]*)</command-args>").a) // "") | oneline | clip(300))
            elif ($c | startswith("This session is being continued")) then
              "[\($i)] COMPACTED (summary of earlier context follows in transcript)"
            elif ($c | startswith("<")) then empty
            else "[\($i)] USER " + ($c | oneline | clip(800)) end
        elif $e.type == "user" and ($e.message.content | type) == "array" then
          $e.message.content[]
          | if .type == "text" and ((.text | startswith("<") or startswith("Base directory for this skill")) | not) then
              "[\($i)] USER " + (.text | oneline | clip(800))
            elif .type == "tool_result" and .is_error == true then
              "[\($i)] ERROR " + (.content | tostring | oneline | clip(240))
            else empty end
        elif $e.type == "assistant" then
          $e.message.content[]?
          | if .type == "text" then "[\($i)] CLAUDE " + (.text | oneline | clip(400))
            elif .type == "tool_use" and .name == "Skill" then
              "[\($i)] SKILL " + (.input.skill // "?") + " " + ((.input.args // "") | oneline | clip(200))
            elif .type == "tool_use" and .name == "Agent" then
              "[\($i)] AGENT model=\(.input.model // "inherit") effort=\(.input.effort // "-") type=\(.input.subagent_type // "general-purpose") :: "
              + ((.input.description // "") | oneline) + " :: " + ((.input.prompt // "") | oneline | clip(300))
            elif .type == "tool_use" then "[\($i)] TOOL " + .name
            else empty end
        else empty end
    )' "$f" \
  | awk '
      # Collapse runs of plain TOOL lines into one count line.
      /^\[[0-9]+\] TOOL / { split($0, p, " TOOL "); tools[p[2]]++; n++; next }
      { if (n) { line = "        tools:"; for (t in tools) line = line " " t "×" tools[t]; print line; delete tools; n = 0 } print }
      END { if (n) { line = "        tools:"; for (t in tools) line = line " " t "×" tools[t]; print line } }' \
  | if [ "$brief" = 1 ]; then grep -Ev '^(\[[0-9]+\] CLAUDE |        tools:)' || true; else cat; fi
  echo
done
