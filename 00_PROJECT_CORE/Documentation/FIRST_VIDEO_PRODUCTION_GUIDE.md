# First Video Production Guide - Sisi Lola

## 🎬 Complete Pipeline: Script → Voice → Video → Upload

---

## Prerequisites

### 1. Authenticate YouTube (One-Time)
```bash
cd 00_PROJECT_CORE/Scripts
python youtube_content_uploader.py
```
- Opens browser for OAuth consent
- Saves `youtube_token.pickle` for future uploads

### 2. Verify API Keys in `.env`
- ✅ OPENAI_API_KEY (script generation)
- ✅ HEYGEN_API_KEY (avatar video)
- ✅ HEYGEN_AVATAR_ID (Sisi Lola avatar)
- ✅ HEYGEN_VOICE_ID (African voice)
- ✅ ELEVENLABS_API_KEY (voice synthesis - optional)
- ✅ YOUTUBE_OAUTH_CLIENT_ID
- ✅ YOUTUBE_OAUTH_CLIENT_SECRET

---

## 🚀 Quick Start

### Option A: Automated Pipeline
```bash
cd 00_PROJECT_CORE/Scripts
python generate_first_video.py
```

**What it does:**
1. Generates 60-second intro script with OpenAI
2. Creates avatar video with HeyGen (Sisi Lola avatar + African voice)
3. Prompts for YouTube upload confirmation
4. Uploads with optimized title, description, tags
5. Logs everything to `06_RENDER_OUTPUT/youtube_videos/`

**Timeline:** ~5-10 minutes (HeyGen processing time)

---

## 📋 Step-by-Step Breakdown

### Step 1: Script Generation (OpenAI)
**Prompt:**
```
Create a 60-second introduction script for Sisi Lola, 
an AI-powered African cultural ambassador.

Requirements:
- Warm, authentic African voice
- Introduce who Sisi Lola is
- Mission: celebrate African culture, innovation, community
- Invite viewers to subscribe
- Natural, conversational tone
- Include African greetings (Jambo, Sawubona)
```

**Output:** `script_YYYYMMDD_HHMMSS.txt`

---

### Step 2: Avatar Video (HeyGen)
**API Call:**
```json
{
  "video_inputs": [{
    "character": {
      "type": "avatar",
      "avatar_id": "4230c36fe6c540149824db9ad71eec3c",
      "avatar_style": "normal"
    },
    "voice": {
      "type": "text",
      "input_text": "<script>",
      "voice_id": "a2551e97ae4d48faa98aa17d79b732c9"
    },
    "background": {
      "type": "color",
      "value": "#1a1a2e"
    }
  }],
  "dimension": {"width": 1920, "height": 1080},
  "aspect_ratio": "16:9"
}
```

**Processing:** 3-8 minutes
**Output:** `heygen_YYYYMMDD_HHMMSS.mp4`

---

### Step 3: Background Music (Manual - Optional)
**Afrobeat Track Recommendations:**
- Use royalty-free Afrobeat from YouTube Audio Library
- Or: Epidemic Sound, Artlist (subscription required)
- Volume: 20-30% (voice should be primary)

**Tools:**
- **DaVinci Resolve** (free)
- **Adobe Premiere Pro**
- **CapCut** (free, simple)

**Quick Edit:**
1. Import HeyGen video
2. Add Afrobeat track to audio layer
3. Lower music volume to 20%
4. Export as MP4 (H.264, 1920x1080, 30fps)

---

### Step 4: YouTube Upload
**Automated via Script:**
```python
upload_video(
    video_path='path/to/final.mp4',
    title='Meet Sisi Lola - Your AI Guide to African Culture 🌍',
    description='...',
    tags=['Sisi Lola', 'African Culture', 'AI Influencer', ...],
    category_id='22',  # People & Blogs
    privacy='public'
)
```

**Metadata:**
- **Title:** "Meet Sisi Lola - Your AI Guide to African Culture 🌍"
- **Description:** Script excerpt + channel mission + call-to-action
- **Tags:** Sisi Lola, African Culture, AI Influencer, Africa, Innovation, Afrobeat
- **Thumbnail:** Custom (create in Canva - 1280x720px)
- **Category:** People & Blogs
- **Playlist:** "Introduction" (create first)

---

## 🎯 Optimization Checklist

### Before Upload
- [ ] Video is 1920x1080, 30fps, H.264
- [ ] Audio is clear, voice at -3dB, music at -18dB
- [ ] First 8 seconds are engaging (hook)
- [ ] Includes call-to-action (subscribe)
- [ ] Closed captions added (YouTube auto-generates, review)

### After Upload
- [ ] Add custom thumbnail (Canva template)
- [ ] Add to "Introduction" playlist
- [ ] Add end screen (subscribe button + next video)
- [ ] Add cards at 30s and 50s (subscribe prompts)
- [ ] Pin comment: "Welcome! Where are you watching from? 🌍"
- [ ] Share on other platforms (when ready)

---

## 📊 Success Metrics (Week 1)

**Target:**
- 100+ views
- 10+ subscribers
- 5+ comments
- 50%+ watch time

**Track:**
```bash
python youtube_analytics.py
```

---

## 🔄 Content Pipeline (After First Video)

### Week 1: Foundation (3 videos)
1. ✅ Introduction (this video)
2. "What is African Innovation?" (educational)
3. "African Languages: Swahili Basics" (tutorial)

### Week 2: Engagement (3 videos)
4. "African Music: Afrobeat Explained" (entertainment)
5. "Q&A: Your Questions About Africa" (community)
6. "African Fashion: Ankara Styles" (cultural)

### Ongoing: 3 videos/week
- Monday: Educational
- Wednesday: Entertainment/Cultural
- Friday: Community/Q&A

---

## 🎨 Thumbnail Template (Canva)

**Specs:** 1280x720px
**Elements:**
- Sisi Lola avatar (large, centered)
- Bold text: "MEET SISI LOLA"
- Subtitle: "AI Guide to African Culture"
- African-inspired background (warm colors, patterns)
- Emoji: 🌍✨

**Colors:**
- Primary: #FF6B35 (orange)
- Secondary: #F7931E (gold)
- Accent: #1A1A2E (dark blue)
- Text: White with dark outline

---

## 🐛 Troubleshooting

### HeyGen Video Fails
- Check API key is valid
- Verify avatar_id and voice_id are correct
- Script must be under 500 words
- Wait 10 minutes, retry if timeout

### YouTube Upload Fails
- Re-authenticate: delete `youtube_token.pickle`, run uploader again
- Check video file is valid MP4
- Verify OAuth credentials in `.env`
- Check YouTube account is in good standing

### Voice Sounds Off
- HeyGen voice_id must match African accent
- Alternative: Use ElevenLabs for voice, then sync with HeyGen avatar
- Test different voice_ids in HeyGen dashboard

---

## 📝 Production Log Template

```
VIDEO PRODUCTION LOG
====================
Date: YYYY-MM-DD
Video #: 1
Title: Meet Sisi Lola

SCRIPT:
-------
[Paste script here]

GENERATION:
-----------
- Script generated: HH:MM
- HeyGen video started: HH:MM
- HeyGen video completed: HH:MM
- Music added: HH:MM
- Final export: HH:MM

UPLOAD:
-------
- YouTube upload: HH:MM
- Video ID: [YouTube ID]
- URL: https://youtu.be/[ID]

METRICS (24h):
--------------
- Views: 
- Likes:
- Comments:
- Subscribers gained:
- Watch time:

NOTES:
------
[Any observations, improvements for next video]
```

---

## ✅ Ready to Launch!

Run the pipeline:
```bash
python generate_first_video.py
```

Monitor progress, confirm upload, and celebrate your first video! 🎉

---

## 🔗 Resources

- **HeyGen Dashboard:** https://app.heygen.com
- **YouTube Studio:** https://studio.youtube.com
- **Canva Templates:** https://canva.com
- **Afrobeat Music:** YouTube Audio Library → Genre: World
- **Analytics:** `python youtube_analytics.py`

---

**Next:** After first video is live, generate videos 2-3 using the same pipeline with different scripts.
