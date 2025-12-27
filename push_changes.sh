#!/bin/bash
# Sisi Lola Clean Push Script (Linux/WSL)

# Add changes
git add .

# Try to commit
git commit -m "🚀 SISI LOLA: Final Production Ready (Security Sanitized & Optimized)" || echo "No new changes to commit"

# Pull latest from remote
echo "📥 Integrating remote changes..."
git pull --rebase origin main

# Push to main
echo "📤 Pushing to main..."
git push origin main
