#!/usr/bin/env bash
# Checks whether the current changeset touches any path considered
# "sensitive" (i.e. requires human approval before merge, no matter who or
# what authored the change). Exit code 0 = sensitive change detected.
#
# Usage: check_sensitive_paths.sh <base-ref> <head-ref>
#   e.g. check_sensitive_paths.sh origin/main HEAD

set -euo pipefail

BASE_REF="${1:-origin/main}"
HEAD_REF="${2:-HEAD}"

# Add/adjust patterns here as the demo's "policy" — this is intentionally a
# simple, readable stand-in for a real policy-as-code engine.
SENSITIVE_PATTERNS=(
  "^app/auth\.py$"
  "^app/payments\.py$"
)

CHANGED_FILES=$(git diff --name-only "${BASE_REF}" "${HEAD_REF}" || true)

echo "Changed files:"
echo "${CHANGED_FILES}"
echo "---"

MATCHED=""
for f in ${CHANGED_FILES}; do
  for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if echo "${f}" | grep -qE "${pattern}"; then
      MATCHED="${MATCHED}${f}\n"
    fi
  done
done

if [ -n "${MATCHED}" ]; then
  echo "SENSITIVE PATH CHANGE DETECTED:"
  echo -e "${MATCHED}"
  exit 0
else
  echo "No sensitive paths touched."
  exit 1
fi
