# Observability Thresholds

## Disk Usage

| Level | Threshold | Action |
|-------|-----------|--------|
| OK | < 80% | Normal operation |
| WARNING | 80–89% | Monitor closely |
| CRITICAL | ≥ 90% | Immediate action required |

## Memory Usage

| Level | Threshold | Action |
|-------|-----------|--------|
| OK | < 80% | Normal operation |
| WARNING | 80–89% | Monitor closely |
| CRITICAL | ≥ 90% | Immediate action required |

## Cron Jobs

| Level | Condition |
|-------|-----------|
| OK | All jobs running normally |
| WARNING | Any job in error/failed/stopped state |
| CRITICAL | Multiple jobs failed |

## Gateway Processes

| Level | Condition |
|-------|-----------|
| OK | All gateway processes online |
| WARNING | Gateway processes found but some issue |
| CRITICAL | No gateway processes running |

## Active Fronts

| Level | Condition |
|-------|-----------|
| OK | All fronts healthy |
| WARNING | Fronts exist with errors/stopped flags |
| CRITICAL | No fronts found (when fronts expected) |

## Recent Failures

| Level | Condition |
|-------|-----------|
| OK | No errors in last 24h logs |
| WARNING | 1–5 errors in last 24h logs |
| CRITICAL | > 5 errors in last 24h logs |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All systems OK |
| 1 | One or more WARNING |
| 2 | One or more CRITICAL |
