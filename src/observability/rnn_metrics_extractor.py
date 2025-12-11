"""
RNNMetricsExtractor - Captura de Métricas do RNN ConsciousSystem

Implementa Task 2.3.1 do Sprint 2: Integração com RNN
Extrai métricas detalhadas dos pesos, ativações e gradientes do ConsciousSystem.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-11
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

import numpy as np
import torch

logger = logging.getLogger(__name__)


class RNNMetricsExtractor:
    """
    Extrator de métricas para RNN ConsciousSystem.

    Características:
    - Hook em ConsciousSystem após cada update
    - Extrai pesos (mean, variance, max, min)
    - Extrai ativações (% neurônios ativos)
    - Calcula gradientes (magnitude)
    - Registra mudanças por camada
    """

    def __init__(self, enable_metrics: bool = True):
        """
        Inicializa RNNMetricsExtractor.

        Args:
            enable_metrics: Se True, registra métricas via ModuleMetricsCollector
        """
        self.enable_metrics = enable_metrics
        self._previous_weights: Dict[str, torch.Tensor] = {}
        self._logger = logger.getChild(self.__class__.__name__)

        # Lazy import para evitar circular dependencies
        self._metrics_collector = None

        self._logger.info("RNNMetricsExtractor inicializado")

    def _get_metrics_collector(self) -> Any:
        """
        Obtém o ModuleMetricsCollector (lazy loading).

        Returns:
            ModuleMetricsCollector instance ou None se não disponível
        """
        if self._metrics_collector is None and self.enable_metrics:
            try:
                from src.observability.module_metrics import get_module_metrics

                self._metrics_collector = get_module_metrics()
                self._logger.debug("ModuleMetricsCollector carregado")
            except ImportError as e:
                self._logger.warning(f"ModuleMetricsCollector não disponível: {e}")

        return self._metrics_collector

    def extract_metrics(
        self,
        conscious_system: Any,
        cycle_id: Optional[int] = None,
        phi_value: Optional[float] = None,
    ) -> None:
        """
        Extrai métricas do ConsciousSystem após um step.

        Args:
            conscious_system: Instância do ConsciousSystem
            cycle_id: ID do ciclo de consciência (para correlação)
            phi_value: Valor de Φ do ciclo (para correlação)
        """
        if not self.enable_metrics:
            return

        metrics_collector = self._get_metrics_collector()
        if metrics_collector is None:
            return

        try:
            # Layers do RNN a serem rastreadas
            layers = {
                "W_PC": conscious_system.W_PC,  # Pré-consciente -> Consciente
                "W_UC": conscious_system.W_UC,  # Inconsciente -> Consciente
                "W_CP": conscious_system.W_CP,  # Consciente -> Pré-consciente
                "W_CU": conscious_system.W_CU,  # Consciente -> Inconsciente
            }

            # States (ativações)
            states = {
                "rho_C": conscious_system.rho_C,  # Consciente
                "rho_P": conscious_system.rho_P,  # Pré-consciente
                "rho_U": conscious_system.rho_U,  # Inconsciente
            }

            # Nome do módulo base
            module_name_base = "RNNConsciousSystem"
            if cycle_id is not None:
                module_name_base = f"{module_name_base}_cycle_{cycle_id}"

            labels = {}
            if cycle_id is not None:
                labels["cycle"] = cycle_id
            if phi_value is not None:
                labels["phi"] = f"{phi_value:.4f}"

            # Extrair métricas de pesos por camada
            for layer_name, weight_tensor in layers.items():
                self._extract_weight_metrics(
                    metrics_collector,
                    module_name_base,
                    layer_name,
                    weight_tensor,
                    labels,
                )

            # Extrair métricas de ativações
            for state_name, state_tensor in states.items():
                self._extract_activation_metrics(
                    metrics_collector,
                    module_name_base,
                    state_name,
                    state_tensor,
                    labels,
                )

            # Extrair métricas de repressão
            self._extract_repression_metrics(
                metrics_collector,
                module_name_base,
                conscious_system,
                labels,
            )

        except Exception as e:
            self._logger.debug(f"Falha ao extrair métricas RNN: {e}")

    def _extract_weight_metrics(
        self,
        metrics_collector: Any,
        module_name_base: str,
        layer_name: str,
        weight_tensor: torch.Tensor,
        labels: Dict[str, Any],
    ) -> None:
        """
        Extrai métricas de pesos de uma camada.

        Args:
            metrics_collector: ModuleMetricsCollector instance
            module_name_base: Nome base do módulo
            layer_name: Nome da camada (ex: "W_PC")
            weight_tensor: Tensor de pesos
            labels: Labels adicionais
        """
        # Converter para numpy para cálculos estatísticos
        weights_np = weight_tensor.detach().cpu().numpy()

        # Estatísticas básicas
        weight_mean = float(np.mean(weights_np))
        weight_variance = float(np.var(weights_np))
        weight_max = float(np.max(weights_np))
        weight_min = float(np.min(weights_np))
        weight_std = float(np.std(weights_np))

        # Labels específicos da camada
        layer_labels = labels.copy()
        layer_labels["layer"] = layer_name

        # Registrar métricas
        metrics_collector.record_metric(
            module_name=f"{module_name_base}_layer_{layer_name}",
            metric_name="weight_mean",
            value=weight_mean,
            labels=layer_labels,
        )

        metrics_collector.record_metric(
            module_name=f"{module_name_base}_layer_{layer_name}",
            metric_name="weight_variance",
            value=weight_variance,
            labels=layer_labels,
        )

        metrics_collector.record_metric(
            module_name=f"{module_name_base}_layer_{layer_name}",
            metric_name="weight_max",
            value=weight_max,
            labels=layer_labels,
        )

        metrics_collector.record_metric(
            module_name=f"{module_name_base}_layer_{layer_name}",
            metric_name="weight_min",
            value=weight_min,
            labels=layer_labels,
        )

        metrics_collector.record_metric(
            module_name=f"{module_name_base}_layer_{layer_name}",
            metric_name="weight_std",
            value=weight_std,
            labels=layer_labels,
        )

        # Calcular delta se temos pesos anteriores
        if layer_name in self._previous_weights:
            previous_weights = self._previous_weights[layer_name].detach().cpu().numpy()
            weight_delta = float(np.mean(np.abs(weights_np - previous_weights)))

            metrics_collector.record_metric(
                module_name=f"{module_name_base}_layer_{layer_name}",
                metric_name="weight_delta_per_epoch",
                value=weight_delta,
                labels=layer_labels,
            )

        # Calcular magnitude do gradiente (aproximação via mudança de peso)
        if layer_name in self._previous_weights:
            gradient_magnitude = float(
                np.linalg.norm(
                    weights_np - self._previous_weights[layer_name].detach().cpu().numpy()
                )
            )

            metrics_collector.record_metric(
                module_name=f"{module_name_base}_layer_{layer_name}",
                metric_name="gradient_magnitude",
                value=gradient_magnitude,
                labels=layer_labels,
            )

            # Direção do gradiente (positivo vs negativo dominante)
            weight_diff = weights_np - self._previous_weights[layer_name].detach().cpu().numpy()
            gradient_direction = float(np.sign(np.mean(weight_diff)))

            metrics_collector.record_metric(
                module_name=f"{module_name_base}_layer_{layer_name}",
                metric_name="gradient_direction",
                value=gradient_direction,
                labels=layer_labels,
            )

        # Armazenar pesos atuais para próxima iteração
        self._previous_weights[layer_name] = weight_tensor.clone()

    def _extract_activation_metrics(
        self,
        metrics_collector: Any,
        module_name_base: str,
        state_name: str,
        state_tensor: torch.Tensor,
        labels: Dict[str, Any],
    ) -> None:
        """
        Extrai métricas de ativações de um estado.

        Args:
            metrics_collector: ModuleMetricsCollector instance
            module_name_base: Nome base do módulo
            state_name: Nome do estado (ex: "rho_C")
            state_tensor: Tensor de estado
            labels: Labels adicionais
        """
        # Converter para numpy
        state_np = state_tensor.detach().cpu().numpy()

        # Calcular taxa de ativação (% de neurônios "ativos")
        # Consideramos ativo se |valor| > threshold
        activation_threshold = 0.1
        active_neurons = np.sum(np.abs(state_np) > activation_threshold)
        total_neurons = state_np.size
        activation_rate = float(active_neurons / total_neurons) if total_neurons > 0 else 0.0

        # Labels específicos do estado
        state_labels = labels.copy()
        state_labels["state"] = state_name

        # Registrar taxa de ativação
        metrics_collector.record_metric(
            module_name=f"{module_name_base}_state_{state_name}",
            metric_name="activation_rate",
            value=activation_rate,
            labels=state_labels,
        )

        # Registrar magnitude do estado
        state_magnitude = float(np.linalg.norm(state_np))
        metrics_collector.record_metric(
            module_name=f"{module_name_base}_state_{state_name}",
            metric_name="state_magnitude",
            value=state_magnitude,
            labels=state_labels,
        )

        # Estatísticas do estado
        state_mean = float(np.mean(state_np))
        state_std = float(np.std(state_np))

        metrics_collector.record_metric(
            module_name=f"{module_name_base}_state_{state_name}",
            metric_name="state_mean",
            value=state_mean,
            labels=state_labels,
        )

        metrics_collector.record_metric(
            module_name=f"{module_name_base}_state_{state_name}",
            metric_name="state_std",
            value=state_std,
            labels=state_labels,
        )

    def _extract_repression_metrics(
        self,
        metrics_collector: Any,
        module_name_base: str,
        conscious_system: Any,
        labels: Dict[str, Any],
    ) -> None:
        """
        Extrai métricas de repressão do sistema.

        Args:
            metrics_collector: ModuleMetricsCollector instance
            module_name_base: Nome base do módulo
            conscious_system: Instância do ConsciousSystem
            labels: Labels adicionais
        """
        # Força de repressão
        repression_strength = float(conscious_system.repression_strength)

        metrics_collector.record_metric(
            module_name=f"{module_name_base}_system",
            metric_name="repression_strength",
            value=repression_strength,
            labels=labels,
        )


# Singleton global
_rnn_metrics_extractor: Optional[RNNMetricsExtractor] = None


def get_rnn_metrics_extractor() -> RNNMetricsExtractor:
    """
    Obtém a instância singleton do RNNMetricsExtractor.

    Returns:
        RNNMetricsExtractor instance
    """
    global _rnn_metrics_extractor
    if _rnn_metrics_extractor is None:
        _rnn_metrics_extractor = RNNMetricsExtractor()
    return _rnn_metrics_extractor
