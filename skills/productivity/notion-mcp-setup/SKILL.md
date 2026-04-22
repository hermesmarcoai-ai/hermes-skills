---
name: notion-mcp-setup
description: Setup Notion MCP server with internal integration token for Hermes Agent.
version: 1.0.0
author: Hermes Agent
---

# Notion MCP Setup

Configure Notion as an MCP server using an internal integration token (Bearer auth).

## Why Not OAuth?

Notion's MCP at mcp.notion.com does NOT support OAuth via a clickable browser link from a headless server. The reliable approach is using a **Notion Internal Integration Secret** (starts with `ntn_...`).

## Setup Steps

1. **Get the token**: User creates an integration at https://www.notion.so/my-integrations
   - Click "+ New integration"
   - Give it a name, select capabilities (read/write content, users, databases, etc.)
   - Copy the "Internal Integration Secret" (starts with `ntn_...`)

2. **Add to config.yaml**:
```yaml
mcp_servers:
  notion:
    url: "https://mcp.notion.com/mcp"
    headers:
      Authorization: "Bearer ntn_YOUR_TOKEN_HERE"
    timeout: 180
    connect_timeout: 60
```

3. **Restart Hermes** to reload MCP servers.

4. **Share pages** from Notion with the integration:
   - Go to any Notion page → click **⋯** (top right) → "Connections" → add the integration
   - The bot can ONLY access pages explicitly shared with it

## Verification

```bash
curl -s -H "Authorization: Bearer ntn_..." \
  -H "Notion-Version: 2022-06-28" \
  https://api.notion.com/v1/users/me
```

Should return bot user info with workspace_name and workspace_id.

## Pitfalls

- **Token starts with `ntn_`**: This is correct. Secret tokens from Notion integrations start with `secret_...` but the MCP endpoint uses `ntn_...` tokens. If user has a `secret_` token, they need to create a new integration or find the Internal Integration token.
- **"All systems OK" doesn't mean write access**: The bot can authenticate but may get 403 on page creation if pages aren't shared with the integration.
- **Workspace-level permissions**: If the integration is workspace-scoped, it can see all published pages. For fine-grained access, use page-level sharing.
- **The token in your config is a secret**: Treat it like an API key.

## Troubleshooting

- **401 on API calls**: Token is invalid or expired. Regenerate at https://www.notion.so/my-integrations.
- **403 on page creation**: Page not shared with the integration. Share it via page → ⋯ → Connections.
- **MCP tools not appearing**: Restart Hermes after adding to config.yaml.
- **Empty workspace**: No pages shared yet, or integration has no capabilities enabled.