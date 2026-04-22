---
name: obsidian-hermes-memory
description: Manage Marco's Obsidian Knowledge Graph / Memory Vault synced via GitHub. Read, create, update vault files, and push changes so they sync to Marco's Macbook.
---

# Obsidian Hermes Memory Vault

## Overview

Marco's persistent memory system backed by Obsidian notes synced via GitHub.

- **Repo:** https://github.com/marcoolibusiness-oss/marcoolibusiness-obsidian-vault
- **Local path on server:** `/home/Obsidian-Vault/`
- **User device:** Macbook (macOS), Obsidian desktop app
- **Sync:** Obsidian Git plugin (pull on startup, auto-backup every 5 min)

## Vault Structure

```
marcoolibusiness-obsidian-vault/
├── MEMORY.md              # ★ Distilled long-term memory (high-signal facts)
├── USER.md                # Marco's profile, traits, goals, constraints
├── AGENTS.md              # How Hermes operates, memory protocol, tool rules
├── SOUL.md                # AI persona & tone guidelines
├── HEARTBEAT.md           # Proactive maintenance checklist
├── memory/                # Daily session logs (YYYY-MM-DD.md)
├── second-brain/
│   ├── README.md          # Index & navigation
│   └── concepts/          # Knowledge base concept notes
├── directives/            # SOPs and workflows
└── skills/                # Hermes skills (adapted from upstream)
```

## When to Use

- User asks to check/write/update Obsidian notes
- Session ends → create/update daily log in `memory/`
- New durable knowledge discovered → update `MEMORY.md` or add to `second-brain/`
- User shares research/ideas → save to appropriate concept note
- Proactive: update `MEMORY.md` after meaningful conversations

## Workflow

1. Clone/pull repo to server temp if not already at `/home/Obsidian-Vault/`
2. Read existing file if updating
3. Create or modify markdown files as needed
4. Use wiki-links `[[filename]]` (without .md) to maintain graph connections
5. `git add -A && git commit -m "..." && git push`

## Git Commands

```bash
cd /home/Obsidian-Vault/
git pull origin main          # Get latest changes from Marco
git add -A
git commit -m "Description"
git push origin main           # Push to Marco's Mac (auto-pulled by Obsidian Git plugin)
```

## Installed Obsidian Plugins (Marco's Mac)
- **Obsidian Git** (denolehov) — sync automation
- **Calendar** — daily note calendar view
- **QuickAdd** — rapid capture
- **Kanban** — project management boards

## Pitfalls
- Obsidian is a **local desktop app** on Marco's Mac — not accessible from server directly
- All interaction happens through GitHub push/pull
- If push fails, check `git status` and resolve conflicts before forcing
- Marco may write notes locally between sessions — always `git pull` before editing