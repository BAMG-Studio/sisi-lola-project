#!/bin/bash
# Sisi Lola Clean Push Script

# 1. Add everything (now sanitized)
git add .

# 2. Try to commit
git commit -m "🚀 SISI LOLA: Final Production Ready (Security Sanitized)" || echo "No new changes to commit"

# 3. Pull latest from remote to stay in sync
echo "📥 Integrating remote changes..."
git pull --rebase origin main

# 4. Push to main
echo "📤 Pushing to main..."
git push origin main
