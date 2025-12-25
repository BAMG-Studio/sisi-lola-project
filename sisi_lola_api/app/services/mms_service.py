"""
SISI LOLA NATIVE VOICE SERVICE (MMS)
Provides high-quality, native Yoruba/Igbo/Hausa speech via Meta's MMS.
Focuses on authentic pronunciation which ElevenLabs often lacks for dialects.
"""

import os
import torch
import base64
import tempfile
import scipy.io.wavfile
from typing import Optional, Tuple
from enum import Enum

try:
    from transformers import VitsModel, AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class MMSLanguage(str, Enum):
    YORUBA = "yo"
    IGBO = "ibb" # MMS uses specific codes
    HAUSA = "hau"
    ENGLISH = "eng"
    PIDGIN = "pcm"

class MMSService:
    def __init__(self, device: str = "cpu"):
        self.device = "cuda" if torch.cuda.is_available() and device == "auto" else "cpu"
        self.models = {}
        self.tokenizers = {}
        print(f"🎙️ MMS Native Voice Service initialized on {self.device}")

    def _load_model(self, lang: str):
        if lang not in self.models and TRANSFORMERS_AVAILABLE:
            model_id = f"facebook/mms-tts-{lang}"
            print(f"📥 Loading MMS model for {lang} (this may take a few minutes the first time)...")
            try:
                # Set a local cache dir to avoid permission issues
                cache_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "mms_cache")
                os.makedirs(cache_dir, exist_ok=True)
                
                self.tokenizers[lang] = AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir)
                self.models[lang] = VitsModel.from_pretrained(model_id, cache_dir=cache_dir).to(self.device)
                print(f"✅ MMS model {lang} loaded successfully.")
            except Exception as e:
                print(f"❌ Failed to load MMS model {lang}: {e}")
                return False
        return lang in self.models

    def preload_common_models(self):
        """Preloads major African native languages for instant response"""
        print("🚚 Preloading Pan-African Voice Models (MMS)...")
        for lang in ["yor", "ibo", "hau", "pcm"]:
            try:
                self._load_model(lang)
            except Exception as e:
                print(f"⚠️ Could not preload {lang}: {e}")

    async def generate_speech(self, text: str, lang_code: str = "yo") -> Tuple[Optional[str], Optional[str]]:
        """
        Generates native speech audio.
        Returns (audio_base64, None)
        """
        if not TRANSFORMERS_AVAILABLE:
            print("⚠️ Transformers not available for MMS")
            return None, None

        # Map internal codes to MMS codes
        mms_map = {
            "yo": "yor",
            "yoruba": "yor",
            "ig": "ibo",
            "ha": "hau",
            "en": "eng",
            "pcm": "pcm",
            "pidgin": "pcm"
        }
        lang = mms_map.get(lang_code.lower(), "yor")

        if not self._load_model(lang):
            return None, None

        try:
            inputs = self.tokenizers[lang](text, return_tensors="pt").to(self.device)
            with torch.no_grad():
                output = self.models[lang](**inputs).waveform
            
            # Convert to bytes
            audio_data = output.cpu().numpy().squeeze()
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                temp_path = f.name
                # MMS output is usually 16kHz
                scipy.io.wavfile.write(temp_path, 16000, audio_data)
            
            with open(temp_path, "rb") as f:
                audio_bytes = f.read()
            
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            os.remove(temp_path)
            
            return audio_base64, None
            
        except Exception as e:
            print(f"❌ MMS Generation error: {e}")
            return None, None

# Global instance
mms_service = MMSService()
