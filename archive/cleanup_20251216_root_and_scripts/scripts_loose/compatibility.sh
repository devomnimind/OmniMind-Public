#!/bin/bash
# Compatibility layer for old script paths
# This file maintains backward compatibility for scripts that reference old paths

# Canonical scripts
ln -sf canonical/system/start_omnimind_system.sh start_omnimind_system.sh
ln -sf canonical/system/run_cluster.sh run_cluster.sh
ln -sf canonical/system/start_mcp_servers.sh start_mcp_servers.sh
ln -sf canonical/monitor/monitor_tests.sh monitor_tests.sh
ln -sf canonical/monitor/monitor_tests_live.sh monitor_tests_live.sh
ln -sf canonical/test/run_tests_by_category.sh run_tests_by_category.sh
ln -sf canonical/test/run_full_certification.sh run_full_certification.sh
ln -sf canonical/validate/run_real_metrics.sh run_real_metrics.sh
ln -sf canonical/validate/verify_gpu_setup.sh verify_gpu_setup.sh
ln -sf canonical/diagnose/diagnostic_quick.sh diagnostic_quick.sh
ln -sf canonical/diagnose/final_status.sh final_status.sh
ln -sf canonical/install/install_systemd_services.sh install_systemd_services.sh
ln -sf canonical/install/setup_security_privileges.sh setup_security_privileges.sh

echo "🔗 Compatibility links created for backward compatibility"
