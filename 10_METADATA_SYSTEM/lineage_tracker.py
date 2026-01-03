#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
                         ASSET LINEAGE TRACKER
═══════════════════════════════════════════════════════════════════════════════
              Track data transformations and model provenance
═══════════════════════════════════════════════════════════════════════════════

Provides:
- Detailed lineage tracking for all assets
- Transformation history
- Model provenance tracking
- Impact analysis
- Visual lineage graphs
"""

import json
import logging
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from enum import Enum
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TransformationType(Enum):
    """Types of data transformations."""
    EXTRACTION = "extraction"           # Extract from source
    CONVERSION = "conversion"           # Format conversion
    ENHANCEMENT = "enhancement"         # Quality improvement
    FILTERING = "filtering"             # Data filtering
    AGGREGATION = "aggregation"         # Combine multiple sources
    TRAINING = "training"               # Model training
    INFERENCE = "inference"             # Model inference
    ANNOTATION = "annotation"           # Adding labels/metadata
    GENERATION = "generation"           # AI-generated content


@dataclass
class TransformationRecord:
    """
    Record of a single transformation in the lineage.
    """
    transformation_id: str
    transformation_type: TransformationType
    input_asset_ids: List[str]
    output_asset_ids: List[str]
    operator: str                        # What performed the transformation
    parameters: Dict[str, Any]           # Transformation parameters
    metrics: Dict[str, float]            # Quality metrics
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    status: str = "completed"
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['transformation_type'] = self.transformation_type.value
        data['started_at'] = self.started_at.isoformat()
        data['completed_at'] = self.completed_at.isoformat() if self.completed_at else None
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransformationRecord':
        data['transformation_type'] = TransformationType(data['transformation_type'])
        data['started_at'] = datetime.fromisoformat(data['started_at'])
        if data['completed_at']:
            data['completed_at'] = datetime.fromisoformat(data['completed_at'])
        return cls(**data)


@dataclass
class ModelProvenance:
    """
    Track the provenance of a trained model.
    """
    model_id: str
    model_name: str
    model_type: str                      # voice, vision, language, etc.
    version: str
    
    # Training details
    training_dataset_ids: List[str]
    training_config: Dict[str, Any]
    training_metrics: Dict[str, float]
    
    # Parent models (for fine-tuning)
    parent_model_ids: List[str] = field(default_factory=list)
    
    # Deployment
    deployed_to: List[str] = field(default_factory=list)  # replicate, modal, etc.
    deployment_version: str = ""
    
    # Timestamps
    trained_at: datetime = field(default_factory=datetime.now)
    deployed_at: Optional[datetime] = None
    
    # Nigerian content specifics
    nigerian_data_ratio: float = 0.0
    dialect_coverage: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['trained_at'] = self.trained_at.isoformat()
        data['deployed_at'] = self.deployed_at.isoformat() if self.deployed_at else None
        return data


class LineageTracker:
    """
    Track and query asset lineage.
    """
    
    def __init__(self, storage_path: str = "lineage_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.transformations_file = self.storage_path / "transformations.jsonl"
        self.provenance_file = self.storage_path / "model_provenance.json"
        
        self.transformations: Dict[str, TransformationRecord] = {}
        self.model_provenance: Dict[str, ModelProvenance] = {}
        
        self._load_data()
    
    def _load_data(self):
        """Load existing data from storage."""
        # Load transformations
        if self.transformations_file.exists():
            with open(self.transformations_file, 'r') as f:
                for line in f:
                    record = TransformationRecord.from_dict(json.loads(line))
                    self.transformations[record.transformation_id] = record
        
        # Load provenance
        if self.provenance_file.exists():
            with open(self.provenance_file, 'r') as f:
                data = json.load(f)
                for model_id, prov_data in data.items():
                    prov_data['trained_at'] = datetime.fromisoformat(prov_data['trained_at'])
                    if prov_data['deployed_at']:
                        prov_data['deployed_at'] = datetime.fromisoformat(prov_data['deployed_at'])
                    self.model_provenance[model_id] = ModelProvenance(**prov_data)
    
    def _save_transformation(self, record: TransformationRecord):
        """Append transformation to storage."""
        with open(self.transformations_file, 'a') as f:
            f.write(json.dumps(record.to_dict()) + '\n')
    
    def _save_provenance(self):
        """Save all model provenance."""
        data = {
            model_id: prov.to_dict()
            for model_id, prov in self.model_provenance.items()
        }
        with open(self.provenance_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_transformation(
        self,
        transformation_type: TransformationType,
        input_asset_ids: List[str],
        output_asset_ids: List[str],
        operator: str,
        parameters: Dict[str, Any] = None,
        metrics: Dict[str, float] = None,
        notes: str = ""
    ) -> str:
        """
        Record a data transformation.
        """
        transformation_id = f"tf_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        record = TransformationRecord(
            transformation_id=transformation_id,
            transformation_type=transformation_type,
            input_asset_ids=input_asset_ids,
            output_asset_ids=output_asset_ids,
            operator=operator,
            parameters=parameters or {},
            metrics=metrics or {},
            notes=notes,
            completed_at=datetime.now()
        )
        
        self.transformations[transformation_id] = record
        self._save_transformation(record)
        
        logger.info(f"Recorded transformation: {transformation_id} ({transformation_type.value})")
        return transformation_id
    
    def record_audio_extraction(
        self,
        video_asset_id: str,
        audio_asset_id: str,
        format: str = "wav",
        sample_rate: int = 16000
    ) -> str:
        """Record audio extraction from video."""
        return self.record_transformation(
            transformation_type=TransformationType.EXTRACTION,
            input_asset_ids=[video_asset_id],
            output_asset_ids=[audio_asset_id],
            operator="audio_extractor",
            parameters={
                'format': format,
                'sample_rate': sample_rate
            }
        )
    
    def record_transcription(
        self,
        audio_asset_id: str,
        transcript_asset_id: str,
        model: str,
        confidence: float
    ) -> str:
        """Record audio transcription."""
        return self.record_transformation(
            transformation_type=TransformationType.CONVERSION,
            input_asset_ids=[audio_asset_id],
            output_asset_ids=[transcript_asset_id],
            operator="speech_to_text",
            parameters={'model': model},
            metrics={'confidence': confidence}
        )
    
    def record_training(
        self,
        dataset_ids: List[str],
        model_asset_id: str,
        model_name: str,
        model_type: str,
        training_config: Dict[str, Any],
        metrics: Dict[str, float],
        parent_model_id: str = None,
        nigerian_ratio: float = 0.0,
        dialects: List[str] = None
    ) -> str:
        """
        Record model training.
        """
        # Record transformation
        tf_id = self.record_transformation(
            transformation_type=TransformationType.TRAINING,
            input_asset_ids=dataset_ids,
            output_asset_ids=[model_asset_id],
            operator="modal_training",
            parameters=training_config,
            metrics=metrics
        )
        
        # Create provenance record
        provenance = ModelProvenance(
            model_id=model_asset_id,
            model_name=model_name,
            model_type=model_type,
            version="1.0",
            training_dataset_ids=dataset_ids,
            training_config=training_config,
            training_metrics=metrics,
            parent_model_ids=[parent_model_id] if parent_model_id else [],
            nigerian_data_ratio=nigerian_ratio,
            dialect_coverage=dialects or []
        )
        
        self.model_provenance[model_asset_id] = provenance
        self._save_provenance()
        
        return tf_id
    
    def record_generation(
        self,
        model_id: str,
        prompt_or_input: str,
        output_asset_id: str,
        generation_type: str,  # image, video, audio, text
        parameters: Dict[str, Any] = None,
        quality_score: float = None
    ) -> str:
        """Record AI content generation."""
        return self.record_transformation(
            transformation_type=TransformationType.GENERATION,
            input_asset_ids=[model_id],
            output_asset_ids=[output_asset_id],
            operator=f"{generation_type}_generator",
            parameters={
                'prompt_or_input': prompt_or_input,
                **(parameters or {})
            },
            metrics={'quality_score': quality_score} if quality_score else {}
        )
    
    def get_asset_history(self, asset_id: str) -> List[TransformationRecord]:
        """
        Get all transformations involving an asset.
        """
        history = []
        
        for record in self.transformations.values():
            if asset_id in record.input_asset_ids or asset_id in record.output_asset_ids:
                history.append(record)
        
        # Sort by time
        history.sort(key=lambda x: x.started_at)
        return history
    
    def get_ancestors(self, asset_id: str, depth: int = 10) -> List[str]:
        """
        Get all ancestor assets (inputs that led to this asset).
        """
        ancestors = set()
        to_check = [asset_id]
        checked = set()
        current_depth = 0
        
        while to_check and current_depth < depth:
            current_id = to_check.pop(0)
            if current_id in checked:
                continue
            checked.add(current_id)
            
            for record in self.transformations.values():
                if current_id in record.output_asset_ids:
                    for input_id in record.input_asset_ids:
                        ancestors.add(input_id)
                        to_check.append(input_id)
            
            current_depth += 1
        
        return list(ancestors)
    
    def get_descendants(self, asset_id: str, depth: int = 10) -> List[str]:
        """
        Get all descendant assets (outputs derived from this asset).
        """
        descendants = set()
        to_check = [asset_id]
        checked = set()
        current_depth = 0
        
        while to_check and current_depth < depth:
            current_id = to_check.pop(0)
            if current_id in checked:
                continue
            checked.add(current_id)
            
            for record in self.transformations.values():
                if current_id in record.input_asset_ids:
                    for output_id in record.output_asset_ids:
                        descendants.add(output_id)
                        to_check.append(output_id)
            
            current_depth += 1
        
        return list(descendants)
    
    def get_model_provenance(self, model_id: str) -> Optional[ModelProvenance]:
        """Get provenance for a model."""
        return self.model_provenance.get(model_id)
    
    def get_model_training_data(self, model_id: str) -> List[str]:
        """Get all training data IDs for a model."""
        prov = self.get_model_provenance(model_id)
        if prov:
            return prov.training_dataset_ids
        return []
    
    def impact_analysis(self, asset_id: str) -> Dict[str, Any]:
        """
        Analyze the impact of an asset across the system.
        """
        ancestors = self.get_ancestors(asset_id)
        descendants = self.get_descendants(asset_id)
        
        # Get history
        history = self.get_asset_history(asset_id)
        
        # Check if used in any model training
        models_using_asset = []
        for model_id, prov in self.model_provenance.items():
            if asset_id in prov.training_dataset_ids:
                models_using_asset.append(model_id)
            elif asset_id in self.get_ancestors(model_id):
                models_using_asset.append(model_id)
        
        return {
            'asset_id': asset_id,
            'ancestor_count': len(ancestors),
            'descendant_count': len(descendants),
            'transformation_count': len(history),
            'models_impacted': models_using_asset,
            'ancestors': ancestors[:10],  # Limit for display
            'descendants': descendants[:10],
            'recent_transformations': [t.to_dict() for t in history[-5:]]
        }
    
    def generate_lineage_report(self, asset_id: str) -> str:
        """
        Generate a human-readable lineage report.
        """
        impact = self.impact_analysis(asset_id)
        history = self.get_asset_history(asset_id)
        
        report = []
        report.append(f"# Lineage Report for {asset_id}")
        report.append(f"\nGenerated: {datetime.now().isoformat()}")
        
        report.append("\n## Summary")
        report.append(f"- Ancestors: {impact['ancestor_count']}")
        report.append(f"- Descendants: {impact['descendant_count']}")
        report.append(f"- Transformations: {impact['transformation_count']}")
        report.append(f"- Models Impacted: {len(impact['models_impacted'])}")
        
        report.append("\n## Transformation History")
        for record in history:
            report.append(f"\n### {record.transformation_type.value.title()}")
            report.append(f"- ID: {record.transformation_id}")
            report.append(f"- Operator: {record.operator}")
            report.append(f"- Time: {record.started_at.isoformat()}")
            report.append(f"- Inputs: {record.input_asset_ids}")
            report.append(f"- Outputs: {record.output_asset_ids}")
            if record.metrics:
                report.append(f"- Metrics: {record.metrics}")
        
        if impact['models_impacted']:
            report.append("\n## Models Using This Asset")
            for model_id in impact['models_impacted']:
                prov = self.get_model_provenance(model_id)
                if prov:
                    report.append(f"\n### {prov.model_name}")
                    report.append(f"- Type: {prov.model_type}")
                    report.append(f"- Version: {prov.version}")
                    report.append(f"- Nigerian Data Ratio: {prov.nigerian_data_ratio:.1%}")
        
        return "\n".join(report)


if __name__ == "__main__":
    # Demo
    tracker = LineageTracker("demo_lineage")
    
    # Simulate a content processing pipeline
    video_id = "video_001"
    audio_id = "audio_001"
    transcript_id = "transcript_001"
    model_id = "model_voice_001"
    
    # Record extraction
    tracker.record_audio_extraction(video_id, audio_id)
    
    # Record transcription
    tracker.record_transcription(audio_id, transcript_id, "whisper-large-v3", 0.95)
    
    # Record training
    tracker.record_training(
        dataset_ids=[transcript_id],
        model_asset_id=model_id,
        model_name="sisi-lola-voice-v1",
        model_type="voice_lora",
        training_config={'epochs': 10, 'lr': 1e-4},
        metrics={'wer': 0.08, 'cer': 0.03},
        nigerian_ratio=0.85,
        dialects=['pidgin', 'yoruba']
    )
    
    # Record generation
    tracker.record_generation(
        model_id=model_id,
        prompt_or_input="How you dey?",
        output_asset_id="generated_audio_001",
        generation_type="audio",
        quality_score=0.92
    )
    
    # Get impact analysis
    impact = tracker.impact_analysis(video_id)
    print(f"\nImpact Analysis for {video_id}:")
    print(f"  Descendants: {impact['descendant_count']}")
    print(f"  Models Impacted: {impact['models_impacted']}")
    
    # Generate report
    report = tracker.generate_lineage_report(video_id)
    print("\n" + report)
