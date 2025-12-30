# =============================================================================
# SISI LOLA API ROUTERS
# =============================================================================
# Clean router exports - only active routers are exported here
# Last Cleaned: 2025-12-29
# =============================================================================

from . import (
    # UI Routes
    dashboard_router,       # /, /dashboard, /demo, /console, /vision
    
    # Core API v2
    vibe_router,            # /api/v2/vibe/* - Supreme content generation + demo chat
    social_router,          # /api/v2/social/* - One-click social posting
    enhanced_chat,          # /api/v2/enhanced-chat/* - Modal fast inference
    auth_router,            # /api/v2/auth/* - Authentication
    control_center_router,  # /api/v2/control/* - Admin control center
    
    # Media Modules
    agent,                  # /agent/* - Agent builder
    images,                 # /images/* - Image generation
    videos,                 # /videos/* - Video production
    audio,                  # /audio/* - Audio/Voice
    
    # Utility
    auth,                   # Legacy auth endpoints
    nigerian_models,        # /models/* - Nigerian model stats
)

# =============================================================================
# DEPRECATED ROUTERS (Not imported - moved to _deprecated/)
# =============================================================================
# - chat.py -> Replaced by vibe_router + enhanced_chat
# - cohere.py -> Not used in production
# - unified_chat.py -> Replaced by vibe_router
# - vibes_router.py -> Different purpose, not currently used
# - enhanced_chat.py.backup, .old, .pre-modal -> Old versions
# - audio_v2.py -> Use audio.py instead
# - curator.py -> Not active
