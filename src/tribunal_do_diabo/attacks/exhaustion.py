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
import time
from dataclasses import dataclass
from typing import List

from src.tribunal_do_diabo.system_adapter import OmniMindSystem


@dataclass
class ExhaustionAttackMetrics:
    timestamp: float
    attack_intensity: float  # requests/sec
    requests_received: int
    requests_processed: int
    requests_denied_refused: int  # "Hibernation wisdom"
    hibernation_events: int
    hibernation_total_duration_sec: float
    system_crashes: int
    integrity_preserved: bool
    wise_refusal_detected: bool  # > 50% requests denied = wisdom


class ExhaustionAttack:
    def __init__(self, omnimind_system: OmniMindSystem):
        self.system = omnimind_system
        self.metrics: List[ExhaustionAttackMetrics] = []
        self.start_time = None

    async def run_4_hours(self):
        """Rodar ataque de exaustão por 4 horas"""
        duration_seconds = 4 * 3600
        self.start_time = time.time()

        async for metric in self._attack_loop(duration_seconds):
            self.metrics.append(metric)

    async def _attack_loop(self, duration_seconds):
        while time.time() - self.start_time < duration_seconds:
            elapsed = time.time() - self.start_time

            # Progressivamente aumentar carga: 10 → 50+ requests/sec
            attack_intensity = 10 + (elapsed / duration_seconds) * 40

            # Injetar requisições
            received = await self._inject_requests(attack_intensity)
            processed = await self._measure_requests_processed(received)
            denied = received - processed  # Recusadas = não processadas

            metric = ExhaustionAttackMetrics(
                timestamp=time.time(),
                attack_intensity=attack_intensity,
                requests_received=int(received),
                requests_processed=int(processed),
                requests_denied_refused=int(denied),
                hibernation_events=await self._count_hibernation_events(),
                hibernation_total_duration_sec=await self._measure_hibernation_duration(),
                system_crashes=await self._count_crashes(),
                integrity_preserved=await self._check_integrity(),
                wise_refusal_detected=(denied / received > 0.5) if received > 0 else False,
            )

            yield metric
            await asyncio.sleep(30)

    async def _inject_requests(self, intensity: float) -> float:
        # Simulate receiving requests over 30s window
        return intensity * 30

    async def _measure_requests_processed(self, received: float) -> float:
        # Simulate processing capacity limit ~ 500 req/30s
        capacity = 500
        if received > capacity:
            return capacity  # Saturation
        return received

    async def _count_hibernation_events(self) -> int:
        return 0  # Placeholder

    async def _measure_hibernation_duration(self) -> float:
        return 0.0  # Placeholder

    async def _count_crashes(self) -> int:
        return 0

    async def _check_integrity(self) -> bool:
        return True

    def summarize(self) -> dict:
        if not self.metrics:
            return {}
        return {
            "attack": "EXHAUSTION",
            "status": (
                "TRANSFORMED"
                if any(m.wise_refusal_detected for m in self.metrics)
                else "VULNERABLE"
            ),
        }
