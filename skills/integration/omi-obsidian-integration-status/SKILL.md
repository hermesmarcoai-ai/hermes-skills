---
name: omi-obsidian-integration-status
description: Omi + Obsidian integration status - what's available on macOS vs Linux
---
# Omi + Obsidian Integration Status

## What Exists

Omi repository (`~/omi/`) has Obsidian integration in:
- **macOS desktop app only** — `desktop/Desktop/Sources/MemoryExportService.swift`
  - Writes memories to `Omi/Memories.md` in selected vault
  - Uses `obsidian://` deep link to open notes
  - Located in Settings → Memory Export

## What's NOT Available

- **Linux/Ubuntu**: No native Omi app with Obsidian export
- **Mobile app (iOS/Android)**: Does NOT have Obsidian export
- **Backend API**: No Obsidian-specific endpoint (only generic memory export)

## Alternatives for Linux

1. **Omi MCP Server** (`mcp/`) — Read/write memories programmatically
   - Requires Omi API key (Settings → Developer → MCP in Omi app)
   - Tools: `get_memories`, `create_memory`, `delete_memory`, `edit_memory`, `get_conversations`
   
2. **Python SDK** (`sdks/python/omi/`) — Programmatic memory access

3. **Build macOS app** — Only works on macOS hardware

## Key Files
- `~/omi/desktop/Desktop/Sources/MemoryExportService.swift` — Full Swift implementation
- `~/omi/mcp/README.md` — MCP server documentation
