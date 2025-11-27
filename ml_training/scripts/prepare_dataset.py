#!/usr/bin/env python3
"""Dataset preparation script for ML training"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

def prepare_dataset(model, dataset_path, output, incremental=False, phase=None):
    """Prepare dataset for training"""
    print(f"Preparing dataset for {model}")
    print(f"Source: {dataset_path}")
    print(f"Output: {output}")
    
    dataset_path = Path(dataset_path)
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Count files
    files = list(dataset_path.rglob('*'))
    data_files = [f for f in files if f.is_file() and not f.name.startswith('.')]
    
    print(f"Found {len(data_files)} files")
    
    # Create manifest
    manifest = {
        "model": model,
        "dataset_path": str(dataset_path),
        "total_files": len(data_files),
        "prepared_at": datetime.now().isoformat(),
        "incremental": incremental,
        "phase": phase,
        "files": [str(f.relative_to(dataset_path)) for f in data_files[:100]]  # Sample
    }
    
    manifest_file = output_path / "manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Dataset prepared: {manifest_file}")
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True)
    parser.add_argument('--dataset-path', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--incremental', action='store_true')
    parser.add_argument('--phase', default=None)
    
    args = parser.parse_args()
    return prepare_dataset(args.model, args.dataset_path, args.output, 
                          args.incremental, args.phase)

if __name__ == '__main__':
    sys.exit(main())
