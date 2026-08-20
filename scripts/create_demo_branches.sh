#!/usr/bin/env bash
# Builds every branch needed for the demo, in order, from the current repo.
# Run this ONCE after you've pushed the initial baseline (main) to GitHub.
#
# Usage: ./scripts/create_demo_branches.sh <remote-name>
#   e.g. ./scripts/create_demo_branches.sh origin
#
# Creates:
#   feature/ai-agent-config-tuning     (Act 1a — ungated path, non-sensitive)
#   feature/ai-agent-auth-refactor     (Act 1b — gated path, sensitive)
#   nightly                            (Act 2 — all three AI PRs merged)

set -euo pipefail
REMOTE="${1:-origin}"

echo "==> Ensuring we're starting clean from main"
git checkout main
git pull "${REMOTE}" main

echo "==> Creating feature/ai-agent-config-tuning (Act 1a: ungated)"
git checkout -b feature/ai-agent-config-tuning
cp branch-patches/ai-config-tuning/config.py app/config.py
git add app/config.py
git commit -m "AI agent: tune retry/timeout defaults to reduce infra cost"
git checkout main

echo "==> Creating feature/ai-agent-auth-refactor (Act 1b: gated)"
git checkout -b feature/ai-agent-auth-refactor
cp branch-patches/ai-auth-refactor/auth.py app/auth.py
git add app/auth.py
git commit -m "AI agent: refactor token verification for clarity"
git checkout main

echo "==> Creating nightly (Act 2: all three AI PRs merged overnight)"
git checkout -b nightly
cp branch-patches/ai-auth-refactor/auth.py app/auth.py
cp branch-patches/ai-config-tuning/config.py app/config.py
cp branch-patches/ai-notification-tweak/notifications.py app/notifications.py
git add app/auth.py app/config.py app/notifications.py
git commit -m "Nightly integration: merge overnight AI agent PRs (auth, config, notifications)"
git checkout main

echo "==> Done. Push branches with:"
echo "    git push ${REMOTE} feature/ai-agent-config-tuning"
echo "    git push ${REMOTE} feature/ai-agent-auth-refactor"
echo "    git push ${REMOTE} nightly"
