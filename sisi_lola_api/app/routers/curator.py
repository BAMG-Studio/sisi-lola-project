"""
Sisi Lola Voice Dataset Curator API Router

This router provides endpoints for:
1. Ingesting curated dataset manifests from the Voice Dataset Curator GPT
2. Validating and processing curated samples
3. Registering datasets for training
4. Querying available datasets and coverage
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import json
import shutil
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/curator", tags=["Voice Dataset Curator"])

# Paths
CURATOR_DIR = Path(__file__).parent.parent.parent.parent / "ml_training" / "curator"
DATASETS_DIR = Path(__file__).parent.parent.parent.parent / "ml_training" / "datasets" / "curated"
MANIFESTS_DIR = CURATOR_DIR / "manifests"

# Ensure directories exist
CURATOR_DIR.mkdir(parents=True, exist_ok=True)
DATASETS_DIR.mkdir(parents=True, exist_ok=True)
MANIFESTS_DIR.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Request/Response Models
# =============================================================================

class CuratedSampleInput(BaseModel):
    """Input model for a curated sample"""
    audio_path: str
    text: Optional[str] = None
    translation: Optional[str] = None
    language: str = "yoruba"
    dialect: str = "lagos"
    duration: float = 0.0
    quality_score: float = 0.7
    is_clean: bool = True
    speaker_gender: str = "female"
    speaker_age_range: str = "28-40"
    emotion: str = "neutral"
    source_dataset: Optional[str] = None
    source_url: Optional[str] = None
    sisi_compatible: bool = False
    persona_match_score: float = 0.0


class CuratedManifestInput(BaseModel):
    """Input model for a curated dataset manifest"""
    dataset_id: str = Field(..., description="Unique identifier for the dataset")
    name: str = Field(..., description="Human-readable name")
    version: str = "1.0.0"
    
    # Content
    language: str = "yoruba"
    dialect: str = "lagos"
    samples: List[CuratedSampleInput] = []
    
    # Technical specs
    sample_rate: int = 22050
    channels: int = 1
    audio_format: str = "wav"
    
    # Licensing
    license: str = "CC-BY-SA-4.0"
    commercial_ready: bool = True
    attribution_text: str = ""
    
    # Source tracking
    source_datasets: List[str] = []
    curator: str = "voice_dataset_curator_gpt"
    
    # Notes
    notes: str = ""


class DatasetSummary(BaseModel):
    """Summary of a registered dataset"""
    dataset_id: str
    name: str
    language: str
    dialect: str
    total_samples: int
    total_duration_hours: float
    sisi_compatible_count: int
    commercial_ready: bool
    license: str
    registered_at: str


class CoverageReport(BaseModel):
    """Language coverage report"""
    language: str
    total_datasets: int
    total_samples: int
    total_hours: float
    commercial_hours: float
    sisi_compatible_samples: int
    quality_breakdown: Dict[str, int]
    gap_status: str  # "critical", "moderate", "covered"


class ValidationResult(BaseModel):
    """Result of manifest validation"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    samples_validated: int
    sisi_compatible_count: int


# =============================================================================
# Helper Functions
# =============================================================================

def get_registered_manifests() -> List[Dict]:
    """Get all registered manifest summaries"""
    manifests = []
    for manifest_file in MANIFESTS_DIR.glob("*.json"):
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Calculate sisi_compatible_count from samples
                samples = data.get("samples", [])
                sisi_compatible_count = sum(1 for s in samples if s.get("sisi_compatible", False))
                manifests.append({
                    "dataset_id": data.get("dataset_id"),
                    "name": data.get("name"),
                    "language": data.get("language"),
                    "dialect": data.get("dialect", "lagos"),
                    "total_samples": data.get("total_samples", len(samples)),
                    "total_duration_hours": data.get("total_duration_hours", 0),
                    "sisi_compatible_count": data.get("sisi_compatible_count", sisi_compatible_count),
                    "commercial_ready": data.get("commercial_ready", False),
                    "license": data.get("license"),
                    "registered_at": data.get("created_at")
                })
        except Exception as e:
            logger.error(f"Error reading manifest {manifest_file}: {e}")
    return manifests


def validate_manifest(manifest_data: Dict) -> Dict:
    """Validate a manifest"""
    errors = []
    warnings = []
    
    # Required fields
    if not manifest_data.get("dataset_id"):
        errors.append("Missing dataset_id")
    if not manifest_data.get("name"):
        errors.append("Missing name")
    
    samples = manifest_data.get("samples", [])
    sisi_compatible = 0
    
    for i, sample in enumerate(samples):
        duration = sample.get("duration", 0)
        if duration < 1:
            warnings.append(f"Sample {i}: Duration too short ({duration}s)")
        elif duration > 120:
            warnings.append(f"Sample {i}: Duration too long ({duration}s)")
        
        if not sample.get("audio_path"):
            errors.append(f"Sample {i}: Missing audio_path")
        
        if sample.get("sisi_compatible"):
            sisi_compatible += 1
    
    # License check
    license_type = manifest_data.get("license", "unknown")
    if manifest_data.get("commercial_ready") and "NC" in license_type:
        errors.append("commercial_ready is True but license is non-commercial")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "samples_validated": len(samples),
        "sisi_compatible_count": sisi_compatible
    }


def calculate_coverage() -> Dict[str, Any]:
    """Calculate language coverage from all registered datasets"""
    manifests = get_registered_manifests()
    
    coverage = {}
    
    for m in manifests:
        lang = m.get("language", "unknown")
        if lang not in coverage:
            coverage[lang] = {
                "total_datasets": 0,
                "total_samples": 0,
                "total_hours": 0.0,
                "commercial_hours": 0.0,
                "datasets": []
            }
        
        coverage[lang]["total_datasets"] += 1
        coverage[lang]["total_samples"] += m.get("total_samples", 0)
        coverage[lang]["total_hours"] += m.get("total_duration_hours", 0)
        if m.get("commercial_ready"):
            coverage[lang]["commercial_hours"] += m.get("total_duration_hours", 0)
        coverage[lang]["datasets"].append(m.get("dataset_id"))
    
    return coverage


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/health")
async def curator_health():
    """Health check for curator service"""
    return {
        "status": "healthy",
        "service": "voice_dataset_curator",
        "manifests_dir": str(MANIFESTS_DIR),
        "datasets_dir": str(DATASETS_DIR),
        "registered_datasets": len(list(MANIFESTS_DIR.glob("*.json")))
    }


@router.post("/ingest", response_model=Dict)
async def ingest_manifest(manifest: CuratedManifestInput):
    """
    Ingest a curated dataset manifest from the Voice Dataset Curator GPT.
    
    This endpoint receives the output from the Custom GPT and registers it
    for use in the Sisi Lola training pipeline.
    """
    try:
        # Convert to dict
        manifest_data = manifest.dict()
        
        # Add metadata
        manifest_data["created_at"] = datetime.now().isoformat()
        manifest_data["updated_at"] = datetime.now().isoformat()
        manifest_data["audio_specs"] = {
            "sample_rate": manifest.sample_rate,
            "channels": manifest.channels,
            "format": manifest.audio_format,
            "bit_depth": 16
        }
        
        # Calculate stats
        samples = manifest_data.get("samples", [])
        total_duration = sum(s.get("duration", 0) for s in samples)
        manifest_data["total_samples"] = len(samples)
        manifest_data["total_duration_hours"] = total_duration / 3600
        manifest_data["sisi_compatible_count"] = sum(1 for s in samples if s.get("sisi_compatible"))
        manifest_data["average_quality_score"] = (
            sum(s.get("quality_score", 0) for s in samples) / len(samples)
            if samples else 0
        )
        
        # Validate
        validation = validate_manifest(manifest_data)
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={"message": "Manifest validation failed", "errors": validation["errors"]}
            )
        
        # Save manifest
        manifest_file = MANIFESTS_DIR / f"{manifest.dataset_id}.json"
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Ingested manifest: {manifest.dataset_id} with {len(samples)} samples")
        
        return {
            "status": "success",
            "dataset_id": manifest.dataset_id,
            "message": f"Successfully ingested {len(samples)} samples",
            "validation": validation,
            "manifest_path": str(manifest_file)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting manifest: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=ValidationResult)
async def validate_manifest_endpoint(manifest: CuratedManifestInput):
    """
    Validate a manifest without registering it.
    
    Use this to check a manifest before ingestion.
    """
    manifest_data = manifest.dict()
    result = validate_manifest(manifest_data)
    return ValidationResult(**result)


@router.get("/datasets", response_model=List[DatasetSummary])
async def list_datasets():
    """List all registered curated datasets"""
    manifests = get_registered_manifests()
    return [DatasetSummary(**m) for m in manifests]


@router.get("/datasets/{dataset_id}")
async def get_dataset(dataset_id: str):
    """Get details of a specific dataset"""
    manifest_file = MANIFESTS_DIR / f"{dataset_id}.json"
    
    if not manifest_file.exists():
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    
    with open(manifest_file, 'r', encoding='utf-8') as f:
        return json.load(f)


@router.delete("/datasets/{dataset_id}")
async def delete_dataset(dataset_id: str):
    """Delete a registered dataset"""
    manifest_file = MANIFESTS_DIR / f"{dataset_id}.json"
    
    if not manifest_file.exists():
        raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    
    manifest_file.unlink()
    logger.info(f"Deleted dataset: {dataset_id}")
    
    return {"status": "deleted", "dataset_id": dataset_id}


@router.get("/coverage")
async def get_coverage():
    """
    Get language coverage report.
    
    Shows which languages have good coverage and which need more data.
    """
    coverage = calculate_coverage()
    
    # Load target languages from matrix
    matrix_file = CURATOR_DIR / "language_coverage_matrix.json"
    target_languages = []
    
    if matrix_file.exists():
        with open(matrix_file, 'r') as f:
            matrix = json.load(f)
            target_languages = matrix.get("sisi_lola_target_languages", {}).get("primary", [])
    
    # Build report
    report = {
        "total_datasets": sum(c["total_datasets"] for c in coverage.values()),
        "total_hours": sum(c["total_hours"] for c in coverage.values()),
        "commercial_hours": sum(c["commercial_hours"] for c in coverage.values()),
        "languages": {},
        "gaps": []
    }
    
    for lang in target_languages:
        if lang in coverage:
            c = coverage[lang]
            status = "covered" if c["total_hours"] > 10 else ("moderate" if c["total_hours"] > 2 else "critical")
            report["languages"][lang] = {
                "total_datasets": c["total_datasets"],
                "total_hours": c["total_hours"],
                "commercial_hours": c["commercial_hours"],
                "status": status
            }
            if status != "covered":
                report["gaps"].append({"language": lang, "status": status, "hours": c["total_hours"]})
        else:
            report["languages"][lang] = {
                "total_datasets": 0,
                "total_hours": 0,
                "commercial_hours": 0,
                "status": "critical"
            }
            report["gaps"].append({"language": lang, "status": "critical", "hours": 0})
    
    return report


@router.get("/catalog")
async def get_catalog():
    """
    Get the African language datasets catalog.
    
    Returns all known datasets from the curator knowledge base.
    """
    catalog_file = CURATOR_DIR / "african_language_datasets_catalog.csv"
    
    if not catalog_file.exists():
        raise HTTPException(status_code=404, detail="Catalog file not found")
    
    import csv
    datasets = []
    
    with open(catalog_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            datasets.append(row)
    
    return {
        "total": len(datasets),
        "datasets": datasets
    }


@router.post("/search")
async def search_datasets(
    language: Optional[str] = None,
    quality_tier: Optional[str] = None,
    commercial_only: bool = False,
    min_hours: float = 0
):
    """
    Search the datasets catalog with filters.
    
    Used by the Voice Dataset Curator GPT to find matching datasets.
    """
    catalog_file = CURATOR_DIR / "african_language_datasets_catalog.csv"
    
    if not catalog_file.exists():
        raise HTTPException(status_code=404, detail="Catalog file not found")
    
    import csv
    results = []
    
    with open(catalog_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Apply filters
            if language and language.lower() not in row.get("Languages", "").lower():
                continue
            if quality_tier and row.get("Quality_Tier", "").lower() != quality_tier.lower():
                continue
            if commercial_only and row.get("Commercial_Ready", "").lower() != "yes":
                continue
            try:
                hours = float(row.get("Duration_Hours", "0").replace("+", ""))
                if hours < min_hours:
                    continue
            except ValueError:
                pass
            
            results.append(row)
    
    return {
        "query": {
            "language": language,
            "quality_tier": quality_tier,
            "commercial_only": commercial_only,
            "min_hours": min_hours
        },
        "total": len(results),
        "datasets": results
    }


@router.get("/recipes")
async def get_processing_recipes():
    """
    Get available audio processing recipes.
    
    Returns documentation on how to process datasets for Sisi Lola.
    """
    return {
        "recipes": [
            {
                "name": "convert_any_to_sisi_format",
                "description": "Convert any audio to Sisi Lola standard (WAV, 22050 Hz, mono)",
                "usage": "python audio_processing_recipes.py convert -i input.flac -o ./output/"
            },
            {
                "name": "batch_convert_bibletts",
                "description": "Batch convert BibleTTS 48kHz FLAC files to 22050 Hz WAV",
                "usage": "python audio_processing_recipes.py batch_convert -i ./bibletts/ -o ./converted/"
            },
            {
                "name": "filter_by_duration",
                "description": "Filter audio files by duration (3-60 seconds for voice cloning)",
                "usage": "python audio_processing_recipes.py filter_duration -i ./audio/ -o report.json"
            },
            {
                "name": "hf_to_wav",
                "description": "Export HuggingFace dataset to WAV files with transcripts",
                "usage": "python audio_processing_recipes.py hf_export -i Abdullah804/yoruba-ljspeech -o ./yoruba/"
            },
            {
                "name": "quality_check",
                "description": "Run quality assessment on audio files",
                "usage": "python audio_processing_recipes.py quality_check -i ./audio/ -o report.json"
            },
            {
                "name": "create_manifest",
                "description": "Create Sisi Lola training manifest from processed audio",
                "usage": "python audio_processing_recipes.py create_manifest -i ./audio/ -o manifest.json -l yoruba"
            }
        ],
        "audio_specs": {
            "sample_rate": 22050,
            "channels": 1,
            "format": "wav",
            "bit_depth": 16,
            "optimal_duration": "10-30 seconds",
            "acceptable_duration": "3-60 seconds"
        }
    }


@router.post("/trigger-training")
async def trigger_training(dataset_ids: List[str], background_tasks: BackgroundTasks):
    """
    Trigger voice training with specified curated datasets.
    
    This queues the datasets for the next training run.
    """
    # Validate all datasets exist
    for dataset_id in dataset_ids:
        manifest_file = MANIFESTS_DIR / f"{dataset_id}.json"
        if not manifest_file.exists():
            raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_id}")
    
    # Create training queue file
    queue_file = DATASETS_DIR / "training_queue.json"
    queue = {
        "created_at": datetime.now().isoformat(),
        "status": "pending",
        "dataset_ids": dataset_ids
    }
    
    with open(queue_file, 'w') as f:
        json.dump(queue, f, indent=2)
    
    logger.info(f"Training queued with datasets: {dataset_ids}")
    
    return {
        "status": "queued",
        "dataset_ids": dataset_ids,
        "message": "Datasets queued for training. Run train_nigerian_models.bat to start.",
        "queue_file": str(queue_file)
    }


# =============================================================================
# Export for main.py
# =============================================================================

def register_curator_router(app):
    """Register the curator router with the main app"""
    app.include_router(router)
