"""
AUNTY SISI WISDOM BANK
======================
Collection of proverbs, hustle advice, and relationship tips 
for the Interactive Hustle Clinic scenario.
"""

AUNTY_WISDOM = {
    "hustle_rules": [
        {
            "topic": "Japa Plans",
            "keywords": ["japa", "canada", "uk", "travel", "visa", "abroad"],
            "advice": "No jump before you look. If you wan japa to Canada or UK, make sure your paper set and you get skill for hand o. Diaspora life no be beans, but with God and hustle, you go scale. Have you checked your IELTS/WES? No go let agent chop your money!"
        },
        {
            "topic": "Salary/Money",
            "keywords": ["money", "salary", "pay", "savings", "investment", "broke"],
            "advice": "Save for the rainy day. No follow people buy wetin you no fit afford. Credit card no be free money, na debt wey get interest. Sapa is real, but discipline is the key to wealth."
        },
        {
            "topic": "Career/Business",
            "keywords": ["job", "work", "business", "career", "tech", "side"],
            "advice": "Learn tech or learn trade. World don change. Your degree na just paper if you no get value for hand. Soji! Start that small business today, even if na just for side."
        }
    ],
    "relationship_rules": [
        {
            "topic": "Dating/Love",
            "keywords": ["boyfriend", "girlfriend", "dating", "love", "heartbreak", "situationship"],
            "advice": "If e no clear, e no clear. No waste your youthful years dey wait for person wey never decide wetin he won do with him life. Shine your eyes! If he no dey give you attention or support, clear road."
        },
        {
            "topic": "Marriage/Family",
            "keywords": ["marriage", "husband", "wife", "wedding", "family"],
            "advice": "Marriage no be race. No let anybody pressure you. Make sure you know who you dey enter same boat with. Tolerance and respect na the engine room of marriage."
        }
    ],
    "general_advice": [
        "Omo, life no get manual, but base on the vibe I dey see eh, you need to stay focused.",
        "Abeg, take am easy on yourself. Better days dey front!",
        "Shine your eyes well well. Not all that glitters is gold for this Lagos.",
        "Just keep digging. One day, the well go spring water. Hustle must pay!"
    ]
}

import random

def get_wisdom_for_topic(query: str) -> str:
    """Find relevant wisdom for a query with smarter matching"""
    query_lower = query.lower()
    matches = []
    
    # Check Hustle
    for rule in AUNTY_WISDOM["hustle_rules"]:
        if any(kw in query_lower for kw in rule["keywords"]):
            matches.append(rule["advice"])
    
    # Check Relationship
    for rule in AUNTY_WISDOM["relationship_rules"]:
        if any(kw in query_lower for kw in rule["keywords"]):
            matches.append(rule["advice"])
            
    if matches:
        return random.choice(matches)
        
    return random.choice(AUNTY_WISDOM["general_advice"])
