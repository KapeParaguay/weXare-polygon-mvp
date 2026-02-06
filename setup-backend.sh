#!/bin/zsh
set -euo pipefail

ROOT="$(pwd)"
BACKEND="$ROOT/backend"

python3 -m venv "$BACKEND/.venv"
"$BACKEND/.venv/bin/python" -m pip install --upgrade pip
"$BACKEND/.venv/bin/python" -m pip install -r "$BACKEND/requirements.txt"

echo "Backend venv ready at $BACKEND/.venv"
