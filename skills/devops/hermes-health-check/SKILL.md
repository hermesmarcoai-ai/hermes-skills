---
name: hermes-health-check
description: Health check process for the Hermes system.

---

# Hermes Health Check Skill

## Overview
A skill used for performing health checks on the Hermes system and reporting results in a connected messaging platform.

## Steps
1. **List Cron Jobs**: Use `cronjob` tool to list all scheduled jobs and check for failures in the last 24 hours.
2. **Check Gateway Status**: Verify if the gateway service is actively running using the command `systemctl is-active hermes-gateway.service`.
3. **Check Disk Usage**: Use the command `df -h /` and `du -sh /root/.hermes/` to assess disk space usage.
4. **Delivery Conditions for Notifications**: Notify on Discord if:
   - Any cron job failed in the last 24 hours.
   - The gateway is not running.
   - Disk usage is above 80%.
5. **Status Confirmation**: If all systems are fine, send concise confirmation of system health via Telegram (user ID 1358373153).

## Notes
This skill outlines the process followed in the recent task to ensure that all core systems are operating correctly, reporting issues when detected.