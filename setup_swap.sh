#!/bin/bash
#
# Swap Space Setup for EC2 t3.small (2GB RAM)
# Creates 4GB swap to prevent OOM issues with NudeNet
#
# Usage: sudo ./setup_swap.sh
#

set -e

echo "=========================================="
echo "Setting up 4GB Swap Space for t3.small"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root (use sudo)"
    exit 1
fi

# Check if swap already exists
if swapon --show | grep -q '/swapfile'; then
    echo "⚠️  Swap file already exists!"
    echo ""
    swapon --show
    echo ""
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting without changes."
        exit 0
    fi

    echo "Turning off existing swap..."
    swapoff /swapfile
    rm -f /swapfile
fi

# Create swap file
echo "1. Creating 4GB swap file (this may take a minute)..."
dd if=/dev/zero of=/swapfile bs=1M count=4096 status=progress

# Set permissions
echo ""
echo "2. Setting permissions..."
chmod 600 /swapfile

# Make swap
echo ""
echo "3. Setting up swap area..."
mkswap /swapfile

# Enable swap
echo ""
echo "4. Enabling swap..."
swapon /swapfile

# Verify
echo ""
echo "5. Verifying swap is active..."
swapon --show
echo ""
free -h

# Make swap permanent (survive reboots)
echo ""
echo "6. Making swap permanent..."
if ! grep -q '/swapfile' /etc/fstab; then
    echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
    echo "✅ Added to /etc/fstab"
else
    echo "✅ Already in /etc/fstab"
fi

# Optimize swap settings for better performance
echo ""
echo "7. Optimizing swap settings..."

# vm.swappiness: How aggressively to use swap (0-100)
# Lower = prefer RAM, Higher = use swap more
# 10 is good for servers with enough RAM but need swap as backup
echo "vm.swappiness=10" | tee /etc/sysctl.d/99-swap.conf

# vm.vfs_cache_pressure: How aggressively to reclaim inode/dentry cache
# Lower = keep cache longer (good for file-heavy workloads like Django)
# 50 is good balance
echo "vm.vfs_cache_pressure=50" | tee -a /etc/sysctl.d/99-swap.conf

# Apply settings
sysctl -p /etc/sysctl.d/99-swap.conf

echo ""
echo "=========================================="
echo "✅ Swap Setup Complete!"
echo "=========================================="
echo ""
echo "📊 Memory Status:"
free -h
echo ""
echo "💾 Swap Status:"
swapon --show
echo ""
echo "⚙️  Swap Settings:"
echo "   - Swappiness: $(cat /proc/sys/vm/swappiness)"
echo "   - Cache Pressure: $(cat /proc/sys/vm/vfs_cache_pressure)"
echo ""
echo "📝 Notes:"
echo "   - Swap will persist across reboots"
echo "   - Total memory available: 2GB RAM + 4GB Swap = 6GB"
echo "   - NudeNet will use ~1GB RAM, leaving room for Django/MySQL/Redis"
echo "   - Swap is slower than RAM, but prevents OOM crashes"
echo ""
echo "🚀 You can now run your Django app with NudeNet on t3.small!"
echo ""
