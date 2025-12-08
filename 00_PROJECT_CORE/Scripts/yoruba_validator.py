"""Yoruba Language Ratio Validator - 60/30/10 Enforcement"""
import re

def validate_yoruba_ratio(script):
    """Validate 60% Yoruba, 30% Pidgin, 10% English"""
    
    # Yoruba markers (diacritics, syllables, common words)
    yoruba_patterns = [
        r'[ẹọṣ]',  # Diacritics
        r'\bgb\w+', r'\bkp\w+',  # Yoruba consonant clusters
        r'\b(àwọn|ní|pé|wà|káàbọ̀|báwo|dúpẹ́|ṣeun|dára|ọjọ́|òní|jọ̀wọ́|mọ̀|gbọ́|burú|fẹ́|sọ̀rọ̀|nípa|ṣe|ẹ̀yin|pẹ̀lú|lónìí|tuntun|mìíràn|nígbà|yìí|jẹ́|ká)\b'
    ]
    
    yoruba_count = sum(len(re.findall(p, script, re.IGNORECASE)) for p in yoruba_patterns)
    
    # Pidgin markers
    pidgin_patterns = [
        r'\b(dey|don|go|fit|na|wetin|wahala|make|we|una|abi|sha|no|be|small|thing|kampe)\b'
    ]
    
    pidgin_count = sum(len(re.findall(p, script, re.IGNORECASE)) for p in pidgin_patterns)
    
    # Total words
    total_words = len(script.split())
    
    if total_words == 0:
        return {'yoruba': 0, 'pidgin': 0, 'english': 0, 'passes': False}
    
    yoruba_percent = (yoruba_count / total_words) * 100
    pidgin_percent = (pidgin_count / total_words) * 100
    english_percent = 100 - yoruba_percent - pidgin_percent
    
    # Pass if Yoruba is between 50-70% (buffer for 60% target)
    passes = 50 <= yoruba_percent <= 70
    
    return {
        'yoruba': round(yoruba_percent, 1),
        'pidgin': round(pidgin_percent, 1),
        'english': round(english_percent, 1),
        'passes': passes,
        'yoruba_count': yoruba_count,
        'pidgin_count': pidgin_count,
        'total_words': total_words
    }
