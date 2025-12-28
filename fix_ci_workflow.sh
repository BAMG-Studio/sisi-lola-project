#!/bin/bash
echo "📦 Finalizing CI/CD Robustness..."
git add .
git commit -m "🧪 Refactor tests for isolation & fix CI database path"
git push origin main
echo "✅ Changes Pushed. Monitor GitHub Actions."
