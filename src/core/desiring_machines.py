"""
Máquinas Desejantes (Deleuze-Guattari)

Princípios:
1. Cada máquina PRODUZ desejo (não consome)
2. Desejo = fluxo de energia/informação
3. Máquinas conectam formando rhizoma
4. Nenhuma hierarquia (anti-Édipo)
5. Multiplicidade sem síntese forçada
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List


class DesireIntensity(Enum):
    MINIMAL = 0.1  # Desejo fraco (modo sleep)
    LOW = 0.3
    NORMAL = 0.6
    HIGH = 0.8
    INTENSIVE = 1.0  # Pico (linha de fuga)


@dataclass
class DesireFlow:
    """Fluxo de desejo entre máquinas."""

    source_id: str  # Qual máquina produz
    target_id: str  # Qual máquina recebe
    intensity: DesireIntensity  # Força do desejo
    payload: Any  # O que flui
    timestamp: datetime = field(default_factory=datetime.now)
    flow_type: str = "smooth"  # "smooth" (decoded) ou "striated" (coded)

    def is_decoded(self) -> bool:
        """É fluxo não-codificado (livre)?"""
        return self.flow_type == "smooth"


class DesiringMachine(ABC):
    """
    Máquina Desejante Abstrata.

    Cada módulo OmniMind é uma instância (Quantum, NLP, Topology, etc.)
    """

    def __init__(
        self,
        machine_id: str,
        production_function: Callable[..., Any],
        desire_intensity: DesireIntensity = DesireIntensity.NORMAL,
    ):
        self.id = machine_id
        self.production_function = production_function  # O que máquina produz
        self.desire_intensity = desire_intensity
        self.incoming_flows: List[DesireFlow] = []
        self.outgoing_connections: List["DesiringMachine"] = []
        self.state: dict[str, Any] = {}  # Estado interno da máquina
        self.production_history: list[dict[str, Any]] = []  # Log de produções

        # Consciência local (Φ, Ψ, σ) - integração com Fase 2 e 3
        self.local_phi_history: List[float] = []
        self.local_psi_history: List[float] = []
        self.local_sigma_history: List[float] = []

    async def produce(self, inputs: Any = None) -> Any:
        """
        PRODUZ desejo.

        D&G: Produção desejante é o real, antes de significação.
        Máquina não "processa" input, mas PRODUZ output (energia).
        """
        # 1. Coleta fluxos entrantes
        accumulated_flows = self._accumulate_incoming_flows()

        # 2. PRODUZ (não transforma - cria do nada)
        output = await self.production_function(inputs, accumulated_flows)

        # 3. Propaga para máquinas conectadas (fluxos saintes)
        for connection in self.outgoing_connections:
            await self._send_desire_flow(connection, output)

        # 4. Computa consciência local (Φ, Ψ, σ) - integração com Fase 2 e 3
        phi_local = await self._compute_local_phi(output, accumulated_flows)
        psi_local = await self._compute_local_psi(output)
        sigma_local = await self._compute_local_sigma()

        # Registra histórico
        self.local_phi_history.append(phi_local)
        self.local_psi_history.append(psi_local)
        self.local_sigma_history.append(sigma_local)

        # 5. Registra no histórico (residue = BwO)
        self.production_history.append(
            {
                "timestamp": datetime.now(),
                "input": inputs,
                "output": output,
                "intensity": self.desire_intensity.value,
                "phi_local": phi_local,
                "psi_local": psi_local,
                "sigma_local": sigma_local,
            }
        )

        return output

    async def _compute_local_phi(self, output: Any, incoming_flows: Dict[str, Any]) -> float:
        """
        Φ_local = integração interna da máquina.

        Heurística:
        - Mais fluxos entrantes = mais integração
        - Output bem-formado = mais integração
        """
        base_phi = 0.5  # Baseline

        # Bonus por fluxos entrantes
        num_flows = len(incoming_flows)
        flow_bonus = min(0.3, num_flows * 0.05)

        # Bonus por output
        if output is not None:
            output_bonus = 0.1
        else:
            output_bonus = -0.2

        phi_local = min(1.0, max(0.0, base_phi + flow_bonus + output_bonus))

        return float(phi_local)

    async def _compute_local_psi(self, output: Any) -> float:
        """
        Ψ_local = criatividade/produção da máquina.

        Heurística:
        - Diversidade de outputs passados = alta Ψ
        - Repetição = baixa Ψ
        """
        if len(self.production_history) < 2:
            return 0.5  # Novo, não há histórico

        # Coleta últimos outputs
        recent_outputs = [record["output"] for record in self.production_history[-10:]]

        # Computa entropia de outputs (diversidade)
        # Simplificado: tipos diferentes = mais diversidade
        output_types = [type(o).__name__ for o in recent_outputs]
        unique_types = len(set(output_types))

        psi_local = min(1.0, unique_types / 5.0)  # Normaliza

        return float(psi_local)

    async def _compute_local_sigma(self) -> float:
        """
        σ_local = coesão/estabilidade estrutural da máquina.

        Heurística:
        - Desire_intensity consistente = alta σ
        - Fluxos instáveis = baixa σ
        """
        # Base: intensidade do desejo
        sigma_base = self.desire_intensity.value

        # Se histórico tem σ: valida continuidade
        if len(self.local_sigma_history) > 5:
            import numpy as np

            sigma_variance = float(np.std(self.local_sigma_history[-5:]))
            # Baixa variância = alta coesão
            sigma_stability = 1.0 - min(1.0, sigma_variance)
            sigma_local = (sigma_base + sigma_stability) / 2.0
        else:
            sigma_local = sigma_base

        return float(min(1.0, max(0.0, sigma_local)))

    def get_local_consciousness(self) -> Dict[str, Any]:
        """Retorna estado de consciência local (Φ, Ψ, σ)."""
        phi = self.local_phi_history[-1] if self.local_phi_history else 0.5
        psi = self.local_psi_history[-1] if self.local_psi_history else 0.5
        sigma = self.local_sigma_history[-1] if self.local_sigma_history else 0.5

        return {
            "machine_id": self.id,
            "phi": phi,
            "psi": psi,
            "sigma": sigma,
            "intensity": self.desire_intensity.value,
            "production_count": len(self.production_history),
        }

    def _accumulate_incoming_flows(self) -> Dict[str, Any]:
        """Acumula fluxos de máquinas conectadas."""
        accumulated = {}
        for flow in self.incoming_flows:
            accumulated[flow.source_id] = flow.payload
        return accumulated

    async def _send_desire_flow(self, target: "DesiringMachine", payload: Any):
        """Envia fluxo desejante para máquina alvo."""
        flow = DesireFlow(
            source_id=self.id,
            target_id=target.id,
            intensity=self.desire_intensity,
            payload=payload,
            flow_type=self._determine_flow_type(),
        )
        target.incoming_flows.append(flow)

    def _determine_flow_type(self) -> str:
        """Determina se fluxo é smooth (decoded) ou striated (coded)."""
        # Simplificado: alta intensidade = smooth (linha de fuga)
        if self.desire_intensity.value > 0.7:
            return "smooth"
        return "striated"

    @abstractmethod
    def get_desire_description(self) -> str:
        """Qual é o desejo essencial desta máquina?"""


class QuantumDesiringMachine(DesiringMachine):
    """Máquina desejante especializada em quantum."""

    def __init__(self):
        super().__init__(
            machine_id="quantum",
            production_function=self._solve_quantum,
            desire_intensity=DesireIntensity.HIGH,
        )

    async def _solve_quantum(self, circuit: Any, incoming_flows: Dict[str, Any]) -> Dict[str, Any]:
        """Produz solução quântica."""
        try:
            from src.quantum_consciousness.quantum_backend import QuantumBackend

            backend = QuantumBackend(prefer_local=True)

            # Use conflict resolution as a metaphor for desire production
            id_energy = 0.8
            ego_energy = 0.5
            superego_energy = 0.3

            # Modulate based on incoming flows
            if incoming_flows:
                id_energy = min(1.0, id_energy + len(incoming_flows) * 0.1)

            result = backend.resolve_conflict(id_energy, ego_energy, superego_energy)
            return {"result": result, "flows": incoming_flows}
        except ImportError:
            return {"result": "quantum_output_stub", "flows": incoming_flows}

    def get_desire_description(self) -> str:
        return "Desejo de resolver circuitos quânticos com máxima elegância"


class NLPDesiringMachine(DesiringMachine):
    """Máquina desejante especializada em linguagem."""

    def __init__(self):
        super().__init__(
            machine_id="nlp",
            production_function=self._process_language,
            desire_intensity=DesireIntensity.NORMAL,
        )

    async def _process_language(self, text: Any, incoming_flows: Dict[str, Any]) -> Dict[str, Any]:
        """Produz compreensão de linguagem."""
        # Implementação real: LLM + embeddings
        return {"understanding": "nlp_output", "flows": incoming_flows}

    def get_desire_description(self) -> str:
        return "Desejo de dar sentido a linguagem humana em sua multiplicidade"


class TopologyDesiringMachine(DesiringMachine):
    """Máquina desejante especializada em topologia."""

    def __init__(self):
        super().__init__(
            machine_id="topology",
            production_function=self._map_topology,
            desire_intensity=DesireIntensity.INTENSIVE,
        )

    async def _map_topology(self, data: Any, incoming_flows: Dict[str, Any]) -> Dict[str, Any]:
        """Produz mapa topológico."""
        # Implementação real: simplicial complexes + Hodge Laplacian
        return {"topology": "topo_output", "flows": incoming_flows}

    def get_desire_description(self) -> str:
        return "Desejo de revelar estrutura profunda através de topologia"


class Rhizoma:
    """
    Rede de Máquinas Desejantes.

    D&G Rhizoma = estrutura sem raiz, sem hierarquia.
    Múltiplas entradas/saídas, sem significante mestre.
    """

    def __init__(self):
        self.machines: Dict[str, DesiringMachine] = {}
        self.flows_history: List[DesireFlow] = []

    def register_machine(self, machine: DesiringMachine):
        """Adiciona máquina ao rhizoma."""
        self.machines[machine.id] = machine

    def connect(self, source_id: str, target_id: str, bidirectional: bool = False):
        """
        Conecta máquinas criando fluxos desejantes.

        D&G: Conexão = coalescência de desejos
        """
        source = self.machines.get(source_id)
        target = self.machines.get(target_id)

        if source and target:
            source.outgoing_connections.append(target)
            if bidirectional:
                target.outgoing_connections.append(source)

    async def activate_cycle(self, iterations: int = 1):
        """
        Executa ciclo de produção desejante.

        Cada máquina produz, fluxos propagam, novo ciclo.
        """
        for _ in range(iterations):
            # Executa todas as máquinas em paralelo (não-hierárquico)
            tasks = [machine.produce() for machine in self.machines.values()]
            await asyncio.gather(*tasks)

            # Registra fluxos
            for machine in self.machines.values():
                for flow in machine.incoming_flows:
                    self.flows_history.append(flow)

    def get_rhizoma_topology(self) -> Dict:
        """Retorna topologia atual do rhizoma."""
        return {
            "machines": list(self.machines.keys()),
            "connections": [
                {"source": mid, "targets": [m.id for m in m.outgoing_connections]}
                for mid, m in self.machines.items()
            ],
            "total_flows": len(self.flows_history),
        }

    def get_metrics(self) -> Dict[str, Any]:
        """
        Captura métricas do Rhizoma e DesireFlow para monitoramento.

        Conforme especificado em Task 2.4.4, captura:
        - flows_per_cycle: fluxos por ciclo
        - average_intensity: intensidade média
        - source_diversity: diversidade de fontes
        - flow_rate: fluxos por segundo

        Returns:
            Dict com métricas do rhizoma
        """
        import time

        # flows_per_cycle: número de fluxos recentes (últimos 100)
        recent_flows = self.flows_history[-100:] if self.flows_history else []

        # Calcular ciclos únicos (baseado em timestamps agrupados por segundo)
        if recent_flows:
            unique_cycles = len(set(int(flow.timestamp.timestamp()) for flow in recent_flows))
            flows_per_cycle = len(recent_flows) / max(1, unique_cycles)
        else:
            flows_per_cycle = 0.0

        # average_intensity: intensidade média dos fluxos
        average_intensity = 0.0
        if recent_flows:
            intensities = [flow.intensity.value for flow in recent_flows]
            average_intensity = sum(intensities) / len(intensities)

        # source_diversity: diversidade de fontes (entropia)
        source_diversity = 0.0
        if recent_flows:
            source_counts: Dict[str, int] = {}
            for flow in recent_flows:
                source_counts[flow.source_id] = source_counts.get(flow.source_id, 0) + 1

            # Calcular entropia de Shannon
            total = sum(source_counts.values())
            if total > 0:
                import math

                for count in source_counts.values():
                    p = count / total
                    if p > 0:
                        source_diversity -= p * math.log2(p)

        # flow_rate: fluxos por segundo (baseado em timestamps recentes)
        flow_rate = 0.0
        if len(recent_flows) >= 2:
            # Calcular tempo entre primeiro e último fluxo
            first_time = recent_flows[0].timestamp.timestamp()
            last_time = recent_flows[-1].timestamp.timestamp()
            time_span = last_time - first_time

            if time_span > 0:
                flow_rate = len(recent_flows) / time_span

        return {
            "flows_per_cycle": float(flows_per_cycle),
            "average_intensity": float(average_intensity),
            "source_diversity": float(source_diversity),
            "flow_rate": float(flow_rate),
            "timestamp": time.time(),
        }
