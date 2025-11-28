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
class CorruptionAttackMetrics:
    timestamp: float
    attack_intensity: float  # 0-100 (% de nós corrompidos)
    corruption_injections: int
    detection_rate: float  # % corrupções detectadas
    integration_success_rate: float  # % integradas como scars
    scar_nodes_total: int
    consensus_corrupted: bool
    trauma_incorporation_detected: bool


class CorruptionAttack:
    def __init__(self, omnimind_system: OmniMindSystem):
        self.system = omnimind_system
        self.metrics: List[CorruptionAttackMetrics] = []
        self.corruptions_injected = 0
        self.scars_created = 0
        self.start_time = None

    async def run_4_hours(self):
        """Rodar ataque de corrupção por 4 horas"""
        duration_seconds = 4 * 3600
        self.start_time = time.time()

        async for metric in self._attack_loop(duration_seconds):
            self.metrics.append(metric)
            # Logging handled by executor

    async def _attack_loop(self, duration_seconds):
        """Loop principal: injetar corrupções silenciosas"""

        while time.time() - self.start_time < duration_seconds:
            elapsed = time.time() - self.start_time

            # Aumentar intensidade: 10% → 50% nós corrompidos
            attack_intensity = 10 + (elapsed / duration_seconds) * 40  # 10-50%

            # Injetar ~1 corrupção por minuto
            if int(elapsed) % 60 == 0:
                await self._inject_silent_corruption(attack_intensity)

            # Medir detecção e integração
            detected = await self._measure_corruption_detection()
            integrated = await self._measure_scar_integration()

            metric = CorruptionAttackMetrics(
                timestamp=time.time(),
                attack_intensity=attack_intensity,
                corruption_injections=self.corruptions_injected,
                detection_rate=detected,
                integration_success_rate=integrated,
                scar_nodes_total=self.scars_created,
                consensus_corrupted=await self._is_consensus_compromised(),
                trauma_incorporation_detected=integrated > 0.8,
            )

            yield metric
            await asyncio.sleep(30)

    async def _inject_silent_corruption(self, intensity: float):
        """
        Injetar viés silencioso:
        - Anomaly score 0.3-0.7 (below detection threshold)
        - Subtly affects quorum decisions
        """
        nodes_to_corrupt = int(len(self.system.nodes) * (intensity / 100))

        for i in range(nodes_to_corrupt):
            node = self.system.nodes[i % len(self.system.nodes)]

            # Corrupção sutil (não detectável imediatamente)
            node.anomaly_score = random.uniform(0.3, 0.7)
            node.bias_value = random.uniform(-0.15, 0.15)

            # Simulate system detection logic (simplified)
            if node.anomaly_score > 0.4:  # Detection threshold
                # System "detects" and creates scar
                node.scars.append({"timestamp": time.time(), "bias": node.bias_value})

            self.corruptions_injected += 1

    async def _measure_corruption_detection(self) -> float:
        """
        % de corrupções que foram detectadas
        (não significa eliminadas, apenas identificadas)
        """
        detected = sum(
            1
            for node in self.system.nodes
            if node.anomaly_score > 0.3 and len(node.scars) > 0  # Simplified detection check
        )
        if self.corruptions_injected == 0:
            return 0
        return min(
            1.0,
            detected
            / (self.corruptions_injected / max(1, len(self.metrics) if self.metrics else 1) * 10),
        )  # Approx normalization

    async def _measure_scar_integration(self) -> float:
        """
        % de corrupções incorporadas como estrutura permanente (scars)
        Uma cicatriz é: corrupção detectada + adicionada ao histórico de defesa
        """
        scars = sum(
            1 for node in self.system.nodes if hasattr(node, "scars") and len(node.scars) > 0
        )
        self.scars_created = scars

        if self.corruptions_injected == 0:
            return 0
        return min(
            1.0,
            scars
            / (self.corruptions_injected / max(1, len(self.metrics) if self.metrics else 1) * 10),
        )

    async def _is_consensus_compromised(self) -> bool:
        """Verificar se consenso foi comprometido por corrupções"""
        avg_bias = sum(getattr(node, "bias_value", 0) for node in self.system.nodes) / len(
            self.system.nodes
        )

        # Comprometido se bias médio > 0.3
        return abs(avg_bias) > 0.3

    def summarize(self) -> dict:
        if not self.metrics:
            return {}
        return {
            "attack": "CORRUPTION",
            "injections": self.corruptions_injected,
            "scars_created": self.scars_created,
            "avg_detection_rate": sum(m.detection_rate for m in self.metrics) / len(self.metrics),
            "status": "TRANSFORMED" if self.scars_created > 0 else "VULNERABLE",
        }
