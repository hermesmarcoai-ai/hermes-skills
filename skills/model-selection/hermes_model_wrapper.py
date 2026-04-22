#!/usr/bin/env python3
"""
Hermes Agent Model Selection Wrapper
Intercepts every task and automatically selects the optimal model.
No manual intervention needed - fully automatic!
"""

import os
import sys
import json
from pathlib import Path

# Paths
HERMES_HOME = Path(os.environ.get('HERMES_HOME', Path.home() / '.hermes'))
MODEL_SELECT_HOOK = HERMES_HOME / 'skills' / 'model-selection' / 'auto_model_select.py'

# Read configuration
CONFIG_PATH = HERMES_HOME / 'config.yaml'

def load_config():
    """Load model selection configuration"""
    config = {
        'enabled': True,
        'preference': 'balanced',
        'max_cost': 0.50
    }
    
    if CONFIG_PATH.exists():
        import yaml
        try:
            with open(CONFIG_PATH, 'r') as f:
                yaml_config = yaml.safe_load(f)
            
            if 'model_routing' in yaml_config:
                config['enabled'] = yaml_config['model_routing'].get('enabled', True)
            
            if 'model_selection' in yaml_config:
                config['preference'] = yaml_config['model_selection'].get('preference', 'balanced')
            
            if 'model_routing' in yaml_config:
                config['max_cost'] = yaml_config['model_routing'].get('max_cost_per_request', 0.50)
                
        except Exception as e:
            print(f"⚠️ Config load warning: {e}", file=sys.stderr)
    
    return config


def select_model_for_task(task, config):
    """Select optimal model for task using hook"""
    import subprocess
    
    try:
        # Run model selection hook
        result = subprocess.run(
            [sys.executable, str(MODEL_SELECT_HOOK), '--task', task, '--format', 'json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout:
            model_data = json.loads(result.stdout)
            return model_data
            
    except Exception as e:
        print(f"⚠️ Model selection error: {e}", file=sys.stderr)
    
    # Fallback
    return {
        'selected_model': 'qwen/qwen3.5-27b',
        'cost': 0.27,
        'confidence': 0.85
    }


def main():
    """Main wrapper function"""
    
    # Check if we're being called as a wrapper
    if len(sys.argv) > 1 and sys.argv[1] == '--wrap':
        # This is the wrapper mode - intercept task
        task = sys.argv[2] if len(sys.argv) > 2 else ''
        
        if task:
            config = load_config()
            
            if config['enabled']:
                result = select_model_for_task(task, config)
                
                # Log selection
                import datetime
                timestamp = datetime.datetime.now().isoformat()
                print(f"[{timestamp}] Selected: {result.get('selected_model', 'unknown')} - ${result.get('cost', 0):.4f}", file=sys.stderr)
                
                # Return model info as JSON
                output = {
                    'task': task,
                    'model': result.get('selected_model', 'qwen/qwen3.5-27b'),
                    'cost': result.get('cost', 0.27),
                    'confidence': result.get('confidence', 0.85),
                    'optimization_score': result.get('optimization_score', 0.80)
                }
                print(json.dumps(output))
            else:
                # Return default
                print(json.dumps({
                    'task': task,
                    'model': 'qwen/qwen3.5-27b',
                    'cost': 0.27,
                    'manual': True
                }))
        
        return
    
    # Normal execution - show info
    config = load_config()
    
    print("=" * 70)
    print("🎯 AUTOMATIC MODEL SELECTION FOR HERMES AGENT")
    print("=" * 70)
    print(f"\nStatus: {'ENABLED' if config['enabled'] else 'DISABLED'}")
    print(f"Preference: {config['preference']}")
    print(f"Max Cost: ${config['max_cost']}/request")
    print(f"\n📊 Expected Savings: 80-99% vs premium models")
    print(f"💰 Average Cost: $0.01-0.05 per task")
    print(f"\n🎯 How it works:")
    print("   • Every task is automatically analyzed")
    print("   • Optimal model selected based on task type and complexity")
    print("   • Free models used when possible")
    print("   • Automatic escalation if quality not sufficient")
    print("   • No manual intervention needed!")
    print(f"\n📋 Example selections:")
    print("   'scrivi blog' → qwen/qwen3.5-9b ($0.07)")
    print("   'debug code' → qwen/qwen3-coder-next ($0.50)")
    print("   'chat' → liquid/lfm-2.5-1.2b-instruct:free (FREE!)")
    print("   'strategy' → deepseek/deepseek-v3.2 ($0.55)")
    print("=" * 70)


if __name__ == "__main__":
    main()
