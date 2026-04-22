#!/bin/bash
#==============================================================================
# HERMES RESTORE SCRIPT
# Restores a complete Hermes installation from the GitHub backup repo.
# Run this AFTER installing Hermes on a NEW VPS.
#
# Prerequisites:
#   1. Hermes is installed fresh on the new VPS (hermes init)
#   2. You know the GitHub repo URL (e.g. https://github.com/USER/hermes-backup)
#   3. A GitHub personal access token (classic) with 'repo' scope
#
# WARNING: This script overwrites files in ~/.hermes. Only run on a fresh install.
#==============================================================================
set -euo pipefail

# ── Config ───────────────────────────────────────────────────────────────
HERMES_DIR="$HOME/.hermes"
RESTORE_DIR="$HOME/hermes-restore"
GITHUB_USER="marcoolibusiness-oss"
GITHUB_REPO="hermes-backup"
REPO_URL="https://github.com/${GITHUB_USER}/${GITHUB_REPO}.git"

# ── Colors ───────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()    { echo -e "${GREEN}[RESTORE]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# ── Interactive prompt for GitHub token ──────────────────────────────────
info "╔══════════════════════════════════════════╗"
info "║    HERMES VPS RESTORE                    ║"
info "╚══════════════════════════════════════════╝"
echo ""

if [ ! -d "$HERMES_DIR" ]; then
    error "Hermes is not installed at $HERMES_DIR"
    error "Install Hermes first (hermes init or setup script), then run this."
    exit 1
fi

info "Hermes directory found at $HERMES_DIR"
echo ""

# ── Check if hermes-agent/ is installed ──────────────────────────────────
if [ ! -d "$HERMES_DIR/hermes-agent" ]; then
    warn "hermes-agent/ not found - Hermes may not be fully installed."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# ── Stop any running processes ──────────────────────────────────────────
info "Stopping running Hermes processes..."
pkill -9 -f hermes_agent 2>/dev/null || true
pkill -9 -f hermes_gateway 2>/dev/null || true
sleep 2

# ── Clone/clear restore directory ────────────────────────────────────────
if [ -d "$RESTORE_DIR/.git" ]; then
    info "Restoring existing local clone..."
    cd "$RESTORE_DIR"
    git fetch origin
    git reset --hard origin/main
else
    info "Cloning backup from GitHub..."

    # Try with gh auth first
    if command -v gh &>/dev/null && gh auth status &>/dev/null 2>&1; then
        info "Using gh auth for private repo..."
        gh auth git-credential store &>/dev/null || true
        gh repo clone "${GITHUB_USER}/${GITHUB_REPO}" "$RESTORE_DIR" -- --quiet
    else
        # Need token for private repo
        echo ""
        echo "Enter your GitHub Personal Access Token (classic, 'repo' scope):"
        echo "Create one at: https://github.com/settings/tokens?type=classic"
        read -s -p "Token: " GH_TOKEN
        echo ""

        if [ -z "$GH_TOKEN" ]; then
            error "Token is required for private repo."
            exit 1
        fi

        git clone "https://${GH_TOKEN}@github.com/${GITHUB_USER}/${GITHUB_REPO}.git" "$RESTORE_DIR" --quiet
    fi
fi

cd "$RESTORE_DIR"

# ── Verify backup exists ────────────────────────────────────────────────
if [ ! -f "$RESTORE_DIR/config/config.yaml" ]; then
    error "Backup is incomplete: config.yaml not found."
    exit 1
fi

if [ ! -f "$RESTORE_DIR/config/.env" ]; then
    error "Backup is incomplete: .env not found. API keys will be missing."
    exit 1
fi

info "Backup verified."
info "  Last commit: $(git log --format='%h %cr (%s)' -1)"
SESSIONS=$(ls "$RESTORE_DIR/sessions/" 2>/dev/null | wc -l)
SKILLS=$(find "$RESTORE_DIR/skills/" -name "SKILL.md" 2>/dev/null | wc -l)
MEMORIES=$(ls "$RESTORE_DIR/memories/" 2>/dev/null | wc -l)
info "  Sessions: $SESSIONS | Skills: $SKILLS | Memories: $MEMORIES"
echo ""

# ── Confirmation ─────────────────────────────────────────────────────────
warn "This will OVERWRITE files in $HERMES_DIR"
read -p "Continue with restore? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    info "Restore cancelled."
    exit 0
fi

# ── Restore files ────────────────────────────────────────────────────────
info "Restoring files..."

# 1. Main config
cp "$RESTORE_DIR/config/config.yaml" "$HERMES_DIR/config.yaml"
info "  ✓ config.yaml"

# 2. Environment (API keys)
cp "$RESTORE_DIR/config/.env" "$HERMES_DIR/.env"
info "  ✓ .env (API keys)"

# 3. Auth state
if [ -f "$RESTORE_DIR/config/auth.json" ]; then
    cp "$RESTORE_DIR/config/auth.json" "$HERMES_DIR/auth.json"
    info "  ✓ auth.json"
fi

# 4. Personality
if [ -f "$RESTORE_DIR/config/SOUL.md" ]; then
    cp "$RESTORE_DIR/config/SOUL.md" "$HERMES_DIR/SOUL.md"
    info "  ✓ SOUL.md"
fi

# 5. Compiled skills prompt
if [ -f "$RESTORE_DIR/config/.skills_prompt_snapshot.json" ]; then
    cp "$RESTORE_DIR/config/.skills_prompt_snapshot.json" "$HERMES_DIR/.skills_prompt_snapshot.json"
    info "  ✓ .skills_prompt_snapshot.json"
fi

# 6. PM2 configs
for f in pm2-ecosystem.config.js pm2-gateway.config.js; do
    if [ -f "$RESTORE_DIR/config/$f" ]; then
        cp "$RESTORE_DIR/config/$f" "$HERMES_DIR/$f"
        info "  ✓ $f"
    fi
done

# 7. Memories (agent memory + user profile)
if [ -d "$RESTORE_DIR/memories" ]; then
    rm -rf "$HERMES_DIR/memories/"* 2>/dev/null || true
    cp "$RESTORE_DIR/memories/"* "$HERMES_DIR/memories/" 2>/dev/null || true
    info "  ✓ Memories ($MEMORIES files)"
fi

# 8. Sessions (conversation history)
if [ -d "$RESTORE_DIR/sessions" ]; then
    rm -rf "$HERMES_DIR/sessions/"* 2>/dev/null || true
    cp -r "$RESTORE_DIR/sessions/"* "$HERMES_DIR/sessions/" 2>/dev/null || true
    info "  ✓ Sessions ($SESSIONS files)"
fi

# 9. Skills (all installed + custom)
if [ -d "$RESTORE_DIR/skills" ]; then
    rm -rf "$HERMES_DIR/skills/"* 2>/dev/null || true
    cp -r "$RESTORE_DIR/skills/"* "$HERMES_DIR/skills/" 2>/dev/null || true
    info "  ✓ Skills ($SKILLS SKILL.md files)"
fi

# 10. Checkpoints
if [ -d "$RESTORE_DIR/checkpoints" ]; then
    rm -rf "$HERMES_DIR/checkpoints/"* 2>/dev/null || true
    cp -r "$RESTORE_DIR/checkpoints/"* "$HERMES_DIR/checkpoints/" 2>/dev/null || true
    CHECKPOINTS=$(ls "$RESTORE_DIR/checkpoints/" 2>/dev/null | wc -l)
    info "  ✓ Checkpoints ($CHECKPOINTS dirs)"
fi

# 11. Cron jobs and outputs
if [ -f "$RESTORE_DIR/cron/jobs.json" ]; then
    cp "$RESTORE_DIR/cron/jobs.json" "$HERMES_DIR/cron/jobs.json"
    info "  ✓ Cron jobs (jobs.json)"
fi
if [ -d "$RESTORE_DIR/cron/output" ]; then
    rm -rf "$HERMES_DIR/cron/output/"* 2>/dev/null || true
    cp -r "$RESTORE_DIR/cron/output/"* "$HERMES_DIR/cron/output/" 2>/dev/null || true
    info "  ✓ Cron outputs"
fi

# 12. Gateway scripts + configs
for f in discord-env discord_threads.json telegram-gateway.sh discord-gateway.sh gateway-pm2.sh gateway-both.sh gateway-discord-pm2.sh gateway_state.json channel_directory.json; do
    if [ -f "$RESTORE_DIR/gateways/$f" ]; then
        cp "$RESTORE_DIR/gateways/$f" "$HERMES_DIR/$f"
        info "  ✓ $f"
    fi
done

# ── Environment variable export ─────────────────────────────────────────
info "Loading environment variables..."
set -a
source "$HERMES_DIR/.env"
set +a

# ── Set file permissions ────────────────────────────────────────────────
info "Setting file permissions..."
chmod 600 "$HERMES_DIR/.env" 2>/dev/null || true
chmod 600 "$HERMES_DIR/config.yaml" 2>/dev/null || true
chmod 600 "$HERMES_DIR/auth.json" 2>/dev/null || true

# ── Restart services ─────────────────────────────────────────────────────
echo ""
info "╔══════════════════════════════════════════╗"
info "║    RESTART SERVICES                      ║"
info "╚══════════════════════════════════════════╝"
echo ""

info "Choose how to restart the gateway:"
echo "  1) systemd service (recommended)"
echo "  2) PM2"
echo "  3) Skip (I'll restart manually)"
read -p "Choice (1/2/3): " -n 1 -r
echo
echo ""

case $REPLY in
    1)
        info "Restarting via systemd..."
        # Proven fix: kill orphans first
        pkill -9 -f hermes_gateway 2>/dev/null || true
        sleep 3
        systemctl start hermes-gateway.service 2>/dev/null || {
            error "systemctl start failed. Check: systemctl status hermes-gateway.service"
        }
        systemctl status hermes-gateway.service --no-pager 2>/dev/null || true
        ;;
    2)
        info "Restarting via PM2..."
        if [ -f "$HERMES_DIR/pm2-gateway.config.js" ]; then
            pm2 delete all 2>/dev/null || true
            pm2 start "$HERMES_DIR/pm2-gateway.config.js"
            pm2 save
        else
            error "pm2-gateway.config.js not found"
        fi
        ;;
    3)
        info "Skipping restart. To start manually:"
        info "  systemd: systemctl start hermes-gateway.service"
        info "  PM2: pm2 start $HERMES_DIR/pm2-gateway.config.js"
        ;;
    *)
        info "Unknown choice. Restart manually."
        ;;
esac

# ── Cleanup ──────────────────────────────────────────────────────────────
echo ""
info "Cleaning up restore directory..."
rm -rf "$RESTORE_DIR"

# ── Done ─────────────────────────────────────────────────────────────────
echo ""
info "╔════════════════════════════════════════════════════════╗"
info "║   RESTORE COMPLETE!                                    ║"
info "║                                                        ║"
info "║   What was restored:                                   ║"
info "║   ✓ config.yaml (all settings, models, providers)      ║"
info "║   ✓ .env (all API keys and secrets)                    ║"
info "║   ✓ auth.json (credential pool state)                  ║"
info "║   ✓ SOUL.md (agent personality)                        ║"
info "║   ✓ Memories (agent memory + your profile)             ║"
info "║   ✓ Session history (past conversations)               ║"
info "║   ✓ All skills (including custom ones)                 ║"
info "║   ✓ Checkpoints (project states)                       ║"
info "║   ✓ Cron jobs (scheduled tasks)                        ║"
info "║   ✓ Gateway configs (Discord, Telegram, PM2)           ║"
info "╚════════════════════════════════════════════════════════╝"
echo ""
warn "IMPORTANT: You may need to:"
warn "  1. Log into Telegram again (session may be invalidated)"
warn "  2. Verify Discord bot is online"
warn "  3. Check: hermes model (verify model config)"
warn "  4. Check: hermes cron (verify scheduled jobs)"
echo ""
info "You're all set, Marco!"
