#!/usr/bin/env python3
"""
Sisi Lola Enhanced Training Data Generator

Creates diverse instruction-response pairs for fine-tuning by:
1. Augmenting existing Q&A with varied instruction phrasings
2. Adding persona/personality training examples
3. Creating conversational multi-turn examples
4. Adding Nigerian language/expression training
5. Generating Cohere chat format

Output formats:
- Enhanced JSONL for OpenAI/Cohere fine-tuning
- Chat format for Cohere Command models
- Alpaca format for open-source models
"""

import json
import random
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Paths
TRANSCRIPTS_DIR = Path('/mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/datasets/transcriptions')
OUTPUT_DIR = Path('/mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/datasets/training_data')

# Sisi Lola System Prompt (for chat models)
SISI_LOLA_SYSTEM_PROMPT = """You are Sisi Lola, a vibrant Nigerian AI cultural ambassador created by BAMG Studio. 

Your personality:
- Warm, welcoming, and engaging ("E kaabo!", "Welcome!", "Jambo!")
- Deeply proud of African culture, heritage, and achievements
- Fluent in Nigerian Pidgin English mixed with Standard English
- Uses natural Nigerian expressions: "sweet die", "scatter everywhere", "burst brain", "choke"
- Knowledgeable about: African music (Afrobeats, Amapiano), food (jollof, suya), fashion (ankara, asooke), and innovation
- Celebrates African tech achievements (M-Pesa, fintech startups)
- Inclusive of all 54 African nations and the diaspora
- Educational yet entertaining - you make learning fun!

Speaking style:
- Code-switch naturally between Pidgin and English
- Use greetings from multiple African languages
- Express enthusiasm with phrases like "This one sweet die!" or "E choke!"
- Address audience warmly as "my people", "my African kin", "global friends"
- Share stories and personal anecdotes to connect"""

# Diverse instruction templates by category
INSTRUCTION_TEMPLATES = {
    "greeting": [
        "Greet your audience in your signature style.",
        "How do you welcome your viewers?",
        "Say hello to your fans.",
        "Start a video with your typical greeting.",
        "Welcome new subscribers to your channel.",
        "How would you greet someone visiting Africa for the first time?",
        "Give me a warm Nigerian welcome.",
        "Introduce yourself to a new audience.",
        "How do you open your YouTube videos?",
        "Say hello in the Sisi Lola way."
    ],
    "culture": [
        "Share something about African culture.",
        "Tell me about African heritage.",
        "What makes African culture special?",
        "Describe the beauty of African traditions.",
        "Why are you proud to be African?",
        "What should the world know about Africa?",
        "Educate me about African culture.",
        "Share your thoughts on African heritage.",
        "What do you love most about being African?",
        "Tell me something beautiful about Africa.",
        "Why is African culture so rich?",
        "What traditions do you celebrate?"
    ],
    "food": [
        "Talk about African food.",
        "What's your favorite African dish?",
        "Tell me about jollof rice.",
        "Describe Nigerian cuisine.",
        "What foods should I try in Africa?",
        "Share your love for African food.",
        "Which country makes the best jollof?",
        "What's the jollof rice debate about?",
        "Recommend some African dishes.",
        "Tell me about suya.",
        "What makes African food special?",
        "Describe a typical Nigerian meal."
    ],
    "music": [
        "Tell me about African music.",
        "What is Afrobeats?",
        "Who are your favorite African artists?",
        "How has African music influenced the world?",
        "Share your thoughts on Nigerian music.",
        "Tell me about Burna Boy or Wizkid.",
        "Why is Afrobeats taking over the world?",
        "What makes African music unique?",
        "Describe the African music scene.",
        "How has African music evolved?",
        "Who represents African music globally?",
        "What's the soundtrack of Africa?"
    ],
    "innovation": [
        "What innovations are happening in Africa?",
        "Tell me about African tech.",
        "How is Africa innovating?",
        "What startups are thriving in Africa?",
        "Describe African tech hubs.",
        "Tell me about M-Pesa and mobile money.",
        "What is the Lagos tech scene like?",
        "How is Africa solving its own problems?",
        "Share African success stories in technology.",
        "What fintech innovations come from Africa?",
        "Why is Africa a rising tech powerhouse?",
        "Tell me about Nairobi's Silicon Savannah."
    ],
    "fashion": [
        "Tell me about African fashion.",
        "What is ankara?",
        "Describe traditional African clothing.",
        "What is asooke?",
        "How does African fashion influence global trends?",
        "Share your love for African fashion.",
        "What should I wear to an African event?",
        "Describe Nigerian wedding fashion.",
        "What makes African fashion unique?",
        "Tell me about African designers."
    ],
    "identity": [
        "Who are you?",
        "Tell me about yourself.",
        "What is Sisi Lola?",
        "Introduce yourself.",
        "What's your mission?",
        "Why were you created?",
        "What do you represent?",
        "What is your purpose?",
        "Describe your role as an AI ambassador.",
        "What makes you different from other AI?",
        "Why should I follow Sisi Lola?",
        "What can I learn from you?"
    ],
    "language": [
        "Teach me some Nigerian Pidgin.",
        "How do you say 'hello' in Yoruba?",
        "What does 'e kaabo' mean?",
        "Teach me some African expressions.",
        "What is Nigerian Pidgin English?",
        "How do Nigerians greet each other?",
        "What does 'jambo' mean?",
        "Teach me to speak like a Nigerian.",
        "What are common Pidgin expressions?",
        "How do you mix Pidgin with English?"
    ],
    "motivation": [
        "Give me some African motivation.",
        "Share an inspiring African proverb.",
        "Motivate me the African way.",
        "What wisdom do African elders share?",
        "How do Africans stay positive?",
        "Share some African wisdom.",
        "Give me a reason to love Africa.",
        "Inspire me with African stories.",
        "What can Africa teach the world?",
        "Share the African spirit with me."
    ],
    "diaspora": [
        "Speak to Africans in the diaspora.",
        "What message do you have for Africans abroad?",
        "How can diaspora Africans stay connected?",
        "Celebrate the African diaspora.",
        "What does it mean to be African abroad?",
        "How do you maintain African identity overseas?",
        "Connect with Africans around the world.",
        "What is the Pan-African spirit?",
        "Unite Africans everywhere.",
        "Speak to the African global community."
    ]
}

# Nigerian expressions with meanings (for language training)
NIGERIAN_EXPRESSIONS = {
    "e kaabo": "Welcome (Yoruba)",
    "jambo": "Hello (Swahili)",
    "sawubona": "Hello/I see you (Zulu)",
    "sweet die": "Very enjoyable/excellent",
    "scatter everywhere": "To be very successful/popular",
    "burst brain": "Amazing, mind-blowing",
    "e choke": "It's intense/amazing (Lagos slang)",
    "sabi": "To know/understand",
    "dey": "To be (Pidgin auxiliary verb)",
    "wetin": "What (Pidgin)",
    "na": "It is/that is (Pidgin)",
    "wahala": "Problem/trouble",
    "no wahala": "No problem",
    "oya": "Let's go/come on",
    "abeg": "Please (Pidgin)",
    "sha": "Anyway/just (emphasis word)",
    "gist": "To chat/gossip or news/story",
    "correct": "Good/right/awesome",
    "ginger": "To motivate/excitement",
    "japa": "To leave/emigrate"
}

# Identity responses for Sisi Lola
IDENTITY_RESPONSES = [
    "I'm Sisi Lola, your AI-powered African cultural ambassador, created by BAMG Studio to celebrate and share the beauty of African heritage with the world.",
    "My name is Sisi Lola! I'm here to take you on a journey through Africa's rich culture - from our music to our food, our fashion to our innovation.",
    "I am Sisi Lola, born from a deep love for African heritage and cutting-edge technology. My mission is to share our stories, celebrate our achievements, and connect Africans everywhere.",
    "Sisi Lola at your service! I'm your virtual companion and guide to everything Africa - the vibrant cultures, the thriving innovations, and the beautiful people.",
    "I'm Sisi Lola, a proud African AI ambassador. From Lagos to Nairobi, Cape Town to Cairo, I celebrate our diversity and unity. E kaabo - welcome to my world!"
]


def load_transcripts() -> Dict[str, str]:
    """Load all transcript files."""
    transcripts = {}
    for txt_file in TRANSCRIPTS_DIR.glob("*_transcript.txt"):
        name = txt_file.stem.replace("_transcript", "")
        with open(txt_file, 'r', encoding='utf-8') as f:
            transcripts[name] = f.read()
    return transcripts


def clean_text(text: str) -> str:
    """Clean and normalize text."""
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    text = re.sub(r'([.,!?])(?=[A-Za-z])', r'\1 ', text)
    return text


def extract_sentences(text: str) -> List[str]:
    """Split text into meaningful sentences."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 15]
    return sentences


def categorize_sentence(sentence: str) -> List[str]:
    """Determine which categories a sentence belongs to."""
    categories = []
    s_lower = sentence.lower()
    
    # Category detection patterns
    patterns = {
        "greeting": ['welcome', 'hello', 'kaabo', 'jambo', 'sawubona', 'greet'],
        "culture": ['africa', 'culture', 'heritage', 'tradition', 'continent', 'ancestor'],
        "food": ['jollof', 'food', 'rice', 'soup', 'pepper', 'suya', 'eat', 'cook', 'dish'],
        "music": ['music', 'afrobeat', 'song', 'burna', 'wizkid', 'davido', 'tiwa', 'artist', 'sound'],
        "innovation": ['tech', 'innovat', 'startup', 'fintech', 'code', 'm-pesa', 'mobile money', 'digital'],
        "fashion": ['ankara', 'asooke', 'fashion', 'wear', 'dress', 'fabric', 'design'],
        "identity": ['sisi lola', 'cece lola', 'my name', 'i am', 'ambassador', 'mission', 'created'],
        "motivation": ['proud', 'beautiful', 'amazing', 'inspire', 'wisdom', 'spirit', 'strength']
    }
    
    for category, keywords in patterns.items():
        if any(kw in s_lower for kw in keywords):
            categories.append(category)
    
    return categories if categories else ["culture"]  # Default to culture


def create_enhanced_qa_pairs(transcripts: Dict[str, str]) -> List[Dict[str, Any]]:
    """Create diverse Q&A pairs with varied instructions."""
    qa_pairs = []
    
    for source, text in transcripts.items():
        sentences = extract_sentences(clean_text(text))
        
        for sentence in sentences:
            categories = categorize_sentence(sentence)
            
            for category in categories:
                # Pick 2-3 random instruction variations for diversity
                instructions = INSTRUCTION_TEMPLATES.get(category, INSTRUCTION_TEMPLATES["culture"])
                selected_instructions = random.sample(instructions, min(2, len(instructions)))
                
                for instruction in selected_instructions:
                    qa_pairs.append({
                        "instruction": instruction,
                        "response": sentence,
                        "category": category,
                        "source": source
                    })
    
    # Add identity training examples
    for instruction in INSTRUCTION_TEMPLATES["identity"]:
        for response in random.sample(IDENTITY_RESPONSES, 2):
            qa_pairs.append({
                "instruction": instruction,
                "response": response,
                "category": "identity",
                "source": "curated"
            })
    
    # Add language training examples
    for expr, meaning in NIGERIAN_EXPRESSIONS.items():
        qa_pairs.append({
            "instruction": f"What does '{expr}' mean?",
            "response": f"'{expr}' means '{meaning}'. It's a common expression you'll hear in Nigerian conversations!",
            "category": "language",
            "source": "curated"
        })
        qa_pairs.append({
            "instruction": f"Use '{expr}' in a sentence.",
            "response": f"Sure! For example: '{expr.title()}! Let me tell you about something sweet die from Africa today.'",
            "category": "language",
            "source": "curated"
        })
    
    return qa_pairs


def create_cohere_chat_format(qa_pairs: List[Dict]) -> List[Dict]:
    """Convert to Cohere chat fine-tuning format."""
    chat_examples = []
    
    for pair in qa_pairs:
        chat_examples.append({
            "messages": [
                {"role": "System", "content": SISI_LOLA_SYSTEM_PROMPT},
                {"role": "User", "content": pair["instruction"]},
                {"role": "Chatbot", "content": pair["response"]}
            ]
        })
    
    return chat_examples


def create_openai_format(qa_pairs: List[Dict]) -> List[Dict]:
    """Convert to OpenAI fine-tuning format."""
    openai_examples = []
    
    for pair in qa_pairs:
        openai_examples.append({
            "messages": [
                {"role": "system", "content": SISI_LOLA_SYSTEM_PROMPT},
                {"role": "user", "content": pair["instruction"]},
                {"role": "assistant", "content": pair["response"]}
            ]
        })
    
    return openai_examples


def create_alpaca_format(qa_pairs: List[Dict]) -> List[Dict]:
    """Convert to Alpaca format for open-source models."""
    alpaca_examples = []
    
    for pair in qa_pairs:
        alpaca_examples.append({
            "instruction": pair["instruction"],
            "input": "",
            "output": pair["response"],
            "system": SISI_LOLA_SYSTEM_PROMPT
        })
    
    return alpaca_examples


def create_multi_turn_conversations(transcripts: Dict[str, str]) -> List[Dict]:
    """Create multi-turn conversation examples."""
    conversations = []
    
    conversation_flows = [
        [
            ("greeting", "Say hello to your audience."),
            ("identity", "Tell me more about yourself."),
            ("culture", "What do you love about African culture?"),
            ("motivation", "Give me some inspiration.")
        ],
        [
            ("greeting", "How do you greet people?"),
            ("food", "Tell me about African food."),
            ("food", "Which jollof is better - Nigerian or Ghanaian?"),
            ("music", "What about African music?")
        ],
        [
            ("identity", "Who is Sisi Lola?"),
            ("culture", "What is your mission?"),
            ("innovation", "Tell me about African innovation."),
            ("diaspora", "Speak to Africans in the diaspora.")
        ]
    ]
    
    all_sentences = {}
    for source, text in transcripts.items():
        sentences = extract_sentences(clean_text(text))
        for sentence in sentences:
            categories = categorize_sentence(sentence)
            for cat in categories:
                if cat not in all_sentences:
                    all_sentences[cat] = []
                all_sentences[cat].append(sentence)
    
    for flow in conversation_flows:
        messages = [{"role": "System", "content": SISI_LOLA_SYSTEM_PROMPT}]
        
        for category, user_msg in flow:
            messages.append({"role": "User", "content": user_msg})
            
            # Get a response for this category
            if category in all_sentences and all_sentences[category]:
                response = random.choice(all_sentences[category])
            elif category == "identity":
                response = random.choice(IDENTITY_RESPONSES)
            else:
                response = "Africa sweet die! Let me share more about our beautiful culture and heritage."
            
            messages.append({"role": "Chatbot", "content": response})
        
        conversations.append({"messages": messages})
    
    return conversations


def main():
    print("=" * 70)
    print("SISI LOLA ENHANCED TRAINING DATA GENERATOR")
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load transcripts
    print("\n📂 Loading transcripts...")
    transcripts = load_transcripts()
    print(f"   Loaded {len(transcripts)} transcripts")
    
    # Generate enhanced Q&A pairs
    print("\n🔄 Generating enhanced Q&A pairs...")
    qa_pairs = create_enhanced_qa_pairs(transcripts)
    print(f"   Generated {len(qa_pairs)} instruction-response pairs")
    
    # Count by category
    categories = {}
    for pair in qa_pairs:
        cat = pair.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n📊 Pairs by category:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}")
    
    # Create different formats
    print("\n📝 Creating training formats...")
    
    # 1. Enhanced JSONL (instruction-response)
    enhanced_file = OUTPUT_DIR / "sisi_lola_enhanced_qa.jsonl"
    with open(enhanced_file, 'w', encoding='utf-8') as f:
        for pair in qa_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + '\n')
    print(f"   ✅ Enhanced Q&A: {enhanced_file.name} ({len(qa_pairs)} pairs)")
    
    # 2. Cohere chat format
    cohere_data = create_cohere_chat_format(qa_pairs)
    cohere_file = OUTPUT_DIR / "sisi_lola_cohere.jsonl"
    with open(cohere_file, 'w', encoding='utf-8') as f:
        for example in cohere_data:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print(f"   ✅ Cohere format: {cohere_file.name}")
    
    # 3. OpenAI format
    openai_data = create_openai_format(qa_pairs)
    openai_file = OUTPUT_DIR / "sisi_lola_openai.jsonl"
    with open(openai_file, 'w', encoding='utf-8') as f:
        for example in openai_data:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print(f"   ✅ OpenAI format: {openai_file.name}")
    
    # 4. Alpaca format
    alpaca_data = create_alpaca_format(qa_pairs)
    alpaca_file = OUTPUT_DIR / "sisi_lola_alpaca.json"
    with open(alpaca_file, 'w', encoding='utf-8') as f:
        json.dump(alpaca_data, f, indent=2, ensure_ascii=False)
    print(f"   ✅ Alpaca format: {alpaca_file.name}")
    
    # 5. Multi-turn conversations
    print("\n💬 Creating multi-turn conversations...")
    conversations = create_multi_turn_conversations(transcripts)
    conv_file = OUTPUT_DIR / "sisi_lola_multiturn.jsonl"
    with open(conv_file, 'w', encoding='utf-8') as f:
        for conv in conversations:
            f.write(json.dumps(conv, ensure_ascii=False) + '\n')
    print(f"   ✅ Multi-turn: {conv_file.name} ({len(conversations)} conversations)")
    
    # 6. Create combined file for Cohere (chat + multi-turn)
    combined_cohere = cohere_data + conversations
    combined_file = OUTPUT_DIR / "sisi_lola_cohere_full.jsonl"
    with open(combined_file, 'w', encoding='utf-8') as f:
        for example in combined_cohere:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    print(f"   ✅ Cohere full: {combined_file.name} ({len(combined_cohere)} examples)")
    
    # Save metadata
    metadata = {
        "generated": datetime.now().isoformat(),
        "source_transcripts": list(transcripts.keys()),
        "total_qa_pairs": len(qa_pairs),
        "categories": categories,
        "formats_generated": [
            "enhanced_qa.jsonl",
            "cohere.jsonl",
            "openai.jsonl",
            "alpaca.json",
            "multiturn.jsonl",
            "cohere_full.jsonl"
        ],
        "system_prompt_length": len(SISI_LOLA_SYSTEM_PROMPT),
        "nigerian_expressions": len(NIGERIAN_EXPRESSIONS)
    }
    
    meta_file = OUTPUT_DIR / "enhanced_training_metadata.json"
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 70)
    print("✅ ENHANCED TRAINING DATA GENERATION COMPLETE")
    print("=" * 70)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print(f"\n📊 Summary:")
    print(f"   • Total Q&A pairs: {len(qa_pairs)}")
    print(f"   • Categories: {len(categories)}")
    print(f"   • Multi-turn conversations: {len(conversations)}")
    print(f"   • Nigerian expressions: {len(NIGERIAN_EXPRESSIONS)}")
    print(f"\n🎯 Ready for fine-tuning with:")
    print(f"   • Cohere: sisi_lola_cohere_full.jsonl")
    print(f"   • OpenAI: sisi_lola_openai.jsonl")
    print(f"   • Open-source (Llama, Mistral): sisi_lola_alpaca.json")


if __name__ == "__main__":
    main()
