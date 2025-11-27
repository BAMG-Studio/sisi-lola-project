#!/usr/bin/env python3
"""Update production config with new model versions"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

def update_production_config(models_dir, config_file):
    """Update .env with new model versions"""
    print("=" * 60)
    print("UPDATING PRODUCTION CONFIG")
    print("=" * 60)
    
    models_path = Path(models_dir)
    config_path = Path(config_file)
    
    updates = []
    
    # Read current config
    if config_path.exists():
        with open(config_path) as f:
            config_lines = f.readlines()
    else:
        config_lines = []
    
    # Find deployed models
    for model_dir in models_path.iterdir():
        if not model_dir.is_dir():
            continue
        
        model_name = model_dir.name
        
        # Check for deployment info
        latest_checkpoint = model_dir / "latest"
        if not latest_checkpoint.exists():
            phase_dirs = [d for d in model_dir.iterdir() if d.is_dir()]
            if phase_dirs:
                latest_checkpoint = phase_dirs[0]
        
        if latest_checkpoint.exists():
            metadata_file = latest_checkpoint / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                
                # Add/update model version in config
                model_key = f"{model_name.upper()}_MODEL_VERSION"
                model_value = metadata.get('completed_at', datetime.now().isoformat())
                
                updates.append(f"{model_key}={model_value}")
                print(f"  {model_key}={model_value}")
    
    if updates:
        # Append updates to config
        with open(config_path, 'a') as f:
            f.write(f"\n# Model versions updated: {datetime.now().isoformat()}\n")
            for update in updates:
                f.write(f"{update}\n")
        
        print(f"\n✓ Config updated: {config_path}")
        print(f"  Updates: {len(updates)}")
    else:
        print("\n! No updates needed")
    
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--models', required=True)
    parser.add_argument('--config', required=True)
    
    args = parser.parse_args()
    return update_production_config(args.models, args.config)

if __name__ == '__main__':
    sys.exit(main())
