#!/bin/bash
# Push all changes to GitHub and deploy to Modal

echo "🚀 SISI LOLA SUPREME DEPLOYMENT"
echo "================================"

# Stage all changes
git add -A

# Commit
git commit -m "🚀 SUPREME: Add conversation logging, Singstress, Social Dispatch, Live Engagement

Features Added:
- Conversation logger for training data refinement
- Singstress service (Lyria + Voice synthesis)  
- One-Click Social Dispatch (Instagram, TikTok, YouTube)
- Live Engagement batch comment processing
- Dashboard with new UI panels
- Public demo-chat endpoint (no auth required)
- Fixed .env loading for Modal deployment

Data Logging:
- All conversations logged for training refinement
- Export to JSONL for fine-tuning
- Analytics dashboard integration"

# Push
git push origin main

echo ""
echo "✅ Pushed to GitHub!"
echo ""
echo "📦 Now deploying to Modal..."
echo "Run: modal deploy sisi_lola_api/app/services/modal_stub.py"
