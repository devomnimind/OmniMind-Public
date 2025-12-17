#!/bin/bash

# 🎯 OPTIMIZE UBUNTU FOR OMNIMIND DEVELOPMENT ENVIRONMENT
# ============================================================
# Otimizações para Ubuntu focando em:
# - Prioridade para serviços OmniMind
# - QoS de rede para downloads VS Code
# - Performance geral de desenvolvimento
#
# Não mexe em GPU (CUDA sendo recompilada)

set -e

PROJECT_ROOT="${1:-/home/fahbrain/projects/omnimind}"
NETWORK_INTERFACE="${2:-enp7s0}"  # Detectar automaticamente se possível

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  🎯 OPTIMIZING UBUNTU FOR OMNIMIND DEV ENVIRONMENT           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# ===== DETECT NETWORK INTERFACE =====
if [ "$NETWORK_INTERFACE" = "auto" ]; then
    NETWORK_INTERFACE=$(ip route | grep default | awk '{print $5}' | head -1)
    if [ -z "$NETWORK_INTERFACE" ]; then
        echo "❌ Could not detect network interface"
        exit 1
    fi
fi

echo "📡 Using network interface: $NETWORK_INTERFACE"
echo ""

# ===== 1. CPU GOVERNOR OPTIMIZATION =====
echo "⚡ 1. Optimizing CPU governor for performance..."
echo ""

# Set all CPUs to performance governor
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance | sudo tee "$cpu" > /dev/null
done

echo "✅ CPU governor set to performance"
echo ""

# ===== 2. KERNEL PARAMETERS OPTIMIZATION =====
echo "🔧 2. Optimizing kernel parameters..."
echo ""

# Reduce swappiness for better memory management (keep some for desktop)
sudo sysctl -w vm.swappiness=10

# Optimize dirty ratios for SSD
sudo sysctl -w vm.dirty_ratio=10
sudo sysctl -w vm.dirty_background_ratio=5

# Optimize for NVMe/SSD
sudo sysctl -w vm.dirty_writeback_centisecs=1500

# Network optimizations
sudo sysctl -w net.core.rmem_max=16777216
sudo sysctl -w net.core.wmem_max=16777216
sudo sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"
sudo sysctl -w net.ipv4.tcp_wmem="4096 65536 16777216"
sudo sysctl -w net.ipv4.tcp_congestion_control=bbr

# Make persistent
sudo tee -a /etc/sysctl.conf > /dev/null << 'EOF'

# OmniMind Development Optimizations
vm.swappiness=10
vm.dirty_ratio=10
vm.dirty_background_ratio=5
vm.dirty_writeback_centisecs=1500
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 87380 16777216
net.ipv4.tcp_wmem=4096 65536 16777216
net.ipv4.tcp_congestion_control=bbr
EOF

echo "✅ Kernel parameters optimized"
echo ""

# ===== 3. NETWORK QoS FOR VS CODE DOWNLOADS =====
echo "🌐 3. Setting up QoS for VS Code downloads..."
echo ""

# Remove existing qdisc
sudo tc qdisc del dev "$NETWORK_INTERFACE" root 2>/dev/null || true

# Create HTB qdisc with 3 classes:
# 1:1 - Highest priority (VS Code downloads, ports 80,443)
# 1:2 - High priority (OmniMind services)
# 1:3 - Default (everything else)

sudo tc qdisc add dev "$NETWORK_INTERFACE" root handle 1: htb default 3
sudo tc class add dev "$NETWORK_INTERFACE" parent 1: classid 1:1 htb rate 100mbit ceil 100mbit prio 1
sudo tc class add dev "$NETWORK_INTERFACE" parent 1: classid 1:2 htb rate 50mbit ceil 100mbit prio 2
sudo tc class add dev "$NETWORK_INTERFACE" parent 1: classid 1:3 htb rate 10mbit ceil 100mbit prio 3

# Filter for VS Code downloads (HTTP/HTTPS ports)
sudo tc filter add dev "$NETWORK_INTERFACE" parent 1: protocol ip prio 1 u32 match ip dport 80 0xffff flowid 1:1
sudo tc filter add dev "$NETWORK_INTERFACE" parent 1: protocol ip prio 1 u32 match ip dport 443 0xffff flowid 1:1

# Filter for OmniMind services (ports 8000, 6333, etc.)
sudo tc filter add dev "$NETWORK_INTERFACE" parent 1: protocol ip prio 2 u32 match ip dport 8000 0xffff flowid 1:2
sudo tc filter add dev "$NETWORK_INTERFACE" parent 1: protocol ip prio 2 u32 match ip dport 6333 0xffff flowid 1:2
sudo tc filter add dev "$NETWORK_INTERFACE" parent 1: protocol ip prio 2 u32 match ip dport 6379 0xffff flowid 1:2

echo "✅ QoS configured for network prioritization"
echo ""

# ===== 4. SSD/NVMe OPTIMIZATION =====
echo "💾 4. Optimizing SSD/NVMe settings..."
echo ""

# Set I/O scheduler to none for NVMe (already optimal)
for disk in /sys/block/nvme*; do
    if [ -f "$disk/queue/scheduler" ]; then
        echo none | sudo tee "$disk/queue/scheduler" > /dev/null
    fi
done

# Enable TRIM
sudo systemctl enable fstrim.timer
sudo systemctl start fstrim.timer

# Optimize mount options (add to fstab if not present)
# Assuming / is on NVMe, add noatime,discard if not present
if ! grep -q "noatime" /etc/fstab; then
    echo "⚠️  Consider adding 'noatime,discard' to /etc/fstab for better SSD performance"
fi

echo "✅ SSD optimizations applied"
echo ""

# ===== 5. DISABLE UNNECESSARY SERVICES =====
echo "🛑 5. Disabling unnecessary services..."
echo ""

SERVICES_TO_DISABLE=(
    "bluetooth.service"
    "cups.service"
    "ModemManager.service"
    "avahi-daemon.service"
    "unattended-upgrades.service"
)

for service in "${SERVICES_TO_DISABLE[@]}"; do
    if sudo systemctl is-active --quiet "$service" 2>/dev/null; then
        sudo systemctl stop "$service"
        sudo systemctl disable "$service"
        echo "✅ Disabled $service"
    else
        echo "ℹ️  $service already disabled or not found"
    fi
done

echo ""

# ===== 6. RESOURCE ISOLATION FOR OMNIMIND =====
echo "🔒 6. Setting up resource isolation for OmniMind..."
echo ""

# Run the existing smart resources setup
if [ -f "scripts/setup_smart_resources.sh" ]; then
    bash scripts/setup_smart_resources.sh "$PROJECT_ROOT" full
else
    echo "⚠️  setup_smart_resources.sh not found, skipping resource isolation"
fi

echo ""

# ===== 7. CREATE PERSISTENT OPTIMIZATION SERVICE =====
echo "🔄 7. Creating persistent optimization service..."
echo ""

sudo tee /etc/systemd/system/omnimind-dev-optimization.service > /dev/null << EOF
[Unit]
Description=OmniMind Development Environment Optimization
After=network.target

[Service]
Type=oneshot
ExecStart=$PROJECT_ROOT/scripts/optimize_ubuntu_dev.sh $PROJECT_ROOT $NETWORK_INTERFACE
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable omnimind-dev-optimization

echo "✅ Persistent optimization service created"
echo ""

# ===== 8. FINAL VERIFICATION =====
echo "🔍 8. Verification..."
echo ""

echo "CPU Governor:"
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor

echo ""
echo "Swappiness:"
cat /proc/sys/vm/swappiness

echo ""
echo "Network QoS:"
tc qdisc show dev "$NETWORK_INTERFACE"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ UBUNTU OPTIMIZATION COMPLETE!"
echo ""
echo "📊 Optimizations Applied:"
echo "  • CPU: Performance governor"
echo "  • Memory: Reduced swappiness (10%)"
echo "  • Network: QoS prioritizing VS Code downloads"
echo "  • SSD: TRIM enabled, optimal I/O scheduler"
echo "  • Services: Disabled unnecessary ones"
echo "  • Resources: Isolated for OmniMind"
echo ""
echo "🚀 System is now optimized for OmniMind development!"
echo ""
echo "💡 To reapply optimizations: sudo systemctl restart omnimind-dev-optimization"
echo ""
