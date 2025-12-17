"""
Cycle History - Armazena e acessa histórico de ciclos com getters seguros.

Fornece API imutável para acessar outputs de ciclos anteriores.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: decisões arquiteturais aprovadas
"""

import logging
from typing import Dict, List, Optional

import numpy as np

from src.consciousness.extended_cycle_result import ExtendedLoopCycleResult

logger = logging.getLogger(__name__)


class CycleHistory:
    """
    Armazena histórico de ciclos com acesso seguro e imutável.

    Fornece API para:
    - get_module_output(cycle_index, module_id) -> output or None
    - get_cycle_metrics(cycle_index) -> ExtendedLoopCycleResult-like dict
    - get_phi_history() -> List[float]
    """

    def __init__(self, max_history_size: int = 1000):
        """
        Inicializa histórico.

        Args:
            max_history_size: Tamanho máximo do histórico
        """
        self.max_history_size = max_history_size
        self.history: List[ExtendedLoopCycleResult] = []
        self.logger = logger

    def add_cycle(self, cycle_result: ExtendedLoopCycleResult) -> None:
        """
        Adiciona ciclo ao histórico.

        Args:
            cycle_result: Resultado do ciclo (cópia defensiva será feita)
        """
        # Cria cópia defensiva dos dados críticos
        copied_result = self._create_defensive_copy(cycle_result)
        self.history.append(copied_result)

        # Remove ciclos antigos se exceder tamanho máximo
        if len(self.history) > self.max_history_size:
            self.history.pop(0)

    def get_module_output(self, cycle_index: int, module_id: str) -> Optional[np.ndarray]:
        """
        Obtém output de um módulo em um ciclo específico.

        Args:
            cycle_index: Índice do ciclo (0 = mais antigo, -1 = mais recente)
            module_id: ID do módulo

        Returns:
            np.ndarray com output do módulo, ou None se não encontrado
        """
        try:
            cycle = self._get_cycle(cycle_index)
            if cycle and cycle.module_outputs:
                output = cycle.module_outputs.get(module_id)
                if output is not None:
                    return output.copy()  # Cópia defensiva
        except (IndexError, KeyError) as e:
            self.logger.debug(f"Erro ao obter module_output: {e}")

        return None

    def get_cycle_metrics(self, cycle_index: int) -> Optional[Dict]:
        """
        Obtém métricas completas de um ciclo.

        Args:
            cycle_index: Índice do ciclo

        Returns:
            Dict com métricas do ciclo, ou None se não encontrado
        """
        try:
            cycle = self._get_cycle(cycle_index)
            if cycle:
                return cycle.to_dict()
        except IndexError as e:
            self.logger.debug(f"Erro ao obter cycle_metrics: {e}")

        return None

    def get_phi_history(self, last_n: Optional[int] = None) -> List[float]:
        """
        Obtém histórico de Φ.

        Args:
            last_n: Número de últimos valores (None = todos)

        Returns:
            List[float] com valores de Φ
        """
        # CORREÇÃO (2025-12-08 20:30): NÃO filtrar valores zero - incluir todos para análise
        # Se filtrar, quando Phi está zerando, phi_history fica vazio e sigma usa fallback
        # Valores zero são válidos para análise de desintegração
        phi_values = [cycle.phi_estimate for cycle in self.history]

        if last_n is not None:
            return phi_values[-last_n:]

        return phi_values

    def get_previous_cycle(self, current_cycle_number: int) -> Optional[ExtendedLoopCycleResult]:
        """
        Obtém ciclo anterior ao ciclo atual.

        Args:
            current_cycle_number: Número do ciclo atual

        Returns:
            ExtendedLoopCycleResult do ciclo anterior, ou None
        """
        # Procura ciclo com cycle_number = current_cycle_number - 1
        for cycle in reversed(self.history):
            if cycle.cycle_number == current_cycle_number - 1:
                return self._create_defensive_copy(cycle)

        return None

    def get_recent_cycles(self, n: int = 5) -> List[ExtendedLoopCycleResult]:
        """
        Obtém últimos N ciclos.

        Args:
            n: Número de ciclos a retornar

        Returns:
            List[ExtendedLoopCycleResult] com últimos N ciclos (cópias defensivas)
        """
        recent = self.history[-n:] if len(self.history) >= n else self.history
        return [self._create_defensive_copy(cycle) for cycle in recent]

    def _get_cycle(self, cycle_index: int) -> Optional[ExtendedLoopCycleResult]:
        """
        Obtém ciclo por índice (com suporte a índices negativos).

        Args:
            cycle_index: Índice do ciclo (0 = mais antigo, -1 = mais recente)

        Returns:
            ExtendedLoopCycleResult ou None
        """
        if not self.history:
            return None

        try:
            return self.history[cycle_index]
        except IndexError:
            return None

    def _create_defensive_copy(self, cycle: ExtendedLoopCycleResult) -> ExtendedLoopCycleResult:
        """
        Cria cópia defensiva de ExtendedLoopCycleResult.

        Args:
            cycle: Ciclo a copiar

        Returns:
            ExtendedLoopCycleResult com cópias dos arrays
        """
        # Cria cópia dos module_outputs (arrays)
        module_outputs_copy = None
        if cycle.module_outputs:
            module_outputs_copy = {name: emb.copy() for name, emb in cycle.module_outputs.items()}

        # Outros campos são imutáveis ou já são cópias
        return ExtendedLoopCycleResult.from_base_result(
            base_result=cycle,  # LoopCycleResult é imutável
            module_outputs=module_outputs_copy,
            module_activations=(
                cycle.module_activations.copy() if cycle.module_activations else None
            ),
            integration_strength=cycle.integration_strength,
            temporal_signature=(
                cycle.temporal_signature.copy() if cycle.temporal_signature else None
            ),
            psi=cycle.psi,
            sigma=cycle.sigma,
            triad=cycle.triad,  # ConsciousnessTriad é imutável
            cycle_id=cycle.cycle_id,
        )

    def clear(self) -> None:
        """Limpa histórico."""
        self.history.clear()

    def size(self) -> int:
        """Retorna tamanho do histórico."""
        return len(self.history)
