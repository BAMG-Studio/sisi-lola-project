"""
Unit tests for language detection and code-switching functionality.

Tests:
- Pure language detection (Yoruba, Pidgin, Swahili, etc.)
- Code-switching detection (Yoruba-English, Pidgin-English)
- Confidence scoring
- Edge cases (empty, mixed, unknown)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "sisi_lola_api"))

import pytest
from app.utils.language_detector import SisiLolaLanguageDetector, LanguageSegment


@pytest.fixture
def detector():
    """Fixture to create detector instance."""
    return SisiLolaLanguageDetector()


class TestPureLanguageDetection:
    """Tests for single-language inputs."""
    
    def test_pure_yoruba(self, detector):
        """Test pure Yoruba detection."""
        text = "Ẹ káàsán, báwo ni? Mo fẹ́ràn rẹ."
        segments = detector.detect_code_switching(text)
        
        assert len(segments) == 1
        assert segments[0].language == "yo"
        assert segments[0].confidence > 0.8
        assert not detector.requires_prosody_adjustment(segments)
    
    def test_pure_nigerian_pidgin(self, detector):
        """Test Nigerian Pidgin detection."""
        text = "How far my guy? I dey kampe o. Wetin dey happen?"
        segments = detector.detect_code_switching(text)
        
        assert len(segments) == 1
        assert segments[0].language == "pcm"
        assert segments[0].confidence > 0.7
    
    def test_pure_swahili(self, detector):
        """Test Swahili detection."""
        text = "Habari yako? Mimi ni mzuri sana, asante."
        segments = detector.detect_code_switching(text)
        
        assert len(segments) == 1
        assert segments[0].language == "sw"
        assert segments[0].confidence > 0.6
    
    def test_pure_hausa(self, detector):
        """Test Hausa detection."""
        text = "Sannu, yaya kake? Na gode sosai."
        segments = detector.detect_code_switching(text)
        
        assert len(segments) == 1
        assert segments[0].language == "ha"
        assert segments[0].confidence > 0.6
    
    def test_pure_igbo(self, detector):
        """Test Igbo detection."""
        text = "Nnọọ, kedu ka ị mere? Daalụ nke ọma."
        segments = detector.detect_code_switching(text)
        
        assert len(segments) == 1
        assert segments[0].language == "ig"
        assert segments[0].confidence > 0.6
    
    def test_pure_english(self, detector):
        """Test English fallback."""
        text = "Hello, how are you? I'm doing great today."
        segments = detector.detect_code_switching(text)
        
        assert len(segments) == 1
        assert segments[0].language == "en"


class TestCodeSwitching:
    """Tests for mixed-language inputs."""
    
    def test_yoruba_english_switch(self, detector):
        """Test Yoruba-English code-switching (Yorunglish)."""
        text = "Ẹ káàsán! My name is Sisi Lola, mo wá láti Nigeria."
        segments = detector.detect_code_switching(text)
        
        # Should detect multiple segments
        assert len(segments) > 1
        
        # Should have both Yoruba and English
        languages = {seg.language for seg in segments}
        assert "yo" in languages
        assert "en" in languages
        
        # Should require prosody adjustment for English part
        assert detector.requires_prosody_adjustment(segments)
    
    def test_pidgin_english_switch(self, detector):
        """Test Pidgin-English code-switching."""
        text = "I dey come now. Please wait for me, abeg."
        segments = detector.detect_code_switching(text)
        
        # Should detect Pidgin
        languages = {seg.language for seg in segments}
        assert "pcm" in languages
    
    def test_multiple_switches(self, detector):
        """Test multiple rapid switches."""
        text = "Ẹ káàsán! Good morning everyone, mo dúpẹ́ púpọ̀. Thank you so much!"
        segments = detector.detect_code_switching(text)
        
        # Should detect at least 2 segments
        assert len(segments) >= 2
        
        # Should have mixed languages
        languages = {seg.language for seg in segments}
        assert len(languages) > 1


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_string(self, detector):
        """Test empty input."""
        segments = detector.detect_code_switching("")
        
        assert len(segments) == 1
        assert segments[0].language == "en"  # Default fallback
        assert segments[0].text == ""
    
    def test_whitespace_only(self, detector):
        """Test whitespace-only input."""
        segments = detector.detect_code_switching("   \n\t  ")
        
        assert len(segments) == 1
        assert segments[0].language == "en"
    
    def test_numbers_only(self, detector):
        """Test numeric input."""
        segments = detector.detect_code_switching("123 456 789")
        
        assert len(segments) == 1
        # Should fallback to English
        assert segments[0].language == "en"
    
    def test_mixed_scripts(self, detector):
        """Test mixed scripts (Latin + diacritics)."""
        text = "Àdúrà pẹ̀lú prayer fun success"
        segments = detector.detect_code_switching(text)
        
        # Should detect Yoruba (diacritics) and English
        languages = {seg.language for seg in segments}
        assert "yo" in languages


class TestConfidenceScoring:
    """Tests for confidence score accuracy."""
    
    def test_high_confidence_yoruba(self, detector):
        """High confidence for text with many Yoruba markers."""
        text = "Ẹ káàsán, ẹ káàbọ̀, mo dúpẹ́ lọ́wọ́ rẹ, ẹ ṣé o."
        segments = detector.detect_code_switching(text)
        
        # First segment should be Yoruba with high confidence
        yoruba_seg = [s for s in segments if s.language == "yo"][0]
        assert yoruba_seg.confidence > 0.9
    
    def test_low_confidence_ambiguous(self, detector):
        """Lower confidence for ambiguous text."""
        text = "I want to go home."  # Could be English or Pidgin
        segments = detector.detect_code_switching(text)
        
        # Should have lower confidence
        assert segments[0].confidence < 0.9


class TestProsodyRequirements:
    """Tests for prosody adjustment detection."""
    
    def test_requires_prosody_for_foreign(self, detector):
        """Should require prosody for foreign language with Nigerian context."""
        text = "Buongiorno! Come stai?"  # Italian
        segments = detector.detect_code_switching(text)
        
        # If we detect this as foreign (not yo/pcm/ig/ha), prosody needed
        if segments[0].language not in ["yo", "pcm", "ig", "ha", "sw"]:
            assert detector.requires_prosody_adjustment(segments)
    
    def test_no_prosody_for_native(self, detector):
        """Should NOT require prosody for pure Nigerian languages."""
        text = "Ẹ káàsán, báwo ni?"
        segments = detector.detect_code_switching(text)
        
        assert not detector.requires_prosody_adjustment(segments)
    
    def test_prosody_for_code_switch(self, detector):
        """Should require prosody for code-switched Nigerian + foreign."""
        text = "Ẹ káàsán! Ciao bella, how are you?"
        segments = detector.detect_code_switching(text)
        
        # Should require prosody for foreign parts
        assert detector.requires_prosody_adjustment(segments)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
