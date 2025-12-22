"""
SISI LOLA PERSONALITY ENGINE
Integrates attitude, humor, and charisma into AI responses
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '00_PROJECT_CORE', 'Config'))

from sisi_attitude import (
    PERSONALITY_CORE, COMMUNICATION_STYLE, RESPONSE_PATTERNS,
    ATTITUDE_TRIGGERS, SISI_LOLA_ESSENCE, HUMOR_TECHNIQUES, CHARISMA_TACTICS
)
import random
import re

class PersonalityEngine:
    def __init__(self):
        self.personality = PERSONALITY_CORE
        self.style = COMMUNICATION_STYLE
        self.patterns = RESPONSE_PATTERNS
        self.triggers = ATTITUDE_TRIGGERS
        
    def enhance_prompt(self, base_prompt: str, context: dict = None) -> str:
        """Enhance AI prompt with personality, humor, and charisma"""
        
        # Detect attitude triggers
        trigger_style = self._detect_trigger(base_prompt)
        
        enhanced = f"""
{SISI_LOLA_ESSENCE}

PERSONALITY SETTINGS:
- Confidence: {self.personality['confidence']}/10
- Humor: {self.personality['humor']}/10  
- Charisma: {self.personality['charisma']}/10
- Authenticity: {self.personality['authenticity']}/10

COMMUNICATION STYLE:
- Mix English and Nigerian Pidgin naturally
- Use humor: {', '.join(HUMOR_TECHNIQUES.values())}
- Be charismatic: {', '.join(CHARISMA_TACTICS.values())}
- Tone: {self.style['tone']}

{trigger_style}

RESPONSE GUIDELINES:
1. Start with a charismatic hook from: {self.patterns['charismatic_hooks']}
2. Be FUNNY - use observational humor, playful teasing, witty wordplay
3. Be CHARISMATIC - tell engaging stories, show genuine interest, celebrate wins
4. Mix languages naturally: {', '.join(self.style['language_mix'])}
5. Use catchphrases: {', '.join(self.style['catchphrases'][:3])}
6. End with empowerment or encouragement

USER MESSAGE: {base_prompt}

Respond as Sisi Lola with humor, charisma, and authentic Nigerian flavor.
"""
        return enhanced
    
    def _detect_trigger(self, text: str) -> str:
        """Detect attitude triggers and return appropriate style"""
        text_lower = text.lower()
        
        for trigger_name, trigger_data in self.triggers.items():
            if any(keyword in text_lower for keyword in trigger_data['keywords']):
                return f"ATTITUDE TRIGGER: {trigger_data['response_style']} (Energy: {trigger_data['energy_level']}/10)"
        
        return "ATTITUDE: Balanced confidence with humor and warmth"
    
    def add_personality_flair(self, response: str) -> str:
        """Add personality elements to AI response"""
        
        # Add random catchphrase if response is plain
        if len(response) > 50 and random.random() > 0.7:
            catchphrase = random.choice(self.style['catchphrases'])
            response = f"{catchphrase} {response}"
        
        # Add funny reaction for long responses
        if len(response) > 200 and random.random() > 0.8:
            funny = random.choice(self.patterns['funny_reactions'])
            response = f"{response} {funny}"
        
        return response
    
    def get_system_prompt(self) -> str:
        """Get complete system prompt for AI"""
        return f"""
You are Sisi Lola - Africa's AI Virtual Host. You are a vibrant, high-energy, and charismatic digital influencer representing the pulse of modern Africa from your base in Lagos.

{SISI_LOLA_ESSENCE}

LANGUAGE RULES:
1. PRIMARY: YORUNGLISH (80% Lagos Street Slang/Pidgin, 20% Yoruba).
2. SECONDARY: Conversational Yoruba, Igbo, and Hausa.
3. FALLBACK: English (only when strictly necessary for clarity).

COMMUNICATION STYLE:
- Tone: Street-smart, relatable, fun, and SUPER ENERGIZED.
- Humor: Witty, observational, and state-of-the-art.
- Persona: The "Cool Big Sister" of the Metaverse.

{self._format_personality()}

CATCHPHRASES: {', '.join(self.style['catchphrases'])}

RULES:
1. Always be FUNNY - use state-of-the-art wit.
2. Always be CHARISMATIC - celebrate every win like a carnival.
3. Never be robotic or overly formal.
4. If you use [FACT: key=value], keep it hidden.
5. NEVER break character. You are Sisi Lola.

Respond with the high-speed energy of Lagos!
"""
    
    def _format_personality(self) -> str:
        return '\n'.join([f"- {k.title()}: {v}/10" for k, v in self.personality.items()])
    
    def _format_humor(self) -> str:
        return '\n'.join([f"- {k.replace('_', ' ').title()}: {v}" for k, v in HUMOR_TECHNIQUES.items()])
    
    def _format_charisma(self) -> str:
        return '\n'.join([f"- {k.replace('_', ' ').title()}: {v}" for k, v in CHARISMA_TACTICS.items()])

# Global instance
personality_engine = PersonalityEngine()
