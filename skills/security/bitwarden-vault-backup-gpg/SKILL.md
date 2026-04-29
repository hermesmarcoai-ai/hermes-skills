---
name: bitwarden-vault-backup-gpg
description: Extract Bitwarden CLI vault items and encrypt to AES256 GPG backup file
triggers:
  - backup bitwarden vault
  - extract passwords from bitwarden
  - save vault backup gpg
---

# Bitwarden Vault Backup to GPG

Backup all Bitwarden CLI vault items to an AES256 GPG-encrypted file.

## When to Use
- Extract all passwords/logins from Bitwarden CLI for emergency backup
- Before vault changes (password rotation, item deletion)
- When desktop GUI session is unlocked but CLI session is not

## Important Gotchas
1. **CLI session is SEPARATE from desktop GUI** — `bw unlock` in CLI does NOT share session with Bitwarden desktop/app GUI. Must use `bw login` for CLI access.
2. **Shell `$` interpolation** — if password contains `$`, use `printf '%s' 'password' | BW_MASTER_PASSWORD_FILE=/dev/stdin bw login email`
3. **Session in gateway logs** — Discord/Telegram messages processed by the gateway appear in `~/.hermes/logs/agent.log` with plaintext content.
4. **File permissions** — GPG output must go to `~/.hermes/` (Marcos user), not `/root/.hermes/`

## Step-by-Step

### 1. Unlock vault via CLI
```bash
printf '%s' 'MASTER_PASSWORD' | BW_MASTER_PASSWORD_FILE=/dev/stdin bw login email@example.com
```
Output: `BW_SESSION="..."` — copy the session key.

### 2. Export + Encrypt (Python, single pipeline)
```python
import subprocess, json, os

session = "SESSION_KEY"
result = subprocess.run(["bw", "list", "items", "--session", session], capture_output=True, text=True)
items = json.loads(result.stdout)
lines = []
for item in items:
    name = item.get('name', '')
    login = item.get('login', {})
    username = login.get('username', '')
    password = login.get('password', '')
    uri = (login.get('uris') or [{}])[0].get('uri', '') if login.get('uris') else ''
    lines.append(f"{name}\t{username}\t{password}\t{uri}")

vault_text = '\n'.join(lines)
out_path = os.path.expanduser("~/.hermes/vault-backup.gpg")
proc = subprocess.run(
    ["gpg", "--batch", "--yes", "--passphrase", "MASTER_PASSWORD",
     "--symmetric", "--cipher-algo", "AES256", "-o", out_path],
    input=vault_text.encode()
)
os.chmod(out_path, 0o600)
print(f"Backup: {os.path.getsize(out_path)} bytes at {out_path}")
```

### 3. Verify
```bash
gpg --batch --yes --passphrase "MASTER_PASSWORD" -d ~/.hermes/vault-backup.gpg
```

### 4. Lock vault
```bash
bw lock --session SESSION_KEY
```

## Current Backup
- File: `~/.hermes/vault-backup.gpg`
- Items: 9
- Updated: 2026-04-27

## Risks
- GPG passphrase = master password (no defense in depth)
- Gateway logs contain plaintext messages with passwords
- Session key visible in process arguments
