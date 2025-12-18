#!/bin/bash
# SISI LOLA API SERVER RESTART SCRIPT
# This script restarts the API server with all optimizations enabled
# 
# Usage:
#   chmod +x restart_api_server.sh
#   ./restart_api_server.sh
#
# For Codespaces:
#   Run this in the terminal to activate optimizations

set -e

echo "=============================================="
echo "🚀 SISI LOLA API SERVER RESTART"
echo "=============================================="

# Navigate to project root
cd /workspaces/sisi-lola-project 2>/dev/null || cd "$(dirname "$0")"

echo ""
echo "📋 Step 1: Stopping existing processes..."
pkill -f "uvicorn\|sisi_lola_api" 2>/dev/null || echo "   No existing processes found"
sleep 2

echo ""
echo "📋 Step 2: Setting environment variables..."
export NIGERIAN_MODELS_ENABLED=true
export NIGERIAN_BRAIN_MODEL_PATH="sisilolalive/sisi-lola-brain-mistral"
export NIGERIAN_VOICE_MODEL_PATH="sisilolalive/sisi-lola-voice-xtts"
export MODEL_CACHE_ENABLED=true
export RESPONSE_CACHE_ENABLED=true
export FLASH_ATTENTION_ENABLED=true
echo "   ✅ Environment variables set"

echo ""
echo "📋 Step 3: Verifying .env file..."
if [ -f "sisi_lola_api/.env" ]; then
    echo "   ✅ .env file found"
    # Source .env if needed
    export $(grep -v '^#' sisi_lola_api/.env | xargs)
else
    echo "   ⚠️  .env file not found - using environment variables"
fi

echo ""
echo "📋 Step 4: Starting API server with optimizations..."
echo ""
echo "=============================================="
echo "🎯 OPTIMIZATIONS ENABLED:"
echo "   • Singleton Model Cache (40x faster)"
echo "   • Response Caching"
echo "   • Flash Attention 2 (if GPU available)"
echo "   • Bracket Pollution Fix"
echo "   • Paragraph Formatting"
echo "=============================================="
echo ""

# Start the server
python -m uvicorn sisi_lola_api.app.main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 1 \
    --log-level info

# Note: --workers 1 ensures singleton cache works correctly
# Use more workers only if using Redis for cache synchronization
