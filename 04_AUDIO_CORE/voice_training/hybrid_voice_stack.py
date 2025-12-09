#!/usr/bin/env python3
"""
SISI LOLA HYBRID VOICE STACK
==============================
Multi-engine voice synthesis combining:
1. XTTS-v2: Primary cloned voice for English + light code-switching
2. YarnGPT-local: Nigerian-accented English, Yoruba, Igbo, Hausa
3. Yoruba VITS: Fine-tuned on YorùLect + ÌròyìnSpeech
4. NaijaTTS: Nigerian Pidgin with pitch control
5. Festival-Yoruba: Reference/evaluation baseline for tone checking

Architecture:
┌─────────────────────────────────────────────────────────────────────────┐
│                     SISI LOLA HYBRID VOICE STACK                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Input Text (with language tags from N-ATLaS)                          │
│  "How you dey? [YO]Ẹ kú àárọ̀[/YO]. [NP]Wetin dey happen?[/NP]"       │
│                          │                                              │
│                          ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    LANGUAGE ROUTER                                │  │
│  │  • Parse [YO], [NP], [IG], [HA] tags                            │  │
│  │  • Split into language-specific segments                         │  │
│  │  • Apply prosody/style tags                                      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                          │                                              │
│          ┌───────────────┼───────────────┬───────────────┐             │
│          ▼               ▼               ▼               ▼             │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │  XTTS-v2   │ │ Yoruba VITS │ │  NaijaTTS   │ │ YarnGPT-loc │      │
│  │            │ │             │ │             │ │             │      │
│  │ • English  │ │ • Yoruba    │ │ • Pidgin    │ │ • Multi-NG  │      │
│  │ • Cloned   │ │ • YorùLect  │ │ • Pitch ctl │ │ • Fallback  │      │
│  │ • Primary  │ │ • ÌròyìnSp  │ │ • Prosody   │ │ • All langs │      │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘      │
│         │               │               │               │              │
│         └───────────────┴───────────────┴───────────────┘              │
│                          │                                              │
│                          ▼                                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    AUDIO STITCHER                                 │  │
│  │  • Concatenate language segments                                  │  │
│  │  • Normalize volume/sample rate                                   │  │
│  │  • Add transitions/crossfades                                     │  │
│  │  • Apply final prosody adjustments                               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                          │                                              │
│                          ▼                                              │
│                   Final Audio Output                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

Usage:
    from hybrid_voice_stack import HybridVoiceStack
    
    stack = HybridVoiceStack()
    audio = stack.synthesize("How you dey? [YO]Ẹ kú àárọ̀[/YO]")
    audio.export("output.wav")
"""

import os
import re
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages in the Sisi Lola voice stack"""
    ENGLISH = "en"
    YORUBA = "yo"
    PIDGIN = "np"  # Nigerian Pidgin
    IGBO = "ig"
    HAUSA = "ha"
    MIXED = "mix"  # Code-switched content


class VoiceEngine(Enum):
    """Available voice synthesis engines"""
    XTTS_V2 = "xtts"           # Primary cloned voice
    YORUBA_VITS = "yoruba_vits" # YorùLect/ÌròyìnSpeech trained
    NAIJA_TTS = "naija_tts"     # Nigerian Pidgin TTS
    YARNGPT = "yarngpt"         # Multi-Nigerian language
    FESTIVAL_YORUBA = "festival" # Reference/evaluation
    EDGE_TTS = "edge_tts"       # Fallback (Nigerian English)
    ELEVENLABS = "elevenlabs"   # Premium fallback


@dataclass
class TextSegment:
    """A segment of text with language and style annotations"""
    text: str
    language: Language
    style_tags: List[str] = field(default_factory=list)
    prosody: Dict[str, str] = field(default_factory=dict)
    
    def __repr__(self):
        return f"TextSegment({self.language.value}: '{self.text[:30]}...')"


@dataclass
class AudioSegment:
    """A synthesized audio segment"""
    audio_path: str
    duration_ms: int
    language: Language
    engine_used: VoiceEngine
    sample_rate: int = 22050


class LanguageRouter:
    """
    Routes text segments to appropriate voice engines based on language tags.
    
    Tag format from N-ATLaS:
    - [YO]Yoruba text[/YO]
    - [NP]Pidgin text[/NP]
    - [IG]Igbo text[/IG]
    - [HA]Hausa text[/HA]
    - Untagged = English or auto-detect
    """
    
    # Language tag patterns
    TAG_PATTERNS = {
        Language.YORUBA: (r'\[YO\]', r'\[/YO\]'),
        Language.PIDGIN: (r'\[NP\]', r'\[/NP\]'),
        Language.IGBO: (r'\[IG\]', r'\[/IG\]'),
        Language.HAUSA: (r'\[HA\]', r'\[/HA\]'),
    }
    
    # Style/prosody tag patterns
    STYLE_PATTERNS = {
        'laugh': r'\(laughs?\)',
        'whisper': r'\(whispers?\)',
        'soft': r'\(soft(?:ly)?\)',
        'excited': r'\(excited\)',
        'emphasis': r'\(emphasis\)',
    }
    
    # Nigerian Pidgin markers for auto-detection
    PIDGIN_MARKERS = [
        r'\b(dey|na|wetin|abeg|abi|sha|sef|o!|wahala|omo|chai)\b',
        r'\b(no be|e don|make we|how far|i go|you sabi)\b',
    ]
    
    # Yoruba markers for auto-detection
    YORUBA_MARKERS = [
        r'[ẹọṣ]',  # Yoruba diacritics
        r'\b(ẹ kú|bàwo|ṣé|kí ni|ó dára|àbí)\b',
    ]
    
    def __init__(self):
        self.pidgin_pattern = re.compile('|'.join(self.PIDGIN_MARKERS), re.IGNORECASE)
        self.yoruba_pattern = re.compile('|'.join(self.YORUBA_MARKERS), re.IGNORECASE)
    
    def parse_text(self, text: str) -> List[TextSegment]:
        """
        Parse text into language-tagged segments.
        
        Args:
            text: Input text with optional language tags
            
        Returns:
            List of TextSegment objects
        """
        segments = []
        
        # First, extract explicitly tagged segments
        remaining = text
        for lang, (open_tag, close_tag) in self.TAG_PATTERNS.items():
            pattern = f'{open_tag}(.*?){close_tag}'
            matches = list(re.finditer(pattern, remaining, re.DOTALL | re.IGNORECASE))
            
            for match in matches:
                # Add the text before this match as English/auto-detect
                before_text = remaining[:match.start()]
                if before_text.strip():
                    segments.extend(self._parse_untagged(before_text))
                
                # Add the tagged segment
                tagged_text = match.group(1).strip()
                if tagged_text:
                    segments.append(TextSegment(
                        text=tagged_text,
                        language=lang,
                        style_tags=self._extract_style_tags(tagged_text)
                    ))
                
                remaining = remaining[match.end():]
        
        # Handle any remaining untagged text
        if remaining.strip():
            segments.extend(self._parse_untagged(remaining))
        
        return segments if segments else [TextSegment(text=text, language=Language.ENGLISH)]
    
    def _parse_untagged(self, text: str) -> List[TextSegment]:
        """Parse untagged text, auto-detecting language where possible"""
        segments = []
        
        # Split by sentence for finer-grained language detection
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            # Auto-detect language
            lang = self._detect_language(sentence)
            segments.append(TextSegment(
                text=sentence.strip(),
                language=lang,
                style_tags=self._extract_style_tags(sentence)
            ))
        
        return segments
    
    def _detect_language(self, text: str) -> Language:
        """Auto-detect language from text content"""
        # Check for Yoruba markers (diacritics are strong signal)
        if self.yoruba_pattern.search(text):
            return Language.YORUBA
        
        # Check for Pidgin markers
        if self.pidgin_pattern.search(text):
            return Language.PIDGIN
        
        # Default to English
        return Language.ENGLISH
    
    def _extract_style_tags(self, text: str) -> List[str]:
        """Extract style/prosody tags from text"""
        tags = []
        for tag_name, pattern in self.STYLE_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                tags.append(tag_name)
        return tags


class VoiceEngineManager:
    """
    Manages multiple voice synthesis engines and routes requests appropriately.
    """
    
    # Engine priority by language (first available is used)
    ENGINE_PRIORITY = {
        Language.ENGLISH: [VoiceEngine.XTTS_V2, VoiceEngine.ELEVENLABS, VoiceEngine.EDGE_TTS],
        Language.YORUBA: [VoiceEngine.YORUBA_VITS, VoiceEngine.YARNGPT, VoiceEngine.XTTS_V2, VoiceEngine.EDGE_TTS],
        Language.PIDGIN: [VoiceEngine.NAIJA_TTS, VoiceEngine.YARNGPT, VoiceEngine.XTTS_V2, VoiceEngine.EDGE_TTS],
        Language.IGBO: [VoiceEngine.YARNGPT, VoiceEngine.XTTS_V2, VoiceEngine.EDGE_TTS],
        Language.HAUSA: [VoiceEngine.YARNGPT, VoiceEngine.XTTS_V2, VoiceEngine.EDGE_TTS],
        Language.MIXED: [VoiceEngine.XTTS_V2, VoiceEngine.YARNGPT, VoiceEngine.EDGE_TTS],
    }
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.available_engines = self._detect_available_engines()
        self._engine_instances = {}
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load voice configuration"""
        if config_path and Path(config_path).exists():
            import yaml
            with open(config_path) as f:
                return yaml.safe_load(f)
        
        # Default config
        return {
            'primary_engine': 'xtts',
            'sample_rate': 22050,
            'output_format': 'wav',
            'engines': {
                'xtts': {
                    'model_path': 'ml_training/checkpoints/xtts_sisi_lola',
                    'reference_audio': '04_AUDIO_CORE/voice_samples/sisi_lola_reference.wav'
                },
                'edge_tts': {
                    'voice_id': 'en-NG-EzinneNeural'
                }
            }
        }
    
    def _detect_available_engines(self) -> List[VoiceEngine]:
        """Detect which voice engines are available"""
        available = []
        
        # Always available (cloud-based)
        available.append(VoiceEngine.EDGE_TTS)
        
        # Check for ElevenLabs API key
        if os.getenv('ELEVENLABS_API_KEY'):
            available.append(VoiceEngine.ELEVENLABS)
        
        # Check for XTTS (Coqui TTS)
        try:
            from TTS.api import TTS
            available.append(VoiceEngine.XTTS_V2)
        except ImportError:
            logger.warning("Coqui TTS not available - XTTS disabled")
        
        # Check for YarnGPT
        try:
            # YarnGPT would be loaded from HuggingFace or local
            available.append(VoiceEngine.YARNGPT)
        except Exception:
            pass
        
        logger.info(f"Available engines: {[e.value for e in available]}")
        return available
    
    def get_engine_for_language(self, language: Language) -> VoiceEngine:
        """Get the best available engine for a language"""
        priority_list = self.ENGINE_PRIORITY.get(language, [VoiceEngine.EDGE_TTS])
        
        for engine in priority_list:
            if engine in self.available_engines:
                return engine
        
        # Fallback
        return VoiceEngine.EDGE_TTS
    
    async def synthesize_segment(
        self, 
        segment: TextSegment,
        output_path: str
    ) -> AudioSegment:
        """
        Synthesize a single text segment using the appropriate engine.
        """
        engine = self.get_engine_for_language(segment.language)
        logger.info(f"Synthesizing [{segment.language.value}] with {engine.value}: {segment.text[:50]}...")
        
        if engine == VoiceEngine.EDGE_TTS:
            return await self._synthesize_edge_tts(segment, output_path)
        elif engine == VoiceEngine.XTTS_V2:
            return await self._synthesize_xtts(segment, output_path)
        elif engine == VoiceEngine.ELEVENLABS:
            return await self._synthesize_elevenlabs(segment, output_path)
        elif engine == VoiceEngine.YARNGPT:
            return await self._synthesize_yarngpt(segment, output_path)
        elif engine == VoiceEngine.YORUBA_VITS:
            return await self._synthesize_yoruba_vits(segment, output_path)
        elif engine == VoiceEngine.NAIJA_TTS:
            return await self._synthesize_naija_tts(segment, output_path)
        else:
            # Fallback to EdgeTTS
            return await self._synthesize_edge_tts(segment, output_path)
    
    async def _synthesize_edge_tts(
        self, 
        segment: TextSegment, 
        output_path: str
    ) -> AudioSegment:
        """Synthesize using Microsoft EdgeTTS (free, Nigerian voices)"""
        import edge_tts
        
        # Select voice based on language
        voice_map = {
            Language.ENGLISH: 'en-NG-EzinneNeural',
            Language.YORUBA: 'en-NG-EzinneNeural',  # No native Yoruba, use Nigerian English
            Language.PIDGIN: 'en-NG-EzinneNeural',
            Language.IGBO: 'en-NG-AbeoNeural',
            Language.HAUSA: 'en-NG-AbeoNeural',
        }
        voice = voice_map.get(segment.language, 'en-NG-EzinneNeural')
        
        # Apply prosody based on style tags
        text = segment.text
        if 'whisper' in segment.style_tags:
            text = f'<prosody volume="soft" rate="slow">{text}</prosody>'
        elif 'excited' in segment.style_tags:
            text = f'<prosody pitch="+10%" rate="fast">{text}</prosody>'
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        
        return AudioSegment(
            audio_path=output_path,
            duration_ms=self._get_audio_duration(output_path),
            language=segment.language,
            engine_used=VoiceEngine.EDGE_TTS,
            sample_rate=24000
        )
    
    async def _synthesize_xtts(
        self, 
        segment: TextSegment, 
        output_path: str
    ) -> AudioSegment:
        """Synthesize using XTTS-v2 (Coqui TTS)"""
        try:
            from TTS.api import TTS
            
            # Initialize XTTS
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            
            # Get reference audio for voice cloning
            reference_audio = self.config.get('engines', {}).get('xtts', {}).get(
                'reference_audio', 
                '04_AUDIO_CORE/voice_samples/sisi_lola_reference.wav'
            )
            
            # Language code for XTTS
            lang_map = {
                Language.ENGLISH: 'en',
                Language.YORUBA: 'en',  # XTTS doesn't support Yoruba natively
                Language.PIDGIN: 'en',
                Language.IGBO: 'en',
                Language.HAUSA: 'en',
            }
            
            if Path(reference_audio).exists():
                tts.tts_to_file(
                    text=segment.text,
                    file_path=output_path,
                    speaker_wav=reference_audio,
                    language=lang_map.get(segment.language, 'en')
                )
            else:
                # Without reference, use default speaker
                tts.tts_to_file(
                    text=segment.text,
                    file_path=output_path,
                    language=lang_map.get(segment.language, 'en')
                )
            
            return AudioSegment(
                audio_path=output_path,
                duration_ms=self._get_audio_duration(output_path),
                language=segment.language,
                engine_used=VoiceEngine.XTTS_V2,
                sample_rate=22050
            )
        except Exception as e:
            logger.error(f"XTTS synthesis failed: {e}, falling back to EdgeTTS")
            return await self._synthesize_edge_tts(segment, output_path)
    
    async def _synthesize_elevenlabs(
        self, 
        segment: TextSegment, 
        output_path: str
    ) -> AudioSegment:
        """Synthesize using ElevenLabs API"""
        from elevenlabs import generate, save, set_api_key
        
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            return await self._synthesize_edge_tts(segment, output_path)
        
        set_api_key(api_key)
        
        audio = generate(
            text=segment.text,
            voice="Rachel",  # Or custom Sisi Lola voice
            model="eleven_multilingual_v2"
        )
        
        save(audio, output_path)
        
        return AudioSegment(
            audio_path=output_path,
            duration_ms=self._get_audio_duration(output_path),
            language=segment.language,
            engine_used=VoiceEngine.ELEVENLABS,
            sample_rate=44100
        )
    
    async def _synthesize_yarngpt(
        self, 
        segment: TextSegment, 
        output_path: str
    ) -> AudioSegment:
        """
        Synthesize using YarnGPT-local.
        YarnGPT is optimized for Nigerian languages.
        """
        # TODO: Implement YarnGPT integration when model is available
        # For now, fallback to EdgeTTS
        logger.info("YarnGPT not yet integrated, using EdgeTTS fallback")
        return await self._synthesize_edge_tts(segment, output_path)
    
    async def _synthesize_yoruba_vits(
        self, 
        segment: TextSegment, 
        output_path: str
    ) -> AudioSegment:
        """
        Synthesize using Yoruba-optimized VITS model.
        Trained on YorùLect + ÌròyìnSpeech.
        """
        # TODO: Implement Yoruba VITS when model is trained
        logger.info("Yoruba VITS not yet trained, using EdgeTTS fallback")
        return await self._synthesize_edge_tts(segment, output_path)
    
    async def _synthesize_naija_tts(
        self, 
        segment: TextSegment, 
        output_path: str
    ) -> AudioSegment:
        """
        Synthesize using NaijaTTS.
        Specialized for Nigerian Pidgin with pitch control.
        """
        # TODO: Implement NaijaTTS when model is available
        logger.info("NaijaTTS not yet integrated, using EdgeTTS fallback")
        return await self._synthesize_edge_tts(segment, output_path)
    
    def _get_audio_duration(self, audio_path: str) -> int:
        """Get audio duration in milliseconds"""
        try:
            from pydub import AudioSegment as PydubSegment
            audio = PydubSegment.from_file(audio_path)
            return len(audio)
        except Exception:
            return 0


class AudioStitcher:
    """
    Stitches multiple audio segments into a single output.
    Handles normalization, crossfades, and format conversion.
    """
    
    def __init__(self, target_sample_rate: int = 22050):
        self.target_sample_rate = target_sample_rate
    
    def stitch(
        self, 
        segments: List[AudioSegment], 
        output_path: str,
        crossfade_ms: int = 50
    ) -> str:
        """
        Stitch audio segments together with optional crossfades.
        """
        try:
            from pydub import AudioSegment as PydubSegment
            
            if not segments:
                raise ValueError("No segments to stitch")
            
            # Load first segment
            combined = PydubSegment.from_file(segments[0].audio_path)
            
            # Append remaining segments with crossfade
            for segment in segments[1:]:
                next_audio = PydubSegment.from_file(segment.audio_path)
                
                if crossfade_ms > 0 and len(combined) > crossfade_ms:
                    combined = combined.append(next_audio, crossfade=crossfade_ms)
                else:
                    combined = combined + next_audio
            
            # Normalize
            combined = combined.normalize()
            
            # Export
            combined.export(output_path, format="wav")
            
            return output_path
            
        except ImportError:
            # Without pydub, just return the first segment
            logger.warning("pydub not available, returning first segment only")
            import shutil
            shutil.copy(segments[0].audio_path, output_path)
            return output_path


class HybridVoiceStack:
    """
    Main interface for the hybrid voice synthesis stack.
    
    Combines multiple TTS engines for optimal Nigerian language support:
    - XTTS-v2 for English and voice cloning
    - Yoruba VITS for Yoruba content
    - NaijaTTS for Pidgin content
    - YarnGPT for multi-language fallback
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.router = LanguageRouter()
        self.engine_manager = VoiceEngineManager(config_path)
        self.stitcher = AudioStitcher()
        self.temp_dir = Path(tempfile.gettempdir()) / "sisi_lola_voice"
        self.temp_dir.mkdir(exist_ok=True)
    
    async def synthesize(
        self, 
        text: str, 
        output_path: Optional[str] = None
    ) -> str:
        """
        Synthesize text with automatic language routing.
        
        Args:
            text: Input text with optional language tags
            output_path: Output file path (auto-generated if not provided)
            
        Returns:
            Path to the synthesized audio file
        """
        if output_path is None:
            output_path = str(self.temp_dir / f"output_{hash(text)}.wav")
        
        # Parse text into segments
        segments = self.router.parse_text(text)
        logger.info(f"Parsed {len(segments)} segments from text")
        
        # Synthesize each segment
        audio_segments = []
        for i, segment in enumerate(segments):
            segment_path = str(self.temp_dir / f"segment_{i}.wav")
            audio_segment = await self.engine_manager.synthesize_segment(
                segment, segment_path
            )
            audio_segments.append(audio_segment)
        
        # Stitch segments together
        if len(audio_segments) == 1:
            # Single segment, just copy
            import shutil
            shutil.copy(audio_segments[0].audio_path, output_path)
        else:
            self.stitcher.stitch(audio_segments, output_path)
        
        return output_path
    
    def synthesize_sync(self, text: str, output_path: Optional[str] = None) -> str:
        """Synchronous wrapper for synthesize()"""
        import asyncio
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.synthesize(text, output_path))
    
    def get_available_engines(self) -> Dict[str, List[str]]:
        """Get available engines by language"""
        result = {}
        for lang in Language:
            engine = self.engine_manager.get_engine_for_language(lang)
            result[lang.value] = engine.value
        return result


# Convenience functions
def synthesize_text(text: str, output_path: Optional[str] = None) -> str:
    """Quick synthesis function"""
    stack = HybridVoiceStack()
    return stack.synthesize_sync(text, output_path)


def parse_language_tags(text: str) -> List[Dict]:
    """Parse language tags from text"""
    router = LanguageRouter()
    segments = router.parse_text(text)
    return [{'text': s.text, 'language': s.language.value, 'styles': s.style_tags} for s in segments]


if __name__ == "__main__":
    import asyncio
    
    # Test the hybrid stack
    test_texts = [
        "How you dey? I hope say you dey kampe!",
        "Good morning! [YO]Ẹ kú àárọ̀, ṣé ọ wà dáadáa?[/YO] How's everything?",
        "[NP]Wetin dey happen na? Abeg tell me o![/NP]",
        "Welcome to Sisi Lola's show! (laughs) Today we dey talk about tech.",
    ]
    
    async def test():
        stack = HybridVoiceStack()
        
        print("Available engines by language:")
        for lang, engine in stack.get_available_engines().items():
            print(f"  {lang}: {engine}")
        
        print("\nTesting synthesis...")
        for text in test_texts:
            print(f"\nInput: {text[:60]}...")
            segments = stack.router.parse_text(text)
            for seg in segments:
                print(f"  [{seg.language.value}] {seg.text[:40]}...")
            
            try:
                output = await stack.synthesize(text)
                print(f"  ✓ Output: {output}")
            except Exception as e:
                print(f"  ✗ Error: {e}")
    
    asyncio.run(test())
