# 🎬 EXTERNAL VIDEO ACQUISITION: IMPLEMENTATION GUIDE
# ═══════════════════════════════════════════════════════════════════════════════
# Week-by-week execution plan for acquiring and processing external training videos
# December 14, 2025

---

## 📋 OVERVIEW

This document provides detailed step-by-step instructions for acquiring, processing, and integrating external video sources into Sisi Lola's training pipeline.

### Expected Outcomes

| Metric | Before | After (6 Weeks) |
|--------|--------|-----------------|
| Training Examples | 600 | 3,430 (+5.7x) |
| Language Coverage | 1 | 5 |
| Cultural Authority | Self | Expert + Native |
| Cost per 1000 API calls | $2.50 | $0.0019 |

---

## 📁 DIRECTORY STRUCTURE

```
ml_training/
├── external_videos/
│   ├── tier1_ted/                    # TED Talks (CC-licensed)
│   │   ├── *.mp4
│   │   └── *.json (metadata)
│   ├── tier1_bbc/                    # BBC Learning (public use)
│   │   ├── *.mp4
│   │   └── *.json
│   ├── tier1_educational/            # Khan Academy, Crash Course
│   │   ├── *.mp4
│   │   └── *.json
│   ├── tier2_youtube/                # Permission-based YouTube
│   │   ├── *.mp4
│   │   └── *.json
│   ├── tier2_podcasts/               # Permission-based podcasts
│   │   ├── *.mp3
│   │   └── *.json
│   └── tier3_licensed/               # Paid licensed content
│       ├── *.mp4
│       └── *.json
├── datasets/
│   └── external_video_training/      # Processed transcripts
│       ├── phase1_transcripts.jsonl
│       ├── phase2_transcripts.jsonl
│       ├── phase3_transcripts.jsonl
│       └── unified_external_data.jsonl
└── scripts/
    ├── submit_external_videos.py     # Batch submission to RecCloud
    ├── process_external_transcripts.py
    └── merge_external_native.py
```

---

## 🗓️ WEEK 1: PHASE 1 EXECUTION (TIER 1 CONTENT)

### Day 1-2: Download Free Videos

#### TED Talks (3 videos)
```bash
# Option 1: Direct download from TED.com
# Go to: https://www.ted.com/talks
# Search: "Yoruba" OR "Nigerian" OR "African language"
# Click video → Share → Download (1080p MP4)

# Option 2: Using yt-dlp (recommended)
pip install yt-dlp

# Download TED Talks
yt-dlp -o "ml_training/external_videos/tier1_ted/%(title)s.%(ext)s" "TED_TALK_URL_1"
yt-dlp -o "ml_training/external_videos/tier1_ted/%(title)s.%(ext)s" "TED_TALK_URL_2"
yt-dlp -o "ml_training/external_videos/tier1_ted/%(title)s.%(ext)s" "TED_TALK_URL_3"
```

**Recommended TED Talks:**
1. "The Beauty of Yoruba" - Language learning
2. "African Storytelling Traditions" - Cultural authority
3. "African Identity in the Diaspora" - Diaspora perspective

#### BBC Learning (3 videos)
```bash
# BBC Learning English - check https://www.bbc.co.uk/learningenglish
# Download using browser extension or yt-dlp

yt-dlp -o "ml_training/external_videos/tier1_bbc/%(title)s.%(ext)s" "BBC_VIDEO_URL_1"
yt-dlp -o "ml_training/external_videos/tier1_bbc/%(title)s.%(ext)s" "BBC_VIDEO_URL_2"
yt-dlp -o "ml_training/external_videos/tier1_bbc/%(title)s.%(ext)s" "BBC_VIDEO_URL_3"
```

**Recommended BBC Content:**
1. "Nigerian English: Accents & Expressions"
2. "Business English for Africans"
3. "Pronunciation Guide: West African English"

#### Khan Academy / Educational (2 videos)
```bash
# Khan Academy: https://www.khanacademy.org
# Search: "African history" OR "West Africa"

yt-dlp -o "ml_training/external_videos/tier1_educational/%(title)s.%(ext)s" "KHAN_URL_1"
yt-dlp -o "ml_training/external_videos/tier1_educational/%(title)s.%(ext)s" "KHAN_URL_2"
```

**Recommended Educational Content:**
1. "Pre-Colonial African Empires" - Historical authority
2. "West African Trade Routes" - Cultural context

### Day 3: Create Metadata Files

For each downloaded video, create a corresponding `.json` metadata file:

```json
{
    "video_id": "EXT_TED_001",
    "title": "The Beauty of Yoruba Language",
    "creator": "Dr. Kola Akanda",
    "source_url": "https://www.ted.com/talks/example",
    "duration_seconds": 1080,
    "primary_language": "yo",
    "secondary_languages": ["en"],
    "license_type": "CC-BY-NC-ND",
    "acquisition_date": "2025-12-14",
    "tier": 1,
    "category": "language_learning",
    "attribution": "Dr. Kola Akanda, TED Talks",
    "processing_status": "pending",
    "cost": 0.00,
    "notes": "Excellent for Yoruba pronunciation and cultural significance"
}
```

### Day 4-5: Submit to RecCloud

```bash
# Run the batch submission script
cd c:/Users/POK28/Dropbox/Sisi_Lola
python ml_training/scripts/submit_external_videos.py --phase 1

# Monitor processing status
python ml_training/scripts/submit_external_videos.py --status
```

### Day 6-7: Quality Check & Processing

```bash
# Download completed transcripts
python ml_training/scripts/process_external_transcripts.py --phase 1

# Validate transcript quality
python ml_training/scripts/validate_external_transcripts.py --phase 1
```

---

## 🗓️ WEEK 2-3: PHASE 2 EXECUTION (TIER 2 CONTENT)

### Day 1-3: Creator Outreach

#### Email Template for YouTube Creators
```
Subject: Educational AI Training License Request – Sisi Lola (Nigerian AI Personality)

Dear [Creator Name],

I'm reaching out regarding your wonderful video: "[Video Title]"

We're building **Sisi Lola**, an AI personality dedicated to celebrating Nigerian language, 
culture, and diaspora experiences. Your content is authentic, insightful, and would be 
invaluable for training our model to speak with genuine cultural authority.

**What we're asking:**
- Permission to include your video in our non-commercial AI training dataset
- This means your voice and wisdom will help shape how Sisi Lola teaches others about Nigerian culture

**What you get:**
- Full attribution & credits in our documentation
- Public recognition as a contributor to cultural AI preservation
- Potential collaboration opportunities

**Fair use assurance:**
- Non-commercial educational use only
- No commercial profit from your content
- Your original work remains fully credited and unaltered

Would you be open to this? I'd love to chat more about it.

Best regards,
[Your Name]
[Your Organization]
[Contact Info]
```

#### DM Template for Social Media
```
Hi [Creator]! 👋

Love your content on [topic]! We're building Sisi Lola, an AI that celebrates 
Nigerian language and culture. Would you let us use your video for training? 

We'll give you full credit + link to your channel. 🙌
```

### Day 4-7: Download Approved Content

```bash
# Download approved YouTube videos
yt-dlp -o "ml_training/external_videos/tier2_youtube/%(title)s.%(ext)s" "APPROVED_URL_1"

# Download podcast episodes (often available as MP3)
yt-dlp -x --audio-format mp3 -o "ml_training/external_videos/tier2_podcasts/%(title)s.%(ext)s" "PODCAST_URL"
```

### Week 3: Process Tier 2

```bash
# Submit Phase 2 to RecCloud
python ml_training/scripts/submit_external_videos.py --phase 2

# Process transcripts
python ml_training/scripts/process_external_transcripts.py --phase 2
```

---

## 🗓️ WEEK 4-5: PHASE 3 EXECUTION (OPTIONAL - TIER 3)

### Licensed Content Acquisition

**Estimated Costs:**
- Nollywood clips: $500-2,000 per scene
- Comedy specials: $500-2,000 per set
- Documentary segments: $500-3,000 per segment

### Process Licensed Content

```bash
# Submit Phase 3 to RecCloud
python ml_training/scripts/submit_external_videos.py --phase 3

# Process transcripts
python ml_training/scripts/process_external_transcripts.py --phase 3
```

---

## 🗓️ WEEK 6: UNIFICATION & TRAINING

### Merge All External Data

```bash
# Merge all phases
python ml_training/scripts/merge_external_native.py

# Generate unified dataset
python ml_training/scripts/generate_brain_dataset.py --include-external
```

### Train Mistral-7B

```bash
# Start training with expanded dataset
python ml_training/modal_unified_training.py --dataset unified_with_external.jsonl
```

---

## 📊 TRACKING YOUR PROGRESS

### Progress Tracker Template

Create `external_videos_tracker.csv`:

```csv
video_id,title,creator,tier,phase,status,cost,expected_examples,date_acquired,date_processed,notes
EXT_TED_001,The Beauty of Yoruba,Dr. Kola Akanda,1,1,completed,0.00,120,2025-12-14,2025-12-15,Excellent Yoruba content
EXT_BBC_001,Nigerian English Accents,BBC Learning,1,1,processing,0.00,100,2025-12-14,,RecCloud job #12345
EXT_YT_001,Pidgin Explained,Naija Talk,2,2,pending_permission,0.00,150,,,Email sent 2025-12-14
```

### Status Definitions

| Status | Description |
|--------|-------------|
| `pending_download` | Video identified, not yet downloaded |
| `downloaded` | Video downloaded, awaiting processing |
| `pending_permission` | Awaiting creator permission |
| `permission_granted` | Permission received, ready to download |
| `permission_denied` | Creator declined, do not use |
| `processing` | Submitted to RecCloud, awaiting transcription |
| `completed` | Transcription complete, ready for training |
| `failed` | Processing failed, requires investigation |

---

## 🔧 CONFIGURATION

### RecCloud Settings for External Videos

Add to `.env`:

```bash
# External video processing settings
EXTERNAL_VIDEO_PRIMARY_LANG=yo
EXTERNAL_VIDEO_SECONDARY_LANG=en
EXTERNAL_VIDEO_SPEAKER_DETECTION=true
EXTERNAL_VIDEO_TRANSLATION=true
```

### Batch Processing Configuration

Create `ml_training/configs/external_video_config.yaml`:

```yaml
external_videos:
  source_dirs:
    tier1_ted: "ml_training/external_videos/tier1_ted"
    tier1_bbc: "ml_training/external_videos/tier1_bbc"
    tier1_educational: "ml_training/external_videos/tier1_educational"
    tier2_youtube: "ml_training/external_videos/tier2_youtube"
    tier2_podcasts: "ml_training/external_videos/tier2_podcasts"
    tier3_licensed: "ml_training/external_videos/tier3_licensed"
  
  output_dir: "ml_training/datasets/external_video_training"
  
  reccloud_settings:
    primary_language: "yo"
    secondary_language: "en"
    speaker_detection: true
    translation_enabled: true
    dual_transcript: true
  
  processing:
    batch_size: 5
    retry_attempts: 3
    polling_interval_seconds: 30
```

---

## ✅ SUCCESS CRITERIA

### Week 1 Complete When:
- [ ] 8 Tier 1 videos downloaded
- [ ] 8 metadata files created
- [ ] Phase 1 submitted to RecCloud
- [ ] ~530 training examples extracted

### Week 3 Complete When:
- [ ] 10+ creator permissions received
- [ ] 10-15 Tier 2 videos downloaded
- [ ] Phase 2 submitted to RecCloud
- [ ] ~700 additional examples extracted

### Week 6 Complete When:
- [ ] All phases merged
- [ ] Unified dataset generated (3,430+ examples)
- [ ] Mistral training completed
- [ ] Evaluation tests passed
- [ ] Sisi Lola v2 deployed

---

## 📊 COST BREAKDOWN

| Phase | Videos | Duration | RecCloud Cost | Other Costs | Total |
|-------|--------|----------|---------------|-------------|-------|
| Phase 1 | 8 | ~60 min | $0.24 | $0 | $0.24 |
| Phase 2 | 12 | ~90 min | $0.36 | $0 | $0.36 |
| Phase 3 | 5 | ~60 min | $0.24 | $2,500-10,000 | $2,524-10,024 |
| **Total** | **25** | **~210 min** | **$0.84** | **$0-10,000** | **$0.84-10,000** |

**Note:** Phase 3 is optional. Phases 1-2 alone provide 1,230+ new examples for under $1.

---

## 🚀 QUICK START COMMANDS

```bash
# Full Phase 1 execution
cd c:/Users/POK28/Dropbox/Sisi_Lola

# 1. Download videos (after installing yt-dlp)
pip install yt-dlp

# 2. Submit to RecCloud
python ml_training/scripts/submit_external_videos.py --phase 1

# 3. Check status
python ml_training/scripts/submit_external_videos.py --status

# 4. Process completed transcripts
python ml_training/scripts/process_external_transcripts.py --phase 1

# 5. Merge with native data
python ml_training/scripts/merge_external_native.py
```

---

**Ready to execute? Start with Phase 1 today!** 🚀
