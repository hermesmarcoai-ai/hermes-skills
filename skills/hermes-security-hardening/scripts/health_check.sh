#!/bin/bash
# Quick Security Health Check for Hermes Agent

echo "🛡️  HERMES SECURITY HEALTH CHECK"
echo "================================="
echo ""

echo -n "1. Running as non-root: "
[ "$(whoami)" != "root" ] && echo "✅ PASS" || echo "❌ FAIL (WARNING: running as root!)"

echo -n "2. SSH hardened (root no, password no): "
grep -q "^PermitRootLogin no" /etc/ssh/sshd_config && grep -q "^PasswordAuthentication no" /etc/ssh/sshd_config && echo "✅ PASS" || echo "❌ FAIL"

echo -n "3. Firewall active: "
sudo ufw status 2>/dev/null | grep -q "Status: active" && echo "✅ PASS" || echo "⚠️  WARNING"

echo -n "4. Token file secure (600 perms): "
[ -f /etc/environment.d/hermes-env ] && [ "$(stat -c %a /etc/environment.d/hermes-env 2>/dev/null)" = "600" ] && echo "✅ PASS" || echo "❌ FAIL"

echo -n "5. Gateway localhost-only: "
ss -tlnp 2>/dev/null | grep "127.0.0.1:8642" > /dev/null && echo "✅ PASS" || echo "❌ FAIL"

echo -n "6. exec-approvals.json exists: "
[ -f /root/.hermes/exec-approvals.json ] && [ "$(stat -c %a /root/.hermes/exec-approvals.json 2>/dev/null)" = "600" ] && echo "✅ PASS" || echo "❌ FAIL"

echo -n "7. SOUL.md exists: "
[ -f /root/.hermes/SOUL.md ] && echo "✅ PASS" || echo "❌ FAIL"

echo -n "8. User allowlist set: "
grep -q "1486248213559250995" /root/.hermes/exec-approvals.json 2>/dev/null && echo "✅ PASS" || echo "❌ FAIL"

echo ""
echo "================================="
echo "Check complete!"
echo ""
[ "$(whoami)" = "root" ] && echo "🚨 ACTION REQUIRED: Switch to hermes user!" || echo "✅ Running as hermes user"
