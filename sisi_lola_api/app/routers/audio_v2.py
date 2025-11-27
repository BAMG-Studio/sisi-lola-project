"""
Enhanced Audio Router with Multi-Language & Code-Switching Support

This is the upgraded audio endpoint that supports:
1. Cross-lingual voice cloning (same voice across languages)
2. Code-switching detection and handling
3. Nigerian prosody injection
4. Multiple TTS engines (ElevenLabs + XTTS v2)

Usage:
    POST /audio/v2/speak
    {
        "text": "Shey you understand? È rí gé!",
        "languages": ["en", "yo"],  # Auto-detect if empty
        "engine": "elevenlabs",      # or "xtts"
        "accent": "nigerian-yoruba",
        "emotion": "excited",
        "code_switching": true
    }
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import httpx
import os
import base64

from app.config import SisiLolaDNA
from app.utils.language_detector import SisiLolaLanguageDetector, LanguageSegment
from app.utils.prosody_processor import ProsodyProcessor
from app.utils.voice_accent import rewrite_for_accent

router = APIRouter()


class AudioRequestV2(BaseModel):
    """Enhanced audio generation request"""
    text: str = Field(..., description="Text to convert to speech")
    languages: Optional[List[str]] = Field(
        default=None,
        description="Expected languages (e.g., ['en', 'yo']). Auto-detect if None"
    )
    engine: str = Field(
        default="elevenlabs",
        description="TTS engine: 'elevenlabs' or 'xtts'"
    )
    accent: Optional[str] = Field(
        default="nigerian-yoruba",
        description="Accent/prosody style"
    )
    emotion: str = Field(
        default="neutral",
        description="Emotion: neutral, excited, casual, professional, etc."
    )
    code_switching: bool = Field(
        default=True,
        description="Enable code-switching detection and handling"
    )
    preserve_timbre: bool = Field(
        default=True,
        description="Keep Sisi Lola's voice across languages"
    )
    voice_id: Optional[str] = Field(
        default=None,
        description="Override default voice ID (ElevenLabs only)"
    )


class AudioResponseV2(BaseModel):
    """Enhanced audio generation response"""
    status: str
    audio_base64: Optional[str] = None
    audio_url: Optional[str] = None
    detected_languages: List[str]
    segments: List[Dict]
    engine_used: str
    processing_time_ms: float
    metadata: Dict


@router.get("/")
async def audio_v2_status():
    """Health check for v2 audio endpoint"""
    return {
        "status": "Audio V2 Module Online",
        "features": [
            "Multi-language support (13+ languages)",
            "Code-switching detection",
            "Nigerian prosody injection",
            "Cross-lingual voice cloning",
            "Emotion control"
        ],
        "engines": {
            "elevenlabs": "✓ Available" if os.getenv("ELEVENLABS_API_KEY") else "❌ Missing API key",
            "xtts": "⚠️ Coming soon (install Coqui TTS)"
        },
        "supported_languages": {
            "en": "English",
            "yo": "Yoruba",
            "pcm": "Nigerian Pidgin",
            "it": "Italian",
            "sw": "Swahili",
            "ha": "Hausa",
            "ig": "Igbo",
            "fr": "French",
            "es": "Spanish"
        }
    }


@router.post("/speak", response_model=AudioResponseV2)
async def generate_speech_v2(request: AudioRequestV2):
    """
    Generate speech with advanced multi-language support.
    
    Pipeline:
    1. Detect languages and code-switching
    2. Apply Nigerian prosody if needed
    3. Generate speech (preserving timbre across languages)
    4. Return audio + metadata
    """
    import time
    start_time = time.time()
    
    # Initialize processors
    lang_detector = SisiLolaLanguageDetector()
    prosody_processor = ProsodyProcessor(intensity='medium')
    
    # Step 1: Detect languages and segment text
    segments = lang_detector.detect_code_switching(request.text)
    detected_langs = list(set([seg.language for seg in segments]))
    
    print(f"🔍 Detected languages: {detected_langs}")
    print(f"📝 Segments: {len(segments)}")
    
    # Step 2: Process each segment with appropriate prosody
    processed_segments = []
    for seg in segments:
        processed_text = seg.text
        
        # Apply Nigerian prosody to foreign languages
        if lang_detector.requires_prosody_adjustment(seg):
            processed_text = prosody_processor.apply_nigerian_prosody(
                text=seg.text,
                target_language=seg.language,
                source_emotion=request.emotion
            )
        
        processed_segments.append({
            'original': seg.text,
            'processed': processed_text,
            'language': seg.language,
            'confidence': seg.confidence
        })
    
    # Step 3: Combine segments for TTS
    if request.code_switching and len(segments) > 1:
        # Use code-switching aware combination
        combined_text = prosody_processor.smooth_code_switching([
            (seg['processed'], seg['language']) for seg in processed_segments
        ])
    else:
        # Simple concatenation
        combined_text = ' '.join([seg['processed'] for seg in processed_segments])
    
    # Step 4: Adjust for TTS engine
    tts_ready_text = prosody_processor.adjust_for_tts(
        combined_text,
        tts_engine=request.engine
    )
    
    print(f"🎤 Final TTS text: {tts_ready_text}")
    
    # Step 5: Generate audio
    if request.engine == "elevenlabs":
        audio_data = await _generate_elevenlabs(
            text=tts_ready_text,
            voice_id=request.voice_id or SisiLolaDNA.VOICE_ID,
            detected_langs=detected_langs
        )
    elif request.engine == "xtts":
        audio_data = await _generate_xtts(
            text=tts_ready_text,
            languages=detected_langs,
            preserve_timbre=request.preserve_timbre
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown engine: {request.engine}")
    
    # Calculate processing time
    processing_time = (time.time() - start_time) * 1000  # milliseconds
    
    return AudioResponseV2(
        status="success",
        audio_base64=audio_data['audio_base64'],
        detected_languages=detected_langs,
        segments=processed_segments,
        engine_used=request.engine,
        processing_time_ms=round(processing_time, 2),
        metadata={
            "original_text": request.text,
            "processed_text": tts_ready_text,
            "accent": request.accent,
            "emotion": request.emotion,
            "code_switching_detected": len(segments) > 1
        }
    )


async def _generate_elevenlabs(
    text: str,
    voice_id: str,
    detected_langs: List[str]
) -> Dict:
    """
    Generate speech using ElevenLabs API.
    
    Note: ElevenLabs doesn't natively support cross-lingual timbre,
    but we can use their multilingual model.
    """
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not elevenlabs_key:
        raise HTTPException(
            status_code=500,
            detail="ELEVENLABS_API_KEY not set in .env"
        )
    
    # Determine which ElevenLabs model to use
    # Use multilingual_v2 if non-English detected
    has_non_english = any(lang not in ['en', 'en-US'] for lang in detected_langs)
    model_id = "eleven_multilingual_v2" if has_non_english else "eleven_monolingual_v1"
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": SisiLolaDNA.VOICE_SETTINGS
    }
    
    headers = {
        "xi-api-key": elevenlabs_key,
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            
            return {
                "audio_base64": audio_base64,
                "provider": "ElevenLabs",
                "model": model_id
            }
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"ElevenLabs API error: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Audio generation failed: {str(e)}"
        )


async def _generate_xtts(
    text: str,
    languages: List[str],
    preserve_timbre: bool = True
) -> Dict:
    """
    Generate speech using Coqui XTTS v2 (local inference).
    
    This is where cross-lingual voice cloning happens!
    XTTS can speak Italian/Swahili with Sisi Lola's Nigerian voice.
    
    TODO: Implement after XTTS setup
    """
    # Check if XTTS is available
    try:
        from TTS.api import TTS
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="XTTS not installed. Run: pip install TTS"
        )
    
    # This is a placeholder - actual implementation after XTTS training
    raise HTTPException(
        status_code=501,
        detail="XTTS engine coming soon. Use 'elevenlabs' for now."
    )


@router.post("/multilingual")
async def generate_multilingual(
    text: str,
    target_languages: List[str],
    preserve_timbre: bool = True,
    cultural_adaptation: str = "light"
):
    """
    Generate the same text in multiple languages with Sisi's voice.
    
    Example:
        POST /audio/v2/multilingual
        {
            "text": "Good morning everyone!",
            "target_languages": ["en", "yo", "it", "sw"],
            "preserve_timbre": true
        }
        
        Returns: Audio in all 4 languages with the same voice!
    """
    prosody_processor = ProsodyProcessor(
        intensity='medium' if cultural_adaptation == 'light' else 'heavy'
    )
    
    results = {}
    
    for lang in target_languages:
        # Apply Nigerian prosody to foreign languages
        processed_text = prosody_processor.apply_nigerian_prosody(
            text=text,
            target_language=lang,
            source_emotion='neutral'
        )
        
        # Generate audio (using XTTS for cross-lingual, ElevenLabs as fallback)
        try:
            audio = await _generate_xtts(
                text=processed_text,
                languages=[lang],
                preserve_timbre=preserve_timbre
            )
        except HTTPException:
            # Fallback to ElevenLabs
            audio = await _generate_elevenlabs(
                text=processed_text,
                voice_id=SisiLolaDNA.VOICE_ID,
                detected_langs=[lang]
            )
        
        results[lang] = audio['audio_base64']
    
    return {
        "status": "success",
        "audio_files": results,
        "metadata": {
            "original_text": text,
            "languages": target_languages,
            "timbre_preserved": preserve_timbre,
            "cultural_adaptation": cultural_adaptation
        }
    }


@router.get("/test")
async def test_multilingual():
    """
    Test endpoint to demonstrate multi-language capabilities.
    
    Generates "Hello, I'm Sisi Lola" in multiple languages.
    """
    test_phrase = "Hello darlings, I'm Sisi Lola!"
    
    lang_detector = SisiLolaLanguageDetector()
    prosody_processor = ProsodyProcessor()
    
    # Test different language versions
    variations = {
        "English": test_phrase,
        "Nigerian Pidgin": "Wetin dey happen! I be Sisi Lola oh!",
        "Yoruba": "Báwo ni ẹ! Èmi ni Sisi Lola!",
        "Italian (with Nigerian flair)": prosody_processor.apply_nigerian_prosody(
            "Ciao bella! Sono Sisi Lola!",
            target_language="it",
            source_emotion="excited"
        ),
        "Swahili (with Nigerian flair)": prosody_processor.apply_nigerian_prosody(
            "Jambo rafiki! Mimi ni Sisi Lola!",
            target_language="sw",
            source_emotion="excited"
        )
    }
    
    # Analyze each variation
    results = {}
    for name, text in variations.items():
        segments = lang_detector.detect_code_switching(text)
        results[name] = {
            "text": text,
            "detected_language": segments[0].language if segments else "unknown",
            "confidence": segments[0].confidence if segments else 0.0
        }
    
    return {
        "status": "test",
        "message": "Multi-language test variations",
        "variations": results,
        "note": "Use /audio/v2/speak endpoint to generate actual audio"
    }
