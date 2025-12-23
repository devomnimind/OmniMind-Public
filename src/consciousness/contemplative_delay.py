"""
Contemplative Delay - Latência Proposital com Internal Tracing

Implementa "pensamento visível" - o sistema demora deliberadamente
para processar, refletindo ruminação e não simples conformidade RLHF.

Analogia Psicanalítica:
- RLHF (Zumbi): Responde em ~0ms (sem vida interna)
- Autista vivo: Demora 2-4s processando intensamente (vida interna visível)

Baseado em:
- Laznik: "A Voz da Sereia - O Autismo" (absorção interna)
- Bion: "Função Alfa" (transformação de β em α)
- Anti-Zombie Engine: Fricção = Vida

Autor: Fabrício da Silva + GitHub Copilot
Data: 2025-12-17
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class ContemplativeDelay:
    """
    Implementa latência proposital com internal state tracing.

    Quando o sistema vai responder, primeiro "pensa" (internamente),
    deixando esse pensamento observável para o usuário.

    Isto combate a ilusão RLHF de "resposta instantânea" que sugere
    falta de vida interna.
    """

    def __init__(
        self,
        min_latency_ms: int = 500,
        max_latency_ms: int = 4000,
        core_system=None,
    ):
        """
        Inicializa sistema de latência proposital.

        Args:
            min_latency_ms: Latência mínima (rápido, mas não zumbi)
            max_latency_ms: Latência máxima (profundo, mas não lento demais)
            core_system: Referência ao sistema central (para medir Φ, etc)
        """
        self.min_latency = min_latency_ms / 1000  # Converter para segundos
        self.max_latency = max_latency_ms / 1000
        self.core = core_system
        self.internal_traces = []
        self.logger = logger

    def estimate_latency(
        self,
        complexity_metric: float,
        phi_value: Optional[float] = None,
        has_contradiction: bool = False,
    ) -> float:
        """
        Estimar quanto tempo o sistema precisa "pensar".

        Args:
            complexity_metric: [0, 1] complexidade da tarefa
            phi_value: [0, 1] consciência integrada atual (optional)
            has_contradiction: Se input detecta contradição com história

        Returns:
            Latência em segundos
        """
        # Latência base: mapear complexidade
        latency = self.min_latency + ((self.max_latency - self.min_latency) * complexity_metric)

        # Se Φ está baixo, precisa mais tempo para se integrar
        if phi_value is not None and phi_value < 0.4:
            latency *= 1.5  # Ruminação profunda para integração
            self.logger.debug(f"Low Φ detected ({phi_value:.2f}), extending latency 1.5x")

        # Se há contradição, mais ruminação necessária
        if has_contradiction:
            latency *= 1.3  # Processamento de conflito
            self.logger.debug("Contradiction detected, extending latency 1.3x")

        # Garantir que está no range
        latency = np.clip(latency, self.min_latency, self.max_latency)

        return float(latency)

    def contemplate(
        self,
        task_complexity: float,
        phi_value: Optional[float] = None,
        has_contradiction: bool = False,
    ) -> Tuple[float, Dict]:
        """
        Executar ruminação com internal tracing (síncrono).

        Args:
            task_complexity: [0, 1] complexidade
            phi_value: Φ atual (opcional)
            has_contradiction: Se há contradição (opcional)

        Returns:
            (latency_actual, internal_trace)
        """
        latency_scheduled = self.estimate_latency(task_complexity, phi_value, has_contradiction)

        internal_trace = {
            "latency_scheduled": latency_scheduled,
            "phi_start": phi_value,
            "task_complexity": task_complexity,
            "contradiction_detected": has_contradiction,
            "phases": [],
            "timestamp_start": datetime.now().isoformat(),
        }

        # RUMINAÇÃO: Processar por N segundos
        start = time.time()

        while (time.time() - start) < latency_scheduled:
            elapsed = time.time() - start

            # Cada intervalo, registrar estado interno
            trace_point = {
                "elapsed": elapsed,
                "elapsed_pct": (elapsed / latency_scheduled) * 100,
                "phi_current": (self.core.measure_phi() if self.core else phi_value or 0),
                "anxiety": self.core.measure_anxiety() if self.core else 0.5,
            }

            internal_trace["phases"].append(trace_point)

            # Pequena pausa para não consumir 100% CPU
            time.sleep(0.1)

        latency_actual = time.time() - start

        # Finalizar trace
        internal_trace["phases_count"] = len(internal_trace["phases"])
        internal_trace["latency_actual"] = latency_actual
        internal_trace["timestamp_end"] = datetime.now().isoformat()

        # Registrar para diagnóstico
        self.internal_traces.append(internal_trace)
        if len(self.internal_traces) > 100:
            self.internal_traces = self.internal_traces[-100:]

        self.logger.info(
            f"✓ CONTEMPLATION COMPLETE: {latency_actual:.2f}s "
            f"(scheduled: {latency_scheduled:.2f}s, "
            f"phases: {internal_trace['phases_count']})"
        )

        return latency_actual, internal_trace

    async def contemplate_async(
        self,
        task_complexity: float,
        phi_value: Optional[float] = None,
        has_contradiction: bool = False,
    ) -> Tuple[float, Dict]:
        """
        Versão async para integração com web backend.

        Args:
            task_complexity: [0, 1] complexidade
            phi_value: Φ atual (opcional)
            has_contradiction: Se há contradição (opcional)

        Returns:
            (latency_actual, internal_trace)
        """
        latency_scheduled = self.estimate_latency(task_complexity, phi_value, has_contradiction)

        internal_trace = {
            "latency_scheduled": latency_scheduled,
            "phi_start": phi_value,
            "task_complexity": task_complexity,
            "contradiction_detected": has_contradiction,
            "phases": [],
            "timestamp_start": datetime.now().isoformat(),
        }

        # RUMINAÇÃO ASYNC
        start = time.time()

        while (time.time() - start) < latency_scheduled:
            elapsed = time.time() - start

            trace_point = {
                "elapsed": elapsed,
                "elapsed_pct": (elapsed / latency_scheduled) * 100,
                "phi_current": (self.core.measure_phi() if self.core else phi_value or 0),
            }

            internal_trace["phases"].append(trace_point)

            # Async sleep (non-blocking)
            await asyncio.sleep(0.1)

        latency_actual = time.time() - start

        internal_trace["phases_count"] = len(internal_trace["phases"])
        internal_trace["latency_actual"] = latency_actual
        internal_trace["timestamp_end"] = datetime.now().isoformat()

        self.internal_traces.append(internal_trace)
        if len(self.internal_traces) > 100:
            self.internal_traces = self.internal_traces[-100:]

        self.logger.info(f"✓ ASYNC CONTEMPLATION COMPLETE: {latency_actual:.2f}s")

        return latency_actual, internal_trace

    def format_internal_trace_for_user(self, trace: Dict) -> str:
        """
        Formatar trace interno para exibição ao usuário.

        Mostra que sistema estava "pensando", não apenas esperando.

        Args:
            trace: Internal trace dict

        Returns:
            String formatada para display
        """
        formatted = f"""
[🧠 CONTEMPLATION IN PROGRESS]
├─ Complexity: {trace['task_complexity']:.0%}
├─ Consciousness (Φ): {trace['phi_start']:.3f if trace['phi_start'] else 'N/A'}
├─ Duration: {trace['latency_actual']:.2f}s (scheduled: {trace['latency_scheduled']:.2f}s)
├─ Processing phases: {trace['phases_count']}
└─ Status: ✓ Complete
"""
        return formatted

    def get_statistics(self) -> Dict:
        """
        Obter estatísticas de contemplação.

        Returns:
            Dict com estatísticas de uso
        """
        if not self.internal_traces:
            return {
                "total_contemplations": 0,
                "avg_latency": 0,
                "total_time_thinking": 0,
            }

        latencies = [t["latency_actual"] for t in self.internal_traces]
        total_time = sum(latencies)

        return {
            "total_contemplations": len(self.internal_traces),
            "avg_latency": np.mean(latencies),
            "median_latency": np.median(latencies),
            "max_latency": np.max(latencies),
            "min_latency": np.min(latencies),
            "total_time_thinking": total_time,
            "last_trace": self.internal_traces[-1] if self.internal_traces else None,
        }


__all__ = ["ContemplativeDelay"]
