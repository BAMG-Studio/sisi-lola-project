"""
HUGGINGFACE REPOSITORY SETUP
============================
Creates the required model repositories for Sisi Lola unified training pipeline.

Repositories to create:
1. sisilolalive/sisi-lola-personality - Personality model (DistilGPT2 fine-tuned)
2. sisilolalive/sisi-lola-brain-mistral - Brain model (Mistral-7B LoRA adapters)
3. sisilolalive/sisi-lola-voice-xtts - Voice model (XTTS speaker embeddings)

Run with: python setup_hf_repos.py
"""

from huggingface_hub import HfApi, create_repo, upload_file
from huggingface_hub.utils import RepositoryNotFoundError
import os

# Configuration
OWNER = "sisilolalive"  # Your HuggingFace username

REPOS = [
    {
        "name": "sisi-lola-personality",
        "type": "model",
        "description": "Sisi Lola Personality Model - DistilGPT2 fine-tuned for Nigerian cultural context with multi-language support (English, Yoruba, Pidgin, Igbo, Hausa)",
        "tags": ["text-generation", "personality", "nigerian", "multilingual", "distilgpt2"],
        "readme": """---
license: apache-2.0
language:
  - en
  - yo
  - pcm
  - ig
  - ha
tags:
  - text-generation
  - personality
  - nigerian
  - multilingual
  - sisi-lola
library_name: transformers
pipeline_tag: text-generation
---

# Sisi Lola Personality Model

Nigerian AI personality model fine-tuned on cultural context data.

## Languages Supported
- 🇬🇧 English (EN)
- 🇳🇬 Yoruba (YO)
- 🇳🇬 Nigerian Pidgin (NP)
- 🇳🇬 Igbo (IG)
- 🇳🇬 Hausa (HA)

## Usage

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("sisilolalive/sisi-lola-personality")
tokenizer = AutoTokenizer.from_pretrained("sisilolalive/sisi-lola-personality")

prompt = "Hello, how are you today?"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=100)
print(tokenizer.decode(outputs[0]))
```

## Training
- Base model: distilgpt2
- Training data: Curated Nigerian cultural conversations
- Fine-tuning: Full model fine-tuning with personality data
- Automated retraining: Every 2 days via Modal.com

## Part of Sisi Lola Project
[GitHub Repository](https://github.com/BAMG-Studio/sisi-lola-project)
"""
    },
    {
        "name": "sisi-lola-brain-mistral",
        "type": "model",
        "description": "Sisi Lola Brain Model - Mistral-7B with QLoRA adapters for intelligent Nigerian AI assistant",
        "tags": ["text-generation", "mistral", "lora", "nigerian", "multilingual"],
        "readme": """---
license: apache-2.0
language:
  - en
  - yo
  - pcm
  - ig
  - ha
tags:
  - text-generation
  - mistral
  - lora
  - peft
  - nigerian
  - sisi-lola
library_name: peft
base_model: mistralai/Mistral-7B-v0.1
pipeline_tag: text-generation
---

# Sisi Lola Brain Model (Mistral-7B + QLoRA)

High-performance Nigerian AI assistant brain powered by Mistral-7B with QLoRA fine-tuning.

## Model Details
- **Base Model:** mistralai/Mistral-7B-v0.1
- **Adapter:** QLoRA (4-bit quantization)
- **LoRA Config:** r=32, alpha=64, dropout=0.05
- **Target Modules:** q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj

## Languages Supported
- 🇬🇧 English (EN)
- 🇳🇬 Yoruba (YO)
- 🇳🇬 Nigerian Pidgin (NP)
- 🇳🇬 Igbo (IG)
- 🇳🇬 Hausa (HA)

## Usage

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

# Load base model with quantization
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
)

base_model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    quantization_config=bnb_config,
    device_map="auto",
)

# Load LoRA adapters
model = PeftModel.from_pretrained(base_model, "sisilolalive/sisi-lola-brain-mistral")
tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")

# Generate
prompt = "[EN] Hello! How can I help you today? [NP] Wetin you wan make I help you with?"
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=200)
print(tokenizer.decode(outputs[0]))
```

## Training
- GPU: NVIDIA A100-40GB (Modal.com)
- Training data: Curated conversations with quality ratings
- Automated retraining: Every 2 days

## Part of Sisi Lola Project
[GitHub Repository](https://github.com/BAMG-Studio/sisi-lola-project)
"""
    },
    {
        "name": "sisi-lola-voice-xtts",
        "type": "model",
        "description": "Sisi Lola Voice Model - XTTS-v2 speaker embeddings for Nigerian voice synthesis",
        "tags": ["text-to-speech", "xtts", "voice-cloning", "nigerian", "tts"],
        "readme": """---
license: apache-2.0
language:
  - en
  - yo
  - pcm
tags:
  - text-to-speech
  - xtts
  - voice-cloning
  - nigerian
  - sisi-lola
library_name: coqui-tts
pipeline_tag: text-to-speech
---

# Sisi Lola Voice Model (XTTS-v2 Embeddings)

Nigerian voice synthesis using XTTS-v2 speaker embeddings for authentic voice cloning.

## Model Details
- **Base TTS:** coqui/XTTS-v2
- **Voice Style:** Nigerian English with cultural authenticity
- **Format:** Speaker embeddings (.pth files)

## Voice Routing System
The Sisi Lola voice system uses language tags to route to appropriate TTS engines:

| Tag | Language | Primary Engine |
|-----|----------|----------------|
| `[EN]` | English | XTTS-v2 (this model) |
| `[NP]` | Pidgin | YarnGPT / XTTS |
| `[YO]` | Yoruba | VITS-Yoruba |
| `[IG]` | Igbo | YarnGPT |
| `[HA]` | Hausa | YarnGPT |

## Usage

```python
from TTS.api import TTS
import torch

# Load XTTS model
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Load Sisi Lola speaker embedding
from huggingface_hub import hf_hub_download
embedding_path = hf_hub_download(
    repo_id="sisilolalive/sisi-lola-voice-xtts",
    filename="speaker_embedding.pth"
)
speaker_embedding = torch.load(embedding_path)

# Synthesize with Sisi Lola voice
tts.tts_to_file(
    text="Hello! How are you doing today?",
    file_path="output.wav",
    speaker_embedding=speaker_embedding,
    language="en",
)
```

## Files
- `speaker_embedding.pth` - Main speaker embedding tensor
- `gpt_cond_latent.pth` - GPT conditioning latent (for XTTS)
- `config.json` - Voice configuration

## Part of Sisi Lola Project
[GitHub Repository](https://github.com/BAMG-Studio/sisi-lola-project)
"""
    }
]


def create_repositories():
    """Create all required HuggingFace repositories"""
    api = HfApi()
    
    # Get current user info
    user_info = api.whoami()
    print(f"🔑 Authenticated as: {user_info['name']}")
    print(f"📧 Full name: {user_info.get('fullname', 'N/A')}")
    print()
    
    results = []
    
    for repo_config in REPOS:
        repo_id = f"{OWNER}/{repo_config['name']}"
        print(f"{'='*60}")
        print(f"📦 Setting up: {repo_id}")
        print(f"{'='*60}")
        
        # Check if repo exists
        try:
            repo_info = api.repo_info(repo_id=repo_id, repo_type="model")
            print(f"✅ Repository already exists!")
            print(f"   URL: https://huggingface.co/{repo_id}")
            results.append({"repo": repo_id, "status": "exists", "url": f"https://huggingface.co/{repo_id}"})
        except RepositoryNotFoundError:
            # Create the repository
            print(f"📝 Creating new repository...")
            try:
                url = create_repo(
                    repo_id=repo_id,
                    repo_type="model",
                    private=False,
                    exist_ok=True,
                )
                print(f"✅ Created: {url}")
                
                # Upload README
                print(f"📄 Uploading README.md...")
                readme_content = repo_config["readme"]
                
                # Create a temporary README file (Windows compatible)
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
                    f.write(readme_content)
                    readme_path = f.name
                
                api.upload_file(
                    path_or_fileobj=readme_path,
                    path_in_repo="README.md",
                    repo_id=repo_id,
                    repo_type="model",
                    commit_message="Initial README with model documentation",
                )
                print(f"✅ README uploaded!")
                
                results.append({"repo": repo_id, "status": "created", "url": str(url)})
                
            except Exception as e:
                print(f"❌ Error creating repo: {e}")
                results.append({"repo": repo_id, "status": "error", "error": str(e)})
        
        print()
    
    # Summary
    print(f"{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    
    for result in results:
        status_icon = "✅" if result["status"] in ["exists", "created"] else "❌"
        print(f"{status_icon} {result['repo']}: {result['status']}")
        if "url" in result:
            print(f"   🔗 {result['url']}")
    
    print()
    print("🎉 HuggingFace repository setup complete!")
    print()
    print("Next steps:")
    print("1. Add speaker reference WAV to: ml_training/data/speaker_reference.wav")
    print("2. Trigger a training run: modal run ml_training/modal_unified_training.py")
    print("3. Models will be automatically pushed to these repos after training")
    
    return results


if __name__ == "__main__":
    create_repositories()
