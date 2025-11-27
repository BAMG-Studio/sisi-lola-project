#!/usr/bin/env python3
"""Filter manifest by category and export prompts for batch generation"""

import csv
import sys

MANIFEST = "MASTER_ASSET_MANIFEST.csv"

def filter_by_category(category):
    """Extract all prompts for a specific category"""
    prompts = []
    
    with open(MANIFEST, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Category'] == category and row['Status'] == 'Pending Generation':
                prompts.append({
                    'id': row['ID'],
                    'filename': row['Filename'],
                    'prompt': row['Prompt']
                })
    
    # Save to text file
    output_file = f"PROMPTS_{category}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for p in prompts:
            f.write(f"// {p['id']} - {p['filename']}\n")
            f.write(f"{p['prompt']}\n\n")
            f.write("-" * 80 + "\n\n")
    
    print(f"Exported {len(prompts)} prompts to {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python filter_manifest.py <CATEGORY>")
        print("\nAvailable categories:")
        print("  01_AVATAR_DNA")
        print("  02_ENVIRONMENTS_VR")
        print("  03_MEDIA_ASSETS")
        print("  04_AUDIO_CORE")
        print("  05_BRANDING_ARTIFACTS")
    else:
        filter_by_category(sys.argv[1])
