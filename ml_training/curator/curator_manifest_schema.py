"""
Sisi Lola Curated Dataset Manifest Schema

This module defines the schema for datasets curated by the Voice Dataset Curator GPT.
It provides validation, ingestion, and integration with the Sisi Lola training pipeline.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from enum import Enum
from datetime import datetime
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# Enums
# =============================================================================

class License(str, Enum):
    """Supported license types"""
    CC0 = "CC0-1.0"
    MIT = "MIT"
    CC_BY = "CC-BY-4.0"
    CC_BY_SA = "CC-BY-SA-4.0"
    APACHE = "Apache-2.0"
    RESEARCH = "research-only"
    UNKNOWN = "unknown"


class QualityTier(str, Enum):
    """Dataset quality tiers"""
    STUDIO = "studio"
    FILTERED = "filtered"
    CROWDSOURCED = "crowdsourced"
    RESEARCH = "research"
    RAW = "raw"


class Language(str, Enum):
    """Supported languages"""
    YORUBA = "yoruba"
    HAUSA = "hausa"
    IGBO = "igbo"
    NIGERIAN_PIDGIN = "nigerian_pidgin"
    NIGERIAN_ENGLISH = "nigerian_english"
    SWAHILI = "swahili"
    ZULU = "zulu"
    XHOSA = "xhosa"
    TWI = "twi"
    LINGALA = "lingala"
    AMHARIC = "amharic"
    ENGLISH = "english"
    MIXED = "mixed"


class Emotion(str, Enum):
    """Emotional states in audio"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    EXCITED = "excited"
    SAD = "sad"
    ANGRY = "angry"
    CALM = "calm"
    PLAYFUL = "playful"
    PROFESSIONAL = "professional"
    WHISPERING = "whispering"
    LAUGHING = "laughing"


class Dialect(str, Enum):
    """Nigerian dialects"""
    LAGOS = "lagos"
    IBADAN = "ibadan"
    OYO = "oyo"
    EKITI = "ekiti"
    KANO = "kano"
    KADUNA = "kaduna"
    ENUGU = "enugu"
    OWERRI = "owerri"
    PORT_HARCOURT = "port_harcourt"
    GENERAL = "general"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class AudioSpecs:
    """Audio technical specifications"""
    sample_rate: int = 22050
    channels: int = 1
    format: str = "wav"
    bit_depth: int = 16
    
    def to_dict(self) -> Dict:
        return {
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "format": self.format,
            "bit_depth": self.bit_depth
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AudioSpecs":
        return cls(**data)


@dataclass
class CuratedSample:
    """A single curated audio sample"""
    # Required fields
    audio_path: str
    language: str
    duration: float
    
    # Content
    text: Optional[str] = None
    translation: Optional[str] = None  # English translation if applicable
    
    # Quality metrics
    quality_score: float = 0.0  # 0.0 to 1.0
    is_clean: bool = True
    snr_estimate: Optional[float] = None  # Signal-to-noise ratio
    
    # Metadata
    speaker_id: Optional[str] = None
    speaker_gender: str = "female"  # Sisi Lola preference
    speaker_age_range: str = "28-40"  # Sisi Lola persona
    emotion: str = "neutral"
    dialect: str = "general"
    
    # Source tracking
    source_dataset: Optional[str] = None
    source_url: Optional[str] = None
    original_id: Optional[str] = None
    
    # Sisi Lola compatibility
    sisi_compatible: bool = False
    persona_match_score: float = 0.0  # How well it matches Sisi Lola's persona
    
    def to_dict(self) -> Dict:
        return {
            "audio_path": self.audio_path,
            "text": self.text,
            "translation": self.translation,
            "language": self.language,
            "duration": self.duration,
            "quality_score": self.quality_score,
            "is_clean": self.is_clean,
            "snr_estimate": self.snr_estimate,
            "speaker_id": self.speaker_id,
            "speaker_gender": self.speaker_gender,
            "speaker_age_range": self.speaker_age_range,
            "emotion": self.emotion,
            "dialect": self.dialect,
            "source_dataset": self.source_dataset,
            "source_url": self.source_url,
            "original_id": self.original_id,
            "sisi_compatible": self.sisi_compatible,
            "persona_match_score": self.persona_match_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CuratedSample":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class CuratedDatasetManifest:
    """
    Complete manifest for a curated dataset.
    
    This is the primary output format from the Voice Dataset Curator GPT.
    """
    # Identity
    dataset_id: str
    name: str
    version: str = "1.0.0"
    
    # Source
    curator: str = "voice_dataset_curator_gpt"
    source_datasets: List[str] = field(default_factory=list)
    
    # Content
    language: str = "yoruba"
    dialect: str = "lagos"
    samples: List[CuratedSample] = field(default_factory=list)
    
    # Technical specs
    audio_specs: AudioSpecs = field(default_factory=AudioSpecs)
    
    # Licensing
    license: str = "CC-BY-SA-4.0"
    commercial_ready: bool = True
    attribution_required: bool = True
    attribution_text: str = ""
    
    # Quality summary
    total_duration_hours: float = 0.0
    total_samples: int = 0
    average_quality_score: float = 0.0
    sisi_compatible_count: int = 0
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    notes: str = ""
    
    # Sisi Lola specific
    target_persona: str = "sisi_lola"
    recommended_use: str = "voice_training"  # or "personality_training", "both"
    
    def to_dict(self) -> Dict:
        return {
            "dataset_id": self.dataset_id,
            "name": self.name,
            "version": self.version,
            "curator": self.curator,
            "source_datasets": self.source_datasets,
            "language": self.language,
            "dialect": self.dialect,
            "samples": [s.to_dict() for s in self.samples],
            "audio_specs": self.audio_specs.to_dict(),
            "license": self.license,
            "commercial_ready": self.commercial_ready,
            "attribution_required": self.attribution_required,
            "attribution_text": self.attribution_text,
            "total_duration_hours": self.total_duration_hours,
            "total_samples": self.total_samples,
            "average_quality_score": self.average_quality_score,
            "sisi_compatible_count": self.sisi_compatible_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "notes": self.notes,
            "target_persona": self.target_persona,
            "recommended_use": self.recommended_use
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CuratedDatasetManifest":
        # Parse samples
        samples = [CuratedSample.from_dict(s) for s in data.get("samples", [])]
        
        # Parse audio specs
        audio_specs = AudioSpecs.from_dict(data.get("audio_specs", {}))
        
        # Create manifest
        manifest = cls(
            dataset_id=data["dataset_id"],
            name=data["name"],
            version=data.get("version", "1.0.0"),
            curator=data.get("curator", "voice_dataset_curator_gpt"),
            source_datasets=data.get("source_datasets", []),
            language=data.get("language", "yoruba"),
            dialect=data.get("dialect", "lagos"),
            samples=samples,
            audio_specs=audio_specs,
            license=data.get("license", "CC-BY-SA-4.0"),
            commercial_ready=data.get("commercial_ready", True),
            attribution_required=data.get("attribution_required", True),
            attribution_text=data.get("attribution_text", ""),
            total_duration_hours=data.get("total_duration_hours", 0.0),
            total_samples=data.get("total_samples", len(samples)),
            average_quality_score=data.get("average_quality_score", 0.0),
            sisi_compatible_count=data.get("sisi_compatible_count", 0),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            notes=data.get("notes", ""),
            target_persona=data.get("target_persona", "sisi_lola"),
            recommended_use=data.get("recommended_use", "voice_training")
        )
        
        return manifest
    
    def save(self, path: str) -> str:
        """Save manifest to JSON file"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        logger.info(f"Saved manifest to {path}")
        return path
    
    @classmethod
    def load(cls, path: str) -> "CuratedDatasetManifest":
        """Load manifest from JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
    
    def calculate_stats(self) -> None:
        """Recalculate statistics from samples"""
        self.total_samples = len(self.samples)
        self.total_duration_hours = sum(s.duration for s in self.samples) / 3600
        
        if self.samples:
            self.average_quality_score = sum(s.quality_score for s in self.samples) / len(self.samples)
            self.sisi_compatible_count = sum(1 for s in self.samples if s.sisi_compatible)
    
    def get_sisi_compatible_samples(self) -> List[CuratedSample]:
        """Get only Sisi Lola compatible samples"""
        return [s for s in self.samples if s.sisi_compatible]
    
    def get_samples_by_language(self, language: str) -> List[CuratedSample]:
        """Filter samples by language"""
        return [s for s in self.samples if s.language == language]
    
    def get_samples_by_emotion(self, emotion: str) -> List[CuratedSample]:
        """Filter samples by emotion"""
        return [s for s in self.samples if s.emotion == emotion]
    
    def validate(self) -> Dict:
        """Validate the manifest"""
        errors = []
        warnings = []
        
        # Check required fields
        if not self.dataset_id:
            errors.append("Missing dataset_id")
        if not self.name:
            errors.append("Missing name")
        
        # Check samples
        if not self.samples:
            warnings.append("No samples in manifest")
        
        # Check audio specs
        if self.audio_specs.sample_rate != 22050:
            warnings.append(f"Non-standard sample rate: {self.audio_specs.sample_rate} (expected 22050)")
        
        # Check licensing for commercial use
        non_commercial_licenses = ["research-only", "CC-BY-NC", "unknown"]
        if self.commercial_ready and any(nc in self.license for nc in non_commercial_licenses):
            errors.append(f"Commercial flag set but license is restrictive: {self.license}")
        
        # Validate each sample
        for i, sample in enumerate(self.samples):
            if sample.duration < 1:
                warnings.append(f"Sample {i} too short: {sample.duration}s")
            if sample.duration > 120:
                warnings.append(f"Sample {i} too long: {sample.duration}s")
            if not sample.audio_path:
                errors.append(f"Sample {i} missing audio_path")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }


# =============================================================================
# Factory Functions
# =============================================================================

def create_manifest_from_directory(
    audio_dir: str,
    dataset_id: str,
    name: str,
    language: str = "yoruba",
    dialect: str = "lagos",
    license: str = "CC-BY-SA-4.0"
) -> CuratedDatasetManifest:
    """
    Create a manifest from a directory of audio files.
    
    Looks for .wav files and corresponding .txt transcripts.
    """
    import librosa
    
    audio_path = Path(audio_dir)
    samples = []
    
    for wav_file in sorted(audio_path.glob("*.wav")):
        txt_file = wav_file.with_suffix('.txt')
        
        # Get duration
        try:
            duration = librosa.get_duration(path=str(wav_file))
        except Exception as e:
            logger.warning(f"Could not get duration for {wav_file}: {e}")
            continue
        
        # Get transcript
        text = ""
        if txt_file.exists():
            text = txt_file.read_text(encoding='utf-8').strip()
        
        # Create sample
        sample = CuratedSample(
            audio_path=str(wav_file.name),
            text=text,
            language=language,
            dialect=dialect,
            duration=duration,
            quality_score=0.7,  # Default, should be validated
            sisi_compatible=3 <= duration <= 60  # Duration check
        )
        samples.append(sample)
    
    # Create manifest
    manifest = CuratedDatasetManifest(
        dataset_id=dataset_id,
        name=name,
        language=language,
        dialect=dialect,
        samples=samples,
        license=license,
        commercial_ready=license not in ["research-only", "unknown"]
    )
    
    manifest.calculate_stats()
    
    return manifest


def merge_manifests(manifests: List[CuratedDatasetManifest]) -> CuratedDatasetManifest:
    """Merge multiple manifests into one"""
    if not manifests:
        raise ValueError("No manifests to merge")
    
    # Use first manifest as base
    merged = CuratedDatasetManifest(
        dataset_id=f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        name="Merged Dataset",
        source_datasets=[m.dataset_id for m in manifests]
    )
    
    # Collect all samples
    all_samples = []
    all_sources = set()
    
    for manifest in manifests:
        all_samples.extend(manifest.samples)
        all_sources.update(manifest.source_datasets)
        all_sources.add(manifest.dataset_id)
    
    merged.samples = all_samples
    merged.source_datasets = list(all_sources)
    merged.calculate_stats()
    
    return merged


# =============================================================================
# Example Usage
# =============================================================================

if __name__ == "__main__":
    # Example: Create a sample curated manifest
    sample = CuratedSample(
        audio_path="yoruba_sample_001.wav",
        text="Ẹ káàbọ̀! Mo ń bọ̀ láti Lagos",
        translation="Welcome! I'm coming from Lagos",
        language="yoruba",
        dialect="lagos",
        duration=15.5,
        quality_score=0.85,
        is_clean=True,
        speaker_gender="female",
        speaker_age_range="28-40",
        emotion="excited",
        source_dataset="BibleTTS",
        sisi_compatible=True,
        persona_match_score=0.9
    )
    
    manifest = CuratedDatasetManifest(
        dataset_id="curated_yoruba_v1",
        name="Curated Yoruba Voice Samples for Sisi Lola",
        language="yoruba",
        dialect="lagos",
        samples=[sample],
        license="CC-BY-SA-4.0",
        commercial_ready=True,
        attribution_required=True,
        attribution_text="BibleTTS Dataset (CC-BY-SA 4.0)",
        notes="High-quality female Yoruba samples matching Sisi Lola persona"
    )
    
    manifest.calculate_stats()
    
    # Validate
    validation = manifest.validate()
    print("Validation:", validation)
    
    # Save
    manifest.save("example_manifest.json")
    
    # Display
    print(json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False))
