#!/usr/bin/env python3
"""Detect new training data since last training"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

def detect_new_data(model, dataset_path, last_training_file):
    """Detect new data files since last training"""
    dataset_path = Path(dataset_path)
    
    # Get last training timestamp
    last_training = None
    if Path(last_training_file).exists():
        with open(last_training_file) as f:
            metadata = json.load(f)
            last_training = datetime.fromisoformat(metadata.get('completed_at', metadata.get('last_training', '')))
    
    if not last_training:
        print("new_data_found: No previous training found")
        return 0
    
    # Count new files
    new_files = []
    for file in dataset_path.rglob('*'):
        if file.is_file() and not file.name.startswith('.'):
            file_mtime = datetime.fromtimestamp(file.stat().st_mtime)
            if file_mtime > last_training:
                new_files.append(str(file))
    
    print(f"new_data_found: {len(new_files)} new files since {last_training.isoformat()}")
    
    if new_files:
        print(f"Sample files: {new_files[:5]}")
    
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True)
    parser.add_argument('--dataset-path', required=True)
    parser.add_argument('--last-training', required=True)
    
    args = parser.parse_args()
    return detect_new_data(args.model, args.dataset_path, args.last_training)

if __name__ == '__main__':
    sys.exit(main())
