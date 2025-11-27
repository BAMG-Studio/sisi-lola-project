#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ ! -d "venv" ]; then
  echo "[ERROR] Python virtual environment not found at $ROOT_DIR/venv" >&2
  echo "Create it with: python3 -m venv venv" >&2
  exit 1
fi

source "venv/bin/activate"

HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
RELOAD=${RELOAD:-1}

CMD=("$ROOT_DIR/venv/bin/python" "-m" "uvicorn" "app.main:app" "--host" "$HOST" "--port" "$PORT")

if [ "$RELOAD" != "0" ]; then
  CMD+=("--reload")
fi

echo "🚀 Starting Sisi Lola API on $HOST:$PORT (reload=${RELOAD})"
echo "    Using environment from $ROOT_DIR/.env"

exec "${CMD[@]}"
