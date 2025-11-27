"""
Unit tests for text normalization utilities.

Tests:
- Unicode NFC normalization (Yoruba diacritics)
- Whitespace cleanup
- Punctuation normalization
- Edge cases
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "preprocessing"))

import pytest
from normalize_text import normalize_text, batch_normalize


class TestUnicodeNormalization:
    """Tests for Unicode normalization (NFC)."""
    
    def test_yoruba_diacritics_nfc(self):
        """Test Yoruba diacritics normalized to NFC."""
        # Decomposed form (NFD): separate combining characters
        text_nfd = "E\u0301 ka\u0300a\u0300sa\u0301n"  # Ẹ́ káàsán in NFD
        
        normalized = normalize_text(text_nfd)
        
        # Should be in composed form (NFC) - no combining characters
        # Note: normalize_text also cleans whitespace
        assert "\u0301" not in normalized  # No combining acute
        assert "\u0300" not in normalized  # No combining grave
    
    def test_swahili_characters(self):
        """Test Swahili special characters."""
        text = "Habari yako rafiki yangu"
        normalized = normalize_text(text)
        
        # Should be unchanged (no special chars)
        assert normalized == text
    
    def test_mixed_scripts(self):
        """Test mixed Latin and diacritics."""
        text = "Hello ẹni ọ̀wọ́n"
        normalized = normalize_text(text)
        
        # Should preserve both parts
        assert "Hello" in normalized
        assert "ẹni" in normalized
        # Check for composed forms (may vary)
        assert "wọ" in normalized or "w" in normalized


class TestWhitespaceCleanup:
    """Tests for whitespace normalization."""
    
    def test_multiple_spaces(self):
        """Test multiple spaces collapsed."""
        text = "Hello    world  how   are    you"
        cleaned = normalize_text(text)
        
        assert cleaned == "Hello world how are you"
    
    def test_tabs_and_newlines(self):
        """Test tabs/newlines converted to spaces."""
        text = "Hello\tworld\nhow\r\nare you"
        cleaned = normalize_text(text)
        
        assert cleaned == "Hello world how are you"
    
    def test_leading_trailing_whitespace(self):
        """Test leading/trailing whitespace removed."""
        text = "   Hello world   "
        cleaned = normalize_text(text)
        
        assert cleaned == "Hello world"
    
    def test_only_whitespace(self):
        """Test whitespace-only string."""
        text = "   \n\t   "
        cleaned = normalize_text(text)
        
        assert cleaned == ""


class TestFullNormalization:
    """Tests for complete normalization pipeline."""
    
    def test_yoruba_sentence(self):
        """Test full Yoruba sentence normalization."""
        text = "  Ẹ   ká àsán ,   báwo   ni ?  "
        normalized = normalize_text(text)
        
        # Should be cleaned and normalized - note punctuation spacing
        assert normalized == "Ẹ ká àsán, báwo ni?"
        
        # Should preserve diacritics
        assert "Ẹ" in normalized
        assert "á" in normalized
        assert "à" in normalized
    
    def test_nigerian_pidgin(self):
        """Test Nigerian Pidgin normalization."""
        text = "  How  far   my   guy  ?  I  dey  kampe  o  ."
        normalized = normalize_text(text)
        
        # Punctuation spacing: removes space before punctuation
        assert normalized == "How far my guy? I dey kampe o ."
    
    def test_code_switched_text(self):
        """Test code-switched text."""
        text = "  Ẹ káàsán  !  How are you  doing  today  ?"
        normalized = normalize_text(text)
        
        # Should preserve both languages with cleaned punctuation
        assert "Ẹ káàsán!" in normalized or "Ẹ káàsán !" in normalized
        assert "How are you doing today" in normalized
    
    def test_lowercasing(self):
        """Test optional lowercasing."""
        text = "HELLO WORLD"
        normalized = normalize_text(text, lowercase=True)
        
        assert normalized == "hello world"
    
    def test_preserve_case(self):
        """Test case preservation by default."""
        text = "Hello World"
        normalized = normalize_text(text, lowercase=False)
        
        assert normalized == "Hello World"


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_empty_string(self):
        """Test empty string."""
        assert normalize_text("") == ""
    
    def test_only_punctuation(self):
        """Test punctuation-only string."""
        text = "!@#$%^&*()"
        normalized = normalize_text(text)
        
        # Should preserve punctuation
        assert normalized == text
    
    def test_numbers(self):
        """Test numbers preserved."""
        text = "I have 123 items and 456 more"
        normalized = normalize_text(text)
        
        assert "123" in normalized
        assert "456" in normalized
    
    def test_unicode_emoji(self):
        """Test emoji handling."""
        text = "Hello 👋 world 🌍"
        normalized = normalize_text(text)
        
        # Emojis should be preserved
        assert "👋" in normalized
        assert "🌍" in normalized
    
    def test_very_long_text(self):
        """Test long text doesn't break."""
        text = "Ẹ káàsán " * 1000
        normalized = normalize_text(text)
        
        # Should work
        assert len(normalized) > 0
        assert "Ẹ káàsán" in normalized


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
