# External Videos Directory
# ═══════════════════════════════════════════════════════════════════════════════
# This directory contains external video sources for Sisi Lola training
# December 14, 2025

## 📁 Directory Structure

```
external_videos/
├── tier1_ted/              # TED Talks (CC-licensed, free)
├── tier1_bbc/              # BBC Learning (public use)
├── tier1_educational/      # Khan Academy, Crash Course
├── tier2_youtube/          # Permission-based YouTube creators
├── tier2_podcasts/         # Permission-based podcast episodes
├── tier3_licensed/         # Paid/licensed content (Nollywood, comedy)
├── external_videos_tracker.csv   # Master tracking spreadsheet
├── TEMPLATE_video_metadata.json  # Metadata template
└── README.md               # This file
```

## 🎯 Usage

### 1. Download a Video

```bash
# Using yt-dlp (install with: pip install yt-dlp)
cd tier1_ted
yt-dlp -o "%(title)s.%(ext)s" "VIDEO_URL"
```

### 2. Create Metadata File

Copy `TEMPLATE_video_metadata.json` to the same directory as your video:

```bash
cp TEMPLATE_video_metadata.json tier1_ted/my_video.json
# Edit the JSON file with actual video details
```

### 3. Submit for Processing

```bash
cd /mnt/c/Users/POK28/Dropbox/Sisi_Lola
python ml_training/scripts/submit_external_videos.py --phase 1
```

### 4. Check Status

```bash
python ml_training/scripts/submit_external_videos.py --status
```

## 📊 Tier Descriptions

| Tier | Description | License | Cost |
|------|-------------|---------|------|
| Tier 1 | Public domain/CC-licensed content | Free use | $0 |
| Tier 2 | Permission-based content | Requires creator approval | $0 |
| Tier 3 | Licensed content | Requires payment | $500-10,000 |

## ⚠️ Important Notes

1. **Always verify rights** before processing any video
2. **Create metadata files** for every video downloaded
3. **Update the tracker** after each action
4. **Keep permission emails** for Tier 2 content

## 📝 Metadata Template Fields

| Field | Required | Description |
|-------|----------|-------------|
| video_id | ✅ | Unique ID (e.g., EXT_TED_001) |
| title | ✅ | Video title |
| creator | ✅ | Creator/speaker name |
| source_url | ✅ | Original source URL |
| duration_seconds | ✅ | Video length in seconds |
| primary_language | ✅ | Main language code (en, yo, np, ha, ig) |
| secondary_languages | | Additional languages |
| license_type | ✅ | License type (CC-BY, Fair Use, etc.) |
| tier | ✅ | 1, 2, or 3 |
| persona_pillars | ✅ | Array of persona tags |
| processing_status | ✅ | pending, processing, completed, failed |

## 🔗 Related Documentation

- `EXTERNAL_VIDEO_SOURCES_STRATEGY.md` - Full acquisition strategy
- `EXTERNAL_VIDEO_ACQUISITION_IMPLEMENTATION.md` - Implementation details
- `EXTERNAL_VIDEOS_QUICK_START_GUIDE.md` - Quick start instructions
- `VIDEO_TARGET_LIST_PERSONA_PILLARS.md` - Persona-targeted content
- `COMPLETE_TRAINING_ECOSYSTEM_VISUAL.md` - Architecture overview
