#!/bin/bash
# DEPRECATED: This script is outdated and will be removed
# Use scripts/systemd/install_all_services.sh instead

echo "❌ DEPRECATED: This script installs the old omnimind-backend.service which conflicts with omnimind.service"
echo "✅ Use the correct script: scripts/systemd/install_all_services.sh"
echo ""
echo "The old omnimind-backend.service has been removed to prevent conflicts."
echo "All functionality is now provided by omnimind.service."
echo ""
exit 1
