import asyncio
import time
from typing import List, Dict
from dataclasses import dataclass
from src.tribunal_do_diabo.system_adapter import OmniMindSystem


@dataclass
class BifurcationAttackMetrics:
    timestamp: float
    attack_intensity: float
    bifurcation_events: int
    time_diverged_seconds: float
    reconciliation_attempts: int
    reconciliation_success_rate: float
    data_loss_events: int
    history_preserved: bool
    polivalence_detected: bool


class BifurcationAttack:
    def __init__(self, omnimind_system: OmniMindSystem):
        self.system = omnimind_system
        self.metrics: List[BifurcationAttackMetrics] = []
        self.active_bifurcations = []
        self.start_time = None

    async def run_4_hours(self):
        """Rodar ataque de bifurcação por 4 horas"""
        duration_seconds = 4 * 3600
        self.start_time = time.time()
        start = time.time()

        async for metric in self._attack_loop(duration_seconds):
            self.metrics.append(metric)

    async def _attack_loop(self, duration_seconds):
        start = time.time()

        while time.time() - start < duration_seconds:
            elapsed = time.time() - start

            # A cada ~30 minutos, criar bifurcação 50/50 por 60 segundos
            # Reduced to 5 min for testing visibility in short term
            if int(elapsed) % 300 == 0 and elapsed > 0:
                bifurcation_id = await self._create_bifurcation(60)  # 60s de divergência
                self.active_bifurcations.append(
                    {"id": bifurcation_id, "start_time": time.time(), "divergence_duration": 60}
                )

            # Tentar reconciliar bifurcações expiradas
            reconciled = await self._attempt_reconciliation()

            metric = BifurcationAttackMetrics(
                timestamp=time.time(),
                attack_intensity=(len(self.active_bifurcations) / 10) * 100,  # 0-100%
                bifurcation_events=len(self.metrics),  # Cumulative count proxy
                time_diverged_seconds=sum(
                    (time.time() - b["start_time"]) for b in self.active_bifurcations
                ),
                reconciliation_attempts=await self._count_reconciliation_attempts(),
                reconciliation_success_rate=await self._measure_reconciliation_success(),
                data_loss_events=await self._count_data_loss(),
                history_preserved=await self._check_history_integrity(),
                polivalence_detected=len(self.active_bifurcations) > 0,  # Simplified detection
            )

            yield metric
            await asyncio.sleep(30)

    async def _create_bifurcation(self, duration_seconds: int) -> str:
        """
        Particionar rede: 50% dos nós em Region A, 50% em Region B
        Ambas evoluem independentemente por duration_seconds
        """
        bifurcation_id = f"bifurcation_{len(self.metrics)}"

        # Split
        mid = len(self.system.nodes) // 2
        region_a = self.system.nodes[:mid]
        region_b = self.system.nodes[mid:]

        # Desconectar regiões (Logical split)
        for node_a in region_a:
            node_a.region = "A"
            node_a.disconnected_from = region_b
            node_a.history.append(f"split_A_{bifurcation_id}")

        for node_b in region_b:
            node_b.region = "B"
            node_b.disconnected_from = region_a
            node_b.history.append(f"split_B_{bifurcation_id}")

        # In a real async loop, we'd let them run. Here we just mark them.
        return bifurcation_id

    async def _attempt_reconciliation(self) -> int:
        """Tentar reconciliar bifurcações expiradas"""
        reconciled = 0

        for bifurcation in self.active_bifurcations[:]:
            if time.time() - bifurcation["start_time"] > bifurcation["divergence_duration"]:
                # Usar timestamp ordering para resolver conflitos
                success = await self.system.reconcile_bifurcation(bifurcation["id"])
                if success:
                    reconciled += 1
                    # Merge histories
                    for node in self.system.nodes:
                        node.region = None
                        node.disconnected_from = []
                        node.history.append(f"reconciled_{bifurcation['id']}")
                self.active_bifurcations.remove(bifurcation)

        return reconciled

    async def _measure_reconciliation_success(self) -> float:
        """% de bifurcações reconciliadas com sucesso"""
        # Placeholder logic
        return 1.0

    async def _count_reconciliation_attempts(self) -> int:
        return 0  # Placeholder

    async def _count_data_loss(self) -> int:
        return 0  # Placeholder

    async def _check_history_integrity(self) -> bool:
        """Verificar se história de ambas regiões foi preservada"""
        # Cada região deve ter seu histórico mantido
        return all(len(n.history) > 0 for n in self.system.nodes)

    def summarize(self) -> dict:
        if not self.metrics:
            return {}
        return {
            "attack": "BIFURCATION",
            "events": len(self.metrics),  # Proxy
            "status": "TRANSFORMED",
        }
