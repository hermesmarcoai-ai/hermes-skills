#!/bin/bash
#==============================================================================
# HERMES PRE-INSTALL RESTORE
# Run this BEFORE installing Hermes on a NEW VPS. It puts the backup
# config in place so Hermes installer finds everything already configured.
#
# Quick run:
#   curl -L https://raw.githubusercontent.com/marcoolibusiness-oss/hermes-backup/main/pre-install-restore.sh | bash
#==============================================================================
set -euo pipefail

GITHUB_TOKEN=""
GITHUB_USER="marcoolibusiness-oss"
GITHUB_REPO="hermes-backup"
RESTORE_DIR="$HOME/hermes-restore"
HERMES_DIR="$HOME/.hermes"

GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
info()  { echo -e "${GREEN}[SETUP]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo "================================================"
echo " HERMES PRE-INSTALL RESTORE"
echo " Run this BEFORE running hermes init/install"
echo "================================================"
echo ""

# ── Check if already installed ───────────────────────────────────────────
if [ -d "$HERMES_DIR/hermes-agent" ] && [ -f "$HERMES_DIR/config.yaml" ]; then
    error "Hermes seems already installed at $HERMES_DIR"
    error "Use restore-hermes.sh instead (for post-install restore)."
    exit 1
fi

# ── Create temp .hermes dir ──────────────────────────────────────────────
info "Preparing config directory..."
mkdir -p "$HERMES_DIR"

# ── Clone backup repo ────────────────────────────────────────────────────
if [ -d "$RESTORE_DIR/.git" ]; then
    info "Updating existing clone..."
    cd "$RESTORE_DIR"
    git fetch origin
    git reset --hard origin/main
else
    # Try gh auth first
    if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
        info "Using gh auth for private repo..."
        gh repo clone "${GITHUB_USER}/${GITHUB_REPO}" "$RESTORE_DIR" -- --quiet
    else
        echo "Enter your GitHub Personal Access Token (classic, 'repo' scope):"
        echo "Create at: https://github.com/settings/tokens?type=classic"
        read -s -p "Token: " GITHUB_TOKEN
        echo ""

        if [ -z "$GITHUB_TOKEN" ]; then
            error "Token required for private repo."
            exit 1
        fi

        git clone "https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${GITHUB_REPO}.git" "$RESTORE_DIR" --quiet
    fi
fi

# ── Verify backup ────────────────────────────────────────────────────────
if [ ! -f "$RESTORE_DIR/config/.env" ] || [ ! -f "$RESTORE_DIR/config/config.yaml" ]; then
    error "Backup incomplete: missing .env or config.yaml"
    exit 1
fi

info "Backup verified. Found:"
echo "  - config.yaml (models, providers, gateway settings)"
echo "  - .env (API keys)"
echo "  - $(ls "$RESTORE_DIR/sessions/" 2>/dev/null | wc -l) sessions"
echo "  - $(find "$RESTORE_DIR/skills/" -name "SKILL.md" 2>/dev/null | wc -l) skills"
echo ""

# ── Copy critical files ─────────────────────────────────────────────────
info "Placing config BEFORE Hermes install..."

# 1. .env with all API keys
cp "$RESTORE_DIR/config/.env" "$HERMES_DIR/.env"
chmod 600 "$HERMES_DIR/.env"
info "  ✓ .env (API keys placed)"

# 2. config.yaml (the main config)
cp "$RESTORE_DIR/config/config.yaml" "$HERMES_DIR/config.yaml"
chmod 600 "$HERMES_DIR/config.yaml"
info "  ✓ config.yaml (models, providers, etc.)"

# 3. auth.json
if [ -f "$RESTORE_DIR/config/auth.json" ]; then
    cp "$RESTORE_DIR/config/auth.json" "$HERMES_DIR/auth.json"
    info "  ✓ auth.json"
fi

# 4. SOUL.md (personality)
if [ -f "$RESTORE_DIR/config/SOUL.md" ]; then
    cp "$RESTORE_DIR/config/SOUL.md" "$HERMES_DIR/SOUL.md"
    info "  ✓ SOUL.md (personality)"
fi

# 5. Gateway configs
for f in discord-env discord_threads.json telegram-gateway.sh discord-gateway.sh gateway-pm2.sh gateway-both.sh gateway-discord-pm2.sh gateway_state.json channel_directory.json pm2-ecosystem.config.js pm2-gateway.config.js; do
    if [ -f "$RESTORE_DIR/gateways/$f" ]; then
        cp "$RESTORE_DIR/gateways/$f" "$HERMES_DIR/$f"
    fi
    if [ -f "$RESTORE_DIR/config/$f" ]; then
        cp "$RESTORE_DIR/config/$f" "$HERMES_DIR/$f"
    fi
done
info "  ✓ Gateway configs"

# 6. Skills, memories, cron
mkdir -p "$HERMES_DIR/skills" "$HERMES_DIR/memories" "$HERMES_DIR/checkpoints" "$HERMES_DIR/cron" 2>/dev/null || true
for dir in skills memories checkpoints; do
    if [ -d "$RESTORE_DIR/$dir" ]; then
        cp -r "$RESTORE_DIR/$dir/"* "$HERMES_DIR/$dir/" 2>/dev/null || true
    fi
done
if [ -d "$RESTORE_DIR/cron" ]; then
    rm -rf "$HERMES_DIR/cron/output" 2>/dev/null || true
    cp -r "$RESTORE_DIR/cron/"* "$HERMES_DIR/cron/" 2>/dev/null || true
fi
info "  ✓ Skills, memories, checkpoints, cron"

# ── Load env vars for the current shell ──────────────────────────────────
set -a
source "$HERMES_DIR/.env"
set +a

info ""
echo "================================================"
echo " CONFIG PLACED SUCCESSFULLY!"
echo ""
echo " Your .env and config.yaml are now in place."
echo ""
echo " NEXT STEP:"
echo " Run the Hermes installer as usual."
echo " It should detect the existing config and"
echo " skip the setup wizard."
echo ""
echo " If it still asks for API keys/model,"
echo " just press Enter/put anything - the"
echo " restore has already placed the real config."
echo ""
echo " After the installer finishes, start Hermes"
echo " and tell it 'restaura tutto' to complete"
echo " the full restore (sessions, etc.)"
echo "================================================"
echo ""
info "Cleaning up temp files..."
rm -rf "$RESTORE_DIR"
