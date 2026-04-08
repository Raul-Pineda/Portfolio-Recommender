#!/bin/bash
set -e
cd "$(dirname "$0")"

# ── 1. Check for Python 3.10+ ───────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
  echo "❌  Python 3 is required but not found. Install it from https://www.python.org/downloads/"
  exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
  echo "❌  Python 3.10+ is required (found $PY_VERSION)"
  exit 1
fi
echo "✅  Python $PY_VERSION"

# ── 2. Create / activate virtual environment ─────────────────────────────────
if [ ! -d ".venv" ]; then
  echo "📦  Creating virtual environment…"
  python3 -m venv .venv
fi
source .venv/bin/activate
echo "✅  Virtual environment activated"

# ── 3. Install Python dependencies ───────────────────────────────────────────
echo "📦  Installing Python dependencies…"
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅  Python dependencies installed"

# ── 4. Check for Node.js (needed for frontend) ──────────────────────────────
if ! command -v node &>/dev/null; then
  echo "❌  Node.js is required but not found."
  echo "   Install it from https://nodejs.org/ (LTS recommended)"
  exit 1
fi
echo "✅  Node $(node -v)"

# ── 5. Install frontend dependencies ────────────────────────────────────────
if [ ! -d "frontend/node_modules" ]; then
  echo "📦  Installing frontend dependencies…"
  (cd frontend && npm install)
fi
echo "✅  Frontend dependencies ready"

# ── 6. Kill old instances ────────────────────────────────────────────────────
pkill -f "uvicorn backend.app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true

# ── 7. Start backend & frontend ─────────────────────────────────────────────
echo ""
echo "🚀  Starting backend on http://localhost:8001"
echo "🚀  Starting frontend (Vite dev server)…"
echo ""

uvicorn backend.app:app --port 8001 &
BACK=$!

(cd frontend && npm run dev -- --open) &
FRONT=$!

trap "kill $BACK $FRONT 2>/dev/null" EXIT
wait
