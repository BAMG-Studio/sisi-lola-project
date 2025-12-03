# 🚀 Sisi Lola Social Media Automation - Deployment Guide

This guide details how to deploy, configure, and run the Sisi Lola social media automation system. The system handles content generation, scheduling, posting, and analytics across 9 platforms.

---

## 📋 System Requirements

- **OS:** Windows (via WSL2) or Linux (Ubuntu 20.04+)
- **Python:** 3.8 or higher
- **Database:** SQLite (built-in)
- **Network:** Internet access for API calls

---

## 🛠️ Installation & Setup

### 1. Environment Setup
The project uses a virtual environment to manage dependencies.

```bash
# Navigate to project root
cd /mnt/c/Users/POK28/Dropbox/Sisi_Lola

# Create virtual environment (if not exists)
python3 -m venv .venv_auto

# Activate environment
source .venv_auto/bin/activate

# Install dependencies
pip install -r requirements_automation.txt
```

### 2. Database Initialization
The system uses a local SQLite database (`00_PROJECT_CORE/PROJECT_DB.sqlite`).

```bash
# Initialize DB and seed initial data
export PROJECT_DB_PATH="$PWD/00_PROJECT_CORE/PROJECT_DB.sqlite"
python3 00_PROJECT_CORE/Scripts/social_media_account_db.py
```

### 3. Platform Configuration
Platform details are stored in `00_PROJECT_CORE/platforms_config.json`.

**To update platform data:**
1. Edit `00_PROJECT_CORE/platforms_config.json`
2. Run the batch ingestion script:
   ```bash
   python3 00_PROJECT_CORE/Scripts/batch_platform_ingestion.py
   ```

---

## 🔑 Credential Management

**⚠️ SECURITY WARNING:** Never commit `.env` files or raw credentials to version control.

### Managing Credentials
Use the interactive credential manager to securely add/update API keys.

```bash
python3 00_PROJECT_CORE/Scripts/oauth_credential_manager.py
```
Follow the on-screen prompts to select a platform and enter credentials (Client ID, Secret, Tokens).

---

## 🤖 Running the Automation

### Master Orchestrator
The orchestrator is the main entry point. It guides you through the entire workflow:
1. **Generate Content** (using templates)
2. **Schedule Posts** (optimal timing)
3. **Post to Platforms** (API integration)
4. **View Reports** (analytics)

**Run the Orchestrator:**
```bash
python3 00_PROJECT_CORE/Scripts/master_orchestrator.py
```

### Individual Components
You can also run specific components independently:

- **Content Generator:**
  ```bash
  python3 00_PROJECT_CORE/Scripts/content_template_generator.py
  ```

- **Scheduler:**
  ```bash
  python3 00_PROJECT_CORE/Scripts/automated_content_scheduler.py
  ```

- **Unified Poster (Manual/API):**
  ```bash
  python3 00_PROJECT_CORE/Scripts/unified_api_poster.py
  ```

---

## 🧪 Testing & Validation

Run the comprehensive test suite to ensure all systems are go.

```bash
export PROJECT_DB_PATH="$PWD/00_PROJECT_CORE/PROJECT_DB.sqlite"
python3 00_PROJECT_CORE/Scripts/comprehensive_test_suite.py
```

**Expected Output:** `OK` with 100% success rate.

---

## 📂 Directory Structure

- `00_PROJECT_CORE/`
  - `PROJECT_DB.sqlite`: Main database
  - `platforms_config.json`: Platform metadata
  - `Scripts/`: All automation scripts
    - `master_orchestrator.py`: Main CLI
    - `unified_api_poster.py`: API logic
    - `automated_content_scheduler.py`: Scheduling logic
    - `social_media_account_db.py`: DB management
  - `03_MEDIA_ASSETS/content_queue/`: Generated schedules & CSVs

---

## 🆘 Troubleshooting

**Issue: "Module not found"**
- **Fix:** Ensure virtual environment is activated (`source .venv_auto/bin/activate`) and requirements are installed.

**Issue: "Database locked"**
- **Fix:** Ensure no other script is writing to the DB simultaneously.

**Issue: API Authentication Errors**
- **Fix:** Re-run `oauth_credential_manager.py` to refresh tokens. Check `.env` file for correct keys.

---

**Maintained by:** BAMG Studio / Sisi Lola Tech Team
**Last Updated:** December 1, 2025
