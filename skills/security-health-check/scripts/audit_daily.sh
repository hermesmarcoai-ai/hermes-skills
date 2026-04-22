#!/bin/bash
# Daily Security Audit Script
# Runs every morning at 7 AM
# Checks for critical security issues

set -e

# Configuration
REPORT_DIR="/home/hermes/.hermes/reports"
AUDIT_LOG="/home/hermes/.hermes/logs/security_audit.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/audit_$TIMESTAMP.json"
ALERT_THRESHOLD_CRITICAL=1
ALERT_THRESHOLD_HIGH=2

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Initialize counters
ISSUES_CRITICAL=0
ISSUES_HIGH=0
ISSUES_MEDIUM=0
ISSUES_LOW=0

# Initialize report
cat > "$REPORT_FILE" << EOF
{
  "audit_type": "daily_security_audit",
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "scheduler_time": "07:00 UTC",
  "issues": {
    "critical": [],
    "high": [],
    "medium": [],
    "low": []
  },
  "status": "PENDING",
  "actions_taken": []
}
EOF

# Function to log
log_audit() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$AUDIT_LOG"
}

# Function to add issue to report
add_issue() {
    local severity="$1"
    local check="$2"
    local details="$3"
    local solution="$4"
    
    case "$severity" in
        critical)
            ((ISSUES_CRITICAL++))
            echo "    ${RED}[CRITICAL]${NC} $check: $details"
            ;;
        high)
            ((ISSUES_HIGH++))
            echo "    ${YELLOW}[HIGH]${NC} $check: $details"
            ;;
        medium)
            ((ISSUES_MEDIUM++))
            echo "    ${YELLOW}[MEDIUM]${NC} $check: $details"
            ;;
        low)
            ((ISSUES_LOW++))
            echo "    [INFO] $check: $details"
            ;;
    esac
    
    # Add to JSON report
    local json_entry=$(cat << ENTRY
    {
      "severity": "$severity",
      "check": "$check",
      "details": "$details",
      "solution": "$solution",
      "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    }
ENTRY
)
    
    # Update JSON file (append to appropriate array)
    local temp_file=$(mktemp)
    python3 << PYTHON
import json
import sys

with open("$REPORT_FILE", "r") as f:
    data = json.load(f)

data["issues"]["$severity"].append(json.loads("""$json_entry"""))

with open("$REPORT_FILE", "w") as f:
    json.dump(data, f, indent=2)
PYTHON
    rm -f "$temp_file"
}

echo "============================================"
echo "🛡️  DAILY SECURITY AUDIT - $TIMESTAMP"
echo "============================================"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S UTC')"
echo ""

log_audit "AUDIT" "Starting daily security audit"

# =============================================================================
# CHECK 1: Open Ports & Network Exposure
# =============================================================================
echo "1. Checking open ports and network exposure..."

# Get all listening ports
LISTENING_PORTS=$(ss -tlnp 2>/dev/null | grep LISTEN || echo "")

# Check for services bound to 0.0.0.0 (publicly exposed)
PUBLIC_PORTS=$(ss -tlnp 2>/dev/null | grep "0.0.0.0:" | grep -v "127.0.0.1" | wc -l)

if [ "$PUBLIC_PORTS" -gt 0 ]; then
    add_issue "critical" "Public Network Exposure" \
        "$PUBLIC_PORTS services listening on 0.0.0.0" \
        "Bind services to localhost (127.0.0.1) or restrict via firewall"
    
    ss -tlnp | grep "0.0.0.0:" >> "$AUDIT_LOG"
    log_audit "CRITICAL" "Found $PUBLIC_PORTS publicly exposed services"
else
    echo "    ${GREEN}✓${NC} No publicly exposed services"
    log_audit "INFO" "No public network exposure detected"
fi

# Check for unauthorized ports
UNAUTHORIZED_PORTS=("3000" "3001" "8080" "5000" "9000")
for port in "${UNAUTHORIZED_PORTS[@]}"; do
    if ss -tlnp | grep ":$port " | grep -v "127.0.0.1" > /dev/null 2>&1; then
        add_issue "high" "Unauthorized Port $port" \
            "Port $port is publicly accessible" \
            "Block via firewall or bind to localhost"
        log_audit "HIGH" "Unauthorized port $port detected"
    fi
done

# =============================================================================
# CHECK 2: Gateway Authentication & Binding
# =============================================================================
echo ""
echo "2. Checking Hermes Gateway security..."

# Check if gateway is running
if pgrep -f "hermes gateway" > /dev/null; then
    echo "    ${GREEN}✓${NC} Gateway is running"
    
    # Check binding to localhost
    if ss -tlnp | grep "127.0.0.1:8642" > /dev/null 2>&1; then
        echo "    ${GREEN}✓${NC} Gateway bound to localhost:8642"
    else
        add_issue "critical" "Gateway Not Localhost-Bound" \
            "Gateway not bound to 127.0.0.1:8642" \
            "Bind gateway to localhost: sed -i 's/bind_address.*/bind_address: \"127.0.0.1\"/' ~/.hermes/config.yaml"
        log_audit "CRITICAL" "Gateway not bound to localhost"
    fi
    
    # Check authentication
    if grep -q "require_auth.*true" /home/hermes/.hermes/config.yaml 2>/dev/null; then
        echo "    ${GREEN}✓${NC} Gateway authentication enabled"
    else
        add_issue "high" "Gateway Auth Disabled" \
            "Gateway authentication not enabled in config" \
            "Set require_auth: true in ~/.hermes/config.yaml"
        log_audit "HIGH" "Gateway auth disabled"
    fi
else
    add_issue "critical" "Gateway Not Running" \
        "Hermes Gateway process not found" \
        "Start gateway: hermes gateway run"
    log_audit "CRITICAL" "Gateway not running"
fi

# =============================================================================
# CHECK 3: SSH Configuration
# =============================================================================
echo ""
echo "3. Checking SSH configuration..."

SSH_CONFIG="/etc/ssh/sshd_config"

if [ -f "$SSH_CONFIG" ]; then
    # Check root login
    ROOT_LOGIN=$(grep "^PermitRootLogin" "$SSH_CONFIG" 2>/dev/null | grep -v "^#" | awk '{print $2}')
    if [ "$ROOT_LOGIN" = "no" ]; then
        echo "    ${GREEN}✓${NC} Root login disabled"
    else
        add_issue "critical" "SSH Root Login Enabled" \
            "PermitRootLogin is set to: $ROOT_LOGIN" \
            "Edit /etc/ssh/sshd_config: PermitRootLogin no"
        log_audit "CRITICAL" "SSH root login: $ROOT_LOGIN"
    fi
    
    # Check password authentication
    PASSWORD_AUTH=$(grep "^PasswordAuthentication" "$SSH_CONFIG" 2>/dev/null | grep -v "^#" | awk '{print $2}')
    if [ "$PASSWORD_AUTH" = "no" ]; then
        echo "    ${GREEN}✓${NC} Password authentication disabled"
    else
        add_issue "high" "SSH Password Auth Enabled" \
            "PasswordAuthentication is set to: $PASSWORD_AUTH" \
            "Edit /etc/ssh/sshd_config: PasswordAuthentication no"
        log_audit "HIGH" "SSH password auth: $PASSWORD_AUTH"
    fi
    
    # Check X11 forwarding
    X11_FWD=$(grep "^X11Forwarding" "$SSH_CONFIG" 2>/dev/null | grep -v "^#" | awk '{print $2}')
    if [ "$X11_FWD" = "no" ]; then
        echo "    ${GREEN}✓${NC} X11 forwarding disabled"
    else
        add_issue "medium" "X11 Forwarding Enabled" \
            "X11Forwarding is set to: $X11_FWD" \
            "Consider disabling: X11Forwarding no"
    fi
else
    add_issue "critical" "SSH Config Missing" \
        "SSH configuration file not found" \
        "Check: /etc/ssh/sshd_config exists"
    log_audit "CRITICAL" "SSH config missing"
fi

# =============================================================================
# CHECK 4: Firewall Status
# =============================================================================
echo ""
echo "4. Checking firewall configuration..."

FIREWALL_STATUS="unknown"
FIREWALL_RULES=0

if command -v ufw &>/dev/null; then
    if sudo ufw status 2>/dev/null | grep -q "Status: active"; then
        FIREWALL_STATUS="active"
        FIREWALL_RULES=$(sudo ufw status 2>/dev/null | grep "ALLOW" | wc -l)
        echo "    ${GREEN}✓${NC} Firewall active ($FIREWALL_RULES rules)"
    else
        FIREWALL_STATUS="inactive"
        add_issue "critical" "Firewall Inactive" \
            "UFW firewall is not active" \
            "Enable: sudo ufw enable"
        log_audit "CRITICAL" "Firewall inactive"
    fi
elif command -v iptables &>/dev/null; then
    FIREWALL_STATUS="iptables"
    FIREWALL_RULES=$(sudo iptables -L -n 2>/dev/null | wc -l)
    echo "    [INFO] Using iptables ($FIREWALL_RULES rules)"
else
    add_issue "high" "No Firewall Detected" \
        "Neither ufw nor iptables found" \
        "Install and configure firewall"
    log_audit "HIGH" "No firewall installed"
fi

# Check if SSH port is allowed
if [ "$FIREWALL_STATUS" = "active" ]; then
    if sudo ufw status 2>/dev/null | grep -q "22/tcp.*ALLOW"; then
        echo "    ${GREEN}✓${NC} SSH port (22) allowed"
    else
        add_issue "high" "SSH Not Allowed by Firewall" \
            "SSH port 22 not in firewall allowlist" \
            "Allow: sudo ufw allow 22/tcp"
        log_audit "HIGH" "SSH not allowed by firewall"
    fi
fi

# =============================================================================
# CHECK 5: Exposed Services
# =============================================================================
echo ""
echo "5. Checking for exposed services..."

EXPOSED_SERVICES=0

# Check for web servers on public IPs
if ss -tlnp | grep "0.0.0.0:80\|0.0.0.0:443" > /dev/null 2>&1; then
    add_issue "high" "Web Server Exposed" \
        "HTTP (80) or HTTPS (443) listening publicly" \
        "Configure reverse proxy or restrict access"
    ((EXPOSED_SERVICES++))
fi

# Check for database ports
DB_PORTS=("3306" "5432" "27017" "6379")
for port in "${DB_PORTS[@]}"; do
    if ss -tlnp | grep ":$port " | grep -v "127.0.0.1" > /dev/null 2>&1; then
        add_issue "critical" "Database Exposed" \
            "Database port $port is publicly accessible" \
            "Bind to localhost or configure firewall"
    fi
done

if [ $EXPOSED_SERVICES -eq 0 ]; then
    echo "    ${GREEN}✓${NC} No dangerous services exposed"
fi

# =============================================================================
# CHECK 6: Token Security
# =============================================================================
echo ""
echo "6. Checking token security..."

TOKEN_FILE="/etc/environment.d/hermes-env"

if [ -f "$TOKEN_FILE" ]; then
    TOKEN_PERMS=$(stat -c %a "$TOKEN_FILE" 2>/dev/null)
    if [ "$TOKEN_PERMS" = "600" ]; then
        echo "    ${GREEN}✓${NC} Token file permissions secure (600)"
    else
        add_issue "high" "Token File Permissions" \
            "Token file has permissions: $TOKEN_PERMS" \
            "Fix: chmod 600 $TOKEN_FILE"
        log_audit "HIGH" "Token permissions: $TOKEN_PERMS"
    fi
else
    add_issue "medium" "Token File Missing" \
        "Secure token file not found at $TOKEN_FILE" \
        "Create secure token storage"
fi

# =============================================================================
# CHECK 7: User Privilege
# =============================================================================
echo ""
echo "7. Checking user privileges..."

CURRENT_USER=$(whoami)

if [ "$CURRENT_USER" != "root" ]; then
    echo "    ${GREEN}✓${NC} Running as non-root user: $CURRENT_USER"
else
    add_issue "critical" "Running as Root" \
        "Script executed as root user" \
        "Switch to hermes user: su - hermes"
    log_audit "CRITICAL" "Running as root"
fi

# =============================================================================
# GENERATE REPORT
# =============================================================================
echo ""
echo "============================================"
echo "📊 AUDIT SUMMARY"
echo "============================================"

TOTAL_ISSUES=$((ISSUES_CRITICAL + ISSUES_HIGH + ISSUES_MEDIUM + ISSUES_LOW))

echo "Critical Issues: ${RED}$ISSUES_CRITICAL${NC}"
echo "High Issues:     ${YELLOW}$ISSUES_HIGH${NC}"
echo "Medium Issues:   ${YELLOW}$ISSUES_MEDIUM${NC}"
echo "Low Issues:      ${GREEN}$ISSUES_LOW${NC}"
echo "Total Issues:    $TOTAL_ISSUES"
echo ""

# Update status in JSON
python3 << PYTHON
import json

with open("$REPORT_FILE", "r") as f:
    data = json.load(f)

data["issues"]["critical"] = data["issues"]["critical"] if "critical" in data["issues"] else []
data["issues"]["high"] = data["issues"]["high"] if "high" in data["issues"] else []
data["issues"]["medium"] = data["issues"]["medium"] if "medium" in data["issues"] else []
data["issues"]["low"] = data["issues"]["low"] if "low" in data["issues"] else []

total_critical = len(data["issues"]["critical"])
total_high = len(data["issues"]["high"])
total_medium = len(data["issues"]["medium"])
total_low = len(data["issues"]["low"])

if total_critical > 0:
    data["status"] = "CRITICAL"
elif total_high > 0:
    data["status"] = "HIGH_RISK"
elif total_medium > 0:
    data["status"] = "MODERATE_RISK"
else:
    data["status"] = "HEALTHY"

with open("$REPORT_FILE", "w") as f:
    json.dump(data, f, indent=2)
PYTHON

echo "Report saved: $REPORT_FILE"
echo "Log saved: $AUDIT_LOG"
echo ""

# Notify if critical issues found
if [ $ISSUES_CRITICAL -gt 0 ]; then
    echo -e "${RED}⚠️  CRITICAL ISSUES DETECTED - AUTOMATIC FIXES SHOULD RUN AT 7:30AM${NC}"
    log_audit "CRITICAL" "Audit complete with $ISSUES_CRITICAL critical issues"
    exit 1
elif [ $ISSUES_HIGH -gt 0 ]; then
    echo -e "${YELLOW}⚠️  HIGH SEVERITY ISSUES DETECTED - REVIEW RECOMMENDED${NC}"
    log_audit "HIGH" "Audit complete with $ISSUES_HIGH high issues"
    exit 0
else
    echo -e "${GREEN}✓ AUDIT COMPLETE - NO CRITICAL ISSUES${NC}"
    log_audit "INFO" "Audit complete, no critical issues"
    exit 0
fi
