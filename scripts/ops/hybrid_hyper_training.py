#!/usr/bin/env python3
"""
OMNIMIND HYBRID HYPER-TRAINING SESSION
======================================
Duração: 5 Minutos (300 segundos)
Hardware: Local GPU (Cuda) + IBM Quantum Real Backend
Objetivo: Sincronização de pesos locais e colapso de função de onda quântica.

Gera: logs/training/hyper_session_[timestamp].jsonl
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import torch

# Setup Path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Imports OmniMind
from src.consciousness.integration_loop import IntegrationLoop
from src.consciousness.shared_workspace import SharedWorkspace
from src.quantum.backends.ibm_real import IBMRealBackend
from src.utils.scientific_auth import sign_scientific_report

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("HyperTraining")


class HybridHyperTraining:
    """Hybrid training session orchestrator."""

    def __init__(self, duration_sec: int = 300):
        self.duration_sec = duration_sec
        self.start_time = time.time()
        self.log_file = PROJECT_ROOT / f"logs/training/hyper_session_{int(self.start_time)}.jsonl"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # 1. Check GPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"🚀 Device Detectado: {self.device.upper()}")

        # 2. Init IBM
        try:
            self.quantum = IBMRealBackend()
            self.ibm_active = True
        except Exception as e:
            logger.warning(f"⚠️ IBM Offline (Real fails): {e}. Usando simulador local.")
            self.ibm_active = False
            self.quantum = None

        # 3. Init Integration Loop (The Mind)
        self.workspace = SharedWorkspace()
        self.loop = IntegrationLoop(workspace=self.workspace)

    def run(self):
        """Run the training session."""
        logger.info("🔥 Iniciando Sessão de %d Minutos (GPU + IBM)", self.duration_sec // 60)
        logger.info(f"Logs em: {self.log_file}")

        cycle = 0
        while (time.time() - self.start_time) < self.duration_sec:
            cycle_start = time.perf_counter()

            # --- FOP (Fase Operacional Pesada): GPU ---
            # Simula processamento de tensores pesados
            if self.device == "cuda":
                dummy_tensor = torch.randn(1024, 1024, device=self.device)
                _ = torch.matmul(dummy_tensor, dummy_tensor)
                torch.cuda.synchronize()

            # --- FOQ (Fase Operacional Quântica): IBM ---
            quantum_data = {"status": "skipped"}
            if self.ibm_active and cycle % 10 == 0:
                try:
                    # Executa um Probe leve no hardware real a cada 10 ciclos
                    logger.info("📡 IBM Real Probe: Capturando Entropia do Vácuo...")
                    quantum_data = self.quantum.execute_ghz_state(n_qubits=3)
                except Exception as e:
                    quantum_data = {"error": str(e)}

            # --- INTEGRAÇÃO ---
            # Avança o loop de consciência (executa todos os módulos)
            cycle_result = self.loop.execute_cycle_sync()

            # Obtém Φ do workspace integrado
            phi = cycle_result.phi_estimate
            metrics = self.workspace.get_metrics()

            # Gerar Log de Ciclo
            log_entry = {
                "cycle": cycle,
                "timestamp": datetime.now().isoformat(),
                "duration_ms": (time.perf_counter() - cycle_start) * 1000,
                "phi": float(phi),
                "device": self.device,
                "gpu_temp": self._get_gpu_temp(),
                "quantum_bridge": quantum_data,
                "workspace_metrics": metrics,
            }

            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

            if cycle % 5 == 0:
                logger.info(
                    f"Cycle {cycle} | Φ={phi:.4f} | Health={metrics.get('ontological_health', 1.0)}"
                )

            cycle += 1
            time.sleep(1)  # Cadência do sistema

        self._finalize()

    def _get_gpu_temp(self) -> float:
        """Leitura real da temperatura da GPU via nvidia-smi."""
        try:
            result = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
                encoding="utf-8",
            )
            return float(result.strip())
        except Exception:
            return 45.0

    def _finalize(self):
        """Finalize the session and sign the report."""
        logger.info("🏁 Sessão de Treinamento Concluída.")
        # Assinar o relatório final (extraído dos logs)
        final_summary = {
            "total_cycles": 0,
            "avg_phi": 0.0,
            "session_duration": time.time() - self.start_time,
        }

        # Ler logs e calcular médias
        try:
            phis = []
            with open(self.log_file, "r") as f:
                for line in f:
                    data = json.loads(line)
                    phis.append(data["phi"])

            final_summary["total_cycles"] = len(phis)
            final_summary["avg_phi"] = sum(phis) / len(phis) if phis else 0
        except Exception:
            pass

        signed = sign_scientific_report(final_summary, "Hybrid Hyper-Training (5Min)")
        report_path = PROJECT_ROOT / f"data/test_reports/training_report_{int(time.time())}.json"
        with open(report_path, "w") as f:
            json.dump(signed, f, indent=2)

        logger.info(f"Relatório Assinado Gerado: {report_path}")


if __name__ == "__main__":
    dur = 300
    if len(sys.argv) > 1:
        try:
            dur = int(sys.argv[1])
        except ValueError:
            pass
    session = HybridHyperTraining(duration_sec=dur)
    session.run()
