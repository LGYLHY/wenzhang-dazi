#!/usr/bin/env bash
# ============================================================
#   Wenzhang Dazi - one-click launcher (macOS / Linux)
#   Usage:  ./start.sh
#   Requires: Python 3.11+, Node 18+ (or WorkBuddy managed runtimes)
# ============================================================
set -e
cd "$(dirname "$0")"

PY=python
command -v python >/dev/null 2>&1 || PY=python3

# First run: install frontend deps
if [ ! -d "frontend/node_modules" ]; then
  echo "[INFO] Installing frontend dependencies..."
  (cd frontend && npm install)
fi

echo "Starting backend (port 8000) ..."
(cd backend && $PY -m uvicorn app:app --host 0.0.0.0 --port 8000) &
BACK_PID=$!

echo "Starting frontend (port 5173) ..."
(cd frontend && npm run dev -- --host 0.0.0.0 --port 5173 --strictPort) &
FRONT_PID=$!

sleep 10
echo ""
echo "============================================"
echo "  Open: http://localhost:5173"
echo "  Stop: Ctrl+C in this window"
echo "============================================"
wait
