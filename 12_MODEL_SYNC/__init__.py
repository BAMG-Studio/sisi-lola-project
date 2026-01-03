#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
🔄 SISI LOLA MODEL SYNC - Complete Feedback Loop Infrastructure
═══════════════════════════════════════════════════════════════════════════════

This module closes the feedback loop between training and inference:

    Ingested Data → Modal Training → HuggingFace Hub → Replicate → Users
                                           ↓
                                    DVC Versioning
                                           ↓
                                    Streamlit Dashboard
                                           ↓
                                    Feedback Collection
                                           ↓
                                    (Back to training)

Components:
- huggingface_sync: Push/pull models to HuggingFace Hub
- replicate_sync: Deploy models to Replicate for inference
- dvc_manager: Version control for large model files
- quality_validator: Automated testing before production
- inference_router: Route requests through HF Inference Providers

HuggingFace Pro Features Used:
- Inference Providers: Multi-provider routing (Replicate, Groq, Together)
- ZeroGPU: Free H200 inference for demos
- Model Hub: Central model registry
- Dataset Hub: Training data versioning

═══════════════════════════════════════════════════════════════════════════════
"""

# Lazy imports to avoid circular imports and missing dependencies
def __getattr__(name):
    """Lazy load module components."""
    
    # HuggingFace Sync
    if name in ("HuggingFaceSync", "HFConfig", "push_model_to_hub", "pull_model_from_hub", "create_model_card"):
        from . import huggingface_sync
        return getattr(huggingface_sync, name)
    
    # Replicate Sync
    if name in ("ReplicateSync", "ReplicateConfig", "deploy_to_replicate", "sync_from_huggingface"):
        from . import replicate_sync
        return getattr(replicate_sync, name)
    
    # DVC Manager
    if name in ("DVCManager", "DVCConfig", "track_model", "create_version", "get_versions"):
        from . import dvc_manager
        return getattr(dvc_manager, name)
    
    # Quality Validator
    if name in ("QualityValidator", "ValidationConfig", "validate_model", "is_production_ready"):
        from . import quality_validator
        return getattr(quality_validator, name)
    
    # Inference Router
    if name in ("InferenceRouter", "RouterConfig", "RoutingStrategy", "route_inference", "chat", "generate_voice", "generate_image"):
        from . import inference_router
        return getattr(inference_router, name)
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # HuggingFace
    "HuggingFaceSync",
    "HFConfig",
    "push_model_to_hub",
    "pull_model_from_hub",
    "create_model_card",
    # Replicate
    "ReplicateSync",
    "ReplicateConfig",
    "deploy_to_replicate",
    "sync_from_huggingface",
    # DVC
    "DVCManager",
    "DVCConfig",
    "track_model",
    "create_version",
    "get_versions",
    # Quality
    "QualityValidator",
    "ValidationConfig",
    "validate_model",
    "is_production_ready",
    # Inference
    "InferenceRouter",
    "RouterConfig",
    "RoutingStrategy",
    "route_inference",
    "chat",
    "generate_voice",
    "generate_image",
]

__version__ = "1.0.0"
