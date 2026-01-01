#!/bin/bash
set -e  # Exit instantly if any command fails

echo "========================================================"
echo "🔧 SISI LOLA ENVIRONMENT RESET & RUN TOOL"
echo "========================================================"
echo ""

# Ensure we are in the project root
cd /mnt/c/Users/POK28/Dropbox/Sisi_Lola

echo "📍 Current User: $(whoami)"
echo "📍 Current Dir: $(pwd)"

# 1. Bypass old environment (Use a dedicated Fedora venv)
# We don't touch 'venv' because it might be locked/active
VENV_DIR="sisi_lola_api/venv_fedora"

# 2. Create new environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo "✨ Creating FRESH virtual environment at $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

# 3. Activate
echo "🔌 Activating environment..."
source "$VENV_DIR/bin/activate"

# 4. Install dependencies
echo ""
echo "📦 Installing required packages (this may take a minute)..."
python -m pip install --upgrade pip
python -m pip install httpx python-dotenv Pillow soundfile librosa scipy numpy

echo ""
echo "✅ Environment Ready!"

# 5. Run the Supreme Producer
echo ""
echo "========================================================"
echo "🎬 STARTING PRODUCTION: VIBE010 (New Africa Roll Call)"
echo "========================================================"
echo ""

python -m sisi_lola_api.scripts.authentic_producer_v5 --vibe VIBE010
