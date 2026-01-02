"""
SISI LOLA MULTILINGUAL SERVICE
==============================
Comprehensive language support for Nigerian languages and dialects.

Features:
- Hausa, Igbo, Yoruba, Pidgin English translation
- Multilingual TTS with authentic accents
- Pidgin speech-to-text
- Cultural context awareness
- Prayer/blessing generation in native languages
"""

import os
import re
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum


class NigerianLanguage(Enum):
    """Supported Nigerian languages"""
    ENGLISH = "english"
    PIDGIN = "pidgin"
    HAUSA = "hausa"
    IGBO = "igbo"
    YORUBA = "yoruba"


@dataclass
class LanguageConfig:
    """Configuration for a language"""
    name: str
    code: str
    xtts_language: str
    region: str
    speakers_millions: float
    greeting: str
    script: str = "latin"


LANGUAGE_REGISTRY: Dict[str, LanguageConfig] = {
    "english": LanguageConfig(
        name="English", code="en", xtts_language="en",
        region="Nationwide", speakers_millions=200.0,
        greeting="Hello, how are you?",
    ),
    "pidgin": LanguageConfig(
        name="Nigerian Pidgin", code="pcm", xtts_language="en",
        region="Nationwide", speakers_millions=100.0,
        greeting="How you dey? How body na?",
    ),
    "hausa": LanguageConfig(
        name="Hausa", code="ha", xtts_language="en",
        region="Northern Nigeria", speakers_millions=70.0,
        greeting="Ina kwana? Lafiya lau?",
    ),
    "igbo": LanguageConfig(
        name="Igbo", code="ig", xtts_language="en",
        region="Eastern Nigeria", speakers_millions=45.0,
        greeting="Kedu? I no mma?",
    ),
    "yoruba": LanguageConfig(
        name="Yoruba", code="yo", xtts_language="en",
        region="Western Nigeria", speakers_millions=50.0,
        greeting="Bawo ni? E kaaro?",
    ),
}

PIDGIN_DICTIONARY: Dict[str, str] = {
    "hello": "how you dey",
    "how are you": "how body",
    "good morning": "morning o",
    "good evening": "evening o",
    "yes": "na so",
    "no": "no be so",
    "please": "abeg",
    "thank you": "thank you o",
    "sorry": "sorry o",
    "what happened": "wetin happen",
    "where are you going": "where you dey go",
    "money": "moni",
    "expensive": "e dear",
    "delicious": "e sweet well well",
}

PRAYERS_BY_LANGUAGE: Dict[str, List[str]] = {
    "english": [
        "May the Lord bless you and keep you.",
        "May your path be filled with light and favor.",
    ],
    "pidgin": [
        "Make God bless you well well o, make your matter no dey give you wahala.",
        "Papa God go show you road wey go carry you go better place.",
        "E go dey alright for you, na God matter be dis.",
        "Make money follow you everywhere you go, amen!",
        "God go open door wey nobody fit close for you.",
    ],
    "hausa": [
        "Allah ya ba ka albarka, Allah ya kiyaye ka.",
        "Allah ya yi maka alheri.",
    ],
    "igbo": [
        "Ka Chukwu gozie gi, ka O chekwaba gi.",
        "Ka uzo gi nwee ihe na amara.",
    ],
    "yoruba": [
        "Je ki Oluwa bukun yin, ki o si pa yin mo.",
        "Je ki ona yin kun fun imole ati ojurere.",
    ],
}


class MultilingualService:
    """Comprehensive multilingual service for Nigerian languages"""
    
    def __init__(self):
        self.languages = LANGUAGE_REGISTRY
        self.pidgin_dict = PIDGIN_DICTIONARY
    
    def get_supported_languages(self) -> List[Dict[str, Any]]:
        """Get list of supported languages"""
        return [
            {
                "name": config.name,
                "code": config.code,
                "region": config.region,
                "speakers": f"{config.speakers_millions}M",
                "greeting": config.greeting,
            }
            for config in self.languages.values()
        ]
    
    def detect_language(self, text: str) -> Tuple[str, float]:
        """Detect the language of input text"""
        text_lower = text.lower()
        
        pidgin_markers = ["dey", "wetin", "wahala", "abeg", "oya", "sha", "shey", "no be", "na so", "make", "wey"]
        pidgin_score = sum(1 for marker in pidgin_markers if marker in text_lower)
        
        hausa_markers = ["ina", "lafiya", "sannu", "yaya", "wallahi"]
        hausa_score = sum(1 for marker in hausa_markers if marker in text_lower)
        
        igbo_markers = ["kedu", "ndewo", "biko", "nna"]
        igbo_score = sum(1 for marker in igbo_markers if marker in text_lower)
        
        yoruba_markers = ["bawo", "kilode", "se"]
        yoruba_score = sum(1 for marker in yoruba_markers if marker in text_lower)
        
        scores = {"pidgin": pidgin_score, "hausa": hausa_score, "igbo": igbo_score, "yoruba": yoruba_score}
        max_score = max(scores.values())
        
        if max_score > 0:
            detected = max(scores, key=scores.get)
            confidence = min(max_score / 3.0, 1.0)
            return detected, confidence
        
        return "english", 0.8
    
    def translate_to_pidgin(self, english_text: str) -> str:
        """Translate English text to Nigerian Pidgin"""
        pidgin_text = english_text
        
        transformations = [
            (r"\b(I am|I'm)\b", "I dey"),
            (r"\b(you are|you're)\b", "you dey"),
            (r"\b(he is|she is|it is)\b", "e dey"),
            (r"\bwhat is\b", "wetin be"),
            (r"\bhow are you\b", "how body"),
            (r"\byes\b", "na so"),
            (r"\bno\b", "no be so"),
            (r"\bvery\b", "well well"),
            (r"\bplease\b", "abeg"),
            (r"\bcan you\b", "you fit"),
            (r"\bdon't\b", "no"),
            (r"\bcan't\b", "no fit"),
        ]
        
        for pattern, replacement in transformations:
            pidgin_text = re.sub(pattern, replacement, pidgin_text, flags=re.IGNORECASE)
        
        return pidgin_text
    
    def translate_from_pidgin(self, pidgin_text: str) -> str:
        """Translate Nigerian Pidgin to Standard English"""
        english_text = pidgin_text
        
        transformations = [
            (r"\bI dey\b", "I am"),
            (r"\byou dey\b", "you are"),
            (r"\be dey\b", "it is"),
            (r"\bwetin be\b", "what is"),
            (r"\bhow body\b", "how are you"),
            (r"\bna so\b", "yes"),
            (r"\bno be so\b", "no"),
            (r"\bwell well\b", "very"),
            (r"\babeg\b", "please"),
            (r"\byou fit\b", "can you"),
            (r"\bno fit\b", "can't"),
            (r"\bwahala\b", "problem"),
        ]
        
        for pattern, replacement in transformations:
            english_text = re.sub(pattern, replacement, english_text, flags=re.IGNORECASE)
        
        english_text = re.sub(r"\s+(o|sha|sef)[.!?]?$", ".", english_text, flags=re.IGNORECASE)
        return english_text
    
    def get_greeting(self, language: str = "pidgin", time_of_day: str = "morning") -> str:
        """Get culturally appropriate greeting"""
        greetings = {
            "english": {"morning": "Good morning! How are you today?", "afternoon": "Good afternoon!", "evening": "Good evening!"},
            "pidgin": {"morning": "Ehen! Good morning o! How you dey this fine morning?", "afternoon": "Afternoon o! How work dey go?", "evening": "Evening o! Body don land for house abi?"},
            "hausa": {"morning": "Barka da safiya! Ina kwana?", "afternoon": "Barka da rana!", "evening": "Barka da yamma!"},
            "igbo": {"morning": "Ututu oma! Kedu ka I mere?", "afternoon": "Ehihie oma!", "evening": "Mgbede oma!"},
            "yoruba": {"morning": "E kaaro! Se daadaa ni?", "afternoon": "E kaasan!", "evening": "E kaale!"},
        }
        lang_greetings = greetings.get(language, greetings["english"])
        return lang_greetings.get(time_of_day, lang_greetings["morning"])
    
    def generate_prayer(self, language: str = "pidgin", context: str = "general") -> str:
        """Generate culturally appropriate prayer/blessing"""
        import random
        prayers = PRAYERS_BY_LANGUAGE.get(language, PRAYERS_BY_LANGUAGE["english"])
        selected = random.choice(prayers)
        
        if context == "business" and language == "pidgin":
            selected = f"For your business matter, {selected}"
        elif context == "travel" and language == "pidgin":
            selected = f"As you dey travel, {selected}"
        
        return selected
    
    def add_nigerian_flavor(self, text: str, intensity: float = 0.5) -> str:
        """Add Nigerian expressions and flavor to text"""
        import random
        
        exclamations = ["Ehen!", "Oya!", "Chai!", "Ehn ehn!", "Abeg!", "Na wa o!"]
        fillers = ["you understand?", "you hear me?", "na so e be", "I dey tell you"]
        
        result = text
        if random.random() < intensity * 0.5:
            result = f"{random.choice(exclamations)} {result}"
        if random.random() < intensity * 0.3:
            result = result.rstrip('.!?') + f", {random.choice(fillers)}."
        
        return result
    
    def format_currency(self, amount: float, currency: str = "NGN") -> str:
        """Format currency with Nigerian conventions"""
        if currency == "NGN":
            if amount >= 1_000_000_000:
                return f"N{amount/1_000_000_000:.1f} billion naira"
            elif amount >= 1_000_000:
                return f"N{amount/1_000_000:.1f} million naira"
            elif amount >= 1000:
                return f"N{amount/1000:.0f}k"
            else:
                return f"N{amount:,.0f}"
        elif currency == "USD":
            return f"${amount:,.2f}"
        return f"{amount:,.2f} {currency}"


_service: Optional[MultilingualService] = None

def get_multilingual_service() -> MultilingualService:
    """Get singleton multilingual service instance"""
    global _service
    if _service is None:
        _service = MultilingualService()
    return _service


if __name__ == "__main__":
    service = get_multilingual_service()
    print("SISI LOLA MULTILINGUAL SERVICE")
    print("=" * 40)
    
    tests = ["How you dey today?", "Good morning, how are you?"]
    for text in tests:
        lang, conf = service.detect_language(text)
        print(f"  '{text[:30]}...' -> {lang} ({conf:.0%})")
    
    for lang in ["pidgin", "hausa", "igbo", "yoruba"]:
        greeting = service.get_greeting(lang, "morning")
        print(f"  {lang.upper()}: {greeting}")
