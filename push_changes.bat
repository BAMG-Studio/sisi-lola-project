@echo off
:: Sisi Lola Git Push Script (Windows - Robust)

echo 🚀 Adding changes...
git add .
git commit -m "🚀 SISI LOLA: Posting Engine Finalized, Instagram Polling, and Dropbox Hosting Integrated"

echo 📥 Pulling remote changes...
git pull --rebase origin main

echo 📤 Pushing to main...
git push origin main

if %ERRORLEVEL% EQU 0 (
    echo ✅ SUCCESS: Changes pushed to upstream main!
) else (
    echo ❌ FAILED: Push rejected. If you are SURE, use: git push origin main --force
)
pause
