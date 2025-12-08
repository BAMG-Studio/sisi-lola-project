# Sisi Lola Automated Multi-Platform Posting System

## 🎯 Overview

Complete automation pipeline for Sisi Lola's social media presence:
1. **Content Generation**: AI-powered multi-platform content creation
2. **Media Production**: Video/image asset generation (HeyGen, Runway, etc.)
3. **Multi-Platform Posting**: Automated posting to YouTube, Instagram, TikTok, Twitter/X, Facebook, Reddit

## 🚀 Quick Start (3 Steps)

### Step 1: Complete YouTube OAuth (5 minutes)

```bash
cd "c:\Users\POK28\Dropbox\Sisi_Lola\00_PROJECT_CORE\Scripts"
python youtube_oauth_complete.py
```

**What happens:**
- Browser opens for Google authorization
- Select **sisilolalive@gmail.com** account
- Click "Continue" on unverified app warning
- Grant YouTube permissions
- Token saved to `token_youtube.json`

**Troubleshooting:**
- Ensure sisilolalive@gmail.com is added as test user in Google Cloud Console
- Verify `http://localhost:8080/` is in redirect URIs
- Check port 8080 is not in use

### Step 2: Generate Your First Content (2 minutes)

```bash
python sisi_lola_content_generator.py
```

**What happens:**
- Generates 3 sample content packages
- Creates platform-specific captions, hooks, CTAs
- Saves to `03_MEDIA_ASSETS/content_queue/`
- Each package includes: YouTube, TikTok, Instagram, Twitter/X, LinkedIn, Facebook, Reddit

**Output:**
```
content_20250103_120000.json  # Full content package
```

### Step 3: Run Full Automation (Interactive)

```bash
python sisi_lola_automation_master.py
```

**Menu Options:**
1. **Add single content** - Quick one-off post
2. **Schedule 7 days** - Auto-schedule week of content
3. **Process queue** - Generate & post queued content
4. **View status** - Check queue/posted/failed counts

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  SISI LOLA AUTOMATION MASTER                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     1. CONTENT GENERATION (AI)          │
        │  sisi_lola_content_generator.py         │
        │  • OpenAI GPT-4 with Afro-futuristic    │
        │    Sisi Lola personality prompt         │
        │  • Generates 6-7 platform packages      │
        │  • Unique hooks, CTAs, hashtags         │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     2. MEDIA PRODUCTION (Optional)      │
        │  • HeyGen: Talking head videos          │
        │  • Runway/Kling: B-roll footage         │
        │  • DALL-E/Midjourney: Images            │
        │  • ElevenLabs: Voiceovers               │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │     3. MULTI-PLATFORM POSTING           │
        │  multi_platform_poster.py               │
        │  • YouTube: Videos + Community posts    │
        │  • Twitter/X: Tweets + threads          │
        │  • Reddit: Text posts                   │
        │  • Instagram: (pending approval)        │
        │  • TikTok: (pending approval)           │
        │  • Facebook: (pending approval)         │
        └─────────────────────────────────────────┘
```

## 🔧 Configuration Status

### ✅ Fully Configured
- **YouTube**: OAuth tokens ready (`token_youtube.json`)
- **OpenAI**: Content generation ready

### ⏳ Pending Configuration
- **Twitter/X**: Need API keys in `.env`
- **Reddit**: Need credentials in `.env`
- **Instagram**: Requires Facebook Business approval
- **TikTok**: Requires developer account approval
- **Facebook**: Requires page access token

## 📝 Environment Variables

Add to `00_PROJECT_CORE/.env`:

```bash
# OpenAI (for content generation)
OPENAI_API_KEY=your_key_here

# Twitter/X API v2
TWITTER_BEARER_TOKEN=your_token
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_SECRET=your_secret

# Reddit API
REDDIT_CLIENT_ID=your_id
REDDIT_CLIENT_SECRET=your_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password

# Instagram Graph API (pending approval)
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_id

# TikTok API (pending approval)
TIKTOK_ACCESS_TOKEN=your_token
TIKTOK_OPEN_ID=your_id

# Facebook Graph API (pending approval)
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_PAGE_ID=your_id
```

## 🎨 Content Generation Examples

### Example 1: Tutorial Content
```python
from sisi_lola_content_generator import SisiLolaContentGenerator

generator = SisiLolaContentGenerator()

content = generator.generate_content(
    core_topic="How to batch 30 days of content in one weekend with AI tools",
    content_type_focus="tutorial",
    campaign_tag="#SisiLolaAIStudio",
    preferred_media="short_video"
)
```

**Output:** 6-7 platform-specific packages with:
- Unique hooks per platform
- Platform-optimized captions
- Voiceover scripts (30-60s for shorts, outlines for long-form)
- Media production briefs
- Hashtag strategies
- Posting time recommendations

### Example 2: Story Content
```python
content = generator.generate_content(
    core_topic="Building a virtual host: My journey from idea to 10K followers",
    content_type_focus="story",
    campaign_tag="#SisiLolaJourney",
    preferred_media="short_video"
)
```

### Example 3: Educational Content
```python
content = generator.generate_content(
    core_topic="Why your AI automation is failing (and 3 fixes that actually work)",
    content_type_focus="educational",
    campaign_tag="#SisiLolaAIStudio",
    preferred_media="carousel"
)
```

## 🤖 Automation Workflows

### Workflow 1: Daily Posting (Recommended)

```python
from sisi_lola_automation_master import SisiLolaAutomationMaster

master = SisiLolaAutomationMaster()

# Schedule 7 days of content
master.schedule_daily_content(days=7)

# Process today's content
master.process_queue(limit=1)
```

**Schedule:** Run daily at 9 AM via cron/Task Scheduler

### Workflow 2: Batch Weekly Content

```python
# Monday: Generate full week
master.schedule_daily_content(days=7)

# Each day: Auto-post scheduled content
master.process_queue(limit=1)
```

### Workflow 3: On-Demand Posting

```python
# Add urgent/trending topic
master.add_to_queue(
    core_topic="Breaking: New AI regulation announced",
    content_type_focus="opinion",
    preferred_media="short_video",
    scheduled_time=datetime.now().isoformat()  # Post immediately
)

master.process_queue(limit=1)
```

## 📊 Content Queue Management

### View Queue Status
```python
master.print_status()
```

Output:
```
📊 AUTOMATION STATUS
   Queued: 7
   Posted: 15
   Failed: 0
```

### Inspect Queue
```python
# Load schedule
with open('03_MEDIA_ASSETS/content_queue/content_schedule.json', 'r') as f:
    schedule = json.load(f)

# View queued items
for item in schedule['queue']:
    print(f"{item['scheduled_time']}: {item['core_topic']}")
```

### Retry Failed Posts
```python
# Move failed items back to queue
for item in schedule['failed']:
    item['status'] = 'queued'
    schedule['queue'].append(item)

schedule['failed'] = []
master.save_schedule()
```

## 🎬 Media Asset Integration

### Current: Use Existing Videos
The system automatically uses videos from `03_MEDIA_ASSETS/generated/` as placeholders.

### Future: Full Media Pipeline

```python
def create_media_assets(content, item):
    """Integrate with media generation APIs"""
    
    # 1. Generate talking head video (HeyGen)
    heygen_video = heygen_api.create_video(
        avatar_id="sisi_lola_avatar",
        script=content['voiceover_script'],
        voice_id="sisi_lola_voice"
    )
    
    # 2. Generate b-roll (Runway/Kling)
    broll = runway_api.generate_video(
        prompt=content['media_brief'],
        duration=30
    )
    
    # 3. Composite final video
    final_video = video_editor.composite(
        talking_head=heygen_video,
        broll=broll,
        music=background_music
    )
    
    return {
        'youtube': final_video,
        'tiktok': final_video,
        'instagram': final_video
    }
```

## 🔐 Security Best Practices

1. **Never commit `.env` files**
   ```bash
   # Add to .gitignore
   .env
   token_*.json
   *_credentials.json
   ```

2. **Rotate tokens regularly**
   - YouTube: Tokens auto-refresh
   - Twitter: Regenerate every 90 days
   - Reddit: Change password periodically

3. **Use environment-specific configs**
   ```
   .env.development
   .env.staging
   .env.production
   ```

## 📈 Analytics & Monitoring

### Track Post Performance
```python
# Save post results
results = master.post_content(item)

# Results include:
# - platform
# - status (success/error)
# - post_id
# - url
# - timestamp
```

### Generate Reports
```python
# Weekly performance report
posted = schedule['posted']
last_week = [p for p in posted if is_last_week(p['posted_at'])]

print(f"Posts last week: {len(last_week)}")
print(f"Platforms: {set(r['platform'] for p in last_week for r in p['post_results'])}")
```

## 🐛 Troubleshooting

### Issue: "YouTube token not found"
**Solution:** Run `python youtube_oauth_complete.py`

### Issue: "OpenAI API key not found"
**Solution:** Add `OPENAI_API_KEY` to `.env` file

### Issue: "Port 8080 already in use"
**Solution:** 
```bash
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8080 | xargs kill -9
```

### Issue: Content generation fails
**Solution:** Check OpenAI API quota and billing

### Issue: YouTube upload fails
**Solution:** 
- Check video file exists
- Verify file size < 256GB
- Ensure video format is supported (MP4, MOV, AVI)

## 🚀 Next Steps

1. **Complete Platform Setup**
   - Configure Twitter/X API
   - Set up Reddit credentials
   - Apply for Instagram/TikTok/Facebook approvals

2. **Integrate Media Generation**
   - Connect HeyGen API for talking head videos
   - Set up Runway/Kling for b-roll
   - Configure ElevenLabs for voiceovers

3. **Schedule Automation**
   - Set up daily cron job / Task Scheduler
   - Configure monitoring alerts
   - Set up analytics dashboard

4. **Scale Content Production**
   - Build content calendar (30-90 days)
   - Create topic templates library
   - Implement A/B testing for hooks/CTAs

## 📚 Additional Resources

- **OAuth Setup Guide**: `oauth_credential_manager.py`
- **Content Examples**: `03_MEDIA_ASSETS/content_queue/`
- **Post Results**: `03_MEDIA_ASSETS/content_queue/post_results_*.json`
- **Project README**: `README.md`

## 💡 Pro Tips

1. **Batch content generation** on Sundays for the week ahead
2. **Post at optimal times**: 10 AM, 2 PM, 7 PM (audience timezone)
3. **Rotate content types**: 40% educational, 30% story, 20% tutorial, 10% motivational
4. **Cross-promote**: Mention other platforms in captions
5. **Engage quickly**: Respond to comments within 1 hour

---

**Status**: ✅ YouTube Ready | ⏳ Other Platforms Pending
**Last Updated**: 2025-01-03
**Maintainer**: Sisi Lola Team
