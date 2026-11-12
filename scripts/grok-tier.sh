#!/usr/bin/env bash
# Print whether a skill may run the headless `grok` CLI on its own.
# CLAUDE_GROK_TIER=0 → off, to save Grok usage: take the no-Grok path. Unset or anything else → on.
# Skills call it at load time:  !`bash "${CLAUDE_SKILL_DIR}/../../scripts/grok-tier.sh"`
if [ "${CLAUDE_GROK_TIER:-1}" = 0 ]; then
  echo "Grok tier: off (CLAUDE_GROK_TIER=0). Do not run \`grok\` unless the user named a Grok route in this request. Take the same path as when Grok is not installed, and report Grok as \`off\`."
else
  echo "Grok tier: on. Run Grok where this skill says to."
fi
