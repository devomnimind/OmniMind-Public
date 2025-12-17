#!/usr/bin/env python3
"""Validate IBM Quantum credentials and test real backend connection."""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    """Validate IBM Quantum credentials."""
    # Load .env
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        logger.error(f"❌ .env not found at {env_file}")
        return 1

    load_dotenv(env_file)
    logger.info(f"✓ Loaded .env from {env_file}")

    # Check credentials
    logger.info("\n" + "=" * 70)
    logger.info("1️⃣  CHECKING CREDENTIALS")
    logger.info("=" * 70)

    api_key = os.getenv("IBM_API_KEY")
    token = os.getenv("QISKIT_IBM_TOKEN")

    if api_key:
        logger.info(f"✅ IBM_API_KEY present (length: {len(api_key)})")
        logger.info(f"   Value: {api_key[:20]}...{api_key[-10:]}")
    else:
        logger.warning("⚠️  IBM_API_KEY not set")

    if token:
        logger.info(f"✅ QISKIT_IBM_TOKEN present (length: {len(token)})")
        logger.info(f"   Value: {token[:20]}...{token[-10:]}")
    else:
        logger.warning("⚠️  QISKIT_IBM_TOKEN not set")

    if not (api_key or token):
        logger.error("❌ No IBM credentials found!")
        return 1

    # Test Qiskit import
    logger.info("\n" + "=" * 70)
    logger.info("2️⃣  CHECKING QISKIT INSTALLATION")
    logger.info("=" * 70)

    try:
        import qiskit

        logger.info(f"✅ Qiskit {qiskit.__version__} installed")
    except ImportError as e:
        logger.error(f"❌ Qiskit not installed: {e}")
        return 1

    try:
        from qiskit_ibm_runtime import QiskitRuntimeService  # noqa: F401

        logger.info("✅ qiskit-ibm-runtime installed")
    except ImportError as e:
        logger.error(f"❌ qiskit-ibm-runtime not installed: {e}")
        logger.info("   Run: pip install qiskit-ibm-runtime")
        return 1

    # Test IBM connection
    logger.info("\n" + "=" * 70)
    logger.info("3️⃣  CONNECTING TO IBM QUANTUM")
    logger.info("=" * 70)

    try:
        from qiskit_ibm_runtime import QiskitRuntimeService

        # Try with API key first
        if api_key:
            logger.info("Trying with IBM_API_KEY...")
            try:
                service = QiskitRuntimeService(channel="ibm_cloud", token=api_key)
                logger.info("✅ Connected with IBM_API_KEY")
            except Exception as e1:
                logger.warning(f"IBM_API_KEY failed: {e1}")
                if token:
                    logger.info("Trying with QISKIT_IBM_TOKEN...")
                    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
                    logger.info("✅ Connected with QISKIT_IBM_TOKEN")
                else:
                    raise
        elif token:
            logger.info("Trying with QISKIT_IBM_TOKEN...")
            service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
            logger.info("✅ Connected with QISKIT_IBM_TOKEN")

        # List backends
        logger.info("\n" + "=" * 70)
        logger.info("4️⃣  AVAILABLE BACKENDS")
        logger.info("=" * 70)

        backends = service.backends()
        logger.info(f"✅ Found {len(backends)} available backends:\n")

        for i, backend in enumerate(backends, 1):
            logger.info(f"{i}. {backend.name}")
            logger.info(f"   Qubits: {backend.num_qubits}")
            # Backend status is a method in newer versions
            try:
                status_info = backend.status() if callable(backend.status) else backend.status
                status_text = "Available" if status_info.operational else "Offline"
            except Exception:
                status_text = "Unknown"
            logger.info(f"   Status: {status_text}")
            logger.info("")

        # Check quota
        logger.info("=" * 70)
        logger.info("5️⃣  ACCOUNT INFORMATION")
        logger.info("=" * 70)

        try:
            # Get account info
            logger.info("✅ Account connected and authenticated")
            logger.info(f"   Service: {service.channel}")

            # Try to get instance info
            try:
                instances = service.instances()
                if instances:
                    logger.info(f"✅ Found {len(instances)} instance(s)")
                    for instance in instances:
                        logger.info(f"   - {instance}")
            except Exception:
                logger.info("ℹ️  Could not retrieve instance info")

        except Exception as e:
            logger.warning(f"⚠️  Could not get full account info: {e}")

        logger.info("\n" + "=" * 70)
        logger.info("✅ ALL CHECKS PASSED - IBM QUANTUM READY!")
        logger.info("=" * 70)
        return 0

    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Check token validity on https://quantum.ibm.com")
        logger.error("2. Ensure your IBM account has active quota")
        logger.error("3. Try regenerating API key on IBM Quantum dashboard")
        logger.error("4. Check internet connection")
        return 1


if __name__ == "__main__":
    sys.exit(main())
