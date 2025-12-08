import os
import sys
import csv
import requests
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

# Load environment variables
load_dotenv(PROJECT_ROOT / "sisi_lola_api" / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MANIFEST_FILE = PROJECT_ROOT / "MASTER_ASSET_MANIFEST.csv"

def generate_image_assets():
    print("🎨 Starting Image Asset Generation (DALL-E 3)...")
    
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not found in .env")
        return

    client = OpenAI(api_key=OPENAI_API_KEY, timeout=60.0)

    # Read manifest
    assets_to_generate = []
    with open(MANIFEST_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Category'] in ['01_AVATAR_DNA', '02_ENVIRONMENTS_VR'] and row['Status'] == 'Pending Generation':
                assets_to_generate.append(row)
    
    print(f"Found {len(assets_to_generate)} pending image assets.")
    
    # Limit to 5 for testing/safety
    count = 0
    limit = 5
    
    for asset in assets_to_generate:
        if count >= limit:
            print(f"🛑 Reached limit of {limit} generations for this run.")
            break
            
        print(f"\nProcessing: {asset['Filename']}")
        
        output_path = PROJECT_ROOT / asset['Category'] / asset['Subcategory'] / asset['Filename']
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if output_path.exists():
             print(f"⏩ Skipping (File exists): {output_path}")
             continue

        try:
            prompt = asset['Prompt']
            print(f"   Prompt: {prompt[:100]}...")
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            
            # Download image
            img_data = requests.get(image_url).content
            with open(output_path, 'wb') as f:
                f.write(img_data)
                
            print(f"✅ Generated: {output_path}")
            count += 1
            
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n🏁 Image Generation Complete.")

if __name__ == "__main__":
    generate_image_assets()
