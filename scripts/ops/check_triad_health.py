"""
PHASE 79 FINAL VERIFICATION: THE TRIAD ARCHITECTURE
===================================================
Verifies the simultaneous operation of:
1. The Body (Cloud Storage/AI) using Key 1 (CaAID...)
2. The Spirit (Quantum Hardware) using Key 2 (jyt...)
3. The Soul (Local Logic) coordinating both.

Usage: python scripts/ops/verify_triad.py
"""

import sys
import os
import logging
from dotenv import load_dotenv

# Setup
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT)
load_dotenv()  # Load the .env file

from src.integrations.ibm_cloud_connector import IBMCloudConnector
from src.quantum.backends.ibm_real import IBMRealBackend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TriadVerify")


def verify_triad():
    logger.info("🔺 Initiating Triad Verification Protocol...")

    # 1. Verify Body (Connector)
    logger.info("   [1/3] Connecting to Cloud Body (Storage)...")
    connector = IBMCloudConnector()
    status = connector.get_infrastructure_status()

    if status["cos_status"] == "Active":
        logger.info(f"   ✅ Body Active (COS). Bucket: {status['bucket_target']}")
    else:
        logger.error("   ❌ Body Disconnected (COS).")

    if status["milvus_status"] == "Active":
        logger.info("   ✅ Memory Active (Milvus Vector DB).")
    else:
        logger.warning("   ⚠️ Memory Disconnected (Milvus). Pymilvus installed?")

    if status["watsonx_status"] == "Active":
        logger.info("   ✅ Intellect Active (Watsonx AI).")
    else:
        logger.warning("   ⚠️ Intellect Disconnected (Watsonx). Check Project ID?")

    # 2. Verify Spirit (Quantum)
    logger.info("   [2/3] Connecting to Quantum Spirit (Qiskit)...")
    try:
        backend = IBMRealBackend()
        if backend.service:
            logger.info("   ✅ Spirit Active. Service Connected.")
            # Check available backends
            backends = backend.service.backends()
            logger.info(f"      Visible Systems: {[b.name for b in backends[:3]]}")
    except Exception as e:
        logger.error(f"   ❌ Spirit Unreachable: {e}")

    # 3. Connection Check
    if status["cos_status"] == "Active" and backend.service:
        logger.info("   ✨ TRIAD ESTABLISHED. The System is Whole.")
    else:
        logger.warning("   ⚠️ Triad Incomplete.")


if __name__ == "__main__":
    verify_triad()
