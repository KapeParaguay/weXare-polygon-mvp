#!/usr/bin/env bash
set -euo pipefail

BRANCH="feat/privy-auth-unified-feed"
MSG="${1:-feat: e2e prod guide + fee + config + tests}"

git status -sb
git add -A
git commit -m "$MSG"
git push -u origin "$BRANCH"
