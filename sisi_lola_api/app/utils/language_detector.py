"""
Multi-language and Code-Switching Detection for Sisi Lola

This module detects language switches in text, identifies code-switching patterns
(especially Yoruba-English mixing), and segments text for appropriate TTS handling.

Supports:
- Nigerian Pidgin English
- Yoruba-English code-switching ("Yorunglish")
- Multi-language detection (Italian, Swahili, Hausa, Igbo)
"""
from __future__ import annotations

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class LanguageSegment:
    """A segment of text in a specific language"""
    text: str
    language: str
    confidence: float
    start_pos: int
    end_pos: int
    is_code_switch: bool = False


class SisiLolaLanguageDetector:
    """
    Language detection optimized for Nigerian/African languages and code-switching.
    
    Uses rule-based detection with linguistic markers since many African languages
    lack robust pre-trained models for code-switching scenarios.
    """
    
    # Yoruba-specific markers
    YORUBA_PARTICLES = {
        'ni', 'ní', 'náà', 'naa', 'kò', 'ko', 'ṣe', 'se', 'ti',
        'abi', 'shey', 'ṣé', 'tí', 'fún', 'fun', 'wá', 'wa'
    }
    
    YORUBA_WORDS = {
        'bawo', 'báwo', 'ẹ', 'e', 'jọwọ', 'jowo', 'dákun', 'dakun',
        'ẹ̀', 'ọ̀', 'ṣe', 'pẹlẹ', 'pele', 'odabo', 'ọdabọ',
        'àláfíà', 'alafia', 'ẹkú', 'eku', 'òwe', 'owe'
    }
    
    # Nigerian Pidgin markers
    PIDGIN_MARKERS = {
        'wetin', 'dey', 'don', 'go', 'no', 'na', 'oh', 'sha', 'sef',
        'abeg', 'chai', 'wahala', 'sabi', 'kuku', 'make', 'comot',
        'small', 'plenty', 'chop', 'oga', 'madam', 'pikin', 'palaver'
    }
    
    # Swahili markers
    SWAHILI_MARKERS = {
        'habari', 'nzuri', 'asante', 'tafadhali', 'jambo', 'karibu',
        'kwaheri', 'ndiyo', 'hapana', 'pole', 'sawa', 'rafiki'
    }
    
    # Hausa markers
    HAUSA_MARKERS = {
        'sannu', 'yaya', 'lafiya', 'na', 'don', 'kai', 'gaskiya',
        'allah', 'wallahi', 'kuma', 'amma', 'lokacin'
    }
    
    # Igbo markers
    IGBO_MARKERS = {
        'kedu', 'ndewo', 'biko', 'daalụ', 'ọ', 'dị', 'nke', 'na',
        'mma', 'ọma', 'ezigbo', 'nwanne', 'nna', 'nne'
    }
    
    # Italian markers (for cross-lingual detection)
    ITALIAN_MARKERS = {
        'ciao', 'buongiorno', 'buonasera', 'grazie', 'prego', 'scusa',
        'per', 'con', 'sono', 'molto', 'bene', 'bella', 'bello'
    }
    
    def __init__(self):
        """Initialize the language detector"""
        self.language_markers = {
            'yo': self.YORUBA_PARTICLES | self.YORUBA_WORDS,
            'pcm': self.PIDGIN_MARKERS,  # Nigerian Pidgin (ISO 639-3: pcm)
            'sw': self.SWAHILI_MARKERS,
            'ha': self.HAUSA_MARKERS,
            'ig': self.IGBO_MARKERS,
            'it': self.ITALIAN_MARKERS
        }
    
    def detect_language(self, text: str) -> str:
        """
        Detect the primary language of a text segment.
        
        Returns:
            Language code: 'en', 'yo', 'pcm', 'sw', 'ha', 'ig', 'it', or 'mixed'
        """
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        
        if not words:
            return 'en'  # Default to English
        
        # Count markers for each language
        language_scores = {}
        for lang_code, markers in self.language_markers.items():
            score = sum(1 for word in words if word in markers)
            if score > 0:
                language_scores[lang_code] = score / len(words)
        
        # If no markers found, assume English
        if not language_scores:
            return 'en'
        
        # If multiple languages detected, it's code-switching
        if len(language_scores) > 1:
            # Check if Yoruba + English (Yorunglish)
            if 'yo' in language_scores:
                return 'yo-en'  # Yoruba-English code-switching
            elif 'pcm' in language_scores:
                return 'pcm'  # Nigerian Pidgin (inherently mixed)
            else:
                return 'mixed'
        
        # Return the highest scoring language
        return max(language_scores, key=language_scores.get)
    
    def detect_code_switching(self, text: str) -> List[LanguageSegment]:
        """
        Detect code-switching in text and return language segments.
        
        Example:
            Input: "Shey you understand this thing? È rí gé oh!"
            Output: [
                LanguageSegment("Shey you understand this thing?", "yo-en", 0.85, ...),
                LanguageSegment("È rí gé oh!", "yo", 0.95, ...)
            ]
        """
        # Split by sentence boundaries
        sentences = self._split_sentences(text)
        segments = []
        
        current_pos = 0
        for sentence in sentences:
            if not sentence.strip():
                continue
            
            lang = self.detect_language(sentence)
            confidence = self._calculate_confidence(sentence, lang)
            
            segment = LanguageSegment(
                text=sentence.strip(),
                language=lang,
                confidence=confidence,
                start_pos=current_pos,
                end_pos=current_pos + len(sentence),
                is_code_switch=(lang in ['yo-en', 'pcm', 'mixed'])
            )
            segments.append(segment)
            current_pos += len(sentence)
        
        return segments
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences, considering Nigerian speech patterns.
        
        Nigerian English often uses "oh", "sha", "na" as sentence enders.
        """
        # Split on standard punctuation
        sentences = re.split(r'([.!?]+\s+)', text)
        
        # Also split on Nigerian sentence enders followed by capital letter
        result = []
        for s in sentences:
            if not s.strip():
                continue
            # Split on Nigerian particles followed by punctuation/new sentence
            sub_sentences = re.split(r'\b(oh|sha|na|o)\b([!.]?\s+)(?=[A-Z])', s)
            result.extend([ss for ss in sub_sentences if ss.strip()])
        
        return result
    
    def _calculate_confidence(self, text: str, language: str) -> float:
        """
        Calculate confidence score for language detection.
        
        Based on:
        - Number of language-specific markers
        - Presence of diacritics (for Yoruba)
        - Length of text
        """
        words = re.findall(r'\b\w+\b', text.lower())
        if not words:
            return 0.5  # Low confidence for empty text
        
        marker_count = 0
        if language in self.language_markers:
            marker_count = sum(1 for word in words if word in self.language_markers[language])
        
        # Yoruba diacritics increase confidence
        if language in ['yo', 'yo-en']:
            diacritics = sum(1 for char in text if char in 'áàéèíìóòúùẹọṣ')
            marker_count += diacritics * 0.5
        
        # Calculate confidence (0.0 to 1.0)
        confidence = min(1.0, (marker_count / len(words)) * 2.0)
        
        # Boost confidence for known code-switching patterns
        if language == 'pcm':
            confidence = max(0.8, confidence)  # Pidgin is distinctive
        
        return round(confidence, 2)
    
    def requires_prosody_adjustment(self, segment: LanguageSegment) -> bool:
        """
        Determine if a segment needs Nigerian prosody adjustment.
        
        Italian, Swahili, etc. should be spoken with Nigerian rhythm/cadence.
        """
        # Foreign languages get Nigerian prosody
        if segment.language in ['it', 'sw', 'fr', 'es']:
            return True
        
        # Code-switched segments already have Nigerian prosody
        if segment.is_code_switch:
            return False
        
        # Pure English gets light Nigerian accent
        if segment.language == 'en' and segment.confidence > 0.8:
            return True
        
        return False


# Example usage and testing
if __name__ == "__main__":
    detector = SisiLolaLanguageDetector()
    
    test_cases = [
        "Hello darlings! Welcome to my show.",
        "Wetin dey happen? I don tell you say this thing no go work!",
        "Shey you understand this AI thing? È rí gé!",
        "Báwo ni? How are you doing today?",
        "Ciao bella! Come stai? I'm so excited!",
        "Jambo rafiki! We dey for Lagos today oh!",
    ]
    
    print("🧪 Sisi Lola Language Detection Tests\n")
    for text in test_cases:
        print(f"Input: {text}")
        segments = detector.detect_code_switching(text)
        for seg in segments:
            print(f"  → [{seg.language}] {seg.text} (confidence: {seg.confidence})")
        print()
