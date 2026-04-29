---
name: ollama-open-webui-local-install
description: Install Ollama (local bare-metal) + Open WebUI (docker) on Ubuntu/Linux when official install script fails or sudo unavailable. Covers tmpfs /tmp space issues, tar structure quirks, Docker networking, and standalone docker-compose.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [ollama, open-webui, docker, local-llm, installation]
---

# Ollama + Open WebUI — Local Install Guide

## Context
Installing Ollama (bare-metal, local) + Open WebUI (docker) on Ubuntu when:
- Official `curl -fsSL https://ollama.com/install.sh | sh` fails (needs sudo password)
- `/tmp` is a tmpfs (RAM disk) with limited space — filling it breaks downloads
- `docker compose` plugin not available (use standalone `docker-compose` binary)
- Open WebUI in docker needs to connect to Ollama on host network

## Architecture
```
Surface Pro 3 (Ubuntu):
  ├── Ollama (bare-metal)  →  localhost:11434
  └── Docker: Open WebUI   →  localhost:3000  →  host.docker.internal:11434
```

## Step-by-Step

### 1. Download Ollama binary to ~/tmp (NOT /tmp)
```bash
mkdir -p ~/tmp
cd ~/tmp
curl -fSL "https://github.com/ollama/ollama/releases/download/v0.21.2/ollama-linux-amd64.tar.zst" -o ollama.tar.zst
```

> ⚠️ `/tmp` is a tmpfs (RAM disk). The ~2GB archive will fill it and cause "No space left on device" errors. Always use `~/tmp` for large files.

### 2. Extract
```bash
cd ~/tmp
tar -I zstd -xf ollama.tar.zst
# Binary is at: ~/tmp/bin/ollama  (NOT ~/tmp/ollama)
```

### 3. Install to ~/bin (no sudo needed)
```bash
mkdir -p ~/bin
cp ~/tmp/bin/ollama ~/bin/ollama
chmod +x ~/bin/ollama
export PATH="$HOME/bin:$PATH"  # add to ~/.bashrc too
```

### 4. Start Ollama
```bash
nohup $HOME/bin/ollama serve > /tmp/ollama.log 2>&1 &
# Verify:
curl localhost:11434/api/tags
```

### 5. Pull a model (small, RAM-friendly)
```bash
$HOME/bin/ollama pull qwen2.5:1.5b   # ~1GB, good for 8GB RAM systems
# Or: $HOME/bin/ollama pull llama3.2:1b
```

### 6. Configure Open WebUI (docker)

Create `~/open-webui/.env`:
```bash
OLLAMA_DOCKER_TAG=latest
WEBUI_DOCKER_TAG=main
OPEN_WEBUI_PORT=3000
WEBUI_SECRET_KEY=your-secret-key
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_API_BASE_URL=http://host.docker.internal:11434/api
```

Create `~/open-webui/docker-compose.yaml`:
```yaml
services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:${WEBUI_DOCKER_TAG-main}
    container_name: open-webui
    volumes:
      - open-webui:/app/backend/data
    ports:
      - ${OPEN_WEBUI_PORT-3000}:8080
    environment:
      - 'OLLAMA_BASE_URL=http://host.docker.internal:11434'
      - 'OLLAMA_API_BASE_URL=http://host.docker.internal:11434/api'
      - 'WEBUI_SECRET_KEY=${WEBUI_SECRET_KEY}'
    extra_hosts:
      - host.docker.internal:host-gateway
    restart: unless-stopped

volumes:
  open-webui: {}
```

### 7. Start Open WebUI

Find docker-compose (standalone):
```bash
which docker-compose  # usually ~/.local/bin/docker-compose on systems without docker compose plugin
/home/marco/.local/bin/docker-compose up -d
```

Wait ~60s for initialization, then:
```bash
curl http://localhost:3000/api/version  # should return {"version":"0.x.x",...}
```

### 8. Auto-start Ollama (optional systemd user service)
```bash
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/ollama.service << 'EOF'
[Unit]
Description=Ollama Local LLM Server

[Service]
ExecStart=/home/marco/bin/ollama serve
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable --now ollama
```

## Troubleshooting

### Ollama serve fails to bind port
```bash
pgrep -a ollama  # check if already running
pkill -f ollama  # kill existing instance
```

### Docker can't reach Ollama
- Verify `extra_hosts: host.docker.internal:host-gateway` in compose
- From inside container: `curl http://host.docker.internal:11434/api/tags`

### Open WebUI API returns "Not authenticated"
- Normal — UI requires auth but API endpoints are available
- Register at `http://localhost:3000` for first account

### docker-compose command not found
```bash
# Find standalone docker-compose
find ~ -name "docker-compose" -type f 2>/dev/null
# Or install: pip install docker-compose
```

## Verification Checklist
- [ ] `curl localhost:11434/api/tags` → shows installed models
- [ ] `docker ps` → open-webui status "healthy"
- [ ] `curl localhost:3000/api/version` → returns version JSON
- [ ] Open `http://localhost:3000` in browser → WebUI loads
