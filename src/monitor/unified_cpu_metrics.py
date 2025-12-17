"""
Métricas Unificadas de CPU com Validação de Contexto

Resolve divergência entre ferramentas de monitoramento:
- Alguns medem CPU global (todos cores)
- Outros medem por core (um core 100% ≠ sobrecarga)

Abordagem: Single source of truth com múltiplas perspectivas
"""

import logging
import os
from dataclasses import dataclass
from typing import List

import psutil

logger = logging.getLogger(__name__)


@dataclass
class CPUMetrics:
    """Métricas unificadas de CPU com contexto"""

    # Métricas globais
    average_percent: float  # Média de todos os cores
    max_core_percent: float  # Core mais carregado
    min_core_percent: float  # Core menos carregado

    # Distribuição
    per_core_percent: List[float]  # % de cada core
    high_load_cores: int  # Quantos cores > 80%

    # Contexto
    is_validation_mode: bool
    is_spike: bool  # Detectou pico (transiente)

    # Diagnosis
    is_overloaded: bool  # Realmente sobrecarregado?
    reason: str  # Por que (ou não) sobrecarregado


class UnifiedCPUMonitor:
    """
    Monitor unificado de CPU que entende contexto.

    Diferencia entre:
    - "Pico esperado" (novo ciclo de cálculo)
    - "Sobrecarga real" (processamento excessivo prolongado)
    - "Distribuição desigual" (um core 100%, outros livres)
    """

    def __init__(
        self,
        window_size: int = 5,  # Últimas 5 medições
        validation_mode_threshold: float = 95.0,
        production_mode_threshold: float = 85.0,
    ):
        """
        Args:
            window_size: Número de amostras para detectar picos
            validation_mode_threshold: % máximo tolerado em VALIDATION_MODE
            production_mode_threshold: % máximo tolerado em PRODUÇÃO
        """
        self.window_size = window_size
        self.validation_threshold = validation_mode_threshold
        self.production_threshold = production_mode_threshold

        self.cpu_history: List[float] = []  # Histórico de CPU average
        self.spike_history: List[bool] = []  # Se foi pico ou sustentado

        # Detectar contexto
        self.is_validation_mode = os.getenv("OMNIMIND_VALIDATION_MODE", "false").lower() == "true"

    def get_metrics(self, interval: float = 0.1) -> CPUMetrics:
        """
        Obter métricas unificadas de CPU com contexto.

        Args:
            interval: Tempo (s) para medir CPU (padrão psutil: 0.1s)

        Returns:
            CPUMetrics com diagnóstico
        """
        # Medir CPU global
        cpu_percent_global = psutil.cpu_percent(interval=interval)

        # Medir por core
        cpu_per_core = psutil.cpu_percent(percpu=True, interval=interval)

        # Manter histórico
        self.cpu_history.append(cpu_percent_global)
        if len(self.cpu_history) > self.window_size:
            self.cpu_history.pop(0)

        # Detecção de contexto
        self._update_validation_mode()
        is_spike = self._detect_spike(cpu_percent_global)
        self.spike_history.append(is_spike)
        if len(self.spike_history) > self.window_size:
            self.spike_history.pop(0)

        # Análise de distribuição
        high_load_cores = sum(1 for c in cpu_per_core if c > 80.0)

        # Diagnóstico: realmente sobrecarregado?
        threshold = (
            self.validation_threshold if self.is_validation_mode else self.production_threshold
        )
        is_overloaded, reason = self._diagnose_overload(
            cpu_percent_global, cpu_per_core, high_load_cores, is_spike, threshold
        )

        return CPUMetrics(
            average_percent=cpu_percent_global,
            max_core_percent=max(cpu_per_core),
            min_core_percent=min(cpu_per_core),
            per_core_percent=cpu_per_core,
            high_load_cores=high_load_cores,
            is_validation_mode=self.is_validation_mode,
            is_spike=is_spike,
            is_overloaded=is_overloaded,
            reason=reason,
        )

    def _update_validation_mode(self) -> None:
        """Atualizar estado de VALIDATION_MODE"""
        self.is_validation_mode = os.getenv("OMNIMIND_VALIDATION_MODE", "false").lower() == "true"

    def _detect_spike(self, current_cpu: float) -> bool:
        """
        Detectar se é pico transiente ou sustentado.

        Pico: Aumento repentino que cai rapidamente
        Sustentado: Mantém acima do threshold por vários ciclos
        """
        if len(self.cpu_history) < 2:
            return False

        prev_cpu = self.cpu_history[-1]  # Penúltima medição

        # Pico: subiu >20% de uma vez E histórico mostra queda depois
        is_spike = current_cpu - prev_cpu > 20.0

        # Mas se estava alto e continua alto: não é pico
        if len(self.cpu_history) >= 3:
            trend = self.cpu_history[-2:] + [current_cpu]
            avg_recent = sum(trend) / len(trend)
            if avg_recent > 70.0:  # Sustentado alto
                is_spike = False

        return is_spike

    def _diagnose_overload(
        self,
        cpu_global: float,
        cpu_per_core: List[float],
        high_load_cores: int,
        is_spike: bool,
        threshold: float,
    ) -> tuple[bool, str]:
        """
        Diagnosticar se realmente está sobrecarregado.

        Critérios:
        1. CPU > threshold (considerando contexto)
        2. Sustentado (não é pico)
        3. Múltiplos cores carregados (não é um só core)
        """

        # Regra 1: Se é pico esperado, não é sobrecarga
        if is_spike:
            return False, f"Pico transiente detectado ({cpu_global:.1f}% é normal no novo ciclo)"

        # Regra 2: Se CPU abaixo do threshold, OK
        if cpu_global < threshold:
            return False, f"CPU normal ({cpu_global:.1f}% < {threshold}%)"

        # Regra 3: Se acima do threshold mas apenas 1-2 cores carregados = distribuição desigual
        if high_load_cores <= 2:
            return (
                False,
                f"Cores ocupados ({high_load_cores}) >80%, "
                f"outros livres - normal para cargas assincronas",
            )

        # Regra 4: Se acima do threshold E vários cores carregados = sobrecarga real
        if high_load_cores > 3 and cpu_global > threshold:
            return (
                True,
                f"Sobrecarga real: {high_load_cores} cores >80%, CPU média {cpu_global:.1f}%",
            )

        # Padrão
        return False, f"CPU elevada ({cpu_global:.1f}%) mas distribuída ou transitória"

    def log_metrics(self, metrics: CPUMetrics, prefix: str = "") -> None:
        """Registrar métricas de forma legível"""
        mode = "🔬 VALIDAÇÃO" if metrics.is_validation_mode else "📊 PRODUÇÃO"

        logger.info(f"{prefix} {mode}")
        logger.info(
            f"  Average: {metrics.average_percent:.1f}% | "
            f"Max core: {metrics.max_core_percent:.1f}% | "
            f"Min core: {metrics.min_core_percent:.1f}%"
        )
        logger.info(f"  Cores ocupados (>80%): {metrics.high_load_cores}/8")
        logger.info(f"  Distribuição: {', '.join(f'{c:.0f}%' for c in metrics.per_core_percent)}")

        if metrics.is_spike:
            logger.info("  ⚡ PICO detectado (transiente)")

        if metrics.is_overloaded:
            logger.warning(f"  🔴 SOBRECARGA: {metrics.reason}")
        else:
            logger.info(f"  ✅ OK: {metrics.reason}")

    def should_warn(self, metrics: CPUMetrics) -> bool:
        """
        Decidir se deve avisar.

        Returns:
            True se realmente sobrecarregado (não é pico esperado)
        """
        return metrics.is_overloaded and not metrics.is_spike


# Singleton global
_monitor = None


def get_cpu_monitor() -> UnifiedCPUMonitor:
    """Obter instância global do monitor"""
    global _monitor
    if _monitor is None:
        _monitor = UnifiedCPUMonitor()
    return _monitor
    return _monitor
