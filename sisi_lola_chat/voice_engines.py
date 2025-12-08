"""
SISI LOLA VOICE ENGINES
=======================
Multiple voice synthesis options:
1. ElevenLabs (Premium - Female YettySlay style)
2. Coqui XTTS (Free - Male Nigerian voice)
3. Facebook MMS-TTS Yoruba (Free - Basic)
"""

import os
import sys
import requests
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Optional, Literal
from abc import ABC, abstractmethod

# Fix imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "04_AUDIO_CORE" / "voice_training"))

from dotenv import load_dotenv
load_dotenv(project_root / "sisi_lola_api" / ".env")
load_dotenv(project_root / "00_PROJECT_CORE" / ".env")


class VoiceEngine(ABC):
    """Abstract base class for voice engines"""
    
    @abstractmethod
    def generate_speech(self, text: str, output_path: str) -> Optional[str]:
        """Generate speech from text"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Engine name"""
        pass
    
    @property
    @abstractmethod
    def voice_type(self) -> str:
        """Voice type description"""
        pass


class ElevenLabsVoice(VoiceEngine):
    """
    ElevenLabs Voice Engine - Premium quality
    Female Nigerian voice (YettySlay-inspired)
    
    Features:
    - Ultra-realistic voice synthesis
    - Voice cloning capability
    - Nigerian accent support
    """
    
    # Pre-configured voices that work well for Nigerian English
    VOICE_OPTIONS = {
        "rachel": "21m00Tcm4TlvDq8ikWAM",      # Natural female
        "bella": "EXAVITQu4vr4xnSDxMaL",        # Warm female
        "elli": "MF3mGyEYCl7XYWbV9V6O",         # Young female
        "charlotte": "XB0fDUnXU5powFXDhCwa",    # Elegant female
        "sarah": "EXAVITQu4vr4xnSDxMaL",        # Conversational
    }
    
    def __init__(self, api_key: Optional[str] = None, voice_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ElevenLabs API key not found. Set ELEVENLABS_API_KEY env var.")
        
        # Use provided voice_id or default to a warm female voice
        self.voice_id = voice_id or self.VOICE_OPTIONS.get("bella", "EXAVITQu4vr4xnSDxMaL")
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Voice settings for Nigerian style
        self.voice_settings = {
            "stability": 0.5,           # Allow for expressiveness
            "similarity_boost": 0.75,   # Balance natural variation
            "style": 0.5,               # Add some style/emotion
            "use_speaker_boost": True
        }
        
        # Model selection - use multilingual for better Nigerian accent
        self.model_id = "eleven_multilingual_v2"  # Best for Nigerian English/Pidgin
        
    @property
    def name(self) -> str:
        return "ElevenLabs"
    
    @property
    def voice_type(self) -> str:
        return "Female (YettySlay-style)"
    
    def list_voices(self) -> list:
        """List available voices from ElevenLabs"""
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers={"xi-api-key": self.api_key}
            )
            if response.status_code == 200:
                return response.json().get("voices", [])
            return []
        except Exception as e:
            print(f"[!] Failed to list voices: {e}")
            return []
    
    def clone_voice(self, name: str, audio_files: list, description: str = "") -> Optional[str]:
        """
        Clone a voice from audio samples
        Returns the new voice_id
        """
        try:
            files = []
            for audio_path in audio_files:
                files.append(("files", open(audio_path, "rb")))
            
            response = requests.post(
                f"{self.base_url}/voices/add",
                headers={"xi-api-key": self.api_key},
                data={
                    "name": name,
                    "description": description or f"Cloned voice: {name}"
                },
                files=files
            )
            
            # Close file handles
            for _, f in files:
                f.close()
            
            if response.status_code == 200:
                voice_data = response.json()
                return voice_data.get("voice_id")
            else:
                print(f"[!] Voice cloning failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"[!] Voice cloning error: {e}")
            return None
    
    def generate_speech(self, text: str, output_path: str) -> Optional[str]:
        """Generate speech using ElevenLabs API"""
        try:
            # Clean text for TTS
            clean_text = self._clean_text(text)
            
            response = requests.post(
                f"{self.base_url}/text-to-speech/{self.voice_id}",
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "text": clean_text,
                    "model_id": self.model_id,
                    "voice_settings": self.voice_settings
                }
            )
            
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return output_path
            else:
                print(f"[!] ElevenLabs error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"[!] ElevenLabs generation failed: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text for better TTS output"""
        # Remove emojis and special characters that might confuse TTS
        import re
        # Remove emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        text = emoji_pattern.sub('', text)
        
        # Convert common Pidgin contractions for better pronunciation
        replacements = {
            "dey": "day",  # Helps with pronunciation
            "wetin": "wet-in",
            "omo": "oh-mo",
            "wahala": "wa-ha-la",
            "abeg": "ah-beg",
        }
        
        for old, new in replacements.items():
            text = re.sub(rf'\b{old}\b', new, text, flags=re.IGNORECASE)
        
        return text.strip()


class CoquiXTTSVoice(VoiceEngine):
    """
    Coqui XTTS Voice Engine - Free, open-source
    Male Nigerian voice with voice cloning
    
    Features:
    - Free and open-source
    - Voice cloning from samples
    - Multilingual support
    """
    
    def __init__(self, speaker_wav: Optional[str] = None):
        self.speaker_wav = speaker_wav
        self.model = None
        self.sample_rate = 24000
        
        # Try to load the model
        self._load_model()
    
    def _load_model(self):
        """Load Coqui XTTS model"""
        try:
            from TTS.api import TTS
            
            # Use XTTS v2 for best quality
            self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            print("[OK] Coqui XTTS v2 loaded")
            
        except ImportError:
            print("[!] Coqui TTS not installed. Run: pip install TTS")
            self.model = None
        except Exception as e:
            print(f"[!] Failed to load Coqui XTTS: {e}")
            self.model = None
    
    @property
    def name(self) -> str:
        return "Coqui XTTS"
    
    @property
    def voice_type(self) -> str:
        return "Male (Nigerian cloned)"
    
    def generate_speech(self, text: str, output_path: str) -> Optional[str]:
        """Generate speech using Coqui XTTS"""
        if not self.model:
            print("[!] Coqui XTTS model not loaded")
            return None
        
        try:
            # Clean text
            clean_text = self._clean_text(text)
            
            if self.speaker_wav and Path(self.speaker_wav).exists():
                # Use voice cloning with reference audio
                self.model.tts_to_file(
                    text=clean_text,
                    file_path=output_path,
                    speaker_wav=self.speaker_wav,
                    language="en"
                )
            else:
                # Use default speaker
                self.model.tts_to_file(
                    text=clean_text,
                    file_path=output_path,
                    language="en"
                )
            
            return output_path
            
        except Exception as e:
            print(f"[!] Coqui XTTS generation failed: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text for TTS"""
        import re
        # Remove emojis
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        
        return emoji_pattern.sub('', text).strip()


class FacebookMMSVoice(VoiceEngine):
    """
    Facebook MMS-TTS Yoruba - Free, basic
    Original voice engine (for fallback)
    """
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.model_id = "facebook/mms-tts-yor"
        self.device = "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load the MMS model"""
        try:
            import torch
            from transformers import VitsModel, AutoTokenizer
            
            self.model = VitsModel.from_pretrained(self.model_id)
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            print(f"[OK] Facebook MMS-TTS loaded on {self.device}")
            
        except Exception as e:
            print(f"[!] Failed to load MMS model: {e}")
            self.model = None
    
    @property
    def name(self) -> str:
        return "Facebook MMS"
    
    @property
    def voice_type(self) -> str:
        return "Yoruba (basic)"
    
    def generate_speech(self, text: str, output_path: str) -> Optional[str]:
        """Generate speech using Facebook MMS"""
        if not self.model:
            return None
        
        try:
            import torch
            import soundfile as sf
            
            # Clean for Yoruba TTS
            clean_text = self._clean_text(text)
            
            inputs = self.tokenizer(clean_text, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                output = self.model(**inputs).waveform
            
            audio = output.cpu().numpy().squeeze()
            sf.write(output_path, audio, samplerate=16000)
            return output_path
            
        except Exception as e:
            print(f"[!] MMS generation failed: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """Clean text - keep Yoruba-friendly"""
        # Remove emojis but keep Yoruba diacritics
        import re
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"
            u"\U0001F300-\U0001F5FF"
            u"\U0001F680-\U0001F6FF"
            u"\U0001F1E0-\U0001F1FF"
            "]+", flags=re.UNICODE)
        
        return emoji_pattern.sub('', text).strip()


class VoiceEngineFactory:
    """Factory to create voice engines"""
    
    @staticmethod
    def create(
        engine_type: Literal["elevenlabs", "coqui", "mms"] = "elevenlabs",
        **kwargs
    ) -> VoiceEngine:
        """Create a voice engine instance"""
        
        if engine_type == "elevenlabs":
            return ElevenLabsVoice(**kwargs)
        elif engine_type == "coqui":
            return CoquiXTTSVoice(**kwargs)
        elif engine_type == "mms":
            return FacebookMMSVoice()
        else:
            raise ValueError(f"Unknown engine type: {engine_type}")
    
    @staticmethod
    def get_available_engines() -> list:
        """Get list of available engines based on installed packages"""
        available = []
        
        # Check ElevenLabs (just needs API key and requests)
        if os.getenv("ELEVENLABS_API_KEY"):
            available.append("elevenlabs")
        
        # Check Coqui TTS
        try:
            from TTS.api import TTS
            available.append("coqui")
        except ImportError:
            pass
        
        # Check Facebook MMS (needs transformers + torch)
        try:
            from transformers import VitsModel
            import torch
            available.append("mms")
        except ImportError:
            pass
        
        return available


# Test function
if __name__ == "__main__":
    print("Available voice engines:", VoiceEngineFactory.get_available_engines())
    
    # Test ElevenLabs if available
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if api_key:
        print("\n[*] Testing ElevenLabs...")
        engine = ElevenLabsVoice(api_key=api_key)
        output = engine.generate_speech(
            "Omo! How you dey? Na Sisi Lola be this o!",
            "test_elevenlabs.mp3"
        )
        if output:
            print(f"[OK] Generated: {output}")
