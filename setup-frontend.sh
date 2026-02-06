#!/bin/zsh
set -euo pipefail

ROOT="$(pwd)"
FRONTEND="$ROOT/frontend"

cd "$FRONTEND"
npm install

