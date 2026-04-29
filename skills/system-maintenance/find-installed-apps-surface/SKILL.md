---
name: find-installed-apps-surface
description: Find installed applications on Marco's Surface Pro 3 (Lubuntu Linux)
---

# Find Installed Applications on Surface (Lubuntu)

## Context
This Surface Pro 3 runs Lubuntu (Linux), not Windows. When looking for installed apps, use Linux package managers first, not Windows paths.

## How to Find Installed Apps

### 1. Check package managers first
```bash
snap list           # Snap packages (e.g. bitwarden, firefox)
flatpak list        # Flatpak packages
dpkg -l            # Debian packages
```

### 2. Find executables on PATH
```bash
which <app-name>   # e.g. which bitwarden
```

### 3. Search for app files
```bash
find ~/snap/<app>  # Snap apps are under ~/snap/
find ~/Downloads   # AppImage files
```

### 4. Desktop shortcuts (`.desktop` files)
```bash
ls ~/Desktop/*.desktop
# Read existing ones as templates
cat ~/Desktop/qterminal.desktop
```

## Bitwarden on This System
- Installed as: Snap package `bitwarden`
- Executable: `/snap/bin/bitwarden`
- To create desktop shortcut: write a `.desktop` file to `~/Desktop/` and `chmod +x`
- Icon cache: `~/.cache/gnome-software/`

## Key Realization
Marco's Surface Pro 3 is a Linux machine. Don't search for `.exe` or Windows paths like `C:\Users\...`.
