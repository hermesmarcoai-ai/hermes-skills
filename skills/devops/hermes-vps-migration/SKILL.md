---
name: hermes-vps-migration
category: devops
description: Backup Hermes agent to GitHub and restore on a new VPS. Covers what to include/exclude, GitHub token requirements, and restore steps. Includes automated scripts.
---

## Trigger Conditions
- User wants to migrate Hermes to a new VPS
- User wants to backup their Hermes configuration and history
- User is changing cloud/VPS providers

## Automated Scripts (Recommended)

Three scripts are available in ~/hermes-backup/ for fully automated backup/restore.

### Pre-Install Restore (run on NEW VPS BEFORE running hermes install)
```bash
curl -L https://raw.githubusercontent.com/marcoolibusiness-oss/hermes-backup/main/pre-install-restore.sh | bash
```
This is the BEST approach because the Hermes installer asks for API keys and model config BEFORE it starts. This script places .env and config.yaml in ~/.hermes BEFORE the installer runs, so the installer detects existing config and skips the wizard entirely.

What it does:
- Clones backup repo (handles private repo auth via gh or token)
- Places .env (API keys) in ~/.hermes/.env
- Places config.yaml (models, providers, all settings) in ~/.hermes/config.yaml
- Places SOUL.md, auth.json, gateway configs
- Copies skills, memories, checkpoints, cron
- Cleans up

After this, run the Hermes installer — it should skip the setup wizard since config already exists.

### Backup (run on OLD VPS before migrating)
```bash
~/hermes-backup/backup-hermes.sh
```
This automatically:
- Cleans old backup data
- Copies config.yaml, .env, auth.json, SOUL.md
- Copies all sessions, skills, memories, checkpoints
- Copies cron jobs + outputs
- Copies gateway scripts + PM2 configs
- Commits and pushes to GitHub

### Restore (run on NEW VPS after fresh Hermes install)
```bash
~/hermes-backup/restore-hermes.sh
```
This automatically:
- Clones the backup repo (handles private repo auth)
- Stops running Hermes processes
- Restores ALL files to ~/.hermes
- Optionally restarts the gateway (systemd or PM2)
- Verifies everything is in place

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
