#!/usr/bin/env python3
"""
OmniMind Health Check - Detecta falhas e aciona recovery automaticamente
Roda a cada minuto via cron ou systemd timer
"""

import logging
import socket
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Setup logging
PROJECT_ROOT = Path("/home/fahbrain/projects/omnimind")
LOG_FILE = PROJECT_ROOT / "logs" / "healthcheck.log"
LOG_FILE.parent.mkdir(exist_ok=True, parents=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


def check_port(host="127.0.0.1", port=8000, timeout=2):
    """Verificar se porta está respondendo"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        logger.error(f"Erro ao verificar porta {port}: {e}")
        return False


def trigger_recovery():
    """Acionar script de recovery"""
    recovery_script = PROJECT_ROOT / "scripts" / "omnimind_intelligent_recovery.sh"

    if not recovery_script.exists():
        logger.error(f"Recovery script não encontrado: {recovery_script}")
        return False

    try:
        logger.warning("🚨 Backend down! Acionando recovery automático...")
        subprocess.run(
            ["bash", str(recovery_script)],
            cwd=str(PROJECT_ROOT),
            timeout=300,  # 5 minutos max
            capture_output=True,
            text=True,
        )
        logger.info("✅ Recovery script executado")
        return True
    except subprocess.TimeoutExpired:
        logger.error("❌ Recovery script timeout")
        return False
    except Exception as e:
        logger.error(f"❌ Erro ao executar recovery: {e}")
        return False


def main():
    """Health check principal"""
    logger.info("Executando health check...")

    # Verificar porta 8000 (backend principal)
    if not check_port(port=8000):
        logger.warning("⚠️  Backend porta 8000 não respondendo!")

        # Verificar se realmente está down (não é falso positivo)
        if not check_port(port=8000):
            logger.error("❌ Backend confirmado como DOWN - acionando recovery")
            trigger_recovery()
            sys.exit(1)
    else:
        logger.info("✅ Backend respondendo normalmente (porta 8000)")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Erro fatal no health check: {e}")
        sys.exit(1)
