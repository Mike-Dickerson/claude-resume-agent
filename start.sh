#!/usr/bin/env bash
# Resume Agent launcher (macOS / Linux / Git Bash)
# Usage:  ./start.sh             start a new session
#         ./start.sh --continue  pick up the last session
#         ./start.sh --web       open the web app instead (http://127.0.0.1:8765)
set -e
cd "$(dirname "$0")"
echo "Resume Agent"

PY=$(command -v python3 || command -v python || true)
if [ -z "$PY" ]; then
  echo "Python 3.10+ is required: https://www.python.org/downloads/"; exit 1
fi
if ! "$PY" -c "import docx, pypdf, fastapi, uvicorn, multipart, httpx" 2>/dev/null; then
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

case "$1" in
  --web) exec "$PY" web/server.py ;;
  --continue) exec claude --continue ;;
  *) exec claude "Hi" ;;
esac
