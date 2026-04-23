---
name: openclaw-configure-telegram-token
description: Configure Telegram bot token for OpenClaw gateway via systemd environment variable
triggers:
  - openclaw telegram token
  - configure openclaw telegram
  - openclaw channels add telegram timeout
---

## Steps

1. OpenClaw reads Telegram bot token from TELEGRAM_BOT_TOKEN environment variable (not CLI).
2. Edit the systemd service: ~/.config/systemd/user/openclaw-gateway.service
3. Add line: Environment=TELEGRAM_BOT_TOKEN=<your_token>
4. Reload and restart: systemctl --user daemon-reload && systemctl --user restart openclaw-gateway.service
5. Verify: curl https://api.telegram.org/bot<token>/getMe (should return bot info)
6. Check logs: tail -f /tmp/openclaw/openclaw-YYYY-MM-DD.log | grep telegram

## Notes

- openclaw channels add --channel telegram --token <token> CLI command times out (gateway RPC issue)
- Token is NOT stored in openclaw.json — read from env var at startup
- Env var approach survives service restarts
- OpenClaw also supports DISCORD_BOT_TOKEN for Discord
- Service file: /home/marco/.config/systemd/user/openclaw-gateway.service
- Log file: /tmp/openclaw/openclaw-YYYY-MM-DD.log
