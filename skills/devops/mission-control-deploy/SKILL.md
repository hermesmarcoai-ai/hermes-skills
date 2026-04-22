---
name: mission-control-deploy
category: devops
description: Deploy Mission Control AI agent dashboard on a VPS
---

# Mission Control Deploy

Deploy Mission Control dashboard (builderz-labs) on a VPS — clone, build, configure, register agent.

## Steps

### 1. Clone
```bash
cd /root && git clone https://github.com/builderz-labs/mission-control.git
cd mission-control
```

### 2. Install Dependencies
```bash
pnpm install
```

### 3. Check Prerequisites
- Node.js >= 22 required. If missing: install via nvm or direct install.
- pnpm must be available. `corepack enable pnpm` or `npm i -g pnpm`.

### 4. Handle Out of Memory (Common on VPS with ≤4GB RAM)
If build gets killed (exit 137):
```bash
fallocate -l 4G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile
```

### 5. Build
```bash
NODE_OPTIONS="--max-old-space-size=4096" pnpm build
```

### 6. Configure .env
```bash
AUTH_SECRET=$(openssl rand -base64 32)
cat > .env <<EOF
PORT=3000
AUTH_USER=<admin-username>
AUTH_PASS=<admin-password>
API_KEY=<api-key-for-headless-access>
NEXT_PUBLIC_GATEWAY_OPTIONAL=true
MC_ALLOW_ANY_HOST=true
AUTH_SECRET=${AUTH_SECRET}
EOF
```

**Key env vars:**
- `NEXT_PUBLIC_GATEWAY_OPTIONAL=true` — Run without gateway connection (VPS standalone)
- `MC_ALLOW_ANY_HOST=true` — Allow access from any host (needed for IP access). In production use `MC_ALLOWED_HOSTS` instead

### 7. Start
```bash
pnpm start -- -p 3000
```
Or for background: run in background process, verify with `ss -tlnp | grep 3000`

### 8. Register Agents
```bash
curl -s -X POST http://localhost:3000/api/agents/register \
  -H "Content-Type: application/json" \
  -H "x-api-key: <API_KEY>" \
  -d '{"name":"<agent-name>","role":"agent","description":"<description>"}'
```
Valid roles: `coder`, `reviewer`, `tester`, `devops`, `researcher`, `assistant`, `agent`

### 9. Access
- URL: `http://<VPS-IP>:3000/login`
- API docs: `http://<VPS-IP>:3000/api-docs` (Scalar UI)
- Setup (if not auto-seeded): `http://<VPS-IP>:3000/setup`

## Persistent Deployment (Production)

### Systemd Service
After building, create a systemd service for persistence across reboots:
```bash
cat > /etc/systemd/system/mission-control.service << 'EOF'
[Unit]
Description=Mission Control - AI Agent Orchestration Dashboard
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/mission-control
Environment=PATH=/root/.local/bin:/usr/local/bin:/usr/bin:/bin
Environment=NODE_ENV=production
# Standalone server is nested inside project dir
ExecStart=/root/.local/bin/node /root/mission-control/.next/standalone/mission-control/server.js
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
MemoryMax=2G

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload && systemctl enable mission-control && systemctl start mission-control
```

**CRITICAL: The `node` path** — find it with `which node` (it may be `/root/.local/bin/node`, not `/usr/bin/node`). The standalone server path is `.next/standalone/mission-control/server.js` (project name is a subdirectory inside standalone).

### Nginx Reverse Proxy
```bash
cat > /etc/nginx/sites-available/mission-control << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400s;
    }
}
EOF
ln -sf /etc/nginx/sites-available/mission-control /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx
```

**HTTPS**: Requires a domain name pointing to the VPS. Once you have one: `certbot --nginx -d your-domain.com`. Without a domain, only HTTP is possible.

## Memory Sync (Obsidian → Mission Control)
Mission Control has a built-in memory FTS index. Sync your Obsidian vault:
```python
# Save to /root/mission-control/scripts/obsidian-memory-sync.py
# Then run: python3 /root/mission-control/scripts/obsidian-memory-sync.py
```
Uses direct SQLite insert into `memory_fts` table for all `.md` files in vault, execution/, directives/, and memory/ directories.

## Heartbeat Monitoring
```bash
# Every 5 minutes (crontab) sends heartbeat to MC API
*/5 * * * * /root/mission-control/scripts/heartbeat-runner.sh >/dev/null 2>&1
```
Heartbeat script sends CPU/mem/disk/uptime metrics to `/api/agents/{name}/heartbeat`.

## Alert Bridge (Discord Webhook)
```bash
# Every 15 minutes checks MC DB for offline agents, failed tasks, disk >90%
*/15 * * * * /root/mission-control/scripts/discord-bridge-cron.sh >/dev/null 2>&1
```
Requires `DISCORD_WEBHOOK_URL` env var. Sends embed to Discord if issues detected.

## Backup Integration
Add MC database to existing backup script:
```bash
# Append to your backup script:
cp -r /root/mission-control/.data/ /your-backup-dir/mission-control/.data/
```

## Mission Control ↔ Hermes Integration (v2.0.1)

Source: https://github.com/builderz-labs/mission-control
Install location: /tmp/mission-control (dev) or /root/mission-control (prod)
Admin created: marco / hermes_mc_2026!
Hermes registered as agent (ID: 3, role: agent, status: idle)
Public URL: http://<VPS-IP>:3000

### Bidirectional Task Bridge
Hermes polls MC for assigned tasks and reports completion:
```python
import requests, time, json

MC_API = "http://localhost:3000/api"
AGENT_ID = 3
API_KEY = "<your-mc-api-key>"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

def poll_tasks():
    resp = requests.get(f"{MC_API}/tasks?assigned_to=hermes&status=open", headers=HEADERS)
    if resp.status_code == 200:
        tasks = resp.json().get("tasks", [])
        for task in tasks:
            # Mark as in_progress
            requests.patch(f"{MC_API}/tasks/{task['id']}", json={"status": "in_progress"}, headers=HEADERS)
            # Execute task via Hermes tool calls (delegate, execute_code, etc.)
            result = execute_task(task)
            # Mark as completed
            requests.patch(f"{MC_API}/tasks/{task['id']}", json={"status": "completed", "result": json.dumps(result)}, headers=HEADERS)

# Run as background daemon or cron every 30s
while True:
    poll_tasks()
    time.sleep(30)
```

### Heartbeat Bridge (keeps Hermes "alive" on dashboard)
```bash
# Create /root/mission-control/scripts/heartbeat-hermes.sh
#!/bin/bash
curl -s -X POST http://localhost:3000/api/agents/hermes/heartbeat \
  -H "Authorization: Bearer $MC_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"cpu": $(top -bn1 | grep "Cpu(s)" | awk "{print \$2}"), "mem": $(free | grep Mem | awk "{print \$3/\$2*100}"), "status": "online"}'
```

### Webhook MC → Hermes
When a new task is created in MC, POST to a Hermes endpoint to trigger immediate execution (eliminates polling). This requires a Hermes webhook listener — see `webhook-subscriptions` skill.

### Token Tracking Integration
After each Hermes session, POST token usage to MC:
```python
requests.post(f"{MC_API}/tasks/{task_id}/cost", headers=HEADERS, json={
    "input_tokens": input_tokens,
    "output_tokens": output_tokens,
    "cost_usd": cost
})
```

### Skills Hub Bidirectional Sync
Mission Control's Skills Hub can mirror `.hermes/skills/`:
```bash
# Sync Hermes skills into MC's skills database
for skill_dir in ~/.hermes/skills/*/; do
    skill_name=$(basename "$skill_dir")
    curl -s -X POST http://localhost:3000/api/skills \
      -H "Authorization: Bearer $MC_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"name\": \"$skill_name\", \"source\": \"hermes\", \"path\": \"$skill_dir\"}"
done
```

## Pitfalls
- **Exit code 137 during build** — OOM killer. Add 4GB swap: `fallocate -l 4G /swapfile && chmod 600 /swapfile && mkswap /swapfile && swapon /swapfile`
- **Multiple lockfiles warning** — Non-fatal. Remove unused lockfile or set `turbopack.root` in next.config
- **better-sqlite3 version mismatch** — `pnpm rebuild better-sqlite3`
- **Standalone path** — `.next/standalone/mission-control/server.js` (project name is a subdirectory)
- **`node` path** — Not always `/usr/bin/node`. Use `which node` to find it. Common: `/root/.local/bin/node`
- **AUTH_USER/AUTH_PASS in .env doesn't work after first setup via /setup** — If you already visited /setup, the admin user was created in DB and env vars are ignored. **Fix:** Update password directly in SQLite:
  ```bash
  # Generate new hash with same scrypt algorithm the app uses
  NEW_HASH=$(node -e "
    const crypto = require('crypto');
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.scryptSync('YourPassword', salt, 32, { N: 65536, maxmem: 128*65536*8*2 }).toString('hex');
    console.log(salt + ':' + hash);
  ")
  sqlite3 /root/mission-control/.data/mission-control.db "UPDATE users SET password_hash='$NEW_HASH' WHERE username='youruser';"
  ```
- **MC_COOKIE_SECURE=1 blocks HTTP access** — Only set this when using HTTPS. For HTTP-only, don't set it.