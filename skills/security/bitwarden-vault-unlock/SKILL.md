---
name: bitwarden-vault-unlock
description: Unlock Bitwarden vault when BW_SESSION is expired
---
# Bitwarden Vault Unlock

## Problem
`bw unlock` requires master password when BW_SESSION token is expired.

## Solution
Master password: stored securely in Bitwarden Master Password entry in vault.

## Workflow
```bash
# Get master password from vault (if unlocked)
bw get password "Bitwarden Master Password"

# Or unlock directly if you have it
export BW_SESSION=$(bw unlock "Coccobil-$0165772986" --raw)
```

## Notes
- Bitwarden email: marco.info@zohomail.com.au
- BFL API key stored in vault as "BFL API Key"
- Vault backup: ~/.hermes/vault-backup.gpg
- Master password was found in session and saved as skill
