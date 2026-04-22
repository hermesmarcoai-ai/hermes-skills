#!/bin/bash
# Security Monitoring Script
# Continuous monitoring with automated alerts

set -e

# Configuration
HERMES_HOME="${HERMES_HOME:-/home/hermes/.hermes}"
SCRIPT="$HERMES_HOME/skills/security-health-check/scripts/health_check.sh"
REPORTS_DIR="$HERMES_HOME/reports"
ALERT_CHANNEL="${ALERT_CHANNEL:-discord}"
HERMES_USER_ID="1486248213559250995"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Alert threshold
THRESHOLD_WARNING=90
THRESHOLD_CRITICAL=80

# Get current score from last report
get_current_score() {
    local latest_report=$(ls -t $REPORTS_DIR/security_report_*.json 2>/dev/null | head -1)
    if [ -f "$latest_report" ]; then
        grep -o '"score": [0-9]*' "$latest_report" | grep -o '[0-9]*'
    else
        echo "0"
    fi
}

# Send Discord alert
send_discord_alert() {
    local severity="$1"
    local message="$2"
    local score="$3"
    
    # Get bot token from environment
    local token=$(grep DISCORD_BOT_TOKEN /etc/environment.d/hermes-env 2>/dev/null | cut -d'=' -f2-)
    
    local embed="{\"embeds\": [{\"title\": \"🚨 Security Alert\", \"color\": $( [ \"$severity\" = \"CRITICAL\" ] && echo 16711680 || echo 16776960 ), \"fields\": [{\"name\": \"Status\", \"value\": \"$severity\", \"inline\": true}, {\"name\": \"Score\", \"value\": \"${score}%\", \"inline\": true}, {\"name\": \"Message\", \"value\": \"$message\", \"inline\": false}], \"footer\": {\"text\": \"Hermes Security Monitor\"}, \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}]}"
    
    curl -s -X POST "https://discord.com/api/webhooks/WEBHOOK_ID" \
         -H "Content-Type: application/json" \
         -d "$embed" 2>/dev/null || echo "Discord webhook failed"
}

# Send Telegram alert
send_telegram_alert() {
    local severity="$1"
    local message="$2"
    local score="$3"
    
    local token=$(grep TELEGRAM_BOT_TOKEN ~/.hermes/.env 2>/dev/null | cut -d'=' -f2-)
    local chat_id=$(grep TELEGRAM_CHAT_ID ~/.hermes/.env 2>/dev/null | cut -d'=' -f2-)
    
    local text="🚨 *Security Alert*\n\nSeverity: *$severity*\nScore: ${score}%\n\n$message"
    
    curl -s -X POST "https://api.telegram.org/bot$token/sendMessage" \
         -d "chat_id=$chat_id&text=$(echo -e "$text")&parse_mode=Markdown" 2>/dev/null || echo "Telegram failed"
}

# Send notification based on channel
send_alert() {
    local severity="$1"
    local message="$2"
    local score="$3"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] Sending $severity alert: $message"
    
    case "$ALERT_CHANNEL" in
        discord)
            send_discord_alert "$severity" "$message" "$score"
            ;;
        telegram)
            send_telegram_alert "$severity" "$message" "$score"
            ;;
        local)
            # Log to file and print
            echo "[$severity] $message (Score: ${score}%)" >> $HERMES_HOME/logs/security_alerts.log
            echo -e "${RED}[$severity] $message${NC}"
            ;;
        *)
            echo "Unknown alert channel: $ALERT_CHANNEL"
            ;;
    esac
}

# Run health check and evaluate
run_monitoring() {
    local score=$(get_current_score)
    local new_score=0
    
    echo "=== Running Security Monitoring ==="
    echo "Current score: ${score}%"
    
    # Run health check (redirect output to avoid noise)
    if [ -f "$SCRIPT" ]; then
        echo "Running health check..."
        
        # Capture output to analyze
        local output=$($SCRIPT 2>&1)
        new_score=$(echo "$output" | grep -o "Score: [0-9]*%" | grep -o '[0-9]*' || echo "0")
        
        # Check for failures
        if echo "$output" | grep -q "\[✗\]"; then
            send_alert "CRITICAL" "Security checks failed" "$new_score"
        fi
    else
        send_alert "CRITICAL" "Health check script not found" "0"
        return 1
    fi
    
    echo "New score: ${new_score}%"
    
    # Determine alert level
    if [ "$new_score" -lt "$THRESHOLD_CRITICAL" ]; then
        send_alert "CRITICAL" "Security score critically low" "$new_score"
    elif [ "$new_score" -lt "$THRESHOLD_WARNING" ]; then
        send_alert "WARNING" "Security score below threshold" "$new_score"
    else
        echo -e "${GREEN}✓ Security checks passed (Score: ${new_score}%)${NC}"
    fi
    
    # Archive report
    mkdir -p $REPORTS_DIR
    if [ -f "$REPORTS_DIR/security_report_${TIMESTAMP}.json" ]; then
        cp "$REPORTS_DIR/security_report_${TIMESTAMP}.json" \
           "$REPORTS_DIR/security_archive_$(date +%Y%m).json" 2>/dev/null || true
    fi
    
    return 0
}

# Main
if [ "$1" = "--help" ]; then
    echo "Security Monitoring Script"
    echo "Usage: $0 [--daily|--hourly|--once]"
    echo ""
    echo "Options:"
    echo "  --daily   Run daily at 6AM (default)"
    echo "  --hourly  Run every hour"
    echo "  --once    Run once and exit"
    exit 0
fi

# Run based on schedule
case "$1" in
    --daily)
        echo "Monitoring: Daily at 6AM"
        run_monitoring
        ;;
    --hourly)
        echo "Monitoring: Every hour"
        run_monitoring
        ;;
    --once)
        echo "Monitoring: One-time check"
        run_monitoring
        ;;
    *)
        run_monitoring
        ;;
esac
