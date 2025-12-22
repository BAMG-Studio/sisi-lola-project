import os
import httpx
from sisi_lola_api.app.config import SisiLolaDNA


def _fallback_prompt(scenario: str, outfit: str, modality: str) -> str:
    base = (
        f"{SisiLolaDNA.VISUAL_PROMPT_CORE} "
        f"She is {scenario}. "
        f"She is wearing {outfit}. "
        f"{SisiLolaDNA.STYLE_WRAPPER}"
    )
    if modality == "video":
        base += " Cinematic camera movement, smooth motion."
    return base


async def enhance_prompt_with_perplexity(scenario: str, outfit_override: str = None, aspect_ratio: str = "16:9", modality: str = "image") -> str:
    """
    Uses Perplexity API to generate a highly detailed, DNA-consistent prompt.
    Acts as the 'Visual Director' for Sisi Lola.
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    outfit = outfit_override if outfit_override else SisiLolaDNA.OUTFIT_DNA
    if not api_key:
        return _fallback_prompt(scenario, outfit, modality)

    asset_type = "video" if modality == "video" else "image"

    system_prompt = (
        "You are the Lead Visual Director for 'Sisi Lola', a top-tier African virtual influencer. "
        f"Your task is to write a premium, photorealistic {asset_type} generation prompt. "
        "Strictly enforce her Visual DNA (face, body, skin tone) and Nigerian Yoruba heritage.\n\n"
        f"VISUAL DNA LOCK:\n{SisiLolaDNA.VISUAL_PROMPT_CORE}\n\n"
        f"DEFAULT STYLE:\n{SisiLolaDNA.STYLE_WRAPPER}\n\n"
        "RULES:\n"
        "- Preserve Yoruba facial features, dark luminous skin, and hourglass proportions.\n"
        "- Keep her mature, confident, and glamorous; never change age or body type.\n"
        "- Describe lighting, camera angle, and atmosphere; include outfit detail.\n"
        "- For VIDEO: specify camera movement (pan/dolly/zoom) and subject motion.\n"
        "- Avoid extra characters, de-aging, overexposed skin, pale tones, or fantasy skin colors.\n"
        "- Output a single cohesive paragraph only."
    )

    user_content = (
        f"SCENARIO: {scenario}\n"
        f"OUTFIT: {outfit}\n"
        f"ASPECT RATIO: {aspect_ratio}\n"
        f"TYPE: {asset_type.upper()}\n"
        "Generate the prompt now."
    )

    payload = {
        "model": SisiLolaDNA.RESEARCH_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.4,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post("https://api.perplexity.ai/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            enhanced_prompt = data["choices"][0]["message"]["content"].strip()
            if enhanced_prompt.startswith('"') and enhanced_prompt.endswith('"'):
                enhanced_prompt = enhanced_prompt[1:-1]
            # Ensure key DNA phrases stay present even if the model omits them
            if "luminous dark skin" not in enhanced_prompt.lower():
                enhanced_prompt += " Her luminous dark skin has realistic texture and gentle sheen under the light."
            if "voluptuous" not in enhanced_prompt.lower():
                enhanced_prompt += " She remains voluptuous with a confident, curvy hourglass silhouette."
            return enhanced_prompt
        except Exception as e:
            print(f"Perplexity enhancement failed: {e}")
            return _fallback_prompt(scenario, outfit, modality)
