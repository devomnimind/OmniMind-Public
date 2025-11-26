#!/bin/bash
# OmniMind External Auditor - Continuous Mode
# Validates system integrity continuously with 15-minute checkpoints

PROJECT_ROOT="/home/fahbrain/projects/omnimind"
LOG_DIR="$PROJECT_ROOT/data/long_term_logs"
REPORT_FILE="$LOG_DIR/audit_report_latest.md"
CHECKPOINT_INTERVAL=900  # 15 minutes in seconds

# Ensure log directory exists
mkdir -p "$LOG_DIR"

cd "$PROJECT_ROOT"
source .venv/bin/activate

echo "Starting External Auditor in continuous mode..."
echo "Checkpoints every 15 minutes"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$TIMESTAMP] Running audit checkpoint..." >> "$LOG_DIR/auditor_continuous.log"

    # Run Python auditor
    python -c "
from src.audit.external_auditor import ExternalAuditor
from datetime import datetime
import json

auditor = ExternalAuditor(log_path='$LOG_DIR/audit_checkpoints.jsonl')
report = auditor.run_full_audit()

# Write report
with open('$REPORT_FILE', 'w') as f:
    f.write(f'# OmniMind External Audit Report\n')
    f.write(f'**Date:** {datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")}\n')
    f.write(f'**Status:** {\"✅ HEALTHY\" if report.get(\"status\") == \"healthy\" else \"⚠️ ISSUES\"}\n\n')
    f.write(f'## Checkpoint\n')
    f.write(f'- **Anomalies:** {len(report.get(\"anomalies\", []))}\n')
    f.write(f'- **Logs Analyzed:** {report.get(\"total_logs\", 0)}\n')
" >> "$LOG_DIR/auditor_continuous.log" 2>&1

    echo "[$TIMESTAMP] Checkpoint complete. Next in $CHECKPOINT_INTERVAL seconds." >> "$LOG_DIR/auditor_continuous.log"
    sleep $CHECKPOINT_INTERVAL
done
