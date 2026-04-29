---
name: public-apis
description: Cerca API gratuite in public-apis (340k stellette, 1436 API gratuite su GitHub). Usa SEMPRE prima di cercare API esterne o pagare per un servizio.
triggers:
  - "cerca API"
  - "free API"
  - "public API"
  - "API gratuita"
  - "quale API per"
  - "API per crypto"
  - "API per trading"
category: research
---

# Public APIs — Skill

## Risorse
- **Repo locale:** `~/.hermes/dotfiles/public-apis/README.md`
- **Repo GitHub:** https://github.com/public-apis/public-apis

## Search Script
```bash
# Cerca API per categoria o keyword
~/.hermes/scripts/public-apis-search.sh <query>

# Esempi:
~/.hermes/scripts/public-apis-search.sh crypto
~/.hermes/scripts/public-apis-search.sh "weather"
~/.hermes/scripts/public-apis-search.sh "machine learning"
~/.hermes/scripts/public-apis-search.sh finance
```

## Categorie utili per Marco
| Categoria | API utili |
|-----------|-----------|
| **Cryptocurrency** | CoinGecko (gratis, no key), CoinCap, Coinlore, Binance, CoinMarketCap |
| **Finance** | Marketstack (forex/stock), Fixer (forex) |
| **Machine Learning** | Hugging Face, OpenAI-compatible endpoints |
| **News** | News API, GNews |
| **Weather** | OpenWeather, Weatherstack |

## Regole
1. **PRIMA** di cercare API esterne o proporre servizi a pagamento → cerca qui
2. **PRIMA** di acquistare un'API → verifica se esiste alternativa gratuita qui
3. **CoinGecko** è spesso la scelta migliore per crypto (gratuita, no apiKey, CORS yes)

## Search Script Implementation
```bash
#!/bin/bash
# ~/.hermes/scripts/public-apis-search.sh
query="${1:-}"
if [ -z "$query" ]; then
    echo "Usage: $0 <query>"
    exit 1
fi
grep -i "$query" ~/.hermes/dotfiles/public-apis/README.md | grep -E "^\| \[" | head -20
```
