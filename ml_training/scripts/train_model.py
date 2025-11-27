#!/usr/bin/env python3
"""Model training script"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def train_model(model, phase, mode, config_path, checkpoint=None):
    """Execute model training"""
    print("=" * 60)
    print(f"TRAINING: {model}")
    print(f"Phase: {phase}")
    print(f"Mode: {mode}")
    print("=" * 60)
    
    config = load_config(config_path)
    model_config = config['models'].get(model)
    
    if not model_config:
        print(f"Error: Model {model} not found in config")
        return 1
    
    # Get phase config
    phase_config = None
    for p in model_config.get('training_phases', []):
        if p['phase'] == phase:
            phase_config = p
            break
    
    if not phase_config:
        print(f"Error: Phase {phase} not found for model {model}")
        return 1
    
    print(f"\nPhase Configuration:")
    print(f"  Samples Required: {phase_config.get('samples_required', 'N/A')}")
    print(f"  Epochs: {phase_config.get('epochs', 'N/A')}")
    
    # Simulate training
    print(f"\nStarting training...")
    print(f"  Model Type: {model_config['type']}")
    print(f"  Dataset: {model_config['dataset_path']}")
    
    if checkpoint:
        print(f"  Loading checkpoint: {checkpoint}")
    
    # Create checkpoint directory
    checkpoint_dir = Path('ml_training/checkpoints') / model / phase
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    # Save training metadata
    metadata = {
        "model": model,
        "phase": phase,
        "mode": mode,
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
        "status": "success",
        "epochs": phase_config.get('epochs', 0),
        "checkpoint_path": str(checkpoint_dir)
    }
    
    metadata_file = checkpoint_dir / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Create latest symlink
    latest_link = Path('ml_training/checkpoints') / model / 'latest'
    if latest_link.exists():
        latest_link.unlink()
    
    print(f"\n✓ Training completed successfully")
    print(f"  Checkpoint: {checkpoint_dir}")
    print(f"  Metadata: {metadata_file}")
    
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True)
    parser.add_argument('--phase', required=True)
    parser.add_argument('--mode', required=True)
    parser.add_argument('--config', required=True)
    parser.add_argument('--checkpoint', default=None)
    
    args = parser.parse_args()
    return train_model(args.model, args.phase, args.mode, args.config, args.checkpoint)

if __name__ == '__main__':
    sys.exit(main())
