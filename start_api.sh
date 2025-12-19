#!/bin/bash
# ============================================================================
# SISI LOLA API - START SCRIPT
# Launches the unified multimodal API with web demo
# ============================================================================

set -e

echo "🇳🇬 =============================================="
echo "   SISI LOLA - Nigerian AI Virtual Host"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -f "sisi_lola_api/app/main.py" ]; then
    echo "❌ Error: Run this from the Sisi_Lola project root"
    echo "   Expected: /path/to/Sisi_Lola/"
    exit 1
fi

# Activate virtual environment if exists
if [ -d "venv_wsl" ]; then
    echo "📦 Activating virtual environment..."
    source venv_wsl/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/sisi_lola_api"

# Check for required packages
echo "📦 Checking dependencies..."
python -c "import fastapi" 2>/dev/null || pip install fastapi uvicorn python-dotenv

# Print startup info
echo ""
echo "🚀 Starting Sisi Lola API..."
echo ""
echo "📍 Endpoints:"
echo "   • Web Demo: http://localhost:8000/demo"
echo "   • API Docs: http://localhost:8000/docs"
echo "   • Health:   http://localhost:8000/unified/health"
echo ""
echo "🎙️ Features:"
echo "   • 🧠 Brain: Mistral-7B + LoRA (Nigerian languages)"
echo "   • 💃 Personality: Charismatic Nigerian host"
echo "   • 🎤 Voice: XTTS-v2 voice synthesis"
echo "   • 📱 Instagram: Webhook integration"
echo ""
echo "=============================================="
echo ""

# Start the server
cd sisi_lola_api
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
