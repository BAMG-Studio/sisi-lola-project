#!/bin/bash
# ============================================================================
# SISI LOLA API - SAFE START SCRIPT
# Bypasses REPL issues and launches the Modal-integrated API
# ============================================================================

set -e

# Clear any force-interactive flags to prevent >>> prompt
unset PYTHONINSPECT
unset PYTHONSTARTUP
unalias python3 2>/dev/null || true

echo "🇳🇬 =============================================="
echo "   SISI LOLA - Nigerian AI Virtual Host"
echo "=============================================="

# 1. Environment Activation
if [ -d "venv_wsl" ]; then
    source venv_wsl/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# 2. Path Configuration
export PYTHONPATH=$PYTHONPATH:$(pwd)

# 3. Direct Launch
echo "🚀 Starting Accelerated API..."
echo "📍 Web Demo: http://localhost:8000/demo"
echo "=============================================="

# Run using the absolute venv python to be 100% safe
python3 -m uvicorn sisi_lola_api.app.main:app --host 0.0.0.0 --port 8000 --reload
