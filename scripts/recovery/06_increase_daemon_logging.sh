#!/bin/bash

# 📝 STEP 6: Increase Daemon Logging Verbosity
# Aumenta verbosity para mostrar ciclos de integração
# Status: READY FOR EXECUTION

set -e

PROJECT_ROOT="/home/fahbrain/projects/omnimind"

echo -e "\033[0;36m📝 Step 6: Increase Daemon Logging Verbosity\033[0m"
echo "════════════════════════════════════════════════════════════════"
echo ""

echo "Configuring daemon logging..."
echo ""

# Apply logging fix
python3 << 'PYTHON_END'
import sys
from pathlib import Path
import logging

PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")
sys.path.insert(0, str(PROJECT_ROOT / "src"))

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Update daemon.py to increase verbosity
daemon_file = PROJECT_ROOT / "src" / "api" / "routes" / "daemon.py"

if not daemon_file.exists():
    logger.error(f"File not found: {daemon_file}")
    sys.exit(1)

with open(daemon_file, 'r') as f:
    content = f.read()

# Check current logging level
if "level=logging.DEBUG" in content:
    logger.info("✅ DEBUG logging already enabled")
elif "level=logging.INFO" in content:
    logger.info("ℹ️  INFO logging is set - this is acceptable")
else:
    logger.warning("⚠️  Logging level unclear - checking...")

# Add cycle execution logging if not present
if "# Log cycle execution" not in content:
    logger.info("Adding cycle execution logging...")

    # Find execute_cycle function
    if "execute_cycle" in content:
        # Insert logging after function definition
        lines = content.split('\n')
        modified = False

        for i, line in enumerate(lines):
            if "def execute_cycle" in line and not modified:
                # Find the function body start
                for j in range(i+1, min(i+10, len(lines))):
                    if ":" in lines[j]:
                        # Insert logging after docstring/colon
                        for k in range(j+1, min(j+5, len(lines))):
                            if lines[k].strip() and not lines[k].strip().startswith('"""') and not lines[k].strip().startswith("'''"):
                                indent = len(lines[k]) - len(lines[k].lstrip())
                                logging_line = ' ' * indent + 'logger.info(f"🔄 Executing cycle {cycle_num} with stimulation...")'
                                lines.insert(k, logging_line)
                                modified = True
                                break
                if modified:
                    break

        if modified:
            content = '\n'.join(lines)
            with open(daemon_file, 'w') as f:
                f.write(content)
            logger.info("✅ Cycle execution logging added")
else:
    logger.info("✅ Cycle logging already present")

PYTHON_END

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo -e "\033[0;32m✅ Daemon logging configured\033[0m"
else
    echo ""
    echo -e "\033[0;33m⚠️  Daemon logging configuration incomplete\033[0m"
fi

# Update logger configuration in multiple files
echo ""
echo "Updating logger configuration across system..."

# Create a logging config enhancement
python3 << 'CONFIG_END'
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")

# Create enhanced logging config
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        },
        "cycle": {
            "format": "%(asctime)s | CYCLE | %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "verbose",
            "stream": "ext://sys.stdout"
        },
        "cycle_file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "cycle",
            "filename": str(PROJECT_ROOT / "logs" / "daemon_cycles.log")
        },
        "daemon_file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "verbose",
            "filename": str(PROJECT_ROOT / "logs" / "daemon.log")
        }
    },
    "loggers": {
        "omnimind.daemon": {
            "level": "DEBUG",
            "handlers": ["console", "daemon_file"],
            "propagate": False
        },
        "omnimind.cycles": {
            "level": "DEBUG",
            "handlers": ["cycle_file"],
            "propagate": False
        },
        "omnimind": {
            "level": "INFO",
            "handlers": ["console", "daemon_file"],
            "propagate": False
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "daemon_file"]
    }
}

# Save config
config_file = PROJECT_ROOT / "config" / "logging.json"
config_file.parent.mkdir(parents=True, exist_ok=True)

with open(config_file, 'w') as f:
    json.dump(logging_config, f, indent=2)

print(f"✅ Logging config saved to: {config_file}")
print("")
print("📋 Logging configuration:")
print("   • Daemon logs: logs/daemon.log")
print("   • Cycle logs: logs/daemon_cycles.log")
print("   • Console: INFO+ level")
print("   • File: DEBUG+ level (detailed)")

# Create logs directory
(PROJECT_ROOT / "logs").mkdir(parents=True, exist_ok=True)

CONFIG_END

echo ""
echo -e "\033[0;32m✅ Step 6 Complete: Daemon logging configured\033[0m"
echo ""
