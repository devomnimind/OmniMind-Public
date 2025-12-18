#!/usr/bin/env python3
"""Certificação Real: GPU + IBM Quantum + Timestamp Prova."""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import torch

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))


class RealCertification:
    """Certificação com GPU + IBM Quantum."""

    def __init__(self) -> None:
        self.report: Dict[str, Any] = {
            "certification_timestamp": datetime.now().isoformat(),
            "certification_unix_timestamp": time.time(),
            "hardware": {},
            "quantum": {},
            "metrics": {},
            "system_info": {},
        }
        self.ibm_service: Any = None
        self._collect_system_info()

    def _collect_system_info(self) -> None:
        """Coleta GPU + Sistema."""
        logger.info("Coletando informação do sistema...")

        # GPU
        self.report["hardware"]["gpu_available"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            self.report["hardware"]["gpu_name"] = torch.cuda.get_device_name(0)
            self.report["hardware"]["gpu_vram_gb"] = (
                torch.cuda.get_device_properties(0).total_memory / 1e9
            )
            logger.info(
                f"✅ GPU: {self.report['hardware']['gpu_name']} ({self.report['hardware']['gpu_vram_gb']:.1f}GB)"
            )

        # Sistema
        import platform

        self.report["system_info"]["python_version"] = platform.python_version()
        self.report["system_info"]["pytorch_version"] = torch.__version__

    def _check_ibm(self) -> bool:
        """Verifica IBM Quantum."""
        logger.info("Verificando IBM Quantum...")

        try:
            from qiskit_ibm_runtime import QiskitRuntimeService  # noqa: F401

            try:
                self.ibm_service = QiskitRuntimeService(channel="ibm_quantum_platform")
                backends = self.ibm_service.backends()
                self.report["quantum"]["service_available"] = True
                self.report["quantum"]["num_backends"] = len(backends)
                logger.info(f"✅ IBM conectado: {len(backends)} backends")
                return True
            except Exception as e:
                logger.warning(f"⚠️  IBM não conectou: {e}")
                self.report["quantum"]["service_available"] = False
                return False
        except ImportError:
            logger.warning("⚠️  qiskit-ibm-runtime não instalado")
            self.report["quantum"]["service_available"] = False
            return False

    async def _measure_gpu(self, num_cycles: int = 50) -> Dict[str, Any]:
        """Mede Φ em GPU."""
        logger.info(f"Medindo GPU ({num_cycles} ciclos)...")

        try:
            from src.consciousness.integration_loop import IntegrationLoop

            start_time = time.time()
            start_ts = datetime.now().isoformat()
            phi_values = []

            consciousness = IntegrationLoop()
            for i in range(num_cycles):
                result = await consciousness.execute_cycle()
                phi = result.phi_estimate if hasattr(result, "phi_estimate") else 0.0
                phi_values.append(float(phi))
                if (i + 1) % 50 == 0:
                    logger.info(f"  Ciclo {i + 1}/{num_cycles} ✓")

            total_time = time.time() - start_time
            end_ts = datetime.now().isoformat()

            mean_phi = sum(phi_values) / len(phi_values)
            logger.info(f"✅ GPU Φ_mean: {mean_phi:.6f} (tempo: {total_time:.2f}s)")

            return {
                "backend": "GPU",
                "num_cycles": num_cycles,
                "start_timestamp": start_ts,
                "end_timestamp": end_ts,
                "total_time_seconds": total_time,
                "phi_mean": mean_phi,
                "phi_min": min(phi_values),
                "phi_max": max(phi_values),
                "phi_values": phi_values,
            }

        except Exception as e:
            logger.error(f"Erro GPU: {e}")
            return {"backend": "GPU", "error": str(e)}

    def _measure_quantum_simulator(self, num_shots: int = 200) -> Dict[str, Any]:
        """Mede quantum simulator."""
        logger.info(f"Medindo Quantum Simulator ({num_shots} shots)...")

        try:
            from qiskit import QuantumCircuit, QuantumRegister
            from qiskit_aer import AerSimulator

            start_time = time.time()
            start_ts = datetime.now().isoformat()

            qr = QuantumRegister(3, "q")
            circuit = QuantumCircuit(qr)
            circuit.h(qr[0])
            circuit.h(qr[1])
            circuit.h(qr[2])
            circuit.measure_all()

            simulator = AerSimulator()
            job = simulator.run(circuit, shots=num_shots)
            result = job.result()
            counts = result.get_counts()

            total_time = time.time() - start_time
            end_ts = datetime.now().isoformat()

            num_outcomes = len(counts)
            logger.info(f"✅ Quantum: {num_outcomes}/8 superposições (tempo: {total_time:.2f}s)")

            return {
                "backend": "Quantum_Simulator",
                "num_shots": num_shots,
                "start_timestamp": start_ts,
                "end_timestamp": end_ts,
                "total_time_seconds": total_time,
                "num_outcomes": num_outcomes,
                "outcomes_possible": 8,
            }

        except ImportError:
            logger.warning("Qiskit não instalado")
            return {"backend": "Quantum_Simulator", "error": "qiskit not installed"}
        except Exception as e:
            logger.error(f"Erro Quantum: {e}")
            return {"backend": "Quantum_Simulator", "error": str(e)}

    async def run(self) -> None:
        """Executa certificação completa."""
        logger.info("=" * 70)
        logger.info("CERTIFICAÇÃO REAL - GPU + QUANTUM + IBM")
        logger.info("=" * 70)

        # GPU (200 ciclos para robustez científica)
        gpu_result = await self._measure_gpu(num_cycles=200)
        self.report["metrics"]["gpu"] = gpu_result

        # Quantum Simulator (1024 shots para significância estatística)
        quantum_result = self._measure_quantum_simulator(num_shots=1024)
        self.report["metrics"]["quantum"] = quantum_result
        self.report["metrics"]["quantum"] = quantum_result

        # IBM (optional, ~9 min)
        if self._check_ibm():
            logger.info("\n⏱️  IBM demora ~9 minutos. Ctrl+C para pular.")
            try:
                ibm_result = await self._measure_ibm_real()
                self.report["metrics"]["ibm_real"] = ibm_result
            except KeyboardInterrupt:
                logger.warning("IBM cancelado pelo usuário")
                self.report["metrics"]["ibm_real"] = {"status": "cancelled"}
            except Exception as e:
                logger.error(f"Erro IBM: {e}")
                self.report["metrics"]["ibm_real"] = {"error": str(e)}

        # Salva
        self._save_report()
        self._print_summary()

    async def _measure_ibm_real(self) -> Dict[str, Any]:
        """Mede com IBM real QPU."""
        logger.info("Executando no IBM Quantum (QPU real)...")

        try:
            from qiskit import QuantumCircuit, QuantumRegister
            from qiskit.transpiler import generate_preset_pass_manager
            from qiskit_ibm_runtime import Sampler

            start_time = time.time()
            start_ts = datetime.now().isoformat()

            backends = self.ibm_service.backends()
            if not backends:
                return {"error": "No backends available"}

            backend = backends[0]
            logger.info(f"Backend: {backend}")

            qr = QuantumRegister(3, "q")
            circuit = QuantumCircuit(qr)
            circuit.h(qr[0])
            circuit.h(qr[1])
            circuit.h(qr[2])
            circuit.measure_all()

            # Usa Sampler direto com backend
            sampler = Sampler(backend)

            # Transpila circuit para hardware específico
            pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
            transpiled = pm.run(circuit)

            job = sampler.run([transpiled], shots=100)
            result = job.result()
            counts = result[0].data.meas.binary_probabilities()

            total_time = time.time() - start_time
            end_ts = datetime.now().isoformat()

            logger.info(f"✅ IBM completo (tempo: {total_time:.2f}s)")

            return {
                "backend": f"IBM_Real_{backend}",
                "shots": 100,
                "start_timestamp": start_ts,
                "end_timestamp": end_ts,
                "total_time_seconds": total_time,
                "outcomes": len(counts),
            }

        except Exception as e:
            logger.error(f"Erro ao rodar IBM: {e}")
            return {"error": str(e)}

    def _save_report(self) -> None:
        """Salva JSON + TXT."""
        output_dir = Path("/home/fahbrain/projects/omnimind/data/test_reports")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON
        json_file = output_dir / f"certification_real_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(self.report, f, indent=2, default=str)
        logger.info(f"✅ JSON: {json_file}")

        # TXT
        txt_file = output_dir / f"certification_real_{timestamp}_summary.txt"
        with open(txt_file, "w") as f:
            f.write("=" * 70 + "\n")
            f.write("CERTIFICAÇÃO REAL\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"Timestamp: {self.report['certification_timestamp']}\n")
            f.write(f"GPU: {self.report['hardware'].get('gpu_name', 'N/A')}\n")
            f.write(f"GPU VRAM: {self.report['hardware'].get('gpu_vram_gb', 0):.1f}GB\n")
            f.write(f"Python: {self.report['system_info'].get('python_version', 'N/A')}\n")
            f.write(f"PyTorch: {self.report['system_info'].get('pytorch_version', 'N/A')}\n\n")

            gpu = self.report["metrics"].get("gpu", {})
            if "phi_mean" in gpu:
                f.write("GPU MÉTRICAS:\n")
                f.write(f"  Φ_mean: {gpu['phi_mean']:.6f}\n")
                f.write(f"  Φ_min: {gpu['phi_min']:.6f}\n")
                f.write(f"  Φ_max: {gpu['phi_max']:.6f}\n")
                f.write(f"  Ciclos: {gpu['num_cycles']}\n")
                f.write(f"  Tempo: {gpu['total_time_seconds']:.2f}s\n\n")

            quantum = self.report["metrics"].get("quantum", {})
            if "num_outcomes" in quantum:
                f.write("QUANTUM MÉTRICAS:\n")
                f.write(f"  Superposições: {quantum['num_outcomes']}/8\n")
                f.write(f"  Shots: {quantum['num_shots']}\n")
                f.write(f"  Tempo: {quantum['total_time_seconds']:.2f}s\n\n")

            ibm = self.report["metrics"].get("ibm_real", {})
            if "backend" in ibm:
                f.write("IBM MÉTRICAS:\n")
                f.write(f"  Backend: {ibm['backend']}\n")
                f.write(f"  Tempo: {ibm['total_time_seconds']:.2f}s\n")

        logger.info(f"✅ TXT: {txt_file}")

    def _print_summary(self) -> None:
        """Exibe resumo."""
        logger.info("\n" + "=" * 70)
        logger.info("RESUMO")
        logger.info("=" * 70)

        gpu = self.report["metrics"].get("gpu", {})
        if "phi_mean" in gpu:
            logger.info(f"GPU Φ_mean: {gpu['phi_mean']:.6f}")

        quantum = self.report["metrics"].get("quantum", {})
        if "num_outcomes" in quantum:
            logger.info(f"Quantum: {quantum['num_outcomes']}/8 superposições")

        logger.info("=" * 70)


async def main() -> None:
    """Main."""
    try:
        cert = RealCertification()
        await cert.run()
        sys.exit(0)
    except KeyboardInterrupt:
        logger.warning("Interrompido")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
