---
name: hermes-vision-troubleshooting
category: devops
description: Diagnose and fix `vision_analyze` tool failures, especially 401 Authentication errors and `auxiliary` configuration overrides.
---

# Hermes Vision Troubleshooting

## Symptoms
- `vision_analyze` returns `Error code: 401 - {'error': {'message': 'Missing Authentication header' ...}}`.
- User reports images are being sent, but analysis fails.

## Root Cause
The `auxiliary.vision` section in `~/.hermes/config.yaml` can explicitly override the credential pool. If `api_key` is set to an empty string `''`, the tool bypasses the credential pool and sends no `Authorization` header to the API.

Configuration snippet:
```yaml
auxiliary:
  vision:
    provider: openrouter
    api_key: ''  # <--- DANGER: Empty string overrides credential pool, causes 401
```

## Resolution
1. Open `~/.hermes/config.yaml`.
2. Find the `auxiliary:` section.
3. Under `vision:`, either **delete the `api_key` line entirely** or let the credential pool handle it.
4. If using the credential pool (`credential_pool_strategies: openrouter: fill_first`), ensure the pool actually has the key by running `hermes auth` or setting `OPENROUTER_API_KEY` in `~/.hermes/.env`.
5. Restart the agent or gateway if necessary.

## Verification
- Send an image to the agent and ask `vision_analyze` to describe it. It should succeed once the empty `api_key` override is removed.
- Check logs for `Auxiliary vision client: openrouter` to confirm the credential pool client was successfully initialized.

## Other `auxiliary` tasks
The same logic applies to other auxiliary tasks: `web_extract`, `compression`, `session_search`. Each has its own `provider`, `api_key`, `base_url` in `config.yaml`. Explicit empty strings will break credential pooling. Always prefer leaving them blank/absent if using `credential_pool_strategies`.
