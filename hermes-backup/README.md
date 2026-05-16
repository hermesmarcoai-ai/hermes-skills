# Hermes Agent Backup - Marco Olivero

Complete backup of custom skills, scripts, and configuration for Hermes Agent.

## Quick Restore on New VPS
```bash
git clone https://github.com/hermesmarcoai-ai/hermes-skills.git /tmp/hermes-backup
/tmp/hermes-backup/scripts/restore.sh
```

## What's Included
- **19 Custom Skills** - video-watcher, minimax-*, web-scraper, memory-manager, etc.
- **watch-video.py** - YouTube analysis script with frame extraction + captions
- **Cron jobs configuration** - Scheduled tasks setup
- **Restore script** - Fully automated restore for new VPS

## Skills List
- minimax-docx, minimax-pdf, minimax-xlsx, minimax-music-gen
- video-watcher, web-scraper, open-interpreter, image-gen-prompt
- research-agent, puppeteer-screenshot, auto-skills-helper, memory-manager
- task-orchestrator, meeting-notes, social-media-optimizer
- code-review-assistant, seo-content-strategy, api-integration-helper
- data-visualization, documentation-writer

## After Restore
1. `pip install agentmemory --break-system-packages`
2. Configure `~/.hermes/dotfiles/config/config.yaml`
3. `hermes restart`
