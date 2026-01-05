"""
SISI LOLA SERVICES
==================
Central exports for all Sisi Lola services.

Services:
- ReplicateOrchestrator: Multi-model Replicate management
- ImmigrationSuperLawyer: Immigration assistance (Life OS)
- MultilingualService: Nigerian language support
- ContentPlanner: Intelligent content scheduling
"""

from .replicate_orchestrator import (
    ReplicateOrchestrator,
    get_replicate_orchestrator,
    MODEL_REGISTRY,
    ModelCategory,
    ModelConfig,
)

from .immigration_service import (
    ImmigrationSuperLawyer,
    get_immigration_service,
    CaseAssessment,
    PolicyAlert,
    ServiceTier,
)

from .multilingual_service import (
    MultilingualService,
    get_multilingual_service,
    NigerianLanguage,
    LANGUAGE_REGISTRY,
    PIDGIN_DICTIONARY,
    PRAYERS_BY_LANGUAGE,
)

from .content_planner import (
    ContentPlanner,
    get_content_planner,
    Platform,
    ContentType,
    VibeCategory,
    ContentItem,
)

__all__ = [
    # Replicate
    "ReplicateOrchestrator",
    "get_replicate_orchestrator",
    "MODEL_REGISTRY",
    "ModelCategory",
    "ModelConfig",
    
    # Immigration
    "ImmigrationSuperLawyer",
    "get_immigration_service",
    "CaseAssessment",
    "PolicyAlert",
    "ServiceTier",
    
    # Multilingual
    "MultilingualService",
    "get_multilingual_service",
    "NigerianLanguage",
    "LANGUAGE_REGISTRY",
    "PIDGIN_DICTIONARY",
    "PRAYERS_BY_LANGUAGE",
    
    # Content Planner
    "ContentPlanner",
    "get_content_planner",
    "Platform",
    "ContentType",
    "VibeCategory",
    "ContentItem",
]

# Service version
__version__ = "2.0.0"
