---
description: How to maintain and verify the Gemini 3 Pro SDK integration
---

# Gemini 3 Pro SDK Checkpoint

To ensure Sisi Lola maintains her Supreme Brain and "Baddie" persona, follow these steps:

## 1. Verify Environment
Ensure the modern SDK is installed:
// turbo
`sisi_lola_api/venv/bin/python -m pip install google-genai`

## 2. Check Configuration
Verify that `sisi_lola_api/app/services/unified_inference.py` is using the `google.genai` SDK:
- It should import `from google import genai`.
- It should use `model="gemini-3-pro-preview"`.
- It should have `thinking_level="LOW"`.

## 3. Verify Persona
Check `sisi_lola_api/app/config.py` for the latest `SYSTEM_PERSONA`.
- Look for "Auntie Africa (AA)" and "EFCC Probe" in the text.

## 4. Troubleshooting
If responses fail with a 404:
- Ensure the `GOOGLE_AI_STUDIO_API_KEY` is valid.
- Check that the model name `gemini-3-pro-preview` is still available in your region.

If responses are empty or "skip":
- Check the console for `Finish Reason`. If it's `2`, ensure `safety_settings` are set to `BLOCK_NONE` in `unified_inference.py`.

## 5. Startup Command
// turbo
`sisi_lola_api/venv/bin/python -m uvicorn sisi_lola_api.app.main_updated:app --reload --host 0.0.0.0`
