#!/usr/bin/env python3
"""Download and save completed transcripts from RecCloud."""

import requests
import json
from pathlib import Path
from datetime import datetime

API_KEY = 'wxbgr07ikdtvgnws4'
API_URL = 'https://techhk.aoscdn.com/api/tasks/audio/recognition'

# Known successful task IDs
tasks = {
    'authentic_video_001': '8ef57367-6d0a-4179-afac-eef2b1b2dc73',
}

output_dir = Path('/mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/datasets/transcriptions')
output_dir.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("DOWNLOADING TRANSCRIPTS FROM RECCLOUD")
print("=" * 60)

for name, task_id in tasks.items():
    print(f"\n📥 Fetching {name}...")
    
    try:
        response = requests.get(
            f'{API_URL}/{task_id}',
            headers={'X-API-KEY': API_KEY}
        )
        response.raise_for_status()
        data = response.json()
        
        task_data = data.get('data', {})
        state = task_data.get('state', -1)
        
        if state == 1:  # Complete
            transcript = task_data.get('result', '')
            duration = task_data.get('duration', 0)
            
            # Save JSON
            json_path = output_dir / f'{name}_transcript.json'
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Save text
            txt_path = output_dir / f'{name}_transcript.txt'
            with open(txt_path, 'w') as f:
                f.write(transcript)
            
            print(f"✅ Saved: {name}")
            print(f"   Duration: {duration} seconds")
            print(f"   Words: {len(transcript.split())}")
            print(f"   JSON: {json_path}")
            print(f"   Text: {txt_path}")
        else:
            print(f"❌ Not complete. State: {state}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("DONE")
print("=" * 60)
