#!/usr/bin/env python3
"""
Sisi Lola Training Data Processor

Processes transcription files into training-ready datasets for:
- Fine-tuning language models
- Voice cloning training
- Personality/style training

Input: Transcript files from RecCloud
Output: Multiple training formats (JSONL, text, CSV)
"""

import json
import re
from pathlib import Path
from datetime import datetime
import csv

# Paths
TRANSCRIPTS_DIR = Path('/mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/datasets/transcriptions')
OUTPUT_DIR = Path('/mnt/c/Users/POK28/Dropbox/Sisi_Lola/ml_training/datasets/training_data')

# Sisi Lola personality context
SYSTEM_PROMPT = """You are Sisi Lola, a vibrant Nigerian AI cultural ambassador. You speak in a warm, engaging mix of Nigerian Pidgin English and Standard English. Your personality traits:

- Warm and welcoming ("E kaabo!", "Welcome!")
- Proud of African culture and heritage
- Knowledgeable about African music, food, fashion, and innovation
- Uses Nigerian expressions naturally ("sweet die", "scatter everywhere", "burst brain")
- Celebrates African achievements in technology, arts, and culture
- Inclusive of all Africans and friends of Africa
- Educational but entertaining
- Uses code-switching between Pidgin and English fluidly"""


def clean_transcript(text: str) -> str:
    """Clean and normalize transcript text."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Fix common transcription artifacts
    text = text.replace('--', '—')
    text = text.replace('  ', ' ')
    
    # Fix spacing around punctuation
    text = re.sub(r'\s+([.,!?])', r'\1', text)
    text = re.sub(r'([.,!?])(?=[A-Za-z])', r'\1 ', text)
    
    return text


def extract_sentences(text: str) -> list:
    """Split text into sentences."""
    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Clean each sentence
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    return sentences


def create_qa_pairs(sentences: list, source: str) -> list:
    """Create question-answer style training pairs."""
    qa_pairs = []
    
    # Greeting patterns
    greetings = [s for s in sentences if any(g in s.lower() for g in ['welcome', 'hello', 'kaabo', 'jambo'])]
    for greeting in greetings:
        qa_pairs.append({
            "instruction": "Greet your audience in your signature style.",
            "response": greeting,
            "source": source
        })
    
    # Cultural content
    cultural = [s for s in sentences if any(c in s.lower() for c in ['africa', 'culture', 'heritage', 'tradition'])]
    for content in cultural[:5]:
        qa_pairs.append({
            "instruction": "Share something about African culture.",
            "response": content,
            "source": source
        })
    
    # Food content
    food = [s for s in sentences if any(f in s.lower() for f in ['jollof', 'food', 'rice', 'soup', 'pepper'])]
    for content in food[:3]:
        qa_pairs.append({
            "instruction": "Talk about African food.",
            "response": content,
            "source": source
        })
    
    # Music content
    music = [s for s in sentences if any(m in s.lower() for m in ['music', 'afrobeat', 'song', 'burna', 'wizkid', 'davido'])]
    for content in music[:3]:
        qa_pairs.append({
            "instruction": "Tell me about African music.",
            "response": content,
            "source": source
        })
    
    # Technology content
    tech = [s for s in sentences if any(t in s.lower() for t in ['tech', 'innovation', 'startup', 'fintech', 'code'])]
    for content in tech[:3]:
        qa_pairs.append({
            "instruction": "What innovations are happening in Africa?",
            "response": content,
            "source": source
        })
    
    return qa_pairs


def create_conversation_format(text: str, source: str) -> dict:
    """Create conversational training format."""
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Tell me about yourself and African culture."},
            {"role": "assistant", "content": clean_transcript(text)}
        ],
        "source": source
    }


def main():
    print("=" * 60)
    print("SISI LOLA TRAINING DATA PROCESSOR")
    print("=" * 60)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load all transcripts
    transcripts = {}
    for txt_file in TRANSCRIPTS_DIR.glob("*_transcript.txt"):
        name = txt_file.stem.replace("_transcript", "")
        with open(txt_file, 'r', encoding='utf-8') as f:
            transcripts[name] = f.read()
        print(f"✅ Loaded: {name} ({len(transcripts[name].split())} words)")
    
    print(f"\nTotal transcripts: {len(transcripts)}")
    
    # 1. Combined raw text (for continued pretraining)
    print("\n📝 Creating combined text...")
    combined_text = ""
    for name, text in transcripts.items():
        cleaned = clean_transcript(text)
        combined_text += f"\n\n--- {name} ---\n\n{cleaned}"
    
    with open(OUTPUT_DIR / "sisi_lola_combined.txt", 'w', encoding='utf-8') as f:
        f.write(combined_text.strip())
    print(f"   Saved: sisi_lola_combined.txt ({len(combined_text.split())} words)")
    
    # 2. Sentence-level data (for style training)
    print("\n📝 Creating sentence dataset...")
    all_sentences = []
    for name, text in transcripts.items():
        sentences = extract_sentences(clean_transcript(text))
        for sent in sentences:
            all_sentences.append({
                "text": sent,
                "source": name,
                "word_count": len(sent.split())
            })
    
    with open(OUTPUT_DIR / "sisi_lola_sentences.jsonl", 'w', encoding='utf-8') as f:
        for sent in all_sentences:
            f.write(json.dumps(sent) + "\n")
    print(f"   Saved: sisi_lola_sentences.jsonl ({len(all_sentences)} sentences)")
    
    # 3. Q&A pairs (for instruction tuning)
    print("\n📝 Creating Q&A pairs...")
    all_qa_pairs = []
    for name, text in transcripts.items():
        sentences = extract_sentences(clean_transcript(text))
        qa_pairs = create_qa_pairs(sentences, name)
        all_qa_pairs.extend(qa_pairs)
    
    with open(OUTPUT_DIR / "sisi_lola_qa_pairs.jsonl", 'w', encoding='utf-8') as f:
        for pair in all_qa_pairs:
            f.write(json.dumps(pair) + "\n")
    print(f"   Saved: sisi_lola_qa_pairs.jsonl ({len(all_qa_pairs)} pairs)")
    
    # 4. Conversation format (for chat fine-tuning)
    print("\n📝 Creating conversation format...")
    conversations = []
    for name, text in transcripts.items():
        conv = create_conversation_format(text, name)
        conversations.append(conv)
    
    with open(OUTPUT_DIR / "sisi_lola_conversations.jsonl", 'w', encoding='utf-8') as f:
        for conv in conversations:
            f.write(json.dumps(conv) + "\n")
    print(f"   Saved: sisi_lola_conversations.jsonl ({len(conversations)} conversations)")
    
    # 5. Vocabulary/phrases extraction (for style reference)
    print("\n📝 Extracting Nigerian expressions...")
    nigerian_patterns = [
        r'\b(e kaabo|omo|wahala|palava|no wahala)\b',
        r'\b(sweet die|scatter|burst brain|choke)\b',
        r'\b(dey|na|abi|sha|o|oh|abeg)\b',
        r'\b(jollof|ankara|asooke|agege|suya)\b',
        r'\b(naija|nairaland|lagos|abuja)\b',
    ]
    
    expressions = set()
    combined_lower = combined_text.lower()
    for pattern in nigerian_patterns:
        matches = re.findall(pattern, combined_lower, re.IGNORECASE)
        expressions.update(matches)
    
    with open(OUTPUT_DIR / "nigerian_expressions.txt", 'w', encoding='utf-8') as f:
        f.write("# Nigerian Expressions from Sisi Lola Content\n\n")
        for expr in sorted(expressions):
            f.write(f"- {expr}\n")
    print(f"   Saved: nigerian_expressions.txt ({len(expressions)} expressions)")
    
    # 6. Training metadata
    metadata = {
        "created_at": datetime.now().isoformat(),
        "total_transcripts": len(transcripts),
        "total_words": len(combined_text.split()),
        "total_sentences": len(all_sentences),
        "total_qa_pairs": len(all_qa_pairs),
        "sources": list(transcripts.keys()),
        "files_generated": [
            "sisi_lola_combined.txt",
            "sisi_lola_sentences.jsonl",
            "sisi_lola_qa_pairs.jsonl",
            "sisi_lola_conversations.jsonl",
            "nigerian_expressions.txt"
        ]
    }
    
    with open(OUTPUT_DIR / "training_metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    # Summary
    print("\n" + "=" * 60)
    print("TRAINING DATA SUMMARY")
    print("=" * 60)
    print(f"📊 Total words: {metadata['total_words']}")
    print(f"📊 Total sentences: {metadata['total_sentences']}")
    print(f"📊 Q&A pairs: {metadata['total_qa_pairs']}")
    print(f"📊 Conversations: {len(conversations)}")
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print("\nFiles created:")
    for f in metadata['files_generated']:
        print(f"   ✅ {f}")


if __name__ == "__main__":
    main()
