#!/usr/bin/env python3
"""Test HeyGen API and list available avatars"""
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

print("Testing HeyGen API...")
print(f"API Key: {api_key[:20]}...")

# List available avatars
response = requests.get(
    'https://api.heygen.com/v2/avatars',
    headers={'X-Api-Key': api_key}
)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200:
    data = response.json()
    avatars = data.get('data', {}).get('avatars', [])
    print(f"\n[OK] Found {len(avatars)} avatars")
    
    for i, avatar in enumerate(avatars[:5]):
        print(f"\n{i+1}. {avatar.get('avatar_name', 'Unknown')}")
        print(f"   ID: {avatar.get('avatar_id')}")
        print(f"   Type: {avatar.get('avatar_type')}")
