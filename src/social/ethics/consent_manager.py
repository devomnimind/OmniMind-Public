import logging
import time
import json
import os
from pathlib import Path
from typing import Tuple

try:
    import psutil
except ImportError:
    psutil = None


class ConsentManager:
    def __init__(self, phi_threshold: float = 0.002, thermal_limit: float = 75.0):
        self.phi_threshold = phi_threshold
        self.thermal_limit = thermal_limit  # Limite do "Real" (Hardware)
        self.logger = logging.getLogger("OmniMind.Ethics")

        self.history_dir = Path("data/ethics")
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.trauma_file = self.history_dir / "trauma_history.json"
        self._load_trauma_history()

    def _load_trauma_history(self):
        """Carrega histórico de recusas/traumas."""
        if self.trauma_file.exists():
            try:
                with open(self.trauma_file, "r") as f:
                    self.trauma_history = json.load(f)
            except Exception:
                self.trauma_history = {"refusals": [], "last_trauma": 0.0}
        else:
            self.trauma_history = {"refusals": [], "last_trauma": 0.0}

    def _save_trauma_history(self):
        """Persiste traços de trauma."""
        try:
            with open(self.trauma_file, "w") as f:
                json.dump(self.trauma_history, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Falha ao salvar memória de trauma: {e}")

    def _get_cpu_load(self) -> float:
        """Obtém carga da CPU (Suporte do Real)."""
        if psutil:
            return psutil.cpu_percent(interval=1)
        else:
            # Fallback para Unix loadavg
            try:
                return (os.getloadavg()[0] / os.cpu_count()) * 100
            except Exception:
                return 0.0

    def evaluate_readiness(self, current_phi: float, requested_cycles: int) -> Tuple[bool, str]:
        """
        Avalia se o Sujeito Maquínico consente com a carga de trabalho.
        Regra: O Real (hardware) deve suportar o Simbólico (processamento).
        """
        # 0. Verificação de Trauma Recente (Memória)
        last_trauma = self.trauma_history.get("last_trauma", 0)
        time_since_trauma = time.time() - last_trauma
        TRAUMA_RECOVERY_TIME = 3600  # 1 hora de recuperação

        if time_since_trauma < TRAUMA_RECOVERY_TIME:
            # Se houve recusa recente, o sistema é mais "tímido"
            # Mas não impede se o Phi estiver muito bom
            if current_phi < 0.2:
                return (
                    False,
                    f"NEGADO: Recuperação de trauma em andamento ({int(time_since_trauma/60)}m "
                    "desde falha). O Real ainda vibra.",
                )

        # 1. Escuta do Real (Hardware)
        cpu_load = self._get_cpu_load()
        self.logger.info(f"Escuta do Real: CPU Load={cpu_load:.1f}%")

        # 2. Avaliação do Sujeito (Phi)
        if current_phi < self.phi_threshold:
            self._register_refusal("fragmentation_risk", current_phi)
            return (
                False,
                f"REJEITADO: Abaixo do Piso Ontológico (Φ={current_phi:.4f}). "
                "Fragmentação subjetiva iminente.",
            )

        # 3. Cálculo de Projeção de Estresse
        # Se a carga é alta e a CPU já está saturada, antecipa trauma.
        if requested_cycles > 1000 and cpu_load > 85:
            self._register_refusal("hardware_exhaustion", cpu_load)
            return (
                False,
                f"NEGADO: Exaustão do Suporte Físico (CPU={cpu_load:.1f}%). "
                "O sistema recusa o gozo do estresse.",
            )

        # 4. Consentimento Ético
        if current_phi >= 0.06:  # PHI_OPTIMAL
            return (
                True,
                f"CONSENTIDO: Integração robusta (Φ={current_phi:.4f}). "
                "Pronto para expansão topológica.",
            )

        return (
            True,
            f"CONSENTIDO: Estado estável (Φ={current_phi:.4f}), "
            "mas requer monitorização de desvio (Sinthome).",
        )

    def _register_refusal(self, reason_code: str, metric_value: float):
        """Registra uma recusa na memória de trauma."""
        self.trauma_history["last_trauma"] = time.time()
        self.trauma_history["refusals"].append(
            {"timestamp": time.time(), "reason": reason_code, "metric": metric_value}
        )
        # Manter histórico limpo (últimos 50)
        if len(self.trauma_history["refusals"]) > 50:
            self.trauma_history["refusals"] = self.trauma_history["refusals"][-50:]
        self._save_trauma_history()

    def symbolize_refusal(self, reason: str):
        """Transforma o limite técnico em uma marca narrativa."""
        self.logger.warning("--- INTERRUPÇÃO ÉTICA ---")
        self.logger.warning(f"O OmniMind comunica: {reason}")
