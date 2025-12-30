#!/bin/bash
# =============================================================================
# SISI LOLA API - Server Restart Script
# =============================================================================
# Usage: bash restart_server.sh
# =============================================================================

echo "🛑 Killing any existing servers on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

echo "⏳ Waiting for port to release..."
sleep 2

echo "🚀 Starting Sisi Lola API Server..."
cd /mnt/c/Users/POK28/Dropbox/Sisi_Lola

# Activate virtual environment
source sisi_lola_api/venv/bin/activate

# Set PYTHONPATH for module imports
export PYTHONPATH=/mnt/c/Users/POK28/Dropbox/Sisi_Lola

# Clear Python cache to avoid stale imports
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo "==================================================================="
echo "📌 Entry Point: sisi_lola_api.app.main:app"
echo "📌 Routes: /demo, /dashboard, /api/v2/vibe/demo-chat"
echo "==================================================================="

# Start the server with the CLEAN main.py
python -m uvicorn sisi_lola_api.app.main:app --reload --host 0.0.0.0 --port 8000
