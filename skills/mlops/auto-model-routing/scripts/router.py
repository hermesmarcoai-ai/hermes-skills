#!/usr/bin/env python3
"""
Auto Model Router - Lightweight rules-based model selection.

Loads routing rules from references/rules.md and selects the best model
for a given task based on keyword matching.

Performance target: < 50ms per query
"""

import json
import re
import sys
import os
from pathlib import Path

# Default configuration (used if rules.md cannot be loaded)
DEFAULT_MODEL = "MiniMax-M2.7-highspeed"
DEFAULT_PROVIDER = "minimax"
FALLBACK_CONFIDENCE = 0.3

# Routing rules - loaded from references/rules.md or use defaults
ROUTING_RULES = {
    "reasoning/heavy": {
        "model": "claude-sonnet-4-20250514",
        "provider": "anthropic",
        "confidence": 0.85,
        "keywords": ["debug", "architect", "design", "analyze", "complex", "system"]
    },
    "fast/light": {
        "model": "MiniMax-M2.7-highspeed",
        "provider": "minimax",
        "confidence": 0.9,
        "keywords": ["quick", "simple", "one-liner", "small", "easy", "fix typo"]
    },
    "creative": {
        "model": "MiniMax-M2.7-highspeed",
        "provider": "minimax",
        "confidence": 0.8,
        "keywords": ["write", "story", "creative", "song", "poem", "narrative"]
    },
    "research": {
        "model": "deep-research-iterative",
        "provider": "perplexity",
        "confidence": 0.85,
        "keywords": ["research", "find", "investigate", "explore", "search"]
    },
    "coding": {
        "model": "claude-sonnet-4-20250514",
        "provider": "anthropic",
        "confidence": 0.85,
        "keywords": ["code", "implement", "refactor", "program", "build", "function"]
    }
}


def load_rules_from_file(rules_path: str = None) -> dict:
    """
    Load routing rules from references/rules.md.
    
    Args:
        rules_path: Optional path to rules file
        
    Returns:
        dict with routing rules
    """
    if rules_path is None:
        # Default path relative to this script
        script_dir = Path(__file__).parent
        rules_path = script_dir.parent / "references" / "rules.md"
    
    if not os.path.exists(rules_path):
        return ROUTING_RULES
    
    # For now, return default rules (markdown parsing can be added later)
    return ROUTING_RULES


def tokenize(text: str) -> list:
    """
    Convert task text into lowercase tokens.
    
    Args:
        text: Raw task description
        
    Returns:
        List of lowercase tokens
    """
    # Lowercase and extract words
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens


def score_category(category: dict, tokens: list) -> int:
    """
    Score how well a task matches a category.
    
    Args:
        category: Category dict with keywords
        tokens: Tokenized task words
        
    Returns:
        Match score (higher = better match)
    """
    keywords = category.get("keywords", [])
    score = 0
    
    for token in tokens:
        if token in keywords:
            score += 1
    
    return score


def route_task(task: str, rules: dict = None) -> dict:
    """
    Route a task to the best model based on keyword matching.
    
    Args:
        task: Task description text
        rules: Optional routing rules (uses defaults if None)
        
    Returns:
        dict with selected model, provider, confidence, and reason
    """
    if rules is None:
        rules = ROUTING_RULES
    
    tokens = tokenize(task)
    
    if not tokens:
        return {
            "selected": DEFAULT_MODEL,
            "provider": DEFAULT_PROVIDER,
            "confidence": FALLBACK_CONFIDENCE,
            "reason": "Empty task, using fallback model"
        }
    
    best_category = None
    best_score = 0
    best_confidence = FALLBACK_CONFIDENCE
    
    for category_name, category in rules.items():
        score = score_category(category, tokens)
        
        if score > best_score:
            best_score = score
            best_category = category_name
            best_confidence = category.get("confidence", 0.5)
    
    if best_category is None or best_score == 0:
        return {
            "selected": DEFAULT_MODEL,
            "provider": DEFAULT_PROVIDER,
            "confidence": FALLBACK_CONFIDENCE,
            "reason": "No matching keywords, using fallback model"
        }
    
    category = rules[best_category]
    matched_keywords = [k for k in category.get("keywords", []) if k in tokens]
    
    return {
        "selected": category["model"],
        "provider": category["provider"],
        "confidence": best_confidence,
        "reason": f"Matched category '{best_category}' via keyword(s): {', '.join(matched_keywords)}"
    }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: router.py <task_description>")
        print("Example: router.py 'debug my Python code'")
        sys.exit(1)
    
    task = " ".join(sys.argv[1:])
    result = route_task(task)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
