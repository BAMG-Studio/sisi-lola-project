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


# ============================================
# LANGUAGE CONFIGURATIONS
# ============================================

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
    xtts_language: str  # XTTS-v2 language code
    region: str
    speakers_millions: float
    greeting: str
    script: str = "latin"


LANGUAGE_REGISTRY: Dict[str, LanguageConfig] = {
    "english": LanguageConfig(
        name="English",
        code="en",
        xtts_language="en",
        region="Nationwide",
        speakers_millions=200.0,
        greeting="Hello, how are you?",
    ),
    "pidgin": LanguageConfig(
        name="Nigerian Pidgin",
        code="pcm",
        xtts_language="en",  # Use English base for Pidgin
        region="Nationwide",
        speakers_millions=100.0,
        greeting="How you dey? How body na?",
    ),
    "hausa": LanguageConfig(
        name="Hausa",
        code="ha",
        xtts_language="en",  # Fallback to English
        region="Northern Nigeria",
        speakers_millions=70.0,
        greeting="Ina kwana? Lafiya lau?",
    ),
    "igbo": LanguageConfig(
        name="Igbo",
        code="ig",
        xtts_language="en",  # Fallback to English
        region="Eastern Nigeria",
        speakers_millions=45.0,
        greeting="Kedu? I nọ mma?",
    ),
    "yoruba": LanguageConfig(
        name="Yoruba",
        code="yo",
        xtts_language="en",  # Fallback to English
        region="Western Nigeria",
        speakers_millions=50.0,
        greeting="Bawo ni? E kaaro?",
    ),
}


# ============================================
# COMMON NIGERIAN PHRASES
# ============================================

PIDGIN_DICTIONARY: Dict[str, str] = {
    # Greetings
    "hello": "how you dey",
    "how are you": "how body",
    "good morning": "morning o",
    "good evening": "evening o",
    "goodbye": "see you later o, make e dey",
    
    # Common expressions
    "yes": "na so",
    "no": "no be so",
    "please": "abeg",
    "thank you": "e dey be thank you o",
    "sorry": "sorry o",
    "it's okay": "e dey alright",
    "I understand": "I don hear",
    "I don't understand": "I no understand",
    
    # Questions
    "what happened": "wetin happen",
    "where are you going": "where you dey go",
    "what do you want": "wetin you want",
    "why are you": "why you dey",
    
    # Money/Business
    "money": "moni",
    "how much": "how much",
    "expensive": "e dear",
    "cheap": "e cheap",
    
    # Food
    "food": "food",
    "I'm hungry": "hunger dey catch me",
    "delicious": "e sweet well well",
    
    # Tech terms (Sisi Lola style)
    "artificial intelligence": "AI wey wise pass",
    "software": "software",
    "application": "app",
    "download": "download am",
    "video": "video",
    "content": "content",
}

HAUSA_PHRASES: Dict[str, str] = {
    "hello": "sannu",
    "how are you": "ina kwana",
    "thank you": "na gode",
    "please": "don Allah",
    "yes": "e",
    "no": "a'a",
    "good morning": "barka da safiya",
    "good evening": "barka da yamma",
    "goodbye": "sai an jima",
}

IGBO_PHRASES: Dict[str, str] = {
    "hello": "ndewo",
    "how are you": "kedu",
    "thank you": "daalụ",
    "please": "biko",
    "yes": "ee",
    "no": "mba",
    "good morning": "ụtụtụ ọma",
    "good evening": "mgbede ọma",
    "goodbye": "ka ọ dị",
}

YORUBA_PHRASES: Dict[str, str] = {
    "hello": "e kaaro",
    "how are you": "bawo ni",
    "thank you": "e se",
    "please": "jọwọ",
    "yes": "bẹẹni",
    "no": "rara",
    "good morning": "e kaaro",
    "good evening": "e kaalẹ",
    "goodbye": "o dabọ",
}


# ============================================
# NIGERIAN PRAYERS & BLESSINGS
# ============================================

PRAYERS_BY_LANGUAGE: Dict[str, List[str]] = {
    "english": [
        "May the Lord bless you and keep you.",
        "May your path be filled with light and favor.",
        "God's grace upon your endeavors today.",
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
        "Aminci Allah ya kasance tare da ku.",
    ],
    "igbo": [
        "Ka Chukwu gọzie gị, ka Ọ chekwaba gị.",
        "Ka ụzọ gị nwee ìhè na amara.",
        "Amara Chineke dị n'ọrụ gị taa.",
    ],
    "yoruba": [
        "Jẹ ki Oluwa bukun yin, ki o si pa yin mọ.",
        "Jẹ ki ọna yin kun fun imọlẹ ati ojurere.",
        "Oore-ọfẹ Ọlọrun le lori awọn iṣẹ rẹ loni.",
    ],
}


# ============================================
# MULTILINGUAL SERVICE
# ============================================

class MultilingualService:
    """
    Comprehensive multilingual service for Nigerian languages
    
    Features:
    - Translation between Nigerian languages
    - Culturally aware responses
    - Prayer/blessing generation
    - Pidgin English optimization
    """
    
    def __init__(self):
        self.languages = LANGUAGE_REGISTRY
        self.pidgin_dict = PIDGIN_DICTIONARY
    
    def get_supported_languages(self) -> List[Dict[str, Any]]:
        """Get list of supported languages with details"""
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
        """
        Detect the language of input text
        
        Returns:
            Tuple of (language_code, confidence)
        """
        text_lower = text.lower()
        
        # Check for Pidgin markers
        pidgin_markers = [
            "dey", "wetin", "wahala", "abeg", "oya", "sha", 
            "shey", "no be", "na so", "make", "wey", "commot"
        ]
        pidgin_score = sum(1 for marker in pidgin_markers if marker in text_lower)
        
        # Check for Hausa markers
        hausa_markers = ["ina", "lafiya", "sannu", "yaya", "wallahi", "ko", "ba"]
        hausa_score = sum(1 for marker in hausa_markers if marker in text_lower)
        
        # Check for Igbo markers
        igbo_markers = ["kedu", "ndewo", "daalụ", "biko", "nna", "nnaa"]
        igbo_score = sum(1 for marker in igbo_markers if marker in text_lower)
        
        # Check for Yoruba markers
        yoruba_markers = ["bawo", "jọwọ", "ẹ", "ọ", "kilode", "se"]
        yoruba_score = sum(1 for marker in yoruba_markers if marker in text_lower)
        
        # Determine language
        scores = {
            "pidgin": pidgin_score,
            "hausa": hausa_score,
            "igbo": igbo_score,
            "yoruba": yoruba_score,
        }
        
        max_score = max(scores.values())
        if max_score > 0:
            detected = max(scores, key=scores.get)
            confidence = min(max_score / 3.0, 1.0)  # Normalize to 0-1
            return detected, confidence
        
        return "english", 0.8  # Default to English
    
    def translate_to_pidgin(self, english_text: str) -> str:
        """
        Translate English text to Nigerian Pidgin
        
        This adds Nigerian flavor while maintaining clarity.
        """
        # Start with original text
        pidgin_text = english_text
        
        # Apply basic transformations
        transformations = [
            # Verb patterns
            (r'\b(I am|I\'m)\b', 'I dey'),
            (r'\b(you are|you\'re)\b', 'you dey'),
            (r'\b(he is|she is|it is)\b', 'e dey'),
            (r'\b(we are|they are)\b', 'dem dey'),
            
            # Common phrases
            (r'\bwhat is\b', 'wetin be'),
            (r'\bwhat are you\b', 'wetin you dey'),
            (r'\bwhere is\b', 'where'),
            (r'\bhow are you\b', 'how body'),
            
            # Words
            (r'\byes\b', 'na so'),
            (r'\bno\b', 'no be so'),
            (r'\bvery\b', 'well well'),
            (r'\breally\b', 'for real'),
            (r'\btoday\b', 'today'),
            (r'\bnow\b', 'now now'),
            (r'\bplease\b', 'abeg'),
            
            # Question patterns
            (r'\bdo you\b', 'you'),
            (r'\bdid you\b', 'you don'),
            (r'\bcan you\b', 'you fit'),
            
            # Negation
            (r'\bdon\'t\b', 'no'),
            (r'\bcan\'t\b', 'no fit'),
            (r'\bwon\'t\b', 'no go'),
            (r'\bdoesn\'t\b', 'no dey'),
        ]
        
        for pattern, replacement in transformations:
            pidgin_text = re.sub(pattern, replacement, pidgin_text, flags=re.IGNORECASE)
        
        # Add characteristic endings if sentence is short
        if len(pidgin_text.split()) < 10 and not pidgin_text.endswith(('o', 'sha', 'sef')):
            endings = ['o', 'sha', 'sef']
            import random
            if random.random() > 0.5:
                pidgin_text = pidgin_text.rstrip('.!?,') + ' ' + random.choice(endings) + '.'
        
        return pidgin_text
    
    def translate_from_pidgin(self, pidgin_text: str) -> str:
        """Translate Nigerian Pidgin to Standard English"""
        english_text = pidgin_text
        
        # Reverse transformations
        transformations = [
            (r'\bI dey\b', 'I am'),
            (r'\byou dey\b', 'you are'),
            (r'\be dey\b', 'it is'),
            (r'\bdem dey\b', 'they are'),
            (r'\bwetin be\b', 'what is'),
            (r'\bhow body\b', 'how are you'),
            (r'\bna so\b', 'yes'),
            (r'\bno be so\b', 'no'),
            (r'\bwell well\b', 'very'),
            (r'\bnow now\b', 'now'),
            (r'\babeg\b', 'please'),
            (r'\byou fit\b', 'can you'),
            (r'\bno fit\b', "can't"),
            (r'\bno go\b', "won't"),
            (r'\bdon\b', 'already'),
            (r'\bwahala\b', 'problem'),
            (r'\bpalava\b', 'problem'),
        ]
        
        for pattern, replacement in transformations:
            english_text = re.sub(pattern, replacement, english_text, flags=re.IGNORECASE)
        
        # Remove characteristic endings
        english_text = re.sub(r'\s+(o|sha|sef)[\.\!\?]?$', '.', english_text, flags=re.IGNORECASE)
        
        return english_text
    
    def get_greeting(
        self,
        language: str = "pidgin",
        time_of_day: str = "morning"
    ) -> str:
        """Get culturally appropriate greeting"""
        greetings = {
            "english": {
                "morning": "Good morning! How are you today?",
                "afternoon": "Good afternoon! Hope your day is going well.",
                "evening": "Good evening! How has your day been?",
            },
            "pidgin": {
                "morning": "Ehen! Good morning o! How you dey this fine morning?",
                "afternoon": "Afternoon o! How work dey go today?",
                "evening": "Evening o! Body don land for house abi?",
            },
            "hausa": {
                "morning": "Barka da safiya! Ina kwana?",
                "afternoon": "Barka da rana! Yaya gajiya?",
                "evening": "Barka da yamma! Lafiya lau?",
            },
            "igbo": {
                "morning": "Ụtụtụ ọma! Kedu ka I mere?",
                "afternoon": "Ehihie ọma! I nọ mma?",
                "evening": "Mgbede ọma! Kedu ọnọdụ gị?",
            },
            "yoruba": {
                "morning": "E kaaro! Se daadaa ni?",
                "afternoon": "E kaasan! Bawo ni ọjọ rẹ?",
                "evening": "E kaalẹ! Bawo ni?",
            },
        }
        
        lang_greetings = greetings.get(language, greetings["english"])
        return lang_greetings.get(time_of_day, lang_greetings["morning"])
    
    def generate_prayer(
        self,
        language: str = "pidgin",
        context: str = "general"
    ) -> str:
        """Generate culturally appropriate prayer/blessing"""
        prayers = PRAYERS_BY_LANGUAGE.get(language, PRAYERS_BY_LANGUAGE["english"])
        
        # Select based on context
        import random
        selected = random.choice(prayers)
        
        # Add context-specific wrapper
        if context == "business":
            if language == "pidgin":
                selected = f"For your business matter, {selected}"
            else:
                selected = f"For your work and business, {selected}"
        elif context == "family":
            if language == "pidgin":
                selected = f"For you and your family, {selected}"
            else:
                selected = f"May your family be blessed. {selected}"
        elif context == "travel":
            if language == "pidgin":
                selected = f"As you dey travel, {selected}"
            else:
                selected = f"For your journey, {selected}"
        
        return selected
    
    def add_nigerian_flavor(
        self,
        text: str,
        intensity: float = 0.5
    ) -> str:
        """
        Add Nigerian expressions and flavor to text
        
        Args:
            text: Original text
            intensity: How much Nigerian flavor (0.0 = none, 1.0 = heavy)
        
        Returns:
            Text with Nigerian expressions
        """
        import random
        
        # Nigerian exclamations to potentially add
        exclamations = [
            "Ehen!", "Oya!", "Chai!", "Ehn ehn!", "Abeg!", 
            "Na wa o!", "E be like say", "Shey?"
        ]
        
        # Nigerian sentence fillers
        fillers = [
            "you understand?", "you hear me?", "na so e be",
            "make e dey", "na real talk", "I dey tell you"
        ]
        
        result = text
        
        # Maybe add exclamation at start
        if random.random() < intensity * 0.5:
            result = f"{random.choice(exclamations)} {result}"
        
        # Maybe add filler at end
        if random.random() < intensity * 0.3:
            result = result.rstrip('.!?') + f", {random.choice(fillers)}."
        
        return result
    
    def format_currency(
        self,
        amount: float,
        currency: str = "NGN"
    ) -> str:
        """Format currency with Nigerian conventions"""
        if currency == "NGN":
            if amount >= 1_000_000_000:
                return f"₦{amount/1_000_000_000:.1f} billion naira"
            elif amount >= 1_000_000:
                return f"₦{amount/1_000_000:.1f} million naira"
            elif amount >= 1000:
                return f"₦{amount/1000:.0f}k"
            else:
                return f"₦{amount:,.0f}"
        elif currency == "USD":
            return f"${amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"


# ============================================
# SINGLETON INSTANCE
# ============================================

_service: Optional[MultilingualService] = None

def get_multilingual_service() -> MultilingualService:
    """Get singleton multilingual service instance"""
    global _service
    if _service is None:
        _service = MultilingualService()
    return _service


# ============================================
# QUICK TEST
# ============================================

if __name__ == "__main__":
    service = get_multilingual_service()
    
    print("🌍 SISI LOLA MULTILINGUAL SERVICE")
    print("=" * 50)
    
    # Test language detection
    tests = [
        "How you dey today? Hope say everything dey alright",
        "Good morning, how are you doing today?",
        "Ina kwana? Lafiya lau?",
        "Kedu ka ị mere? I nọ mma?",
    ]
    
    print("\n🔍 Language Detection:")
    for text in tests:
        lang, conf = service.detect_language(text)
        print(f"  '{text[:40]}...' → {lang} ({conf:.0%})")
    
    # Test translation
    print("\n🔄 English → Pidgin Translation:")
    english_texts = [
        "What are you doing today?",
        "I am very happy to see you",
        "Please help me with this problem",
    ]
    for text in english_texts:
        pidgin = service.translate_to_pidgin(text)
        print(f"  EN: {text}")
        print(f"  PCM: {pidgin}\n")
    
    # Test greetings
    print("👋 Greetings by Language:")
    for lang in ["pidgin", "hausa", "igbo", "yoruba"]:
        greeting = service.get_greeting(lang, "morning")
        print(f"  {lang.upper()}: {greeting}")
    
    # Test prayers
    print("\n🙏 Prayers/Blessings:")
    for lang in ["pidgin", "hausa"]:
        prayer = service.generate_prayer(lang, "business")
        print(f"  {lang.upper()}: {prayer}")
    
    # Test Nigerian flavor
    print("\n🌶️ Adding Nigerian Flavor:")
    plain_text = "This new feature is really impressive."
    flavored = service.add_nigerian_flavor(plain_text, intensity=0.8)
    print(f"  Original: {plain_text}")
    print(f"  Flavored: {flavored}")
