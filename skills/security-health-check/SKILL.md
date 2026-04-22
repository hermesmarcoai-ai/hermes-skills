# Security Health Check Skill

## Overview

Automated security testing and monitoring for Hermes Agent. Runs health checks, generates alerts, and archives reports.

## Usage

```bash
# Quick health check
hermes security health-check

# Full security audit
hermes security audit

# Generate report
hermes security report --format markdown

# Enable continuous monitoring
hermes security monitor enable

# Disable monitoring
hermes security monitor disable
```

## Commands

### `health-check`

Run comprehensive security verification:
- User privilege check
- SSH configuration
- Firewall status
- Token security
- Command allowlist
- User allowlist
- Gateway binding
- SOUL.md rules

### `audit`

Deep security audit with remediation suggestions. Returns detailed JSON report.

### `report`

Generate formatted security report (markdown or JSON) for archival.

### `monitor enable/disable`

Configure continuous monitoring via cron job. Default: daily at 6AM.

## Alert Thresholds

| Check | Pass | Warning | Critical |
|-------|------|---------|----------|
| Running as non-root | hermes | root | - |
| SSH hardened | both settings | 1 setting | 0 settings |
| Firewall active | active | inactive | unknown |
| Token permissions | 600 | 640 | 644+ |
| Gateway localhost | 127.0.0.1 | 0.0.0.0 | - |

## Security Score Calculation

```
Score = (passed_checks / total_checks) * 100

100% = Fully secured
90-99% = Minor issues
80-89% = Some risks
<80% = Critical vulnerabilities
```

## Integration

- **Cron jobs**: Auto-run daily/weekly
- **Notifications**: Discord/Telegram alerts on failure
- **Archival**: Reports stored in `~/.hermes/reports/`
- **History**: Previous reports kept for 90 days

## Example Output

```
=== HERMES SECURITY HEALTH CHECK ===
1. Running as non-root: ✓
2. SSH hardened: ✓
3. Firewall active: ✓
4. Token secured: ✓
5. Gateway localhost: ✓
6. Command allowlist: ✓
7. User allowlist: ✓
8. SOUL.md loaded: ✓

Security Score: 100%
Status: HEALTHY
Last checked: 2026-04-08 14:35 UTC
```

## Maintenance

- Rotate tokens every 90 days
- Review firewall rules monthly
- Update SOUL.md with new security rules
- Archive reports quarterly

---

*Skill version: 1.0.0*
*Last updated: April 08, 2026*
