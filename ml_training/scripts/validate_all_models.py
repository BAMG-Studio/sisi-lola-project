#!/usr/bin/env python3
"""Validate all trained models"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

def validate_all_models(checkpoints_dir, report_file):
    """Validate all models in checkpoints directory"""
    checkpoints_path = Path(checkpoints_dir)
    
    results = {
        "validated_at": datetime.now().isoformat(),
        "models": {}
    }
    
    # Find all model checkpoints
    for model_dir in checkpoints_path.iterdir():
        if not model_dir.is_dir():
            continue
        
        model_name = model_dir.name
        print(f"Validating {model_name}...")
        
        # Find latest checkpoint
        latest_checkpoint = model_dir / "latest"
        if not latest_checkpoint.exists():
            # Try to find any phase checkpoint
            phase_dirs = [d for d in model_dir.iterdir() if d.is_dir()]
            if phase_dirs:
                latest_checkpoint = phase_dirs[0]
        
        if latest_checkpoint.exists():
            validation_file = latest_checkpoint / "validation_results.json"
            if validation_file.exists():
                with open(validation_file) as f:
                    validation_data = json.load(f)
                    results["models"][model_name] = validation_data
                    print(f"  ✓ Loaded validation results")
            else:
                results["models"][model_name] = {
                    "status": "no_validation",
                    "checkpoint": str(latest_checkpoint)
                }
                print(f"  ! No validation results found")
        else:
            results["models"][model_name] = {
                "status": "no_checkpoint"
            }
            print(f"  ! No checkpoint found")
    
    # Save report
    report_path = Path(report_file)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Validation report saved: {report_path}")
    print(f"  Models validated: {len(results['models'])}")
    
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoints', required=True)
    parser.add_argument('--report', required=True)
    
    args = parser.parse_args()
    return validate_all_models(args.checkpoints, args.report)

if __name__ == '__main__':
    sys.exit(main())
