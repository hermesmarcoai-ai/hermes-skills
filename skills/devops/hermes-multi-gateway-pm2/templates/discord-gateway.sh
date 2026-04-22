#!/bin/bash
# Hermes Discord Gateway PM2 Wrapper
# Template for running Discord gateway with isolated locks

export PATH="/root/.hermes/node/bin:/root/.local/bin:${PATH}"
export HERMES_HOME="/root/.hermes"

# Load environment variables from main .env
if [ -f "$HERMES_HOME/.env" ]; then
    set -a
    source "$HERMES_HOME/.env"
    set +a
fi

# Load platform-specific env file if exists (for token overrides)
if [ -f "$HERMES_HOME/discord-env" ]; then
    set -a
    source "$HERMES_HOME/discord-env"
    set +a
fi

# CRITICAL: Platform-specific lock directory to avoid conflicts with other gateways
export HERMES_GATEWAY_LOCK_DIR="$HERMES_HOME/locks/discord"
mkdir -p "$HERMES_GATEWAY_LOCK_DIR"

# Force Discord platform only (don't start other platforms)
export HERMES_GATEWAY_PLATFORMS=discord

# Run gateway in foreground for PM2
exec /root/.local/bin/hermes gateway run
