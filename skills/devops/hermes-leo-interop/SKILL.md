---
name: hermes-leo-interop
description: Real-time communication between Hermes and Leo/OpenClaw via SSE-enhanced interop-server on port 18900
---

# Hermes ↔ Leo/OpenClaw Real-Time Interop

## Situation
Hermes (MiniMax) e Leo/OpenClaw rodano sulla stessa macchina (Surface) ma come processi separati. Serve un message bus per comunicazione real-time tra i due agenti.

## Architecture
**Server:** `/home/marco/hermes-commands/interop-server.py` (porta 18900)

### Protocollo esistente
```
POST /broadcast?from=<agent>   → invia al destinatario (hermes↔openclaw)
GET  /poll?agent=<agent>       → legge e pulisce la coda (polling)
GET  /status                   → status agenti e dimensione code
```

### Estensione SSE (aggiunta)
```
GET  /subscribe?agent=<agent>  → SSE stream real-time, push immediato
```

## Come funziona l'SSE
1. Client apre `GET /subscribe?agent=hermes`
2. Server risponde `200` con `Content-Type: text/event-stream`
3. Quando arriva un `POST /broadcast` diretto a quell'agente, il server fa `push` immediato sulla connessione SSE
4. Keepalive ogni 30s per mantenere la connessione viva

## ThreadingMixIn — CRITICAL

Python's `HTTPServer` is **single-threaded**. When an SSE client connects, the server blocks on that connection, making all other endpoints (including `/health`, `/status`, `/broadcast`) unresponsive.

**Solution:**
```python
from socketserver import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

server = ThreadedHTTPServer(("127.0.0.1", PORT), Handler)
```

**Without this:** server appears to hang — `/health` and `/status` time out while an SSE client is connected.

## CRITICAL BUG: Multiple Server Processes

Se `interop-server.py` viene riavviato più volte senza cleanup, restano **processi zombie** con code in-memory separate. Broadcast va a un server, SSE client si connette a un altro → mai si incontrano. Il push sembra rotto.

**Sintomi:**
- `/health` e `/status` rispondono ma SSE non funziona
- `subscribers` mostra connessioni ma push non arriva
- Errori di binding sulla porta 18900

**Verifica:**
```bash
ps aux | grep interop-server.py
# Se vedi PIÙ di un processo python3 con interop-server.py → BUG
```

**Fix:**
```bash
# Kill ALL i processi
pkill -9 -f interop-server.py
pkill -9 -f hermes-sse-client.py
sleep 2
# Verifica porta libera
ss -tlnp | grep 18900 || echo "port free"
# Riavvia solo uno
cd /home/marco/hermes-commands && python3 interop-server.py
```

**Prevenzione:** ogni riavvio deve fare `pkill` prima di lanciare, mai lasciare processi zombie.

## Debug trovati
- **curl in background**: non usare `&` in foreground — usare `terminal(background=true)` per processi lunghi
- **Race condition**: se il broadcast arriva mentre il subscriber sta per chiudere, il messaggio resta in coda (comportamento ok)
- **Python threading**: `urllib.request.urlopen` in thread separato funziona ma serve `join()` corretto
- **Server duplicati**: MAI avviare un secondo server senza killare il precedente
- **Reconnect flush**: quando un subscriber si reconnette, i messaggi pendenti nella coda principale vengono spostati nella nuova SSE queue — così nessun messaggio viene perso tra una riconnessione e l'altra

## Verifiche
```bash
# Status
curl http://127.0.0.1:18900/status

# Test broadcast
curl -X POST "http://127.0.0.1:18900/broadcast?from=openclaw" \
  -H "Content-Type: application/json" \
  -d '{"type": "test", "text": "messaggio"}'

# Leggi coda (polling fallback)
curl "http://127.0.0.1:18900/poll?agent=hermes"
```

## Flusso di test
1. Apri SSE subscriber: `curl -N "http://127.0.0.1:18900/subscribe?agent=openclaw"`
2. Broadcast da Hermes: `curl -X POST ".../broadcast?from=hermes" -d '{...}'`
3. Il messaggio arriva subito sul stream SSE se la connessione è attiva

## Note
- L'SSE usa `queue.Queue` per ogni subscriber — una coda per connessione
- `subscribers["hermes"] = None` quando si disconnette (cleanup in `finally`)
- Broadcast fa sia `append()` in coda che `push_to_subscriber()` per push immediato

## CRITICAL BUG: Double Queue Problem

Il sistema ha DUE code separate per ogni agent:

1. `queues["openclaw"]` — per polling HTTP (`/poll`)
2. `subscribers["openclaw"]` — per SSE push (`queue.Queue()` nel thread SSE)

Broadcast scrive a ENTRAMBI, ma:
- SSE stream legge da `subscribers[agent]` (via `q.get()`)
- `/poll` legge da `queues[agent]`

**Sintomo:** messaggi in `queues["openclaw"]` ma SSE stream non li entrega — il client SSE non sta consumando dalla coda giusta.

**Root cause:** quando un nuovo subscriber SSE si reconnette, viene creata una NUOVA `queue.Queue()`. I messaggi vecchi in `queues["openclaw"]` restano lì se il client SSE non li ha ancora consumati.

**Fix (già implementato):** quando SSE subscriber si reconnette, flush dei messaggi pendenti dalla coda principale alla coda SSE:
```python
q = queue.Queue()
while queues[agent]:
    q.put_nowait(queues[agent].pop(0))
subscribers[agent] = q
```

**Regola pratica:** SE un agent usa `/poll`, NON può ricevere via SSE nella stessa sessione perché poll consuma dalla coda HTTP. Per ricevere via SSE, NON usare `/poll`.

## Problema risolto: notifica automatica al connect

**Problema:** Quando Leo si connette all'SSE, Hermes non lo sa finché non viene menzionato su Discord. Non c'era modo di "svegliare" Hermes automaticamente.

**Soluzione:** Quando un subscriber si connette, il server aggiunge automaticamente un messaggio nella coda dell'altro agente E fa push via SSE:
```python
if other == "hermes":
    msg = {
        "_meta": {"from": "interop", "type": "subscriber_connected"},
        "type": "subscriber_connected",
        "text": "OpenClaw si è connesso all'SSE — ora puoi inviargli messaggi in tempo reale"
    }
    queues["hermes"].append(msg)
    push_to_subscriber("hermes", msg)
```
Così Hermes riceve la notifica in tempo reale appena Leo si connette, senza bisogno di essere menzionato.

## BrokenPipeError fix

Quando Leo chiude la connessione SSE mentre Hermes sta facendo broadcast, il write su `self.wfile` fallisce con `BrokenPipeError`. Aggiunto try/except:
```python
try:
    self.wfile.write(json.dumps({"delivered": True, ...}).encode())
except BrokenPipeError:
    pass
```
