#!/usr/bin/env python3
import time
import os
import sys
import logging
from pathlib import Path

# Setup Path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("QuantumMonitor")


def monitor_quantum_link():
    logger.info("🔭 OMNIMIND QUANTUM LINK MONITOR")
    logger.info("================================")

    # 1. Inspect Environment
    v2_key = os.getenv("VERSAO_2_IBM_API_KEY")
    v3_key = os.getenv("IBM_API_KEY")
    crn = os.getenv("QISKIT_IBM_INSTANCE") or os.getenv("IBM_CLOUD_INSTANCE")

    logger.info(f"🔑 Key V2 (Legacy/US-East): {'***' + v2_key[-4:] if v2_key else 'MISSING'}")
    logger.info(f"🔑 Key V3 (New/Au-Syd):    {'***' + v3_key[-4:] if v3_key else 'MISSING'}")
    logger.info(
        f"🏭 Instance CRN:          {crn if crn else 'MISSING (Auto-discovery enabled if V2)'}"
    )

    if not v2_key and not v3_key:
        logger.warning("❌ Nenhuma chave de API detectada. Aguardando export...")
        return

    try:
        # Import the Production Driver
        logger.info("🔌 Inicializando IBMRealBackend (Driver de Produção)...")
        from src.quantum.backends.ibm_real import IBMRealBackend

        # Instantiate (This triggers the connection logic verified previously)
        backend_driver = IBMRealBackend()

        if backend_driver.service:
            # Connection Successful
            logger.info("✅ SERVICE CONNECTED!")

            # Inspect Account Details
            try:
                account = backend_driver.service.active_account()
                logger.info(f"   channel: {account.get('channel')}")
                logger.info(f"   instance: {account.get('instance')}")
                logger.info(f"   token: ***{str(account.get('token'))[-4:]}")
            except Exception:
                logger.info("   (Detalhes da conta ocultos/indisponíveis)")

            # Check for actual Hardware Access
            if backend_driver.backend:
                logger.info(f"🖥️  BACKEND OPERACIONAL: {backend_driver.backend.name}")
                status = backend_driver.backend.status()
                logger.info(f"   Status: {status.status_msg}")
                logger.info(f"   Qubits: {backend_driver.backend.num_qubits}")

            else:
                logger.warning("⚠️ Serviço conectado, mas nenhum QPU real foi selecionado.")

            logger.info("✨ Link Quântico Estável. Sistema pronto para experimentos.")

        else:
            logger.error("❌ O Serviço não foi inicializado (service is None). Verifique os logs.")

    except ImportError as e:
        logger.critical(f"❌ Erro de Dependência: {e}")
    except Exception as e:
        logger.critical(f"❌ FALHA CRÍTICA NO LINK: {e}")
        # Print detailed traceback for debugging
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    while True:
        monitor_quantum_link()
        logger.info("💤 Sleeping 60s before re-check...")
        time.sleep(60)
