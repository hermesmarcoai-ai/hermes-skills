# Hermes Agent Backup - Marco Olivero

Essential backup of Hermes Agent configuration, custom skills, and scripts.

## Contents
- `skills_backup/` - 19 custom skills created for Hermes Agent
- `scripts_backup/` - Utility scripts (watch-video.py for YouTube analysis)
- `cron_backup/` - Scheduled job configurations

## Skills Included
minimax-xlsx, minimax-pdf, minimax-docx, minimax-music-gen, video-watcher, web-scraper, open-interpreter, image-gen-prompt, research-agent, puppeteer-screenshot, auto-skills-helper, memory-manager, task-orchestrator, meeting-notes, social-media-optimizer, code-review-assistant, seo-content-strategy, api-integration-helper, data-visualization, documentation-writer, tdd-assistant, best-practices

## To Restore
```bash
cp -r skills_backup/* ~/.hermes/skills/
cp scripts_backup/* ~/.hermes/scripts/
cp cron_backup/* ~/.hermes/cron/
```
