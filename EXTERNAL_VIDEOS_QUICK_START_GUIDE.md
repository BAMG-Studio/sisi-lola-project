# 🚀 EXTERNAL VIDEOS QUICK START GUIDE
# ═══════════════════════════════════════════════════════════════════════════════
# Copy-paste instructions to get started TODAY
# December 14, 2025

---

## ⚡ START HERE (15 MINUTES TO FIRST DOWNLOAD)

### Step 1: Install Required Tools (2 minutes)

```bash
# Open WSL terminal and run:
pip install yt-dlp requests python-dotenv

# Verify installation
yt-dlp --version
```

### Step 2: Create Directory Structure (1 minute)

```bash
# Navigate to project
cd /mnt/c/Users/POK28/Dropbox/Sisi_Lola

# Create external video directories (already done, but verify)
mkdir -p ml_training/external_videos/{tier1_ted,tier1_bbc,tier1_educational,tier2_youtube,tier2_podcasts,tier3_licensed}
mkdir -p ml_training/datasets/external_video_training
```

### Step 3: Download First Video (5 minutes)

```bash
# Download a sample TED Talk (replace URL with actual video)
cd /mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/external_videos/tier1_ted

# Example download command
yt-dlp -o "%(title)s.%(ext)s" "https://www.ted.com/talks/EXAMPLE_VIDEO"
```

---

## 📥 PHASE 1: TIER 1 DOWNLOADS (Today - $0)

### TED Talks (3 videos)

**Search:** Go to https://www.ted.com/talks and search:
- "Yoruba" OR "Nigerian" OR "African language" OR "African identity"

**Recommended Videos:**
1. Search: "The danger of a single story" (Chimamanda Ngozi Adichie)
2. Search: "African storytelling" 
3. Search: "Language preservation Africa"

**Download Commands:**
```bash
cd /mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/external_videos/tier1_ted

# Download each video (replace with actual URLs)
yt-dlp -o "%(title)s.%(ext)s" "TED_URL_1"
yt-dlp -o "%(title)s.%(ext)s" "TED_URL_2"
yt-dlp -o "%(title)s.%(ext)s" "TED_URL_3"
```

### BBC Learning (3 videos)

**Search:** Go to YouTube and search:
- "BBC Learning English Nigerian"
- "BBC Africa pronunciation"

**Download Commands:**
```bash
cd /mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/external_videos/tier1_bbc

yt-dlp -o "%(title)s.%(ext)s" "BBC_URL_1"
yt-dlp -o "%(title)s.%(ext)s" "BBC_URL_2"
yt-dlp -o "%(title)s.%(ext)s" "BBC_URL_3"
```

### Khan Academy / Educational (2 videos)

**Search:** Go to YouTube and search:
- "Khan Academy African history"
- "Crash Course African empires"

**Download Commands:**
```bash
cd /mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/external_videos/tier1_educational

yt-dlp -o "%(title)s.%(ext)s" "KHAN_URL_1"
yt-dlp -o "%(title)s.%(ext)s" "KHAN_URL_2"
```

---

## 📝 STEP 4: CREATE METADATA FILES

For each downloaded video, create a `.json` metadata file in the same directory.

### Template (Copy and customize):

```json
{
    "video_id": "EXT_TED_001",
    "title": "Video Title Here",
    "creator": "Creator Name",
    "source_url": "https://original-source-url.com",
    "duration_seconds": 600,
    "primary_language": "en",
    "secondary_languages": ["yo"],
    "license_type": "CC-BY-NC-ND",
    "acquisition_date": "2025-12-14",
    "tier": 1,
    "category": "language_learning",
    "persona_pillars": ["cultural_ambassador", "tech_visionary"],
    "attribution": "Creator Name, Source Platform",
    "processing_status": "pending",
    "cost": 0.00,
    "notes": "Brief description of why this video is valuable"
}
```

### Quick Metadata Creation Script:

```bash
# Create metadata file for a video
cat > "video_name.json" << 'EOF'
{
    "video_id": "EXT_TED_001",
    "title": "The Danger of a Single Story",
    "creator": "Chimamanda Ngozi Adichie",
    "source_url": "https://www.ted.com/talks/chimamanda_ngozi_adichie_the_danger_of_a_single_story",
    "duration_seconds": 1120,
    "primary_language": "en",
    "secondary_languages": [],
    "license_type": "CC-BY-NC-ND",
    "acquisition_date": "2025-12-14",
    "tier": 1,
    "category": "cultural_identity",
    "persona_pillars": ["cultural_ambassador", "diaspora_guide"],
    "attribution": "Chimamanda Ngozi Adichie, TED Talks",
    "processing_status": "pending",
    "cost": 0.00,
    "notes": "Nigerian perspective on storytelling and identity"
}
EOF
```

---

## 🚀 STEP 5: SUBMIT TO RECCLOUD

Once you have videos downloaded and metadata created:

```bash
# Navigate to project
cd /mnt/c/Users/POK28/Dropbox/Sisi_Lola

# Submit Phase 1 videos
python ml_training/scripts/submit_external_videos.py --phase 1

# Check processing status
python ml_training/scripts/submit_external_videos.py --status
```

---

## 📧 PHASE 2: CREATOR OUTREACH TEMPLATES

### YouTube Creator DM (Instagram/Twitter)

```
Hi [Creator Name]! 👋

I love your content about [specific topic]! We're building Sisi Lola, an AI 
celebrating Nigerian language and culture. 

Would you allow us to use your video "[Title]" for educational AI training? 
Full credit + link to your channel included. 🙌

This helps preserve Nigerian culture through technology!
```

### Email Template (Longer form)

```
Subject: Educational AI Training License Request – Sisi Lola

Dear [Creator Name],

I'm reaching out regarding your excellent video: "[Video Title]"

We're developing Sisi Lola, an AI personality dedicated to celebrating and 
preserving Nigerian language, culture, and diaspora experiences. Your content 
would be invaluable for training our model.

WHAT WE'RE ASKING:
• Permission to include your video in our non-commercial AI training dataset
• Your authentic voice will help shape how Sisi Lola teaches others

WHAT YOU RECEIVE:
• Full attribution in all documentation
• Public recognition as a contributor
• Link to your channel/platform

FAIR USE ASSURANCE:
• Non-commercial educational use only
• No commercial profit from your content
• Your original work remains credited

Would you be open to this collaboration? Happy to discuss further.

Best regards,
[Your Name]
[Your Organization]
```

### Podcast Host Email

```
Subject: Educational AI License Request - [Podcast Name]

Hi [Host Name],

Big fan of your podcast! The episode on [topic] was particularly insightful.

We're preserving Nigerian culture through an AI project called Sisi Lola. 
Your authentic conversations would help train the AI to speak with genuine 
cultural understanding.

Could we license [specific episode] for educational training? 
Full attribution included.

Let me know if you'd like more details!

Best,
[Your Name]
```

---

## 📊 TRACKING SPREADSHEET

Create `external_videos_tracker.csv`:

```csv
video_id,title,creator,tier,phase,status,cost,expected_examples,date_acquired,date_processed,persona_pillars,notes
EXT_TED_001,The Danger of a Single Story,Chimamanda Adichie,1,1,downloaded,0.00,120,2025-12-14,,cultural_ambassador|diaspora_guide,Nigerian storytelling identity
EXT_TED_002,African Languages Matter,Dr. Example,1,1,pending,0.00,100,,,cultural_ambassador|code_switcher,Language preservation
EXT_BBC_001,Nigerian English Accents,BBC Learning,1,1,pending,0.00,80,,,cultural_ambassador,Accent training
EXT_YT_001,Pidgin English Explained,Naija Talk,2,2,pending_permission,0.00,150,,,code_switcher,Permission email sent
```

### Status Values:
- `pending` - Identified, not yet downloaded
- `downloaded` - Downloaded, awaiting processing
- `pending_permission` - Awaiting creator response
- `permission_granted` - Ready to download
- `permission_denied` - Do not use
- `processing` - Submitted to RecCloud
- `completed` - Ready for training
- `failed` - Needs investigation

---

## ⏱️ TODAY'S CHECKLIST (4-5 hours)

### Hour 1: Setup & First Downloads
- [ ] Install yt-dlp
- [ ] Verify directory structure
- [ ] Find 3 TED Talk URLs
- [ ] Download TED videos

### Hour 2: More Downloads
- [ ] Find 3 BBC Learning URLs
- [ ] Download BBC videos
- [ ] Find 2 Khan Academy URLs
- [ ] Download educational videos

### Hour 3: Metadata Creation
- [ ] Create JSON for each TED video
- [ ] Create JSON for each BBC video
- [ ] Create JSON for educational videos

### Hour 4: RecCloud Submission
- [ ] Run submit_external_videos.py
- [ ] Verify uploads started
- [ ] Check processing status

### Hour 5: Creator Outreach
- [ ] Identify 5 YouTube creators for Phase 2
- [ ] Send DMs/emails
- [ ] Log outreach in tracker

---

## 🎯 QUICK REFERENCE: LANGUAGE CODES

| Language | RecCloud Code | Description |
|:---|:---:|:---|
| English | `en` | Standard English |
| Yoruba | `yo` | Nigerian Yoruba |
| Nigerian Pidgin | `np` or `pcm` | Pidgin English |
| Hausa | `ha` | Nigerian Hausa |
| Igbo | `ig` | Nigerian Igbo |

---

## 🔧 TROUBLESHOOTING

### yt-dlp not working?
```bash
# Update to latest version
pip install --upgrade yt-dlp

# Try with different format
yt-dlp -f best -o "%(title)s.%(ext)s" "URL"
```

### Permission denied on directory?
```bash
# Fix permissions
chmod -R 755 /mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/external_videos/
```

### RecCloud upload failing?
```bash
# Check API key in .env
cat .env | grep RECCLOUD

# Verify video file exists
ls -la ml_training/external_videos/tier1_ted/
```

---

## 📈 EXPECTED RESULTS

After completing Phase 1 (8 videos):

| Metric | Value |
|:---|:---|
| Videos Downloaded | 8 |
| Total Duration | ~60 minutes |
| RecCloud Cost | $0.24 |
| Expected Examples | 530+ |
| Time Investment | 4-5 hours |

---

## 🚀 NEXT STEPS AFTER PHASE 1

1. **Wait for RecCloud processing** (usually 1-24 hours)
2. **Download transcripts** using process_external_transcripts.py
3. **Begin Phase 2 outreach** while waiting
4. **Track responses** in spreadsheet
5. **Proceed to Phase 2** when permissions received

---

**Ready? Start with Step 1 NOW!** 🎬
