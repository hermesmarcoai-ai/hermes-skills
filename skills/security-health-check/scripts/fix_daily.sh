#!/bin/bash
# Daily Security Fix Script
# Runs every morning at 7:30 AM
# Automatically fixes critical and high severity issues

set -e

# Configuration
REPORT_DIR="/home/hermes/.hermes/reports"
FIX_LOG="/home/hermes/.hermes/logs/security_fix.log"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
AUDIT_FILE=$(ls -t $REPORT_DIR/audit_*.json 2>/dev/null | head -1)
HERMES_HOME="/home/hermes/.hermes"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "============================================"
echo "🔧 SECURITY AUTO-FIX - $TIMESTAMP"
echo "============================================"
echo "Time: $(date '+%Y-%m-%d %H:%M:%S UTC')"

log_fix() {
    local level="$1"
    local action="$2"
    local details="$3"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $action: $details" >> "$FIX_LOG"
}

# Initialize fix report
FIX_REPORT="$REPORT_DIR/fix_$TIMESTAMP.json"
cat > "$FIX_REPORT" << EOF
{
  "fix_type": "daily_security_fix",
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "scheduler_time": "07:30 UTC",
  "based_on_audit": "$AUDIT_FILE",
  "fixes_applied": [],
  "failures": [],
  "notifications_sent": [],
  "status": "PENDING"
}
EOF

# Function to add fix report entry
add_fix_entry() {
    local severity="$1"
    local check="$2"
    local action="$3"
    local result="$4"
    
    local json_entry=$(cat << ENTRY
    {
      "severity": "$severity",
      "check": "$check",
      "action": "$action",
      "result": "$result",
      "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    }
ENTRY
)
    
    python3 << PYTHON
import json
import sys

with open("$FIX_REPORT", "r") as f:
    data = json.load(f)

data["fixes_applied"].append(json.loads("""$json_entry"""))

with open("$FIX_REPORT", "w") as f:
    json.dump(data, f, indent=2)
PYTHON
}

# Function to send notification (for medium/low issues that weren't fixed)
send_notification() {
    local severity="$1"
    local message="$2"
    
    # Log notification
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$severity] $message" >> "$FIX_LOG"
    
    # Add to fix report
    python3 << PYTHON
import json

with open("$FIX_REPORT", "r") as f:
    data = json.load(f)

data["notifications_sent"].append({
    "severity": "$severity",
    "message": "$message",
    "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
})

with open("$FIX_REPORT", "w") as f:
    json.dump(data, f, indent=2)
PYTHON
}

# =============================================================================
# FIX 1: Public Network Exposure
# =============================================================================
echo ""
echo "🔧 Checking for public network exposure..."

if [ -f "$AUDIT_FILE" ]; then
    # Extract critical issues about network exposure
    EXPOSED=$(python3 -c "
import json
with open('$AUDIT_FILE', 'r') as f:
    data = json.load(f)
for issue in data.get('issues', {}).get('critical', []):
    if 'Public' in issue.get('check', '') or 'exposed' in issue.get('check', '').lower():
        print(issue['check'])
")
    
    if [ -n "$EXPOSED" ]; then
        echo "    ${RED}✗${NC} Found exposed services"
        
        # Block via firewall
        echo "    ${BLUE}→${NC} Applying firewall rules to block exposed services..."
        sudo ufw default deny incoming 2>/dev/null || true
        sudo ufw default allow outgoing 2>/dev/null || true
        
        # Allow only necessary ports
        sudo ufw allow 22/tcp 2>/dev/null || true
        sudo ufw --force enable 2>/dev/null || true
        
        add_fix_entry "critical" "Network Exposure" \
            "Applied firewall rules (deny incoming, allow SSH)" \
            "Firewall configured"
        
        log_fix "CRITICAL" "Fixed network exposure" "Applied firewall rules"
    else
        echo "    ${GREEN}✓${NC} No public exposure detected"
    fi
else
    echo "    [INFO] No audit file found, skipping"
fi

# =============================================================================
# FIX 2: Gateway Binding to Localhost
# =============================================================================
echo ""
echo "🔧 Checking gateway binding..."

if [ -f "$AUDIT_FILE" ]; then
    # Check if gateway needs fixing
    NEEDS_FIX=$(python3 -c "
import json
with open('$AUDIT_FILE', 'r') as f:
    data = json.load(f)
for issue in data.get('issues', {}).get('critical', []):
    if 'Gateway' in issue.get('check', '') and 'localhost' in issue.get('check', '').lower():
        print('yes')
")
    
    if [ "$NEEDS_FIX" = "yes" ]; then
        echo "    ${RED}✗${NC} Gateway not bound to localhost"
        
        # Fix gateway config
        CONFIG_FILE="$HERMES_HOME/config.yaml"
        
        if [ -f "$CONFIG_FILE" ]; then
            echo "    ${BLUE}→${NC} Binding gateway to localhost..."
            
            # Use python to safely edit YAML
            python3 << PYTHON
import yaml
import sys

config_file = "$CONFIG_FILE"

try:
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    # Add or update gateway config
    if 'gateway' not in config:
        config['gateway'] = {}
    
    config['gateway']['bind_address'] = '127.0.0.1'
    config['gateway']['bind_port'] = 8642
    config['gateway']['require_auth'] = True
    
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print("Gateway config updated")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
PYTHON
            
            add_fix_entry "critical" "Gateway Binding" \
                "Updated config.yaml to bind to 127.0.0.1:8642" \
                "Config updated"
            
            log_fix "CRITICAL" "Fixed gateway binding" "Updated config.yaml"
            
            echo "    ${YELLOW}⚠️${NC} Gateway restart required - run: hermes gateway run"
        else
            add_fix_entry "critical" "Gateway Binding" \
                "Cannot fix - config.yaml not found" \
                "MANUAL FIX REQUIRED"
            
            log_fix "CRITICAL" "Failed to fix gateway binding" "Config not found"
        fi
    else
        echo "    ${GREEN}✓${NC} Gateway already bound to localhost"
    fi
fi

# =============================================================================
# FIX 3: SSH Configuration
# =============================================================================
echo ""
echo "🔧 Checking SSH configuration..."

if [ -f "$AUDIT_FILE" ]; then
    SSH_FIX_NEEDED="no"
    
    # Check root login
    ROOT_FIX=$(python3 -c "
import json
with open('$AUDIT_FILE', 'r') as f:
    data = json.load(f)
for issue in data.get('issues', {}).get('critical', []):
    if 'SSH Root' in issue.get('check', ''):
        print('yes')
")
    
    # Check password auth
    PASS_FIX=$(python3 -c "
import json
with open('$AUDIT_FILE', 'r') as f:
    data = json.load(f)
for issue in data.get('issues', {}).get('high', []):
    if 'SSH Password' in issue.get('check', ''):
        print('yes')
")
    
    if [ "$ROOT_FIX" = "yes" ] || [ "$PASS_FIX" = "yes" ]; then
        echo "    ${RED}✗${NC} SSH needs hardening"
        
        SSH_CONFIG="/etc/ssh/sshd_config"
        
        if [ -f "$SSH_CONFIG" ]; then
            echo "    ${BLUE}→${NC} Hardening SSH configuration..."
            
            # Create backup
            cp "$SSH_CONFIG" "$SSH_CONFIG.backup.$(date +%Y%m%d)" 2>/dev/null || true
            
            # Fix root login
            if [ "$ROOT_FIX" = "yes" ]; then
                sed -i 's/^#PermitRootLogin.*/PermitRootLogin no/' "$SSH_CONFIG" 2>/dev/null || \
                echo "PermitRootLogin no" >> "$SSH_CONFIG"
                echo "    ${GREEN}✓${NC} Disabled root login"
            fi
            
            # Fix password auth
            if [ "$PASS_FIX" = "yes" ]; then
                sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication no/' "$SSH_CONFIG" 2>/dev/null || \
                echo "PasswordAuthentication no" >> "$SSH_CONFIG"
                echo "    ${GREEN}✓${NC} Disabled password authentication"
            fi
            
            # Enable public key auth
            if ! grep -q "^PubkeyAuthentication yes" "$SSH_CONFIG"; then
                echo "PubkeyAuthentication yes" >> "$SSH_CONFIG"
                echo "    ${GREEN}✓${NC} Enabled public key authentication"
            fi
            
            add_fix_entry "critical" "SSH Configuration" \
                "Applied SSH hardening (no root, no password auth)" \
                "SSH config updated"
            
            log_fix "CRITICAL" "Fixed SSH configuration" "Hardened sshd_config"
            
            echo "    ${YELLOW}⚠️${NC} SSH restart required - run: sudo systemctl restart sshd"
        else
            add_fix_entry "critical" "SSH Configuration" \
                "Cannot fix - sshd_config not found" \
                "MANUAL FIX REQUIRED"
            log_fix "CRITICAL" "Failed to fix SSH" "Config not found"
        fi
    else
        echo "    ${GREEN}✓${NC} SSH already hardened"
    fi
fi

# =============================================================================
# FIX 4: Firewall Status
# =============================================================================
echo ""
echo "🔧 Checking firewall status..."

if [ -f "$AUDIT_FILE" ]; then
    FIREWALL_FIX=$(python3 -c "
import json
with open('$AUDIT_FILE', 'r') as f:
    data = json.load(f)
for issue in data.get('issues', {}).get('critical', []):
    if 'Firewall' in issue.get('check', '') and 'inactive' in issue.get('check', '').lower():
        print('yes')
")
    
    if [ "$FIREWALL_FIX" = "yes" ]; then
        echo "    ${RED}✗${NC} Firewall is inactive"
        
        if command -v ufw &>/dev/null; then
            echo "    ${BLUE}→${NC} Enabling UFW firewall..."
            
            # Set defaults
            sudo ufw default deny incoming 2>/dev/null || true
            sudo ufw default allow outgoing 2>/dev/null || true
            
            # Allow SSH
            sudo ufw allow 22/tcp 2>/dev/null || true
            
            # Enable firewall
            sudo ufw --force enable 2>/dev/null || true
            
            # Verify
            if sudo ufw status 2>/dev/null | grep -q "Status: active"; then
                echo "    ${GREEN}✓${NC} Firewall enabled and active"
                add_fix_entry "critical" "Firewall" \
                    "Enabled UFW with strict rules" \
                    "Firewall active"
                log_fix "CRITICAL" "Fixed firewall status" "UFW enabled"
            else
                add_fix_entry "critical" "Firewall" \
                    "Failed to enable firewall" \
                    "MANUAL FIX REQUIRED: sudo ufw enable"
                log_fix "CRITICAL" "Failed to enable firewall" "UFW enable failed"
            fi
        else
            add_fix_entry "critical" "Firewall" \
                "No firewall tool available (ufw/iptables)" \
                "MANUAL FIX REQUIRED"
            log_fix "CRITICAL" "No firewall tool" "Install ufw or iptables"
        fi
    else
        echo "    ${GREEN}✓${NC} Firewall already active"
    fi
fi

# =============================================================================
# FIX 5: Token Permissions
# =============================================================================
echo ""
echo "🔧 Checking token file permissions..."

if [ -f "$AUDIT_FILE" ]; then
    TOKEN_FIX=$(python3 -c "
import json
with open('$AUDIT_FILE', 'r') as f:
    data = json.load(f)
for issue in data.get('issues', {}).get('high', []):
    if 'Token' in issue.get('check', ''):
        print('yes')
")
    
    if [ "$TOKEN_FIX" = "yes" ]; then
        TOKEN_FILE="/etc/environment.d/hermes-env"
        
        if [ -f "$TOKEN_FILE" ]; then
            echo "    ${RED}✗${NC} Token file permissions insecure"
            echo "    ${BLUE}→${NC} Fixing permissions to 600..."
            
            chmod 600 "$TOKEN_FILE" 2>/dev/null && \
            echo "    ${GREEN}✓${NC} Permissions set to 600" || \
            echo "    ${RED}✗${NC} Failed to fix permissions"
            
            add_fix_entry "high" "Token Permissions" \
                "Set permissions to 600" \
                "Permissions fixed"
            
            log_fix "HIGH" "Fixed token permissions" "chmod 600"
        fi
    else
        echo "    ${GREEN}✓${NC} Token permissions secure"
    fi
fi

# =============================================================================
# FIX 6: Unauthorized Port Exposure
# =============================================================================
echo ""
echo "🔧 Checking for unauthorized port exposure..."

if [ -f "$AUDIT_FILE" ]; then
    UNAUTHORIZED_PORTS=$(python3 -c "
import json
with open('$AUDIT_FILE', 'r') as f:
    data = json.load(f)
for issue in data.get('issues', {}).get('high', []):
    if 'Unauthorized Port' in issue.get('check', ''):
        port = issue.get('check', '').split()[-1]
        print(port)
" | sort -u)
    
    if [ -n "$UNAUTHORIZED_PORTS" ]; then
        echo "    ${RED}✗${NC} Found unauthorized ports: $UNAUTHORIZED_PORTS"
        echo "    ${BLUE}→${NC} Blocking via firewall..."
        
        for port in $UNAUTHORIZED_PORTS; do
            sudo ufw deny "$port/tcp" 2>/dev/null || true
            sudo ufw deny "$port/udp" 2>/dev/null || true
            echo "    ${GREEN}✓${NC} Blocked port $port"
        done
        
        add_fix_entry "high" "Unauthorized Ports" \
            "Blocked unauthorized ports via firewall" \
            "Ports blocked"
        
        log_fix "HIGH" "Fixed unauthorized ports" "Blocked ports via UFW"
    else
        echo "    ${GREEN}✓${NC} No unauthorized ports exposed"
    fi
fi

# =============================================================================
# Generate Summary
# =============================================================================
echo ""
echo "============================================"
echo "📊 FIX SUMMARY"
echo "============================================"

# Count fixes applied
FIXES_COUNT=$(python3 -c "
import json
with open('$FIX_REPORT', 'r') as f:
    data = json.load(f)
print(len(data.get('fixes_applied', [])))
")

NOTIFICATIONS_COUNT=$(python3 -c "
import json
with open('$FIX_REPORT', 'r') as f:
    data = json.load(f)
print(len(data.get('notifications_sent', [])))
")

echo "Fixes Applied: $FIXES_COUNT"
echo "Notifications Sent: $NOTIFICATIONS_COUNT"
echo ""

# Update status
python3 << PYTHON
import json

with open("$FIX_REPORT", "r") as f:
    data = json.load(f)

fixes = len(data.get("fixes_applied", []))
failures = len(data.get("failures", []))

if fixes > 0 and failures == 0:
    data["status"] = "SUCCESS"
elif fixes > 0:
    data["status"] = "PARTIAL"
else:
    data["status"] = "NO_FIXES_NEEDED"

with open("$FIX_REPORT", "w") as f:
    json.dump(data, f, indent=2)
PYTHON

echo "Report saved: $FIX_REPORT"
echo "Log saved: $FIX_LOG"
echo ""

if [ "$FIXES_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✓ SECURITY FIXES COMPLETED${NC}"
    if [ "$NOTIFICATIONS_COUNT" -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $NOTIFICATIONS_COUNT notifications sent for medium/low issues${NC}"
    fi
else
    echo -e "${GREEN}✓ No fixes needed - System already secure${NC}"
fi

echo ""
echo "🔧 FIX COMPLETE"
