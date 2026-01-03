# 🔒 SECURITY REMEDIATION & PUSH GUIDE

## ⚠️ CRITICAL: Keys Have Been Exposed

The following credentials were exposed in git history and must be **rotated immediately**:

### Exposed Keys (ALL MUST BE REGENERATED):
- ❌ YouTube API Key & OAuth credentials
- ❌ Instagram Access Token
- ❌ OpenAI API Key (sk-proj-...)
- ❌ Perplexity API Key (pplx-...)
- ❌ HeyGen API Key (sk_V2_...)
- ❌ KlingAI Access/Secret Keys
- ❌ ElevenLabs API Key (sk_...)
- ❌ Google AI Studio API Keys (AIzaSy...)
- ❌ HuggingFace Token (hf_...)
- ❌ Cohere API Key
- ❌ D-ID API Key
- ❌ OpenRouter API Key (sk-or-v1-...)
- ❌ Discord Bot Token & Secrets
- ❌ Facebook/Meta App Secrets
- ❌ Twitch Client Secret
- ❌ TikTok Client Secret
- ❌ Dropbox Access Token

---

## 📋 REMEDIATION STEPS

### Step 1: Regenerate ALL Exposed Keys
Go to each service's dashboard and regenerate:
1. https://console.cloud.google.com → YouTube/Google APIs
2. https://platform.openai.com → API Keys
3. https://elevenlabs.io → API Keys
4. https://replicate.com → API Tokens
5. https://huggingface.co/settings/tokens → Access Tokens
6. https://dashboard.cohere.com → API Keys
7. All other services listed above

### Step 2: Update Your Local .env
Copy `.env.example` to `sisi_lola_api/.env` and add your NEW keys.

---

## 🚀 POWERSHELL COMMANDS TO PUSH

Open PowerShell and run these commands in order:

```powershell
# Navigate to project
cd "C:\Users\POK28\Dropbox\Sisi_Lola"

# 1. Check git status
git status

# 2. Stage all changes (new .gitignore will exclude sensitive files)
git add .gitignore
git add .env.example
git add dvc.yaml
git add params.yaml
git add dvc-storage/.gitkeep
git add sisi_lola_chat/.streamlit/config.toml
git add sisi_lola_chat/requirements.txt
git add SECURITY_PUSH_GUIDE.md

# 3. Remove tracked sensitive files from git (but keep locally)
git rm --cached sisi_lola_api/.env 2>$null
git rm --cached client_secrets.json 2>$null
git rm --cached youtube_token.json 2>$null
git rm --cached tools/curator/credentials.json 2>$null
git rm --cached data/youtube_credentials.json 2>$null

# 4. Commit the security fixes
git commit -m "🔒 SECURITY: Remove exposed credentials and add .gitignore protection"

# 5. Pull with rebase to sync with remote
git pull origin main --rebase

# 6. Force push (only if you own the repo and want to clean history)
# WARNING: This rewrites history - coordinate with team members
git push origin main --force-with-lease
```

---

## 🧹 OPTIONAL: Clean Git History (BFG Repo-Cleaner)

If you want to completely remove credentials from git history:

```powershell
# 1. Download BFG Repo-Cleaner
# From: https://rtyley.github.io/bfg-repo-cleaner/

# 2. Create a file with patterns to remove
@"
sk-proj-*
AIzaSy*
hf_*
pplx-*
sk_V2_*
sk-or-v1-*
"@ | Out-File -FilePath secrets-patterns.txt

# 3. Run BFG (requires Java)
java -jar bfg.jar --replace-text secrets-patterns.txt

# 4. Clean up
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 5. Force push
git push origin main --force
```

---

## ✅ VERIFICATION CHECKLIST

After pushing, verify:
- [ ] `.env` files are NOT in the repository
- [ ] `client_secrets.json` is NOT in the repository
- [ ] `youtube_token.json` is NOT in the repository
- [ ] `.env.example` IS in the repository (with placeholder values)
- [ ] All new API keys are working locally
- [ ] GitHub shows no sensitive data in recent commits

---

## 🔐 FUTURE BEST PRACTICES

1. **Never commit `.env` files** - They should always be in `.gitignore`
2. **Use environment variables** - Reference keys with `os.getenv("KEY_NAME")`
3. **Use GitHub Secrets** - For CI/CD pipelines
4. **Use Modal Secrets** - For Modal deployments: `modal secret create`
5. **Regular key rotation** - Rotate keys quarterly

---

## 📦 DVC STATUS

DVC is now configured with:
- **Local remote**: `dvc-storage/` (synced via Dropbox)
- **Auto-staging**: Enabled

To use DVC:
```powershell
# Track a large file
dvc add data/raw/videos/

# Push to remote storage
dvc push

# Pull data
dvc pull
```

---

## 🎨 STREAMLIT STATUS

Streamlit is configured with:
- **Theme**: Nigerian green (#008751)
- **Port**: 8501
- **Config**: `sisi_lola_chat/.streamlit/config.toml`

To run:
```powershell
cd sisi_lola_chat
streamlit run Home.py
```

---

Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
