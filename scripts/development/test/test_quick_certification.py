#!/usr/bin/env python3
"""
TESTE RÁPIDO - Verifica se certificação pode rodar em 30 segundos

Valida:
1. GPU disponível
2. Imports OK
3. Pode executar 1 ciclo de verdade
4. Pode rodar quantum simulator
5. Pode salvar JSON
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import torch

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_quick_certification() -> bool:
    """Teste rápido de 30 segundos."""
    logger.info("=" * 70)
    logger.info("⚡ TESTE RÁPIDO - Certificação em 30 segundos")
    logger.info("=" * 70)

    results = {"timestamp": datetime.now().isoformat(), "tests": {}}

    # 1. GPU
    logger.info("\n1️⃣  Testando GPU...")
    try:
        gpu_available = torch.cuda.is_available()
        if gpu_available:
            logger.info(f"✅ GPU: {torch.cuda.get_device_name(0)}")
            results["tests"]["gpu"] = "PASS"
        else:
            logger.warning("⚠️  GPU não disponível (CPU será usado)")
            results["tests"]["gpu"] = "PASS_CPU"
    except Exception as e:
        logger.error(f"❌ GPU test falhou: {e}")
        results["tests"]["gpu"] = "FAIL"
        return False

    # 2. Imports
    logger.info("\n2️⃣  Testando imports...")
    try:
        from src.consciousness.integration_loop import IntegrationLoop  # noqa: F401

        logger.info("✅ IntegrationLoop importado")
        results["tests"]["imports"] = "PASS"
    except Exception as e:
        logger.error(f"❌ Import falhou: {e}")
        results["tests"]["imports"] = "FAIL"
        return False

    # 3. Uma execução de consciência
    logger.info("\n3️⃣  Executando 1 ciclo de consciência...")
    try:
        from src.consciousness.integration_loop import IntegrationLoop

        consciousness = IntegrationLoop()
        result = await consciousness.execute_cycle()
        phi = result.phi_estimate if hasattr(result, "phi_estimate") else 0.0
        logger.info(f"✅ Ciclo completo: Φ = {phi:.4f}")
        results["tests"]["consciousness_cycle"] = "PASS"
        results["phi_sample"] = float(phi)
    except Exception as e:
        logger.error(f"❌ Ciclo falhou: {e}")
        results["tests"]["consciousness_cycle"] = "FAIL"
        return False

    # 4. Quantum Simulator
    logger.info("\n4️⃣  Testando Quantum Simulator...")
    try:
        from qiskit import QuantumCircuit, QuantumRegister
        from qiskit_aer import AerSimulator

        qr = QuantumRegister(3, "q")
        circuit = QuantumCircuit(qr)
        circuit.h(qr[0])
        circuit.h(qr[1])
        circuit.h(qr[2])
        circuit.measure_all()

        simulator = AerSimulator()
        job = simulator.run(circuit, shots=100)
        result_qiskit = job.result()
        counts = result_qiskit.get_counts()

        logger.info(f"✅ Quantum: {len(counts)} superposições")
        results["tests"]["quantum"] = "PASS"
    except ImportError:
        logger.warning("⚠️  Qiskit não instalado (pulando)")
        results["tests"]["quantum"] = "SKIP"
    except Exception as e:
        logger.error(f"❌ Quantum falhou: {e}")
        results["tests"]["quantum"] = "FAIL"
        return False
        return False

    # 5. IBM Check
    logger.info("\n5️⃣  Verificando IBM Quantum...")
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService  # noqa: F401

        try:
            service = QiskitRuntimeService()
            backends = service.backends()
            logger.info(f"✅ IBM: {len(backends)} backends disponíveis")
            results["tests"]["ibm"] = "PASS"
        except Exception:
            logger.warning("⚠️  IBM credenciais não carregadas")
            results["tests"]["ibm"] = "NO_CREDS"
    except ImportError:
        logger.warning("⚠️  qiskit-ibm-runtime não instalado")
        results["tests"]["ibm"] = "NOT_INSTALLED"

    # 6. Salvar JSON
    logger.info("\n6️⃣  Salvando JSON...")
    try:
        output_dir = Path("/home/fahbrain/projects/omnimind/data/test_reports")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = output_dir / f"test_quick_certification_{timestamp}.json"

        with open(json_file, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"✅ JSON salvo: {json_file}")
        results["tests"]["json_save"] = "PASS"
    except Exception as e:
        logger.error(f"❌ JSON falhou: {e}")
        results["tests"]["json_save"] = "FAIL"
        return False

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("✅ TESTE RÁPIDO PASSOU")
    logger.info("=" * 70)
    logger.info("\n🎯 Resumo de Testes:")
    for test_name, status in results["tests"].items():
        logger.info(f"   {test_name}: {status}")

    logger.info("\n🚀 Sistema pronto para certificação completa!")
    logger.info("   Próximo comando: bash scripts/run_full_certification.sh")
    logger.info("")

    return True


async def main() -> None:
    """Main."""
    try:
        success = await test_quick_certification()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("⚠️  Interrompido")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
