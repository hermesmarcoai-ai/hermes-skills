# cron-conditional-execution

**Category:** devops  
**Version:** 1.0.0  
**Author:** Marco  
**Last Updated:** 2026-04-25

Conditional cron job execution using price/state/time/shell predicates. Wrapper script evaluates conditions before job run.

---

## Overview

This skill provides a framework for conditional cron job execution. Instead of running cron jobs unconditionally, you can define predicates (conditions) that must be satisfied before the job actually executes.

## Predicate Types

### 1. Shell Predicate
Execute any shell command; job runs if command returns exit code 0.

```bash
# Run only if a file exists
shell: test -f /tmp/healthcheck.ok

# Run only if a service is running
shell: pgrep -x nginx > /dev/null

# Run only if disk usage is below 90%
shell: df / | awk 'NR==2 {exit !($5+0 < 90)}'
```

### 2. Time Predicate
Cron-like time constraints using `@hourly`, `@daily`, `@weekly`, or numeric ranges.

```bash
# Run only between 9 AM and 5 PM
time: 9-17 * * *

# Run only on weekdays (Mon-Fri)
time: * * * * 1-5

# Run only at midnight
time: 0 0 * * *
```

### 3. State Predicate
Check file-based state flags (create/manage state files).

```bash
# Run only if maintenance mode is OFF
state: maintenance_mode != on

# Run only if previous job succeeded (uses lock file)
state: /var/run/myjob.lock == clean

# Run only if feature flag is enabled
state: FEATURE_NEW_API == enabled
```

### 4. Price Predicate (Crypto/Financial)
Query price data and compare; supports common price APIs.

```bash
# Run only if BTC price > $50000
price: BTC > 50000

# Run only if ETH price < $3000
price: ETH < 3000

# Run only if SOL price between $100 and $200
price: SOL > 100 && SOL < 200
```

## Wrapper Script

The `cron-wrapper.sh` script is the core component that evaluates predicates before executing your job.

### Usage

```bash
cron-wrapper.sh [OPTIONS] -- PREDICATES -- COMMAND [ARG...]
```

### Options

| Option | Description |
|--------|-------------|
| `-v`   | Verbose output (print predicate evaluation results) |
| `-n`   | Dry-run mode (show what would run without executing) |
| `-l LOG` | Log file for execution history |
| `-s STATE_DIR` | Directory for state files (default: `/var/run/cond-cron`) |

### Examples

```bash
# Basic shell predicate
cron-wrapper.sh -- shell:"pgrep -x myapp" -- /usr/local/bin/backup.sh

# Multiple predicates (all must pass)
cron-wrapper.sh -v -- shell:"test -f /tmp/ready" -- time:"9-17 * * *" -- ./deploy.sh

# Price predicate
cron-wrapper.sh -- price:"BTC > 50000" -- /scripts/alerta.sh

# Complex conditions
cron-wrapper.sh -- \
  shell:"test -f /tmp/db_ready" \
  -- time:"0 2 * * *" \
  -- /backup.sh
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0    | Job executed successfully |
| 1    | Condition failed (job skipped) |
| 2    | Syntax error in predicates |
| 3    | Command not found |

## Test Condition Command

Use `test-condition.sh` to validate predicates without running the full wrapper.

```bash
# Test a shell predicate
test-condition.sh shell "test -f /tmp/exists"

# Test a time predicate
test-condition.sh time "9-17 * * *"

# Test a price predicate
test-condition.sh price "BTC > 50000"
```

### Test Script Features

- Validates predicate syntax
- Shows resolved value for state predicates
- Displays current price data for price predicates
- Returns exit code 0 if condition passes, 1 if fails

## Cron Installation

### Method 1: Direct in crontab

```cron
# Run backup every day at 2 AM only if system is healthy
0 2 * * * /home/marco/.hermes/skills/devops/cron-conditional-execution/scripts/cron-wrapper.sh -l /var/log/cond-cron.log -- shell:"test -f /tmp/backup_ok" -- /home/marco/bin/backup.sh

# Run trading bot only when BTC > $50000
*/5 * * * * /home/marco/.hermes/skills/devops/cron-conditional-execution/scripts/cron-wrapper.sh -- price:"BTC > 50000" -- /home/marco/bin/trading-bot.sh
```

### Method 2: Using template

```bash
# Generate crontab entry from template
cat ~/.hermes/skills/devops/cron-conditional-execution/templates/cron-example.txt
```

## File Structure

```
cron-conditional-execution/
├── SKILL.md                    # This file
├── scripts/
│   ├── cron-wrapper.sh         # Main wrapper script
│   ├── test-condition.sh       # Predicate tester
│   └── predicates/
│       ├── shell.sh            # Shell predicate evaluator
│       ├── time.sh             # Time predicate evaluator
│       ├── state.sh            # State predicate evaluator
│       └── price.sh            # Price predicate evaluator
└── templates/
    └── cron-example.txt        # Example crontab entries
```

## State Management

State files are simple text files in `STATE_DIR` (default: `/var/run/cond-cron`).

```bash
# Create a state file
echo "on" > /var/run/cond-cron/maintenance_mode

# Check state
cat /var/run/cond-cron/maintenance_mode
```

### State Files Used by This Framework

| File | Purpose |
|------|---------|
| `maintenance_mode` | Global maintenance flag |
| `*.lock` | Job lock files (created by wrapper) |

## Price API Configuration

For price predicates, the script uses free APIs:

- **CoinGecko** (default) - `https://api.coingecko.com/api/v3`
- **Binance** (fallback) - `https://api.binance.com/api/v3`

No API key required for basic usage. Rate limits apply.

## Pitfalls

1. **Shell predicate quoting** - Always quote shell commands with `shell:"command"` syntax; inner quotes must be escaped if needed.

2. **Time predicate format** - Uses cron format (minute hour day month weekday). Not cron schedule syntax — this is the *condition*, not the schedule.

3. **Price predicate caching** - Prices are cached for 60 seconds to avoid rate limiting. Multiple price checks in the same wrapper call share the cache.

4. **State race conditions** - State files are not atomic. For production use with concurrent jobs, use flock or similar.

5. **Exit code 1 means skipped** - When a condition fails, the wrapper exits with code 1 (not 0). This is intentional so cron can detect skipped jobs.

## Verification Steps

```bash
# 1. Verify wrapper is executable
ls -la ~/.hermes/skills/devops/cron-conditional-execution/scripts/cron-wrapper.sh

# 2. Test predicate evaluator
~/.hermes/skills/devops/cron-conditional-execution/scripts/test-condition.sh shell "echo ok"

# 3. Dry-run a complete command
~/.hermes/skills/devops/cron-conditional-execution/scripts/cron-wrapper.sh -n -v -- shell:"true" -- echo "Job would run"

# 4. Check cron syntax
crontab -l | grep -A1 "cron-wrapper"
```

## See Also

- [cron-alert-noise-reduction](../cron-alert-noise-reduction/) - Reduce alert fatigue from conditional cron jobs
- [cron-job-recovery](../cron-job-recovery/) - Auto-restart failed cron jobs
