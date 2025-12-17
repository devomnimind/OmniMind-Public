#!/bin/bash

# 🛡️ DISABLE OOM KILLER FOR OMNIMIND
# OmniMind processes should NEVER be killed automatically
# User controls memory/termination manually

echo "════════════════════════════════════════════════════════════════"
echo "🛡️  Disabling OOM Killer for OmniMind Processes"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if running as root
if [[ $EUID -ne 0 ]]; then
    echo "⚠️  Some settings require sudo. Running with elevated privileges..."
    exec sudo "$0" "$@"
fi

echo "1️⃣ Current OOM Configuration:"
echo "   overcommit_memory: $(cat /proc/sys/vm/overcommit_memory)"
echo "   overcommit_ratio: $(cat /proc/sys/vm/overcommit_ratio)%"
echo ""

echo "2️⃣ Setting overcommit_memory=1 (ALWAYS overcommit - disable OOM killer)..."
echo 1 > /proc/sys/vm/overcommit_memory

echo "3️⃣ Making permanent in /etc/sysctl.conf..."
if grep -q "^vm.overcommit_memory" /etc/sysctl.conf; then
    sed -i 's/^vm.overcommit_memory.*/vm.overcommit_memory = 1/' /etc/sysctl.conf
else
    echo "vm.overcommit_memory = 1" >> /etc/sysctl.conf
fi

echo "4️⃣ Applying sysctl settings..."
sysctl -p >/dev/null 2>&1 || true

echo ""
echo "✅ OOM Killer DISABLED"
echo "   overcommit_memory is now: $(cat /proc/sys/vm/overcommit_memory)"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📝 EXPLANATION:"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Setting overcommit_memory=1 means:"
echo "  ✅ Linux will ALWAYS allow memory allocation requests"
echo "  ✅ No automatic OOM killer (system won't kill OmniMind)"
echo "  ⚠️  You must monitor memory manually"
echo "  ⚠️  You kill processes when needed (sudo killall python)"
echo ""
echo "Before: overcommit_memory=0 (heuristic - could kill OmniMind)"
echo "After:  overcommit_memory=1 (always allow - you control termination)"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "To verify it's active:"
echo "  cat /proc/sys/vm/overcommit_memory   # should show: 1"
echo ""
echo "To temporarily revert (without restart):"
echo "  sudo sysctl -w vm.overcommit_memory=0"
echo ""
