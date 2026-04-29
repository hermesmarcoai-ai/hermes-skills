---
name: surface-gui-app-launch
description: Launch GUI applications on Surface Pro 3 (LXQt Ubuntu) from a root/hermes terminal context
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [gui, firefox, electron, surface, desktop, launch]
    category: system-maintenance
---

# Surface GUI App Launch

How to launch graphical applications on the Surface Pro 3 desktop from a root or hermes terminal session where the app must appear on the user's active LXQt session.

## The Problem

Running a GUI app as root or in a hermes context doesn't automatically connect to the user's active X11 session (`:0`). The app either silently fails or the window doesn't appear on the correct display.

## The Working Pattern

```bash
sudo -u marco env DISPLAY=:0 HOME=/home/marco DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus <command>
```

### Environment variables explained

| Variable | Value | Purpose |
|----------|-------|---------|
| `DISPLAY` | `:0` | X11 display of the active LXQt session |
| `HOME` | `/home/marco` | Ensures correct home for configs, profiles |
| `DBUS_SESSION_BUS_ADDRESS` | `unix:path=/run/user/1000/bus` | D-Bus session bus for the logged-in user |
| `sudo -u marco` | — | Run as the actual desktop user (marco), not root |

### Finding the correct DBus path

If user ID is not 1000, find the right bus path:
```bash
ls /run/user/
```

## Firefox on Surface

`/usr/bin/firefox` is a snap wrapper that fails with "cannot communicate with server". Use `firefox-esr` directly:

```bash
sudo -u marco env DISPLAY=:0 HOME=/home/marco DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus firefox-esr --new-window https://example.com
```

To open a URL in an existing Firefox instance (if already running):
```bash
sudo -u marco env DISPLAY=:0 HOME=/home/marco DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus firefox-esr --new-tab https://example.com
```

## Electron Apps on Surface

Electron apps (like Space Agent) also need this pattern:

```bash
sudo -u marco env DISPLAY=:0 HOME=/home/marco DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus ~/.space-agent/space-agent --no-sandbox
```

## AppImage with FUSE errors

If an AppImage fails with `dlopen(): error loading libfuse.so.2`, extract instead of installing FUSE:

```bash
chmod +x SomeApp.AppImage
./SomeApp.AppImage --appimage-extract
# Extracts to ./squashfs-root/
# Run the extracted binary directly:
./squashfs-root/<extracted-binary>
```

Then copy to a permanent location and create a `.desktop` launcher if needed.

## Creating a .desktop launcher

```ini
[Desktop Entry]
Name=App Name
Exec=/path/to/app --no-sandbox %U
Terminal=false
Type=Application
Icon=/path/to/icon.png
Categories=Development;
```

```bash
mkdir -p ~/.local/share/applications/
mv myapp.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

## Troubleshooting

- App doesn't appear → Check `ps aux | grep <appname>` to confirm it's running
- Silent crash → Check `journalctl --user -xe 2>/dev/null` or look for crash logs
- Wrong display → Verify with `echo $DISPLAY` and `w` to see active sessions
- DBus error → Verify bus socket exists: `ls /run/user/1000/bus`
