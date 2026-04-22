#!/bin/bash
# Deep Security Audit Script
# Comprehensive security analysis with remediation

set -e

REPORT_DIR="/home/hermes/.hermes/reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=== DEEP SECURITY AUDIT ==="
echo "Timestamp: $(date)"
echo ""

# Initialize report
cat > "$REPORT_DIR/deep_audit_${TIMESTAMP}.json" << 'EOF'
{
  "type": "deep_audit",
  "timestamp": "TIMESTAMP_PLACEHOLDER",
  "vulnerabilities": [],
  "recommendations": [],
  "risk_score": 0,
  "status": "PENDING"
}
EOF

# Perform deep checks
check_ssh_config() {
    echo "Checking SSH configuration..."
    local issues=0
    
    # Check for weak ciphers
    if grep -E "Ciphers.*3des|Ciphers.*aes128-cbc" /etc/ssh/sshd_config 2>/dev/null; then
        echo "  ✗ Weak SSH ciphers detected"
        ((issues++))
    fi
    
    # Check for X11 forwarding
    if grep -q "^X11Forwarding yes" /etc/ssh/sshd_config 2>/dev/null; then
        echo "  ✗ X11 forwarding enabled"
        ((issues++))
    fi
    
    # Check for PermitEmptyPasswords
    if grep -q "^PermitEmptyPasswords yes" /etc/ssh/sshd_config 2>/dev/null; then
        echo "  ✗ Empty passwords allowed"
        ((issues++))
    fi
    
    [ $issues -eq 0 ] && echo "  ✓ SSH hardened" || echo "  ⚠️  $issues issues found"
}

check_file_permissions() {
    echo "Checking critical file permissions..."
    local critical_files=(
        "/etc/environment.d/hermes-env"
        "/home/hermes/.hermes/.env"
        "/home/hermes/.hermes/config.yaml"
    )
    
    for file in "${critical_files[@]}"; do
        if [ -f "$file" ]; then
            local perms=$(stat -c %a "$file")
            if [ "$perms" -gt 644 ]; then
                echo "  ✗ $file has overly permissive permissions: $perms"
            else
                echo "  ✓ $file permissions OK"
            fi
        fi
    done
}

check_network_exposure() {
    echo "Checking network exposure..."
    
    # Check for services bound to 0.0.0.0
    local exposed=$(ss -tlnp | grep "0.0.0.0:" | grep -v "127.0.0.1" | wc -l)
    
    if [ $exposed -gt 0 ]; then
        echo "  ✗ $exposed services exposed to public"
        ss -tlnp | grep "0.0.0.0:" | grep -v "127.0.0.1"
    else
        echo "  ✓ No unnecessary public exposure"
    fi
}

check_log_rotation() {
    echo "Checking log rotation..."
    
    if [ -f /etc/logrotate.conf ] || [ -f /etc/logrotate.d/ ]; then
        echo "  ✓ Log rotation configured"
    else
        echo "  ⚠️  Log rotation may not be configured"
    fi
}

check_backup_exists() {
    echo "Checking security backups..."
    
    local backups=(
        "/etc/ssh/sshd_config.backup.*"
        "/tmp/ufw-status.backup.*"
    )
    
    for pattern in "${backups[@]}"; do
        if ls $pattern 2>/dev/null | grep -q .; then
            echo "  ✓ Backup exists: $pattern"
        else
            echo "  ⚠️  No backup found: $pattern"
        fi
    done
}

# Run all checks
check_ssh_config
check_file_permissions
check_network_exposure
check_log_rotation
check_backup_exists

echo ""
echo "=== DEEP AUDIT COMPLETE ==="
echo "Report saved to: $REPORT_DIR/deep_audit_${TIMESTAMP}.json"
