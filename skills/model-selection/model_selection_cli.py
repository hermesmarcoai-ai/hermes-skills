#!/usr/bin/env python3
"""
Hermes CLI Integration: Model Selection Commands

Integra comandi CLI per gestire la selezione modelli OpenRouter

Comandi disponibili:
- /model-select ANALYSIS — Analizza task e seleziona modello
- /model-list LIST — Lista modelli disponibili  
- /model-cost COST — Stima costo per task
- /model-set SET — Imposta modello manualmente
- /model-report REPORT — Genera report costi
"""

import sys
import json
import argparse
from pathlib import Path

# Add model selection engine to path
MODEL_SELECTION_PATH = Path(__file__).parent / "model_selection_engine.py"
if MODEL_SELECTION_PATH.exists():
    sys.path.insert(0, str(MODEL_SELECTION_PATH.parent.parent))
    from model_selection_engine import ModelSelectionEngine, TaskRequirements
else:
    print(f"Error: Model selection engine not found at {MODEL_SELECTION_PATH}")
    sys.exit(1)


class ModelSelectCommand:
    """CLI command for model selection analysis"""
    
    NAME = "model-select"
    ALIASES = ["ms", "model-select-analyze"]
    
    def __init__(self):
        self.engine = ModelSelectionEngine()
    
    def parse_args(self, args):
        """Parse command arguments"""
        parser = argparse.ArgumentParser(
            prog=f"/{self.NAME}",
            description="Analyze task and recommend optimal OpenRouter model"
        )
        parser.add_argument(
            "task",
            nargs="?",
            default="",
            help="Task description to analyze"
        )
        parser.add_argument(
            "--complexity",
            choices=["low", "medium", "high", "enterprise"],
            default="medium",
            help="Task complexity"
        )
        parser.add_argument(
            "--budget",
            choices=["max_savings", "balanced", "quality_first"],
            default="balanced",
            help="Budget priority"
        )
        parser.add_argument(
            "--domain",
            choices=["coding", "writing", "research", "general"],
            default="general",
            help="Domain specialization"
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output as JSON"
        )
        parser.add_argument(
            "--quick",
            action="store_true",
            help="Quick analysis without detailed breakdown"
        )
        
        return parser.parse_args(args) if args else parser.parse_args([])
    
    def execute(self, args):
        """Execute model selection analysis"""
        
        # Get task description
        task_description = args.task
        
        # If no task provided, show usage
        if not task_description:
            return self._show_help()
        
        # Create task requirements
        task = TaskRequirements(
            task_type='general',  # Will be auto-detected
            complexity=args.complexity,
            budget_priority=args.budget,
            domain=args.domain
        )
        
        # Generate recommendation
        result = self.engine.generate_recommendations(task)
        
        # Output
        if args.json:
            print(json.dumps(result, indent=2))
        elif args.quick:
            primary = result['primary_selection']
            print(f"🎯 Recommended: {primary['model']}")
            print(f"📊 Category: {primary['category']}")
            print(f"💰 Cost: ${primary['estimated_cost']:.6f}")
            print(f"⭐ Confidence: {primary['confidence']*100:.0f}%")
        else:
            return self._format_detailed(result)
    
    def _show_help(self):
        """Show command help"""
        help_text = """
🎯 /model-select — Analyze task and recommend optimal model

USAGE:
  /model-select "your task description" [options]

OPTIONS:
  --complexity  : low | medium | high | enterprise (default: medium)
  --budget      : max_savings | balanced | quality_first (default: balanced)
  --domain      : coding | writing | research | general (default: general)
  --json        : Output as JSON for programmatic use
  --quick       : Quick summary without detailed breakdown

EXAMPLES:
  /model-select "scrivi articolo blog"
  /model-select "debug code Python" --domain coding
  /model-select "analyze business strategy" --complexity high --json
  /model-select "chat with user" --budget max_savings --quick

AVAILABLE MODELS BY CATEGORY:
  Ultra Cheap (FREE/cheap):
    - liquid/lfm-2.5-1.2b-instruct:free (FREE, 200ms)
    - google/gemma-4-26b-a4b-it:free (FREE)
    - nvidia/nemotron-3-super-120b-a12b:free (FREE)
  
  Cheap ($0.05-0.12):
    - nemotron-3-nano-30b-a3b ($0.05)
    - qwen/qwen3.5-9b ($0.07)
    - mistralai/ministral-8b-2512 ($0.08)
  
  Balanced (Best Value):
    - qwen/qwen3.5-27b ($0.27) ⭐ RECOMMENDED
    - mistralai/mistral-large-2512 ($0.30)
    - anthropic/claude-sonnet-4.6 ($3.00)
  
  High Performance:
    - deepseek/deepseek-v3.2 ($0.55) ⭐ BEST VALUE
    - qwen/qwen3.5-397b-a17b ($2.50)
    - anthropic/claude-opus-4.6 ($15.00)
  
  Specialized (Coding):
    - qwen/qwen3-coder-next ($0.50) ⭐ CODING SPECIALIST
    - openai/gpt-5.3-codex ($3.00)

OUTPUT FORMAT:
  - Detailed breakdown with cost estimate
  - Confidence score (0.0-1.0)
  - Optimization score (0.0-1.0)
  - Fallback model suggestion
  - Cost comparison

💡 TIP: Start with balanced budget, then optimize to max_savings once confident!
"""
        return help_text
    
    def _format_detailed(self, result):
        """Format detailed output"""
        
        primary = result['primary_selection']
        cost = result['cost_estimate']
        fallback = result['fallback_selection']
        
        output = []
        output.append("=" * 70)
        output.append(f"🎯 MODEL SELECTION RECOMMENDATION")
        output.append("=" * 70)
        output.append(f"\n📝 Task Analysis:")
        output.append(f"   Type: {result['task_analysis']['task_type']}")
        output.append(f"   Complexity: {result['task_analysis']['complexity']}")
        output.append(f"   Budget: {result['task_analysis']['budget_priority']}")
        
        output.append(f"\n⭐ PRIMARY SELECTION:")
        output.append(f"   Model: {primary['model']}")
        output.append(f"   Name: {primary['name']}")
        output.append(f"   Category: {primary['category']}")
        output.append(f"   Confidence: {primary['confidence']*100:.0f}%")
        output.append(f"   Estimated Cost: ${primary['estimated_cost']:.6f}")
        output.append(f"   Latency: ~{primary['latency']}ms")
        
        output.append(f"\n💰 COST BREAKDOWN:")
        output.append(f"   Input Tokens: {cost['input_tokens']} (${cost['input_cost']:.6f})")
        output.append(f"   Output Tokens: {cost['output_tokens']} (${cost['output_cost']:.6f})")
        output.append(f"   Total: ${cost['total_cost']:.6f}")
        
        output.append(f"\n🔄 FALLBACK:")
        output.append(f"   If primary fails: {fallback['model']}")
        
        output.append(f"\n📊 OPTIMIZATION SCORE: {result['optimization_score']}/1.0")
        
        if result['recommendations']:
            output.append(f"\n💡 RECOMMENDATIONS:")
            for rec in result['recommendations']:
                icon = "✓" if rec['type'] == 'cost_savings' else "⚠" if rec['impact'] != 'critical' else "✗"
                output.append(f"   {icon} {rec['message']}")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)


class ModelListCommand:
    """CLI command for listing available models"""
    
    NAME = "model-list"
    ALIASES = ["ml", "models"]
    
    def __init__(self):
        self.engine = ModelSelectionEngine()
    
    def execute(self, args):
        """List models by category"""
        
        models = self.engine.models
        
        # Group by category
        categories = {}
        for model_id, info in models.items():
            cat = info.get('category', 'unknown')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((model_id, info))
        
        output = []
        output.append("=" * 70)
        output.append("📊 OPENROUTER MODELS AVAILABLE")
        output.append("=" * 70)
        
        # Print categories in order
        category_order = ['ultra_cheap', 'cheap', 'balanced', 'high_performance', 'specialized_coding']
        
        for cat_name in category_order:
            if cat_name in categories:
                output.append(f"\n{'='*10} {cat_name.upper().replace('_', ' ')} {'='*10}")
                
                for model_id, info in sorted(categories[cat_name], key=lambda x: x[1].get('prompt_cost', 0)):
                    cost = info.get('prompt_cost', 0)
                    latency = info.get('latency', 0)
                    reasoning = info.get('reasoning', 0)
                    
                    # Add indicators
                    indicators = []
                    if cost == 0:
                        indicators.append("FREE")
                    elif reasoning >= 5:
                        indicators.append("TOP RATING")
                    
                    indicator_str = f" [{', '.join(indicators)}]" if indicators else ""
                    
                    output.append(f"  • {model_id}")
                    output.append(f"    Name: {info.get('name', 'Unknown')}")
                    output.append(f"    Cost: ${cost:.2f}/1M | Latency: {latency}ms | Reasoning: {reasoning}/5{indicator_str}")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)


class ModelCostCommand:
    """CLI command for cost estimation"""
    
    NAME = "model-cost"
    ALIASES = ["mc", "cost"]
    
    def __init__(self):
        self.engine = ModelSelectionEngine()
    
    def execute(self, args):
        """Estimate cost for task"""
        
        parser = argparse.ArgumentParser(description="Estimate cost for task")
        parser.add_argument("task", nargs="?", help="Task description")
        parser.add_argument("--model", help="Specific model to use")
        parser.add_argument("--tokens", help="Estimated tokens (input/output)")
        
        parsed = parser.parse_args(args) if args else parser.parse_args([])
        
        if parsed.model:
            # Use specific model
            model_info = self.engine.models.get(parsed.model, {})
            cost_per_request = (model_info.get('prompt_cost', 0) + model_info.get('completion_cost', 0))
            
            output = f"""
💰 Cost Estimation for Model: {parsed.model}

Cost per 1M tokens:
  Input:  ${model_info.get('prompt_cost', 0):.2f}
  Output: ${model_info.get('completion_cost', 0):.2f}

Estimated cost per request (typical task):
  ~${cost_per_request:.6f}

💡 Tip: Typical task uses ~1-2K tokens
        """
            return output
        
        elif parsed.task:
            # Analyze task
            task = TaskRequirements(
                task_type='general',
                complexity='medium',
                budget_priority='balanced'
            )
            
            result = self.engine.generate_recommendations(task)
            primary = result['primary_selection']
            cost = result['cost_estimate']
            
            return f"""
💰 Cost Estimation for Task: "{parsed.task}"

Recommended Model: {primary['model']}
  Cost per request: ${cost['total_cost']:.6f}
  Tokens used: {cost['input_tokens'] + cost['output_tokens']}
  
For 100 requests: ~${cost['total_cost'] * 100:.2f}
For 1000 requests: ~${cost['total_cost'] * 1000:.2f}
            """
        
        else:
            return "Usage: /model-cost [task] or /model-cost --model <model_id>"


def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        print("Hermes Model Selection CLI")
        print("Usage: python model_selection_cli.py <command> [args]")
        print("\nCommands:")
        print("  model-select <task>  — Analyze task and recommend model")
        print("  model-list           — List available models")
        print("  model-cost           — Estimate cost for task")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    if command in ["model-select", "ms"]:
        cmd = ModelSelectCommand()
        result = cmd.execute(args)
        print(result)
        
    elif command in ["model-list", "ml", "models"]:
        cmd = ModelListCommand()
        result = cmd.execute(args)
        print(result)
        
    elif command in ["model-cost", "mc"]:
        cmd = ModelCostCommand()
        result = cmd.execute(args)
        print(result)
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
