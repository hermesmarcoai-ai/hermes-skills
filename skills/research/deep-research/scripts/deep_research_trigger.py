#!/usr/bin/env python3
"""
Deep Research Trigger Detector

Checks if user input should trigger deep research mode.
"""

import os
import re
from typing import Tuple, Optional

# Deep research model configuration
DEEP_RESEARCH_MODEL = "perplexity/sonar-deep-research"
DEEP_RESEARCH_PROVIDER = "openrouter"
DEEP_RESEARCH_BASE_URL = "https://openrouter.ai/api/v1"
DEEP_RESEARCH_TIMEOUT = "60"

# Standard model (fallback)
STANDARD_MODEL = "perplexity/sonar-pro"
STANDARD_TIMEOUT = "30"

# Trigger phrases for deep research (case insensitive)
DEEP_RESEARCH_TRIGGERS = [
    r"\bdeep\s+research\b",
    r"\bsonar-deep-research\b",
    r"\bdo\s+deep\s+research\b",
    r"\bperform\s+deep\s+research\b",
    r"\bdeep\s+research\s+(on|about|into)\b",
]


def should_use_deep_research(user_input: str) -> bool:
    """
    Detect if user is requesting deep research mode.
    
    Args:
        user_input: The user's message/query
        
    Returns:
        True if deep research mode should be activated
    """
    if not user_input:
        return False
    
    user_lower = user_input.lower()
    
    for trigger in DEEP_RESEARCH_TRIGGERS:
        if re.search(trigger, user_lower):
            return True
    
    return False


def get_triggered_phrase(user_input: str) -> Optional[str]:
    """Return the matched trigger phrase for logging."""
    if not user_input:
        return None
    
    user_lower = user_input.lower()
    
    for trigger in DEEP_RESEARCH_TRIGGERS:
        match = re.search(trigger, user_lower)
        if match:
            return match.group(0)
    
    return None


def activate_deep_research_mode() -> Tuple[bool, dict]:
    """
    Activate deep research mode by setting environment variables.
    
    Returns:
        Tuple of (success, previous_values dict for restoration)
    """
    import os
    
    # Store current values for restoration
    previous_values = {
        "AUXILIARY_WEB_EXTRACT_MODEL": os.environ.get("AUXILIARY_WEB_EXTRACT_MODEL", ""),
        "AUXILIARY_WEB_EXTRACT_PROVIDER": os.environ.get("AUXILIARY_WEB_EXTRACT_PROVIDER", ""),
        "AUXILIARY_WEB_EXTRACT_BASE_URL": os.environ.get("AUXILIARY_WEB_EXTRACT_BASE_URL", ""),
        "AUXILIARY_WEB_EXTRACT_TIMEOUT": os.environ.get("AUXILIARY_WEB_EXTRACT_TIMEOUT", ""),
    }
    
    # Set deep research values
    os.environ["AUXILIARY_WEB_EXTRACT_MODEL"] = DEEP_RESEARCH_MODEL
    os.environ["AUXILIARY_WEB_EXTRACT_PROVIDER"] = DEEP_RESEARCH_PROVIDER
    os.environ["AUXILIARY_WEB_EXTRACT_BASE_URL"] = DEEP_RESEARCH_BASE_URL
    os.environ["AUXILIARY_WEB_EXTRACT_TIMEOUT"] = DEEP_RESEARCH_TIMEOUT
    
    return True, previous_values


def restore_standard_mode(previous_values: dict) -> bool:
    """
    Restore standard web extract model settings.
    
    Args:
        previous_values: Dict with previous environment variable values
        
    Returns:
        True if successful
    """
    import os
    
    for key, value in previous_values.items():
        if value:  # Only restore if there was a previous value
            os.environ[key] = value
        else:
            # Remove if wasn't set before
            os.environ.pop(key, None)
    
    return True


def get_current_web_extract_model() -> str:
    """Get the currently configured web extract model."""
    return os.environ.get("AUXILIARY_WEB_EXTRACT_MODEL", "perplexity/sonar-pro")


def is_deep_research_active() -> bool:
    """Check if deep research mode is currently active."""
    current = get_current_web_extract_model()
    return DEEP_RESEARCH_MODEL in current


# Example usage
if __name__ == "__main__":
    # Test examples
    test_phrases = [
        "Find information about Python",
        "Do deep research on quantum computing",
        "Search for AI papers",
        "I need deep research into climate change",
        "Perform deep research on crypto markets",
    ]
    
    for phrase in test_phrases:
        triggered = should_use_deep_research(phrase)
        trigger_word = get_triggered_phrase(phrase) if triggered else None
        print(f"'{phrase[:50]}...' -> Deep Research: {triggered} {f'(matched: {trigger_word})' if trigger_word else ''}")
