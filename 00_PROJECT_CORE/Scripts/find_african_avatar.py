#!/usr/bin/env python3
"""Find African or diverse avatars in HeyGen"""
import os
import requests
from pathlib import Path

# Load .env
env_path = Path(__file__).parent.parent.parent / 'sisi_lola_api' / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

api_key = os.getenv('HEYGEN_API_KEY')

response = requests.get(
    'https://api.heygen.com/v2/avatars',
    headers={'X-Api-Key': api_key}
)

if response.status_code == 200:
    data = response.json()
    avatars = data.get('data', {}).get('avatars', [])
    
    # Search for diverse/African names
    keywords = ['african', 'black', 'dark', 'diverse', 'ethnic', 'amara', 'zuri', 'ada', 'nia', 'kenya', 'ghana']
    
    print(f"Searching {len(avatars)} avatars for African/diverse options...\n")
    
    matches = []
    for avatar in avatars:
        name = avatar.get('avatar_name', '').lower()
        avatar_id = avatar.get('avatar_id', '').lower()
        
        if any(kw in name or kw in avatar_id for kw in keywords):
            matches.append(avatar)
    
    if matches:
        print(f"[OK] Found {len(matches)} potential matches:\n")
        for i, avatar in enumerate(matches[:20]):
            print(f"{i+1}. {avatar.get('avatar_name')}")
            print(f"   ID: {avatar.get('avatar_id')}")
            print(f"   Preview: {avatar.get('preview_image_url', 'N/A')[:80]}")
            print()
    else:
        print("[INFO] No specific African avatars found by name.")
        print("[INFO] Using first available female avatar as fallback:")
        
        # Find first female avatar
        for avatar in avatars:
            if avatar.get('gender') == 'female':
                print(f"\n{avatar.get('avatar_name')}")
                print(f"ID: {avatar.get('avatar_id')}")
                print(f"Preview: {avatar.get('preview_image_url')}")
                break
