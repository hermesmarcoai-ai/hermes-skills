---
name: automatic-model-selection-integration
description: Automatically integrate OpenRouter cost-optimization into Hermes agent workflow
category: automation
---

# Automatic Model Selection Integration

Automatically integrate OpenRouter cost-optimization into Hermes agent workflow.

## Prerequisites

- Model selection system installed at `~/.hermes/skills/model-selection/`
- Config.yaml updated with `model_routing` settings
- Agent restarted to load configuration

## Automatic Integration Steps

### Step 1: Create Model Selection Wrapper

```bash
#!/usr/bin/env python3
# ~/.hermes/skills/model-selection/select_model.py

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from model_selection_engine import ModelSelectionEngine, TaskRequirements

def get_optimal_model(task, complexity='medium', budget='balanced'):
    """Select optimal model for task"""
    engine = ModelSelectionEngine()
    req = TaskRequirements(
        task_type='general',
        complexity=complexity,
        budget_priority=budget
    )
    result = engine.generate_recommendations(req)
    return result['primary_selection']['model']

if __name__ == "__main__":
    task = sys.argv[1] if len(sys.argv) > 1 else ''
    if task:
        model = get_optimal_model(task)
        print(model)
```

### Step 2: Create Auto-Select Shell Wrapper

```bash
#!/bin/bash
# ~/.hermes/skills/model-selection/auto_select.sh

TASK="$1"

if [ -z "$TASK" ]; then
    echo "Usage: auto_select.sh 'your task'"
    exit 1
fi

# Select optimal model
MODEL=$(python3 ~/.hermes/skills/model-selection/select_model.py "$TASK")

# Return recommendation
echo "🎯 Optimal model: $MODEL"
python3 ~/.hermes/skills/model-selection/select_model.py "$TASK"
```

### Step 3: Integrate into Agent Workflow

Add to `~/.hermes/config.yaml`:

```yaml
model_routing:
  enabled: true
  strategy: cost_optimized
  fallback_enabled: true
  max_cost_per_request: 0.50
  daily_budget: 10.00

model_selection:
  auto_select: true
  preference: balanced
```

### Step 4: Auto-Selection Hook

Create `~/.hermes/hooks/pre-task.sh`:

```bash
#!/bin/bash
# Automatically select optimal model before each task

TASK="$1"
if [ -z "$TASK" ]; then
    exit 0
fi

# Get optimal model
MODEL=$(python3 ~/.hermes/skills/model-selection/select_model.py "$TASK")

if [ -n "$MODEL" ] && [ "$MODEL" != "qwen/qwen3.5-35b-a3b" ]; then
    echo "🎯 Auto-selected: $MODEL"
    export HERMES_DEFAULT_MODEL="$MODEL"
fi
```

## Usage

### Manual Selection

```bash
hermes model-select "scrivi articolo blog"
hermes model-select "debug code" --domain coding
```

### Automatic (After Integration)

```bash
hermes "scrivi articolo blog"
# → Automatically uses qwen/qwen3.5-9b ($0.07)

hermes "refactor code"
# → Automatically uses qwen/qwen3-coder-next ($0.50)

hermes "chat"
# → Automatically uses liquid/lfm-2.5-1.2b-instruct:free (FREE!)
```

## Model Selection Rules

| Task Type | Budget | Model | Cost |
|-----------|--------|-------|------|
| Chat/Quick | max_savings | liquid/lfm-2.5-1.2b:free | FREE |
| Content Short | balanced | qwen/qwen3.5-9b | $0.07 |
| Coding | balanced | qwen/qwen3-coder-next | $0.50 |
| Analysis | balanced | deepseek/deepseek-v3.2 | $0.55 |
| Enterprise | quality_first | qwen/qwen3.5-397b | $2.50 |

## Troubleshooting

**Issue**: Models not auto-selected

**Solution**:
```bash
# Verify configuration
grep "model_routing" ~/.hermes/config.yaml

# Test model selection
python3 ~/.hermes/skills/model-selection/select_model.py "test"

# Restart agent
systemctl restart hermes-agent
```

**Issue**: Error in wrapper script

**Solution**:
```bash
# Make scripts executable
chmod +x ~/.hermes/skills/model-selection/*.sh

# Test Python script
python3 ~/.hermes/skills/model-selection/select_model.py "test task"
```

## Expected Results

- **Cost savings**: 80-99% vs manual premium selection
- **Average cost**: $0.01-0.05 per task
- **Quality maintained**: 85-99% confidence scores
- **Automatic fallback**: If primary fails, escalates to next tier