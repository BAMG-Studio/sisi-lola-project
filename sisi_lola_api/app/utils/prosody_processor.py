"""
Prosody Processing for Natural Multi-Language Speech

This module adjusts prosody (rhythm, intonation, stress) to maintain
Sisi Lola's Nigerian vocal identity across all languages.

Key Features:
- Add Nigerian rhythm to foreign languages (Italian, Swahili, etc.)
- Preserve emotional tone across language switches
- Inject cultural particles naturally
- Maintain code-switching fluency
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ProsodyMarker:
    """A prosody modification instruction"""
    position: int
    marker_type: str  # 'particle', 'pause', 'emphasis', 'tone'
    value: str
    reason: str


class ProsodyProcessor:
    """
    Process text to maintain Nigerian prosody across languages.
    
    Strategy:
    1. Detect emotion/tone in source text
    2. Add Nigerian particles where culturally appropriate
    3. Adjust rhythm for foreign languages
    4. Preserve emphasis patterns
    """
    
    # Nigerian particles and their contexts
    PARTICLES = {
        'oh': {
            'position': 'end',
            'emotion': ['surprise', 'emphasis', 'concern'],
            'example': "This is amazing oh!"
        },
        'sha': {
            'position': 'end',
            'emotion': ['resignation', 'acceptance'],
            'example': "Just do it sha."
        },
        'sef': {
            'position': 'end',
            'emotion': ['frustration', 'disbelief'],
            'example': "You no know sef?"
        },
        'na': {
            'position': 'start',
            'emotion': ['emphasis', 'correction'],
            'example': "Na so the thing be!"
        },
        'o': {
            'position': 'end',
            'emotion': ['warning', 'advice'],
            'example': "Be careful o!"
        },
        'abi': {
            'position': 'end',
            'emotion': ['question', 'confirmation'],
            'example': "You understand, abi?"
        },
        'ehn': {
            'position': 'mid',
            'emotion': ['thinking', 'hesitation'],
            'example': "So, ehn, what should we do?"
        }
    }
    
    # Emotion indicators in text
    EMOTION_PATTERNS = {
        'excited': r'(!+|wow|amazing|incredible|fantastic)',
        'question': r'\?',
        'emphasis': r'(really|very|so|absolutely|definitely)',
        'concern': r'(careful|worry|problem|issue)',
        'casual': r'(just|like|you know|basically)'
    }
    
    def __init__(self, intensity: str = 'medium'):
        """
        Initialize prosody processor.
        
        Args:
            intensity: 'light', 'medium', 'heavy' - How much Nigerian flavor to add
        """
        self.intensity = intensity
        self.particle_frequency = {
            'light': 0.2,    # 20% of opportunities
            'medium': 0.4,   # 40% of opportunities
            'heavy': 0.6     # 60% of opportunities
        }
    
    def apply_nigerian_prosody(
        self,
        text: str,
        target_language: str,
        source_emotion: str = 'neutral'
    ) -> str:
        """
        Apply Nigerian prosody to text in any language.
        
        Args:
            text: Input text
            target_language: 'en', 'it', 'sw', 'yo', etc.
            source_emotion: Detected emotion from context
        
        Returns:
            Modified text with Nigerian prosodic markers
        
        Example:
            Input:  "Buongiorno! Come stai?" (Italian)
            Output: "Buongiorno oh! Come stai?"
            (^ Nigerian "oh" adds warmth and cultural flavor)
        """
        # Don't modify if already Nigerian language
        if target_language in ['yo', 'pcm', 'yo-en']:
            return text
        
        # Detect emotion from text if not provided
        if source_emotion == 'neutral':
            source_emotion = self._detect_emotion(text)
        
        # Apply prosody based on language and emotion
        modified_text = text
        
        # Add particles at appropriate positions
        if target_language in ['it', 'sw', 'ha', 'ig', 'fr', 'es']:
            modified_text = self._inject_particles(modified_text, source_emotion)
        
        # Adjust for English (lighter touch)
        elif target_language == 'en':
            modified_text = self._adjust_english_prosody(modified_text, source_emotion)
        
        return modified_text
    
    def _detect_emotion(self, text: str) -> str:
        """
        Detect emotion from text patterns.
        
        Returns: 'excited', 'question', 'emphasis', 'concern', 'casual', 'neutral'
        """
        text_lower = text.lower()
        
        for emotion, pattern in self.EMOTION_PATTERNS.items():
            if re.search(pattern, text_lower):
                return emotion
        
        return 'neutral'
    
    def _inject_particles(self, text: str, emotion: str) -> str:
        """
        Inject Nigerian particles into foreign language text.
        
        Strategy:
        - Add particles that match the emotional tone
        - Place at sentence boundaries (don't break grammar)
        - Keep frequency moderate (not every sentence)
        """
        import random
        
        # Check if we should add a particle (based on intensity)
        threshold = self.particle_frequency.get(self.intensity, 0.4)
        if random.random() > threshold:
            return text  # Skip this time
        
        # Find particles that match the emotion
        matching_particles = [
            particle for particle, info in self.PARTICLES.items()
            if emotion in info['emotion']
        ]
        
        if not matching_particles:
            # Fallback: use generic particles
            matching_particles = ['oh', 'sha']
        
        particle = random.choice(matching_particles)
        particle_info = self.PARTICLES[particle]
        
        # Inject particle at appropriate position
        if particle_info['position'] == 'end':
            # Add before final punctuation
            text = re.sub(r'([.!?])$', f' {particle}\\1', text)
            # If no punctuation, add at end
            if not re.search(r'[.!?]$', text):
                text = f"{text} {particle}!"
        
        elif particle_info['position'] == 'start':
            # Add at beginning
            text = f"{particle.capitalize()} {text}"
        
        elif particle_info['position'] == 'mid':
            # Add after first clause
            text = re.sub(r'(^[^,]+,)', f'\\1 {particle},', text)
        
        return text
    
    def _adjust_english_prosody(self, text: str, emotion: str) -> str:
        """
        Lightly adjust English prosody for Nigerian accent.
        
        More subtle than foreign language injection - just add cultural markers.
        """
        # Only add particles to high-emotion sentences
        if emotion in ['excited', 'concern', 'emphasis']:
            return self._inject_particles(text, emotion)
        
        # For questions, maybe add "abi?" or "shey?"
        if emotion == 'question' and '?' in text:
            if 'understand' in text.lower() or 'know' in text.lower():
                text = text.replace('?', ', abi?')
        
        return text
    
    def smooth_code_switching(
        self,
        segments: List[Tuple[str, str]]
    ) -> str:
        """
        Smooth transitions between code-switched segments.
        
        Args:
            segments: List of (text, language) tuples
        
        Returns:
            Smoothly connected text
        
        Example:
            Input:  [("Hello", "en"), ("Báwo ni?", "yo"), ("I'm good", "en")]
            Output: "Hello! Báwo ni? I'm good!"
            (^ Ensures natural flow with proper punctuation)
        """
        if not segments:
            return ""
        
        result = []
        for i, (text, lang) in enumerate(segments):
            text = text.strip()
            
            # Add connecting punctuation if missing
            if i > 0 and not result[-1][-1] in '.!?,;':
                # Previous segment needs punctuation
                if lang != segments[i-1][1]:
                    # Language switch - add stronger break
                    result[-1] += '!'
                else:
                    result[-1] += '.'
            
            result.append(text)
        
        return ' '.join(result)
    
    def adjust_for_tts(self, text: str, tts_engine: str = 'xtts') -> str:
        """
        Adjust text for optimal TTS pronunciation.
        
        Different TTS engines need different adjustments:
        - XTTS: Can handle particles naturally
        - ElevenLabs: May need phonetic spelling
        - Others: May need SSML tags
        """
        if tts_engine == 'elevenlabs':
            # ElevenLabs struggles with some particles
            # Phonetically respell them
            text = text.replace(' oh!', ' oh.')  # Less exclamatory
            text = text.replace(' sha.', ' sha.')
        
        elif tts_engine == 'xtts':
            # XTTS handles particles well, no changes needed
            pass
        
        # Remove excessive punctuation (confuses TTS)
        text = re.sub(r'!{2,}', '!', text)
        text = re.sub(r'\?{2,}', '?', text)
        
        # Ensure spaces after punctuation
        text = re.sub(r'([.!?,])([A-Z])', r'\1 \2', text)
        
        return text
    
    def generate_ssml(
        self,
        text: str,
        language: str,
        emotion: str = 'neutral',
        rate: float = 1.0,
        pitch: float = 1.0
    ) -> str:
        """
        Generate SSML (Speech Synthesis Markup Language) for advanced TTS control.
        
        Args:
            text: Input text
            language: Language code
            emotion: Emotion/style
            rate: Speech rate (0.5 = slow, 2.0 = fast)
            pitch: Pitch adjustment (0.5 = low, 2.0 = high)
        
        Returns:
            SSML-tagged text for TTS engines that support it
        """
        # Map emotions to SSML styles
        style_map = {
            'excited': 'enthusiastic',
            'question': 'curious',
            'concern': 'empathetic',
            'casual': 'chat',
            'neutral': 'default'
        }
        
        style = style_map.get(emotion, 'default')
        
        ssml = f'''
        <speak>
            <prosody rate="{rate}" pitch="{pitch}">
                <voice language="{language}" style="{style}">
                    {text}
                </voice>
            </prosody>
        </speak>
        '''.strip()
        
        return ssml


# Example usage and testing
if __name__ == "__main__":
    processor = ProsodyProcessor(intensity='medium')
    
    test_cases = [
        ("Buongiorno! Come stai?", "it", "excited"),
        ("I think this is a great idea.", "en", "emphasis"),
        ("Jambo rafiki! Habari yako?", "sw", "excited"),
        ("Do you understand what I'm saying?", "en", "question"),
        ("Bonjour! Comment allez-vous?", "fr", "excited"),
    ]
    
    print("🎭 Sisi Lola Prosody Processing Tests\n")
    for text, lang, emotion in test_cases:
        processed = processor.apply_nigerian_prosody(text, lang, emotion)
        print(f"Original:  {text}")
        print(f"Processed: {processed}")
        print(f"Language: {lang} | Emotion: {emotion}\n")
    
    # Test code-switching smoothing
    print("🔗 Code-Switching Smoothing Test\n")
    segments = [
        ("Hello everyone", "en"),
        ("Báwo ni", "yo"),
        ("How are you doing today", "en"),
        ("È rí gé oh", "yo")
    ]
    smoothed = processor.smooth_code_switching(segments)
    print(f"Segments: {segments}")
    print(f"Smoothed: {smoothed}\n")
