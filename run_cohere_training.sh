#!/bin/bash
# Cohere Training Automation Script

set -e

echo "🚀 Starting Cohere Training for Sisi Lola..."

# Set project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Load environment variables
if [ -f "sisi_lola_api/.env" ]; then
    export $(cat sisi_lola_api/.env | grep -v '^#' | xargs)
    echo "✅ Environment loaded"
else
    echo "❌ .env file not found"
    exit 1
fi

# Check for required variables
if [ -z "$COHERE_API_KEY" ]; then
    echo "❌ COHERE_API_KEY not set in .env"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r ml_training/requirements.txt
pip install -q cohere python-dotenv

# Run Ansible playbook
echo "🎭 Running Ansible playbook..."
ansible-playbook ansible/playbooks/cohere_training.yml \
    -e "github_token=${GITHUB_TOKEN:-}" \
    -e "github_repo=${GITHUB_REPO:-}" \
    -v

echo "✅ Training automation complete!"
echo "📊 Check ml_training/logs/ for reports"
