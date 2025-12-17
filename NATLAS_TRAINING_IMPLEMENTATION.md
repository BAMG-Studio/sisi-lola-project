# N-ATLaS Training Implementation for Sisi Lola

## Overview

This document outlines the complete implementation of the N-ATLaS training pipeline for Sisi Lola, as recommended in the Perplexity search results. The system enables continuous learning through chatbox interactions and autonomous social media engagement.

## Implementation Status

### ✅ Completed Components

#### 1. Conversation Logging System
**Location**: `ml_training/conversation_logger.py`

**Features**:
- JSONL-based conversation storage
- Session tracking with unique IDs
- Metadata capture (platform, language, topic, rating)
- Quality rating system (1-5 scale)
- Keep-for-training flags

**Usage**:
```python
from ml_training.conversation_logger import ConversationLogger

logger = ConversationLogger()
interaction_id = logger.log_interaction(
    session_id="chat_123",
    user_message="How do I learn DevSecOps?",
    model_response="Omo, DevSecOps na very important skill o!",
    model_used="N-ATLaS",
    metadata={"language": "english_nigerian", "topic": "devsecops"},
    rating=5
)
```

#### 2. Training Data Curation Pipeline
**Location**: `ml_training/curate_training_data.py`

**Features**:
- Quality filtering (rating >= 3, non-empty, non-toxic)
- Instruction format conversion for N-ATLaS
- Personality system prompt integration
- Spam/toxic content filtering
- Dataset statistics and analytics

**Format**:
```json
{
  "system": "You are Sisi Lola, a confident, funny, and charismatic Nigerian virtual host...",
  "user": "<user_message>",
  "assistant": "<model_response>",
  "metadata": {...}
}
```

**Usage**:
```bash
python ml_training/curate_training_data.py
# Outputs: ml_training/datasets/curated_chat_data.jsonl
```

#### 3. Social Media Bot Infrastructure
**Location**: `social_media_bot/`

**YouTube Bot** (`youtube/youtube_bot.py`):
- Comment monitoring via YouTube Data API v3
- Intent classification (question, praise, spam, toxic)
- Sisi Lola-style response generation
- Automatic training data logging
- Rate limiting (10,000 units/day)
- Dry-run mode for testing

**Features**:
- ✅ Comment fetching
- ✅ Intent classification
- ✅ Response generation (template-based)
- ✅ Training data logging
- ✅ Rate limiting
- ✅ Safety filters
- ⏳ Full N-ATLaS API integration (pending)

### ⏳ Pending Components

#### 1. N-ATLaS API Integration
**Location**: `sisi_lola_api/`

**Requirements**:
- Expose N-ATLaS as HTTP endpoint
- Follow pattern: `/chat/natlas`
- Support system prompts with personality
- Return structured responses

**Integration Points**:
```python
# In social_media_bot/youtube/youtube_bot.py
def generate_reply(self, comment_text, classification):
    response = requests.post(
        self.model_endpoint,
        headers={"Authorization": f"Bearer {self.api_key}"},
        json={
            "messages": [
                {"role": "system", "content": SISI_PERSONALITY_PROMPT},
                {"role": "user", "content": comment_text}
            ],
            "max_tokens": 150,
            "temperature": 0.8
        }
    )
    return response.json()["choices"][0]["message"]["content"]
```

#### 2. Instagram Bot
**Location**: `social_media_bot/instagram/`

**TODO**:
- Implement Instagram Graph API integration
- Comment/DM monitoring
- Story mention tracking
- Similar structure to YouTube bot

#### 3. Chat UI Integration
**Location**: `sisi_lola_chat/`

**Requirements**:
- Import ConversationLogger
- Log every chat interaction
- Add rating UI (thumbs up/down)
- Store session metadata

**Pseudocode**:
```javascript
// In chat UI
onUserMessage(message) {
  const response = await callNATLaSAPI(message);
  
  // Log interaction
  await logInteraction({
    session_id: sessionId,
    user_message: message,
    model_response: response,
    model_used: "N-ATLaS",
    metadata: {
      platform: "web_chat",
      timestamp: Date.now()
    }
  });
  
  return response;
}

onUserRating(interactionId, thumbsUp) {
  await updateRating(interactionId, thumbsUp ? 5 : 1);
}
```

#### 4. Automated Retraining Pipeline
**Location**: `.github/workflows/retrain_model.yml`

**Workflow**:
1. **Trigger**: Weekly schedule or manual
2. **Steps**:
   - Fetch latest chat logs
   - Run curation pipeline
   - Filter high-quality examples (rating >= 4)
   - Merge with existing training data
   - Run N-ATLaS fine-tuning script
   - Deploy updated model
   - Update personality version

**Example Workflow**:
```yaml
name: Retrain Sisi Lola N-ATLaS

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  retrain:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Curate training data
        run: python ml_training/curate_training_data.py
        
      - name: Run fine-tuning
        run: |
          python ml_training/fine_tune_natlas.py \
            --input ml_training/datasets/curated_chat_data.jsonl \
            --output models/sisi_lola_natlas_v2.bin \
            --epochs 3 \
            --learning_rate 1e-5
        
      - name: Deploy model
        run: python deploy_model.py --model models/sisi_lola_natlas_v2.bin
```

#### 5. Video Generation Integration
**Location**: `03_MEDIA_ASSETS/`, `04_AUDIO_CORE/`

**Workflow**:
```
User/Automation Request
  ↓
sisi_lola_api (N-ATLaS endpoint)
  ↓
Generate Script
  ↓
04_AUDIO_CORE/test_audio_generation.py (TTS)
  ↓
wav2lip_workspace (Lip Sync)
  ↓
06_RENDER_OUTPUT (Final Video)
```

**Implementation**:
```python
# Automation script
from sisi_lola_api import generate_script
from audio_core import generate_audio
from wav2lip import sync_audio_video

def generate_video(topic, duration=60):
    # 1. Generate script with N-ATLaS
    script = generate_script(topic, max_words=duration*3)
    
    # 2. Generate audio
    audio_file = generate_audio(script, voice="sisi_lola")
    
    # 3. Sync with avatar
    video_file = sync_audio_video(
        audio=audio_file,
        reference_image="01_AVATAR_DNA/reference.jpg"
    )
    
    return video_file
```

## Training Data Requirements

Based on Perplexity recommendations:

### 1. Personality and Style Spec
✅ **Implemented** in `curate_training_data.py`:
```
Confidence: 8.5/10
Humor: 8.5/10
Charisma: 9.0/10
Authenticity: 9.0/10
Empowerment: 9.0/10

Communication Style:
- Mix English and Nigerian Pidgin
- Use observational humor
- Charismatic storytelling
- Catchphrases: "Omo see gobe!", "E choke!", "Las las, we go dey alright!"
```

### 2. Brand and Knowledge Datasets
⏳ **TODO**: Create structured Q&A datasets in `datasets/`

**Topics**:
- DevSecOps explanations (Naija context)
- Social media/creator advice
- Diaspora life discussions
- Nigerian culture and technology

**Format**:
```json
{
  "question": "How can I start a tech career in Nigeria?",
  "answer": "Omo, tech career in Naija dey very sweet o! First, you fit learn coding free on platforms like FreeCodeCamp...",
  "category": "career_advice",
  "language": "english_nigerian"
}
```

### 3. Dialogue and Safety Data
✅ **Partially Implemented** in YouTube bot

**Safety Filters**:
- Toxic keywords: hate, kill, die
- Spam keywords: spam, scam, click here
- Action: hide or ignore

⏳ **TODO**: Expand with:
- Red-team prompts for politics, NSFW, medical/financial advice
- Target safe responses for each category
- Multi-turn conversation examples

## Expected Results

From Perplexity recommendations:

### 1. Natural Naija Code-Switching ✅
- Mix Nigerian-accented English, Yoruba, Pidgin
- Fewer "Westernized" assumptions
- Better understanding of local entities (JAMB, NYSC, etc.)

### 2. Consistent Sisi Lola Character ✅
- Stable tone across platforms
- Same humor, empathy, catchphrases
- Reduced personality drift

### 3. Improved Multilingual Reach ⏳
- Ability to answer in Yoruba/English blend
- Stronger resonance with Nigeria-based audience
- Serve diaspora in clean English

### 4. Lower Hallucination (with RAG) ⏳
- More accurate answers about offers/pricing
- Better grounding on Nigeria-specific facts

## Next Steps (Priority Order)

1. **✅ DONE**: Create conversation logging system
2. **✅ DONE**: Create training data curation pipeline  
3. **✅ DONE**: Build social media bot scaffolding
4. **🔄 IN PROGRESS**: Integrate N-ATLaS API with bots
5. **TODO**: Add logging to sisi_lola_chat UI
6. **TODO**: Create automated retraining GitHub Actions
7. **TODO**: Implement Instagram bot
8. **TODO**: Build brand knowledge Q&A datasets
9. **TODO**: Set up video generation integration
10. **TODO**: Deploy to production with monitoring

## Monitoring and Iteration

### Metrics to Track
1. **Data Collection**:
   - Interactions logged per day
   - Training examples generated
   - Platforms coverage (YouTube, Instagram, Web Chat)

2. **Model Performance**:
   - Response quality ratings
   - Code-switching accuracy
   - Personality consistency scores

3. **Engagement**:
   - Comment reply rate
   - User follow-up rate
   - Positive sentiment %

### Review Cycle
- **Daily**: Check recent logs for quality
- **Weekly**: Curate and review training examples
- **Biweekly**: Fine-tune model with new data
- **Monthly**: Evaluate overall performance metrics

## References

- Perplexity Search: [Training Sisi Lola with N-ATLaS](https://www.perplexity.ai/search/voice-what-do-i-need-to-know-a-SZcRYyMCTmKNfA5sD_iJsA)
- N-ATLaS Model: [HuggingFace](https://huggingface.co/NCAIR1/N-ATLaS)
- YouTube Data API: [Documentation](https://developers.google.com/youtube/v3/docs)
- Instagram Graph API: [Documentation](https://developers.facebook.com/docs/instagram-api)

## Contact

**Author**: BAMG Studio (seun.beaconagiletech@gmail.com)  
**Last Updated**: December 17, 2025  
**Version**: 1.0.0
