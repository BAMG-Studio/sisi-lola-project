#!/bin/bash
# Sisi Lola Nigerian Training - Unix/Linux/Mac Quick Start

set -e

echo "============================================================"
echo "SISI LOLA NIGERIAN TRAINING PIPELINE"
echo "============================================================"

# Activate virtual environment
if [ -d ".venv_sisi" ]; then
    source .venv_sisi/bin/activate
elif [ -d "venv_new" ]; then
    source venv_new/bin/activate
else
    echo "Creating new virtual environment..."
    python3 -m venv .venv_sisi
    source .venv_sisi/bin/activate
fi

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r ml_training/requirements_nigerian.txt

# Load environment variables
if [ -f "sisi_lola_api/.env" ]; then
    echo "Loading environment variables..."
    export $(cat sisi_lola_api/.env | grep -v '^#' | xargs)
fi

# Run setup
echo ""
echo "Running setup..."
python ml_training/scripts/setup_nigerian_models.py

# Run training
echo ""
echo "Starting training..."
python ml_training/scripts/unified_training_orchestrator.py --mode full

echo ""
echo "============================================================"
echo "TRAINING COMPLETE!"
echo "============================================================"
echo ""
echo "Check outputs:"
echo "  - Brain: ml_training/checkpoints/natlas_lora/"
echo "  - Voice: ml_training/checkpoints/xtts_sisi_lola/"
echo "  - Config: ml_training/outputs/production_config.json"
echo ""
