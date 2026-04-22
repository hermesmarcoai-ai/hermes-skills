# Hermes Model Selection - Configuration

## Comandi CLI Disponibili

Dopo la configurazione, questi comandi saranno disponibili in `/hermes`:

### `/model-select` — Analisi task e selezione modello

```bash
hermes model-select "scrivi articolo blog"
hermes model-select "debug code Python" --domain coding --complexity high
hermes model-select "chat analysis" --budget max_savings --quick
hermes model-select "enterprise strategy" --json
```

**Output:**
- Modello raccomandato con confidence score
- Stima costo in tempo reale
- Fallback automatic o se il modello primario fallisce
- Optimization score (0-1)

### `/model-list` — Lista modelli disponibili

```bash
hermes model-list
hermes model-list --category cheap
hermes model-list --best-value
```

**Output:**
- Tutti i modelli disponibili raggruppati per categoria
- Prezzi input/output per 1M token
- Latenze medie
- Rating reasoning (1-5)

### `/model-cost` — Stima costi

```bash
hermes model-cost "scrivi email"
hermes model-cost --model qwen/qwen3-coder-next
hermes model-cost "debug code" --tokens 5000
```

**Output:**
- Costo stimato per task
- Breakdown token input/output
- Proiezione per 100/1000 richieste

### `/model-set` — Imposta modello manualmente

```bash
hermes model-set qwen/qwen3.5-27b
hermes model-set qwen/qwen3-coder-next --permanent
hermes model-list --current
```

## Configurazione Automatica

Per abilitare i comandi nel CLI:

1. **Aggiorna config.yaml:**

```bash
cd ~/.hermes

# Backup
cp config.yaml config.yaml.backup

# Aggiungi sezione model_routing
cat >> config.yaml << 'EOF'

# Model Routing Configuration
model_routing:
  enabled: true
  strategy: cost_optimized
  fallback_enabled: true
  max_cost_per_request: 0.50
  daily_budget: 10.00
EOF
```

2. **Crea symlink per comandi CLI:**

```bash
# Crea script wrapper
cat > ~/.hermes/bin/hermes-models << 'EOF'
#!/bin/bash
python3 ~/.hermes/skills/model-selection/model_selection_cli.py "$@"
EOF

chmod +x ~/.hermes/bin/hermes-models
```

3. **Integra nel sistema principale:**

Il sistema di model selection si attiva automaticamente quando:
- `model_routing.enabled = true` in config.yaml
- L'agent riceve un nuovo task
- Viene chiamata la funzione `handle_function_call()`

## Regole di Selezione Automatica

Una volta configurato, il sistema segue queste regole:

```
Task: "scrivi articolo blog"
  → task_type = 'content', complexity = 'medium'
  → budget = 'balanced'
  → MODEL: qwen/qwen3.5-9b ($0.07)
  → Costo: ~$0.00014 per request

Task: "refactor React component"
  → task_type = 'coding', domain = 'development'
  → MODEL: qwen/qwen3-coder-next ($0.50)
  → Costo: ~$0.00008 per request

Task: "analizza mercato finanziario"
  → task_type = 'analysis', complexity = 'high'
  → MODEL: deepseek/deepseek-v3.2 ($0.55)
  → Costo: ~$0.001 per request

Task: "decisione mission-critical"
  → task_type = 'enterprise'
  → MODEL: anthropic/claude-opus-4.6 ($15)
  → Costo: ~$0.015 per request
```

## Monitoraggio Costi

Per tracciare le spese:

```bash
# Vedi costi di oggi
hermes model-cost --today

# Imposta alert budget
hermes model-alert --daily 10.00

# Esporta report
hermes model-report --format json --output ~/reports/
```

## Troubleshooting

### Comando non riconosciuto
```bash
# Riavvia Hermes CLI
systemctl restart hermes-agent
# O per gateway
systemctl restart hermes-gateway
```

### Errori di configurazione
```bash
# Test config
python3 ~/.hermes/skills/model-selection/model_selection_engine.py --task "test"

# Reset config
cp ~/.hermes/config.yaml.backup ~/.hermes/config.yaml
```

### Modelli non trovati
```bash
# Aggiorna database
python3 ~/.hermes/skills/model-selection/model_selection_engine.py --update-db
```

## Best Practices

1. **Monitora i costi** nelle prime 2 settimane
2. **Ajusta budget_priority** in base alle performance
3. **Abilita escalation** per task critici
4. **Usa fallback** per garantire continuità
5. **Export report** settimanali per ottimizzazione

## Supporto

- Documentazione completa: `~/.hermes/skills/model-selection/README.md`
- Engine script: `~/.hermes/skills/model-selection/model_selection_engine.py`
- CLI integration: `~/.hermes/skills/model-selection/model_selection_cli.py`
