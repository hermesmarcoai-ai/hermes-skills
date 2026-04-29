---
name: pass-password-store
description: Linux password manager CLI — già installato sul Surface
---

# Password Store (pass) CLI

`pass` è il password manager Linux standard, già installato sul Surface.

## Comandi base

```bash
# Elencare password
pass

# Cercare
pass find "keyword"
pass grep "query"

# Mostrare password (copia in clipboard automaticamente, 45s)
pass show -c "social/twitter.com"
pass show "hermes/api-keys"        # vedere senza copiare

# Inserire nuova password
pass insert ".Label"               # modo interattivo (sicuro)
pass insert -m "Label"            # multilinea (note incluse)

# Generare password
pass generate "Label" 24
pass generate -c "Label" 24       # copia subito

# Eliminare
pass rm "Label"

# Backup (esporta in chiaro — usa con cautela)
pass git status
```

## Struttura consigliata per Marco

```
pass
├── discord/bot-token
├── telegram/bot-token
├── thebettertraders.com
├── openclaw/telegram-bot
└── ...
```

## Note sicurezza

- Il vault è crittografato GPG in `~/.password-store/`
- La chiave GPG è sbloccata con la tua password
- Per sessioni lunghe: `pass init "your@email.com"` una volta
- Non salvare mai password in chiaro in file .md — usa sempre `pass`
