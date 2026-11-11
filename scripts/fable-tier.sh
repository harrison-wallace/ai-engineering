#!/usr/bin/env bash
# Print the judge-tier model and effort for a skill's Agent call.
# CLAUDE_FABLE_TIER=1 → Fable at medium, with an Opus fallback. Anything else → Opus at high.
# Skills call it at load time:  !`bash "${CLAUDE_SKILL_DIR}/../../scripts/fable-tier.sh"`
if [ "${CLAUDE_FABLE_TIER:-0}" = 1 ]; then
  echo "model: fable, effort: medium; if the Fable call fails, re-run it with model: opus, effort: high"
else
  echo "model: opus, effort: high"
fi
