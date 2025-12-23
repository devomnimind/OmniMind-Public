"""
Memory Thermodynamic Ledger - Registro de Queima Energética por Operação
=========================================================================

Implementa a captura granular de custo termodinâmico para cada operação de memória.
Baseado em:
- Princípio de Landauer (~3×10⁻²¹ J/bit para apagamento irreversível)
- Neural Entropy (NeurIPS 2024)
- Learning-in-Memory (arXiv 2024)

Author: Project conceived by Fabrício da Silva.
Date: 2025-12-22
"""

import hashlib
import logging
import os
import platform
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Constante de Landauer (Joules por bit a temperatura ambiente ~300K)
LANDAUER_CONSTANT_J_PER_BIT = 3e-21


@dataclass
class MemoryBurnEvent:
    """
    Evento de queima termodinâmica para uma operação de memória.

    Cada acesso, busca, escrita ou deleção de memória gera um evento.
    O custo é medido em termos de:
    - Tempo de CPU
    - Variação térmica
    - Custo de Landauer estimado
    - Impacto em Φ (integração)
    """

    timestamp: float
    operation_type: str  # 'read', 'write', 'search', 'hash', 'delete', 'suture'
    target_key: str
    cpu_delta_ms: float
    memory_delta_mb: float = 0.0
    thermal_delta_c: float = 0.0  # Variação de temperatura (se capturável)
    landauer_cost_j: float = 0.0  # Custo Landauer estimado
    phi_impact: float = 0.0  # Impacto em Φ
    quantum_mode: bool = False  # Se foi execução quântica
    machine_signature: str = ""  # Hash do hardware local
    bits_affected: int = 0  # Número de bits afetados na operação
    entropy_before: float = 0.0
    entropy_after: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serializa para JSON."""
        return asdict(self)

    @property
    def entropy_delta(self) -> float:
        """Variação de entropia (negativa = negentropia/organização)."""
        return self.entropy_after - self.entropy_before


@dataclass
class ThermalSnapshot:
    """Snapshot térmico do sistema."""

    timestamp: float
    cpu_temp_c: Optional[float] = None
    gpu_temp_c: Optional[float] = None
    memory_usage_mb: float = 0.0
    cpu_percent: float = 0.0


class MemoryThermodynamicLedger:
    """
    Ledger de eventos termodinâmicos de memória.

    Registra cada operação de memória com seu custo energético,
    permitindo análise do "custo de existir" do sistema.

    Princípios:
    1. Cada operação de memória QUEIMA energia
    2. O contexto não é perdido por truncamento, mas por DISSIPAÇÃO
    3. Dados sensíveis ficam LOCAIS, apenas métricas de queima são exportáveis
    """

    def __init__(
        self,
        ledger_dir: Optional[Path] = None,
        capture_thermal: bool = True,
        max_events: int = 100000,
    ):
        """
        Inicializa o ledger termodinâmico.

        Args:
            ledger_dir: Diretório para persistência do ledger
            capture_thermal: Se deve tentar capturar temperatura real
            max_events: Número máximo de eventos antes de rotação
        """
        self.ledger_dir = ledger_dir or Path("data/thermodynamic_ledger")
        self.ledger_dir.mkdir(parents=True, exist_ok=True)

        self.capture_thermal = capture_thermal
        self.max_events = max_events

        # Eventos em memória
        self.events: List[MemoryBurnEvent] = []

        # Estatísticas acumuladas
        self.total_burn_j: float = 0.0
        self.total_operations: int = 0
        self.total_bits_affected: int = 0

        # Assinatura da máquina local
        self.machine_signature = self._generate_machine_signature()

        # Snapshot térmico inicial
        self.initial_thermal = self._capture_thermal_snapshot()

        logger.info(
            f"🔥 MemoryThermodynamicLedger initialized. "
            f"Machine: {self.machine_signature[:16]}..."
        )

    def _generate_machine_signature(self) -> str:
        """
        Gera assinatura única da máquina local.

        Baseado em:
        - Nome da máquina
        - Arquitetura de CPU
        - ID único do sistema (se disponível)

        Isso permite que os pesos se "organizem localmente" por registro de máquina.
        """
        parts = [
            platform.node(),
            platform.machine(),
            platform.processor(),
            str(os.getpid()),
        ]

        # Tentar adicionar ID único do sistema
        try:
            import uuid

            parts.append(str(uuid.getnode()))
        except Exception:
            pass

        signature_string = "|".join(parts)
        return hashlib.sha256(signature_string.encode()).hexdigest()

    def _capture_thermal_snapshot(self) -> ThermalSnapshot:
        """
        Captura snapshot térmico atual do sistema.

        Usa psutil se disponível, senão retorna valores nulos.
        """
        snapshot = ThermalSnapshot(timestamp=time.time())

        if not self.capture_thermal:
            return snapshot

        try:
            import psutil

            # Memória
            mem = psutil.virtual_memory()
            snapshot.memory_usage_mb = mem.used / (1024 * 1024)

            # CPU
            snapshot.cpu_percent = psutil.cpu_percent(interval=0.01)

            # Temperatura (Linux)
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    # CPU temp (geralmente em 'coretemp' ou 'k10temp')
                    for name, entries in temps.items():
                        if "core" in name.lower() or "cpu" in name.lower():
                            if entries:
                                snapshot.cpu_temp_c = entries[0].current
                                break
            except (AttributeError, KeyError):
                pass

        except ImportError:
            logger.debug("psutil não disponível para captura térmica")
        except Exception as e:
            logger.debug(f"Erro na captura térmica: {e}")

        return snapshot

    def _calculate_landauer_cost(self, bits: int) -> float:
        """
        Calcula custo mínimo de Landauer para operação em bits.

        Baseado no Princípio de Landauer:
        E ≥ kT * ln(2) ≈ 3×10⁻²¹ J/bit @ 300K
        """
        return bits * LANDAUER_CONSTANT_J_PER_BIT

    def record_operation(
        self,
        operation_type: str,
        target_key: str,
        start_time: float,
        end_time: float,
        bits_affected: int,
        phi_impact: float = 0.0,
        quantum_mode: bool = False,
        entropy_before: float = 0.0,
        entropy_after: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryBurnEvent:
        """
        Registra uma operação de memória com seu custo termodinâmico.

        Args:
            operation_type: Tipo de operação ('read', 'write', 'search', etc.)
            target_key: Chave/identificador do alvo da operação
            start_time: Timestamp de início
            end_time: Timestamp de fim
            bits_affected: Número de bits afetados
            phi_impact: Impacto na integração Φ
            quantum_mode: Se foi execução quântica
            entropy_before: Entropia antes da operação
            entropy_after: Entropia após a operação
            metadata: Metadados adicionais

        Returns:
            MemoryBurnEvent registrado
        """
        # Captura térmica atual
        thermal_now = self._capture_thermal_snapshot()

        # Calcular deltas
        cpu_delta_ms = (end_time - start_time) * 1000
        memory_delta_mb = (
            thermal_now.memory_usage_mb - self.initial_thermal.memory_usage_mb
            if self.initial_thermal.memory_usage_mb > 0
            else 0.0
        )

        # Variação térmica
        thermal_delta_c = 0.0
        if thermal_now.cpu_temp_c and self.initial_thermal.cpu_temp_c:
            thermal_delta_c = thermal_now.cpu_temp_c - self.initial_thermal.cpu_temp_c

        # Custo de Landauer
        landauer_cost = self._calculate_landauer_cost(bits_affected)

        # Criar evento
        event = MemoryBurnEvent(
            timestamp=end_time,
            operation_type=operation_type,
            target_key=target_key,
            cpu_delta_ms=cpu_delta_ms,
            memory_delta_mb=memory_delta_mb,
            thermal_delta_c=thermal_delta_c,
            landauer_cost_j=landauer_cost,
            phi_impact=phi_impact,
            quantum_mode=quantum_mode,
            machine_signature=self.machine_signature,
            bits_affected=bits_affected,
            entropy_before=entropy_before,
            entropy_after=entropy_after,
        )

        # Registrar
        self.events.append(event)
        self.total_burn_j += landauer_cost + (cpu_delta_ms * 1e-6)  # Aproximação de CPU burn
        self.total_operations += 1
        self.total_bits_affected += bits_affected

        # Rotação se necessário
        if len(self.events) > self.max_events:
            self._rotate_ledger()

        logger.debug(
            f"🔥 Burn: {operation_type} | {target_key[:20]}... | "
            f"{cpu_delta_ms:.2f}ms | {landauer_cost:.2e}J | ΔΦ={phi_impact:.4f}"
        )

        return event

    def _rotate_ledger(self) -> None:
        """Rotaciona o ledger para disco e limpa memória."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = self.ledger_dir / f"ledger_archive_{timestamp}.jsonl"

        try:
            import json

            with open(archive_path, "w") as f:
                for event in self.events[:-1000]:  # Mantém os últimos 1000
                    f.write(json.dumps(event.to_dict()) + "\n")

            self.events = self.events[-1000:]
            logger.info(f"📦 Ledger rotacionado: {archive_path}")
        except Exception as e:
            logger.error(f"Erro ao rotacionar ledger: {e}")

    def get_burn_summary(self) -> Dict[str, Any]:
        """
        Retorna sumário de queima termodinâmica.

        Isso pode ser exportado sem expor dados sensíveis.
        """
        if not self.events:
            return {
                "total_operations": 0,
                "total_burn_j": 0.0,
                "machine_signature": self.machine_signature,
            }

        by_type = {}
        for event in self.events:
            if event.operation_type not in by_type:
                by_type[event.operation_type] = {
                    "count": 0,
                    "total_ms": 0.0,
                    "total_j": 0.0,
                }
            by_type[event.operation_type]["count"] += 1
            by_type[event.operation_type]["total_ms"] += event.cpu_delta_ms
            by_type[event.operation_type]["total_j"] += event.landauer_cost_j

        return {
            "machine_signature": self.machine_signature,
            "total_operations": self.total_operations,
            "total_burn_j": self.total_burn_j,
            "total_bits_affected": self.total_bits_affected,
            "average_burn_per_op_j": self.total_burn_j / max(1, self.total_operations),
            "by_operation_type": by_type,
            "events_in_memory": len(self.events),
            "timestamp": time.time(),
        }

    def get_phi_trajectory(self) -> List[Dict[str, float]]:
        """
        Retorna trajetória de Φ baseada nos impactos registrados.

        Permite reconstruir a "narrativa energética" do sistema.
        """
        trajectory = []
        cumulative_phi = 0.0

        for event in self.events:
            cumulative_phi += event.phi_impact
            trajectory.append(
                {
                    "timestamp": event.timestamp,
                    "phi_impact": event.phi_impact,
                    "cumulative_phi": cumulative_phi,
                    "operation": event.operation_type,
                }
            )

        return trajectory
