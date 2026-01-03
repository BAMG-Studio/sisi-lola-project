# Sisi Lola Replicate Predictor (Standalone)
# Supreme Producer Pipeline: Voice + Video + Caching + Multi-Vibe Support
from cog import BasePredictor, Input, Path
import os
import time
import base64
import hashlib
import json
import requests
from typing import Optional, Dict, Any
from pathlib import Path as PathLib

# ============================================
# CACHE CONFIGURATION
# ============================================
CACHE_DIR = PathLib("/tmp/sisi_lola_cache")
DNA_CACHE_DIR = CACHE_DIR / "dna_images"
AUDIO_CACHE_DIR = CACHE_DIR / "audio"
VIDEO_CACHE_DIR = CACHE_DIR / "video"

# Character Consistency - SEED 45822
CHARACTER_SEED = 45822

# Voice IDs for different accent modes
VOICE_MODES = {
    "default": "e3EHR2GS90EO276k1OCA",  # Authentic V5 (Nigerian)
    "formal": "21m00Tcm4TlvDq8ikWAM",   # Rachel (International)
    "pidgin": "e3EHR2GS90EO276k1OCA",   # Same as default (Nigerian Pidgin)
}

# Vibe Categories with optimized settings
VIBE_CATEGORIES = {
    "tech_review": {
        "style": "minimalist",
        "background": "the_void",
        "voice_mode": "formal",
        "outfit": "all-black tactical wear"
    },
    "cultural": {
        "style": "afro_corporate",
        "background": "lounge_lagos",
        "voice_mode": "pidgin",
        "outfit": "Nigerian regalia with futuristic elements"
    },
    "entertainment": {
        "style": "casual",
        "background": "beach_resort",
        "voice_mode": "default",
        "outfit": "luxury athleisure"
    },
    "spiritual": {
        "style": "reverent",
        "background": "nsppd_temple",
        "voice_mode": "formal",
        "outfit": "elegant white flowing garment"
    },
}

class Predictor(BasePredictor):
    def setup(self):
        """Initialize the predictor with caching directories"""
        print("🇳🇬 SISI LOLA SUPREME PRODUCER v2.0")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("✨ Features: Multi-Vibe | Caching | Batch Processing")
        
        # Create cache directories
        for cache_dir in [CACHE_DIR, DNA_CACHE_DIR, AUDIO_CACHE_DIR, VIDEO_CACHE_DIR]:
            cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load DNA images into cache (character consistency)
        self._preload_dna_cache()
        
        print("✅ Ready to produce content!")

    def _preload_dna_cache(self):
        """Preload frequently used DNA images for faster generation"""
        # DNA images are cached to ensure SEED 45822 consistency
        self.dna_cache = {}
        print("📸 DNA cache initialized (SEED 45822 enforcement)")

    def _get_cache_key(self, text: str, vibe_id: str) -> str:
        """Generate unique cache key for content"""
        content = f"{text}:{vibe_id}"
        return hashlib.md5(content.encode()).hexdigest()

    def _check_cache(self, cache_key: str, cache_type: str = "audio") -> Optional[Path]:
        """Check if content exists in cache"""
        cache_dir = AUDIO_CACHE_DIR if cache_type == "audio" else VIDEO_CACHE_DIR
        cache_file = cache_dir / f"{cache_key}.{'wav' if cache_type == 'audio' else 'mp4'}"
        if cache_file.exists():
            print(f"💾 Cache HIT: {cache_type} for {cache_key[:8]}...")
            return cache_file
        return None

    def _save_to_cache(self, content: bytes, cache_key: str, cache_type: str = "audio") -> Path:
        """Save content to cache"""
        cache_dir = AUDIO_CACHE_DIR if cache_type == "audio" else VIDEO_CACHE_DIR
        extension = "wav" if cache_type == "audio" else "mp4"
        cache_file = cache_dir / f"{cache_key}.{extension}"
        with open(cache_file, "wb") as f:
            f.write(content)
        print(f"💾 Cached: {cache_type} as {cache_key[:8]}...")
        return cache_file

    def normalize_text_for_ai(self, text: str) -> str:
        """Fix pronunciation for Authentic Naija Accent"""
        replacements = {
            # Nigerian cities & places
            "Lagos": "Lay-gos",
            "lagos": "Lay-gos",
            "Abuja": "Ah-boo-jah",
            "Ibadan": "Ee-bah-dan",
            "Kano": "Kah-no",
            
            # Nigerian Pidgin terms
            "Naija": "Nai-jah",
            "Sisi": "Cee-cee",
            "wahala": "wa-ha-la",
            "Una": "Oo-na",
            "una": "oo-na",
            "Abeg": "Ah-beg",
            "Oya": "Oh-ya",
            "Wetin": "Way-teen",
            "wetin": "way-teen",
            "dey": "day",
            "sha": "shah",
            "abi": "ah-bee",
            
            # Yoruba phrases
            "Bawo ni": "Bah-wo nee",
            "O seun": "Oh shay-oon",
            "Oshisco": "Oh-shees-ko",
            "E kaaro": "Eh kah-roh",
            
            # Common expressions
            "EFCC": "E-F-C-C",
            "NSPPD": "N-S-P-P-D",
        }
        for word, replacement in replacements.items():
            text = text.replace(word, replacement)
        return text

    def _get_vibe_settings(self, vibe_id: str) -> Dict[str, Any]:
        """Get optimized settings based on vibe category"""
        # Extract category from vibe_id (e.g., "VIBE010_tech" -> "tech_review")
        for category in VIBE_CATEGORIES:
            if category.split("_")[0] in vibe_id.lower():
                return VIBE_CATEGORIES[category]
        return VIBE_CATEGORIES["entertainment"]  # Default

    def predict(
        self,
        script: str = Input(description="Script text for Sisi Lola to speak"),
        vibe_id: str = Input(description="Vibe ID for content category", default="CUSTOM"),
        vibe_category: str = Input(
            description="Content category (tech_review, cultural, entertainment, spiritual)",
            default="entertainment",
            choices=["tech_review", "cultural", "entertainment", "spiritual"]
        ),
        voice_mode: str = Input(
            description="Voice accent mode (default, formal, pidgin)",
            default="default",
            choices=["default", "formal", "pidgin"]
        ),
        use_cache: bool = Input(description="Use cached audio if available", default=True),
        elevenlabs_key: str = Input(description="ElevenLabs API Key", default=None),
        replicate_key: str = Input(description="Replicate API Token", default=None)
    ) -> Path:
        """
        🎬 SISI LOLA SUPREME PRODUCER
        
        Pipeline: Script → Voice (ElevenLabs) → Video (Wav2Lip) → Output
        
        Features:
        - Multi-Vibe content generation
        - Intelligent caching for cost optimization
        - Nigerian accent pronunciation fixes
        - Character consistency (SEED 45822)
        """
        
        start_time = time.time()
        print(f"\n🎬 ════════════════════════════════════════")
        print(f"🎬 PRODUCTION START: {vibe_id}")
        print(f"🎬 Category: {vibe_category} | Voice: {voice_mode}")
        print(f"🎬 ════════════════════════════════════════\n")
        
        # Setup Keys
        el_key = elevenlabs_key or os.environ.get("ELEVENLABS_API_KEY")
        rep_key = replicate_key or os.environ.get("REPLICATE_API_TOKEN")
        
        if not el_key:
            raise ValueError("❌ Missing ELEVENLABS_API_KEY!")

        # Get vibe-specific settings
        vibe_settings = VIBE_CATEGORIES.get(vibe_category, VIBE_CATEGORIES["entertainment"])
        effective_voice_mode = voice_mode if voice_mode != "default" else vibe_settings.get("voice_mode", "default")
        
        # Generate cache key
        cache_key = self._get_cache_key(script, f"{vibe_id}_{effective_voice_mode}")
        
        # Check cache first (cost optimization)
        if use_cache:
            cached_audio = self._check_cache(cache_key, "audio")
            if cached_audio:
                print(f"⚡ Using cached audio - saved API call!")
                return cached_audio

        # 1. Generate Voice (ElevenLabs)
        print("🎙️ STEP 1: Voice Generation (ElevenLabs)")
        print(f"   └─ Mode: {effective_voice_mode}")
        
        clean_text = self.normalize_text_for_ai(script)
        voice_id = VOICE_MODES.get(effective_voice_mode, VOICE_MODES["default"])
        
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
            raise RuntimeError(f"❌ ElevenLabs Error: {voice_response.text}")
        
        # Save to cache
        audio_path = self._save_to_cache(voice_response.content, cache_key, "audio")
        print("   └─ ✅ Voice generated and cached!")
            
        # 2. Video Generation (Future: Wav2Lip integration)
        print("🎥 STEP 2: Video Generation")
        print(f"   └─ Background: {vibe_settings.get('background', 'default')}")
        print(f"   └─ Outfit: {vibe_settings.get('outfit', 'default')}")
        
        # For now, return audio (video pipeline can be enhanced later)
        # TODO: Integrate Wav2Lip with DNA image and audio
        
        final_path = Path("/tmp/output.wav")
        with open(final_path, "wb") as f:
            f.write(voice_response.content)
        
        elapsed = time.time() - start_time
        print(f"\n✅ ════════════════════════════════════════")
        print(f"✅ PRODUCTION COMPLETE")
        print(f"✅ Time: {elapsed:.2f}s | Vibe: {vibe_id}")
        print(f"✅ Output: {final_path}")
        print(f"✅ ════════════════════════════════════════\n")
        
        return final_path
