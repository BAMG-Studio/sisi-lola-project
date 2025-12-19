"""
from ml_training.scripts.model_cache_manager import get_model_cache
import httpx
import time
from sisi_lola_api.app.config import MODAL_INFERENCE_URL, MODAL_TIMEOUT
SISI LOLA ENHANCED CHAT ROUTER
Multimodal endpoint with training data collection, special commands, and improved responses.

Features:
- /BAMG-STUDIO developer mode
- /REPORT training data export
- Session management with training data
- Multimodal input processing (URLs, files)
- Quality-scored responses
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

# ========================================
# MODAL INFERENCE OPTIMIZATION
# Connects to optimized Modal endpoint for 20-80x speedup
# ========================================

async def call_modal_inference(message: str, max_tokens: int = 256, temperature: float = 0.7):
    """
    Call optimized Modal inference endpoint.
    Expected response: <2 seconds (vs 30-60s with old system)
    """
    start = time.time()
    
    # OLD MODAL HTTP IMPLEMENTATION - REPLACED WITH LOCAL MODEL CACHEtry:
        async with httpx.AsyncClient(timeout=MODAL_TIMEOUT) as client:
            response = await client.post(
                MODAL_INFERENCE_URL,
                json={
                    "message": message,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                },
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            result = response.json()
            
            elapsed = time.time() - start
            print(f"[⚡ MODAL] Response in {elapsed:.2f}s - {len(result.get('text', ''))} chars")
            
            # Return just the text
            return result.get("text", "Sorry, I couldn't generate a response.")
            
    except httpx.TimeoutException as e:
        elapsed = time.time() - start
        print(f"[❌ MODAL] Timeout after {elapsed:.2f}s: {e}")
        return "I'm taking longer than expected. Please try again."
    except httpx.HTTPStatusError as e:
        print(f"[❌ MODAL] HTTP error {e.response.status_code}: {e}")
        return "Sorry, there was a server error. Please try again."
    except Exception as e:
        elapsed = time.time() - start
        print(f"[❌ MODAL] Error after {elapsed:.2f}s: {type(e).__name__}: {e}")
        return "Sorry, I encountered an error. Please try again."

import asyncio
import json
import os
from datetime import datetime

router = APIRouter(prefix="/v2", tags=["enhanced-chat"])

# Lazy import to avoid loading models on import
_service = None

def get_service():
    """Lazy-load the enhanced inference service"""
    global _service
    if _service is None:
        from sisi_lola_api.app.services.enhanced_inference import get_enhanced_inference_service
        _service = get_enhanced_inference_service(load_brain=True, load_voice=False)
    return _service


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ResponseMode(str, Enum):
    TEXT_ONLY = "text"
    VOICE_ONLY = "voice"
    MULTIMODAL = "multimodal"

class Language(str, Enum):
    ENGLISH = "en"
    PIDGIN = "pcm"
    YORUBA = "yo"
    IGBO = "ig"
    HAUSA = "ha"
    YORUNGLISH = "yoen"
    MIXED = "mixed"

class ChatMessage(BaseModel):
    role: str = Field(..., description="Either 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class EnhancedChatRequest(BaseModel):
    """Request for enhanced chat endpoint"""
    message: str = Field(..., description="User's message to Sisi Lola")
    session_id: Optional[str] = Field(default=None, description="Session ID for conversation tracking")
    mode: ResponseMode = Field(default=ResponseMode.MULTIMODAL, description="Response mode")
    language: Language = Field(default=Language.MIXED, description="Preferred language")
    max_tokens: int = Field(default=512, ge=50, le=2048, description="Max response length")
    temperature: float = Field(default=0.7, ge=0.0, le=1.5, description="Creativity level")
    include_audio_base64: bool = Field(default=False, description="Include audio as base64")

class EnhancedChatResponse(BaseModel):
    """Response from enhanced chat endpoint"""
    text: str = Field(..., description="Text response from Sisi Lola")
    audio_base64: Optional[str] = Field(default=None, description="Audio as base64 string")
    session_id: str = Field(..., description="Session ID for tracking")
    language_tags: List[str] = Field(default=[], description="Languages used in response")
    personality_metrics: Dict[str, float] = Field(default={}, description="Personality trait scores")
    generation_time_ms: float = Field(default=0, description="Time to generate response")
    mode: ResponseMode = Field(default=ResponseMode.TEXT_ONLY, description="Response mode used")
    prompt_mode: str = Field(default="standard", description="Prompt mode (standard, developer, report)")
    quality_score: float = Field(default=0, description="Response quality score 0-1")
    training_logged: bool = Field(default=False, description="Whether training data was logged")
    multimodal_analysis: Optional[Dict] = Field(default=None, description="Analysis of multimodal inputs")

class SessionInfo(BaseModel):
    """Session information"""
    session_id: str
    user_id: str
    started_at: str
    turn_count: int
    is_developer_session: bool
    primary_language: str

class TrainingReport(BaseModel):
    """Training data report"""
    generated_at: str
    summary: Dict
    quality_distribution: Dict
    language_distribution: Dict
    category_distribution: Dict
    recommendations: List[Dict]
    session_details: Optional[Dict]

class ExportRequest(BaseModel):
    """Request for training data export"""
    format: str = Field(default="jsonl", description="Export format: jsonl, huggingface")
    min_quality: str = Field(default="good", description="Minimum quality: excellent, good, needs_review, poor")
    languages: Optional[List[str]] = Field(default=None, description="Filter by languages")
    categories: Optional[List[str]] = Field(default=None, description="Filter by categories")


# ============================================================================
# MAIN CHAT ENDPOINTS
# ============================================================================

@router.get("/health")
async def health_check():
    """Check enhanced service health and status"""
    try:
        service = get_service()
        status = service.get_status()
        return {
            "status": "healthy",
            "version": "2.0",
            "timestamp": datetime.now().isoformat(),
            **status
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/chat", response_model=EnhancedChatResponse)
async def enhanced_chat(request: EnhancedChatRequest):
    """
    🗣️ Enhanced Chat with Sisi Lola
    
    Features:
    - 🧠 Improved coherence with enhanced prompts
    - 📊 Training data collection for model improvement
    - 🔗 Multimodal input (URLs, YouTube links processed)
    - 🔐 Developer mode with /BAMG-STUDIO prefix
    - 📋 Report mode with /REPORT prefix
    
    Special Commands:
    - Start message with `/BAMG-STUDIO:` for developer mode
    - Start message with `/REPORT` for training data report
    
    Languages:
    - Default: Yorunglish (Yoruba-English mix)
    - Supports: English, Pidgin, Yoruba, Igbo, Hausa
    """
    try:
        service = get_service()
        
        # Import enums from service
        from sisi_lola_api.app.services.enhanced_inference import ResponseMode as ServiceMode, Language as ServiceLang
        
        # Map enums
        service_mode = ServiceMode(request.mode.value)
        service_lang = ServiceLang(request.language.value) if request.language.value in [l.value for l in ServiceLang] else ServiceLang.MIXED
        
        # Generate response
        response = await service.generate(
            message=request.message,
            session_id=request.session_id,
            mode=service_mode,
            language=service_lang,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        
        return EnhancedChatResponse(
            text=response.text,
            audio_base64=response.audio_base64 if request.include_audio_base64 else None,
            session_id=request.session_id or "auto",
            language_tags=response.language_tags or [],
            personality_metrics=response.personality_metrics or {},
            generation_time_ms=response.generation_time_ms,
            mode=request.mode,
            prompt_mode=response.prompt_mode,
            quality_score=response.quality_score,
            training_logged=response.training_data_logged,
            multimodal_analysis=response.multimodal_analysis,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# SESSION MANAGEMENT
# ============================================================================

@router.post("/session/start")
async def start_session(
    user_id: str = Query(default="anonymous"),
    user_name: Optional[str] = Query(default=None, description="User's name for personalized greetings"),
    primary_language: str = Query(default="yorunglish", description="yorunglish, pidgin, igbo, hausa, english"),
    language_mode: str = Query(default="heavy", description="heavy, medium, light"),
    mood: str = Query(default="default", description="default, flirty, mama_bear, strict_aunty, therapist, street_smart")
):
    """
    Start a new conversation session with personality mode settings
    
    Personality Modes:
    - Language: yorunglish, pidgin, igbo, hausa, english
    - Intensity: heavy (70-90% target), medium (50-70%), light (30-50%)
    - Mood: default, flirty, mama_bear, strict_aunty, therapist, street_smart, hype_woman, storyteller
    """
    from sisi_lola_api.app.services.personality_modes import PrimaryLanguage, LanguageMode, MoodPreset
    
    service = get_service()
    
    # Parse enums safely
    try:
        primary_lang = PrimaryLanguage(primary_language)
    except ValueError:
        primary_lang = PrimaryLanguage.YORUNGLISH
    
    try:
        lang_mode = LanguageMode(language_mode)
    except ValueError:
        lang_mode = LanguageMode.HEAVY
    
    try:
        mood_preset = MoodPreset(mood)
    except ValueError:
        mood_preset = MoodPreset.DEFAULT
    
    session_id = service.start_session(
        user_id=user_id,
        user_name=user_name,
        primary_language=primary_lang,
        language_mode=lang_mode,
        mood=mood_preset
    )
    
    # Get personalized greeting
    greeting = service.get_session_greeting(session_id)
    
    return {
        "session_id": session_id,
        "user_id": user_id,
        "user_name": user_name,
        "started_at": datetime.now().isoformat(),
        "personality": {
            "language": primary_language,
            "mode": language_mode,
            "mood": mood
        },
        "greeting": greeting,
        "message": "Session started. Include session_id in subsequent requests for context."
    }

@router.post("/session/{session_id}/end")
async def end_session(session_id: str):
    """End a session and save training data"""
    service = get_service()
    result = service.end_session(session_id)
    
    return {
        "session_id": session_id,
        "ended_at": datetime.now().isoformat(),
        "training_data_saved": True,
        "details": result
    }


# ============================================================================
# TRAINING DATA ENDPOINTS
# ============================================================================

@router.get("/training/report", response_model=TrainingReport)
async def get_training_report(session_id: Optional[str] = None):
    """
    📊 Get Training Data Report
    
    Returns comprehensive statistics about collected training data:
    - Quality distribution
    - Language distribution  
    - Category distribution
    - Recommendations for improvement
    
    Optionally filter by session_id for specific session details.
    """
    service = get_service()
    report = service.get_training_report(session_id)
    
    if "error" in report:
        raise HTTPException(status_code=400, detail=report["error"])
    
    return report

@router.post("/training/export")
async def export_training_data(request: ExportRequest):
    """
    📤 Export Training Data
    
    Export collected conversation data for fine-tuning.
    
    Formats:
    - jsonl: JSON Lines format (default)
    - huggingface: HuggingFace Datasets format
    
    Quality filters:
    - excellent: Only top-quality samples
    - good: Good and excellent samples (recommended)
    - needs_review: Include samples needing review
    - poor: Include all samples
    """
    service = get_service()
    
    try:
        export_path = service.export_training_data(
            format=request.format,
            min_quality=request.min_quality
        )
        
        return {
            "status": "success",
            "export_path": export_path,
            "format": request.format,
            "min_quality": request.min_quality,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DEVELOPER MODE ENDPOINTS
# ============================================================================

@router.post("/developer/analyze-url")
async def analyze_url(url: str = Query(..., description="URL to analyze")):
    """
    🔗 Analyze URL Content
    
    Extract and analyze content from URLs:
    - YouTube videos (transcript extraction)
    - Web pages (content extraction)
    - Audio files (transcription)
    
    Returns language pattern analysis for training data.
    """
    from sisi_lola_api.app.services.multimodal_processor import get_multimodal_processor
    
    processor = get_multimodal_processor()
    result = await processor.process_input(url)
    
    if not result.success:
        raise HTTPException(status_code=400, detail=result.error)
    
    return {
        "url": url,
        "input_type": result.input_type.value,
        "success": result.success,
        "extracted_text_preview": result.extracted_text[:1000] if result.extracted_text else None,
        "language_analysis": result.language_analysis,
        "processing_time_ms": result.processing_time_ms,
        "metadata": result.metadata
    }

@router.get("/developer/prompt-preview")
async def preview_prompt(
    mode: str = Query(default="standard", description="Prompt mode: standard, developer, report"),
    language_style: str = Query(default="yorunglish", description="Language style")
):
    """
    📝 Preview System Prompt
    
    See the system prompt that will be used for a given mode.
    Useful for understanding and debugging Sisi Lola's behavior.
    """
    from sisi_lola_api.app.services.prompt_engine import get_prompt_engine, PromptMode, LanguageStyle
    
    engine = get_prompt_engine()
    
    try:
        prompt_mode = PromptMode(mode)
    except:
        prompt_mode = PromptMode.STANDARD
    
    try:
        lang_style = LanguageStyle(language_style)
    except:
        lang_style = LanguageStyle.YORUNGLISH
    
    prompt = engine.build_system_prompt(
        mode=prompt_mode,
        language_style=lang_style,
        include_intro=True
    )
    
    return {
        "mode": mode,
        "language_style": language_style,
        "prompt_length": len(prompt),
        "prompt_preview": prompt[:2000] + "..." if len(prompt) > 2000 else prompt
    }


# ============================================================================
# QUICK PROMPTS
# ============================================================================

QUICK_PROMPTS = {
    "nigerian_culture": "Tell me something fascinating about Nigerian culture",
    "make_me_laugh": "Make me laugh with some Nigerian humor",
    "teach_yoruba": "Teach me some useful Yoruba phrases",
    "about_lagos": "What's the vibe like in Lagos?",
    "afrobeats": "Recommend some fire Afrobeats music",
    "motivate_me": "I need some motivation today",
    "proverb": "Share a Nigerian proverb with me",
    "igbo_love": "How do I express love in Igbo?"
}

@router.get("/quick-prompts")
async def get_quick_prompts():
    """Get available quick prompts for demo purposes"""
    return {
        "prompts": QUICK_PROMPTS,
        "usage": "Include prompt key in your message or use /quick/{prompt_key}"
    }

@router.post("/quick/{prompt_key}")
async def quick_chat(prompt_key: str, session_id: Optional[str] = None):
    """Use a quick prompt for fast demo"""
    if prompt_key not in QUICK_PROMPTS:
        raise HTTPException(status_code=404, detail=f"Prompt key '{prompt_key}' not found")
    
    request = EnhancedChatRequest(
        message=QUICK_PROMPTS[prompt_key],
        session_id=session_id,
        mode=ResponseMode.TEXT_ONLY,
        language=Language.MIXED
    )
    
    return await enhanced_chat(request)


# ============================================================================
# PERSONALITY MODE ENDPOINTS
# ============================================================================

class PersonalityModeRequest(BaseModel):
    """Request to update personality mode"""
    primary_language: Optional[str] = Field(default=None, description="yorunglish, pidgin, igbo, hausa, english")
    language_mode: Optional[str] = Field(default=None, description="heavy, medium, light")
    mood: Optional[str] = Field(default=None, description="default, flirty, mama_bear, strict_aunty, therapist, street_smart, hype_woman, storyteller")
    user_name: Optional[str] = Field(default=None, description="User's name for personalized greetings")


@router.get("/personality/modes")
async def get_available_modes():
    """
    🎭 Get Available Personality Modes
    
    Returns all available language modes, intensity levels, and mood presets.
    """
    from sisi_lola_api.app.services.personality_modes import (
        PrimaryLanguage, LanguageMode, MoodPreset, get_personality_modes
    )
    
    engine = get_personality_modes()
    
    return {
        "languages": {
            "yorunglish": {
                "modes": ["heavy", "medium", "light"],
                "description": "Yoruba-English mix (Lagos style)",
                "heavy_ratio": "70-90% Yoruba, 10-30% English"
            },
            "pidgin": {
                "modes": ["heavy", "medium"],
                "description": "Nigerian Pidgin",
                "heavy_ratio": "80-95% Pidgin"
            },
            "igbo": {
                "modes": ["heavy"],
                "description": "Igbo language (Eastern Nigerian)",
                "heavy_ratio": "70-90% Igbo"
            },
            "hausa": {
                "modes": ["heavy"],
                "description": "Hausa language (Northern Nigerian)",
                "heavy_ratio": "70-90% Hausa"
            },
            "english": {
                "modes": ["light"],
                "description": "Nigerian English with cultural flavor"
            }
        },
        "moods": {
            mood.value: engine.MOOD_PRESETS[mood]["name"]
            for mood in MoodPreset
        },
        "mood_descriptions": {
            "default": "Warm, balanced big-sister energy",
            "flirty": "Playful, teasing, charming",
            "mama_bear": "Protective, nurturing, unconditional care",
            "strict_aunty": "Firm but loving, naming ceremony energy",
            "therapist": "Calm, empathetic, wise counselor",
            "street_smart": "Lagos Island/Yaba savvy, quick-witted",
            "hype_woman": "Enthusiastic cheerleader, celebration mode",
            "storyteller": "Rich narrative, proverbs, ancestral wisdom"
        }
    }


@router.post("/session/{session_id}/personality")
async def update_session_personality(session_id: str, request: PersonalityModeRequest):
    """
    🎭 Update Session Personality Mode
    
    Change language intensity and mood for the current session.
    Changes take effect immediately for subsequent messages.
    """
    from sisi_lola_api.app.services.personality_modes import PrimaryLanguage, LanguageMode, MoodPreset
    
    service = get_service()
    
    # Parse enums safely
    primary_lang = None
    lang_mode = None
    mood = None
    
    if request.primary_language:
        try:
            primary_lang = PrimaryLanguage(request.primary_language)
        except ValueError:
            raise HTTPException(400, f"Invalid language: {request.primary_language}")
    
    if request.language_mode:
        try:
            lang_mode = LanguageMode(request.language_mode)
        except ValueError:
            raise HTTPException(400, f"Invalid mode: {request.language_mode}")
    
    if request.mood:
        try:
            mood = MoodPreset(request.mood)
        except ValueError:
            raise HTTPException(400, f"Invalid mood: {request.mood}")
    
    success = service.update_session_personality(
        session_id=session_id,
        primary_language=primary_lang,
        language_mode=lang_mode,
        mood=mood,
        user_name=request.user_name
    )
    
    if not success:
        raise HTTPException(404, f"Session not found: {session_id}")
    
    # Get personalized greeting
    greeting = service.get_session_greeting(session_id)
    
    return {
        "status": "success",
        "session_id": session_id,
        "updated": {
            "primary_language": request.primary_language,
            "language_mode": request.language_mode,
            "mood": request.mood,
            "user_name": request.user_name
        },
        "greeting": greeting
    }


@router.get("/session/{session_id}/greeting")
async def get_session_greeting(session_id: str):
    """Get a personalized greeting for the current session's personality mode"""
    service = get_service()
    greeting = service.get_session_greeting(session_id)
    return {"session_id": session_id, "greeting": greeting}


# ============================================================================
# TRAINING REINFORCEMENT ENDPOINTS  
# ============================================================================

@router.get("/training/dashboard")
async def get_training_dashboard():
    """
    📊 Get Training Reinforcement Dashboard
    
    Returns:
    - Today's training focus
    - Weekly language focus
    - Training statistics
    - Next training prompt
    """
    from sisi_lola_api.app.services.training_reinforcement import get_training_engine
    
    engine = get_training_engine()
    dashboard = engine.get_training_dashboard()
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        **dashboard
    }


@router.get("/training/schedule")
async def get_training_schedule():
    """
    📅 Get Training Schedule
    
    Returns the daily and weekly training schedule:
    - Daily: Focus areas by day of week
    - Weekly: Language focus by week number
    """
    from sisi_lola_api.app.services.training_reinforcement import get_training_engine
    
    engine = get_training_engine()
    focus, language, description = engine.get_today_focus()
    
    return {
        "current": {
            "day_focus": focus.value,
            "language_focus": language,
            "description": description,
            "day_of_week": datetime.now().strftime("%A"),
            "week_number": engine.schedule.current_week
        },
        "daily_schedule": {
            "Monday": "greetings - Greeting & Opener styles",
            "Tuesday": "empathy - Encouragement & Empathy phrases",
            "Wednesday": "teasing - Teasing with love patterns",
            "Thursday": "success - Celebration templates",
            "Friday": "storytelling - Story/Proverb injection",
            "Saturday": "humor - Mix + humor",
            "Sunday": "cultural - Cultural wisdom"
        },
        "weekly_rotation": {
            "Week 1": "Yorunglish Heavy Mastery",
            "Week 2": "Pidgin Heavy Mastery",
            "Week 3": "Igbo Pattern Integration",
            "Week 4": "Hausa Pattern Integration"
        }
    }


@router.get("/training/prompt")
async def get_training_prompt(focus: Optional[str] = None):
    """
    📝 Get Training Prompt
    
    Generate a training prompt for the current focus area.
    Use this to practice and improve specific personality aspects.
    """
    from sisi_lola_api.app.services.training_reinforcement import get_training_engine, TrainingFocus
    
    engine = get_training_engine()
    
    if focus:
        try:
            training_focus = TrainingFocus(focus)
        except ValueError:
            raise HTTPException(400, f"Invalid focus: {focus}")
    else:
        training_focus = None
    
    prompt = engine.generate_training_prompt(training_focus)
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        **prompt
    }


@router.get("/training/weekly-report")
async def get_weekly_report():
    """
    📊 Get Weekly Training Report
    
    Summarizes the past week's training sessions and progress.
    """
    from sisi_lola_api.app.services.training_reinforcement import get_training_engine
    
    engine = get_training_engine()
    report = engine.get_weekly_report()
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        **report
    }


@router.get("/training/monthly-evolution")
async def get_monthly_evolution_plan():
    """
    🚀 Get Monthly Evolution Plan
    
    Analyze training data and generate recommendations for model improvement.
    """
    from sisi_lola_api.app.services.training_reinforcement import get_training_engine
    
    engine = get_training_engine()
    plan = engine.get_monthly_evolution_plan()
    
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        **plan
    }


# ============================================================================
# WEBSOCKET FOR REAL-TIME CHAT
# ============================================================================

class ConnectionManager:
    """Manage WebSocket connections"""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, message: dict, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    🔌 WebSocket Chat
    
    Real-time bidirectional chat with Sisi Lola.
    
    Send JSON:
    {
        "message": "Your message",
        "language": "mixed",
        "temperature": 0.7
    }
    
    Receive JSON:
    {
        "type": "response",
        "text": "Sisi Lola's response",
        "language_tags": ["EN", "NP"],
        "quality_score": 0.85
    }
    """
    await manager.connect(websocket, session_id)
    
    service = get_service()
    service.start_session(session_id)
    
    try:
        # Send welcome message
        await manager.send_message({
            "type": "welcome",
            "message": "Connected to Sisi Lola! Send your message.",
            "session_id": session_id
        }, session_id)
        
        while True:
            data = await websocket.receive_json()
            
            message = data.get("message", "")
            language = data.get("language", "mixed")
            temperature = data.get("temperature", 0.7)
            
            # Import enums
            from sisi_lola_api.app.services.enhanced_inference import ResponseMode as ServiceMode, Language as ServiceLang
            
            # Generate response
            response = await service.generate(
                message=message,
                session_id=session_id,
                mode=ServiceMode.TEXT_ONLY,
                language=ServiceLang(language) if language in [l.value for l in ServiceLang] else ServiceLang.MIXED,
                temperature=temperature,
            )
            
            # Send response
            await manager.send_message({
                "type": "response",
                "text": response.text,
                "language_tags": response.language_tags,
                "quality_score": response.quality_score,
                "generation_time_ms": response.generation_time_ms,
                "prompt_mode": response.prompt_mode,
            }, session_id)
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        service.end_session(session_id)
