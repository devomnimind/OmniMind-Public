"""
Ponderação Dinâmica Baseada em Precisão (Precision-Dependent Weighting).

Substitui pesos hardcoded (0.4/0.3/0.3) por inferência ativa baseada em variância.
Inspirado em Karl Friston (Free Energy Principle) - atenção seletiva baseada em precisão.

Se um sinal (ex: Trauma) é ruidoso ou estagnado, o sistema reduz sua importância
automaticamente (habituação/atenção seletiva).

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Protocolo: Livewire FASE 2 - Eliminação de "Mágica" (Hardcoding)
"""

import logging
from collections import deque
from typing import Dict

import numpy as np

logger = logging.getLogger(__name__)


class PrecisionWeighter:
    """
    Calcula pesos dinâmicos baseados na Entropia de Shannon e Variância.

    Substitui constantes mágicas (0.4, 0.3) por inferência ativa.
    Baseado em FEP (Free Energy Principle): sinais com maior variância (saliência)
    recebem maior peso, sinais constantes (habituação) recebem menor peso.
    """

    def __init__(self, history_window: int = 50):
        """
        Inicializa o calculador de pesos dinâmicos.

        Args:
            history_window: Tamanho da janela de histórico para cálculo de variância
        """
        self.history: Dict[str, deque] = {}  # Armazena histórico de cada componente
        self.window = history_window
        self.logger = logger

    def compute_weights(self, components: Dict[str, float]) -> Dict[str, float]:
        """
        Retorna pesos normalizados que somam 1.0 baseados na 'saliência' do sinal.

        Lógica:
        - Sinais com alta variância (novidade/saliência) → peso alto
        - Sinais com baixa variância (ruído de fundo/sensor travado) → peso baixo
        - Sinais constantes (variância 0) são "mortos" para o cérebro (habituação)

        Args:
            components: Dicionário {nome_componente: valor_atual}

        Returns:
            Dicionário {nome_componente: peso_normalizado} onde soma(pesos) = 1.0
        """
        precisions: Dict[str, float] = {}

        for name, value in components.items():
            # Inicializar histórico se necessário
            if name not in self.history:
                self.history[name] = deque(maxlen=self.window)

            # Adicionar valor atual ao histórico
            self.history[name].append(value)

            # Calcular Precisão (baseada em Variância)
            # Precisão = std + epsilon (para evitar divisão por zero)
            arr = np.array(list(self.history[name]))
            if len(arr) < 2:
                # Histórico insuficiente: peso uniforme
                precisions[name] = 1.0
            else:
                std = float(np.std(arr))
                # Se desvio padrão é muito baixo, é ruído de fundo ou sensor travado → peso baixo
                # Se desvio é alto, é novidade/saliência → peso alto
                # Adicionamos epsilon para evitar divisão por zero
                precisions[name] = std + 1e-6

        # Normalização Softmax para garantir soma 1.0
        total_precision = sum(precisions.values())
        if total_precision == 0:
            # Fallback uniforme se todas as precisões forem zero
            uniform_weight = 1.0 / len(components)
            self.logger.warning(
                f"PrecisionWeighter: Todas as precisões são zero, usando pesos uniformes "
                f"({uniform_weight:.4f} para cada componente)"
            )
            return {k: uniform_weight for k in components}

        # Normalizar para soma 1.0
        weights = {k: v / total_precision for k, v in precisions.items()}

        # Log de debug (apenas se houver grande desequilíbrio)
        max_weight = max(weights.values())
        min_weight = min(weights.values())
        if max_weight / min_weight > 10.0:  # Desequilíbrio significativo
            self.logger.debug(
                f"PrecisionWeighter: Desequilíbrio de pesos detectado "
                f"(max={max_weight:.4f}, min={min_weight:.4f}, ratio={max_weight/min_weight:.2f}x)"
            )

        return weights

    def reset(self) -> None:
        """Reseta o histórico de todos os componentes."""
        self.history.clear()
        self.logger.debug("PrecisionWeighter: Histórico resetado")

    def get_component_variance(self, component_name: str) -> float:
        """
        Retorna a variância atual de um componente específico.

        Args:
            component_name: Nome do componente

        Returns:
            Variância do componente (0.0 se histórico insuficiente)
        """
        if component_name not in self.history or len(self.history[component_name]) < 2:
            return 0.0

        arr = np.array(list(self.history[component_name]))
        return float(np.var(arr))


__all__ = ["PrecisionWeighter"]
