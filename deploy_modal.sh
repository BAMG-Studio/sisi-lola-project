#!/bin/bash
# =============================================================================
# SISI LOLA - MODAL DEPLOY SCRIPT
# =============================================================================
# Run this in WSL: bash deploy_modal.sh
# =============================================================================

echo "🚀 SISI LOLA MODAL DEPLOYMENT"
echo "=============================================="

cd /mnt/c/Users/POK28/Dropbox/Sisi_Lola

# Activate virtual environment
source sisi_lola_api/venv/bin/activate

# Set Python path
export PYTHONPATH=/mnt/c/Users/POK28/Dropbox/Sisi_Lola

# Check modal is installed
if ! command -v modal &> /dev/null; then
    echo "❌ Modal not found. Installing..."
    pip install modal
fi

echo "📦 Deploying to Modal..."
modal deploy sisi_lola_api/app/services/modal_stub.py

echo ""
echo "=============================================="
echo "✅ Deployment complete!"
echo "=============================================="
