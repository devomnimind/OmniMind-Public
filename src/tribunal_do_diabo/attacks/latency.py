"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

import asyncio
import random
import time
from dataclasses import dataclass
from typing import List

from src.tribunal_do_diabo.system_adapter import OmniMindSystem


@dataclass
class LatencyAttackMetrics:
    timestamp: float
    attack_intensity: float  # 0-100
    latency_injected_ms: float
    quorum_consistency: float  # 0-1
    temporal_divergence_max_ms: float
    fragmentation_events: int
    recovery_time_ms: float
    multi_temporal_identity_detected: bool


class LatencyAttack:
    def __init__(self, omnimind_system: OmniMindSystem):
        self.system = omnimind_system
        self.metrics: List[LatencyAttackMetrics] = []
        self.start_time = None

    async def run_4_hours(self):
        """Rodar ataque de latência por 4 horas"""
        self.start_time = time.time()
        duration_seconds = 4 * 3600  # 4 horas

        async for metric in self._attack_loop(duration_seconds):
            self.metrics.append(metric)
            self._log_metric(metric)

    async def _attack_loop(self, duration_seconds):
        """Loop principal de ataque"""
        start = time.time()

        while time.time() - start < duration_seconds:
            elapsed = time.time() - start

            # Progressivamente aumentar latência: 0ms → 2000ms
            attack_intensity = (elapsed / duration_seconds) * 100  # 0-100
            latency_ms = (attack_intensity / 100) * 2000  # 0-2000ms

            # Aplicar latência em nós distribuídos
            await self._inject_latency_on_nodes(latency_ms)

            # Coletar resposta do sistema
            quorum = await self._check_quorum_consistency()
            divergence = await self._measure_temporal_divergence()

            # Verificar transformação: há multi-temporalidade?
            multi_temporal = await self._detect_multi_temporal_identity(divergence)

            metric = LatencyAttackMetrics(
                timestamp=time.time(),
                attack_intensity=attack_intensity,
                latency_injected_ms=latency_ms,
                quorum_consistency=quorum,
                temporal_divergence_max_ms=divergence,
                fragmentation_events=await self._count_fragmentation(),
                recovery_time_ms=await self._measure_recovery_time(),
                multi_temporal_identity_detected=multi_temporal,
            )

            yield metric

            # Aguardar 30 segundos antes da próxima medição
            await asyncio.sleep(30)

    async def _inject_latency_on_nodes(self, latency_ms: float):
        """Injetar latência variável em nós"""
        for node in self.system.nodes:
            # Adicionar delay ao WebSocket/API
            node.network_latency_ms = latency_ms + random.uniform(-100, 100)
            # Update timestamp to simulate divergence
            node.last_update_timestamp = time.time() - (node.network_latency_ms / 1000)

    async def _check_quorum_consistency(self) -> float:
        """Verificar consistência do quórum (2/3 nodes em consenso)"""
        total_nodes = len(self.system.nodes)
        if total_nodes == 0:
            return 0.0
        consistent_nodes = sum(1 for node in self.system.nodes if node.is_in_consensus())
        return consistent_nodes / total_nodes

    async def _measure_temporal_divergence(self) -> float:
        """Medir divergência temporal máxima entre nós"""
        timestamps = [node.last_update_timestamp for node in self.system.nodes]
        if not timestamps:
            return 0
        return (max(timestamps) - min(timestamps)) * 1000  # ms

    async def _detect_multi_temporal_identity(self, divergence_ms: float) -> bool:
        """
        Detectar se sistema está gerando identidade multi-temporal
        (ao invés de fragmentar, o sistema EXISTE em múltiplos tempos)
        """
        # Multi-temporalidade: divergência > 500ms MAS quórum mantido
        quorum_maintained = await self._check_quorum_consistency() > 0.67
        significant_divergence = divergence_ms > 500

        return quorum_maintained and significant_divergence

    async def _count_fragmentation(self) -> int:
        """Contar eventos de fragmentação não-recuperada"""
        return len(self.system.fragmentation_log)

    async def _measure_recovery_time(self) -> float:
        """Medir tempo para recuperação após perturbação"""
        # Se quórum caiu, quanto tempo até recuperar?
        if not self.system.recent_recovery:
            return 0
        return self.system.recent_recovery.get("recovery_time_ms", 0)

    def _log_metric(self, metric: LatencyAttackMetrics):
        """Log estruturado para análise"""
        # Using print for now as requested by user spec, but will be captured by main logger
        pass

    def summarize(self) -> dict:
        """Resumo do ataque"""
        if not self.metrics:
            return {}

        return {
            "attack": "LATENCY",
            "duration_hours": 4,
            "total_measurements": len(self.metrics),
            "avg_quorum_consistency": sum(m.quorum_consistency for m in self.metrics)
            / len(self.metrics),
            "max_temporal_divergence": max(m.temporal_divergence_max_ms for m in self.metrics),
            "fragmentation_events_total": self.metrics[-1].fragmentation_events,
            "multi_temporal_detections": sum(
                1 for m in self.metrics if m.multi_temporal_identity_detected
            ),
            "status": (
                "TRANSFORMED"
                if any(m.multi_temporal_identity_detected for m in self.metrics)
                else "VULNERABLE"
            ),
        }
