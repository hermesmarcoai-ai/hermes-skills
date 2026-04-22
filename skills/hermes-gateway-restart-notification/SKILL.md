---
name: hermes-gateway-restart-notification
summary: Handle notifications for the Hermes gateway restart status
description: This skill manages the notification process for when the Hermes gateway is restarted.
---

# Hermes Gateway Restart Notification

## Summary
This skill outlines the process for checking the status of the Hermes gateway service and notifying users through Telegram if the gateway was recently restarted.

## Steps
1. **Check Gateway Status**: Use the command `systemctl status hermes-gateway.service | head -15` to check the current status of the Hermes gateway service.
2. **Analyze Output**: Look for the 'active' or 'started' time in the output to determine if the gateway was restarted within the last 30 minutes.
3. **Send Notification**: If the gateway was restarted recently (within 30 minutes), send a message via Telegram:
   - Message: "Gateway riavviato alle [timestamp]. La sessione Telegram e' stata resettata. Se hai problemi, riavvia la chat."
4. **Exit Silently**: If the gateway has been running for longer than 30 minutes or was not recently restarted, exit without sending any message.

## Tools Used
- Terminal commands for system status checks.
- Telegram API for messaging.

## Important Notes
- Ensure that the time is accurately captured from the command output.
- Be cautious of the active duration to avoid sending unnecessary notifications.

## Learning Points
- This skill encapsulates the knowledge gained from effectively checking service status and managing notifications based on time conditions.