#!/usr/bin/env python3
"""Generate markdown report from validation results"""

import json
import argparse
from pathlib import Path
from datetime import datetime

def generate_report(input_file, output_file):
    """Generate markdown report"""
    with open(input_file) as f:
        data = json.load(f)
    
    report = []
    report.append("# ML Model Validation Report\n")
    report.append(f"**Generated:** {data['validated_at']}\n")
    report.append(f"**Models Validated:** {len(data['models'])}\n")
    report.append("\n---\n")
    
    for model_name, model_data in data['models'].items():
        report.append(f"\n## {model_name}\n")
        
        status = model_data.get('status', 'unknown')
        if status == 'passed':
            report.append("**Status:** ✅ PASSED\n")
            
            metrics = model_data.get('metrics', {})
            report.append("\n### Metrics\n")
            report.append(f"- **Accuracy:** {metrics.get('accuracy', 0):.2%}\n")
            report.append(f"- **Loss:** {metrics.get('loss', 0):.4f}\n")
            report.append(f"- **F1 Score:** {metrics.get('f1_score', 0):.2%}\n")
            
            if 'baseline_comparison' in model_data:
                comp = model_data['baseline_comparison']
                delta = comp.get('accuracy_delta', 0)
                symbol = "📈" if delta > 0 else "📉"
                report.append(f"\n### Baseline Comparison\n")
                report.append(f"{symbol} Accuracy change: {delta:+.2%}\n")
        
        elif status == 'no_validation':
            report.append("**Status:** ⚠️ No validation results\n")
        elif status == 'no_checkpoint':
            report.append("**Status:** ❌ No checkpoint found\n")
        else:
            report.append(f"**Status:** ❓ {status}\n")
        
        report.append("\n---\n")
    
    # Write report
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(''.join(report))
    
    print(f"✓ Report generated: {output_path}")
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    
    args = parser.parse_args()
    return generate_report(args.input, args.output)

if __name__ == '__main__':
    sys.exit(main())
