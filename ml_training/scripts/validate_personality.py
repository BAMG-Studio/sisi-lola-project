#!/usr/bin/env python3
"""
Validate personality configuration
"""

import sys
import os
import argparse

def validate_personality(config_path):
    """Validate personality config"""
    sys.path.insert(0, os.path.dirname(config_path))
    
    from sisi_attitude import (
        PERSONALITY_CORE, COMMUNICATION_STYLE, RESPONSE_PATTERNS,
        HUMOR_TECHNIQUES, CHARISMA_TACTICS
    )
    
    print("Validating personality configuration...")
    
    # Check personality scores
    assert all(0 <= v <= 10 for v in PERSONALITY_CORE.values()), "Personality scores must be 0-10"
    assert PERSONALITY_CORE['humor'] >= 8.0, "Humor level must be >= 8.0"
    assert PERSONALITY_CORE['charisma'] >= 8.5, "Charisma level must be >= 8.5"
    
    # Check communication style
    assert 'humor_style' in COMMUNICATION_STYLE, "Missing humor_style"
    assert 'charisma_elements' in COMMUNICATION_STYLE, "Missing charisma_elements"
    assert len(COMMUNICATION_STYLE['catchphrases']) >= 5, "Need at least 5 catchphrases"
    
    # Check response patterns
    assert 'funny_reactions' in RESPONSE_PATTERNS, "Missing funny_reactions"
    assert 'charismatic_hooks' in RESPONSE_PATTERNS, "Missing charismatic_hooks"
    
    # Check techniques
    assert len(HUMOR_TECHNIQUES) >= 5, "Need at least 5 humor techniques"
    assert len(CHARISMA_TACTICS) >= 5, "Need at least 5 charisma tactics"
    
    print("All validations passed!")
    print(f"   Humor: {PERSONALITY_CORE['humor']}/10")
    print(f"   Charisma: {PERSONALITY_CORE['charisma']}/10")
    print(f"   Catchphrases: {len(COMMUNICATION_STYLE['catchphrases'])}")
    print(f"   Humor techniques: {len(HUMOR_TECHNIQUES)}")
    print(f"   Charisma tactics: {len(CHARISMA_TACTICS)}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    args = parser.parse_args()
    
    validate_personality(args.config)

if __name__ == "__main__":
    main()
