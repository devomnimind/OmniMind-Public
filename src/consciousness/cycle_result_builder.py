"""
Loop Cycle Result Builder - Constrói ExtendedLoopCycleResult a partir de SharedWorkspace.

Extrai embeddings, calcula ativações, integração e assinatura temporal.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: REDESENHO_RADICAL_EMBEDDINGS.py
"""

import logging
from typing import Dict, List, Optional

import numpy as np

from src.consciousness.extended_cycle_result import ExtendedLoopCycleResult
from src.consciousness.integration_loop import LoopCycleResult
from src.consciousness.shared_workspace import SharedWorkspace

logger = logging.getLogger(__name__)


class LoopCycleResultBuilder:
    """
    Constrói ExtendedLoopCycleResult a partir de SharedWorkspace.

    Extrai:
    - module_outputs: embeddings do workspace
    - module_activations: magnitude normalizada dos embeddings
    - integration_strength: correlação média entre embeddings
    - temporal_signature: sequência de ativações + deltas
    """

    def __init__(self, workspace: SharedWorkspace):
        """
        Inicializa builder.

        Args:
            workspace: SharedWorkspace para extrair dados
        """
        self.workspace = workspace

    def build_from_workspace(
        self,
        base_result: LoopCycleResult,
        previous_cycle: Optional[ExtendedLoopCycleResult] = None,
    ) -> ExtendedLoopCycleResult:
        """
        Constrói ExtendedLoopCycleResult a partir de workspace e ciclo anterior.

        Args:
            base_result: LoopCycleResult base (já calculado)
            previous_cycle: Ciclo anterior (para calcular deltas)

        Returns:
            ExtendedLoopCycleResult com todos os campos estendidos
        """
        # 1. Extrair embeddings como module_outputs
        module_outputs = self._extract_embeddings()

        # 2. Calcular module_activations
        module_activations = self._calculate_activations(module_outputs, previous_cycle)

        # 3. Calcular integration strength
        integration_strength = self._calculate_integration(module_outputs)

        # 4. Construir temporal_signature
        temporal_signature = self._build_temporal_signature(module_activations, previous_cycle)

        # 5. Gerar cycle_id
        cycle_id = f"cycle_{base_result.cycle_number}_{int(base_result.timestamp.timestamp())}"

        return ExtendedLoopCycleResult.from_base_result(
            base_result=base_result,
            module_outputs=module_outputs,
            module_activations=module_activations,
            integration_strength=integration_strength,
            temporal_signature=temporal_signature,
            cycle_id=cycle_id,
        )

    def _extract_embeddings(self) -> Dict[str, np.ndarray]:
        """
        Extrai embeddings da workspace e normaliza dimensões.

        Returns:
            Dict[str, np.ndarray] com embeddings de cada módulo (todas com dimensão normalizada)
        """
        normalized_embeddings = {}
        for module_name, embedding in self.workspace.embeddings.items():
            # Normaliza dimensão automáticamente
            normalized = self.workspace._normalize_embedding_dimension(embedding, module_name)
            normalized_embeddings[module_name] = normalized
        return normalized_embeddings

    def _calculate_activations(
        self,
        module_outputs: Dict[str, np.ndarray],
        previous_cycle: Optional[ExtendedLoopCycleResult] = None,
    ) -> Dict[str, float]:
        """
        Calcula ativação de cada módulo.

        Estratégia: Magnitude normalizada + mudança temporal.
        activation = 0.6 * magnitude_normalized + 0.4 * delta_normalized

        Args:
            module_outputs: Embeddings dos módulos
            previous_cycle: Ciclo anterior (para calcular deltas)

        Returns:
            Dict[str, float] com ativações [0, 1]
        """
        activations = {}

        # Calcula magnitudes
        magnitudes = {name: np.linalg.norm(emb) for name, emb in module_outputs.items()}
        max_magnitude = max(magnitudes.values()) if magnitudes else 1.0

        # Calcula ativações baseadas em magnitude
        for name, magnitude in magnitudes.items():
            # Componente 1: Magnitude normalizada
            magnitude_normalized: float = float(
                min(1.0, magnitude / max_magnitude if max_magnitude > 0 else 0.5)
            )

            # Componente 2: Mudança temporal (delta)
            if previous_cycle is not None and previous_cycle.module_outputs is not None:
                prev_embedding = previous_cycle.module_outputs.get(name)
                if prev_embedding is not None:
                    # Garante que são arrays numpy
                    current_emb = module_outputs[name]
                    if not isinstance(current_emb, np.ndarray):
                        current_emb = np.array(current_emb)
                    if not isinstance(prev_embedding, np.ndarray):
                        prev_embedding = np.array(prev_embedding)

                    # Garante mesma dimensão
                    current_emb = current_emb.flatten()
                    prev_embedding = prev_embedding.flatten()

                    if current_emb.shape[0] != prev_embedding.shape[0]:
                        min_dim = min(current_emb.shape[0], prev_embedding.shape[0])
                        current_emb = current_emb[:min_dim]
                        prev_embedding = prev_embedding[:min_dim]

                    delta = np.linalg.norm(current_emb - prev_embedding)
                    # Normaliza delta (threshold adaptável)
                    delta_normalized: float = min(
                        1.0, float(delta) / 1.0
                    )  # Ajustar threshold se necessário
                else:
                    delta_normalized = 0.5  # Sem histórico anterior
            else:
                delta_normalized = 0.5  # Primeiro ciclo

            # Combinação (weighted)
            activation: float = 0.6 * magnitude_normalized + 0.4 * delta_normalized
            activations[name] = activation

        return activations

    def _calculate_integration(self, module_outputs: Dict[str, np.ndarray]) -> float:
        """
        Calcula força de integração entre módulos.

        Estratégia: correlação média (cosine similarity) entre embeddings.

        Args:
            module_outputs: Embeddings dos módulos

        Returns:
            float [0, 1] representando força de integração
        """
        embeddings_list = list(module_outputs.values())

        if len(embeddings_list) < 2:
            return 0.5  # Sem módulos suficientes

        # Calcular correlações pairwise
        correlations = []
        for i in range(len(embeddings_list)):
            for j in range(i + 1, len(embeddings_list)):
                sim = self._cosine_similarity(embeddings_list[i], embeddings_list[j])
                correlations.append(sim)

        # Média das correlações
        integration = np.mean(correlations) if correlations else 0.5

        # Normaliza para [0, 1] (cosine similarity está em [-1, 1])
        integration = (integration + 1.0) / 2.0

        return float(integration)

    def _build_temporal_signature(
        self,
        module_activations: Dict[str, float],
        previous_cycle: Optional[ExtendedLoopCycleResult] = None,
    ) -> List[float]:
        """
        Constrói assinatura temporal para cálculo de LZ.

        Estratégia: concatenar ativações atuais + deltas + acelerações.

        Args:
            module_activations: Ativações atuais
            previous_cycle: Ciclo anterior (para deltas)

        Returns:
            List[float] com assinatura temporal completa
        """
        current_sig = list(module_activations.values())

        if previous_cycle and previous_cycle.module_activations:
            # Parte 1: Ativações atuais
            signature = current_sig.copy()

            # Parte 2: Deltas (mudança vs ciclo anterior)
            prev_sig = list(previous_cycle.module_activations.values())
            # Garante mesma ordem
            if len(prev_sig) == len(current_sig):
                deltas = [c - p for c, p in zip(current_sig, prev_sig)]
                signature.extend(deltas)
            else:
                # Ordem diferente ou módulos diferentes - apenas valores atuais
                logger.warning(
                    f"Mismatch em número de módulos: {len(current_sig)} vs {len(prev_sig)}"
                )

            return signature
        else:
            # Primeiro ciclo - apenas valores atuais
            return current_sig

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """
        Calcula cosine similarity entre dois vetores.

        Garante que ambos são arrays numpy e possuem mesma dimensão.

        Args:
            a: Vetor 1
            b: Vetor 2

        Returns:
            float [-1, 1] representando similaridade
        """
        # Garantir que são arrays numpy
        if not isinstance(a, np.ndarray):
            a = np.array(a)
        if not isinstance(b, np.ndarray):
            b = np.array(b)

        # Garantir que são 1D
        a = a.flatten()
        b = b.flatten()

        # Se diferentes dimensões, truncar para a menor (ou padding)
        if a.shape[0] != b.shape[0]:
            min_dim = min(a.shape[0], b.shape[0])
            a = a[:min_dim]
            b = b[:min_dim]

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return float(np.dot(a, b) / (norm_a * norm_b))
