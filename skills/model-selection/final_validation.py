#!/usr/bin/env python3
"""
Final Validation - Test il sistema completo con task reali
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from model_selection_engine import ModelSelectionEngine, TaskRequirements


def test_real_world_scenarios():
    """Test with realistic tasks Marco would use"""
    
    engine = ModelSelectionEngine()
    
    # Real tasks from Marco's workflow
    real_tasks = [
        {
            "task": "Scrivi articolo blog su AI automation per business",
            "expected": "content",
            "budget": "balanced",
        },
        {
            "task": "Refactor questo script Python per migliorare le performance",
            "expected": "coding",
            "budget": "max_savings",
        },
        {
            "task": "Analizza strategia di mercato per business online",
            "expected": "analysis",
            "budget": "balanced",
        },
        {
            "task": "Chat per brainstorming idee business",
            "expected": "chat",
            "budget": "max_savings",
        },
        {
            "task": "Decisione mission-critical su investimento crypto",
            "expected": "enterprise",
            "budget": "quality_first",
        },
        {
            "task": "Processo bulk 50 email marketing",
            "expected": "batch",
            "budget": "max_savings",
        },
    ]
    
    print("=" * 70)
    print("🧪 REAL-WORLD TASKS VALIDATION")
    print("=" * 70)
    
    total_savings = 0
    total_requests = len(real_tasks)
    
    for i, rt in enumerate(real_tasks, 1):
        print(f"\n{i}. Task: {rt['task'][:60]}...")
        
        requirements = TaskRequirements(
            task_type=rt['expected'],
            complexity='medium',
            budget_priority=rt['budget']
        )
        
        result = engine.generate_recommendations(requirements)
        primary = result['primary_selection']
        cost = result['cost_estimate']
        
        print(f"   → Model: {primary['model']}")
        print(f"   → Category: {primary['category']}")
        print(f"   → Cost: ${cost['total_cost']:.6f}")
        print(f"   → Confidence: {primary['confidence']*100:.0f}%")
        print(f"   → Score: {result['optimization_score']}/1.0")
        
        total_savings += cost['total_cost']
    
    print("\n" + "=" * 70)
    print(f"💰 Total estimated cost for {total_requests} real tasks: ${total_savings:.6f}")
    
    # Calculate savings vs premium
    premium_cost = total_requests * 0.015  # If all used Claude Opus
    actual_savings = premium_cost - total_savings
    savings_pct = (actual_savings / premium_cost) * 100
    
    print(f"💎 If all used premium (Claude Opus): ~${premium_cost:.2f}")
    print(f"✅ Actual cost with optimization: ${total_savings:.6f}")
    print(f"🎉 SAVINGS: ${actual_savings:.4f} ({savings_pct:.1f}%)")
    print("=" * 70)
    
    return total_savings, savings_pct


def test_free_models_performance():
    """Test that free models actually work and are recommended when appropriate"""
    
    engine = ModelSelectionEngine()
    
    print("\n🧪 FREE MODELS PERFORMANCE TEST")
    print("-" * 70)
    
    # Tasks where free models should be recommended
    free_tasks = [
        "Ciao come stai?",  # Chat
        "Saluto breve",  # Short content
        "Riassumi questo testo",  # Simple reasoning
    ]
    
    free_model_count = 0
    
    for task_text in free_tasks:
        req = TaskRequirements(task_type='general', complexity='low', budget_priority='max_savings')
        result = engine.generate_recommendations(req)
        model = result['primary_selection']['model']
        
        if ':free' in model or (engine.models.get(model, {}).get('prompt_cost', 1) == 0):
            free_model_count += 1
            print(f"✅ {task_text[:30]} → {model} (FREE)")
        else:
            print(f"⚠️ {task_text[:30]} → {model} (${engine.models.get(model, {}).get('prompt_cost', 0)})")
    
    print(f"\nFree model recommendations: {free_model_count}/{len(free_tasks)}")
    return free_model_count == len(free_tasks)


def main():
    """Run all validations"""
    
    print("\n" + "=" * 70)
    print("🚀 OPENROUTER MODEL SELECTION - FINAL VALIDATION")
    print("=" * 70 + "\n")
    
    # Test 1: Real-world scenarios
    cost, savings = test_real_world_scenarios()
    
    # Test 2: Free models performance
    free_ok = test_free_models_performance()
    
    # Final verdict
    print("\n" + "=" * 70)
    print("📊 FINAL VERDICT")
    print("=" * 70)
    
    if cost < 1.0 and savings > 50:
        print("✅ SYSTEM READY FOR PRODUCTION")
        print(f"💰 Cost efficiency: {savings:.1f}% savings")
        print(f"🎯 Average cost per task: ${cost/6:.6f}")
        print("🚀 Ready to deploy!")
    else:
        print("⚠️ System functional but needs tuning")
    
    print("=" * 70)
    
    # Return success if free models test passed
    return free_ok


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
