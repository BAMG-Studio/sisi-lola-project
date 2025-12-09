#!/usr/bin/env python3
"""
SISI LOLA MULTI-VOICE LANGUAGE ROUTER
======================================
Routes text to appropriate voice engines based on language tags.

Voice Strategy:
- XTTS-v2: Primary neural voice for English + light Yoruba/Pidgin
- YarnGPT: Nigerian-accented English, Yoruba, Igbo, Hausa, Pidgin
- EdgeTTS: Fallback Nigerian English voices
- Festival: Reference for Yoruba tone evaluation (optional)

Language Tags (from N-ATLaS):
- [EN] ... [/EN] - English
- [YO] ... [/YO] - Yoruba
- [PG] ... [/PG] - Nigerian Pidgin
- [HA] ... [/HA] - Hausa
- [IG] ... [/IG] - Igbo
- [MX] ... [/MX] - Mixed/Code-switching

Prosody Tags (preserved across all engines):
- (laughs), (whispers), (soft tone), etc.
"""

import os
import re
import asyncio
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import yaml


class Language(Enum):
    ENGLISH = "en"
    YORUBA = "yo"
    PIDGIN = "pcm"  # ISO 639-3 for Nigerian Pidgin
    HAUSA = "ha"
    IGBO = "ig"
    MIXED = "mix"


class VoiceEngine(Enum):
    XTTS = "xtts"           # Primary neural voice (English + light Yoruba/Pidgin)
    YARNGPT = "yarngpt"     # Nigerian-centric TTS
    EDGE_TTS = "edge_tts"   # Fallback Nigerian English
    FESTIVAL = "festival"   # Reference Yoruba (evaluation only)
    ELEVENLABS = "elevenlabs"  # Premium option


@dataclass
class VoiceSegment:
    """A segment of text with its target language and voice engine."""
    text: str
    language: Language
    engine: VoiceEngine
    prosody_tags: List[str] = field(default_factory=list)
    ssml: Optional[str] = None


@dataclass
class VoiceProfile:
    """Configuration for a specific voice engine."""
    engine: VoiceEngine
    enabled: bool = True
    priority: int = 1
    languages: List[Language] = field(default_factory=list)
    config: Dict = field(default_factory=dict)


class LanguageVoiceRouter:
    """
    Routes text segments to appropriate voice engines based on language.
    
    Usage:
        router = LanguageVoiceRouter()
        segments = router.parse_and_route(text)
        for segment in segments:
            audio = await router.synthesize(segment)
    """
    
    # Language tag patterns
    LANGUAGE_PATTERNS = {
        Language.ENGLISH: r'\[EN\](.*?)\[/EN\]',
        Language.YORUBA: r'\[YO\](.*?)\[/YO\]',
        Language.PIDGIN: r'\[PG\](.*?)\[/PG\]',
        Language.HAUSA: r'\[HA\](.*?)\[/HA\]',
        Language.IGBO: r'\[IG\](.*?)\[/IG\]',
        Language.MIXED: r'\[MX\](.*?)\[/MX\]',
    }
    
    # Prosody tag patterns
    PROSODY_PATTERNS = [
        r'\(laughs?\)',
        r'\(whispers?\)',
        r'\(soft tone\)',
        r'\(excited\)',
        r'\(sad\)',
        r'\(angry\)',
        r'\(sarcastic\)',
    ]
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the router with voice engine configurations."""
        self.config_path = config_path or Path(__file__).parent.parent.parent / "sisi_lola_chat" / "voice_config.yaml"
        self.voice_profiles = self._load_voice_profiles()
        self.language_engine_map = self._build_language_engine_map()
        
    def _load_voice_profiles(self) -> Dict[VoiceEngine, VoiceProfile]:
        """Load voice profiles from config or use defaults."""
        profiles = {
            VoiceEngine.XTTS: VoiceProfile(
                engine=VoiceEngine.XTTS,
                enabled=True,
                priority=1,
                languages=[Language.ENGLISH, Language.PIDGIN, Language.MIXED],
                config={
                    "model_id": "tts_models/multilingual/multi-dataset/xtts_v2",
                    "speaker_wav": "04_AUDIO_CORE/voice_samples/sisi_lola_reference.wav",
                    "language": "en",
                }
            ),
            VoiceEngine.YARNGPT: VoiceProfile(
                engine=VoiceEngine.YARNGPT,
                enabled=True,  # Enable when available
                priority=1,
                languages=[Language.YORUBA, Language.PIDGIN, Language.HAUSA, Language.IGBO],
                config={
                    "api_endpoint": os.getenv("YARNGPT_API_URL", ""),
                    "api_key": os.getenv("YARNGPT_API_KEY", ""),
                }
            ),
            VoiceEngine.EDGE_TTS: VoiceProfile(
                engine=VoiceEngine.EDGE_TTS,
                enabled=True,
                priority=2,  # Fallback
                languages=[Language.ENGLISH, Language.PIDGIN],
                config={
                    "voice_female": "en-NG-EzinneNeural",
                    "voice_male": "en-NG-AbeoNeural",
                }
            ),
            VoiceEngine.FESTIVAL: VoiceProfile(
                engine=VoiceEngine.FESTIVAL,
                enabled=False,  # Reference only
                priority=99,
                languages=[Language.YORUBA],
                config={
                    "use_for_evaluation": True,
                    "voice": "yoruba_festival",
                }
            ),
            VoiceEngine.ELEVENLABS: VoiceProfile(
                engine=VoiceEngine.ELEVENLABS,
                enabled=bool(os.getenv("ELEVENLABS_API_KEY")),
                priority=0,  # Premium - highest priority when available
                languages=[Language.ENGLISH, Language.PIDGIN, Language.MIXED],
                config={
                    "voice_id": os.getenv("ELEVENLABS_VOICE_ID", ""),
                    "model_id": "eleven_multilingual_v2",
                }
            ),
        }
        
        # Try to load from config file
        if self.config_path and Path(self.config_path).exists():
            try:
                with open(self.config_path) as f:
                    config = yaml.safe_load(f)
                    # Merge with defaults
                    # TODO: Implement config merging
            except Exception as e:
                print(f"[WARN] Could not load voice config: {e}")
        
        return profiles
    
    def _build_language_engine_map(self) -> Dict[Language, List[VoiceEngine]]:
        """Build mapping from language to available engines (sorted by priority)."""
        lang_map: Dict[Language, List[Tuple[int, VoiceEngine]]] = {lang: [] for lang in Language}
        
        for engine, profile in self.voice_profiles.items():
            if profile.enabled:
                for lang in profile.languages:
                    lang_map[lang].append((profile.priority, engine))
        
        # Sort by priority and extract engines
        return {
            lang: [engine for _, engine in sorted(engines)]
            for lang, engines in lang_map.items()
        }
    
    def detect_language(self, text: str) -> Language:
        """
        Detect the primary language of text without explicit tags.
        Uses heuristics for Nigerian languages.
        """
        text_lower = text.lower()
        
        # Yoruba indicators (tonal marks, specific words)
        yoruba_markers = ['ẹ', 'ọ', 'ṣ', 'àbí', 'kílọ́', 'báwo', 'ṣé', 'jọ̀ọ́']
        if any(marker in text_lower for marker in yoruba_markers):
            return Language.YORUBA
        
        # Pidgin indicators
        pidgin_markers = [' dey ', ' wetin ', ' wahala ', ' abeg ', ' sef ', ' sha ', 
                         ' no be ', ' e don ', ' make ', ' for ', ' na ', ' o!']
        pidgin_count = sum(1 for marker in pidgin_markers if marker in text_lower)
        if pidgin_count >= 2:
            return Language.PIDGIN
        
        # Hausa indicators
        hausa_markers = ['ƙ', 'ɗ', 'ɓ', 'yaya', 'sannnu', 'nagode']
        if any(marker in text_lower for marker in hausa_markers):
            return Language.HAUSA
        
        # Igbo indicators
        igbo_markers = ['ị', 'ọ', 'ụ', 'ṅ', 'kedu', 'ndewo', 'daalu']
        if any(marker in text_lower for marker in igbo_markers):
            return Language.IGBO
        
        # Default to English
        return Language.ENGLISH
    
    def extract_prosody_tags(self, text: str) -> Tuple[str, List[str]]:
        """Extract prosody tags from text and return cleaned text + tags."""
        tags = []
        for pattern in self.PROSODY_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            tags.extend(matches)
        
        # Don't remove tags from text - they're handled by SSML generation
        return text, tags
    
    def parse_tagged_text(self, text: str) -> List[VoiceSegment]:
        """
        Parse text with language tags into segments.
        
        Example:
            "Hello! [YO]Báwo ni[/YO] How you dey?"
            -> [Segment(English), Segment(Yoruba), Segment(English/Pidgin)]
        """
        segments = []
        
        # Find all language-tagged sections
        all_matches = []
        for lang, pattern in self.LANGUAGE_PATTERNS.items():
            for match in re.finditer(pattern, text, re.DOTALL):
                all_matches.append((match.start(), match.end(), lang, match.group(1)))
        
        # Sort by position
        all_matches.sort(key=lambda x: x[0])
        
        # Build segments including untagged portions
        current_pos = 0
        for start, end, lang, content in all_matches:
            # Add untagged portion before this match
            if start > current_pos:
                untagged = text[current_pos:start].strip()
                if untagged:
                    detected_lang = self.detect_language(untagged)
                    clean_text, prosody = self.extract_prosody_tags(untagged)
                    segments.append(VoiceSegment(
                        text=clean_text,
                        language=detected_lang,
                        engine=self._get_best_engine(detected_lang),
                        prosody_tags=prosody,
                    ))
            
            # Add tagged portion
            clean_text, prosody = self.extract_prosody_tags(content.strip())
            segments.append(VoiceSegment(
                text=clean_text,
                language=lang,
                engine=self._get_best_engine(lang),
                prosody_tags=prosody,
            ))
            current_pos = end
        
        # Add remaining untagged portion
        if current_pos < len(text):
            remaining = text[current_pos:].strip()
            if remaining:
                detected_lang = self.detect_language(remaining)
                clean_text, prosody = self.extract_prosody_tags(remaining)
                segments.append(VoiceSegment(
                    text=clean_text,
                    language=detected_lang,
                    engine=self._get_best_engine(detected_lang),
                    prosody_tags=prosody,
                ))
        
        # If no segments found, treat whole text as one segment
        if not segments:
            detected_lang = self.detect_language(text)
            clean_text, prosody = self.extract_prosody_tags(text)
            segments.append(VoiceSegment(
                text=clean_text,
                language=detected_lang,
                engine=self._get_best_engine(detected_lang),
                prosody_tags=prosody,
            ))
        
        return segments
    
    def _get_best_engine(self, language: Language) -> VoiceEngine:
        """Get the best available engine for a language."""
        engines = self.language_engine_map.get(language, [])
        if engines:
            return engines[0]
        # Fallback to EdgeTTS
        return VoiceEngine.EDGE_TTS
    
    def generate_ssml(self, segment: VoiceSegment) -> str:
        """Generate SSML for a segment with prosody tags."""
        text = segment.text
        
        # Apply prosody transformations
        for tag in segment.prosody_tags:
            tag_lower = tag.lower()
            if 'laugh' in tag_lower:
                text = text.replace(tag, '<prosody pitch="+10%">haha</prosody>')
            elif 'whisper' in tag_lower:
                text = text.replace(tag, f'<prosody volume="x-soft" rate="85%">{text}</prosody>')
            elif 'soft' in tag_lower:
                text = text.replace(tag, '')
                text = f'<prosody volume="soft" rate="90%">{text}</prosody>'
            elif 'excited' in tag_lower:
                text = text.replace(tag, '')
                text = f'<prosody pitch="+10%" rate="110%">{text}</prosody>'
        
        # Wrap in speak tags
        ssml = f'<speak>{text}</speak>'
        return ssml
    
    async def synthesize_segment(self, segment: VoiceSegment) -> Optional[bytes]:
        """Synthesize audio for a single segment using the appropriate engine."""
        engine = segment.engine
        profile = self.voice_profiles.get(engine)
        
        if not profile or not profile.enabled:
            # Fallback to EdgeTTS
            engine = VoiceEngine.EDGE_TTS
            profile = self.voice_profiles[engine]
        
        try:
            if engine == VoiceEngine.EDGE_TTS:
                return await self._synthesize_edge_tts(segment, profile)
            elif engine == VoiceEngine.XTTS:
                return await self._synthesize_xtts(segment, profile)
            elif engine == VoiceEngine.YARNGPT:
                return await self._synthesize_yarngpt(segment, profile)
            elif engine == VoiceEngine.ELEVENLABS:
                return await self._synthesize_elevenlabs(segment, profile)
            else:
                print(f"[WARN] Engine {engine} not implemented, falling back to EdgeTTS")
                return await self._synthesize_edge_tts(segment, self.voice_profiles[VoiceEngine.EDGE_TTS])
        except Exception as e:
            print(f"[ERROR] Synthesis failed for {engine}: {e}")
            # Try fallback
            if engine != VoiceEngine.EDGE_TTS:
                print("[INFO] Falling back to EdgeTTS")
                return await self._synthesize_edge_tts(segment, self.voice_profiles[VoiceEngine.EDGE_TTS])
            return None
    
    async def _synthesize_edge_tts(self, segment: VoiceSegment, profile: VoiceProfile) -> bytes:
        """Synthesize using EdgeTTS."""
        import edge_tts
        
        voice = profile.config.get("voice_female", "en-NG-EzinneNeural")
        communicate = edge_tts.Communicate(segment.text, voice)
        
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        return audio_data
    
    async def _synthesize_xtts(self, segment: VoiceSegment, profile: VoiceProfile) -> bytes:
        """Synthesize using Coqui XTTS-v2."""
        try:
            from TTS.api import TTS
            import torch
            import io
            import soundfile as sf
            
            device = "cuda" if torch.cuda.is_available() else "cpu"
            tts = TTS(model_name=profile.config["model_id"]).to(device)
            
            speaker_wav = profile.config.get("speaker_wav")
            if speaker_wav and Path(speaker_wav).exists():
                # Clone voice from reference
                audio = tts.tts(
                    text=segment.text,
                    speaker_wav=speaker_wav,
                    language=profile.config.get("language", "en")
                )
            else:
                # Use default speaker
                audio = tts.tts(text=segment.text)
            
            # Convert to bytes
            buffer = io.BytesIO()
            sf.write(buffer, audio, 22050, format='WAV')
            return buffer.getvalue()
            
        except Exception as e:
            print(f"[ERROR] XTTS synthesis failed: {e}")
            raise
    
    async def _synthesize_yarngpt(self, segment: VoiceSegment, profile: VoiceProfile) -> bytes:
        """Synthesize using YarnGPT API."""
        import httpx
        
        api_url = profile.config.get("api_endpoint")
        api_key = profile.config.get("api_key")
        
        if not api_url:
            raise ValueError("YarnGPT API endpoint not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                api_url,
                headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
                json={
                    "text": segment.text,
                    "language": segment.language.value,
                }
            )
            response.raise_for_status()
            return response.content
    
    async def _synthesize_elevenlabs(self, segment: VoiceSegment, profile: VoiceProfile) -> bytes:
        """Synthesize using ElevenLabs API."""
        import httpx
        
        api_key = os.getenv("ELEVENLABS_API_KEY")
        voice_id = profile.config.get("voice_id") or os.getenv("ELEVENLABS_VOICE_ID")
        
        if not api_key or not voice_id:
            raise ValueError("ElevenLabs API key or voice ID not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "text": segment.text,
                    "model_id": profile.config.get("model_id", "eleven_multilingual_v2"),
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75,
                    }
                }
            )
            response.raise_for_status()
            return response.content
    
    async def synthesize_all(self, text: str, output_path: Optional[str] = None) -> bytes:
        """
        Parse text, route to engines, synthesize, and concatenate audio.
        
        Args:
            text: Input text (may contain language tags)
            output_path: Optional path to save the combined audio
            
        Returns:
            Combined audio as bytes
        """
        segments = self.parse_tagged_text(text)
        
        print(f"[INFO] Parsed {len(segments)} segments:")
        for i, seg in enumerate(segments):
            print(f"  [{i+1}] {seg.language.value} -> {seg.engine.value}: {seg.text[:50]}...")
        
        # Synthesize all segments
        audio_parts = []
        for segment in segments:
            audio = await self.synthesize_segment(segment)
            if audio:
                audio_parts.append(audio)
        
        # Concatenate audio (simple concatenation for now)
        # TODO: Add crossfade and proper audio processing
        combined = b"".join(audio_parts)
        
        if output_path:
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(combined)
            print(f"[OK] Saved to {output_path}")
        
        return combined
    
    def get_status(self) -> Dict:
        """Get status of all voice engines."""
        status = {}
        for engine, profile in self.voice_profiles.items():
            status[engine.value] = {
                "enabled": profile.enabled,
                "priority": profile.priority,
                "languages": [l.value for l in profile.languages],
            }
        return status


# Convenience function
async def speak_multilingual(text: str, output_path: Optional[str] = None) -> bytes:
    """Quick function to synthesize multilingual text."""
    router = LanguageVoiceRouter()
    return await router.synthesize_all(text, output_path)


if __name__ == "__main__":
    import asyncio
    
    # Test the router
    router = LanguageVoiceRouter()
    
    print("Voice Engine Status:")
    for engine, info in router.get_status().items():
        print(f"  {engine}: {info}")
    
    # Test parsing
    test_texts = [
        "Hello! How you dey today?",
        "[YO]Báwo ni[/YO] my friend! [PG]Wetin dey happen?[/PG]",
        "Omo! (laughs) This thing sweet o!",
        "[EN]Welcome to the show![/EN] [YO]Ẹ káàbọ̀![/YO] [PG]Make we start![/PG]",
    ]
    
    for text in test_texts:
        print(f"\nInput: {text}")
        segments = router.parse_tagged_text(text)
        for seg in segments:
            print(f"  -> [{seg.language.value}] {seg.engine.value}: {seg.text}")
    
    # Test synthesis (async)
    async def test_synthesis():
        test_text = "How you dey? I dey fine o! (laughs)"
        audio = await router.synthesize_all(test_text, "voice_outputs/multilingual_test.mp3")
        print(f"\nGenerated {len(audio)} bytes of audio")
    
    asyncio.run(test_synthesis())
