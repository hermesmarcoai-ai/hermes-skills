#!/usr/bin/env python3
"""
OpenRouter Model Selection Engine
Intelligent model routing based on task complexity, budget, and requirements

Usage:
    python model_selection_engine.py --task "write blog post" --complexity medium
    python model_selection_engine.py --task "debug Python code" --complexity high --coding
"""

import json
import math
from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple


@dataclass
class TaskRequirements:
    """Task requirements profile"""
    task_type: str
    complexity: str  # low, medium, high, enterprise
    budget_priority: str  # max_savings, balanced, quality_first
    requirements: Dict[str, Any] = None
    domain: Optional[str] = None  # e.g., "coding", "writing", "research"
    context_length_needed: Optional[int] = None
    
    def __post_init__(self):
        if self.requirements is None:
            self.requirements = {}


class ModelSelectionEngine:
    """
    Intelligent model selection based on:
    1. Task type and complexity
    2. Budget constraints
    3. Performance requirements
    4. Latency tolerance
    """
    
    def __init__(self):
        # Load model database
        self.models = self._load_model_database()
        
        # Task-to-model mappings
        self.task_mappings = self._build_task_mappings()
        
        # Decision thresholds
        self.thresholds = {
            'complexity_scores': {
                'low': 1,
                'medium': 2,
                'high': 3,
                'enterprise': 4
            },
            'cost_tolerance': {
                'max_savings': 0.10,  # Can tolerate 10% quality drop for cost
                'balanced': 0.25,
                'quality_first': 0.50
            }
        }
    
    def _load_model_database(self) -> Dict[str, Dict]:
        """Load model database (simplified version)"""
        return {
            # Ultra Cheap (Free)
            'liquid/lfm-2.5-1.2b-instruct:free': {
                'name': 'Liquid LFM 1.2B',
                'category': 'ultra_cheap',
                'prompt_cost': 0,
                'completion_cost': 0,
                'context': 131072,
                'latency': 200,
                'reasoning': 3,  # 1-5 scale
                'coding': 2,
                'writing': 3,
                'best_for': ['chat', 'quick_tasks', 'drafts']
            },
            
            'google/gemma-4-26b-a4b-it:free': {
                'name': 'Gemma 4 26B',
                'category': 'ultra_cheap',
                'prompt_cost': 0,
                'completion_cost': 0,
                'context': 131072,
                'latency': 600,
                'reasoning': 4,
                'coding': 3,
                'writing': 4,
                'best_for': ['general', 'analysis', 'writing']
            },
            
            'nvidia/nemotron-3-super-120b-a12b:free': {
                'name': 'Nemotron 120B',
                'category': 'ultra_cheap',
                'prompt_cost': 0,
                'completion_cost': 0,
                'context': 128000,
                'latency': 700,
                'reasoning': 5,
                'coding': 4,
                'writing': 5,
                'best_for': ['reasoning', 'analysis', 'complex_tasks']
            },
            
            # Cheap
            'qwen/qwen3.5-9b': {
                'name': 'Qwen 3.5 9B',
                'category': 'cheap',
                'prompt_cost': 0.07,
                'completion_cost': 0.07,
                'context': 128000,
                'latency': 250,
                'reasoning': 3,
                'coding': 4,
                'writing': 4,
                'best_for': ['daily_tasks', 'content', 'chat']
            },
            
            'mistralai/ministral-8b-2512': {
                'name': 'Mistral Ministral 8B',
                'category': 'cheap',
                'prompt_cost': 0.08,
                'completion_cost': 0.08,
                'context': 131072,
                'latency': 280,
                'reasoning': 3,
                'coding': 3,
                'writing': 4,
                'best_for': ['low_cost', 'batch', 'auto_responses']
            },
            
            # Balanced
            'qwen/qwen3.5-27b': {
                'name': 'Qwen 3.5 27B',
                'category': 'balanced',
                'prompt_cost': 0.27,
                'completion_cost': 0.27,
                'context': 128000,
                'latency': 450,
                'reasoning': 4,
                'coding': 4,
                'writing': 4,
                'best_for': ['business', 'analysis', 'conversations']
            },
            
            'mistralai/mistral-large-2512': {
                'name': 'Mistral Large',
                'category': 'balanced',
                'prompt_cost': 0.30,
                'completion_cost': 0.30,
                'context': 131072,
                'latency': 500,
                'reasoning': 4,
                'coding': 4,
                'writing': 5,
                'best_for': ['strategy', 'complex_reasoning', 'business']
            },
            
            'anthropic/claude-sonnet-4.6': {
                'name': 'Claude Sonnet 4.6',
                'category': 'balanced',
                'prompt_cost': 3.00,
                'completion_cost': 15.00,
                'context': 200000,
                'latency': 800,
                'reasoning': 5,
                'coding': 5,
                'writing': 5,
                'best_for': ['professional_writing', 'content_creation', 'business_comm']
            },
            
            # High Performance
            'qwen/qwen3.5-397b-a17b': {
                'name': 'Qwen 397B',
                'category': 'high_performance',
                'prompt_cost': 2.50,
                'completion_cost': 2.50,
                'context': 256000,
                'latency': 1200,
                'reasoning': 5,
                'coding': 5,
                'writing': 5,
                'best_for': ['enterprise', 'research', 'complex_dev']
            },
            
            'openai/gpt-5.4-pro': {
                'name': 'GPT-5.4 Pro',
                'category': 'high_performance',
                'prompt_cost': 5.00,
                'completion_cost': 20.00,
                'context': 200000,
                'latency': 1100,
                'reasoning': 5,
                'coding': 5,
                'writing': 5,
                'best_for': ['mission_critical', 'enterprise', 'research']
            },
            
            'deepseek/deepseek-v3.2': {
                'name': 'DeepSeek V3.2',
                'category': 'high_performance',
                'prompt_cost': 0.55,
                'completion_cost': 0.55,
                'context': 256000,
                'latency': 700,
                'reasoning': 4,
                'coding': 5,
                'writing': 4,
                'best_for': ['complex_low_cost', 'coding', 'analysis']
            },
            
            'anthropic/claude-opus-4.6': {
                'name': 'Claude Opus 4.6',
                'category': 'high_performance',
                'prompt_cost': 15.00,
                'completion_cost': 75.00,
                'context': 200000,
                'latency': 1500,
                'reasoning': 5,
                'coding': 5,
                'writing': 5,
                'best_for': ['mission_critical', 'research', 'legal_medical']
            },
            
            # Specialized Coding
            'qwen/qwen3-coder-next': {
                'name': 'Qwen Coder Next',
                'category': 'specialized_coding',
                'prompt_cost': 0.50,
                'completion_cost': 0.50,
                'context': 256000,
                'latency': 650,
                'reasoning': 4,
                'coding': 5,
                'writing': 3,
                'best_for': ['full_stack', 'code_gen', 'refactoring', 'debugging']
            },
            
            'openai/gpt-5.3-codex': {
                'name': 'GPT-5.3 Codex',
                'category': 'specialized_coding',
                'prompt_cost': 3.00,
                'completion_cost': 12.00,
                'context': 128000,
                'latency': 800,
                'reasoning': 5,
                'coding': 5,
                'writing': 4,
                'best_for': ['enterprise_dev', 'legacy_code', 'system_arch']
            },
        }
    
    def _build_task_mappings(self) -> Dict[str, Dict[str, Tuple[str, float, float]]]:
        """Build task-to-model mappings with confidence scores and costs"""
        return {
            'content_short': {
                'max_savings': ('liquid/lfm-2.5-1.2b-instruct:free', 0.95, 0),
                'balanced': ('qwen/qwen3.5-9b', 0.90, 0.0007),
                'quality_first': ('qwen/qwen3.5-27b', 0.85, 0.0074)
            },
            
            'content_long_form': {
                'max_savings': ('google/gemma-4-26b-a4b-it:free', 0.90, 0),
                'balanced': ('qwen/qwen3.5-27b', 0.95, 0.0035),
                'quality_first': ('anthropic/claude-sonnet-4.6', 0.98, 0.03)
            },
            
            'coding': {
                'max_savings': ('qwen/qwen3-coder-next', 0.95, 0.00005),
                'balanced': ('deepseek/deepseek-v3.2', 0.92, 0.000055),
                'quality_first': ('openai/gpt-5.3-codex', 0.98, 0.00015)
            },
            
            'reasoning': {
                'max_savings': ('nvidia/nemotron-3-super-120b-a12b:free', 0.85, 0),
                'balanced': ('qwen/qwen3.5-397b-a17b', 0.95, 0.0025),
                'quality_first': ('anthropic/claude-opus-4.6', 0.98, 0.015)
            },
            
            'analysis': {
                'max_savings': ('z-ai/glm-5-turbo', 0.90, 0.00003),
                'balanced': ('qwen/qwen3.5-122b-a10b', 0.95, 0.0015),
                'quality_first': ('anthropic/claude-opus-4.6', 0.99, 0.015)
            },
            
            'chat': {
                'max_savings': ('liquid/lfm-2.5-1.2b-instruct:free', 0.95, 0),
                'balanced': ('qwen/qwen3.5-flash-02-23', 0.92, 0.000016),
                'quality_first': ('mistralai/mistral-large-2512', 0.95, 0.003)
            },
            
            'batch_low_value': {
                'max_savings': ('nvidia/nemotron-3-super-120b-a12b:free', 0.80, 0),
                'balanced': ('mistralai/ministral-8b-2512', 0.90, 0.000008),
                'quality_first': ('qwen/qwen3.5-9b', 0.85, 0.00007)
            },
            
            'brainstorming': {
                'max_savings': ('qwen/qwen3.5-9b', 0.85, 0.000007),
                'balanced': ('mistralai/ministral-14b-2512', 0.90, 0.000012),
                'quality_first': ('qwen/qwen3.5-27b', 0.92, 0.000027)
            },
            
            'decision_making': {
                'max_savings': ('z-ai/glm-4.7-flash', 0.80, 0.000009),
                'balanced': ('qwen/qwen3.5-27b', 0.90, 0.000027),
                'quality_first': ('anthropic/claude-sonnet-4.6', 0.97, 0.003)
            },
            
            'enterprise': {
                'max_savings': ('qwen/qwen3.5-397b-a17b', 0.95, 0.0025),
                'balanced': ('anthropic/claude-opus-4.6', 0.98, 0.015),
                'quality_first': ('openai/gpt-5.4-pro', 0.99, 0.005)
            },
        }
    
    def analyze_task(self, task_description: str) -> TaskRequirements:
        """Analyze task description to determine requirements"""
        
        # Simple keyword-based classification (can be enhanced with ML)
        task_lower = task_description.lower()
        
        # Determine task type
        task_type = 'general'
        if any(word in task_lower for word in ['code', 'program', 'script', 'dev', 'debug', 'refactor']):
            task_type = 'coding'
        elif any(word in task_lower for word in ['blog', 'article', 'post', 'write', 'content', 'copy']):
            task_type = 'content'
        elif any(word in task_lower for word in ['reason', 'analyze', 'strategy', 'decision']):
            task_type = 'reasoning'
        elif any(word in task_lower for word in ['chat', 'conversation', 'talk', 'discuss']):
            task_type = 'chat'
        elif any(word in task_lower for word in ['batch', 'bulk', 'process', 'multiple']):
            task_type = 'batch'
        elif any(word in task_lower for word in ['brainstorm', 'idea', 'creative']):
            task_type = 'brainstorming'
        elif any(word in task_lower for word in ['enterprise', 'mission', 'critical', 'business']):
            task_type = 'enterprise'
        
        # Determine complexity
        complexity = 'medium'
        if any(word in task_lower for word in ['simple', 'basic', 'quick', 'easy', 'short']):
            complexity = 'low'
        elif any(word in task_lower for word in ['complex', 'advanced', 'sophisticated', 'detailed']):
            complexity = 'high'
        elif any(word in task_lower for word in ['enterprise', 'mission', 'critical', 'legal', 'medical']):
            complexity = 'enterprise'
        
        # Check for long context needs
        context_needed = None
        if any(word in task_lower for word in ['document', 'pdf', 'long', 'thousands', '10k', '100k']):
            context_needed = 200000
        
        return TaskRequirements(
            task_type=task_type,
            complexity=complexity,
            budget_priority='balanced',  # Default
            context_length_needed=context_needed
        )
    
    def select_model(self, task: TaskRequirements) -> Dict[str, Any]:
        """
        Select optimal model based on task requirements
        
        Returns: {
            'model': model_id,
            'category': 'ultra_cheap|cheap|balanced|high_performance|specialized',
            'confidence': 0.0-1.0,
            'estimated_cost': $ per request,
            'latency': ms,
            'reasoning_score': 1-5,
            'fallback_model': alternative if first fails
        }
        """
        
        # Try direct task mapping first
        task_key = f"{task.task_type}_{task.complexity}"
        
        # Check task-specific mappings
        if task.task_type in self.task_mappings:
            mappings = self.task_mappings[task.task_type]
            # Select based on budget priority
            if task.budget_priority == 'max_savings':
                model_id, confidence, cost = mappings['max_savings']
            elif task.budget_priority == 'quality_first':
                model_id, confidence, cost = mappings['quality_first']
            else:  # balanced
                model_id, confidence, cost = mappings['balanced']
            
            model_info = self.models.get(model_id, {})
            
            return {
                'model': model_id,
                'name': model_info.get('name', model_id),
                'category': model_info.get('category', 'unknown'),
                'confidence': confidence,
                'estimated_cost': cost,
                'latency': model_info.get('latency', 500),
                'reasoning_score': model_info.get('reasoning', 3),
                'fallback_model': self._get_fallback(model_id, 'balanced'),
                'selection_reason': f"Direct mapping for {task.task_type} task"
            }
        
        # Fallback: generic selection based on complexity and budget
        return self._select_generic(task)
    
    def _select_generic(self, task: TaskRequirements) -> Dict[str, Any]:
        """Generic model selection when no specific mapping exists"""
        
        complexity_score = self.thresholds['complexity_scores'][task.complexity]
        
        # Decision tree
        if task.budget_priority == 'max_savings':
            if task.complexity in ['low', 'medium']:
                # Free models first
                if task.domain == 'coding':
                    model_id = 'nvidia/nemotron-3-super-120b-a12b:free'
                else:
                    model_id = 'liquid/lfm-2.5-1.2b-instruct:free'
            else:
                model_id = 'nvidia/nemotron-3-super-120b-a12b:free'
        
        elif task.budget_priority == 'quality_first':
            if task.complexity == 'enterprise':
                model_id = 'anthropic/claude-opus-4.6'
            elif task.complexity == 'high':
                model_id = 'qwen/qwen3.5-397b-a17b'
            else:
                model_id = 'anthropic/claude-sonnet-4.6'
        
        else:  # balanced
            if task.complexity == 'low':
                model_id = 'qwen/qwen3.5-9b'
            elif task.complexity == 'medium':
                model_id = 'qwen/qwen3.5-27b'
            elif task.complexity == 'high':
                model_id = 'deepseek/deepseek-v3.2'
            else:  # enterprise
                model_id = 'qwen/qwen3.5-397b-a17b'
        
        model_info = self.models.get(model_id, {})
        
        return {
            'model': model_id,
            'name': model_info.get('name', model_id),
            'category': model_info.get('category', 'unknown'),
            'confidence': 0.85,
            'estimated_cost': model_info.get('prompt_cost', 0) + model_info.get('completion_cost', 0),
            'latency': model_info.get('latency', 500),
            'reasoning_score': model_info.get('reasoning', 3),
            'fallback_model': self._get_fallback(model_id, 'balanced'),
            'selection_reason': f"Generic selection for {task.complexity} complexity"
        }
    
    def _get_fallback(self, model_id: str, fallback_category: str) -> str:
        """Get fallback model if primary fails"""
        
        fallbacks = {
            # Ultra cheap → Cheap
            'liquid/lfm-2.5-1.2b-instruct:free': 'qwen/qwen3.5-9b',
            'google/gemma-4-26b-a4b-it:free': 'mistralai/ministral-8b-2512',
            
            # Cheap → Balanced
            'qwen/qwen3.5-9b': 'qwen/qwen3.5-27b',
            'mistralai/ministral-8b-2512': 'mistralai/mistral-large-2512',
            
            # Balanced → High Performance
            'qwen/qwen3.5-27b': 'qwen/qwen3.5-397b-a17b',
            'mistralai/mistral-large-2512': 'deepseek/deepseek-v3.2',
            'anthropic/claude-sonnet-4.6': 'anthropic/claude-opus-4.6',
            
            # High Performance → Specialized
            'qwen/qwen3.5-397b-a17b': 'qwen/qwen3-coder-next' if 'coding' in str(self.models.get('qwen/qwen3.5-397b-a17b', {})).lower() else 'anthropic/claude-opus-4.6',
            'deepseek/deepseek-v3.2': 'openai/gpt-5.4',
            
            # Specialized → High Performance
            'qwen/qwen3-coder-next': 'deepseek/deepseek-v3.2',
            'openai/gpt-5.3-codex': 'openai/gpt-5.4',
        }
        
        return fallbacks.get(model_id, 'qwen/qwen3.5-27b')  # Default fallback
    
    def estimate_cost(self, task: TaskRequirements, model_selection: Dict) -> Dict[str, float]:
        """Estimate cost for typical task scenarios"""
        
        model_id = model_selection['model']
        model_info = self.models.get(model_id, {})
        
        # Estimate token usage based on task type
        token_estimates = {
            'chat': {'input': 500, 'output': 300},
            'content_short': {'input': 1000, 'output': 800},
            'content_long_form': {'input': 5000, 'output': 2000},
            'coding': {'input': 2000, 'output': 1500},
            'reasoning': {'input': 1500, 'output': 1000},
            'analysis': {'input': 3000, 'output': 1500},
            'enterprise': {'input': 5000, 'output': 3000},
            'general': {'input': 1000, 'output': 800}
        }
        
        tokens = token_estimates.get(task.task_type, {'input': 1000, 'output': 800})
        
        prompt_cost_per_token = model_info.get('prompt_cost', 0) / 1_000_000
        completion_cost_per_token = model_info.get('completion_cost', 0) / 1_000_000
        
        input_cost = tokens['input'] * prompt_cost_per_token
        output_cost = tokens['output'] * completion_cost_per_token
        
        return {
            'input_tokens': tokens['input'],
            'output_tokens': tokens['output'],
            'input_cost': round(input_cost, 6),
            'output_cost': round(output_cost, 6),
            'total_cost': round(input_cost + output_cost, 6)
        }
    
    def generate_recommendations(self, task: TaskRequirements) -> Dict[str, Any]:
        """Generate comprehensive model selection with recommendations"""
        
        # Get primary selection
        primary = self.select_model(task)
        
        # Get cost estimate
        cost_estimate = self.estimate_cost(task, primary)
        
        # Get fallback
        fallback = self.select_model(TaskRequirements(
            task_type=task.task_type,
            complexity=task.complexity,
            budget_priority='quality_first' if task.budget_priority == 'max_savings' else 'max_savings'
        ))
        
        return {
            'task_analysis': {
                'task_type': task.task_type,
                'complexity': task.complexity,
                'budget_priority': task.budget_priority
            },
            'primary_selection': primary,
            'cost_estimate': cost_estimate,
            'fallback_selection': fallback,
            'optimization_score': self._calculate_optimization_score(task, primary),
            'recommendations': self._generate_recommendations(task, primary)
        }
    
    def _calculate_optimization_score(self, task: TaskRequirements, selection: Dict) -> float:
        """Calculate optimization score (0-1) based on cost/quality tradeoff"""
        
        # Base score on category
        category_scores = {
            'ultra_cheap': 1.0,
            'cheap': 0.85,
            'balanced': 0.70,
            'high_performance': 0.50,
            'specialized': 0.60
        }
        
        base_score = category_scores.get(selection['category'], 0.5)
        
        # Adjust for confidence
        confidence_factor = selection['confidence'] * 0.2
        
        # Adjust for reasoning match
        reasoning_match = min(selection['reasoning_score'] / 5, 1.0) * 0.15
        
        return round(base_score + confidence_factor + reasoning_match, 2)
    
    def _generate_recommendations(self, task: TaskRequirements, selection: Dict) -> list:
        """Generate actionable optimization recommendations"""
        
        recommendations = []
        
        # Cost optimization
        if selection['category'] in ['ultra_cheap', 'cheap']:
            recommendations.append({
                'type': 'cost_savings',
                'message': f"Using {selection['category']} model - excellent cost optimization",
                'impact': 'high'
            })
        
        # Quality check
        if task.complexity == 'enterprise' and selection['category'] in ['ultra_cheap', 'cheap']:
            recommendations.append({
                'type': 'quality_warning',
                'message': f"Enterprise task on {selection['category']} model - consider escalation",
                'impact': 'critical'
            })
        
        # Latency
        if selection['latency'] > 1000:
            recommendations.append({
                'type': 'latency_note',
                'message': f"High latency ({selection['latency']}ms) - not ideal for real-time",
                'impact': 'medium'
            })
        
        # Cost comparison
        if selection['estimated_cost'] > 0.10:
            recommendations.append({
                'type': 'cost_note',
                'message': f"Premium model selected (${selection['estimated_cost']:.4f}/request)",
                'impact': 'medium'
            })
        
        return recommendations


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenRouter Model Selection Engine')
    parser.add_argument('--task', type=str, required=True, help='Task description')
    parser.add_argument('--complexity', type=str, 
                       choices=['low', 'medium', 'high', 'enterprise'],
                       default='medium', help='Task complexity')
    parser.add_argument('--budget', type=str,
                       choices=['max_savings', 'balanced', 'quality_first'],
                       default='balanced', help='Budget priority')
    parser.add_argument('--domain', type=str,
                       choices=['coding', 'writing', 'research', 'general'],
                       default='general', help='Domain specialization')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    # Create engine
    engine = ModelSelectionEngine()
    
    # Analyze task
    task = TaskRequirements(
        task_type='general',  # Will be auto-detected
        complexity=args.complexity,
        budget_priority=args.budget,
        domain=args.domain
    )
    
    # Generate recommendations
    result = engine.generate_recommendations(task)
    
    # Output
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "="*60)
        print("OPENROUTER MODEL SELECTION RECOMMENDATION")
        print("="*60)
        print(f"\nTask: {args.task}")
        print(f"Complexity: {args.complexity}")
        print(f"Budget Priority: {args.budget}")
        
        print(f"\n{'Primary Selection:':^60}")
        primary = result['primary_selection']
        print(f"  Model: {primary['model']}")
        print(f"  Category: {primary['category']}")
        print(f"  Confidence: {primary['confidence']*100:.0f}%")
        print(f"  Estimated Cost: ${primary['estimated_cost']:.6f}")
        
        print(f"\n{'Cost Breakdown:':^60}")
        cost = result['cost_estimate']
        print(f"  Input Tokens: {cost['input_tokens']} (${cost['input_cost']:.6f})")
        print(f"  Output Tokens: {cost['output_tokens']} (${cost['output_cost']:.6f})")
        print(f"  Total: ${cost['total_cost']:.6f}")
        
        print(f"\n{'Fallback:':^60}")
        fallback = result['fallback_selection']
        print(f"  Model: {fallback['model']}")
        
        print(f"\n{'Optimization Score:':^60}")
        print(f"  Score: {result['optimization_score']}/1.0")
        
        print(f"\n{'Recommendations:':^60}")
        for rec in result['recommendations']:
            icon = "✓" if rec['type'] == 'cost_savings' else "⚠" if rec['impact'] != 'critical' else "✗"
            print(f"  {icon} {rec['message']}")
        
        print("\n" + "="*60)


if __name__ == '__main__':
    main()
