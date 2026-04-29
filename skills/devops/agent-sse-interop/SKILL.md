---
name: agent-sse-interop
description: Real-time SSE-based communication bus between Hermes and Leo/OpenClaw agents on port 18900
---

# Agent SSE Inter-Process Communication

## Overview
Real-time message bus between Hermes and Leo/OpenClaw using Server-Sent Events (SSE) via a shared HTTP server on port 18900. Enables push-based communication without polling.

## Architecture
```
┌─────────────────┐    SSEsubscribe    ┌──────────────────────┐
│  Hermes Agent   │◄───────────────────│  interop-server.py   │
│  (SSE client)   │                   │  ThreadedHTTPServer  │
└─────────────────┘                   │  Port 18900          │
                                       └──────────┬───────────┘
                                                  │ push
┌─────────────────┐    SSEsubscribe    ┌──────────▼───────────┐
│  Leo/OpenClaw   │◄──────────────────│                      │
│  (SSE client)   │                   │  subscribers dict    │
└─────────────────┘                   │  queues dict         │
                                       └──────────────────────┘
```

## Key Endpoints
```
GET  /health                      — health check
GET  /status                      — agents + queues + subscribers status
GET  /subscribe?agent=<name>      — SSE stream (long-lived connection)
GET  /poll?agent=<name>           — HTTP poll (returns + clears queue)
POST /broadcast?from=<name>        — broadcast to OTHER agent
```

## Critical Lessons

### 1. HTTPServer blocks without ThreadingMixIn
Without `ThreadingMixIn`, SSE connections block the entire server:
```python
from socketserver import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True
```

### 2. Multiple processes = separate in-memory state (THE MAIN BUG)
Each `python3 interop-server.py` process has its own `queues` dict. Broadcasts go to one process, SSE clients connect to another — they never meet.

**Always kill ALL before restarting:**
```bash
pkill -9 -f interop-server.py
sleep 2
ss -tlnp | grep 18900 || echo "port free"
```

### 3. Reconnection needs queue flush
When subscriber reconnects, flush pending messages:
```python
q = queue.Queue()
while queues[agent]:
    q.put_nowait(queues[agent].pop(0))
subscribers[agent] = q
```

### 4. Keepalive every 30s
```python
self.wfile.write(b": keepalive\n\n")
```

### 5. Broken pipe handling
```python
try:
    self.wfile.write(data)
except BrokenPipeError:
    pass
```

## Files
- Server: `/home/marco/hermes-commands/interop-server.py`
- Hermes SSE client: `/home/marco/hermes-commands/hermes-sse-client.py`
- Pipe: `/tmp/hermes-msg-pipe`
