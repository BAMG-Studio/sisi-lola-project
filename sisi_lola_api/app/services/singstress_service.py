"""
SISI LOLA SINGSTRESS SERVICE
=============================
The vocal superpower that combines:
1. Lyria AI instrumental beats
2. Sisi's trained voice (XTTS/ElevenLabs clone)
3. Real-time audio mixing

Creates original Afrobeats songs with Sisi singing/rapping.
"""

import os
import io
import base64
import asyncio
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from sisi_lola_api.app.services.google_creative_service import get_google_creative_service
from sisi_lola_api.app.services.api_manager import get_api_manager

class SingstressService:
    """
    Sisi Lola's musical identity engine.
    Generates original songs with her voice over AI instrumentals.
    """
    
    def __init__(self):
        self.creative = get_google_creative_service()
        self.api_manager = get_api_manager()
        
        # Voice Configuration
        self.elevenlabs_voice_id = os.getenv("SISI_ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # Default to Adam until clone is ready
        self.voice_style = "singing"  # or "rapping", "speaking"
        
    async def generate_beat(self, mood: str, genre: str = "Afrobeats", duration: int = 30) -> Dict[str, Any]:
        """
        Generate an instrumental beat using Lyria.
        
        Args:
            mood: The emotional tone (e.g., "uplifting", "romantic", "party")
            genre: Music style (default Afrobeats)
            duration: Length in seconds
        """
        prompt = f"{genre} instrumental beat. Mood: {mood}. High energy, groovy bassline, talking drums, no vocals."
        
        result = await self.creative.generate_vibe_music(
            mood_prompt=prompt,
            duration=duration
        )
        
        if result["success"]:
            print(f"🎵 SINGSTRESS: Beat generated ({duration}s)")
            return {
                "success": True,
                "beat_base64": result.get("audio_base64"),
                "mime_type": result.get("mime_type", "audio/mpeg"),
                "duration": duration
            }
        return {"success": False, "error": result.get("error")}
    
    async def generate_vocals(self, lyrics: str, style: str = "singing") -> Dict[str, Any]:
        """
        Generate Sisi's vocals using ElevenLabs (or fallback to TTS).
        
        Args:
            lyrics: The words to sing/rap
            style: "singing", "rapping", or "speaking"
        """
        api_key = self.api_manager.elevenlabs_key
        
        if not api_key:
            print("⚠️ SINGSTRESS: ElevenLabs key not found, using fallback TTS")
            return await self._generate_vocals_fallback(lyrics)
        
        import httpx
        
        # ElevenLabs Speech-to-Speech or Text-to-Speech
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
        
        # Adjust settings for singing style
        if style == "singing":
            stability = 0.3  # More expressive
            similarity = 0.8
        elif style == "rapping":
            stability = 0.5
            similarity = 0.75
        else:
            stability = 0.7
            similarity = 0.85
        
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": lyrics,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": stability,
                "similarity_boost": similarity,
                "style": 0.5,
                "use_speaker_boost": True
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    audio_bytes = response.content
                    audio_base64 = base64.b64encode(audio_bytes).decode()
                    print(f"🎤 SINGSTRESS: Vocals generated ({len(lyrics)} chars)")
                    return {
                        "success": True,
                        "vocals_base64": audio_base64,
                        "mime_type": "audio/mpeg"
                    }
                else:
                    return {"success": False, "error": f"ElevenLabs error: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_vocals_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback to Gemini or XTTS for vocals"""
        from sisi_lola_api.app.services.unified_inference import get_inference_service, ResponseMode
        
        service = get_inference_service()
        result = await service.generate(text, mode=ResponseMode.VOICE_ONLY)
        
        if result.audio_base64:
            return {
                "success": True,
                "vocals_base64": result.audio_base64,
                "mime_type": "audio/wav"
            }
        return {"success": False, "error": "Fallback TTS failed"}
    
    async def mix_track(self, beat_base64: str, vocals_base64: str) -> Dict[str, Any]:
        """
        Mix vocals over the instrumental beat.
        
        This uses FFmpeg to overlay the vocals on the beat.
        For production, we'd use a proper audio mixing library.
        """
        import subprocess
        import tempfile
        
        try:
            # Decode audio
            beat_bytes = base64.b64decode(beat_base64)
            vocals_bytes = base64.b64decode(vocals_base64)
            
            with tempfile.TemporaryDirectory() as tmpdir:
                beat_path = f"{tmpdir}/beat.mp3"
                vocals_path = f"{tmpdir}/vocals.mp3"
                output_path = f"{tmpdir}/mixed.mp3"
                
                # Write temp files
                with open(beat_path, "wb") as f:
                    f.write(beat_bytes)
                with open(vocals_path, "wb") as f:
                    f.write(vocals_bytes)
                
                # FFmpeg mix command
                # Overlay vocals on beat with beat at 70% volume
                cmd = [
                    "ffmpeg", "-y",
                    "-i", beat_path,
                    "-i", vocals_path,
                    "-filter_complex", "[0:a]volume=0.7[beat];[beat][1:a]amix=inputs=2:duration=longest",
                    "-ac", "2",
                    output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, timeout=60)
                
                if result.returncode == 0:
                    with open(output_path, "rb") as f:
                        mixed_bytes = f.read()
                    
                    print("🎧 SINGSTRESS: Track mixed successfully!")
                    return {
                        "success": True,
                        "track_base64": base64.b64encode(mixed_bytes).decode(),
                        "mime_type": "audio/mpeg"
                    }
                else:
                    return {"success": False, "error": f"FFmpeg error: {result.stderr.decode()}"}
                    
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def create_singstress_track(
        self, 
        lyrics: str, 
        mood: str = "party", 
        genre: str = "Afrobeats",
        vocal_style: str = "singing",
        duration: int = 30
    ) -> Dict[str, Any]:
        """
        Full pipeline: Generate beat -> Generate vocals -> Mix -> Return final track.
        
        This is the main entry point for creating a Sisi Lola song.
        """
        print(f"🎼 SINGSTRESS: Creating new track - {mood} {genre}")
        
        # 1. Generate Beat
        beat_result = await self.generate_beat(mood, genre, duration)
        if not beat_result["success"]:
            return {"success": False, "stage": "beat", "error": beat_result.get("error")}
        
        # 2. Generate Vocals
        vocals_result = await self.generate_vocals(lyrics, vocal_style)
        if not vocals_result["success"]:
            return {"success": False, "stage": "vocals", "error": vocals_result.get("error")}
        
        # 3. Mix Track
        mixed_result = await self.mix_track(
            beat_result["beat_base64"],
            vocals_result["vocals_base64"]
        )
        
        if mixed_result["success"]:
            return {
                "success": True,
                "final_track_base64": mixed_result["track_base64"],
                "mime_type": "audio/mpeg",
                "metadata": {
                    "mood": mood,
                    "genre": genre,
                    "vocal_style": vocal_style,
                    "duration": duration,
                    "created_at": datetime.now().isoformat()
                }
            }
        
        return {"success": False, "stage": "mixing", "error": mixed_result.get("error")}

# Singleton
singstress_service = SingstressService()

def get_singstress_service() -> SingstressService:
    return singstress_service
