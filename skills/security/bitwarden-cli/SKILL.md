---
name: bitwarden-cli
description: Bitwarden CLI per credential management — usa BW_SESSION dal bashrc
---

# Bitwarden CLI (bw)

CLI ufficiale Bitwarden installato in `~/.local/bin/bw`.

## Setup (già fatto)

La sessione è salvata in `~/.bashrc`. Ogni nuova sessione terminal:

```bash
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
```

Se il vault è bloccato:
```bash
bw unlock
# Inserire master password → copia la sessione in ~/.bashrc
```

## Comandi utili

```bash
# Sync vault
bw sync

# Cercare un item
bw list items --search "nome"

# Username
bw get username "nome"

# Password (copia in clipboard 8min)
bw get password "nome"

# Tutto l'item JSON
bw get item "nome"

# Copiare password
echo $(bw get password "nome") | xclip -sel clip
```

## Machine-to-Machine Unlock (without interactive terminal)

When running in a non-interactive context (script, subagent, cron) and session is expired:

```bash
# 1. Unlock with master password — outputs "export BW_SESSION=..."
BW_MASTER_PASSWORD='Coccobil-$0165772986' bw unlock --passwordenv BW_MASTER_PASSWORD

# 2. Extract raw session token from output
SESS=$(BW_MASTER_PASSWORD='Coccobil-$0165772986' bw unlock --passwordenv BW_MASTER_PASSWORD 2>/dev/null | grep 'export BW_SESSION' | cut -d'"' -f2)

# 3. Use --session flag with raw token (NOT env var for subsequent commands)
bw list items --session "$SESS" --search "Surface Pro 3"
```

**Key insight**: `export BW_SESSION=...` in a subshell doesn't propagate to all bw subcommands reliably. Always use `--session "$SESS"` explicitly on each command.

## Session Management

The session token expires periodically. Two recovery options:

### Option 1: User shares session via chat
User runs `bw unlock` locally, gets BW_SESSION token, pastes it in chat. Use with `--session` flag:
```bash
bw list items --search "name" --session 'hvmPvHrpJShs2jqof...'
```

### Option 2: Unlock with Master Password
If session is expired and user can't unlock, they must run `bw unlock` in a terminal, then copy new session to `~/.bashrc`.

### Key lessons
- `--session` flag bypasses `BW_SESSION` env variable — useful when env var is stale
- Bitwarden CLI has a bug with `bw edit item` — item updates fail with TypeError on some items
- `bw get item <name>` works; `bw get item <id>` may fail
- Password retrieval: `bw get password <name> --session <S> --raw | tail -1` strips newlines cleanly
- **Email per Marco**: `marco.info@zohomail.com.au` (non `marco.belladati@icloud.com`)
- **Login flow**: `bw login <email> <password>` → output contiene `BW_SESSION="token..."` → `export BW_SESSION="..."`
- **Entry "Surface Pro 3"** contiene la password sudo del Surface (password: `Coccobil-$1990`)



## Bug noto: `bw edit item` fallisce

Il comando `bw edit item <id> <encodedJson>` ha un bug nel CLI Bitwarden:
- Passando un JSON parziale (solo i campi da modificare) → errore `TypeError: Cannot read properties of undefined (reading 'uris')`
- Il CLI cerca di leggere `login.uris` dall'oggetto originale prima del merge, che è undefined se non incluso

**Soluzione**: Usa sempre il Web Vault (vault.bitwarden.com) per modifiche manuali, oppure passa l'item JSON completo altrimenti il merge fallisce. Non c'è workaround lato CLI — il bug è nel codice Node del CLI stesso.

## Piping sudo password in non-TTY environments

Quando Hermes usa sudo in script Python o pipe, il `$` nella password può causare problemi di shell expansion. Pattern affidabile:

```bash
SUDO_PASS='Coccobil-$1990'
echo "$SUDO_PASS" | sudo -S <comando>
```

O in Python:
```python
import subprocess
password = 'Coccobil-$1990'  # $ non causa problemi in Python strings
result = subprocess.run(['sudo', '-S', 'id'], input=password + '\n', text=True, capture_output=True)
```

**Nota**: `sudo -S` legge da stdin, non funziona se il processo non ha TTY. In questo caso, il password piping funziona ma solo se il processo ha accesso a stdin.

La sessione può essere passata in due modi:
```bash
# Via env (aggiorna ~/.bashrc)
export BW_SESSION="token"

# Via flag --session (più sicuro per scripting)
bw get item "nome" --session "token" --raw
```
