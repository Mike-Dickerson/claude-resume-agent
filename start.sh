#!/usr/bin/env bash
# Resume Agent launcher (macOS / Linux / Git Bash)
# Usage:  ./start.sh             start a new session
#         ./start.sh --continue  pick up the last session
set -e
cd "$(dirname "$0")"
echo "Resume Agent"

PY=$(command -v python3 || command -v python || true)
if [ -z "$PY" ]; then
  echo "Python 3.10+ is required: https://www.python.org/downloads/"; exit 1
fi
if ! "$PY" -c "import docx, pypdf" 2>/dev/null; then
  echo "Installing Python packages..."
  "$PY" -m pip install --quiet -r requirements.txt
fi

if ! command -v claude >/dev/null 2>&1; then
  echo "Claude Code is not installed. Install it with:"
  echo "  curl -fsSL https://claude.ai/install.sh | bash"
  echo "then open a new terminal and run ./start.sh again."
  exit 1
fi

if ! claude auth status 2>/dev/null | grep -q '"loggedIn": *true'; then
  echo "You're not signed in to Claude yet. Opening sign-in..."
  claude auth login
fi

if [ "$1" = "--continue" ]; then exec claude --continue; else exec claude "Hi"; fi
