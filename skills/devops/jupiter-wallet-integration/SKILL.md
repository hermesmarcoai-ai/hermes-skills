---
name: jupiter-wallet-integration
description: Jupiter wallet integration for Hermes Agent — connect Solana wallets, sign transactions, and manage DeFi positions.
version: 1.0
author: Marco
metadata:
  hermes:
    tags: [wallet, solana, defi, jupiter, signing]
    category: devops
---

# Jupiter Wallet Integration

Connect Solana wallets to Hermes Agent for Jupiter DeFi operations. Handles transaction signing, wallet state, and position tracking.

## When to Use

- "Connect my Solana wallet"
- "Sign this Jupiter transaction"
- "Check my DeFi positions"
- "What's my portfolio worth?"

## Prerequisites

```bash
# Install Solana wallet adapter
pip install solana solders

# Or use Phantom wallet via WalletConnect
# Requires: walletconnect-api-key
```

## Wallet Types Supported

| Type | Setup | Use Case |
|------|-------|----------|
| CLI Keypair | `solana-keygen` file | Full control, script automation |
| Phantom (Bridge) | WalletConnect RPC | Browser extension wallets |
| Ledger | `solana-ledger` | Hardware wallet security |
| Paper | Paper keypair | Testing |

## Connecting a Wallet

### CLI Wallet

```python
import solana.rpc.api
from solders.keypair import Keypair

# Load from file
keypair = Keypair.from_bytes(open("~/.config/solana/id.json").read().strip().decode("hex"))
client = solana.rpc.api.Client("https://api.mainnet-beta.solana.com")
```

### Ledger

```python
from solana.rpc.commitment import Confirmed
from ledgerwallet import LedgerWallet

wallet = LedgerWallet()
pubkey = wallet.get_pubkey()
```

## Transaction Signing

```python
from solana.rpc.types import TxOpts

# Build transaction
tx = ...  # Jupiter swap transaction

# Sign with wallet
signed_tx = keypair.sign_message(tx.serialize())

# Send
client.send_raw_transaction(signed_tx, opts=TxOpts(skip_confirmation=False, preflight_commitment=Confirmed))
```

## Position Tracking

```
User: "Show my DeFi positions"
→ Query all token accounts
→ Fetch Jupiter for position data
→ Display:
  SOL:     12.5 SOL ($750)
  USDC:    1,200 USDC ($1,200)
  mSOL:    3.2 mSOL ($400)
  ─────────────────────
  TOTAL:   ~$2,350

  Active orders:
  • DCA SOL→USDC: 2/30 days complete
```

## Security Notes

- NEVER log private keys
- Use hardware wallet for large positions
- Set up transaction confirmations
- Never sign unknown transactions
- Use `skip_confirmation=False` for large swaps

## Tips

- Store keypair securely (encrypted file or env var)
- Use different wallets for different purposes
- Monitor `recent_blockhash` age before signing
