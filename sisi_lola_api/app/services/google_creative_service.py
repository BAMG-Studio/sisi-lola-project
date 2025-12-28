"""
SISI LOLA GOOGLE SUPREME CREATIVE SERVICE
==========================================
Integration with Google's highest-tier GenAI assets:
- Veo 3.1: 8-second cinematic video vibes
- Lyria: Native Afrobeats-inspired music/vocal synthesis
- Imagen 4: Photorealistic branding assets
- Nano Banana (Gemini 2.5 Flash): High-speed multimodal generation
"""

import os
import json
import asyncio
import base64
from typing import Optional, Dict, Any, List
from datetime import datetime
from sisi_lola_api.app.config import SisiLolaDNA
from sisi_lola_api.app.services.api_manager import get_api_manager

class GoogleCreativeService:
    def __init__(self):
        self.api_manager = get_api_manager()
        self.dna = SisiLolaDNA()

    async def generate_vibe_video(self, prompt: str, reference_image_b64: Optional[str] = None) -> Dict[str, Any]:
        """
        Produce a 'Sisi Vibe Short' (8-second cinematic video) using Veo 3.1.
        """
        client = self.api_manager.get_client("gemini")
        if not client:
            return {"success": False, "error": "Gemini API client not configured"}

        print(f"🎬 VEO: Generating 8-second vibe for prompt: {prompt}")
        
        # Combine with Sisi's Visual DNA
        full_prompt = f"{self.dna.VISUAL_PROMPT_CORE} {prompt} {self.dna.STYLE_WRAPPER}"
        
        model_id = self.dna.VEO_3_1
        
        # Request structure for Veo 3.1
        payload = {
            "prompt": full_prompt,
            "video_config": {
                "duration_seconds": 8,
                "fps": 24,
                "resolution": "1080p",
                "aspect_ratio": "9:16"  # Portrait for social engagement
            }
        }
        
        if reference_image_b64:
            payload["reference_image"] = {
                "inline_data": {
                    "mime_type": "image/png",
                    "data": reference_image_b64
                }
            }

        try:
            # Note: Veo often uses a long-running operation pattern in Vertex AI
            # In Gemini API preview, it might be a direct generateContent or specialized endpoint
            endpoint = f"/models/{model_id}:generateVideo"
            response = await client.post(endpoint, json=payload, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                print("✅ VEO: Video generated successfully.")
                return {
                    "success": True, 
                    "video_base64": data.get("video_data") or data.get("inlineData", {}).get("data"),
                    "mime_type": "video/mp4",
                    "model": model_id
                }
            else:
                print(f"❌ VEO Error {response.status_code}: {response.text}")
                return {"success": False, "error": response.text}
        except Exception as e:
            print(f"⚠️ VEO Exception: {e}")
            return {"success": False, "error": str(e)}

    async def generate_vibe_music(self, mood_prompt: str, duration: int = 15) -> Dict[str, Any]:
        """
        Generate background vibes or 'Sisi Beats' using Lyria.
        """
        client = self.api_manager.get_client("gemini")
        if not client: return {"success": False, "error": "Client not found"}

        print(f"🎵 LYRIA: Composing Afrobeats vibe for mood: {mood_prompt}")
        
        # Sisi's musical signature
        musical_dna = "Modern high-energy Afrobeats, soft Yoruba talking drums, rhythmic bass, glossy production."
        full_musical_prompt = f"{musical_dna} Mood: {mood_prompt}"
        
        model_id = self.dna.LYRIA_REALTIME
        
        payload = {
            "prompt": full_musical_prompt,
            "generation_config": {
                "candidate_count": 1,
                "duration_seconds": duration,
                "output_mime_type": "audio/mpeg"
            }
        }

        try:
            endpoint = f"/models/{model_id}:generateContent"
            response = await client.post(endpoint, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                # Lyria returns audio parts
                parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                for part in parts:
                    if "inlineData" in part and "audio" in part["inlineData"].get("mimeType", ""):
                        return {
                            "success": True,
                            "audio_base64": part["inlineData"]["data"],
                            "mime_type": part["inlineData"]["mimeType"]
                        }
            return {"success": False, "error": "No audio generated"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def generate_supreme_snapshot(self, scene: str) -> Dict[str, Any]:
        """
        High-fidelity photorealistic branding asset using Imagen 4.
        """
        client = self.api_manager.get_client("gemini")
        if not client: return {"success": False, "error": "Client not found"}

        full_prompt = f"{self.dna.VISUAL_PROMPT_CORE} {scene}. {self.dna.STYLE_WRAPPER}"
        model_id = self.dna.IMAGEN_4
        
        print(f"📸 IMAGEN: Capturing high-res snapshot: {scene}")
        
        payload = {
            "instances": [{"prompt": full_prompt}],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "1:1",
                "outputMimeType": "image/png"
            }
        }

        try:
            # Imagen often uses different endpoints depending on the platform instance
            endpoint = f"/models/{model_id}:predict"
            response = await client.post(endpoint, json=payload, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                img_data = data.get("predictions", [{}])[0].get("bytesBase64")
                return {"success": True, "image_base64": img_data, "model": model_id}
            return {"success": False, "error": response.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def generate_nano_engagement(self, text: str) -> str:
        """
        Fast 'Nano Banana' multimodal engagement.
        """
        # Nano Banana (Flash 2.5) is excellent for rapid chat + small image creation
        from sisi_lola_api.app.services.unified_inference import get_inference_service
        service = get_inference_service()
        
        # Route to Gemini 2.5 Flash
        return await service._generate_with_gemini(text, system_prompt=self.dna.SYSTEM_PERSONA)

# Singleton Instance
google_creative_service = GoogleCreativeService()

def get_google_creative_service():
    return google_creative_service
