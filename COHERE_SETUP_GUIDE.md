# Cohere Integration Setup Guide

## Overview
This guide covers the integration of Cohere's language models with the Sisi Lola project for personality training and natural language understanding.

## Prerequisites
- Python 3.12+
- Ansible 2.15+
- Cohere API key (configured in `.env`)
- GitHub account (for Actions workflow)

## Quick Start

### 1. Verify Configuration
Your Cohere API key is already configured in `sisi_lola_api/.env`:
```
COHERE_API_KEY=RABGythRT0Pd58wLABvi2NYp1PNtHigKWOHlELIv
COHERE_MODEL=command-r-plus
COHERE_ENDPOINT=https://api.cohere.ai/v1
```

### 2. Install Dependencies
```bash
pip install -r ml_training/requirements.txt
pip install cohere python-dotenv
```

### 3. Run Training (Windows)
```cmd
run_cohere_training.bat
```

### 3. Run Training (Linux/Mac)
```bash
chmod +x run_cohere_training.sh
./run_cohere_training.sh
```

### 4. Manual Ansible Execution
```bash
ansible-playbook ansible/playbooks/cohere_training.yml -v
```

## Training Dataset
The personality training data is located at:
- `ml_training/datasets/sisi_lola_personality.txt`

This file contains Q&A pairs that define Sisi Lola's:
- Personality traits
- Communication style
- Cultural background
- Mission and values
- Language capabilities

## Cohere Models Available

### Command R+ (Recommended)
- Best for: Complex reasoning, multilingual tasks
- Context: 128K tokens
- Languages: 10+ including English

### Command R
- Best for: Fast responses, general tasks
- Context: 128K tokens
- Cost-effective alternative

### Command
- Best for: Simple tasks, high throughput
- Context: 4K tokens

## Training Process

### 1. Dataset Preparation
The training script automatically formats your data for Cohere's fine-tuning API:
```python
{
    "messages": [
        {"role": "user", "content": "question"},
        {"role": "assistant", "content": "answer"}
    ]
}
```

### 2. Fine-Tuning Job
The Ansible playbook:
1. Uploads dataset to Cohere
2. Creates fine-tuning job
3. Monitors training progress
4. Triggers GitHub Actions workflow

### 3. GitHub Actions Integration
The workflow automatically:
- Validates the trained model
- Runs quality checks
- Deploys to production (if tests pass)

## Monitoring Training

### Cohere Dashboard
Monitor your fine-tuning jobs at:
https://dashboard.cohere.com/fine-tuning

### Training Logs
Local logs are saved to:
```
ml_training/logs/cohere_training_[timestamp].md
```

### GitHub Actions
View workflow runs at:
```
https://github.com/[your-repo]/actions
```

## Using the Trained Model

### Python Integration
```python
import cohere
import os
from dotenv import load_dotenv

load_dotenv()

client = cohere.Client(os.getenv("COHERE_API_KEY"))

response = client.chat(
    model="sisi-lola-v1",  # Your fine-tuned model
    message="Tell me about yourself",
    temperature=0.7
)

print(response.text)
```

### API Integration
```python
# In your FastAPI app
from app.services.cohere_service import CohereService

cohere_service = CohereService()
response = cohere_service.generate_response(
    prompt="What's your style?",
    model="sisi-lola-v1"
)
```

## Ansible Playbook Details

### Variables
- `project_root`: Project directory path
- `env_file`: Path to .env file
- `training_script`: Cohere training script
- `github_token`: GitHub PAT for Actions (optional)
- `github_repo`: Repository name (optional)

### Tasks
1. Verify environment configuration
2. Install Python dependencies
3. Validate Cohere API key
4. Run training script
5. Trigger GitHub Actions workflow
6. Generate training report

## GitHub Actions Workflow

### Trigger Methods
1. **Manual**: Via workflow_dispatch
2. **Scheduled**: Weekly on Sundays at 2 AM UTC
3. **Automatic**: On push to training data directories

### Workflow Inputs
- `training_mode`: full, partial, or phasic
- `target_model`: all, natlas_audio, avatar_vision, content_classifier
- `target_phase`: foundation, refinement, production

### Workflow Jobs
1. **detect-training-need**: Analyzes changes and determines training requirements
2. **train-models**: Executes training via Ansible
3. **validate-models**: Runs validation suite
4. **deploy-models**: Deploys to HuggingFace Hub and production

## Extending the Training Data

### Add New Personality Traits
Edit `ml_training/datasets/sisi_lola_personality.txt`:
```
What's your favorite tech?
I'm fascinated by AI and VR technologies! They're transforming how we experience content and connect with each other. Plus, they let me exist and interact with you!
```

### Add Cultural Context
```
How do you celebrate Nigerian culture?
I celebrate Nigerian culture by incorporating our languages, fashion, music, and values into everything I do. From speaking Yoruba and Pidgin to showcasing African innovation!
```

### Add Domain Knowledge
```
What do you know about blockchain?
Blockchain is revolutionizing digital trust and ownership! It's particularly exciting for African creators who can now monetize their work globally without intermediaries.
```

## Troubleshooting

### API Key Issues
```bash
# Verify API key is set
python -c "import os; from dotenv import load_dotenv; load_dotenv('sisi_lola_api/.env'); print(os.getenv('COHERE_API_KEY'))"
```

### Training Failures
Check logs at:
- `ml_training/logs/cohere_training_*.md`
- Cohere dashboard: https://dashboard.cohere.com/

### GitHub Actions Not Triggering
Ensure you've set:
```bash
export GITHUB_TOKEN=your_github_pat
export GITHUB_REPO=username/repo-name
```

## Best Practices

### 1. Dataset Quality
- Use diverse, representative examples
- Include edge cases and variations
- Maintain consistent personality voice
- Cover multiple languages and contexts

### 2. Training Frequency
- Retrain when adding significant new content
- Schedule weekly updates for continuous improvement
- Monitor performance metrics

### 3. Version Control
- Tag each training run
- Document changes in training data
- Keep model versioning consistent

### 4. Testing
- Validate responses before deployment
- Test multilingual capabilities
- Check cultural appropriateness

## Cost Optimization

### Cohere Pricing
- Fine-tuning: Pay per training token
- Inference: Pay per generated token
- Use Command R for cost-effective production

### Tips
- Batch training updates
- Use smaller datasets for testing
- Monitor usage in dashboard

## Next Steps

1. ✅ API key configured
2. ✅ Training dataset created
3. ✅ Ansible playbook ready
4. ✅ GitHub Actions workflow configured
5. 🔄 Run initial training
6. 🔄 Validate model performance
7. 🔄 Deploy to production
8. 🔄 Monitor and iterate

## Support Resources

- Cohere Documentation: https://docs.cohere.com/
- Cohere Dashboard: https://dashboard.cohere.com/
- GitHub Actions Docs: https://docs.github.com/actions
- Ansible Documentation: https://docs.ansible.com/

---

**Status**: Ready for training
**Model**: Command R+
**API**: Configured
**Automation**: Enabled
