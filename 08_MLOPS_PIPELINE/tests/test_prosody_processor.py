"""
Unit tests for prosody injection and SSML generation.

Tests:
- Nigerian particle injection
- Prosody intensity levels
- SSML generation
- Code-switching smoothing
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "sisi_lola_api"))

import pytest
from app.utils.prosody_processor import ProsodyProcessor
from app.utils.language_detector import LanguageSegment


@pytest.fixture
def processor():
    """Fixture to create prosody processor."""
    return ProsodyProcessor()


class TestNigerianProsody:
    """Tests for Nigerian prosody injection."""
    
    def test_light_prosody(self, processor):
        """Test light prosody intensity."""
        text = "How are you doing?"
        result = processor.apply_nigerian_prosody(text, intensity="light")
        
        # Should have some particles
        particles = ["o", "oh", "sha", "na", "abi", "sef"]
        assert any(p in result.lower() for p in particles)
        
        # Should be longer than original
        assert len(result) > len(text)
    
    def test_medium_prosody(self, processor):
        """Test medium prosody intensity."""
        text = "This is really great news!"
        result = processor.apply_nigerian_prosody(text, intensity="medium", emotion="happy")
        
        # Should have multiple particles
        particles = ["o", "oh", "sha", "na", "abi", "sef", "ehn"]
        particle_count = sum(1 for p in particles if p in result.lower())
        assert particle_count >= 2
    
    def test_heavy_prosody(self, processor):
        """Test heavy prosody intensity."""
        text = "I can't believe you did that!"
        result = processor.apply_nigerian_prosody(text, intensity="heavy", emotion="surprised")
        
        # Should have many particles
        particles = ["o", "oh", "sha", "na", "abi", "sef", "ehn"]
        particle_count = sum(1 for p in particles if p in result.lower())
        assert particle_count >= 3
    
    def test_no_prosody(self, processor):
        """Test with prosody disabled."""
        text = "This is a test."
        result = processor.apply_nigerian_prosody(text, intensity="none")
        
        # Should be unchanged
        assert result == text
    
    def test_emotion_particles(self, processor):
        """Test emotion-specific particles."""
        happy_text = "I'm so happy today!"
        happy_result = processor.apply_nigerian_prosody(happy_text, emotion="happy")
        
        # Should preferentially use happy particles
        assert any(p in happy_result for p in ["o", "oh", "sef"])


class TestCodeSwitchingSmoothing:
    """Tests for code-switching transition smoothing."""
    
    def test_smooth_yoruba_english(self, processor):
        """Test smoothing Yoruba-English transition."""
        segments = [
            LanguageSegment(text="Ẹ káàsán", language="yo", confidence=0.9, start=0, end=9),
            LanguageSegment(text="How are you?", language="en", confidence=0.8, start=10, end=22)
        ]
        
        result = processor.smooth_code_switching(segments)
        
        # Should add connectors
        assert any(connector in result for connector in [", you know,", ", sha,", ", o,"])
        
        # Should contain both original segments
        assert "Ẹ káàsán" in result
        assert "How are you" in result
    
    def test_smooth_pidgin_swahili(self, processor):
        """Test smoothing Pidgin-Swahili transition."""
        segments = [
            LanguageSegment(text="How far", language="pcm", confidence=0.7, start=0, end=7),
            LanguageSegment(text="Habari yako", language="sw", confidence=0.8, start=8, end=19)
        ]
        
        result = processor.smooth_code_switching(segments)
        
        # Should contain both segments
        assert "How far" in result
        assert "Habari yako" in result
        
        # Should be longer (connectors added)
        combined_length = len("How far") + len("Habari yako")
        assert len(result) > combined_length
    
    def test_single_segment_no_smoothing(self, processor):
        """Test that single segment doesn't get connectors."""
        segments = [
            LanguageSegment(text="Pure English text.", language="en", confidence=0.9, start=0, end=18)
        ]
        
        result = processor.smooth_code_switching(segments)
        
        # Should be unchanged
        assert result == "Pure English text."


class TestSSMLGeneration:
    """Tests for SSML markup generation."""
    
    def test_ssml_basic(self, processor):
        """Test basic SSML generation."""
        text = "Hello, how are you?"
        ssml = processor.generate_ssml(text)
        
        # Should be wrapped in speak tags
        assert ssml.startswith("<speak>")
        assert ssml.endswith("</speak>")
        
        # Should contain original text
        assert "Hello, how are you?" in ssml
    
    def test_ssml_with_prosody(self, processor):
        """Test SSML with prosody tags."""
        text = "This is exciting!"
        ssml = processor.generate_ssml(text, rate="fast", pitch="high")
        
        # Should have prosody tags
        assert "<prosody" in ssml
        assert 'rate="fast"' in ssml or 'rate="1.2"' in ssml
        assert 'pitch="high"' in ssml or 'pitch="+10%"' in ssml
    
    def test_ssml_with_emphasis(self, processor):
        """Test SSML with emphasis."""
        text = "This is VERY important!"
        ssml = processor.generate_ssml(text, emphasis_words=["VERY"])
        
        # Should have emphasis tags
        assert "<emphasis" in ssml
        assert "VERY" in ssml
    
    def test_ssml_with_breaks(self, processor):
        """Test SSML with pauses."""
        text = "First sentence. Second sentence."
        ssml = processor.generate_ssml(text, add_breaks=True)
        
        # Should have break tags
        assert "<break" in ssml


class TestTTSAdjustment:
    """Tests for TTS engine-specific adjustments."""
    
    def test_elevenlabs_adjustment(self, processor):
        """Test ElevenLabs-specific preprocessing."""
        text = "Ẹ káàsán, oh! How are you, sha?"
        adjusted = processor.adjust_for_tts(text, engine="elevenlabs")
        
        # Should preserve Nigerian particles
        assert "oh" in adjusted.lower()
        assert "sha" in adjusted.lower()
        
        # Should preserve Yoruba diacritics
        assert "Ẹ" in adjusted or "E" in adjusted
    
    def test_xtts_adjustment(self, processor):
        """Test XTTS-specific preprocessing."""
        text = "Hello! How are you???"
        adjusted = processor.adjust_for_tts(text, engine="xtts")
        
        # Should normalize punctuation
        assert adjusted.count("?") <= 2  # Max 2 question marks
    
    def test_unknown_engine_passthrough(self, processor):
        """Test unknown engine passes through unchanged."""
        text = "Test text."
        adjusted = processor.adjust_for_tts(text, engine="unknown")
        
        # Should be unchanged
        assert adjusted == text


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_empty_text(self, processor):
        """Test empty text handling."""
        result = processor.apply_nigerian_prosody("")
        assert result == ""
        
        ssml = processor.generate_ssml("")
        assert "<speak></speak>" in ssml
    
    def test_very_long_text(self, processor):
        """Test long text doesn't break."""
        text = "This is a test sentence. " * 100
        result = processor.apply_nigerian_prosody(text, intensity="light")
        
        # Should still work
        assert len(result) > len(text)
    
    def test_special_characters(self, processor):
        """Test special characters preserved."""
        text = "Price: $100! (50% off) #deal"
        result = processor.apply_nigerian_prosody(text, intensity="light")
        
        # Special chars should be preserved
        assert "$100" in result
        assert "#deal" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
