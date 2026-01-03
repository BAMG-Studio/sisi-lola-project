# =============================================================================
# SISI LOLA - SOCIAL MEDIA CONFIGURATION TRACKER
# =============================================================================
# Track all social media API configurations and their status
# Last Updated: 2025-12-29
# =============================================================================

## 📱 PLATFORM CONFIGURATION STATUS

### 1. TikTok 🎵
```yaml
Status: PENDING VERIFICATION
Required Tokens:
  - TIKTOK_CLIENT_KEY: ""      # From TikTok Developer Portal
  - TIKTOK_CLIENT_SECRET: ""   # From TikTok Developer Portal
  - TIKTOK_ACCESS_TOKEN: ""    # From OAuth flow
  - TIKTOK_OPEN_ID: ""         # User's TikTok ID

Setup Steps:
  1. Go to https://developers.tiktok.com/
  2. Create App → Select "Content Posting API"
  3. Configure OAuth redirect: http://localhost:8000/api/v2/social/tiktok/callback
  4. Scopes needed: video.upload, video.list, user.info.basic
  5. Run OAuth flow to get tokens
  6. Add tokens to .env file

API Documentation:
  - https://developers.tiktok.com/doc/content-posting-api-reference-direct-post

Notes:
  - Videos must be 1-10 minutes
  - 9:16 aspect ratio required
  - Max file size: 4GB
```

### 2. Instagram 📸
```yaml
Status: PENDING VERIFICATION  
Required Tokens:
  - INSTAGRAM_ACCESS_TOKEN: ""   # Page Access Token (long-lived)
  - INSTAGRAM_BUSINESS_ID: ""    # IG Business Account ID
  - FACEBOOK_PAGE_ID: ""         # Connected Facebook Page ID

Setup Steps:
  1. Go to https://developers.facebook.com/
  2. Create App → Business type
  3. Add "Instagram Graph API" product
  4. Connect Instagram Business Account to a Facebook Page
  5. Generate Page Access Token (convert to long-lived)
  6. Get Instagram Business Account ID from /me/accounts?fields=instagram_business_account

Exchange for Long-Lived Token:
  curl "https://graph.facebook.com/v18.0/oauth/access_token?
        grant_type=fb_exchange_token&
        client_id={app-id}&
        client_secret={app-secret}&
        fb_exchange_token={short-lived-token}"

API Documentation:
  - https://developers.facebook.com/docs/instagram-api/guides/content-publishing

Notes:
  - Reels must be 3-90 seconds
  - MP4 format required
  - Need video_url (must be publicly accessible)
  - Use Dropbox shared links for video hosting
```

### 3. YouTube 📺
```yaml
Status: PENDING VERIFICATION
Required Tokens:
  - YOUTUBE_CLIENT_ID: ""        # From Google Cloud Console
  - YOUTUBE_CLIENT_SECRET: ""    # From Google Cloud Console
  - YOUTUBE_REFRESH_TOKEN: ""    # From OAuth flow

Setup Steps:
  1. Go to https://console.cloud.google.com/
  2. Create project "Sisi Lola Content"
  3. Enable "YouTube Data API v3"
  4. Create OAuth 2.0 credentials (Web Application)
  5. Authorized redirect: http://localhost:8000/api/v2/social/youtube/callback
  6. Run OAuth to get refresh_token (with offline access)

OAuth Flow Script:
  # See sisi_lola_api/scripts/youtube_oauth.py

API Documentation:
  - https://developers.google.com/youtube/v3/docs/videos/insert

Notes:
  - Shorts: vertical video < 60 seconds
  - #Shorts in title or description
  - Unlimited uploads with API key
```

### 4. Facebook 📘
```yaml
Status: PENDING VERIFICATION
Required Tokens:
  - FACEBOOK_ACCESS_TOKEN: ""    # Page Access Token
  - FACEBOOK_PAGE_ID: ""         # Target Page ID

Setup Steps:
  1. Same as Instagram (shares the same Facebook App)
  2. Generate Page Access Token with pages_manage_posts permission
  3. Get Page ID from /me/accounts

API Documentation:
  - https://developers.facebook.com/docs/pages/publishing

Notes:
  - Videos posted to Page Feed
  - Can share Reels directly
```

### 5. Twitter/X 🐦
```yaml
Status: NOT CONFIGURED
Required Tokens:
  - TWITTER_API_KEY: ""
  - TWITTER_API_SECRET: ""
  - TWITTER_ACCESS_TOKEN: ""
  - TWITTER_ACCESS_SECRET: ""
  - TWITTER_BEARER_TOKEN: ""

Setup Steps:
  1. Go to https://developer.twitter.com/
  2. Create Project "Sisi Lola"
  3. Create App under the project
  4. Apply for Elevated access (for media upload)
  5. Generate OAuth 1.0a tokens
  6. Enable read/write permissions

API Documentation:
  - https://developer.twitter.com/en/docs/twitter-api/tweets/manage-tweets/api-reference

Notes:
  - Video upload via chunked media endpoint
  - Max 140 seconds for video
```

### 6. LinkedIn 💼
```yaml
Status: NOT CONFIGURED
Required Tokens:
  - LINKEDIN_ACCESS_TOKEN: ""
  - LINKEDIN_ORG_ID: ""         # Organization page ID (optional)

Setup Steps:
  1. Go to https://www.linkedin.com/developers/
  2. Create App "Sisi Lola Official"
  3. Request: w_member_social, r_liteprofile
  4. For company page: rw_organization_admin
  5. OAuth 2.0 flow for access token

API Documentation:
  - https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/share-api

Notes:
  - Max video: 10 minutes
  - Article posts supported
```

---

## 🔗 DROPBOX INTEGRATION (For Video Hosting)

```yaml
Status: CONFIGURED (Check .env)
Required Tokens:
  - DROPBOX_APP_KEY: ""
  - DROPBOX_APP_SECRET: ""
  - DROPBOX_ACCESS_TOKEN: ""
  - DROPBOX_REFRESH_TOKEN: ""

Purpose:
  - Upload produced videos to Dropbox
  - Generate shareable public links
  - Use links for Instagram/TikTok API uploads

API Documentation:
  - https://www.dropbox.com/developers/documentation/http/documentation
```

---

## 🛠️ OAUTH HELPER SCRIPTS

### Generate TikTok Token
```python
# sisi_lola_api/scripts/tiktok_oauth.py
# Run: python -m sisi_lola_api.scripts.tiktok_oauth
```

### Generate YouTube Token
```python
# sisi_lola_api/scripts/youtube_oauth.py
# Run: python -m sisi_lola_api.scripts.youtube_oauth
```

### Generate Instagram Token
```python
# sisi_lola_api/scripts/instagram_oauth.py
# Run: python -m sisi_lola_api.scripts.instagram_oauth
```

---

## ✅ VERIFICATION CHECKLIST

Run this after adding tokens to .env:

```bash
curl http://localhost:8000/api/v2/social/tokens/status
```

Expected Response:
```json
{
  "social_tokens": {
    "tiktok": {"configured": true, "token_preview": "...xxxx"},
    "instagram": {"configured": true, "token_preview": "...xxxx"},
    "youtube": {"configured": true, "token_preview": "...xxxx"},
    "facebook": {"configured": true, "token_preview": "...xxxx"},
    "twitter": {"configured": false},
    "linkedin": {"configured": false}
  }
}
```

---

## 🚨 MANUAL POSTING FALLBACK

If API tokens not ready, post manually:

1. **Generate content** via API
2. **Download** from `03_MEDIA_ASSETS/produced_vibes/`
3. **Upload manually** to each platform
4. **Track** in spreadsheet for consistency

---

**Boss, once you add the tokens to .env, make I know and we go test am properly!** 💪🏾
