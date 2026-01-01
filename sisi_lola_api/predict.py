# Sisi Lola Replicate Predictor
from cog import BasePredictor, Input, Path
import os
import time
import base64
import httpx
import json
import requests
from typing import Optional
from PIL import Image
import io

# Hardcoded for the cloud env (secrets should be set in Replicate dashboard)
DNA_IMAGE_NAME = "sisi_lola_dna.png"

class Predictor(BasePredictor):
    def setup(self):
        """Load static assets"""
        print("🇳🇬 SISI LOLA: Setting up production environment...")
        self.dna_image_path = "sisi_lola_api/assets/dna/Sisi Lola Live Show Hostess.png"
        
        # Ensure we have the image
        if not os.path.exists(self.dna_image_path):
            print(f"⚠️ Warning: DNA image not found at {self.dna_image_path}")

    def normalize_text_for_ai(self, text: str) -> str:
        """Fix pronunciation for Authentic Naija Accent"""
        replacements = {
            "Lagos": "Lay-gos",
            "lagos": "Lay-gos",
            "Naija": "Nai-jah",
            "Sisi": "Cee-cee",
            "wahala": "wa-ha-la",
            "Una": "Oo-na",
            "una": "oo-na",
            "Abeg": "Ah-beg",
            "Oya": "Oh-ya"
        }
        for word, replacement in replacements.items():
            text = text.replace(word, replacement)
        return text

    def file_to_base64(self, file_path) -> str:
        with open(file_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/png;base64,{data}"

    def predict(
        self,
        script: str = Input(description="Script text for Sisi Lola to speak"),
        vibe_id: str = Input(description="Optional Vibe ID (e.g. VIBE010) for metadata", default="CUSTOM"),
        elevenlabs_key: str = Input(description="ElevenLabs API Key (Env Var Preferred)", default=None),
        replicate_key: str = Input(description="Replicate API Token (Env Var Preferred)", default=None)
    ) -> Path:
        """Run the Sisi Lola Pipeline"""
        
        print(f"🎬 Starting Production: {vibe_id}")
        
        # 1. Setup Keys (Support Input or Env Var)
        el_key = elevenlabs_key or os.environ.get("ELEVENLABS_API_KEY")
        rep_key = replicate_key or os.environ.get("REPLICATE_API_TOKEN")
        
        if not el_key or not rep_key:
            raise ValueError("❌ Missing API Keys! Please provide ELEVENLABS_API_KEY and REPLICATE_API_TOKEN.")

        # 2. Generate Voice (ElevenLabs)
        print("🎙️ Generating Voice (ElevenLabs)...")
        clean_text = self.normalize_text_for_ai(script)
        voice_id = "e3EHR2GS90EO276k1OCA" # Authentic V5
        
        voice_response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key": el_key, "Content-Type": "application/json"},
            json={
                "text": clean_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.35,  # High Expression
                    "similarity_boost": 0.80,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }
        )
        
        if voice_response.status_code != 200:
            raise RuntimeError(f"ElevenLabs Failed: {voice_response.text}")
            
        # Save temp audio
        audio_path = "/tmp/audio.wav"
        with open(audio_path, "wb") as f:
            f.write(voice_response.content)
            
        # 3. Generate Video (Replicate: Wav2Lip or OmniHuman)
        # Using Wav2Lip for reliability as per current strategy
        print("🎥 Generating Video (Wav2Lip)...")
        
        # Encode inputs
        with open(audio_path, "rb") as f:
            audio_b64 = "data:audio/wav;base64," + base64.b64encode(f.read()).decode('utf-8')
            
        image_b64 = self.file_to_base64(self.dna_image_path)
        
        # Call Replicate API manually (since we are creating a Replicate model that calls OTHER Replicate models)
        headers = {
            "Authorization": f"Token {rep_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "version": "8d65e3f4f4298520e079198b493c25adfc43c058ffec924f2aefc8010ed25eef", # Wav2Lip
            "input": {
                "face": image_b64,
                "audio": audio_b64,
                "pads": "0 10 0 0",
                "smooth": True
            }
        }
        
        response = requests.post("https://api.replicate.com/v1/predictions", headers=headers, json=payload)
        if response.status_code not in [200, 201]:
            raise RuntimeError(f"Replicate API Failed: {response.text}")
            
        prediction = response.json()
        prediction_id = prediction["id"]
        print(f"⏳ Waiting for video generation: {prediction_id}")
        
        # Poll
        video_url = None
        for _ in range(60): # Wait up to 5 mins
            time.sleep(5)
            status_resp = requests.get(
                f"https://api.replicate.com/v1/predictions/{prediction_id}", 
                headers=headers
            )
            data = status_resp.json()
            if data["status"] == "succeeded":
                video_url = data["output"]
                break
            elif data["status"] == "failed":
                raise RuntimeError(f"Video Generation Failed: {data['error']}")
                
        if not video_url:
            raise TimeoutError("Prediction timed out")
            
        # Download Video
        print(f"⬇️ Downloading: {video_url}")
        final_path = Path("/tmp/output.mp4")
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(final_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
        return final_path
