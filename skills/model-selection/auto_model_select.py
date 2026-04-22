#!/usr/bin/env python3
"""
Automatic Model Selection Hook for Hermes Agent
Analyses every task and selects the optimal model automatically.
No user intervention needed - fully automatic!
"""

import sys
import os
import json
from pathlib import Path

# Add model selection to path
MODEL_SELECTION_PATH = Path(__file__).parent
if str(MODEL_SELECTION_PATH) not in sys.path:
    sys.path.insert(0, str(MODEL_SELECTION_PATH))

from model_selection_engine import ModelSelectionEngine, TaskRequirements

# Configuration
CONFIG_PATH = Path(__file__).parent.parent.parent / "config.yaml"
LOG_PATH = Path(__file__).parent.parent.parent / "logs" / "model_selection.log"

# Ensure log directory exists
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def log_message(message, level="INFO"):
    """Log to file and optionally to console"""
    timestamp = os.popen("date '+%Y-%m-%d %H:%M:%S'").read().strip()
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    # Write to log file
    try:
        with open(LOG_PATH, 'a') as f:
            f.write(log_entry)
    except Exception:
        pass
    
    # Optionally print for debugging
    if os.environ.get('DEBUG_MODEL_SELECTION', '').lower() == 'true':
        print(f"🎯 MODEL_SELECT: {message}")


def get_config():
    """Load model selection configuration"""
    config = {
        'enabled': True,
        'preference': 'balanced',
        'max_cost': 0.50,
        'auto_escalate': True
    }
    
    # Try to load from config.yaml
    if CONFIG_PATH.exists():
        import yaml
        try:
            with open(CONFIG_PATH, 'r') as f:
                yaml_config = yaml.safe_load(f)
                
            if 'model_routing' in yaml_config:
                config['enabled'] = yaml_config['model_routing'].get('enabled', True)
            
            if 'model_selection' in yaml_config:
                config['preference'] = yaml_config['model_selection'].get('preference', 'balanced')
                config['auto_escalate'] = yaml_config['model_selection'].get('escalation_enabled', True)
                
            if 'model_routing' in yaml_config:
                config['max_cost'] = yaml_config['model_routing'].get('max_cost_per_request', 0.50)
                
        except Exception as e:
            log_message(f"Error loading config: {e}", "ERROR")
    
    return config


def analyze_task(task):
    """
    Analyze task and extract characteristics
    Returns: dict with task_type, complexity, domain
    """
    task_lower = task.lower()
    
    # Detect task type
    task_type = 'general'
    if any(word in task_lower for word in ['code', 'program', 'script', 'dev', 'debug', 'refactor', 'build', 'test']):
        task_type = 'coding'
    elif any(word in task_lower for word in ['blog', 'article', 'post', 'write', 'content', 'copy', 'email', 'message']):
        task_type = 'content'
    elif any(word in task_lower for word in ['reason', 'analyze', 'strategy', 'decision', 'evaluate', 'compare']):
        task_type = 'reasoning'
    elif any(word in task_lower for word in ['chat', 'conversation', 'talk', 'discuss', 'casual', 'greeting']):
        task_type = 'chat'
    elif any(word in task_lower for word in ['batch', 'bulk', 'process', 'multiple', 'list', 'many']):
        task_type = 'batch'
    elif any(word in task_lower for word in ['enterprise', 'mission', 'critical', 'important']):
        task_type = 'enterprise'
    elif any(word in task_lower for word in ['legal', 'medical', 'financial', 'contract']):
        task_type = 'critical'
    
    # Detect complexity
    complexity = 'medium'
    if any(word in task_lower for word in ['simple', 'basic', 'quick', 'easy', 'short', 'brief']):
        complexity = 'low'
    elif any(word in task_lower for word in ['complex', 'advanced', 'sophisticated', 'detailed', 'intricate']):
        complexity = 'high'
    elif any(word in task_lower for word in ['enterprise', 'mission', 'critical', 'legal', 'medical']):
        complexity = 'enterprise'
    
    # Detect domain
    domain = 'general'
    if task_type in ['coding', 'dev']:
        domain = 'coding'
    elif task_type in ['content', 'writing', 'blog', 'email']:
        domain = 'writing'
    elif task_type in ['reasoning', 'research', 'analysis']:
        domain = 'research'
    
    # Detect budget preference from task text
    budget = 'balanced'
    if any(word in task_lower for word in ['cheap', 'free', 'economical', 'minimal', 'lowest cost']):
        budget = 'max_savings'
    elif any(word in task_lower for word in ['best', 'premium', 'top', 'maximum', 'highest quality']):
        budget = 'quality_first'
    
    return {
        'task_type': task_type,
        'complexity': complexity,
        'domain': domain,
        'budget': budget,
        'is_critical': task_type == 'critical' or complexity == 'enterprise'
    }


def select_optimal_model(task, config):
    """
    Select optimal model for task using model selection engine.
    Returns: dict with model info
    """
    if not config['enabled']:
        # Return default if disabled
        return {
            'model': 'qwen/qwen3.5-27b',  # Default balanced
            'cost': 0.27,
            'confidence': 0.85,
            'manual': True
        }
    
    # Analyze task
    analysis = analyze_task(task)
    
    log_message(f"Analyzing task: '{task[:50]}...' -> {analysis['task_type']}/{analysis['complexity']}")
    
    # Create task requirements
    requirements = TaskRequirements(
        task_type=analysis['task_type'],
        complexity=analysis['complexity'],
        budget_priority=analysis['budget'],
        domain=analysis['domain']
    )
    
    # Use model selection engine
    try:
        engine = ModelSelectionEngine()
        result = engine.generate_recommendations(requirements)
        
        primary = result['primary_selection']
        cost_estimate = result['cost_estimate']
        
        # Log selection
        log_message(f"Selected: {primary['model']} - ${cost_estimate['total_cost']:.6f} (confidence: {primary['confidence']*100:.0f}%)")
        
        return {
            'model': primary['model'],
            'name': primary['name'],
            'category': primary['category'],
            'cost': cost_estimate['total_cost'],
            'confidence': primary['confidence'],
            'optimization_score': result['optimization_score'],
            'task_type': analysis['task_type'],
            'complexity': analysis['complexity'],
            'budget': analysis['budget'],
            'fallback': result['fallback_selection']['model'],
            'manual': False
        }
        
    except Exception as e:
        log_message(f"Model selection failed: {e}, using fallback", "WARNING")
        
        # Fallback to safe default
        return {
            'model': 'qwen/qwen3.5-27b',
            'name': 'Qwen 3.5 27B',
            'category': 'balanced',
            'cost': 0.27,
            'confidence': 0.70,
            'optimization_score': 0.70,
            'task_type': 'general',
            'complexity': 'medium',
            'budget': 'balanced',
            'fallback': 'qwen/qwen3.5-9b',
            'manual': False
        }


def should_escalate(model_info, config):
    """
    Determine if we should escalate to a more expensive model.
    """
    if not config['auto_escalate']:
        return False
    
    # Check confidence
    if model_info['confidence'] < 0.70:
        return True
    
    # Check if task is critical
    if model_info.get('task_type') == 'critical' or model_info.get('complexity') == 'enterprise':
        if model_info['category'] in ['ultra_cheap', 'cheap']:
            return True
    
    return False


def format_output(model_info, format_type='text'):
    """Format model selection result"""
    if format_type == 'json':
        return json.dumps({
            'model': model_info['model'],
            'name': model_info['name'],
            'cost': model_info['cost'],
            'confidence': model_info['confidence'],
            'optimization_score': model_info['optimization_score'],
            'fallback': model_info['fallback']
        })
    elif format_type == 'model_only':
        return model_info['model']
    else:
        # Text format
        lines = [
            "🎯 Model Selection Result",
            "=" * 50,
            f"Selected: {model_info['model']}",
            f"Name: {model_info['name']}",
            f"Category: {model_info['category']}",
            f"Cost: ${model_info['cost']:.6f}",
            f"Confidence: {model_info['confidence']*100:.0f}%",
            f"Optimization Score: {model_info['optimization_score']}/1.0",
            "=" * 50,
        ]
        return "\n".join(lines)


# Main execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Automatic Model Selection Hook')
    parser.add_argument('--task', '-t', help='Task to analyze')
    parser.add_argument('--config', '-c', action='store_true', help='Show configuration')
    parser.add_argument('--test', action='store_true', help='Run test')
    parser.add_argument('--format', '-f', choices=['text', 'json', 'model'], default='text',
                       help='Output format')
    
    args = parser.parse_args()
    
    # Load configuration
    config = get_config()
    
    if args.config:
        print(f"Model Selection: {'ENABLED' if config['enabled'] else 'DISABLED'}")
        print(f"Preference: {config['preference']}")
        print(f"Max Cost: ${config['max_cost']}/request")
        print(f"Auto Escalate: {config['auto_escalate']}")
        sys.exit(0)
    
    if args.test:
        # Run tests with sample tasks
        test_tasks = [
            "scrivi articolo blog",
            "debug code Python",
            "chat user",
            "analyze business strategy",
            "refactor function"
        ]
        
        print("=" * 70)
        print("🧪 AUTOMATIC MODEL SELECTION - TEST MODE")
        print("=" * 70)
        
        total_cost = 0
        
        for task in test_tasks:
            result = select_optimal_model(task, config)
            total_cost += result['cost']
            
            print(f"\nTask: {task}")
            print(f"  → {result['model']}")
            print(f"  → Cost: ${result['cost']:.6f}")
            print(f"  → Confidence: {result['confidence']*100:.0f}%")
        
        print(f"\n{'='*70}")
        print(f"Average cost per task: ${total_cost/len(test_tasks):.6f}")
        print(f"Test complete!")
        sys.exit(0)
    
    if args.task:
        # Process single task
        result = select_optimal_model(args.task, config)
        
        # Check if escalation needed
        if should_escalate(result, config):
            log_message("Escalation recommended due to confidence or critical task", "INFO")
        
        # Output result
        if args.format == 'json':
            print(format_output(result, 'json'))
        elif args.format == 'model':
            print(result['model'])
        else:
            print(format_output(result, 'text'))
    
    else:
        # Hook mode - wait for input
        print("🎯 Automatic Model Selection Hook Active")
        print("Waiting for task input...")
        print("Send task to stdout and receive optimal model selection")
        
        # For API integration, wait for JSON input
        try:
            import json
            while True:
                line = sys.stdin.readline().strip()
                if not line:
                    break
                
                try:
                    input_data = json.loads(line)
                    task = input_data.get('task', '')
                    
                    if task:
                        result = select_optimal_model(task, config)
                        
                        output = {
                            'task': task,
                            'selected_model': result['model'],
                            'cost': result['cost'],
                            'confidence': result['confidence'],
                            'optimization_score': result['optimization_score'],
                            'fallback_model': result['fallback']
                        }
                        
                        print(json.dumps(output))
                        sys.stdout.flush()
                except json.JSONDecodeError:
                    # Try plain text task
                    result = select_optimal_model(line, config)
                    print(json.dumps({
                        'task': line,
                        'selected_model': result['model'],
                        'cost': result['cost']
                    }))
                    sys.stdout.flush()
        except KeyboardInterrupt:
            print("\nHook stopped")
            sys.exit(0)
