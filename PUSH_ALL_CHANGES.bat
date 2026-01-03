@echo off
REM ═══════════════════════════════════════════════════════════════════════════════
REM                    PUSH ALL CHANGES TO UPSTREAM MAIN
REM ═══════════════════════════════════════════════════════════════════════════════

echo ============================================
echo    Pushing Sisi Lola Updates to GitHub
echo ============================================

cd /d "c:\Users\POK28\Dropbox\Sisi_Lola"

echo.
echo [1/4] Adding new directories and files...
git add 09_FEEDBACK_LOOP
git add 10_METADATA_SYSTEM
git add 11_INTEGRATION
git add sisi_lola_chat/Home.py
git add sisi_lola_chat/pages

echo.
echo [2/4] Checking staged files...
git status --short

echo.
echo [3/4] Creating commit...
git commit -m "feat: Complete Sisi Lola Nigerian AI System - Feedback Loop, Metadata, Integration, Dashboard"

echo.
echo [4/4] Pushing to origin main...
git push origin main

echo.
echo ============================================
echo    Push Complete!
echo ============================================
pause
