"""
Sisi Lola Voice Dataset Curator

A comprehensive system for sourcing, validating, and integrating 
African language speech datasets into the Sisi Lola voice training pipeline.

Components:
- curator_manifest_schema: Data classes for curated dataset manifests
- audio_processing_recipes: Audio conversion and processing utilities
- validate_curated_samples: Validation pipeline for audio samples

Usage:
    from ml_training.curator import CuratedDatasetManifest, CuratedSample
    from ml_training.curator.audio_processing_recipes import convert_any_to_sisi_format
"""

from .curator_manifest_schema import (
    CuratedDatasetManifest,
    CuratedSample,
    AudioSpecs,
    License,
    Language,
    Emotion,
    Dialect,
    QualityTier,
    create_manifest_from_directory,
    merge_manifests
)

__all__ = [
    "CuratedDatasetManifest",
    "CuratedSample", 
    "AudioSpecs",
    "License",
    "Language",
    "Emotion",
    "Dialect",
    "QualityTier",
    "create_manifest_from_directory",
    "merge_manifests"
]

__version__ = "1.0.0"
