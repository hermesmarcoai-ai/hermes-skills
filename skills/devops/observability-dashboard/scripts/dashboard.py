#!/usr/bin/env python3
"""
Observability Dashboard — Hermes Agent health overview
Collects: active fronts, cron jobs, gateway status, disk/memory, recent failures
Exit codes: 0=OK, 1=WARNING, 2=CRITICAL
"""

import os
import sys
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path

# Thresholds
DISK_WARNING = 80
DISK_CRITICAL = 90
MEMORY_WARNING = 80
MEMORY_CRITICAL = 90

# Paths
ACTIVE_FRONTS_PATH = Path.home() / ".hermes" / ".active-fronts.md"
HERMES_DIR = Path.home() / ".hermes"

def run_cmd(cmd, shell=False):
    """Run a command and return output, or empty string on failure."""
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.returncode
    except Exception:
        return "", 1

def check_disk():
    """Check disk usage. Returns (status, details)."""
    output, _ = run_cmd(["df", "-h", "/"])
    if not output:
        return "WARNING", "Could not read disk usage"
    
    lines = output.strip().split("\n")
    if len(lines) < 2:
        return "WARNING", "Unexpected df output"
    
    # Parse: Filesystem      Size  Used Avail Use% Mounted on
    parts = lines[1].split()
    if len(parts) < 5:
        return "WARNING", "Unexpected df output format"
    
    usage_str = parts[4].rstrip("%")
    try:
        usage = int(usage_str)
    except ValueError:
        return "WARNING", f"Could not parse disk usage: {usage_str}"
    
    details = f"Disk: {parts[3]} free / {parts[1]} ({usage_str} used)"
    
    if usage >= DISK_CRITICAL:
        return "CRITICAL", details
    elif usage >= DISK_WARNING:
        return "WARNING", details
    return "OK", details

def check_memory():
    """Check memory usage. Returns (status, details)."""
    output, _ = run_cmd(["free", "-m"])
    if not output:
        return "WARNING", "Could not read memory usage"
    
    lines = output.strip().split("\n")
    if len(lines) < 2:
        return "WARNING", "Unexpected free output"
    
    # Parse: Mem: total used free shared buff/cache available
    parts = lines[1].split()
    if len(parts) < 7:
        return "WARNING", "Unexpected free output format"
    
    try:
        total = int(parts[1])
        available = int(parts[6])
        used_pct = int((total - available) / total * 100)
    except (ValueError, ZeroDivisionError):
        return "WARNING", "Could not parse memory usage"
    
    details = f"Memory: {available}MB available / {total}MB ({used_pct}% used)"
    
    if used_pct >= MEMORY_CRITICAL:
        return "CRITICAL", details
    elif used_pct >= MEMORY_WARNING:
        return "WARNING", details
    return "OK", details

def check_active_fronts():
    """Check active fronts file. Returns (status, details)."""
    if not ACTIVE_FRONTS_PATH.exists():
        return "WARNING", "No active-fronts.md found"
    
    try:
        content = ACTIVE_FRONTS_PATH.read_text()
    except Exception:
        return "WARNING", "Could not read active-fronts.md"
    
    lines = [l.strip() for l in content.strip().split("\n") if l.strip()]
    active = [l for l in lines if not l.startswith("#") and not l.startswith("---")]
    
    if not active:
        return "OK", "No active fronts"
    
    # Check for any issues in fronts (look for failure patterns)
    failures = [l for l in active if any(x in l.lower() for x in ["error", "failed", "stopped", "offline"])]
    if failures:
        return "WARNING", f"{len(active)} active fronts, {len(failures)} with issues"
    
    return "OK", f"{len(active)} active front(s)"

def check_cron_jobs():
    """Check cron jobs status. Returns (status, details)."""
    # Try cronjob command first
    output, rc = run_cmd(["cronjob", "list"])
    if rc == 0 and output:
        lines = [l for l in output.strip().split("\n") if l.strip()]
        if lines:
            failed = [l for l in lines if any(x in l.lower() for x in ["error", "failed", "stopped"])]
            if failed:
                return "WARNING", f"{len(failed)} cron job(s) with issues / {len(lines)} total"
            return "OK", f"{len(lines)} cron job(s)"
    
    # Fallback: parse crontab
    output, rc = run_cmd(["crontab", "-l"])
    if rc == 0 and output:
        lines = [l for l in output.strip().split("\n") if l.strip() and not l.startswith("#")]
        return "OK", f"{len(lines)} cron job(s) (via crontab)"
    
    return "OK", "No cron jobs found"

def check_gateway():
    """Check gateway process status via pm2. Returns (status, details)."""
    output, rc = run_cmd(["pm2", "list"])
    if rc != 0 or not output:
        # pm2 not available, try ps
        output, rc = run_cmd(["ps", "aux"])
        if rc == 0:
            gateway_procs = [l for l in output.split("\n") if "gateway" in l.lower() or "openclaw" in l.lower() or "hermes" in l.lower()]
            if gateway_procs:
                return "OK", f"{len(gateway_procs)} gateway process(es) running"
        return "WARNING", "Gateway status unknown (pm2 unavailable)"
    
    # Parse pm2 output for hermes/gateway processes
    lines = output.strip().split("\n")
    hermes_lines = [l for l in lines if "hermes" in l.lower() or "gateway" in l.lower() or "openclaw" in l.lower()]
    
    if not hermes_lines:
        return "WARNING", "No Hermes gateway processes found"
    
    # Check for stopped or error states
    issues = [l for l in hermes_lines if any(x in l.lower() for x in ["stopped", "error", "failed", "online"])]
    
    return "OK", f"Gateway: {len(hermes_lines)} process(es)"

def check_recent_failures():
    """Check for recent failures in logs. Returns (status, details)."""
    logs_to_check = [
        HERMES_DIR / "logs",
    ]
    
    failures = []
    cutoff = datetime.now() - timedelta(hours=24)
    
    for log_dir in logs_to_check:
        if not log_dir.exists():
            continue
        
        try:
            for log_file in log_dir.glob("*.log"):
                try:
                    # Read last 100 lines
                    content = log_file.read_text()
                    lines = content.strip().split("\n")
                    recent = lines[-100:] if len(lines) > 100 else lines
                    
                    for line in recent:
                        if any(x in line.lower() for x in ["error", "fatal", "critical", "exception"]):
                            # Try to extract timestamp
                            failure_time = log_file.stat().st_mtime
                            failures.append(line[:100])
                except Exception:
                    pass
        except Exception:
            pass
    
    if len(failures) > 5:
        return "CRITICAL", f"{len(failures)} error(s) in recent logs"
    elif failures:
        return "WARNING", f"{len(failures)} error(s) in recent logs"
    return "OK", "No recent failures"

def status_icon(status):
    """Return emoji icon for status."""
    return {"OK": "✅", "WARNING": "⚠️", "CRITICAL": "🔴"}.get(status, "❓")

def print_dashboard():
    """Generate and print the full dashboard."""
    sections = [
        ("Active Fronts", check_active_fronts),
        ("Cron Jobs", check_cron_jobs),
        ("Gateway Status", check_gateway),
        ("Disk / Memory", lambda: (max(check_disk()[0], check_memory()[0]), f"{check_disk()[1]} | {check_memory()[1]}")),
        ("Recent Failures", check_recent_failures),
    ]
    
    overall_status = "OK"
    
    print("=" * 50)
    print("  HERMES OBSERVABILITY DASHBOARD")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print()
    
    for name, check_fn in sections:
        status, details = check_fn()
        icon = status_icon(status)
        print(f"{icon} {name}")
        print(f"   {details}")
        print()
        
        if status == "CRITICAL":
            overall_status = "CRITICAL"
        elif status == "WARNING" and overall_status != "CRITICAL":
            overall_status = "WARNING"
    
    print("-" * 50)
    print(f"  Overall: {overall_status}")
    print("=" * 50)
    
    # Return exit code based on status
    if overall_status == "CRITICAL":
        return 2
    elif overall_status == "WARNING":
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(print_dashboard())
