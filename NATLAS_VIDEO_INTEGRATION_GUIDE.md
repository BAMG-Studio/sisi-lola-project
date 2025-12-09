# N-ATLaS Integration Guide: Video Generation & Chat Data Collection

## Overview

This guide covers two critical paths:
1. **Integrating N-ATLaS LoRA adapter** into the video production pipeline
2. **Collecting chat data** from local Sisi Lola chatbox for retraining

---

## 🎬 PART 1: N-ATLaS Integration into Video Pipeline

### Current Video Pipeline Flow
```
Topic → GPT-4o Script → HeyGen Avatar → YouTube Upload
```

### Enhanced Flow with N-ATLaS
```
Topic → N-ATLaS Brain (LoRA) → Enhanced Script → Your Voice Model → Video → Upload
```

### Step 1: Load the N-ATLaS LoRA Adapter

When training completes, your adapter will be at:
- **HuggingFace**: `BAMG-Studio/sisi-lola-brain-lora`
- **Local backup**: `ml_training/outputs/brain/`

```python
# sisi_lola_api/app/utils/natlas_brain.py

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

class NATLaSBrain:
    """Sisi Lola's N-ATLaS Brain with Nigerian language fine-tuning"""
    
    def __init__(self, 
                 base_model: str = "ALT-AI/natlas-24-afro-llm-7b",
                 adapter_path: str = "BAMG-Studio/sisi-lola-brain-lora"):
        """
        Initialize N-ATLaS Brain with Sisi Lola's LoRA adapter
        
        Args:
            base_model: N-ATLaS base model
            adapter_path: HuggingFace path or local path to LoRA adapter
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
        
        # Load base model
        self.model = AutoModelForCausalLM.from_pretrained(
            base_model,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto",
            trust_remote_code=True
        )
        
        # Apply LoRA adapter
        try:
            self.model = PeftModel.from_pretrained(self.model, adapter_path)
            print(f"✓ Loaded Sisi Lola LoRA adapter from {adapter_path}")
        except Exception as e:
            print(f"⚠ Could not load LoRA adapter: {e}")
            print("  Using base N-ATLaS model")
        
        self.model.eval()
    
    def generate_script(self, 
                       topic: str, 
                       duration_minutes: int = 5,
                       language_ratio: dict = None) -> str:
        """
        Generate video script with authentic Nigerian flavor
        
        Args:
            topic: Video topic
            duration_minutes: Target duration
            language_ratio: Dict with yoruba/pidgin/english percentages
        """
        if language_ratio is None:
            language_ratio = {"yoruba": 60, "pidgin": 30, "english": 10}
        
        words_needed = duration_minutes * 150  # ~150 words per minute
        
        prompt = f"""You are Sisi Lola, a vibrant Nigerian AI content creator.
Generate a {duration_minutes}-minute video script about: {topic}

Language Mix:
- {language_ratio['yoruba']}% Yoruba (ẹ, ọ, ṣ, authentic greetings, proverbs)
- {language_ratio['pidgin']}% Nigerian Pidgin (dey, don, go, fit, wahala, wetin)
- {language_ratio['english']}% English (technical terms only)

Requirements:
- Approximately {words_needed} words
- Natural code-switching like a Lagos girl
- Strong opening hook: "Ẹ káàbọ̀ o! Báwo ni?"
- Cultural references and proverbs
- Engaging, educational, entertaining
- Call-to-action ending

SCRIPT:"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=words_needed * 2,  # Allow for tokenization overhead
                temperature=0.8,
                top_p=0.9,
                do_sample=True,
                repetition_penalty=1.1
            )
        
        script = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract just the generated script after "SCRIPT:"
        if "SCRIPT:" in script:
            script = script.split("SCRIPT:")[-1].strip()
        
        return script
    
    def enhance_script(self, raw_script: str) -> str:
        """Enhance an existing script with more Nigerian flavor"""
        prompt = f"""You are Sisi Lola. Take this script and make it more authentically Nigerian:
- Add Yoruba greetings and expressions
- Add Nigerian Pidgin where it flows naturally
- Keep the meaning but add your personality
- Include humor and warmth

Original Script:
{raw_script}

Enhanced Nigerian Script:"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=len(raw_script.split()) * 3,
                temperature=0.7,
                do_sample=True
            )
        
        enhanced = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        if "Enhanced Nigerian Script:" in enhanced:
            enhanced = enhanced.split("Enhanced Nigerian Script:")[-1].strip()
        
        return enhanced


# Singleton instance
_brain_instance = None

def get_natlas_brain() -> NATLaSBrain:
    """Get or create the N-ATLaS brain instance"""
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = NATLaSBrain()
    return _brain_instance
```

### Step 2: Update Video Generation Scripts

Modify `00_PROJECT_CORE/Scripts/yoruba_content_generator.py`:

```python
# Add at top of file
from sisi_lola_api.app.utils.natlas_brain import get_natlas_brain

# In YorubaContentGenerator class, add method:
def generate_with_natlas(self, topic: str, duration_minutes: int = 7) -> str:
    """Generate script using local N-ATLaS model instead of Cohere API"""
    try:
        brain = get_natlas_brain()
        return brain.generate_script(topic, duration_minutes)
    except Exception as e:
        print(f"N-ATLaS failed, falling back to Cohere: {e}")
        return self.generate_yoruba_script(topic, duration_minutes)
```

### Step 3: Integration Points

| Script | Current | With N-ATLaS |
|--------|---------|--------------|
| `generate_first_video.py` | OpenAI GPT-4 | N-ATLaS Brain |
| `batch_video_generator.py` | OpenAI GPT-4 | N-ATLaS Brain |
| `auto_generate_and_upload.py` | OpenAI GPT-4 | N-ATLaS Brain |
| `yoruba_content_generator.py` | Cohere Command-A | N-ATLaS Brain |

---

## 📊 PART 2: Chat Data Collection for Retraining

### Why Collect Chat Data?

The local Sisi Lola chatbox generates real conversations that can:
1. Train better Nigerian language responses
2. Improve voice naturalness through user feedback
3. Expand vocabulary with real usage patterns
4. Build preference data for RLHF

### Architecture: Chat → Database → Training

```
┌─────────────────────────────────────────────────────────────────────┐
│  Local Chat Interface                                                │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ User: "How you dey?"                                           │ │
│  │ Sisi: "Omo! I dey kampe o! 🇳🇬"                                │ │
│  └───────────────────────────────────────────────────────────────┘ │
│              │                                                       │
│              ▼ [Auto-save on each exchange]                         │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ SQLite: chat_training_data.db                                  │ │
│  │ - conversation_id                                              │ │
│  │ - timestamp                                                    │ │
│  │ - user_message                                                 │ │
│  │ - assistant_response                                           │ │
│  │ - model_used (gpt4/aya/claude)                                │ │
│  │ - voice_engine (elevenlabs/coqui/edge)                        │ │
│  │ - user_rating (optional 👍👎)                                  │ │
│  │ - voice_rating (optional: natural/robotic)                    │ │
│  └───────────────────────────────────────────────────────────────┘ │
│              │                                                       │
│              ▼ [Export for training]                                │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ training_data.jsonl                                            │ │
│  │ {"prompt": "How you dey?", "response": "Omo! I dey kampe!"}   │ │
│  └───────────────────────────────────────────────────────────────┘ │
│              │                                                       │
│              ▼ [GitHub Push]                                         │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ HuggingFace Dataset: BAMG-Studio/sisi-lola-conversations      │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementation: Chat Data Logger

Create this file to add data collection to the chat:

```python
# sisi_lola_chat/chat_data_logger.py

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
import uuid

class ChatDataLogger:
    """
    Logs all chat interactions for future training.
    
    This creates a feedback loop:
    Chat → Database → Export → Training → Better Chat
    """
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "ml_training" / "data" / "chat_training_data.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with proper schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model_used TEXT,
                voice_engine TEXT,
                total_turns INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                role TEXT,  -- 'user' or 'assistant'
                content TEXT,
                -- Quality ratings (for RLHF)
                response_rating INTEGER,  -- 1-5 scale
                voice_naturalness INTEGER,  -- 1-5 scale
                humor_rating INTEGER,  -- 1-5 scale
                cultural_authenticity INTEGER,  -- 1-5 scale
                -- Metadata
                tokens_used INTEGER,
                generation_time_ms INTEGER,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                audio_path TEXT,
                voice_engine TEXT,
                is_natural BOOLEAN,
                pronunciation_issues TEXT,  -- JSON list of problematic words
                user_notes TEXT,
                FOREIGN KEY (message_id) REFERENCES messages(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_conversation(self, model: str, voice_engine: str = None) -> str:
        """Start a new conversation session"""
        conversation_id = str(uuid.uuid4())[:8]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO conversations (id, model_used, voice_engine) VALUES (?, ?, ?)',
            (conversation_id, model, voice_engine)
        )
        conn.commit()
        conn.close()
        
        return conversation_id
    
    def log_message(self, 
                    conversation_id: str,
                    role: str,
                    content: str,
                    tokens: int = 0,
                    gen_time_ms: int = 0) -> int:
        """Log a single message"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO messages (conversation_id, role, content, tokens_used, generation_time_ms)
            VALUES (?, ?, ?, ?, ?)
        ''', (conversation_id, role, content, tokens, gen_time_ms))
        
        message_id = cursor.lastrowid
        
        # Update conversation turn count
        cursor.execute(
            'UPDATE conversations SET total_turns = total_turns + 1 WHERE id = ?',
            (conversation_id,)
        )
        
        conn.commit()
        conn.close()
        
        return message_id
    
    def rate_response(self, message_id: int, 
                      response_rating: int = None,
                      voice_naturalness: int = None,
                      humor_rating: int = None,
                      cultural_authenticity: int = None):
        """Add quality ratings to a response (for RLHF)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        if response_rating:
            updates.append('response_rating = ?')
            values.append(response_rating)
        if voice_naturalness:
            updates.append('voice_naturalness = ?')
            values.append(voice_naturalness)
        if humor_rating:
            updates.append('humor_rating = ?')
            values.append(humor_rating)
        if cultural_authenticity:
            updates.append('cultural_authenticity = ?')
            values.append(cultural_authenticity)
        
        if updates:
            values.append(message_id)
            cursor.execute(
                f'UPDATE messages SET {", ".join(updates)} WHERE id = ?',
                values
            )
            conn.commit()
        
        conn.close()
    
    def log_voice_feedback(self,
                           message_id: int,
                           audio_path: str,
                           voice_engine: str,
                           is_natural: bool,
                           pronunciation_issues: list = None,
                           notes: str = None):
        """Log feedback about voice quality"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO voice_feedback 
            (message_id, audio_path, voice_engine, is_natural, pronunciation_issues, user_notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (message_id, audio_path, voice_engine, is_natural, 
              json.dumps(pronunciation_issues or []), notes))
        
        conn.commit()
        conn.close()
    
    def export_for_training(self, output_path: str = None, min_rating: int = 3) -> str:
        """
        Export high-quality conversations for training.
        
        Returns path to JSONL file suitable for fine-tuning.
        """
        if output_path is None:
            output_path = self.db_path.parent / f"training_export_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get conversations with good ratings
        cursor.execute('''
            SELECT c.id, m.role, m.content, m.response_rating
            FROM conversations c
            JOIN messages m ON c.id = m.conversation_id
            WHERE m.response_rating IS NULL OR m.response_rating >= ?
            ORDER BY c.id, m.timestamp
        ''', (min_rating,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Group by conversation
        conversations = {}
        for conv_id, role, content, rating in rows:
            if conv_id not in conversations:
                conversations[conv_id] = []
            conversations[conv_id].append({
                "role": role,
                "content": content,
                "rating": rating
            })
        
        # Write training data
        with open(output_path, 'w', encoding='utf-8') as f:
            for conv_id, messages in conversations.items():
                # Create instruction-response pairs
                for i in range(0, len(messages) - 1, 2):
                    if i + 1 < len(messages):
                        user_msg = messages[i]
                        assistant_msg = messages[i + 1]
                        
                        if user_msg["role"] == "user" and assistant_msg["role"] == "assistant":
                            training_example = {
                                "instruction": user_msg["content"],
                                "output": assistant_msg["content"],
                                "rating": assistant_msg.get("rating")
                            }
                            f.write(json.dumps(training_example, ensure_ascii=False) + '\n')
        
        print(f"✓ Exported training data to {output_path}")
        return str(output_path)
    
    def get_stats(self) -> dict:
        """Get statistics about collected data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM conversations')
        stats['total_conversations'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM messages')
        stats['total_messages'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM messages WHERE response_rating IS NOT NULL')
        stats['rated_messages'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(response_rating) FROM messages WHERE response_rating IS NOT NULL')
        avg = cursor.fetchone()[0]
        stats['avg_rating'] = round(avg, 2) if avg else None
        
        cursor.execute('SELECT COUNT(*) FROM voice_feedback')
        stats['voice_feedback_count'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM voice_feedback WHERE is_natural = 1')
        stats['natural_voice_count'] = cursor.fetchone()[0]
        
        conn.close()
        return stats
```

---

## 🔌 Integrating Data Logger into Chat

Update `sisi_lola_chat/chat_enhanced.py`:

```python
# Add import at top
from chat_data_logger import ChatDataLogger

# In SisiLolaEnhancedChat.__init__, add:
self.data_logger = ChatDataLogger()
self.conversation_id = self.data_logger.start_conversation(
    model=model,
    voice_engine=voice if voice != "none" else None
)

# In SisiLolaEnhancedChat.chat(), modify:
def chat(self, user_message: str) -> str:
    """Send message and get response"""
    import time
    
    # Log user message
    self.data_logger.log_message(
        self.conversation_id, 
        "user", 
        user_message
    )
    
    # Add to history
    self.conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    # Get response from LLM (with timing)
    start = time.time()
    response = self.llm.chat(self.conversation_history, self.system_prompt)
    gen_time = int((time.time() - start) * 1000)
    
    # Log assistant response
    self.last_message_id = self.data_logger.log_message(
        self.conversation_id,
        "assistant",
        response,
        gen_time_ms=gen_time
    )
    
    # Add response to history
    self.conversation_history.append({
        "role": "assistant",
        "content": response
    })
    
    return response

# Add rating method:
def rate_last_response(self, rating: int, voice_natural: bool = None):
    """Rate the last response (1-5)"""
    if hasattr(self, 'last_message_id'):
        self.data_logger.rate_response(
            self.last_message_id,
            response_rating=rating,
            voice_naturalness=5 if voice_natural else 2 if voice_natural is False else None
        )
        safe_print(f"[OK] Rating recorded: {rating}/5")
```

---

## 📱 Quick Rating Commands in Chat

Add these commands to the chat loop:

```python
# In the main chat loop, add command handlers:
if user_input.startswith('/rate '):
    try:
        rating = int(user_input.split()[1])
        chat.rate_last_response(rating)
        continue
    except:
        safe_print("Usage: /rate 1-5")
        continue

if user_input == '/voice good':
    chat.rate_last_response(None, voice_natural=True)
    continue

if user_input == '/voice bad':
    chat.rate_last_response(None, voice_natural=False)
    continue

if user_input == '/stats':
    stats = chat.data_logger.get_stats()
    safe_print(f"""
📊 Training Data Stats:
   Conversations: {stats['total_conversations']}
   Messages: {stats['total_messages']}
   Rated: {stats['rated_messages']}
   Avg Rating: {stats['avg_rating'] or 'N/A'}
   Voice Feedback: {stats['voice_feedback_count']}
    """)
    continue

if user_input == '/export':
    path = chat.data_logger.export_for_training()
    safe_print(f"[OK] Exported to {path}")
    continue
```

---

## 🔄 Retraining Workflow

### 1. Collect Data (Ongoing)
```bash
# Just use the chat normally
python sisi_lola_chat/chat_enhanced.py --voice elevenlabs

# Rate responses as you go
/rate 5  # Great response!
/rate 2  # Needs improvement
/voice good  # Voice sounds natural
/voice bad   # Voice sounds robotic
```

### 2. Export Training Data
```bash
# Via chat command
/export

# Or via script
python -c "from sisi_lola_chat.chat_data_logger import ChatDataLogger; ChatDataLogger().export_for_training()"
```

### 3. Upload to HuggingFace
```bash
# Add to existing dataset or create new
python ml_training/scripts/upload_training_data.py --file training_export_*.jsonl
```

### 4. Trigger Retraining
```bash
# GitHub Actions workflow
gh workflow run nigerian_training_pipeline.yml -f training_mode=full
```

---

## 🎯 Summary

| Component | Status | Integration Point |
|-----------|--------|-------------------|
| N-ATLaS Brain | Pending training completion | `natlas_brain.py` → Video scripts |
| N-ATLaS Voice | Pending training completion | Replace HeyGen voice |
| Chat Logger | Ready to implement | `chat_enhanced.py` |
| Export Pipeline | Ready to implement | `export_for_training()` |
| Retraining Trigger | Existing workflow | GitHub Actions |

### Next Steps:
1. ✅ Wait for Nigerian Training Pipeline to complete
2. 🔄 Add ChatDataLogger to chat_enhanced.py
3. 🔄 Start collecting conversation data
4. 🔄 Create natlas_brain.py for video integration
5. 🔄 Test N-ATLaS script generation quality
6. 🔄 Replace HeyGen voice with trained N-ATLaS voice

---

*Generated: December 2024*
