---
name: space-agent-setup
description: Install and run Space Agent on Surface Pro 3 — release AppImage or dev clone, user creation, startup
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [space-agent, electron, ai-agent, desktop]
    category: autonomous-ai-agents
---

# Space Agent Setup

Space Agent (agent0ai/space-agent) is a browser-first AI agent runtime. Available as:
- **Release**: pre-built AppImage (v0.64+)
- **Dev**: git clone + npm install

## Release Install (Surface)

### 1. Download AppImage

```bash
curl -sL "https://github.com/agent0ai/space-agent/releases/download/v0.64/Space-Agent-0.64-linux-x64.AppImage" -o ~/Downloads/space-agent.AppImage
chmod +x ~/Downloads/space-agent.AppImage
```

### 2. Extract (FUSE workaround)

Surface Pro 3 lacks FUSE. Extract instead of running directly:

```bash
cd ~/Downloads
./space-agent.AppImage --appimage-extract
# Creates squashfs-root/ in current directory
```

### 3. Move to permanent location

```bash
mkdir -p ~/.space-agent
cp -r squashfs-root/* ~/.space-agent/
chmod +x ~/.space-agent/space-agent
```

### 4. Run

```bash
sudo -u marco env DISPLAY=:0 HOME=/home/marco DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus ~/.space-agent/space-agent --no-sandbox
```

See `surface-gui-app-launch` skill for the full sudo env pattern.

## Dev Install

```bash
git clone https://github.com/agent0ai/space-agent.git ~/space-agent-dev
cd ~/space-agent-dev
npm install
```

First admin user:
```bash
cd ~/space-agent-dev
node space user create admin --password "change-me-now" --full-name "Admin" --groups _admin
```

Start dev server:
```bash
cd ~/space-agent-dev
PORT=3000 node space serve
```

## Desktop Launcher

```ini
# ~/.local/share/applications/space-agent.desktop
[Desktop Entry]
Name=Space Agent
Exec=/home/marco/.space-agent/space-agent --no-sandbox %U
Terminal=false
Type=Application
Icon=/home/marco/.space-agent/space-agent.png
Categories=Development;
```

```bash
mkdir -p ~/.local/share/applications/
mv space-agent.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

## Notes

- Space Agent is an Electron app (~1.4GB RAM when running)
- AppImage extracted to `/tmp/squashfs-root/` won't survive reboot — always use `~/.space-agent/`
- First run requires creating an admin user via CLI before login works
