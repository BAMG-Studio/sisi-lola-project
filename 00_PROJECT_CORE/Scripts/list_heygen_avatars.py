"""List Available HeyGen Avatars"""
import os
import requests
from dotenv import load_dotenv

load_dotenv("../../sisi_lola_api/.env")

headers = {"X-Api-Key": os.getenv("HEYGEN_API_KEY")}

response = requests.get("https://api.heygen.com/v2/avatars", headers=headers)

if response.status_code == 200:
    avatars = response.json()['data']['avatars']
    print(f"\nFound {len(avatars)} avatars:\n")
    for avatar in avatars[:20]:
        print(f"ID: {avatar['avatar_id']}")
        print(f"Name: {avatar['avatar_name']}")
        print(f"Gender: {avatar.get('gender', 'N/A')}")
        print("-" * 50)
else:
    print(f"Error: {response.text}")
