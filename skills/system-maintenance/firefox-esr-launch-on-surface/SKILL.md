---
name: firefox-esr-launch-on-surface
description: Launch Firefox ESR on Surface Pro 3 (LXQt Ubuntu) — bypasses broken snap wrapper
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [firefox, surface, desktop, launch]
    category: system-maintenance
---

# Firefox ESR on Surface Pro 3

## Problem
`/usr/bin/firefox` is a snap wrapper that requires snapd/FUSE — neither is available or working on this Surface. Running it produces:
```
error: cannot communicate with server: Post "http://localhost/v2/snapctl": connection refused
ERROR: not connected to the gnome-42-2204 content interface.
```

## Solution
Use `firefox-esr` directly — the actual Firefox binary installed via apt.

### Launch on Surface desktop (LXQt)
```bash
sudo -u marco env DISPLAY=:0 HOME=/home/marco DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus /usr/bin/firefox-esr --no-sandbox [args]
```

### Desktop launcher (.desktop file)
Copy the system .desktop and patch Exec lines to use absolute path + --no-sandbox:
```
Exec=/usr/bin/firefox-esr --no-sandbox %u
```

Icon: `/usr/share/icons/hicolor/48x48/apps/firefox-esr.png`

### Key environment variables for GUI apps as root->user transition
- `DISPLAY=:0` — X display
- `HOME=/home/marco` — user home for profile/access
- `DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus` — session DBus

## Verification
```bash
/usr/bin/firefox-esr --version  # should print version
ps aux | grep firefox-esr        # should show running processes
```
