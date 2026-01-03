# Sisi Lola Git Push Script
# Run this in PowerShell: .\push_changes.ps1

$ErrorActionPreference = "Continue"
Set-Location "C:\Users\POK28\Dropbox\Sisi_Lola"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "       SISI LOLA GIT PUSH SCRIPT           " -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Step 1: Show current state
Write-Host "`n[1/7] Current commits (local):" -ForegroundColor Yellow
git log --oneline -5

Write-Host "`n[2/7] Staging security files..." -ForegroundColor Yellow
git add .gitignore .env.example dvc.yaml params.yaml SECURITY_PUSH_GUIDE.md push_changes.ps1
git add "dvc-storage/.gitkeep" "sisi_lola_chat/.streamlit/config.toml" "sisi_lola_chat/requirements.txt" ".dvc/config"

# Step 2: Remove sensitive files from tracking
Write-Host "`n[3/7] Removing sensitive files from git tracking..." -ForegroundColor Yellow
git rm --cached "sisi_lola_api/.env" 2>$null
git rm --cached "client_secrets.json" 2>$null  
git rm --cached "youtube_token.json" 2>$null
git rm --cached "tools/curator/credentials.json" 2>$null
git rm --cached "data/youtube_credentials.json" 2>$null

# Step 3: Show status
Write-Host "`n[4/7] Current git status:" -ForegroundColor Yellow
git status --short

# Step 4: Commit if there are changes
Write-Host "`n[5/7] Committing changes..." -ForegroundColor Yellow
$commitResult = git commit -m "SECURITY: Remove exposed credentials, configure DVC and Streamlit" 2>&1
Write-Host $commitResult

# Step 5: Fetch and handle divergence
Write-Host "`n[6/7] Syncing with remote..." -ForegroundColor Yellow
git fetch origin main

# Check if we need to rebase
$behindCount = git rev-list --count HEAD..origin/main 2>$null
$aheadCount = git rev-list --count origin/main..HEAD 2>$null

Write-Host "Local is $aheadCount commits ahead, $behindCount commits behind origin/main"

if ($behindCount -gt 0) {
    Write-Host "Rebasing on top of origin/main..." -ForegroundColor Magenta
    git rebase origin/main
}

# Step 6: Push
Write-Host "`n[7/7] Pushing to origin/main..." -ForegroundColor Yellow
git push origin main --force-with-lease

# Verify
Write-Host "`n============================================" -ForegroundColor Green
Write-Host "             VERIFICATION                   " -ForegroundColor Green  
Write-Host "============================================" -ForegroundColor Green
Write-Host "Remote commits after push:" -ForegroundColor Yellow
git log origin/main --oneline -5

Write-Host "`n✅ DONE! Check GitHub to verify." -ForegroundColor Green
Write-Host "GitHub URL: https://github.com/BAMG-Studio/sisi-lola-project" -ForegroundColor Cyan
