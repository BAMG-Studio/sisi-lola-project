from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import time

from app.config import SisiLolaDNA
from app.dependencies.auth import require_api_key
from app.services import auth_store
from app.utils.heygen import poll_heygen_video, start_heygen_video
from app.utils.perplexity import enhance_prompt_with_perplexity
from app.utils.perplexity_generation import generate_perplexity_video
from app.utils.video_stub import create_stub_video
from app.utils.openai_images import generate_openai_image

router = APIRouter()

class VideoRequest(BaseModel):
    scenario: str  # e.g., "Walking down a runway"
    duration: int = 5  # Duration in seconds
    aspect_ratio: str = "16:9"
    script: str | None = None  # Optional explicit teleprompter script
    avatar_id: str | None = None  # Override default HeyGen avatar
    voice_id: str | None = None  # Override default HeyGen voice
    caption: bool = False  # Toggle burned-in captions

@router.get("/")
async def video_status():
    return {"status": "Video Production Module Online", "provider": "HeyGen"}

@router.post("/generate")
async def generate_sisi_video(request: VideoRequest, ctx=Depends(require_api_key)):
    """
    Generates a video of Sisi Lola using HeyGen avatars, enforcing her visual DNA.
    """
    started = time.time()
    # Rate limit per key and endpoint
    try:
        auth_store.enforce_rate_limit(ctx, "/videos/generate")
    except Exception as limit_err:
        raise HTTPException(status_code=429, detail=str(limit_err))

    # DNA Injection: Uses Perplexity to generate a cinematic video prompt for guidance/meta
    final_prompt = await enhance_prompt_with_perplexity(
        scenario=request.scenario,
        aspect_ratio=request.aspect_ratio,
        modality="video",
    )

    script = request.script or request.scenario

    base_response = {
        "injected_prompt": final_prompt,
        "reference_images": SisiLolaDNA.DNA_IMAGE_PATHS,
        "dna_integrity": "100%",
        "provider": "HeyGen",
        "script": script,
    }

    # HeyGen-first generation
    try:
        start_payload = await start_heygen_video(
            script=script,
            aspect_ratio=request.aspect_ratio,
            avatar_id=request.avatar_id,
            voice_id=request.voice_id,
            caption=request.caption,
        )
        video_id = start_payload.get("data", {}).get("video_id") or start_payload.get("video_id")
        if not video_id:
            raise RuntimeError("HeyGen did not return a video_id.")

        status_payload = await poll_heygen_video(video_id)
        media_url = status_payload.get("data", {}).get("video_url") or status_payload.get("video_url")

        payload = {
            **base_response,
            "status": "success",
            "result": {
                "video_id": video_id,
                "media_url": media_url,
                "start_response": start_payload,
                "status_response": status_payload,
            },
        }
        auth_store.log_usage(ctx, "/videos/generate", "success", duration_ms=int((time.time() - started) * 1000), result_url=media_url)
        return payload

    except ValueError as cred_error:
        error_resp = {
            **base_response,
            "status": "simulation",
            "message": str(cred_error),
        }
        auth_store.log_usage(ctx, "/videos/generate", "error", duration_ms=int((time.time() - started) * 1000), error=str(cred_error))
        return error_resp
    except Exception as heygen_error:
        base_response["heygen_error"] = str(heygen_error)

    # Perplexity fallback if HeyGen fails
    try:
        pplx_result = await generate_perplexity_video(final_prompt, request.duration, request.aspect_ratio)
        media_url = pplx_result.get("media_url")
        if media_url:
            payload = {
                **base_response,
                "status": "success",
                "provider": "Perplexity",
                "result": pplx_result,
            }
            auth_store.log_usage(ctx, "/videos/generate", "success", duration_ms=int((time.time() - started) * 1000), result_url=media_url)
            return payload
    except Exception as pplx_error:
        base_response["perplexity_error"] = str(pplx_error)

    error_payload = {
        **base_response,
        "status": "error",
        "message": base_response.get("heygen_error", "Video generation failed."),
    }

    # Fallback path: generate a still via OpenAI and wrap as stub mp4
    try:
        openai_image = await generate_openai_image(final_prompt, request.aspect_ratio)
        img_url = openai_image["data"][0]["url"]
        video_path, _ = create_stub_video(img_url, duration=request.duration, aspect_ratio=request.aspect_ratio)
        payload = {
            **base_response,
            "status": "success",
            "provider": "OpenAI-stub",
            "fallback_reason": error_payload["message"],
            "result": {
                "media_url": video_path,
                "local_path": video_path,
                "source_image": img_url,
                "note": "Stub video generated from still image due to provider unavailability.",
            },
        }
        auth_store.log_usage(ctx, "/videos/generate", "success", duration_ms=int((time.time() - started) * 1000), result_url=video_path)
        return payload
    except Exception as stub_error:
        error_payload["fallback_stub_error"] = str(stub_error)
        auth_store.log_usage(ctx, "/videos/generate", "error", duration_ms=int((time.time() - started) * 1000), error=str(stub_error))
        return JSONResponse(error_payload, status_code=502)
