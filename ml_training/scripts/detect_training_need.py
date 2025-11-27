#!/usr/bin/env python3
"""
Intelligent Training Need Detection
Analyzes triggers and determines if retraining is needed
"""

import os
import sys
import json
import yaml
import argparse
from pathlib import Path
from datetime import datetime, timedelta

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def check_schedule_trigger(model_config):
    """Check if scheduled retraining is due"""
    for trigger in model_config.get('retrain_triggers', []):
        if trigger['type'] == 'schedule':
            # In real implementation, check cron schedule
            return True
    return False

def check_data_threshold(model_config, dataset_path):
    """Check if new data threshold is met"""
    for trigger in model_config.get('retrain_triggers', []):
        if trigger['type'] == 'data_threshold':
            threshold = trigger.get('new_samples', 100)
            
            # Count new samples since last training
            metadata_file = Path('ml_training/checkpoints') / model_config['name'] / 'metadata.json'
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    last_training = datetime.fromisoformat(metadata['last_training'])
                    
                    # Count files modified after last training
                    dataset = Path(dataset_path)
                    new_files = sum(1 for f in dataset.rglob('*') 
                                  if f.is_file() and 
                                  datetime.fromtimestamp(f.stat().st_mtime) > last_training)
                    
                    if new_files >= threshold:
                        return True, new_files
            else:
                # No previous training, trigger if any data exists
                return True, 0
    
    return False, 0

def check_performance_drop(model_config):
    """Check if model performance has dropped"""
    for trigger in model_config.get('retrain_triggers', []):
        if trigger['type'] == 'performance_drop':
            # In real implementation, check metrics from monitoring
            # For now, return False
            return False
    return False

def detect_changed_models(changed_files, config):
    """Detect which models need retraining based on changed files"""
    models_to_train = []
    
    for model_name, model_config in config['models'].items():
        dataset_path = model_config['dataset_path']
        
        # Check if any changed file is in this model's dataset
        for file in changed_files:
            if dataset_path in file:
                models_to_train.append(model_name)
                break
    
    return models_to_train

def main():
    parser = argparse.ArgumentParser(description='Detect ML training requirements')
    parser.add_argument('--config', required=True, help='Training config file')
    parser.add_argument('--event-type', required=True, help='GitHub event type')
    parser.add_argument('--changed-files', default='', help='Changed files (comma-separated)')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    should_train = False
    models_to_train = []
    training_mode = 'partial'
    
    # Analyze based on event type
    if args.event_type == 'schedule':
        # Scheduled retraining
        should_train = True
        models_to_train = list(config['models'].keys())
        training_mode = 'partial'
        print("Trigger: Scheduled retraining", file=sys.stderr)
    
    elif args.event_type == 'push':
        # Data change trigger
        changed_files = args.changed_files.split(',') if args.changed_files else []
        models_to_train = detect_changed_models(changed_files, config)
        
        if models_to_train:
            should_train = True
            training_mode = 'partial'
            print(f"Trigger: New data for models: {', '.join(models_to_train)}", file=sys.stderr)
    
    elif args.event_type == 'workflow_dispatch':
        # Manual trigger - handled by workflow inputs
        should_train = True
    
    # Check data thresholds for each model
    for model_name, model_config in config['models'].items():
        needs_training, new_samples = check_data_threshold(
            model_config, 
            model_config['dataset_path']
        )
        
        if needs_training and model_name not in models_to_train:
            models_to_train.append(model_name)
            should_train = True
            print(f"Trigger: Data threshold met for {model_name} ({new_samples} new samples)", 
                  file=sys.stderr)
    
    # Output for GitHub Actions
    print(f"::set-output name=should_train::{str(should_train).lower()}")
    print(f"::set-output name=models::{','.join(models_to_train) if models_to_train else 'all'}")
    print(f"::set-output name=mode::{training_mode}")
    
    # Summary
    print("\n=== Training Detection Summary ===", file=sys.stderr)
    print(f"Should Train: {should_train}", file=sys.stderr)
    print(f"Models: {models_to_train or 'all'}", file=sys.stderr)
    print(f"Mode: {training_mode}", file=sys.stderr)

if __name__ == '__main__':
    main()
