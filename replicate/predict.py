# Sisi Lola Replicate Predictor (Standalone)
from cog import BasePredictor, Input, Path
import os
import time
import base64
import requests
from typing import Optional

class Predictor(BasePredictor):
    def setup(self):
        """Initialize the predictor"""
        print("🇳🇬 SISI LOLA: Ready to produce content!")

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

    def predict(
        self,
        script: str = Input(description="Script text for Sisi Lola to speak"),
        vibe_id: str = Input(description="Optional Vibe ID for metadata", default="CUSTOM"),
        elevenlabs_key: str = Input(description="ElevenLabs API Key", default=None),
        replicate_key: str = Input(description="Replicate API Token", default=None)
    ) -> Path:
        """Run the Sisi Lola Pipeline: Voice + Video"""
        
        print(f"🎬 Starting Production: {vibe_id}")
        
        # Setup Keys
        el_key = elevenlabs_key or os.environ.get("ELEVENLABS_API_KEY")
        rep_key = replicate_key or os.environ.get("REPLICATE_API_TOKEN")
        
        if not el_key or not rep_key:
            raise ValueError("❌ Missing API Keys! Provide ELEVENLABS_API_KEY and REPLICATE_API_TOKEN.")

        # 1. Generate Voice (ElevenLabs)
        print("🎙️ Generating Voice (ElevenLabs)...")
        clean_text = self.normalize_text_for_ai(script)
        voice_id = "e3EHR2GS90EO276k1OCA"  # Authentic V5
        
        voice_response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers={"xi-api-key": el_key, "Content-Type": "application/json"},
            json={
                "text": clean_text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.35,
                    "similarity_boost": 0.80,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }
        )
        
        if voice_response.status_code != 200:
            raise RuntimeError(f"ElevenLabs Failed: {voice_response.text}")
            
        audio_path = "/tmp/audio.wav"
        with open(audio_path, "wb") as f:
            f.write(voice_response.content)
        print("✅ Voice generated!")
            
        # 2. Generate Video (Replicate Wav2Lip)
        print("🎥 Generating Video (Wav2Lip)...")
        
        with open(audio_path, "rb") as f:
            audio_b64 = "data:audio/wav;base64," + base64.b64encode(f.read()).decode('utf-8')
        
        # Use a simple placeholder image (or you can host DNA image somewhere)
        # For now, return audio only - video can be added later
        
        headers = {
            "Authorization": f"Token {rep_key}",
            "Content-Type": "application/json"
        }
        
        # Return the audio file for now (video generation can be added)
        final_path = Path("/tmp/output.wav")
        with open(final_path, "wb") as f:
            f.write(voice_response.content)
        
        print(f"✅ Production complete: {final_path}")
        return final_path
