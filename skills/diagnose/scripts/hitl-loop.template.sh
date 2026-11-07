#!/usr/bin/env bash
# Human-in-the-loop repro loop for the diagnose skill.
# Adapted from mattpocock/skills (MIT), skills/engineering/diagnosing-bugs.
#
# Copy this file to the scratchpad, edit the steps between the markers, and
# ask the user to run `bash <path>` in their own terminal. Neither the agent's
# Bash tool nor Claude Code's `!` prefix gives a script an interactive input.
#
#   step "<instruction>"        show an instruction, wait for Enter
#   capture VAR "<question>"    show a question, read the answer into VAR
#
# At the end, every captured value prints as KEY=VALUE and is written to
# <path>.out (or $HITL_OUT) for the agent to read. The agent reads that file
# into the chat, so capture observations only. Make signing in, and anything
# secret, a step.

set -euo pipefail

out="${HITL_OUT:-$0.out}"
[ -t 0 ] || { echo "Run this in your own terminal: bash $0" >&2; exit 1; }
captured=()

step() {
  printf '\n>>> %s\n' "$1"
  read -r -p "    [Enter when done] " _
}

capture() {
  local var="$1" question="$2" answer
  printf '\n>>> %s\n' "$question"
  read -r -p "    > " answer
  printf -v "$var" '%s' "$answer"
  captured+=("$var")
}

# --- edit below ---------------------------------------------------------

step "Open the app at http://localhost:3000 and sign in."

capture ERRORED "Click the 'Export' button. Did it show an error? (y/n)"

capture ERROR_MSG "Paste the error message, or type 'none':"

# --- edit above ---------------------------------------------------------

printf '\n--- Captured ---\n'
: > "$out"
for v in "${captured[@]}"; do
  printf '%s=%s\n' "$v" "${!v}" | tee -a "$out"
done
printf '\nSaved to %s. Tell the agent you are done.\n' "$out"
