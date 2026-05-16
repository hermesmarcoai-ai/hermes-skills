#!/bin/bash
# Hermes Agent Restore Script for New VPS
# Usage: ./restore.sh

set -e

HERMES_DIR="$HOME/.hermes"
BACKUP_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔄 Hermes Agent Restore Script"
echo "==============================="

# Backup existing files
if [ -d "$HERMES_DIR" ]; then
    echo "📦 Backing up existing ~/.hermes directory..."
    mv "$HERMES_DIR" "$HERMES_DIR.backup.$(date +%Y%m%d%H%M%S)"
fi

echo "📁 Creating new Hermes directory..."
mkdir -p "$HERMES_DIR/skills"
mkdir -p "$HERMES_DIR/scripts"
mkdir -p "$HERMES_DIR/cron"
mkdir -p "$HERMES_DIR/dotfiles"

# Copy skills
echo "📚 Installing custom skills..."
for skill_dir in "$BACKUP_DIR"/skills_backup/*/; do
    skill_name=$(basename "$skill_dir")
    echo "  - $skill_name"
    cp -r "$skill_dir" "$HERMES_DIR/skills/"
done

# Copy scripts
echo "📜 Copying scripts..."
cp "$BACKUP_DIR"/scripts_backup/* "$HERMES_DIR/scripts/" 2>/dev/null || true

# Copy cron config
echo "⏰ Restoring cron configuration..."
cp "$BACKUP_DIR"/cron_backup/jobs.json "$HERMES_DIR/cron/" 2>/dev/null || true

echo ""
echo "✅ Restore complete!"
echo ""
echo "Next steps:"
echo "1. Install dependencies: pip install agentmemory"
echo "2. Configure credentials in ~/.hermes/dotfiles/config/config.yaml"
echo "3. Restart Hermes services"
