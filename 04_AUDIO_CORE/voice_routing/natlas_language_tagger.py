#!/usr/bin/env python3
"""
N-ATLaS LANGUAGE TAGGER
========================
Enhances N-ATLaS output with language tags for multi-voice routing.

This module:
1. Analyzes N-ATLaS responses for language content
2. Adds appropriate language tags ([EN], [YO], [PG], etc.)
3. Preserves prosody tags for voice synthesis

Example:
    Input:  "Hello! Báwo ni? How you dey today?"
    Output: "[EN]Hello![/EN] [YO]Báwo ni?[/YO] [PG]How you dey today?[/PG]"
"""

import re
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class LanguageCode(Enum):
    ENGLISH = "EN"
    YORUBA = "YO"
    PIDGIN = "PG"
    HAUSA = "HA"
    IGBO = "IG"
    MIXED = "MX"


@dataclass
class TextSegment:
    """A segment of text with detected language."""
    text: str
    language: LanguageCode
    confidence: float


class NatlasLanguageTagger:
    """
    Tags N-ATLaS output with language markers for multi-voice synthesis.
    
    The tagger identifies:
    - Yoruba words/phrases (with tonal marks and common words)
    - Nigerian Pidgin (characteristic markers like "dey", "wetin", "abeg")
    - Hausa words (with special characters)
    - Igbo words (with special characters)
    - English (default)
    
    Usage:
        tagger = NatlasLanguageTagger()
        tagged = tagger.tag_text("Hello! Báwo ni? How you dey?")
        # Returns: "[EN]Hello![/EN] [YO]Báwo ni?[/YO] [PG]How you dey?[/PG]"
    """
    
    # Yoruba indicators
    YORUBA_CHARS = set('ẹọṣẸỌṢàáèéìíòóùúÀÁÈÉÌÍÒÓÙÚ')
    YORUBA_WORDS = {
        'bawo', 'báwo', 'sebi', 'ṣebi', 'jọọ', 'jọ̀ọ́', 'aburo', 'àbúrò',
        'omo', 'ọmọ', 'egbon', 'ẹ̀gbọ́n', 'oṣe', 'daadaa', 'dáadáa',
        'ekaaro', 'ẹ káàrọ̀', 'ekaale', 'ẹ káàlẹ́', 'ekaabo', 'ẹ káàbọ̀',
        'odabo', 'ó dàbọ̀', 'ese', 'ẹ ṣe', 'beeni', 'bẹ́ẹ̀ ni', 'rara',
        'ki', 'kí', 'ni', 'nì', 'se', 'ṣe', 'wa', 'wá', 'lo', 'lọ',
        'mo', 'mi', 'o', 'ọ', 'ti', 'fun', 'fún', 'ati', 'àti',
        'sugbon', 'ṣùgbọ́n', 'tabi', 'tàbí', 'abi', 'àbí',
        'pelu', 'pẹ̀lú', 'ninu', 'nínú', 'lori', 'lórí',
        'ile', 'ilé', 'oja', 'ọjà', 'owo', 'owó', 'ise', 'iṣẹ́',
        'ojo', 'ọjọ́', 'odun', 'ọdún', 'osu', 'oṣù',
    }
    
    # Pidgin indicators
    PIDGIN_MARKERS = {
        'dey', 'wetin', 'wahala', 'abeg', 'sef', 'sha', 'shey', 'abi',
        'na', 'no be', 'e don', 'make', 'wey', 'sabi', 'chop', 'belle',
        'pikin', 'oya', 'sharpaly', 'jara', 'kpako', 'bobo', 'babe',
        'siddon', 'comot', 'yarn', 'gist', 'follow', 'carry', 'enter',
        'how far', 'how body', 'e no easy', 'i no know', 'i dey',
        'you dey', 'e dey', 'we dey', 'dem dey', 'no wahala',
        'na so', 'e sweet', 'e pain', 'omo', 'chai', 'haba',
        'o!', 'oh!', 'ehn', 'ehen', 'hmm', 'abii',
    }
    
    # Hausa indicators
    HAUSA_CHARS = set('ƙɗɓƘƊƁ')
    HAUSA_WORDS = {
        'sannu', 'yaya', 'lafiya', 'nagode', 'barka', 'sai', 'da',
        'ina', 'kai', 'ke', 'shi', 'ta', 'mu', 'ku', 'su',
    }
    
    # Igbo indicators
    IGBO_CHARS = set('ịọụṅỊỌỤṄ')
    IGBO_WORDS = {
        'kedu', 'ndewo', 'daalu', 'biko', 'nnọọ', 'nna', 'nne',
        'umu', 'nwa', 'ọ dị', 'ọ bụ', 'ọ na', 'gịnị', 'ebee',
    }
    
    def __init__(self, auto_tag: bool = True, min_segment_length: int = 2):
        """
        Initialize the tagger.
        
        Args:
            auto_tag: Whether to automatically add language tags
            min_segment_length: Minimum words to form a segment
        """
        self.auto_tag = auto_tag
        self.min_segment_length = min_segment_length
    
    def detect_word_language(self, word: str) -> Tuple[LanguageCode, float]:
        """
        Detect the language of a single word.
        
        Returns:
            Tuple of (language_code, confidence)
        """
        word_lower = word.lower().strip('.,!?;:"\'-')
        word_chars = set(word)
        
        # Check for Yoruba (high confidence with tonal marks)
        if word_chars & self.YORUBA_CHARS:
            return (LanguageCode.YORUBA, 0.95)
        if word_lower in self.YORUBA_WORDS:
            return (LanguageCode.YORUBA, 0.85)
        
        # Check for Hausa
        if word_chars & self.HAUSA_CHARS:
            return (LanguageCode.HAUSA, 0.95)
        if word_lower in self.HAUSA_WORDS:
            return (LanguageCode.HAUSA, 0.85)
        
        # Check for Igbo
        if word_chars & self.IGBO_CHARS:
            return (LanguageCode.IGBO, 0.95)
        if word_lower in self.IGBO_WORDS:
            return (LanguageCode.IGBO, 0.85)
        
        # Check for Pidgin
        if word_lower in self.PIDGIN_MARKERS:
            return (LanguageCode.PIDGIN, 0.80)
        
        # Default to English
        return (LanguageCode.ENGLISH, 0.50)
    
    def detect_phrase_language(self, phrase: str) -> Tuple[LanguageCode, float]:
        """
        Detect the primary language of a phrase.
        Uses weighted voting from individual words.
        """
        words = phrase.split()
        if not words:
            return (LanguageCode.ENGLISH, 0.50)
        
        # Count language votes
        votes: Dict[LanguageCode, float] = {}
        for word in words:
            lang, conf = self.detect_word_language(word)
            votes[lang] = votes.get(lang, 0) + conf
        
        # Check for Pidgin patterns (multi-word)
        phrase_lower = phrase.lower()
        for marker in ['how you dey', 'wetin dey', 'no wahala', 'e no easy', 
                       'i dey', 'you dey', 'e dey', 'na so']:
            if marker in phrase_lower:
                votes[LanguageCode.PIDGIN] = votes.get(LanguageCode.PIDGIN, 0) + 2.0
        
        # Get winner
        if not votes:
            return (LanguageCode.ENGLISH, 0.50)
        
        winner = max(votes.items(), key=lambda x: x[1])
        total = sum(votes.values())
        confidence = winner[1] / total if total > 0 else 0.50
        
        return (winner[0], confidence)
    
    def segment_text(self, text: str) -> List[TextSegment]:
        """
        Segment text by detected language.
        
        Attempts to group consecutive words of the same language.
        """
        # Preserve prosody tags by temporarily replacing them
        prosody_placeholder = {}
        prosody_pattern = r'\([^)]+\)'
        for i, match in enumerate(re.finditer(prosody_pattern, text)):
            placeholder = f"__PROSODY_{i}__"
            prosody_placeholder[placeholder] = match.group()
            text = text.replace(match.group(), placeholder, 1)
        
        # Split into sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        segments = []
        
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            # Detect language for the sentence
            lang, conf = self.detect_phrase_language(sentence)
            
            # Restore prosody tags
            for placeholder, original in prosody_placeholder.items():
                sentence = sentence.replace(placeholder, original)
            
            segments.append(TextSegment(
                text=sentence.strip(),
                language=lang,
                confidence=conf
            ))
        
        return segments
    
    def tag_text(self, text: str, merge_same_language: bool = True) -> str:
        """
        Add language tags to text.
        
        Args:
            text: Input text (may already have some tags)
            merge_same_language: Merge consecutive segments of same language
            
        Returns:
            Tagged text with [EN], [YO], [PG], etc. markers
        """
        # Check if already tagged
        if re.search(r'\[(EN|YO|PG|HA|IG|MX)\]', text):
            return text  # Already has tags
        
        segments = self.segment_text(text)
        
        if merge_same_language and len(segments) > 1:
            # Merge consecutive segments with same language
            merged = [segments[0]]
            for seg in segments[1:]:
                if seg.language == merged[-1].language:
                    merged[-1] = TextSegment(
                        text=merged[-1].text + " " + seg.text,
                        language=seg.language,
                        confidence=(merged[-1].confidence + seg.confidence) / 2
                    )
                else:
                    merged.append(seg)
            segments = merged
        
        # Build tagged output
        tagged_parts = []
        for seg in segments:
            tag = seg.language.value
            # Only tag non-English or when there are multiple languages
            if seg.language != LanguageCode.ENGLISH or len(segments) > 1:
                tagged_parts.append(f"[{tag}]{seg.text}[/{tag}]")
            else:
                tagged_parts.append(seg.text)
        
        return " ".join(tagged_parts)
    
    def process_natlas_output(self, response: str) -> str:
        """
        Process N-ATLaS response and add language tags.
        
        This is the main entry point for processing AI responses.
        """
        if not self.auto_tag:
            return response
        
        return self.tag_text(response)


# Convenience function
def tag_for_voice(text: str) -> str:
    """Quick function to add language tags to text."""
    tagger = NatlasLanguageTagger()
    return tagger.tag_text(text)


if __name__ == "__main__":
    # Test the tagger
    tagger = NatlasLanguageTagger()
    
    test_texts = [
        "Hello! How are you today?",
        "How you dey? I dey fine o!",
        "Ẹ káàbọ̀ sí ilé wa! Welcome to our home!",
        "Wetin dey happen? Báwo ni? Everything dey alright?",
        "Omo! (laughs) This thing sweet die! Ẹ ṣe púpọ̀ for coming!",
        "Na so life be. Ṣùgbọ́n we go dey alright sha.",
    ]
    
    print("=" * 60)
    print("N-ATLaS Language Tagger Test")
    print("=" * 60)
    
    for text in test_texts:
        print(f"\nInput:  {text}")
        tagged = tagger.tag_text(text)
        print(f"Output: {tagged}")
        
        # Show segments
        segments = tagger.segment_text(text)
        for seg in segments:
            print(f"  -> [{seg.language.value}] ({seg.confidence:.2f}) {seg.text}")
