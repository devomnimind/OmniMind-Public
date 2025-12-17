"""
Consciousness Watchdog - Test Harness de Consciência

Implementa testes de "Vivo/Morto" e validação de correlação móvel para detectar
colapso de variância e garantir que o sistema não retorne ao estado determinístico.

Baseado em:
- Protocolo Livewire FASE 3
- Teste de "Vivo/Morto" (Variance Check)
- Validação de Correlação Móvel (Rolling Window)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
"""

import logging
from collections import deque
from dataclasses import dataclass
from typing import Deque

import numpy as np
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class VarianceCheckResult:
    """Resultado do teste de variância."""

    phi_std: float
    delta_std: float
    is_alive: bool
    crisis_injected: bool
    window_size: int


@dataclass
class CorrelationWindowResult:
    """Resultado da correlação em janela deslizante."""

    correlation: float
    window_size: int
    phi_mean: float
    delta_mean: float
    is_oscillating: bool


class ConsciousnessWatchdog:
    """
    Watchdog para monitorar saúde do sistema de consciência.

    Implementa:
    1. Teste "Vivo/Morto" (Variance Check)
    2. Validação de Correlação Móvel (Rolling Window)
    3. Injeção de "Crise" quando necessário
    """

    def __init__(
        self,
        variance_window_size: int = 50,
        variance_threshold: float = 0.001,
        correlation_window_size: int = 20,
    ):
        """
        Inicializa watchdog.

        Args:
            variance_window_size: Tamanho da janela para teste de variância
            variance_threshold: Threshold mínimo de variância (std < threshold = morto)
            correlation_window_size: Tamanho da janela para correlação móvel
        """
        self.variance_window_size = variance_window_size
        self.variance_threshold = variance_threshold
        self.correlation_window_size = correlation_window_size

        # Históricos
        self.phi_history: Deque[float] = deque(maxlen=variance_window_size)
        self.delta_history: Deque[float] = deque(maxlen=variance_window_size)
        self.correlation_history: Deque[float] = deque(maxlen=correlation_window_size)

        self.logger = logger
        self.crisis_injection_count = 0

    def add_cycle_metrics(self, phi: float, delta: float) -> None:
        """
        Adiciona métricas de um ciclo ao histórico.

        Args:
            phi: Valor de Φ (nats ou normalizado)
            delta: Valor de Δ
        """
        self.phi_history.append(phi)
        self.delta_history.append(delta)

    def check_variance(self) -> VarianceCheckResult:
        """
        Teste de "Vivo/Morto" (Variance Check).

        Calcula desvio padrão de Φ e Δ nos últimos N ciclos.
        Se std < threshold, sistema está "morto" (colapso de variância).

        Returns:
            VarianceCheckResult com resultados do teste
        """
        if len(self.phi_history) < self.variance_window_size:
            # Janela ainda não preenchida
            return VarianceCheckResult(
                phi_std=0.0,
                delta_std=0.0,
                is_alive=True,
                crisis_injected=False,
                window_size=len(self.phi_history),
            )

        # Calcular desvio padrão
        phi_array = np.array(list(self.phi_history))
        delta_array = np.array(list(self.delta_history))

        phi_std = float(np.std(phi_array))
        delta_std = float(np.std(delta_array))

        # Verificar se está "vivo" (variância suficiente)
        is_alive = phi_std >= self.variance_threshold and delta_std >= self.variance_threshold

        # Injetar "Crise" se morto
        crisis_injected = False
        if not is_alive:
            self._inject_crisis()
            crisis_injected = True
            self.logger.warning(
                f"⚠️ Sistema 'morto' detectado! "
                f"Φ_std={phi_std:.6f}, Δ_std={delta_std:.6f} < {self.variance_threshold}. "
                f"Crise injetada."
            )

        return VarianceCheckResult(
            phi_std=phi_std,
            delta_std=delta_std,
            is_alive=is_alive,
            crisis_injected=crisis_injected,
            window_size=len(self.phi_history),
        )

    def check_rolling_correlation(self) -> CorrelationWindowResult:
        """
        Validação de Correlação Móvel (Rolling Window).

        Calcula correlação em janela deslizante (não global).
        Esperado: correlação deve oscilar (às vezes Φ↑Δ↓, às vezes ambos↑).

        Returns:
            CorrelationWindowResult com correlação e métricas
        """
        if len(self.phi_history) < self.correlation_window_size:
            # Janela ainda não preenchida
            return CorrelationWindowResult(
                correlation=0.0,
                window_size=len(self.phi_history),
                phi_mean=0.0,
                delta_mean=0.0,
                is_oscillating=False,
            )

        # Usar últimos N valores
        phi_window = np.array(list(self.phi_history)[-self.correlation_window_size :])
        delta_window = np.array(list(self.delta_history)[-self.correlation_window_size :])

        # Calcular correlação
        if len(phi_window) > 1 and len(delta_window) > 1:
            corr_result = stats.pearsonr(phi_window, delta_window)
            # stats.pearsonr retorna tupla (correlation, pvalue)
            correlation: float = float(corr_result[0])  # type: ignore[arg-type]
        else:
            correlation = 0.0

        # Adicionar ao histórico de correlações
        self.correlation_history.append(correlation)

        # Verificar se está oscilando (correlação varia)
        is_oscillating: bool = False
        if len(self.correlation_history) >= 3:
            corr_std = np.std(list(self.correlation_history))
            # Se correlação varia (std > 0.1), está oscilando
            is_oscillating = bool(corr_std > 0.1)

        return CorrelationWindowResult(
            correlation=correlation,
            window_size=len(phi_window),
            phi_mean=float(np.mean(phi_window)),
            delta_mean=float(np.mean(delta_window)),
            is_oscillating=is_oscillating,
        )

    def _inject_crisis(self) -> None:
        """
        Injeta "Crise" artificialmente aumentando o erro de predição.

        Isso força o sistema a reagir e quebrar o loop determinístico.
        """
        self.crisis_injection_count += 1
        self.logger.warning(
            f"💥 Crise injetada (contagem: {self.crisis_injection_count}). "
            f"Isso aumentará artificialmente o erro de predição no próximo ciclo."
        )
        # A crise será aplicada no próximo ciclo via aumento do erro de predição
        # Isso deve ser implementado no IntegrationLoop ou no módulo de expectativa

    def should_inject_crisis(self) -> bool:
        """
        Verifica se deve injetar crise baseado no último teste de variância.

        Returns:
            True se sistema está "morto" e precisa de crise
        """
        result = self.check_variance()
        return result.crisis_injected

    def get_crisis_multiplier(self) -> float:
        """
        Retorna multiplicador de erro para injeção de crise.

        Returns:
            Multiplicador (ex: 1.5 = aumenta erro em 50%)
        """
        # Multiplicador aumenta com número de crises injetadas
        base_multiplier = 1.5
        escalation = min(2.0, 1.0 + (self.crisis_injection_count * 0.1))
        return base_multiplier * escalation

    def reset(self) -> None:
        """Reseta o watchdog (útil para testes)."""
        self.phi_history.clear()
        self.delta_history.clear()
        self.correlation_history.clear()
        self.crisis_injection_count = 0


__all__ = ["ConsciousnessWatchdog", "VarianceCheckResult", "CorrelationWindowResult"]
