#!/usr/bin/env python3
"""
AUTOMATIC MODEL SELECTION FOR HERMES
Seleziona il modello ottimale per ogni task e mostra il comando da usare.

Usage: python3 auto_use.py "il tuo task"
"""

import sys
import os
import json
from pathlib import Path
import subprocess

# Add model selection to path
MODEL_SELECTION_PATH = Path(__file__).parent / "auto_model_select.py"
if str(Path(__file__).parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent))

from model_selection_engine import ModelSelectionEngine, TaskRequirements


def select_model(task):
    """Select optimal model for task"""
    try:
        engine = ModelSelectionEngine()
        
        # Analyze task
        task_lower = task.lower()
        
        # Auto-detect complexity
        if any(w in task_lower for w in ['code', 'program', 'script', 'debug']):
            complexity = 'medium'
        elif any(w in task_lower for w in ['enterprise', 'mission', 'critical']):
            complexity = 'enterprise'
        elif any(w in task_lower for w in ['simple', 'quick', 'easy']):
            complexity = 'low'
        else:
            complexity = 'medium'
        
        # Create requirements
        requirements = TaskRequirements(
            task_type='general',
            complexity=complexity,
            budget_priority='balanced'
        )
        
        # Get selection
        result = engine.generate_recommendations(requirements)
        primary = result['primary_selection']
        cost = result['cost_estimate']
        
        return {
            'model': primary['model'],
            'name': primary['name'],
            'cost': cost['total_cost'],
            'confidence': primary['confidence'],
            'optimization_score': result['optimization_score']
        }
        
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return {'model': 'qwen/qwen3.5-27b', 'name': 'Fallback', 'cost': 0.27}


def main():
    """Main execution"""
    
    # Check if task provided
    if len(sys.argv) < 2:
        print("=" * 70)
        print("🎯 AUTOMATIC MODEL SELECTION FOR HERMES")
        print("=" * 70)
        print("\nUsage: python3 auto_use.py \"your task description\"")
        print("\nExample:")
        print('  python3 auto_use.py "scrivi articolo blog su AI"')
        print('\n  python3 auto_use.py "debug code Python"')
        print('\n  python3 auto_use.py "analizza strategia business"')
        print("\nThis will automatically select the optimal model for your task")
        print("and show you the exact command to use with Hermes.")
        print("=" * 70)
        return
    
    task = sys.argv[1]
    
    print("=" * 70)
    print("🔍 ANALYZING TASK...")
    print("=" * 70)
    print(f"\nYour task: {task}\n")
    
    # Select optimal model
    print("🤖 Selecting optimal model...")
    result = select_model(task)
    
    print("\n" + "=" * 70)
    print("✅ OPTIMAL MODEL SELECTED")
    print("=" * 70)
    print(f"\n🎯 Model: {result['model']}")
    print(f"📝 Name: {result['name']}")
    print(f"💰 Cost: ${result['cost']:.6f} per request")
    print(f"⭐ Confidence: {result['confidence']*100:.0f}%")
    print(f"📊 Optimization Score: {result['optimization_score']}/1.0")
    
    print("\n" + "=" * 70)
    print("🚀 USE THIS COMMAND WITH HERMES:")
    print("=" * 70)
    print(f"\n  hermes --model {result['model']} \"{task}\"\n")
    
    print("=" * 70)
    print("💡 TIP: Want to use this model automatically next time?")
    print("=" * 70)
    print("\n  Set it temporarily:")
    print(f"  MODEL={result['model']} hermes \"{task}\"")
    print("\n  Or set permanently:")
    print(f"  hermes model-set {result['model']}")
    print("=" * 70)
    
    # Save to file for easy reuse
    with open(str(Path.home() / '.hermes' / 'current_model.txt'), 'w') as f:
        f.write(result['model'])
    
    print(f"\n💾 Model saved to ~/.hermes/current_model.txt")


if __name__ == "__main__":
    main()
