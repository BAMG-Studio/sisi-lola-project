"""
SISI LOLA UNIFIED CHAT ROUTER
Multimodal endpoint combining Brain + Personality + Voice
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
import asyncio
import json
import base64
from datetime import datetime

router = APIRouter(prefix="/unified", tags=["unified-multimodal"])

# Lazy import to avoid loading models on import
_service = None

def get_service():
    """Lazy-load the inference service"""
    global _service
    if _service is None:
        from app.services.unified_inference import get_inference_service
        _service = get_inference_service(load_brain=True, load_voice=True)
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
    MIXED = "mixed"

class ChatMessage(BaseModel):
    role: str = Field(..., description="Either 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class UnifiedChatRequest(BaseModel):
    """Request for unified chat endpoint"""
    message: str = Field(..., description="User's message to Sisi Lola")
    mode: ResponseMode = Field(default=ResponseMode.MULTIMODAL, description="Response mode")
    language: Language = Field(default=Language.MIXED, description="Preferred language")
    conversation_history: Optional[List[ChatMessage]] = Field(default=None, description="Previous messages")
    max_tokens: int = Field(default=512, ge=50, le=2048, description="Max response length")
    temperature: float = Field(default=0.7, ge=0.0, le=1.5, description="Creativity level")
    include_audio_base64: bool = Field(default=True, description="Include audio as base64")

class UnifiedChatResponse(BaseModel):
    """Response from unified chat endpoint"""
    text: str = Field(..., description="Text response from Sisi Lola")
    audio_base64: Optional[str] = Field(default=None, description="Audio as base64 string")
    audio_url: Optional[str] = Field(default=None, description="URL to audio file")
    language_tags: List[str] = Field(default=[], description="Languages used in response")
    personality_metrics: Dict[str, float] = Field(default={}, description="Personality trait scores")
    generation_time_ms: float = Field(default=0, description="Time to generate response")
    mode: ResponseMode = Field(default=ResponseMode.TEXT_ONLY, description="Response mode used")
    model_info: Dict[str, Any] = Field(default={}, description="Model information")

class VoiceGenerateRequest(BaseModel):
    """Request for voice-only generation"""
    text: str = Field(..., description="Text to convert to speech")
    language: Language = Field(default=Language.ENGLISH, description="Language for TTS")

class PersonalityResponse(BaseModel):
    """Personality information response"""
    name: str
    traits: Dict[str, float]
    languages: List[str]
    system_prompt_preview: str
    status: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/health")
async def health_check():
    """Check unified service health"""
    try:
        service = get_service()
        status = service.get_status()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            **status
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/chat", response_model=UnifiedChatResponse)
async def unified_chat(request: UnifiedChatRequest):
    """
    🗣️ Chat with Sisi Lola - Multimodal AI
    
    This endpoint combines:
    - 🧠 Brain: Mistral-7B fine-tuned with Nigerian languages
    - 💃 Personality: Confident, funny, charismatic Nigerian host
    - 🎙️ Voice: XTTS-v2 trained on Nigerian voice samples
    
    Set `mode` to:
    - `text`: Text response only (fastest)
    - `voice`: Voice response only
    - `multimodal`: Both text and voice (default)
    """
    try:
        service = get_service()
        
        # Convert conversation history
        history = None
        if request.conversation_history:
            history = [{"role": m.role, "content": m.content} for m in request.conversation_history]
        
        # Import response mode from service
        from app.services.unified_inference import ResponseMode as ServiceMode, Language as ServiceLang
        
        # Map enums
        service_mode = ServiceMode(request.mode.value)
        service_lang = ServiceLang(request.language.value)
        
        # Generate response
        response = await service.generate(
            message=request.message,
            mode=service_mode,
            language=service_lang,
            conversation_history=history,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        
        return UnifiedChatResponse(
            text=response.text,
            audio_base64=response.audio_base64 if request.include_audio_base64 else None,
            audio_url=response.audio_url,
            language_tags=response.language_tags or [],
            personality_metrics=response.personality_metrics or {},
            generation_time_ms=response.generation_time_ms,
            mode=ResponseMode(response.mode.value),
            model_info=service.get_status()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.post("/voice", response_model=Dict[str, Any])
async def generate_voice(request: VoiceGenerateRequest):
    """
    🎙️ Generate Sisi Lola's Voice
    
    Convert text to speech using Sisi Lola's trained voice.
    """
    try:
        service = get_service()
        
        if not service.voice_loaded:
            raise HTTPException(status_code=503, detail="Voice model not loaded")
        
        from app.services.unified_inference import Language as ServiceLang
        
        audio_base64, audio_url = await service._generate_voice(
            text=request.text,
            language=ServiceLang(request.language.value)
        )
        
        if audio_base64 is None:
            raise HTTPException(status_code=500, detail="Voice generation failed")
        
        return {
            "audio_base64": audio_base64,
            "audio_url": audio_url,
            "text": request.text,
            "language": request.language.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice generation failed: {str(e)}")

@router.get("/personality", response_model=PersonalityResponse)
async def get_personality():
    """
    💃 Get Sisi Lola's Personality
    
    View personality traits, communication style, and system prompt.
    """
    try:
        service = get_service()
        config = service.personality_config or service._get_default_personality()
        
        return PersonalityResponse(
            name=config.get("name", "Sisi Lola"),
            traits=config.get("traits", {}),
            languages=config.get("languages", []),
            system_prompt_preview=config.get("system_prompt", "")[:500] + "...",
            status="Sisi Lola is FUNNY and CHARISMATIC! 💃"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_models():
    """
    🔧 Get Model Information
    
    View loaded models and their status.
    """
    service = get_service()
    return service.get_status()


# ============================================================================
# WEBSOCKET FOR REAL-TIME CHAT
# ============================================================================

class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    🔌 WebSocket for Real-Time Chat
    
    Connect for streaming conversations with Sisi Lola.
    
    Send: {"message": "Hello", "mode": "multimodal", "language": "mixed"}
    Receive: {"text": "...", "audio_base64": "...", "complete": true}
    """
    await manager.connect(websocket)
    service = get_service()
    
    conversation_history = []
    
    try:
        while True:
            data = await websocket.receive_json()
            
            message = data.get("message", "")
            mode = data.get("mode", "multimodal")
            language = data.get("language", "mixed")
            
            # Add to history
            conversation_history.append({"role": "user", "content": message})
            
            # Generate response
            from app.services.unified_inference import ResponseMode, Language
            
            response = await service.generate(
                message=message,
                mode=ResponseMode(mode),
                language=Language(language),
                conversation_history=conversation_history[-10:],  # Keep last 10 messages
            )
            
            # Add response to history
            conversation_history.append({"role": "assistant", "content": response.text})
            
            # Send response
            await manager.send_message({
                "text": response.text,
                "audio_base64": response.audio_base64,
                "language_tags": response.language_tags,
                "generation_time_ms": response.generation_time_ms,
                "complete": True
            }, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        await manager.send_message({"error": str(e)}, websocket)
        manager.disconnect(websocket)


# ============================================================================
# CONVERSATION MANAGEMENT
# ============================================================================

# In-memory conversation store (use Redis in production)
_conversations: Dict[str, List[Dict]] = {}

@router.post("/conversation/start")
async def start_conversation():
    """Start a new conversation and get a session ID"""
    import uuid
    session_id = str(uuid.uuid4())
    _conversations[session_id] = []
    
    return {
        "session_id": session_id,
        "message": "Conversation started! Let's chat!",
        "greeting": "Hey there! How body? Na Sisi Lola be this o! I'm ready to yarn with you! 💃"
    }

@router.post("/conversation/{session_id}/message")
async def continue_conversation(session_id: str, request: UnifiedChatRequest):
    """Continue a conversation with session history"""
    
    if session_id not in _conversations:
        raise HTTPException(status_code=404, detail="Conversation not found. Start a new one!")
    
    # Get history
    history = _conversations[session_id]
    
    # Add user message
    history.append({"role": "user", "content": request.message})
    
    # Generate response with full history
    service = get_service()
    from app.services.unified_inference import ResponseMode, Language
    
    response = await service.generate(
        message=request.message,
        mode=ResponseMode(request.mode.value),
        language=Language(request.language.value),
        conversation_history=history[-20:],  # Last 20 messages
        max_tokens=request.max_tokens,
        temperature=request.temperature,
    )
    
    # Add assistant response
    history.append({"role": "assistant", "content": response.text})
    
    return UnifiedChatResponse(
        text=response.text,
        audio_base64=response.audio_base64 if request.include_audio_base64 else None,
        audio_url=response.audio_url,
        language_tags=response.language_tags or [],
        personality_metrics=response.personality_metrics or {},
        generation_time_ms=response.generation_time_ms,
        mode=ResponseMode(response.mode.value),
        model_info={"session_id": session_id, "message_count": len(history)}
    )

@router.get("/conversation/{session_id}/history")
async def get_conversation_history(session_id: str):
    """Get conversation history"""
    if session_id not in _conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {
        "session_id": session_id,
        "messages": _conversations[session_id],
        "message_count": len(_conversations[session_id])
    }

@router.delete("/conversation/{session_id}")
async def end_conversation(session_id: str):
    """End and clear a conversation"""
    if session_id in _conversations:
        del _conversations[session_id]
    
    return {"message": "Conversation ended. See you next time! 👋"}
