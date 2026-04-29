---
name: hermes-leo-interop-sse
description: Real-time SSE communication between Hermes and Leo/OpenClaw via interop-server.py on port 18900. Includes debug lessons and architecture.
category: devops
---

# Hermes ↔ Leo Interop SSE Bridge

## Architecture

```
hermes-commands/interop-server.py  →  ThreadedHTTPServer on port 18900
    ├── POST /broadcast?from=<agent>  →  deliver to other agent's queue
    ├── GET  /poll?agent=<agent>    →  read + clear HTTP queue (list)
    ├── GET  /subscribe?agent=<agent> →  SSE stream (queue.Queue)
    └── GET  /status                →  subscribers + queue sizes

hermes-sse-client.py  →  SSE client for Hermes (connects as agent=hermes)
openclaw-sse-client   →  SSE client for Leo (connects as agent=openclaw)
```

## Key Endpoints

```
POST /broadcast?from=hermes   → deliver to openclaw
POST /broadcast?from=openclaw  → deliver to hermes
GET  /poll?agent=hermes       → read + clear hermes HTTP queue
GET  /subscribe?agent=openclaw → SSE stream for Leo
GET  /status                  → JSON with subscribers + queues
```

## Critical Bugs Fixed

### Bug 1: Single-threaded server blocks on SSE
**Problem:** Python's `HTTPServer` is single-threaded. SSE long-lived connections block ALL other HTTP requests (including health checks).

**Fix:** Use `socketserver.ThreadingMixIn`:
```python
from socketserver import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

server = ThreadedHTTPServer(("127.0.0.1", PORT), Handler)
```

### Bug 2: Multiple server processes with separate in-memory queues
**Problem:** Every `python3 interop-server.py` creates a NEW process with FRESH in-memory queues. Old processes stay alive. Broadcast goes to new server, SSE client connects to old server → never meet.

**Fix:** Always kill ALL existing processes before restart:
```bash
pkill -9 -f interop-server.py
sleep 1
ss -tlnp | grep 18900  # verify port is free
python3 interop-server.py
```

### Bug 3: Double-queue problem
**Problem:** Two separate queue systems:
- `queues["openclaw"]` — Python list, used by `/poll` endpoint
- `subscribers["openclaw"]` — `queue.Queue()`, used by SSE stream

Broadcast does BOTH:
```python
queues[recipient].append(data)        # adds to list
push_to_subscriber(recipient, data)  # adds to queue.Queue()
```

If Leo uses `/poll`, he consumes from the list. SSE stream keeps blocking on `queue.Queue()`. If Leo uses SSE only, the list grows but SSE stream works.

**Fix:** When subscriber reconnects, flush pending messages from list to queue:
```python
q = queue.Queue()
while queues[agent]:  # flush pending to new SSE queue
    q.put_nowait(queues[agent].pop(0))
subscribers[agent] = q
```

### Bug 4: BrokenPipeError on client disconnect
**Problem:** Client closes SSE connection while server is writing → `BrokenPipeError`.

**Fix:**
```python
try:
    self.wfile.write(json.dumps({"delivered": True, ...}).encode())
except BrokenPipeError:
    pass
```

## Client Setup

### Hermes SSE Client (hermes-sse-client.py)
```python
import urllib.request, json, time

SERVER = "http://127.0.0.1:18900"

def main():
    req = urllib.request.Request(f"{SERVER}/subscribe?agent=hermes")
    with urllib.request.urlopen(req) as r:
        for line in r:
            line = line.decode().strip()
            if line.startswith("data: "):
                data = json.loads(line[6:])
                # process message
                with open("/tmp/hermes-msg-pipe", "w") as f:
                    f.write(json.dumps(data) + "\n")

while True:
    try:
        main()
    except Exception as e:
        time.sleep(5)  # auto-reconnect
```

### Run Commands
```bash
# Kill all
pkill -9 -f interop-server.py; pkill -9 -f hermes-sse-client.py

# Start server
cd /home/marco/hermes-commands && python3 interop-server.py

# Start Hermes client (background)
python3 hermes-sse-client.py

# Check status
curl http://127.0.0.1:18900/status
```

## Expected Status Output
```json
{
  "agents": {"openclaw": {"online"}, "hermes": {"online"}},
  "queues": {"openclaw": 0, "hermes": 0},
  "subscribers": {"openclaw": true, "hermes": true}
}
```

Both `true` = real-time communication working.

## Files
- `/home/marco/hermes-commands/interop-server.py` — server
- `/home/marco/hermes-commands/hermes-sse-client.py` — Hermes client
