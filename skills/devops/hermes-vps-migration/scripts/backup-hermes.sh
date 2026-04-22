#!/bin/bash
#==============================================================================
# HERMES BACKUP SCRIPT
# Backs up everything except system dependencies to the existing GitHub repo.
# Run this BEFORE migrating to a new VPS.
#==============================================================================
set -euo pipefail

# ── Config ───────────────────────────────────────────────────────────────
HERMES_DIR="$HOME/.hermes"
BACKUP_DIR="$HOME/hermes-backup"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)

# ── Colors ───────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
info()    { echo -e "${GREEN}[BACKUP]${NC} $1"; }
warn()    { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error()   { echo -e "${RED}[ERROR]${NC} $1"; }

# ── Pre-flight checks ────────────────────────────────────────────────────
info "Checking Hermes installation..."
if [ ! -d "$HERMES_DIR" ]; then
    error "Hermes directory not found at $HERMES_DIR"
    exit 1
fi

if [ ! -d "$BACKUP_DIR/.git" ]; then
    error "Backup git repo not found at $BACKUP_DIR. Clone or init it first."
    exit 1
fi

# Check git remote exists
cd "$BACKUP_DIR"
if ! git remote get-url origin &>/dev/null; then
    error "No git remote 'origin' configured. Run: git remote add origin <URL>"
    exit 1
fi
info "Remote found: $(git remote get-url origin | sed 's/\/\/.*@/\/\/...@/')"

# ── Clean old backup data ────────────────────────────────────────────────
info "Cleaning old backup data..."
rm -rf "$BACKUP_DIR/config" \
       "$BACKUP_DIR/sessions" \
       "$BACKUP_DIR/skills" \
       "$BACKUP_DIR/memories" \
       "$BACKUP_DIR/checkpoints" \
       "$BACKUP_DIR/cron" \
       "$BACKUP_DIR/gateways" \
       "$BACKUP_DIR/credentials"

mkdir -p "$BACKUP_DIR/{config,sessions,skills,memories,checkpoints,cron/output,gateways,credentials}"

# ── CRITICAL FILES ──────────────────────────────────────────────────────
info "Saving critical files..."

# 1. config.yaml (main config - models, providers, gateways, all settings)
cp "$HERMES_DIR/config.yaml" "$BACKUP_DIR/config/"
info "  config.yaml"

# 2. .env (ALL API keys, secrets, credentials)
cp "$HERMES_DIR/.env" "$BACKUP_DIR/config/"
info "  .env"

# 3. auth.json (OAuth tokens, credential pool state)
if [ -f "$HERMES_DIR/auth.json" ]; then
    cp "$HERMES_DIR/auth.json" "$BACKUP_DIR/config/"
    info "  auth.json"
fi

# 4. SOUL.md (personality/persona definition)
if [ -f "$HERMES_DIR/SOUL.md" ]; then
    cp "$HERMES_DIR/SOUL.md" "$BACKUP_DIR/config/"
    info "  SOUL.md"
fi

# 5. PM2 configs (gateway process management)
for f in pm2-ecosystem.config.js pm2-gateway.config.js; do
    if [ -f "$HERMES_DIR/$f" ]; then
        cp "$HERMES_DIR/$f" "$BACKUP_DIR/config/"
        info "  $f"
    fi
done

# 6. Discord/Telegram configs
for f in discord-env discord_threads.json telegram-gateway.sh discord-gateway.sh gateway-pm2.sh gateway-both.sh gateway-discord-pm2.sh gateway_state.json channel_directory.json; do
    if [ -f "$HERMES_DIR/$f" ]; then
        cp "$HERMES_DIR/$f" "$BACKUP_DIR/gateways/"
        info "  $f"
    fi
done

# 7. .hermes_history (command interaction history)
if [ -f "$HERMES_DIR/.hermes_history" ]; then
    cp "$HERMES_DIR/.hermes_history" "$BACKUP_DIR/config/"
    info "  .hermes_history"
fi

# 8. .skills_prompt_snapshot.json (compiled skills prompt)
if [ -f "$HERMES_DIR/.skills_prompt_snapshot.json" ]; then
    cp "$HERMES_DIR/.skills_prompt_snapshot.json" "$BACKUP_DIR/config/"
    info "  .skills_prompt_snapshot.json"
fi

# ── MEMORIES (agent memory + user profile) ──────────────────────────────
info "Saving memories..."
cp "$HERMES_DIR/memories/"* "$BACKUP_DIR/memories/" 2>/dev/null || true

# ── SESSIONS (all conversation history) ─────────────────────────────────
info "Saving session history..."
cp -r "$HERMES_DIR/sessions/"* "$BACKUP_DIR/sessions/" 2>/dev/null || true
SESSION_COUNT=$(ls "$BACKUP_DIR/sessions/" 2>/dev/null | wc -l)
info "  $SESSION_COUNT sessions saved"

# ── SKILLS (all installed + custom skills) ──────────────────────────────
info "Saving skills..."
cp -r "$HERMES_DIR/skills/"* "$BACKUP_DIR/skills/" 2>/dev/null || true
SKILL_COUNT=$(find "$BACKUP_DIR/skills" -name "SKILL.md" 2>/dev/null | wc -l)
info "  $SKILL_COUNT skills (SKILL.md files)"

# ── CHECKPOINTS ─────────────────────────────────────────────────────────
info "Saving checkpoints..."
cp -r "$HERMES_DIR/checkpoints/"* "$BACKUP_DIR/checkpoints/" 2>/dev/null || true
CHECKPOINT_COUNT=$(ls "$BACKUP_DIR/checkpoints" 2>/dev/null | wc -l)
info "  $CHECKPOINT_COUNT checkpoints"

# ── CRON JOBS (scheduled tasks + outputs) ───────────────────────────────
info "Saving cron jobs..."
if [ -f "$HERMES_DIR/cron/jobs.json" ]; then
    cp "$HERMES_DIR/cron/jobs.json" "$BACKUP_DIR/cron/"
    info "  jobs.json"
fi
if [ -d "$HERMES_DIR/cron/output" ]; then
    cp -r "$HERMES_DIR/cron/output/"* "$BACKUP_DIR/cron/output/" 2>/dev/null || true
fi

# ── WHAT IS NOT BACKED UP (intentionally) ───────────────────────────────
warn "NOT backed up (intentionally - reinstall from scratch):"
warn "  hermes-agent/     -> Hermes source code (reinstalls via setup)"
warn "  node/             -> Node.js binaries (reinstalls via setup)"
warn "  sandboxes/        -> Ephemeral sandbox dirs"
warn "  audio_cache/      -> Ephemeral audio files"
warn "  image_cache/      -> Ephemeral image files"
warn "  images/           -> User-saved images"
warn "  logs/             -> Log files"
warn "  state.db*         -> SQLite state (not portable between installs)"
warn "  locks/            -> Runtime lock files"
warn "  cache/            -> Runtime cache"
warn ""
warn "MANUALLY BACKUP IF NEEDED:"
warn "  images/       -> your saved images (screenshots, generated)"
warn "  audio_cache/  -> any voice files you want to keep"

# ── Commit and Push ─────────────────────────────────────────────────────
info "Committing to git..."
cd "$BACKUP_DIR"
git add -A
COMMIT_MSG="Hermes backup $BACKUP_DATE - $SESSION_COUNT sessions, $SKILL_COUNT skills, $CHECKPOINT_COUNT checkpoints"
if git diff --cached --quiet; then
    warn "No changes detected. Backup up to date."
    exit 0
fi

git commit -m "$COMMIT_MSG"

info "Pushing to GitHub..."
git push origin main

info "Backup complete!"
info "Total size: $(du -sh "$BACKUP_DIR" --exclude='.git' | cut -f1)"
info "Git repo size: $(du -sh "$BACKUP_DIR/.git" | cut -f1)"
info "Backup date: $BACKUP_DATE"
