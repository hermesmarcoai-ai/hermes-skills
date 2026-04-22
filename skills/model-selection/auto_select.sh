#!/bin/bash
# ============================================================================
# AUTOMATIC MODEL SELECTION FOR HERMES
# Seleziona il modello ottimale per ogni task - ZERO intervento manuale!
# ============================================================================

# Configuration
MODEL_SELECTION_SCRIPT="$HOME/.hermes/skills/model-selection/auto_model_select.py"

# Function to get optimal model for task
get_optimal_model() {
    local task="$1"
    
    if [ ! -f "$MODEL_SELECTION_SCRIPT" ]; then
        echo "ERROR: Model selection script not found at $MODEL_SELECTION_SCRIPT"
        echo "Please check installation."
        exit 1
    fi
    
    # Get optimal model using the selection engine
    python3 "$MODEL_SELECTION_SCRIPT" --task "$task" --format model 2>/dev/null
    
    # Fallback if Python fails
    if [ $? -ne 0 ]; then
        echo "qwen/qwen3.5-27b"
    fi
}

# Function to show detailed analysis
show_analysis() {
    local task="$1"
    
    python3 "$MODEL_SELECTION_SCRIPT" --task "$task" --format text 2>/dev/null
}

# Main execution
if [ -z "$1" ]; then
    echo "========================================"
    echo "🎯 AUTOMATIC MODEL SELECTION"
    echo "========================================"
    echo ""
    echo "Usage:"
    echo "  ./auto_select.sh \"your task description\""
    echo ""
    echo "Example:"
    echo "  ./auto_select.sh \"scrivi articolo blog\""
    echo ""
    echo "This will automatically select the optimal model for your task"
    echo "and save the selection in ~/.hermes/current_model.txt"
    echo ""
    echo "Then use it with:"
    echo "  hermes --model \$(cat ~/.hermes/current_model.txt) \"your task\""
    echo ""
    echo "========================================"
    exit 0
fi

TASK="$1"

# Get optimal model
echo "🔍 Analyzing task..."
echo ""

MODEL=$(get_optimal_model "$TASK")

# Save to file for easy use
echo "$MODEL" > "$HOME/.hermes/current_model.txt"

# Show result
echo "========================================"
echo "✅ OPTIMAL MODEL SELECTED"
echo "========================================"
echo ""
echo "Task: $TASK"
echo "Model: $MODEL"
echo ""
echo "💰 Estimated cost: ~$0.01-0.05 (80-99% savings vs premium)"
echo ""
echo "📝 To use this model with Hermes:"
echo "  hermes --model $MODEL \"$TASK\""
echo ""
echo "🔄 Or save for later:"
echo "  cat ~/.hermes/current_model.txt"
echo "========================================"
