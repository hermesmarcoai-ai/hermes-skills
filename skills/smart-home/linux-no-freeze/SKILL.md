---
name: linux-no-freeze
description: Prevent Ubuntu Linux desktop from suspending, blanking, or hibernating
---
# Linux No-Freeze / Prevent Sleep

Prevent an Ubuntu Linux desktop from suspending, blanking, or hibernating.

## Approach (tested on Ubuntu 24.04 / GNOME on Surface-like hardware)

```bash
# 1. Disable X screen blanking and DPMS
xset s off
xset -dpms
xset s noblank

# 2. Allow screen to turn off (without suspending)
xset +dpms           # re-enable DPMS
xset dpms 0 0 60    # screen off in 60s (adjust: 60=1min, 300=5min)

# 3. GNOME power settings (gsettings — works without sudo)
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'nothing'
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-battery-type 'nothing'
gsettings set org.gnome.desktop.session idle-delay 0

# 4. Ensure settings persist on reboot via cron @reboot
# (crontab -e → @reboot bash ~/.hermes/scripts/no-freeze.sh)
mkdir -p /etc/systemd/logind.conf.d/
printf '[Login]\nHandlePowerKey=ignore\nHandleSleepKey=ignore\nHandleHibernateKey=ignore\nHandleSuspendKey=ignore\nIdleAction=ignore\n' > /tmp/99-no-suspend.conf
pkexec tee /etc/systemd/logind.conf.d/99-no-suspend.conf < /tmp/99-no-suspend.conf
# If pkexec fails: use graphical auth dialog or manually add to /etc/polkit-1/localauthority/50-local.d/

# 4. Restart logind (without full sudo)
pkexec systemctl restart systemd-logind
```

## Pitfalls

- `sudo` requires password — use `pkexec` for single commands, or `gsettings` which doesn't need sudo for user prefs
- `/etc/systemd/logind.conf.d/` may not exist — create it first with `mkdir -p`
- `crontab -l | grep ...; echo ... | crontab -` **replaces** the entire crontab — use `(crontab -l; echo "new") | crontab -` to append safely
- On Surface devices, lid events and power key can still trigger suspension — all Handle* keys must be set to `ignore`
- `powercfg` is a Windows tool, not available on Linux

## Verification

```bash
xset q | grep "Screen Saver"   # should show timeout: 0
xset q | grep "DPMS is"        # should show "DPMS is Disabled"
systemctl status systemd-logind  # should show logind.conf.d/99-no-suspend.conf loaded
```
