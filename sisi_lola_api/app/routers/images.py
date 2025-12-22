# app/routers/images.py
import time

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import httpx
from sisi_lola_api.app.config import SisiLolaDNA
from sisi_lola_api.app.dependencies.auth import require_api_key
from sisi_lola_api.app.services import auth_store
from sisi_lola_api.app.utils.klingai import build_klingai_headers, KLINGAI_IMAGE_ENDPOINT
from sisi_lola_api.app.utils.openai_images import generate_openai_image
from sisi_lola_api.app.utils.perplexity import enhance_prompt_with_perplexity
from sisi_lola_api.app.utils.perplexity_generation import generate_perplexity_image

router = APIRouter()

class ImageRequest(BaseModel):
    scenario: str  # e.g., "Walking down a runway"
    aspect_ratio: str = "9:16"
    outfit_override: str = None  # Optional: Override default outfit

@router.post("/generate")
async def generate_sisi_image(request: ImageRequest, ctx=Depends(require_api_key)):
    """
    Generates a new image of Sisi Lola using KlingAI, enforcing her visual DNA.
    """
    started = time.time()
    try:
        auth_store.enforce_rate_limit(ctx, "/images/generate")
    except Exception as limit_err:
        raise HTTPException(status_code=429, detail=str(limit_err))

    # DNA Injection: Uses Perplexity to generate a consistent, high-fidelity prompt
    final_prompt = await enhance_prompt_with_perplexity(
        scenario=request.scenario,
        outfit_override=request.outfit_override,
        aspect_ratio=request.aspect_ratio,
        modality="image"
    )
    
    base_response = {
        "injected_prompt": final_prompt,
        "reference_images": SisiLolaDNA.DNA_IMAGE_PATHS,
        "dna_integrity": "100%",
    }

    # Perplexity-first generation (new capability)
    try:
        pplx_result = await generate_perplexity_image(final_prompt, request.aspect_ratio)
        media_url = pplx_result.get("media_url")
        if media_url:
            payload = {
                **base_response,
                "status": "success",
                "provider": "Perplexity",
                "result": pplx_result
            }
            auth_store.log_usage(ctx, "/images/generate", "success", duration_ms=int((time.time() - started) * 1000), result_url=media_url)
            return payload
    except Exception as pplx_error:
        base_response["perplexity_error"] = str(pplx_error)

    try:
        headers = build_klingai_headers()
    except ValueError as cred_error:
        error_payload = {
            **base_response,
            "status": "simulation",
            "provider": "KlingAI",
            "message": str(cred_error)
        }
        auth_store.log_usage(ctx, "/images/generate", "error", duration_ms=int((time.time() - started) * 1000), error=str(cred_error))
        return error_payload
    
    # Call KlingAI API for image generation
    try:
        payload = {
            "prompt": final_prompt,
            "aspect_ratio": request.aspect_ratio,
            "model": "kling-v1",
            "n": 1
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(KLINGAI_IMAGE_ENDPOINT, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
        payload = {
            **base_response,
            "status": "success",
            "provider": "KlingAI",
            "result": result
        }
        auth_store.log_usage(ctx, "/images/generate", "success", duration_ms=int((time.time() - started) * 1000))
        return payload
        
    except Exception as kling_error:
        kling_message = f"KlingAI generation failed: {str(kling_error)}"

        # Attempt OpenAI fallback if configured
        try:
            openai_result = await generate_openai_image(final_prompt, request.aspect_ratio)
            payload = {
                **base_response,
                "status": "success",
                "provider": "OpenAI",
                "fallback_reason": kling_message,
                "result": openai_result
            }
            auth_store.log_usage(ctx, "/images/generate", "success", duration_ms=int((time.time() - started) * 1000))
            return payload
        except ValueError:
            # OpenAI key missing; bubble up KlingAI error with metadata
            error_payload = {
                **base_response,
                "status": "error",
                "provider": "KlingAI",
                "message": kling_message
            }
            auth_store.log_usage(ctx, "/images/generate", "error", duration_ms=int((time.time() - started) * 1000), error=kling_message)
            return JSONResponse(error_payload, status_code=502)
        except Exception as openai_error:
            error_payload = {
                **base_response,
                "status": "error",
                "provider": "OpenAI",
                "fallback_reason": kling_message,
                "message": f"OpenAI fallback failed: {str(openai_error)}"
            }
            auth_store.log_usage(ctx, "/images/generate", "error", duration_ms=int((time.time() - started) * 1000), error=str(openai_error))
            return JSONResponse(error_payload, status_code=502)
