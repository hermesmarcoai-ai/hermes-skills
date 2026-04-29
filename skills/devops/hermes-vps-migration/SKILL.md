---
name: hermes-vps-migration
category: devops
description: Backup Hermes agent to GitHub and restore on a new VPS. Covers what to include/exclude, GitHub token requirements, and restore steps. Includes automated scripts.
---

## Trigger Conditions
- User wants to migrate Hermes to a new VPS
- User wants to backup their Hermes configuration and history
- User is changing cloud/VPS providers

## Current Backup Repos (both active, synced 2026-04-29)

| Repo | URL | Contents | Auto-sync |
|------|-----|----------|-----------|
| hermes-skills | github.com/hermesmarcoai-ai/hermes-skills | 48 skill categories (SKILL.md + refs/scripts) | Manual sync (see below) |
| hermes-dotfiles | github.com/hermesmarcoai-ai/hermes-dotfiles | memory/, config/, scripts/, SOUL.md, crypto-trading-guide.md | Cron `10f066fc273e` (daily 3AM) |

### Quick Sync Skills (manual, 2 min)
```bash
cd /tmp && rm -rf skills-backup && mkdir skills-backup && cd skills-backup && \
git clone https://github.com/hermesmarcoai-ai/hermes-skills.git . && \
rsync -av --delete /home/marco/.hermes/skills/ skills/ && \
find skills/ -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null && \
git add -A && git commit -m "Sync $(date '+%Y-%m-%d')" && GIT_TERMINAL_PROMPT=0 git push origin master
```

### Quick Sync Dotfiles (manual, 30 sec)
```bash
cd ~/.hermes/dotfiles && \
rsync -av --delete ~/.hermes/memory/ memory/ && \
rsync -av ~/.hermes/config.yaml config/config.yaml && \
rsync -av ~/.hermes/cron/jobs.json config/cron-jobs.json && \
git add -A && git commit -m "Dotfiles sync $(date '+%Y-%m-%d')" && GIT_TERMINAL_PROMPT=0 git push origin main
```

## Automated Scripts (Actual Location)

Available in `~/.hermes/scripts/`:
- `dotfiles-sync.sh` — syncs dotfiles to GitHub (used by cron job)
- `backup.sh` — general backup script
- `daily-maintenance.sh` — daily maintenance automation
- `enhanced-maintenance.sh` — enhanced maintenance
- `checkpoint.sh` — checkpoint creation
- `memory_hygiene.sh` — memory cleanup

## Manual Backup Steps (if scripts don't work)

### 1. Install GitHub CLI
```bash
apt install -y gh
```

### 2. GitHub Token Requirements
- Must be a **Classic** token (NOT fine-grained)
- Required scopes: `repo` (all sub-scopes included automatically)
- `gh auth login` also requires `read:org` scope
- Create at: https://github.com/settings/tokens?type=classic

### 3. Authenticate and Create Repo
```bash
echo "YOUR_GHP_TOKEN" | gh auth login --with-token
gh repo create hermes-backup --private --description "Hermes Agent backup"
```

### 4. Prepare Backup Directory
Exclude these (waste of space or regenerate from zero):
- `hermes-agent/` — 1.1GB source code, reinstalls from zero
- `logs/` — not needed
- `audio_cache/` — ephemeral
- `models_dev_cache.json` — large, regenerates
- `state.db`, `state.db-shm`, `state.db-wal` — SQLite state DB, not portable
- `node/` — Node.js binaries, reinstalls from zero
- `sandboxes/` — ephemeral
- `image_cache/` — ephemeral

Include these:
- `config/*` — config.yaml, .env, auth.json, SOUL.md, channel_directory.json, PM2 configs
- `sessions/*` — all session history
- `skills/*` — all installed skills (including custom ones)
- `memories/*` — personal memory files
- `checkpoints/*` — project checkpoints
- `cron/*` — cron job outputs
- `gateways/*` — gateway shell scripts

### 5. Create .gitignore
```
# Exclude from backup
*.db
*.db-shm
*.db-wal
*.log
*.ogg
*.mp3
audio_cache/
hermes-agent/
node/
logs/
sandboxes/
image_cache/
models_dev_cache.json
```

### 6. Commit and Push
```bash
cd ~/hermes-backup
git init
git config user.email "marco@hermes.ai"
git config user.name "Marco Hermes"
git add -A
git commit -m "Hermes backup"
git branch -m main
git remote add origin https://github.com/USERNAME/hermes-backup.git
git push -u origin main
```

### 7. Push Authentication
If `gh auth login` succeeded but `git push` fails with `fatal: could not read Username`, embed the token in the remote URL:
```bash
git remote set-url origin https://TOKEN@github.com/USERNAME/hermes-backup.git
git push -u origin main
```

## Manual Restore on New VPS (if scripts don't work)

### 1. Install Hermes from scratch
Follow the standard Hermes installation process.

### 2. Clone and Restore
```bash
git clone https://github.com/USERNAME/hermes-backup.git ~/hermes-restore
```

### 3. Stop any running Hermes processes
```bash
pkill -9 -f hermes_gateway
```

### 4. Restore Files
```bash
cp ~/hermes-restore/config/config.yaml ~/.hermes/
cp ~/hermes-restore/config/.env ~/.hermes/
cp ~/hermes-restore/config/auth.json ~/.hermes/
cp ~/hermes-restore/config/SOUL.md ~/.hermes/
cp -r ~/hermes-restore/skills/* ~/.hermes/skills/
cp -r ~/hermes-restore/memories/* ~/.hermes/memories/
cp -r ~/hermes-restore/sessions/* ~/.hermes/sessions/
cp -r ~/hermes-restore/checkpoints/* ~/.hermes/checkpoints/
cp -r ~/hermes-restore/cron/* ~/.hermes/cron/
for f in ~/hermes-restore/gateways/*; do cp "$f" ~/.hermes/; done
```

### 5. Restart Services
```bash
systemctl start hermes-gateway.service
# or via PM2 if using PM2:
pm2 start pm2-gateway.config.js
```

## Important Notes

### What IS preserved
- All API keys and secrets (.env)
- Agent personality (SOUL.md)
- Agent memory and user profile (MEMORY.md, USER.md)
- All conversation history (sessions/)
- All skills including custom ones
- Cron jobs and their outputs
- Discord and Telegram gateway configs
- PM2 process manager configs

### What is NOT portable (not backed up)
- `state.db` — SQLite state, recreated on first run
- `hermes-agent/` — source code, reinstalls from zero
- `node/` — Node.js binaries, reinstalls from zero
- Ephemeral caches (audio_cache, image_cache, sandboxes)
- Telegram session may need re-authentication after migration

## Pitfalls

1. **Fine-grained tokens don't work** — `gh create repo` and `gh auth login` require Classic tokens with `repo` scope. Fine-grained tokens silently fail with "Resource not accessible".

2. **`gh auth login` requires `read:org`** — Even if you only need repo access, `gh auth login` validates this scope. Add it to your Classic token.

3. **`git push` fails after `gh auth login`** — The token from `gh auth login` doesn't automatically propagate to `git push` in all environments. If push fails, embed the token directly in the remote URL.

4. **Don't backup state.db** — The SQLite state database is not portable between installations. Hermes will recreate its state on first run.

5. **Don't backup hermes-agent/** — This is the Hermes source code (~1.1GB). It gets reinstalled during Hermes setup and is not needed in the backup.
