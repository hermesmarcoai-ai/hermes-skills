#!/bin/bash
# restore-hermes.sh — Complete restore of Hermes Agent on a fresh VPS
# Usage: bash <(curl -sL https://raw.githubusercontent.com/hermesmarcoai-ai/hermes-skills/master/skills/devops/hermes-auto-update-cron/scripts/restore-hermes.sh)
set -euo pipefail

REPO="https://github.com/hermesmarcoai-ai/hermes-skills.git"
BACKUP_DIR="${BACKUP_DIR:-/tmp/hermes-backup}"
SKILLS_DIR="${HOME}/.hermes/skills"

echo "=== Hermes Agent Restore Script ==="
echo "Backup repo: $REPO"
echo "Target skills dir: $SKILLS_DIR"

# 1. Clone or update the backup repo
if [ -d "$BACKUP_DIR/.git" ]; then
    echo "[1/5] Updating existing backup..."
    cd "$BACKUP_DIR" && git pull origin master
else
    echo "[1/5] Cloning backup repo..."
    rm -rf "$BACKUP_DIR"
    git clone "$REPO" "$BACKUP_DIR"
fi

# 2. Copy skills to Hermes
echo "[2/5] Restoring skills..."
cp -r "$BACKUP_DIR/skills/"* "$SKILLS_DIR/" 2>/dev/null || true
echo "   → Restored $(ls -1 $BACKUP_DIR/skills/ 2>/dev/null | wc -l) skills"

# 3. Copy cron jobs if exists
if [ -f "$BACKUP_DIR/cron/jobs.json" ]; then
    echo "[3/5] Restoring cron jobs..."
    mkdir -p "${HOME}/.hermes/cron"
    cp "$BACKUP_DIR/cron/jobs.json" "${HOME}/.hermes/cron/jobs.json"
fi

# 4. Copy memory if exists
if [ -f "$BACKUP_DIR/memories/MEMORY.md" ]; then
    echo "[4/5] Restoring memories..."
    mkdir -p "${HOME}/.hermes/memories"
    cp "$BACKUP_DIR/memories/MEMORY.md" "${HOME}/.hermes/memories/MEMORY.md"
fi

# 5. Verification
echo "[5/5] Verification..."
HERMES_VERSION=$(cd "${HOME}/.hermes" && git rev-parse --short HEAD 2>/dev/null || echo "unknown")
SKILLS_COUNT=$(ls -1 "$SKILLS_DIR" 2>/dev/null | wc -l)
echo ""
echo "=== Restore Complete ==="
echo "Hermes commit: $HERMES_VERSION"
echo "Skills restored: $SKILLS_COUNT"
echo ""
echo "Next steps:"
echo "  1. Restart gateway: systemctl restart hermes-gateway.service"
echo "  2. Check status: hermes status"
echo "  3. Verify cron: hermes cron list"