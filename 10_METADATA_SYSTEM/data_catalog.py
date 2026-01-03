#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                    DATA CATALOG & DISCOVERY SERVICE
═══════════════════════════════════════════════════════════════════════════════
                    AWS Glue-style Data Catalog for Sisi Lola
═══════════════════════════════════════════════════════════════════════════════

Provides:
- Data cataloging across all storage locations
- Schema discovery and management
- Data profiling and statistics
- Lineage visualization
- Integration with training pipelines
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from enum import Enum

from metadata_store import (
    MetadataStore,
    AssetMetadata,
    AssetType,
    AssetStatus,
    NigerianLanguage,
    generate_asset_id
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataFormat(Enum):
    """Supported data formats."""
    # Audio
    WAV = "wav"
    MP3 = "mp3"
    FLAC = "flac"
    M4A = "m4a"
    
    # Video
    MP4 = "mp4"
    WEBM = "webm"
    MOV = "mov"
    
    # Image
    PNG = "png"
    JPG = "jpg"
    WEBP = "webp"
    
    # Text
    TXT = "txt"
    JSON = "json"
    JSONL = "jsonl"
    CSV = "csv"
    
    # Model
    SAFETENSORS = "safetensors"
    PT = "pt"
    ONNX = "onnx"


@dataclass
class DatasetSchema:
    """Schema definition for a dataset."""
    name: str
    fields: List[Dict[str, Any]]
    primary_key: str = None
    created_at: datetime = field(default_factory=datetime.now)
    version: str = "1.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'fields': self.fields,
            'primary_key': self.primary_key,
            'created_at': self.created_at.isoformat(),
            'version': self.version
        }


@dataclass
class DataProfile:
    """Statistical profile of a dataset."""
    total_records: int
    total_size_bytes: int
    field_stats: Dict[str, Dict[str, Any]]
    quality_metrics: Dict[str, float]
    nigerian_content_ratio: float
    language_distribution: Dict[str, float]
    profiled_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_records': self.total_records,
            'total_size_bytes': self.total_size_bytes,
            'field_stats': self.field_stats,
            'quality_metrics': self.quality_metrics,
            'nigerian_content_ratio': self.nigerian_content_ratio,
            'language_distribution': self.language_distribution,
            'profiled_at': self.profiled_at.isoformat()
        }


class DataCatalog:
    """
    Central data catalog for discovering and managing datasets.
    """
    
    def __init__(self, metadata_store: MetadataStore):
        self.store = metadata_store
        self.schemas: Dict[str, DatasetSchema] = {}
        self.profiles: Dict[str, DataProfile] = {}
        
        # Nigerian content keywords for auto-detection
        self.nigerian_keywords = [
            'nigeria', 'lagos', 'abuja', 'naija', 'jollof', 'ankara',
            'pidgin', 'yoruba', 'hausa', 'igbo', 'afrobeats', 'nollywood',
            'agege', 'aso-ebi', 'suya', 'egusi', 'eba', 'amala',
            'danfo', 'okada', 'wahala', 'sha', 'abeg', 'wetin'
        ]
    
    def discover_local_data(
        self,
        root_path: str,
        patterns: List[str] = None,
        recursive: bool = True
    ) -> List[AssetMetadata]:
        """
        Discover and catalog data from local filesystem.
        """
        root = Path(root_path)
        patterns = patterns or ["*.mp4", "*.wav", "*.mp3", "*.txt", "*.json"]
        
        discovered = []
        
        for pattern in patterns:
            if recursive:
                files = root.rglob(pattern)
            else:
                files = root.glob(pattern)
            
            for file_path in files:
                try:
                    metadata = self._catalog_file(file_path)
                    if metadata:
                        self.store.register_asset(metadata)
                        discovered.append(metadata)
                except Exception as e:
                    logger.error(f"Error cataloging {file_path}: {e}")
        
        logger.info(f"Discovered {len(discovered)} assets from {root_path}")
        return discovered
    
    def _catalog_file(self, file_path: Path) -> Optional[AssetMetadata]:
        """Catalog a single file."""
        extension = file_path.suffix.lower().lstrip('.')
        
        # Determine asset type
        audio_formats = ['wav', 'mp3', 'flac', 'm4a']
        video_formats = ['mp4', 'webm', 'mov']
        image_formats = ['png', 'jpg', 'jpeg', 'webp']
        text_formats = ['txt', 'json', 'jsonl', 'csv']
        model_formats = ['safetensors', 'pt', 'onnx']
        
        if extension in audio_formats:
            asset_type = AssetType.AUDIO
        elif extension in video_formats:
            asset_type = AssetType.VIDEO
        elif extension in image_formats:
            asset_type = AssetType.IMAGE
        elif extension in text_formats:
            asset_type = AssetType.TRANSCRIPT
        elif extension in model_formats:
            asset_type = AssetType.MODEL
        else:
            return None
        
        # Get file stats
        stat = file_path.stat()
        
        # Auto-detect Nigerian content
        name_lower = file_path.name.lower()
        is_nigerian = any(kw in name_lower for kw in self.nigerian_keywords)
        
        # Try to detect language from filename
        language = NigerianLanguage.ENGLISH
        if 'pidgin' in name_lower:
            language = NigerianLanguage.PIDGIN
        elif 'yoruba' in name_lower:
            language = NigerianLanguage.YORUBA
        elif 'hausa' in name_lower:
            language = NigerianLanguage.HAUSA
        elif 'igbo' in name_lower:
            language = NigerianLanguage.IGBO
        
        return AssetMetadata(
            asset_id=generate_asset_id(asset_type, name=file_path.name),
            asset_type=asset_type,
            name=file_path.name,
            storage_path=str(file_path.absolute()),
            storage_type="local",
            status=AssetStatus.READY,
            size_bytes=stat.st_size,
            format=extension,
            language=language,
            is_nigerian=is_nigerian,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            updated_at=datetime.fromtimestamp(stat.st_mtime)
        )
    
    def register_dataset(
        self,
        name: str,
        description: str,
        asset_ids: List[str],
        schema: DatasetSchema = None,
        tags: List[str] = None
    ) -> str:
        """
        Register a logical dataset composed of multiple assets.
        """
        dataset_id = generate_asset_id(AssetType.DATASET, name=name)
        
        # Calculate aggregated stats
        total_size = 0
        total_duration = 0
        language_counts = {}
        nigerian_count = 0
        
        for asset_id in asset_ids:
            asset = self.store.get_asset(asset_id)
            if asset:
                total_size += asset.size_bytes
                total_duration += asset.duration_seconds
                
                lang = asset.language.value
                language_counts[lang] = language_counts.get(lang, 0) + 1
                
                if asset.is_nigerian:
                    nigerian_count += 1
        
        # Create dataset metadata
        metadata = AssetMetadata(
            asset_id=dataset_id,
            asset_type=AssetType.DATASET,
            name=name,
            storage_path="",  # Virtual dataset
            storage_type="virtual",
            status=AssetStatus.READY,
            size_bytes=total_size,
            duration_seconds=total_duration,
            is_nigerian=nigerian_count > len(asset_ids) / 2,
            nigerian_score=nigerian_count / len(asset_ids) if asset_ids else 0,
            parent_ids=asset_ids,
            tags=tags or [],
            properties={
                'description': description,
                'asset_count': len(asset_ids),
                'language_distribution': language_counts,
                'schema': schema.to_dict() if schema else None
            }
        )
        
        self.store.register_asset(metadata)
        
        if schema:
            self.schemas[dataset_id] = schema
        
        logger.info(f"Registered dataset: {name} ({len(asset_ids)} assets)")
        return dataset_id
    
    def profile_dataset(self, dataset_id: str) -> DataProfile:
        """
        Generate statistical profile for a dataset.
        """
        dataset = self.store.get_asset(dataset_id)
        if not dataset:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        assets = [self.store.get_asset(aid) for aid in dataset.parent_ids]
        assets = [a for a in assets if a is not None]
        
        # Calculate language distribution
        lang_counts = {}
        quality_sum = 0
        nigerian_count = 0
        
        for asset in assets:
            lang = asset.language.value
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
            quality_sum += asset.quality_score
            if asset.is_nigerian:
                nigerian_count += 1
        
        total = len(assets) or 1
        language_dist = {k: v / total for k, v in lang_counts.items()}
        
        profile = DataProfile(
            total_records=len(assets),
            total_size_bytes=dataset.size_bytes,
            field_stats={
                'avg_duration': sum(a.duration_seconds for a in assets) / total,
                'avg_size': dataset.size_bytes / total,
            },
            quality_metrics={
                'avg_quality': quality_sum / total,
                'ready_count': sum(1 for a in assets if a.status == AssetStatus.READY),
                'failed_count': sum(1 for a in assets if a.status == AssetStatus.FAILED),
            },
            nigerian_content_ratio=nigerian_count / total,
            language_distribution=language_dist
        )
        
        self.profiles[dataset_id] = profile
        
        return profile
    
    def get_training_datasets(
        self,
        min_quality: float = 0.5,
        require_nigerian: bool = False,
        min_samples: int = 100
    ) -> List[AssetMetadata]:
        """
        Get datasets suitable for training.
        """
        datasets = self.store.search_assets(
            asset_type=AssetType.DATASET,
            status=AssetStatus.READY,
            min_quality=min_quality
        )
        
        result = []
        for dataset in datasets:
            asset_count = dataset.properties.get('asset_count', 0)
            
            if asset_count < min_samples:
                continue
            
            if require_nigerian and not dataset.is_nigerian:
                continue
            
            result.append(dataset)
        
        return result
    
    def get_lineage_graph(self, asset_id: str, depth: int = 3) -> Dict[str, Any]:
        """
        Get lineage graph for visualization.
        """
        visited = set()
        nodes = []
        edges = []
        
        def traverse(current_id: str, current_depth: int, direction: str):
            if current_id in visited or current_depth > depth:
                return
            
            visited.add(current_id)
            asset = self.store.get_asset(current_id)
            
            if asset:
                nodes.append({
                    'id': asset.asset_id,
                    'name': asset.name,
                    'type': asset.asset_type.value,
                    'status': asset.status.value
                })
            
            lineage = self.store.get_asset_lineage(current_id)
            
            if direction in ['up', 'both']:
                for parent_id in lineage['parents']:
                    edges.append({
                        'source': parent_id,
                        'target': current_id,
                        'type': 'derived'
                    })
                    traverse(parent_id, current_depth + 1, 'up')
            
            if direction in ['down', 'both']:
                for child_id in lineage['children']:
                    edges.append({
                        'source': current_id,
                        'target': child_id,
                        'type': 'derived'
                    })
                    traverse(child_id, current_depth + 1, 'down')
        
        traverse(asset_id, 0, 'both')
        
        return {
            'nodes': nodes,
            'edges': edges,
            'root': asset_id
        }
    
    def search(
        self,
        query: str,
        asset_types: List[AssetType] = None,
        languages: List[NigerianLanguage] = None,
        min_quality: float = None,
        limit: int = 50
    ) -> List[AssetMetadata]:
        """
        Search the catalog with various filters.
        """
        # Start with text search
        results = self.store.search_assets(
            query=query,
            min_quality=min_quality,
            limit=limit * 2  # Get more to filter
        )
        
        # Apply additional filters
        if asset_types:
            results = [r for r in results if r.asset_type in asset_types]
        
        if languages:
            results = [r for r in results if r.language in languages]
        
        return results[:limit]
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get catalog summary.
        """
        stats = self.store.get_statistics()
        
        return {
            'total_assets': sum(stats['by_type'].values()),
            'by_type': stats['by_type'],
            'by_language': stats['by_language'],
            'nigerian_content': stats['nigerian'],
            'quality_distribution': stats['quality_distribution'],
            'storage': stats['storage'],
            'registered_datasets': len(self.store.search_assets(asset_type=AssetType.DATASET)),
            'schemas_defined': len(self.schemas),
            'profiles_computed': len(self.profiles)
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Nigerian Content Classifier
# ═══════════════════════════════════════════════════════════════════════════════

class NigerianContentClassifier:
    """
    Specialized classifier for Nigerian content.
    """
    
    def __init__(self):
        # Pidgin markers
        self.pidgin_markers = [
            'wetin', 'dey', 'abeg', 'wahala', 'abi', 'sha', 'na',
            'how body', 'no wahala', 'e don', 'e go', 'e be',
            'no be', 'i dey', 'you dey', 'e dey', 'dem dey'
        ]
        
        # Yoruba markers
        self.yoruba_markers = [
            'omo', 'bawo', 'se', 'abi', 'jare', 'ko', 'ni',
            'pele', 'ewo', 'wa', 'lo', 'kini'
        ]
        
        # Hausa markers
        self.hausa_markers = [
            'ina', 'yaya', 'lafiya', 'sannu', 'barka', 'yau',
            'gobe', 'yau', 'cikin', 'da', 'su'
        ]
        
        # Igbo markers
        self.igbo_markers = [
            'kedu', 'nwanne', 'nnoo', 'daalu', 'ndewo', 'biko',
            'nne', 'nna', 'ezigbo', 'ofuma'
        ]
        
        # Cultural context markers
        self.cultural_markers = [
            'naija', 'lagos', 'abuja', 'nigeria', 'jollof', 'ankara',
            'aso-ebi', 'agbada', 'gele', 'suya', 'egusi', 'afrobeats',
            'nollywood', 'danfo', 'okada', 'keke', 'molue'
        ]
    
    def classify_text(self, text: str) -> Dict[str, Any]:
        """
        Classify text for Nigerian content and language.
        """
        text_lower = text.lower()
        
        # Count markers
        pidgin_count = sum(1 for m in self.pidgin_markers if m in text_lower)
        yoruba_count = sum(1 for m in self.yoruba_markers if m in text_lower)
        hausa_count = sum(1 for m in self.hausa_markers if m in text_lower)
        igbo_count = sum(1 for m in self.igbo_markers if m in text_lower)
        cultural_count = sum(1 for m in self.cultural_markers if m in text_lower)
        
        total_markers = pidgin_count + yoruba_count + hausa_count + igbo_count
        
        # Determine primary language
        counts = {
            NigerianLanguage.PIDGIN: pidgin_count,
            NigerianLanguage.YORUBA: yoruba_count,
            NigerianLanguage.HAUSA: hausa_count,
            NigerianLanguage.IGBO: igbo_count
        }
        
        primary_lang = max(counts, key=counts.get)
        primary_count = counts[primary_lang]
        
        if primary_count == 0:
            primary_lang = NigerianLanguage.ENGLISH
            confidence = 0.5 if cultural_count > 0 else 0.2
        else:
            confidence = min(1.0, (primary_count + cultural_count) / 10)
        
        # Determine if Nigerian
        is_nigerian = (total_markers > 0) or (cultural_count >= 2)
        
        # Calculate Nigerian score
        nigerian_score = min(1.0, (total_markers + cultural_count * 2) / 15)
        
        return {
            'primary_language': primary_lang,
            'confidence': confidence,
            'is_nigerian': is_nigerian,
            'nigerian_score': nigerian_score,
            'marker_counts': {
                'pidgin': pidgin_count,
                'yoruba': yoruba_count,
                'hausa': hausa_count,
                'igbo': igbo_count,
                'cultural': cultural_count
            },
            'detected_markers': self._get_detected_markers(text_lower)
        }
    
    def _get_detected_markers(self, text: str) -> List[str]:
        """Get all detected markers in text."""
        all_markers = (
            self.pidgin_markers + self.yoruba_markers +
            self.hausa_markers + self.igbo_markers +
            self.cultural_markers
        )
        return [m for m in all_markers if m in text]


if __name__ == "__main__":
    # Demo
    from metadata_store import MetadataStore
    
    store = MetadataStore("demo_catalog.db")
    catalog = DataCatalog(store)
    classifier = NigerianContentClassifier()
    
    # Test classification
    test_texts = [
        "How you dey? I dey fine o!",
        "Wetin dey happen for Lagos today?",
        "The technology conference in Abuja was amazing",
        "Just cooked some delicious jollof rice with suya"
    ]
    
    print("Nigerian Content Classification:")
    print("=" * 50)
    
    for text in test_texts:
        result = classifier.classify_text(text)
        print(f"\nText: '{text}'")
        print(f"  Language: {result['primary_language'].value}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Nigerian Score: {result['nigerian_score']:.2f}")
        print(f"  Markers: {result['detected_markers']}")
