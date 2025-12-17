#!/usr/bin/env python3
"""Validação IBM: ENV + Token + Conexão."""

import os
import sys
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))


def main() -> int:
    """Valida IBM Quantum conexão."""
    logger.info("=" * 70)
    logger.info("VALIDAÇÃO IBM QUANTUM")
    logger.info("=" * 70)

    result: dict = {"env": {}, "validation": {}, "connection": {}}

    # 1. ENV
    logger.info("\n1️⃣  Variáveis de ambiente...")
    token = os.getenv("QISKIT_IBM_TOKEN")
    api_key = os.getenv("IBM_QUANTUM_API_KEY")

    result["env"]["QISKIT_IBM_TOKEN"] = "SET" if token else "NOT SET"
    result["env"]["IBM_QUANTUM_API_KEY"] = "SET" if api_key else "NOT SET"

    if token:
        logger.info(f"✅ QISKIT_IBM_TOKEN: ***{token[-4:]}")
    else:
        logger.warning("⚠️  QISKIT_IBM_TOKEN: NOT SET")

    if api_key:
        logger.info(f"✅ IBM_QUANTUM_API_KEY: ***{api_key[-4:]}")

    # 2. Qiskit
    logger.info("\n2️⃣  Verificando Qiskit...")
    try:
        import qiskit

        logger.info(f"✅ Qiskit: {qiskit.__version__}")
        result["validation"]["qiskit_version"] = qiskit.__version__
    except ImportError:
        logger.error("❌ Qiskit não instalado")
        result["validation"]["qiskit"] = False
        return 1

    # 3. qiskit-ibm-runtime
    logger.info("\n3️⃣  Verificando qiskit-ibm-runtime...")
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService  # noqa: F401

        logger.info("✅ qiskit-ibm-runtime disponível")
        result["validation"]["qiskit_ibm_runtime"] = True
    except ImportError:
        logger.error("❌ qiskit-ibm-runtime não instalado")
        result["validation"]["qiskit_ibm_runtime"] = False
        logger.info("   pip install qiskit-ibm-runtime")
        return 1

    # 4. Conexão
    logger.info("\n4️⃣  Testando conexão...")

    if not token:
        logger.warning("⚠️  Token não disponível")
        result["connection"]["status"] = "NO_TOKEN"
        return 1

    try:
        from qiskit_ibm_runtime import QiskitRuntimeService

        logger.info("  Conectando...")
        service = QiskitRuntimeService(channel="ibm_quantum_platform")

        logger.info("  Listando backends...")
        backends = service.backends()

        logger.info(f"✅ Conectado! {len(backends)} backends disponíveis:")
        result["connection"]["status"] = "CONNECTED"
        result["connection"]["num_backends"] = len(backends)

        backend_names = []
        for backend in backends[:5]:
            name = str(backend)
            backend_names.append(name)
            logger.info(f"  - {name}")

        result["connection"]["backends"] = backend_names

    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Conexão falhou: {error_msg}")
        result["connection"]["status"] = "FAILED"
        result["connection"]["error"] = error_msg

        if "401" in error_msg or "Unauthorized" in error_msg:
            logger.error("   → Token inválido ou expirado")
            result["connection"]["error_type"] = "INVALID_TOKEN"
        elif "Connection" in error_msg or "timeout" in error_msg.lower():
            logger.error("   → Erro de rede")
            result["connection"]["error_type"] = "NETWORK"
        else:
            result["connection"]["error_type"] = "UNKNOWN"

        return 1

    # Salva resultado
    logger.info("\n5️⃣  Salvando resultado...")
    output_dir = Path("/home/fahbrain/projects/omnimind/data/test_reports")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "ibm_validation_result.json"
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    logger.info(f"✅ Resultado: {output_file}")

    logger.info("\n" + "=" * 70)
    logger.info("✅ VALIDAÇÃO IBM OK")
    logger.info("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
