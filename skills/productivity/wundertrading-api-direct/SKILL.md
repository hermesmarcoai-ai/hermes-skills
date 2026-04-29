---
name: wundertrading-api-direct
description: Direct REST API access for WunderTrading when MCP fails
triggers:
  - wundertrading not working
  - wundertrading MCP IP error
  - wundertrading access denied
---

# WunderTrading Direct API Access

When WunderTrading MCP tools fail with IP whitelist errors, use the REST API directly.

## API Endpoint
```
https://wundertrading.com:2083/mcp
```

## Required Headers
```
X-API-Key: <your-api-key>
X-Secret-Key: <your-secret-key>
Content-Type: application/json
Accept: application/json, text/event-stream
```

## Example: List Live Strategies
```bash
curl -s --max-time 15 "https://wundertrading.com:2083/mcp" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "X-Secret-Key: YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_live_strategies","arguments":{"limit":10}},"id":2}'
```

## Example: Get API Profiles
```bash
curl -s --max-time 15 "https://wundertrading.com:2083/mcp" \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "X-Secret-Key: YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","method":"tools/call","params":{"name":"get_api_profiles","arguments":{}},"id":3}'
```

## Response Format
Returns SSE stream. Parse the `data:` lines for JSON results.

## Available Methods (JSON-RPC)
- `get_live_strategies` - Active/recent strategies
- `get_api_profiles` - Connected exchange accounts
- `get_strategies_history` - Historical strategies
- `get_strategy` - Single strategy by ID
- `place_strategy_trade` - Open a trade
- `edit_trade_strategy` - Modify a strategy

## Notes
- Surface's MCP tool may fail with "Access denied: client IP 10.20.165.178" even when IP is whitelisted
- Direct REST API bypasses this issue
- Config stored in `~/.hermes/config.yaml` under `mcp_servers.wundertrading`
