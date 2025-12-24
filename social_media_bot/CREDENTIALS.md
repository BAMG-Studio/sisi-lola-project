# 🔐 SISI LOLA - COMPREHENSIVE API CREDENTIALS GUIDE
**Generated:** December 24, 2025  
**Status:** Configuration Complete - Secrets Require Manual Retrieval

---

## 📊 CREDENTIAL COLLECTION STATUS

| Platform | App Created | Client ID/Key | Secret/Token Status | OAuth Ready |
|----------|-------------|---------------|---------------------|-------------|
| Meta/Facebook/Instagram | ✅ Yes | ✅ Retrieved | ⚠️ Requires Password | ⚠️ Partial |
| Google/YouTube | ✅ Yes | ✅ Available | ⚠️ OAuth Flow Needed | ⚠️ Setup Required |
| Twitter/X | ⚠️ Needs Setup | ❌ Not Created | ❌ Not Created | ❌ Account Unverified |
| TikTok | ✅ Yes | ✅ Retrieved | ⚠️ OAuth Flow Needed | ⚠️ Setup Required |
| Twitch | ✅ Yes | ✅ Retrieved | ⚠️ Must Generate | ⚠️ Setup Required |
| Reddit | ⚠️ CAPTCHA Issue | ❌ Not Created | ❌ Not Created | ❌ Setup Incomplete |
| Dropbox | ✅ Yes | ✅ Retrieved | ⚠️ Team Admin Required | ⚠️ Permissions Issue |

---

## 🎭 META / FACEBOOK / INSTAGRAM

### App Information
- **App Name:** Sisi Lola Content API
- **App ID:** `883228234668574`
- **Developer Portal:** https://developers.facebook.com/apps/883228234668574/

### Credentials Status
✅ **App ID:** `883228234668574`  
⚠️ **App Secret:** Requires password re-entry  
📍 **Location:** https://developers.facebook.com/apps/883228234668574/settings/basic/  
🔒 **Action Required:** Click "Show" next to App Secret and enter Facebook password

### Configuration Details
- **Facebook Page ID:** `61584537404085`
- **Instagram Username:** `sisilolalive`
- **Instagram Product:** Added to app
- **Contact Email:** sisilolalive@gmail.com
- **App Domains:** sisilola.io

### OAuth & Access Tokens
⚠️ **Page Access Token:** Must generate via Graph API Explorer or Business Manager  
📍 **Token Tools:** https://developers.facebook.com/tools/accesstoken/

### Environment Variables Needed
```bash
META_APP_ID=883228234668574
META_APP_SECRET=[RETRIEVE_FROM_PORTAL]
FACEBOOK_PAGE_ID=61584537404085
FACEBOOK_PAGE_ACCESS_TOKEN=[GENERATE_VIA_GRAPH_API]
INSTAGRAM_USERNAME=sisilolalive
INSTAGRAM_PASSWORD=[YOUR_PASSWORD]
```

---

## 📺 GOOGLE / YOUTUBE

### Project Information
- **Project Name:** Default Gemini Project
- **Project ID:** `gen-lang-client-0912090080`
- **Developer Console:** https://console.cloud.google.com/apis/credentials?project=gen-lang-client-0912090080

### Credentials Status
✅ **Project ID:** `gen-lang-client-0912090080`  
⚠️ **API Key:** Available in console (click "Show Key")  
⚠️ **OAuth Client ID:** Must create OAuth 2.0 credentials  
⚠️ **OAuth Client Secret:** Generated with OAuth client  
⚠️ **Refresh Token:** Generated via OAuth flow

### Setup Steps Required
1. Navigate to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "OAuth Client ID"
3. Choose "Desktop app" or "Web application"
4. Configure redirect URIs (http://localhost:8080)
5. Download client_secret.json
6. Run OAuth authorization flow to get refresh_token

### APIs to Enable
- YouTube Data API v3
- YouTube Analytics API (optional)

### Environment Variables Needed
```bash
YOUTUBE_API_KEY=[GET_FROM_CREDENTIALS_PAGE]
GOOGLE_CLIENT_ID=[FROM_OAUTH_CLIENT]
GOOGLE_CLIENT_SECRET=[FROM_OAUTH_CLIENT]
YOUTUBE_REFRESH_TOKEN=[FROM_OAUTH_FLOW]
```

---

## 🐦 TWITTER / X

### Account Status
❌ **Developer Account:** Not verified  
⚠️ **Issue:** Account requires phone number and email verification

### Setup Required
1. Go to: https://developer.x.com/en/portal/dashboard
2. Verify account (add phone number + email)
3. Create a Project
4. Create an App within the project
5. Generate API keys and tokens

### Credentials Needed
```bash
TWITTER_API_KEY=[CREATE_APP_FIRST]
TWITTER_API_SECRET=[CREATE_APP_FIRST]
TWITTER_ACCESS_TOKEN=[GENERATE_IN_APP]
TWITTER_ACCESS_TOKEN_SECRET=[GENERATE_IN_APP]
TWITTER_BEARER_TOKEN=[GENERATE_IN_APP]
```

### Recommended App Settings
- **App Name:** Sisi Lola Bot
- **App Type:** Automated App or Bot
- **Permissions:** Read and Write
- **OAuth:** Enable OAuth 1.0a and/or 2.0

---

## 🎵 TIKTOK

### App Information
- **App Name:** (From Developer Portal)
- **App ID:** `7587288329160116280`
- **Developer Portal:** https://developers.tiktok.com/app/7587288329160116280/

### Credentials Status
✅ **App ID:** `7587288329160116280`  
⚠️ **Client Key:** Available in app details  
⚠️ **Client Secret:** Available in app details  
⚠️ **Access Token:** Requires OAuth 2.0 authorization flow

### OAuth Setup Required
1. Go to app settings
2. Configure redirect URI
3. Implement OAuth 2.0 flow
4. User authorization → Exchange code for access token

### Environment Variables Needed
```bash
TIKTOK_CLIENT_KEY=[FROM_APP_DETAILS]
TIKTOK_CLIENT_SECRET=[FROM_APP_DETAILS]
TIKTOK_ACCESS_TOKEN=[FROM_OAUTH_FLOW]
```

---

## 🎮 TWITCH

### App Information
- **App Name:** sisi_lola
- **Client ID:** `98xxi2srfczfdkyc72iyrpqlciksqo`
- **Developer Portal:** https://dev.twitch.tv/console/apps/98xxi2srfczfdkyc72iyrpqlciksqo

### Credentials Status
✅ **Client ID:** `98xxi2srfczfdkyc72iyrpqlciksqo`  
⚠️ **Client Secret:** Must generate new secret  
📍 **Location:** App settings page  
🔒 **Action:** Click "New Secret" button

### Configuration
- **Redirect URI:** https://management.bamg-studio.com/auth/github/callback
- **Category:** Game Integration
- **Client Type:** Public

### Environment Variables Needed
```bash
TWITCH_CLIENT_ID=98xxi2srfczfdkyc72iyrpqlciksqo
TWITCH_CLIENT_SECRET=[GENERATE_NEW_SECRET]
```

---

## 🔴 REDDIT

### App Status
❌ **App Creation:** Incomplete (CAPTCHA validation issue)  
⚠️ **Form Filled:** Name, Description, Redirect URI entered

### Setup Required
1. Go to: https://www.reddit.com/prefs/apps
2. Complete CAPTCHA verification
3. Submit app creation form
4. Retrieve Client ID and Client Secret

### Form Details (Pre-filled)
- **Name:** Sisi Lola Bot
- **Type:** Script (for personal use)
- **Description:** Sisi Lola social media automation bot for Reddit content management
- **Redirect URI:** http://localhost:8080

### Environment Variables Needed
```bash
REDDIT_CLIENT_ID=[AFTER_APP_CREATION]
REDDIT_CLIENT_SECRET=[AFTER_APP_CREATION]
REDDIT_USERNAME=sisilolalive
REDDIT_PASSWORD=[YOUR_REDDIT_PASSWORD]
```

---

## 📦 DROPBOX

### App Information
- **App Name:** Sisi Lola Content Automation#
- **App Key:** `x4boh5rtnprg4o1`
- **Developer Portal:** https://www.dropbox.com/developers/apps/info/x4boh5rtnprg4o1

### Credentials Status
✅ **App Key:** `x4boh5rtnprg4o1`  
✅ **App Secret:** `p3v1zvwt6S` (visible in settings)  
❌ **Access Token:** Generation failed - "Team administrator" permission required

### Issue & Resolution
⚠️ **Error:** "You must be a team administrator to perform this operation"  
🔧 **Solution:** Request team admin to generate access token OR convert to personal app

### Configuration
- **Permission Type:** Scoped App
- **Redirect URI:** http://localhost:8000
- **Public Clients:** Allowed

### Environment Variables Needed
```bash
DROPBOX_APP_KEY=x4boh5rtnprg4o1
DROPBOX_APP_SECRET=p3v1zvwt6S
DROPBOX_ACCESS_TOKEN=[REQUIRES_TEAM_ADMIN]
```

---

## 🚀 QUICK START GUIDE

### Step 1: Complete Manual Tasks
1. ✅ **Meta:** Enter password to reveal App Secret
2. ❌ **Twitter:** Verify developer account, create app
3. ❌ **Reddit:** Complete CAPTCHA and create app
4. ⚠️ **Twitch:** Generate new client secret
5. ⚠️ **Dropbox:** Get team admin to generate token
6. ⚠️ **YouTube:** Set up OAuth 2.0 client
7. ⚠️ **TikTok:** Complete OAuth authorization flow

### Step 2: Update .env File
```bash
cd social_media_bot
cp .env.template .env
# Edit .env with all retrieved credentials
```

### Step 3: Test Connections
```bash
pip install -r requirements.txt
python main.py
```

---

## 📋 CREDENTIAL RETRIEVAL CHECKLIST

### Immediate Actions (No Additional Setup)
- [ ] Meta App Secret (password required)
- [ ] Dropbox App Secret (already visible: p3v1zvwt6S)
- [ ] Twitch Client Secret (click "New Secret")

### Requires OAuth/Token Generation
- [ ] Facebook Page Access Token
- [ ] YouTube Refresh Token
- [ ] TikTok Access Token
- [ ] Dropbox Access Token (team admin)

### Requires App Creation
- [ ] Twitter Developer Account Verification
- [ ] Twitter App Creation
- [ ] Reddit App Creation (CAPTCHA pending)

### Optional/Advanced
- [ ] Instagram Graph API Access Token
- [ ] YouTube Analytics API
- [ ] Twitch EventSub subscriptions
- [ ] Reddit OAuth 2.0 (vs script)

---

## 🔗 QUICK LINKS

### Developer Portals
- **Meta:** https://developers.facebook.com/apps/883228234668574/
- **Google:** https://console.cloud.google.com/apis/credentials?project=gen-lang-client-0912090080
- **Twitter:** https://developer.x.com/en/portal/dashboard
- **TikTok:** https://developers.tiktok.com/app/7587288329160116280/
- **Twitch:** https://dev.twitch.tv/console/apps/98xxi2srfczfdkyc72iyrpqlciksqo
- **Reddit:** https://www.reddit.com/prefs/apps
- **Dropbox:** https://www.dropbox.com/developers/apps/info/x4boh5rtnprg4o1

### Documentation
- **Meta Graph API:** https://developers.facebook.com/docs/graph-api/
- **YouTube API:** https://developers.google.com/youtube/v3
- **Twitter API:** https://developer.x.com/en/docs/twitter-api
- **TikTok API:** https://developers.tiktok.com/doc/
- **Twitch API:** https://dev.twitch.tv/docs/api/
- **Reddit API:** https://www.reddit.com/dev/api/
- **Dropbox API:** https://www.dropbox.com/developers/documentation

---

## ⚠️ SECURITY NOTES

1. **Never commit .env file** - It's in .gitignore
2. **Rotate secrets regularly** - Especially if exposed
3. **Use environment variables** - Never hardcode credentials
4. **Limit API permissions** - Only request what you need
5. **Monitor API usage** - Watch for unusual activity
6. **Store securely** - Consider using secrets manager for production

---

**Last Updated:** December 24, 2025, 3:00 PM EST  
**Project:** Sisi Lola Social Media Automation System  
**Repository:** https://github.com/BAMG-Studio/sisi-lola-project
