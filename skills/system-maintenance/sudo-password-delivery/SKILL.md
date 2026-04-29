---
name: sudo-password-delivery
description: How to run sudo commands in non-TTY environments (Hermes terminal, cron, scripts)
version: 1.1
author: Marco
metadata:
  hermes:
    tags: [sudo, terminal, automation, security]
    category: system-maintenance
---

# Sudo Password Delivery in Non-TTY Contexts

## The Problem

`sudo -S` (read password from stdin) **does NOT work** in Hermes terminal environment because:
- Commands run without an attached TTY
- Password piped to stdin never reaches sudo
- Error: "sudo: a password is required" or password not received

```bash
# FAILS - password not received
echo 'password' | sudo -S whoami

# FAILS - same issue  
sudo -S <<< 'password' whoami

# FAILS - Python subprocess also doesn't work
python3 -c "subprocess.run(['sudo', '-S', 'id'], input='password\n')"
```

## Verified Working Solutions

### 1. Passwordless Sudo for Specific Commands (Recommended)

Configure in `/etc/sudoers.d/`:
```bash
marco ALL=(ALL) NOPASSWD: /path/to/command
```

### 2. Use Leo/OpenClaw via Interop (for Surface)

Ask the other agent to run the command:
```bash
curl -X POST "http://127.0.0.1:18900/broadcast?from=hermes" \
  -H "Content-Type: application/json" \
  -d '{"type": "request", "text": "your sudo command here"}'
curl "http://127.0.0.1:18900/poll?agent=hermes"
```

### 3. Use pkexec (graphical password prompt)

```bash
pkexec dpkg -i /path/to/package.deb
```
Opens a graphical authentication dialog — works **only if a GUI user is physically present**. Tested on Surface: times out after ~120s when no user is at the display.

### 4. Bitwarden Vault

If the vault is already unlocked (BW_SESSION valid), retrieve stored passwords:
```bash
export BW_SESSION='<token_from_bashrc>'
bw unlock --check   # 0 = unlocked, 1 = locked

# If locked, the stored session has expired — must ask user for master password
# If unlocked, search:
bw list items --search "Surface Pro 3"
```

**Key finding:** BW_SESSION stored in `~/.bashrc` expires. Surface vault was found **locked** — session invalid. Requires master password to unlock fresh.

### 5. SSH Loopback (if SSH configured)

```bash
ssh -o StrictHostKeyChecking=no localhost "sudo systemctl stop open-webui"
```

## Decision Tree (Surface Pro 3)

1. Can user confirm they are at the machine? → Use `pkexec`
2. Is Bitwarden vault already unlocked? → Use `bw` to retrieve stored sudo password
3. Need passwordless sudo? → Ask user to configure `/etc/sudoers.d/marco` manually
4. Is Leo/OpenClaw running on Surface? → Delegate via interop API
5. None of the above? → Ask user directly

## Surface Pro 3 Sudo Password

Password: `Coccobil-$1990` (saved in Bitwarden as "Surface Pro 3")

On Surface (where sudo -S may work with terminal attached):
```bash
echo 'Coccobil-$1990' | sudo -S apt update
```

## Security Note

Never store sudo passwords in scripts or memory. For trusted machines like Surface, configure passwordless sudo for the specific system management commands needed (systemctl, service management, etc.).
