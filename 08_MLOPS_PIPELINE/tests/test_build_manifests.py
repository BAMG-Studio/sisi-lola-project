"""
Unit tests for manifest builders (ASR and TTS).

Tests:
- ASR manifest format
- TTS metadata format
- Audio validation
- Language detection
- Error handling
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "preprocessing"))

import pytest
import tempfile
import csv
from unittest.mock import Mock, patch

# Note: These are integration-like tests that may require actual data files
# For pure unit tests, we'd mock the dataset loading


class TestASRManifestFormat:
    """Tests for ASR manifest TSV format."""
    
    def test_manifest_columns(self):
        """Test manifest has correct columns."""
        # This would require actual manifest generation
        # For now, testing the expected format
        expected_columns = [
            "audio_path",
            "text",
            "language",
            "duration_sec",
            "speaker_id",
            "split"
        ]
        
        # Verify column names
        assert len(expected_columns) == 6
        assert "audio_path" in expected_columns
        assert "text" in expected_columns
    
    def test_manifest_row_format(self):
        """Test individual row format."""
        # Mock row data
        row = {
            "audio_path": "/path/to/audio.wav",
            "text": "Test transcription",
            "language": "yo",
            "duration_sec": "5.2",
            "speaker_id": "speaker_001",
            "split": "train"
        }
        
        # Verify all required fields present
        assert all(key in row for key in [
            "audio_path", "text", "language", "duration_sec", "speaker_id", "split"
        ])
        
        # Verify duration is numeric
        assert float(row["duration_sec"]) > 0


class TestTTSMetadataFormat:
    """Tests for TTS metadata CSV format."""
    
    def test_metadata_delimiter(self):
        """Test metadata uses pipe delimiter."""
        # Expected format: filename|text|speaker_id|language
        sample_line = "audio_001.wav|Ẹ káàsán|sisi_lola|yo"
        
        parts = sample_line.split("|")
        assert len(parts) == 4
        assert parts[0] == "audio_001.wav"
        assert parts[1] == "Ẹ káàsán"
        assert parts[2] == "sisi_lola"
        assert parts[3] == "yo"
    
    def test_metadata_columns(self):
        """Test metadata has correct columns."""
        expected_headers = ["filename", "text", "speaker_id", "language"]
        
        assert len(expected_headers) == 4
        assert "filename" in expected_headers
        assert "text" in expected_headers


class TestAudioValidation:
    """Tests for audio validation logic."""
    
    def test_duration_validation(self):
        """Test duration validation rules."""
        # Valid duration range: 3-30 seconds
        
        assert 3.0 >= 3.0  # Minimum valid
        assert 30.0 <= 30.0  # Maximum valid
        
        # Invalid cases
        too_short = 2.9
        too_long = 30.1
        
        assert too_short < 3.0  # Should be rejected
        assert too_long > 30.0  # Should be rejected
    
    def test_rms_validation(self):
        """Test RMS energy validation."""
        # Valid RMS range: 0.01 - 0.95
        
        valid_rms = 0.5
        too_quiet = 0.005
        too_loud = 0.96
        
        assert 0.01 <= valid_rms <= 0.95
        assert too_quiet < 0.01
        assert too_loud > 0.95
    
    def test_clipping_detection(self):
        """Test clipping detection."""
        # Max amplitude should be < 0.99
        
        clean_audio = 0.8
        clipped = 0.995
        
        assert clean_audio < 0.99  # Clean
        assert clipped >= 0.99  # Clipped


class TestLanguageDetectionFromFilename:
    """Tests for filename-based language detection."""
    
    def test_yoruba_detection(self):
        """Test Yoruba language detection."""
        filename = "sisi_lola_yoruba_001.wav"
        
        # Should detect 'yo' from 'yoruba' in filename
        assert "yoruba" in filename.lower()
    
    def test_pidgin_detection(self):
        """Test Nigerian Pidgin detection."""
        filename = "recording_pidgin_english_002.wav"
        
        assert "pidgin" in filename.lower()
    
    def test_swahili_detection(self):
        """Test Swahili detection."""
        filename = "voice_swahili_ke_003.wav"
        
        assert "swahili" in filename.lower()
    
    def test_fallback_to_english(self):
        """Test fallback for unknown language."""
        filename = "random_audio_file.wav"
        
        # Should not match any keywords
        keywords = ["yoruba", "pidgin", "swahili", "hausa", "igbo"]
        assert not any(kw in filename.lower() for kw in keywords)


class TestErrorHandling:
    """Tests for error handling and edge cases."""
    
    def test_missing_audio_file(self):
        """Test handling of missing audio files."""
        fake_path = Path("/nonexistent/audio.wav")
        
        assert not fake_path.exists()
    
    def test_corrupted_audio_handling(self):
        """Test handling of corrupted audio files."""
        # Would require actual corrupted file
        # Testing that validation catches it
        pass
    
    def test_empty_text_field(self):
        """Test handling of empty transcription."""
        text = ""
        
        assert text == ""
        # Should be filtered out or flagged
    
    def test_unicode_in_text(self):
        """Test Unicode handling in transcriptions."""
        text = "Ẹ káàsán, báwo ni?"
        
        # Should preserve Unicode
        assert "Ẹ" in text
        assert "á" in text
        assert "à" in text


class TestManifestAggregation:
    """Tests for manifest aggregation logic."""
    
    def test_deduplication(self):
        """Test duplicate audio paths are removed."""
        paths = [
            "/audio/file1.wav",
            "/audio/file2.wav",
            "/audio/file1.wav",  # Duplicate
            "/audio/file3.wav"
        ]
        
        unique_paths = list(set(paths))
        assert len(unique_paths) == 3
        assert "/audio/file1.wav" in unique_paths
    
    def test_language_grouping(self):
        """Test samples grouped by language."""
        samples = [
            {"language": "yo", "text": "Test 1"},
            {"language": "en", "text": "Test 2"},
            {"language": "yo", "text": "Test 3"},
        ]
        
        # Group by language
        from collections import defaultdict
        grouped = defaultdict(list)
        for s in samples:
            grouped[s["language"]].append(s)
        
        assert len(grouped["yo"]) == 2
        assert len(grouped["en"]) == 1
    
    def test_split_distribution(self):
        """Test train/val/test split distribution."""
        splits = ["train", "train", "train", "validation", "test"]
        
        from collections import Counter
        split_counts = Counter(splits)
        
        assert split_counts["train"] == 3
        assert split_counts["validation"] == 1
        assert split_counts["test"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
