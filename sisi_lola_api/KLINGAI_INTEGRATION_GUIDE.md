# KlingAI Integration Guide for Sisi Lola

## What is KlingAI?

KlingAI is a powerful AI platform that generates both **images** and **videos** from text prompts. We're using it instead of Midjourney because it provides:
- **Video generation** (Midjourney only does images)
- **API access** (easier automation)
- **Consistent character generation** when we inject our DNA prompts

---

## Authentication Setup (JWT)

KlingAI now requires a short-lived JWT that is signed with your **Access Key** and **Secret Key**. The API service generates this token per request, so you only need to supply the credentials via `.env`:

```
KLINGAI_API_DOMAIN=https://api-singapore.klingai.com
KLINGAI_ACCESS_KEY=your_access_key
KLINGAI_SECRET_KEY=your_secret_key
```

After updating `.env`, restart the server (`RELOAD=0 HOST=127.0.0.1 PORT=8000 bash start_server.sh`) and confirm readiness:

```bash
curl -s http://127.0.0.1:8000/ | jq '.klingai_credentials_loaded'
# Expected output: true
```

If the credentials are missing, image/video endpoints automatically respond with a simulation payload instead of calling KlingAI.

## How the Integration Works

### Curl Playbook (with OpenAI fallback)

Use these ready-to-go commands when validating the stack locally:

```bash
# Inspect API readiness
curl -s http://127.0.0.1:8000/ | jq

# Generate an image (router now falls back to OpenAI if KlingAI throttles)
curl -s -X POST "http://127.0.0.1:8000/images/generate" \
  -H "Content-Type: application/json" \
  -d '{"scenario":"hosting a fintech summit in Lagos","aspect_ratio":"16:9"}' | jq

# Generate a video stub
curl -s -X POST "http://127.0.0.1:8000/videos/generate" \
  -H "Content-Type: application/json" \
  -d '{"scenario":"walking down a Lagos fashion runway","duration":5}' | jq

# Print JWT + API health in one shot
cd 00_PROJECT_CORE/Scripts && RELOAD=0 python3 klingai_status.py
```

The helper script prints the live JWT so you can paste it into KlingAI’s “JWT Verification” modal without digging through code.

### 1. **Image Generation** (`/images/generate`)

**What happens when you call this endpoint:**

```
User Request: "Sisi hosting a tech conference"
                ↓
System reads DNA: "Portrait of Sisi Lola, voluptuous, mature, Yoruba..."
                ↓
System combines: "Portrait of... She is hosting a tech conference... wearing [outfit]"
                ↓
KlingAI receives: Full prompt with DNA injected
                ↓
KlingAI returns: Image URL matching her exact look
```

**Example API Call:**
```bash
curl -X POST "http://127.0.0.1:8000/images/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "scenario": "hosting a tech conference on stage",
       "aspect_ratio": "16:9"
     }'
```

**Response:**
```json
{
  "status": "success",
  "injected_prompt": "Portrait of Sisi Lola, a breathtakingly beautiful...",
  "reference_images": ["assets/dna/sisi_dna_v1.png"],
  "dna_integrity": "100%",
  "result": {
    "data": [{"url": "https://klingai.com/generated_image.jpg"}]
  },
  "provider": "KlingAI"
}
```

---

### 2. **Video Generation** (`/videos/generate`)

**What happens:**

```
User Request: "Sisi walking down a runway"
                ↓
System reads DNA: Same visual description
                ↓
System adds: "Cinematic camera movement, smooth motion"
                ↓
KlingAI receives: Full video prompt
                ↓
KlingAI returns: Video URL (5-second clip by default)
```

**Example API Call:**
```bash
curl -X POST "http://127.0.0.1:8000/videos/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "scenario": "walking down a Lagos fashion runway",
       "duration": 5,
       "aspect_ratio": "16:9"
     }'
```

---

## DNA Enforcement Strategy

### The Problem:
If you just type "A woman hosting a show" into KlingAI 200 times, you'll get 200 different women.

### Our Solution:
Every request **automatically includes**:
1. Her physical description (`VISUAL_PROMPT_CORE`)
2. Her default outfit (`OUTFIT_DNA`)
3. Photography style (`STYLE_WRAPPER`)
4. Reference images (`DNA_IMAGE_PATHS`)

**This means you can't accidentally create an "off-brand" asset.** The system won't let you.

---

## Outfit Override Feature

Sometimes you want her in a different outfit (e.g., swimwear for a beach scene, gym wear for fitness content).

**Default behavior:**
```bash
# Uses her traditional Yoruba outfit (default)
curl -X POST "http://127.0.0.1:8000/images/generate" \
     -d '{"scenario": "hosting a podcast"}'
```

**Override:**
```bash
# Use a custom outfit
curl -X POST "http://127.0.0.1:8000/images/generate" \
     -d '{
       "scenario": "at a beach resort",
       "outfit_override": "Elegant white linen summer dress with gold accessories"
     }'
```

**Important:** Even with outfit override, her face, body type, and skin tone remain locked to the DNA.

---

## Next Steps: Asset Generation Workflow

### Step 1: Generate Your First Test Image
```bash
curl -X POST "http://127.0.0.1:8000/images/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "scenario": "smiling at the camera in a professional studio",
       "aspect_ratio": "1:1"
     }'
```

### Step 2: Validate DNA Consistency
Compare the KlingAI output to your reference images (`sisi_dna_v1.png` and `sisi_dna_v2.png`). Check:
- ✅ Same facial features?
- ✅ Same body type?
- ✅ Same skin tone?

If **YES** → Proceed to mass generation.  
If **NO** → We need to refine the `VISUAL_PROMPT_CORE` in `app/config.py`.

### Step 3: Batch Generate the 200+ Assets
We'll create a Python script that reads your CSV manifest and calls the API for each asset, saving the results automatically.

---

## Technical Notes

### API Endpoints:
- **KlingAI Image Generation**: `https://api-singapore.klingai.com/v1/images/generations`
- **KlingAI Video Generation**: `https://api-singapore.klingai.com/v1/videos/text2video`

### Rate Limits:
KlingAI may have rate limits. If you're generating 200+ assets, we should:
1. Add delays between requests (e.g., 2 seconds)
2. Implement retry logic for failed requests

**Detecting a 429**

- Our API now surfaces KlingAI HTTP errors with a structured JSON payload: `status: "error"`, `message: "KlingAI generation failed: 429 Too Many Requests"`, plus the DNA metadata.
- The CLI helper (`python3 klingai_status.py`) does not hit KlingAI but is useful to confirm JWT validity before re-running.

**Recovery Steps**

1. Pause requests for 60–120 seconds or until the KlingAI dashboard shows quota available.
2. Reduce concurrency and insert `time.sleep(2)` (the batch generator will include this delay).
3. If rate-limited frequently, consider requesting a higher plan or distributing runs across multiple KlingAI regions/keys.

### Cost Management:
Each generation costs credits. Track your usage to avoid surprises.

---

## Troubleshooting

**Problem:** "KlingAI generation failed: 401 Unauthorized"  
**Solution:** Ensure both `KLINGAI_ACCESS_KEY` and `KLINGAI_SECRET_KEY` are present in `.env` and that `/` reports `"klingai_credentials_loaded": true`.

**Problem:** Generated images don't look like the DNA references  
**Solution:** The `VISUAL_PROMPT_CORE` may need to be more specific. We can add details like:
- Specific facial features (e.g., "almond-shaped eyes, full lips")
- Body measurements (e.g., "hourglass figure with 38-26-40 proportions")

**Problem:** Videos are too short  
**Solution:** Increase the `duration` parameter (max is usually 10 seconds for KlingAI).

**Problem:** "KlingAI generation failed: 429 Too Many Requests"  
**Solution:** Wait for the rate limit window to reset, then resume with throttled requests (2s delay). The API still returns the DNA prompt/reference data so the quick test remains useful even when KlingAI throttles.
If the image request includes `"provider": "OpenAI"`, the fallback generated the asset successfully using OpenAI Images while logging the original KlingAI failure in `fallback_reason`.
