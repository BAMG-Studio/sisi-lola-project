"""
═══════════════════════════════════════════════════════════════════════════════
                         SISI LOLA METADATA SYSTEM
═══════════════════════════════════════════════════════════════════════════════
           AWS Glue / Apache Atlas Style Data Catalog & Lineage
═══════════════════════════════════════════════════════════════════════════════
"""

from .metadata_store import (
    MetadataStore,
    AssetMetadata,
    AssetType,
    AssetStatus,
    NigerianLanguage,
    generate_asset_id,
    register_video,
    register_audio,
    register_transcript,
    register_model
)

from .data_catalog import (
    DataCatalog,
    DataFormat,
    DatasetSchema,
    DataProfile,
    NigerianContentClassifier
)

from .lineage_tracker import (
    LineageTracker,
    TransformationType,
    TransformationRecord,
    ModelProvenance
)

__all__ = [
    # Metadata Store
    'MetadataStore',
    'AssetMetadata',
    'AssetType',
    'AssetStatus',
    'NigerianLanguage',
    'generate_asset_id',
    'register_video',
    'register_audio',
    'register_transcript',
    'register_model',
    
    # Data Catalog
    'DataCatalog',
    'DataFormat',
    'DatasetSchema',
    'DataProfile',
    'NigerianContentClassifier',
    
    # Lineage Tracker
    'LineageTracker',
    'TransformationType',
    'TransformationRecord',
    'ModelProvenance'
]
