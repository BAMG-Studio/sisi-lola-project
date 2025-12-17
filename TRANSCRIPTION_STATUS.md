# Transcription Progress Report

## Current Status (December 14, 2025)

### ✅ Successfully Completed

| Video | Task ID | Duration | Words | Status |
|-------|---------|----------|-------|--------|
| authentic_video_001 | 8ef57367-6d0a-4179-afac-eef2b1b2dc73 | 394 sec | 923 | Complete ✅ |

The transcript quality is excellent - it accurately captures Nigerian Pidgin English with proper code-switching patterns!

### ❌ Remaining Videos (Need Manual Shared Links)

The Dropbox API credentials need to be refreshed. In the meantime, you can manually submit videos using shared links.

**Affected Videos (10 remaining):**
- authentic_video_002 through authentic_video_008 (7 videos)
- heygen_20251126_143538
- heygen_20251126_181318
- The danger of a single story (TED Talk)

## Quick Start: Manual Submission (Recommended)

### Step 1: Get Dropbox Shared Links
1. Go to https://www.dropbox.com
2. Navigate to `Sisi_Lola/06_RENDER_OUTPUT/`
3. Right-click on `authentic_video_002.mp4` → "Copy link"
4. **IMPORTANT:** Change `?dl=0` to `?dl=1` at the end of the URL
5. Repeat for each video

### Step 2: Edit the Manual Submission Script
Open `submit_videos_manual.py` and add your links:
```python
VIDEOS = {
    'authentic_video_002': 'https://www.dropbox.com/scl/fi/xxx/...?dl=1',
    'authentic_video_003': 'https://www.dropbox.com/scl/fi/xxx/...?dl=1',
    # Add more...
}
```

### Step 3: Run Submission
```bash
python submit_videos_manual.py
```

### Step 4: Download Transcripts (after ~15 min)
```bash
python download_transcripts.py
```

## Alternative: Fix Dropbox Credentials

### Option 1: Regenerate Dropbox App Credentials
1. Go to https://www.dropbox.com/developers/apps
2. Find your app "Sisi_Lola" (or create new one)
3. Copy the **App key** and **App secret**
4. Update `.env` file:
   ```
   DROPBOX_APP_KEY=<new_app_key>
   DROPBOX_APP_SECRET=<new_app_secret>
   ```
5. Generate new refresh token using the OAuth flow

### Option 2: Generate New OAuth Token
1. Go to https://www.dropbox.com/developers/apps
2. Click on your app
3. Under "OAuth 2" section, click "Generate" to get a new access token
4. Update `.env` file:
   ```
   DROPBOX_ACCESS_TOKEN=<new_token>
   ```

### Option 3: Manual Shared Links
1. Go to Dropbox web interface
2. For each video, right-click → "Copy link"
3. Change `?dl=0` to `?dl=1` at the end of each URL
4. Use the manual submission script below

## Manual Submission Script

Once you have the shared links with `?dl=1`, run:

```python
import requests
import time

API_KEY = 'wxbgr07ikdtvgnws4'
API_URL = 'https://techhk.aoscdn.com/api/tasks/audio/recognition'

# Add your URLs here with dl=1
videos = {
    'authentic_video_002': 'https://www.dropbox.com/scl/fi/...?dl=1',
    # ... add more
}

for name, url in videos.items():
    print(f'Submitting {name}...')
    response = requests.post(API_URL, headers={'X-API-KEY': API_KEY}, data={'url': url})
    if response.status_code == 200:
        task_id = response.json().get('data', {}).get('task_id')
        print(f'  ✅ Task ID: {task_id}')
    else:
        print(f'  ❌ Error: {response.status_code}')
    time.sleep(15)  # Wait between requests
```

## Transcript Sample (Video 001)

The transcription quality is excellent! Here's a sample:

> "Hello everybody, e kaabo, welcome to my channel. I am Sisi Lola, and I dey very happy se you come here today. You know whatin? This channel ne special something o. We go dey talk about African culture, we go dey celebrate our heritage, and we go dey show the world Say, Africa sweet die."

The RecCloud transcription:
- ✅ Accurately captures Nigerian Pidgin English
- ✅ Maintains code-switching patterns
- ✅ Preserves authentic speech patterns
- ✅ 6+ minutes of training data from one video

## Next Steps

1. **Fix Dropbox credentials** (see options above)
2. **Submit remaining 10 videos** 
3. **Wait for transcriptions** (typically 5-15 minutes each)
4. **Download all transcripts**
5. **Process for training data**

## Files Created

- `ml_training/datasets/transcriptions/authentic_video_001_transcript.json` - Full API response
- `ml_training/datasets/transcriptions/authentic_video_001_transcript.txt` - Plain text transcript
- `download_transcripts.py` - Script to download completed transcripts
- `submit_remaining_videos.py` - Script to submit videos (needs working Dropbox)

## RecCloud API Reference

- **API Key:** `wxbgr07ikdtvgnws4`
- **Create Task:** `POST https://techhk.aoscdn.com/api/tasks/audio/recognition`
- **Check Status:** `GET https://techhk.aoscdn.com/api/tasks/audio/recognition/{task_id}`
- **Task States:** 0=Queued, 4=Processing, 1=Complete, <0=Failed
