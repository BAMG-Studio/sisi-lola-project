import requests
import base64
import os
import json

API_URL = "http://localhost:8000/audio/speak"
OUTPUT_DIR = "assets/generated/audio"

def test_audio_generation():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    payload = {
        "text": "Hello darlings! This is Sisi Lola, your favorite virtual host, coming to you live from the heart of Lagos.",
        # "voice_id": "21m00Tcm4TlvDq8ikWAM" # Optional, uses default if omitted
    }

    print(f"Sending request to {API_URL}...")
    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            if "audio_data" in data:
                audio_bytes = base64.b64decode(data["audio_data"])
                output_path = os.path.join(OUTPUT_DIR, "test_sisi_lola_intro.mp3")
                
                with open(output_path, "wb") as f:
                    f.write(audio_bytes)
                
                print(f"SUCCESS: Audio saved to {output_path}")
            else:
                print("ERROR: No 'audio_data' in response")
                print(data)
        else:
            print(f"ERROR: API returned status code {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")

if __name__ == "__main__":
    test_audio_generation()
