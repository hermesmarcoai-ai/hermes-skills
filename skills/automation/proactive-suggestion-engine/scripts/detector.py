#!/usr/bin/env python3
"""
proactive_suggestion_detector.py
Scans logs for failure patterns and generates investigation suggestions.
"""

import os
import re
import json
from datetime import datetime, timedelta
from collections import defaultdict
from pathlib import Path

LOG_DIR = Path("~/.hermes/logs").expanduser()
STATE_FILE = Path("~/.hermes/.failure_patterns.json").expanduser()
CONFIDENCE_THRESHOLDS = {"low": 1, "medium": 3, "high": 5}

# Error patterns to track (regex, label)
# Order matters — more specific patterns first
PATTERNS = [
    (r"Gateway.*down|tui_gateway.*not responding", "gateway_down"),
    (r"ETIMEDOUT.*api\.telegram\.org|telegram.*ETIMEDOUT", "telegram_timeout"),
    (r"ETIMEDOUT", "network_timeout"),
    (r"ConnectionRefused", "connection_refused"),
    (r"max_iterations", "subagent_max_iterations"),
    (r"exit code 1$", "cron_predicate_failed"),
    (r"predicate.*failed", "predicate_failure"),
    (r"shell:.*exit code 1", "shell_predicate_failed"),
    (r"403 Forbidden", "api_403"),
    (r"401 Unauthorized", "api_401"),
    (r"500 Server Error", "api_500"),
    (r"rate.limit|rate_limit", "api_rate_limit"),
    (r"SyntaxError|ImportError|NameError", "python_error"),
]


def parse_logs():
    """Scan recent log files for error patterns."""
    occurrences = defaultdict(list)  # pattern_label -> [(timestamp, context), ...]

    if not LOG_DIR.exists():
        return occurrences

    # Get recent log files (last 24h)
    cutoff = datetime.now() - timedelta(hours=24)

    for log_file in LOG_DIR.glob("*.log"):
        try:
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff:
                continue
        except:
            continue

        try:
            content = log_file.read_text(errors="ignore")
        except:
            continue

        # Extract error lines with context
        for i, line in enumerate(content.splitlines()):
            if not line.strip():
                continue

            for pattern_regex, label in PATTERNS:
                if re.search(pattern_regex, line, re.IGNORECASE):
                    # Get timestamp from line or use file mtime
                    ts_match = re.match(r"\[([\d-]+ [\d:]+)\]", line)
                    ts = ts_match.group(1) if ts_match else mtime.isoformat()

                    # Get surrounding context (3 lines before/after)
                    lines = content.splitlines()
                    ctx_start = max(0, i - 3)
                    ctx_end = min(len(lines), i + 4)
                    context = "\n".join(lines[ctx_start:ctx_end])[:200]

                    occurrences[label].append({
                        "timestamp": ts,
                        "file": log_file.name,
                        "context": context,
                        "line": line[:150]
                    })
                    break  # Only count each line once

    return occurrences


def analyze_patterns(occurrences):
    """Analyze occurrences and generate suggestions."""
    suggestions = []

    for label, events in occurrences.items():
        count = len(events)
        if count < CONFIDENCE_THRESHOLDS["low"]:
            continue

        # Determine confidence
        if count >= CONFIDENCE_THRESHOLDS["high"]:
            confidence = "high"
            severity = "🔴"
        elif count >= CONFIDENCE_THRESHOLDS["medium"]:
            confidence = "medium"
            severity = "⚠️"
        else:
            confidence = "low"
            severity = "ℹ️"

        # Get last occurrence
        last = events[-1]

        # Generate hypothesis based on pattern type
        hypotheses = {
            "gateway_down": "Messaging gateway unreachable — check if process is running and network accessible",
            "telegram_timeout": "Telegram API timeout — network issue specific to api.telegram.org (known issue on Surface)",
            "network_timeout": "Network connectivity issue — check firewall, DNS, or VPN",
            "connection_refused": "Service not running or port blocked — verify service status",
            "subagent_max_iterations": "Task too complex for default iteration limit — increase max_iterations or break into smaller tasks",
            "cron_predicate_failed": "Cron predicate returned failure — conditional job was skipped as expected",
            "predicate_failure": "Cron predicate evaluation failed — check predicate syntax in cron-wrapper",
            "shell_predicate_failed": "Shell predicate returned non-zero exit — predicate logic issue",
            "api_403": "API forbidden — check API key validity or permissions",
            "api_401": "API unauthorized — authentication credentials issue",
            "api_500": "API server error — upstream service issue, retry later",
            "api_rate_limit": "API rate limited — back off and retry with exponential delay",
            "python_error": "Python runtime error — syntax or import issue in script",
        }

        hypothesis = hypotheses.get(label, "Unknown failure pattern — requires investigation")

        # Get unique contexts
        unique_contexts = len(set(e["context"][:50] for e in events))

        suggestion = {
            "label": label,
            "severity": severity,
            "confidence": confidence,
            "count": count,
            "last_seen": last["timestamp"],
            "last_file": last["file"],
            "last_context": last["context"][:200],
            "hypothesis": hypothesis,
            "unique_events": unique_contexts,
            "recommend_investigation": confidence in ("high", "medium"),
            "suggestion_text": f"{severity} Pattern detected: **{label.replace('_', ' ')}**\n\nSeen: {count}x in recent logs\nLast seen: {last['timestamp']}\nHypothesis: {hypothesis}"
        }

        if unique_contexts < count * 0.3:
            suggestion["suggestion_text"] += f"\n⚠️ Same error in {unique_contexts} distinct forms — may be cascading failure"

        suggestions.append(suggestion)

    # Sort by confidence then count
    suggestions.sort(key=lambda x: (
        {"high": 0, "medium": 1, "low": 2}[x["confidence"]],
        -x["count"]
    ))

    return suggestions


def load_previous_state():
    """Load previously seen patterns to avoid duplicate spam."""
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            pass
    return {}


def save_state(suggestions):
    """Save seen patterns to avoid re-notifying."""
    state = {}
    for s in suggestions:
        state[s["label"]] = {
            "count": s["count"],
            "last_notified": datetime.now().isoformat(),
            "notified": s["recommend_investigation"]
        }
    try:
        STATE_FILE.write_text(json.dumps(state, indent=2))
    except:
        pass


def generate_report():
    """Generate full report."""
    occurrences = parse_logs()
    suggestions = analyze_patterns(occurrences)

    report_lines = ["## 🔍 Proactive Health Scan\n"]

    if not suggestions:
        report_lines.append("✅ No significant failure patterns detected in recent logs.")
        return "\n".join(report_lines)

    report_lines.append(f"Found {len(suggestions)} pattern(s):\n")

    for s in suggestions:
        report_lines.append(s["suggestion_text"])
        report_lines.append("")

    save_state(suggestions)

    # Add investigation offers for high/medium confidence
    actionable = [s for s in suggestions if s["recommend_investigation"]]
    if actionable:
        report_lines.append("---")
        report_lines.append("**Recommended actions:**")
        for s in actionable[:3]:
            report_lines.append(f"- `{s['label']}` — {s['hypothesis']}")

    return "\n".join(report_lines)


if __name__ == "__main__":
    import sys

    if "--json" in sys.argv:
        occurrences = parse_logs()
        suggestions = analyze_patterns(occurrences)
        print(json.dumps(suggestions, indent=2, default=str))
    else:
        print(generate_report())
