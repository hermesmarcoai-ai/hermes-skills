#!/bin/bash
# Security Health Check Script
# Automated security verification for Hermes Agent

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
HERMES_HOME="${HERMES_HOME:-/home/hermes/.hermes}"
REPORTS_DIR="${HERMES_HOME}/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SCORE=0
TOTAL=8

# Arrays for tracking
declare -a CHECKS_PASSED=()
declare -a CHECKS_FAILED=()
declare -a WARNINGS=()

# Function to print status
print_header() {
    echo -e "${BLUE}=== HERMES SECURITY HEALTH CHECK ===${NC}"
    echo "Timestamp: $(date '+%Y-%m-%d %H:%M:%S UTC')"
    echo ""
}

print_check() {
    local name="$1"
    local status="$2"
    local details="$3"
    
    if [ "$status" = "PASS" ]; then
        echo -e "${GREEN}[✓]${NC} $name"
        [ -n "$details" ] && echo "      $details"
        CHECKS_PASSED+=("$name")
        ((SCORE++))
    elif [ "$status" = "WARN" ]; then
        echo -e "${YELLOW}[!]${NC} $name"
        [ -n "$details" ] && echo "      $details"
        WARNINGS+=("$name: $details")
    else
        echo -e "${RED}[✗]${NC} $name"
        [ -n "$details" ] && echo "      $details"
        CHECKS_FAILED+=("$name")
    fi
}

# Check 1: User privilege
check_user_privilege() {
    local user=$(whoami)
    if [ "$user" != "root" ]; then
        print_check "User Privilege" "PASS" "Running as: $user"
    else
        print_check "User Privilege" "FAIL" "Running as ROOT!"
    fi
}

# Check 2: SSH hardening
check_ssh() {
    local ssh_config="/etc/ssh/sshd_config"
    local root_login=$(grep "^PermitRootLogin" $ssh_config 2>/dev/null | grep -v "^#" | awk '{print $2}')
    local password_auth=$(grep "^PasswordAuthentication" $ssh_config 2>/dev/null | grep -v "^#" | awk '{print $2}')
    
    if [ "$root_login" = "no" ] && [ "$password_auth" = "no" ]; then
        print_check "SSH Hardening" "PASS" "Root login: disabled, Password auth: disabled"
    elif [ "$root_login" = "no" ] || [ "$password_auth" = "no" ]; then
        print_check "SSH Hardening" "WARN" "Root: $root_login, Password: $password_auth"
    else
        print_check "SSH Hardening" "FAIL" "Insecure SSH configuration"
    fi
}

# Check 3: Firewall status
check_firewall() {
    local firewall_status="unknown"
    
    if command -v ufw &>/dev/null; then
        if sudo ufw status 2>/dev/null | grep -q "Status: active"; then
            firewall_status="active"
        else
            firewall_status="inactive"
        fi
    elif command -v iptables &>/dev/null; then
        firewall_status="iptables (manual check needed)"
    fi
    
    if [ "$firewall_status" = "active" ]; then
        print_check "Firewall Status" "PASS" "$firewall_status"
    else
        print_check "Firewall Status" "WARN" "$firewall_status"
    fi
}

# Check 4: Token security
check_token_security() {
    local token_file="/etc/environment.d/hermes-env"
    local permissions=""
    
    if [ -f "$token_file" ]; then
        permissions=$(stat -c %a "$token_file" 2>/dev/null || echo "unknown")
        
        if [ "$permissions" = "600" ]; then
            print_check "Token Security" "PASS" "Permissions: $permissions"
        elif [ "$permissions" -le 640 ] 2>/dev/null; then
            print_check "Token Security" "WARN" "Permissions: $permissions (should be 600)"
        else
            print_check "Token Security" "FAIL" "Permissions: $permissions (too open!)"
        fi
    else
        print_check "Token Security" "WARN" "Token file not found"
    fi
}

# Check 5: Command allowlist
check_command_allowlist() {
    local allowlist_file="$HERMES_HOME/exec-approvals.json"
    
    if [ -f "$allowlist_file" ]; then
        # Check if DENY policy exists
        if grep -q '"default_policy":\s*"DENY"' "$allowlist_file" 2>/dev/null; then
            print_check "Command Allowlist" "PASS" "DENY policy active"
        else
            print_check "Command Allowlist" "WARN" "Policy not DENY"
        fi
    else
        print_check "Command Allowlist" "FAIL" "File not found"
    fi
}

# Check 6: User allowlist
check_user_allowlist() {
    local allowlist_file="$HERMES_HOME/exec-approvals.json"
    local marco_id="1486248213559250995"
    
    if [ -f "$allowlist_file" ]; then
        if grep -q "$marco_id" "$allowlist_file" 2>/dev/null; then
            print_check "User Allowlist" "PASS" "Marco's ID enforced"
        else
            print_check "User Allowlist" "WARN" "Marco's ID not in allowlist"
        fi
    else
        print_check "User Allowlist" "FAIL" "File not found"
    fi
}

# Check 7: Gateway binding
check_gateway_binding() {
    local binding=$(ss -tlnp 2>/dev/null | grep "127.0.0.1:8642" | wc -l)
    
    if [ "$binding" -gt 0 ]; then
        print_check "Gateway Binding" "PASS" "Bound to localhost:8642"
    else
        print_check "Gateway Binding" "WARN" "Not bound to localhost"
    fi
}

# Check 8: SOUL.md rules
check_soul_md() {
    local soul_file="$HERMES_HOME/SOUL.md"
    
    if [ -f "$soul_file" ]; then
        # Check if critical rules exist
        local rules_found=0
        grep -q "NEVER:" "$soul_file" && ((rules_found++))
        grep -q "ALWAYS:" "$soul_file" && ((rules_found++))
        grep -q "prompt injection" "$soul_file" && ((rules_found++))
        
        if [ "$rules_found" -ge 2 ]; then
            print_check "Security Rules (SOUL.md)" "PASS" "Rules loaded ($rules_found/3 checks)"
        else
            print_check "Security Rules (SOUL.md)" "WARN" "Incomplete rules ($rules_found/3 checks)"
        fi
    else
        print_check "Security Rules (SOUL.md)" "FAIL" "File not found"
    fi
}

# Calculate and display score
print_score() {
    local percentage=$(( (SCORE * 100) / TOTAL ))
    
    echo ""
    echo -e "${BLUE}=== SECURITY SCORE ===${NC}"
    echo "Passed: $SCORE/$TOTAL checks"
    echo "Score: ${GREEN}${percentage}%${NC}"
    echo ""
    
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo -e "${YELLOW}WARNINGS:${NC}"
        for warning in "${WARNINGS[@]}"; do
            echo "  ⚠️  $warning"
        done
        echo ""
    fi
    
    if [ ${#CHECKS_FAILED[@]} -gt 0 ]; then
        echo -e "${RED}FAILED CHECKS:${NC}"
        for failed in "${CHECKS_FAILED[@]}"; do
            echo "  ✗ $failed"
        done
        echo ""
    fi
}

# Generate JSON report
generate_json_report() {
    local report_file="$REPORTS_DIR/security_report_${TIMESTAMP}.json"
    mkdir -p "$REPORTS_DIR"
    
    cat > "$report_file" << EOF
{
  "timestamp": "$(date -u '+%Y-%m-%dT%H:%M:%SZ')",
  "score": ${SCORE},
  "total": ${TOTAL},
  "percentage": $(( (SCORE * 100) / TOTAL )),
  "status": "$([ ${#CHECKS_FAILED[@]} -eq 0 ] && echo 'HEALTHY' || echo 'DEGRADED')",
  "checks": {
    "user_privilege": "${CHECKS_PASSED[0]:-FAILED}",
    "ssh_hardening": "${CHECKS_PASSED[1]:-FAILED}",
    "firewall_status": "${CHECKS_PASSED[2]:-FAILED}",
    "token_security": "${CHECKS_PASSED[3]:-FAILED}",
    "command_allowlist": "${CHECKS_PASSED[4]:-FAILED}",
    "user_allowlist": "${CHECKS_PASSED[5]:-FAILED}",
    "gateway_binding": "${CHECKS_PASSED[6]:-FAILED}",
    "security_rules": "${CHECKS_PASSED[7]:-FAILED}"
  },
  "warnings": [$(printf '"%s",' "${WARNINGS[@]}" | sed 's/,$//')],
  "failures": [$(printf '"%s",' "${CHECKS_FAILED[@]}" | sed 's/,$//')]
}
EOF
    
    echo -e "${BLUE}Report saved: ${report_file}${NC}"
}

# Main execution
main() {
    print_header
    
    check_user_privilege
    check_ssh
    check_firewall
    check_token_security
    check_command_allowlist
    check_user_allowlist
    check_gateway_binding
    check_soul_md
    
    print_score
    
    # Generate report
    generate_json_report
    
    # Exit with appropriate code
    if [ ${#CHECKS_FAILED[@]} -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# Run main
main "$@"
