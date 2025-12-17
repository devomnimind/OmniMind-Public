"""
Embedding Narrative - Narrativa representada como embeddings + estrutura.

Não reconstrói texto (Vec2Text é lossy). Trabalha diretamente com embeddings como
"narrativa digital", extraindo assinatura semântica, goal e actions como padrões numéricos.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
Baseado em: REDESENHO_RADICAL_EMBEDDINGS.py
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np

from src.consciousness.extended_cycle_result import ExtendedLoopCycleResult

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingNarrative:
    """
    Narrativa representada como embeddings + estrutura extraída.

    Não contém texto reconstruído. Trabalha diretamente com embeddings como
    "narrativa digital", extraindo propriedades estruturais e padrões semânticos.

    Campos:
    - module_embeddings: Embeddings brutos de cada módulo
    - module_activations: Ativações normalizadas
    - semantic_signature: Propriedades estruturais (magnitude, entropy, sparsity)
    - goal_inference: Goal como padrão numérico (divergence expectation-realidade)
    - action_pattern: Actions como padrão de ativação (top modules, sincronização)
    - embedding_history: Histórico de embeddings (últimos N ciclos)
    """

    # Dados brutos
    module_embeddings: Dict[str, np.ndarray]
    module_activations: Dict[str, float]

    # Estrutura extraída (SEM decodificação de texto)
    semantic_signature: Dict[str, float]  # Propriedades dos embeddings
    goal_inference: Dict[str, Any]  # Goal como padrão numérico
    action_pattern: Dict[str, Any]  # Ações como padrão de ativação

    # Histórico
    embedding_history: List[Dict[str, np.ndarray]]  # Últimos N ciclos

    # Metadata
    cycle_index: int
    raw_data: ExtendedLoopCycleResult  # Link para dados brutos

    def to_numeric_representation(self) -> np.ndarray:
        """
        Converte narrativa para vetor único para cálculo de Ψ.

        Concatena:
        1. Embedding médio dos módulos
        2. Signature semântica (valores)
        3. Goal inference (valores numéricos)
        4. Action pattern (valores numéricos)

        Returns:
            np.ndarray com representação numérica completa
        """
        # Parte 1: Embedding médio
        embeddings_list = list(self.module_embeddings.values())
        if embeddings_list:
            mean_embedding = np.mean(embeddings_list, axis=0)
        else:
            mean_embedding = np.array([])

        # Parte 2: Signature semântica
        signature_values = np.array(list(self.semantic_signature.values()))

        # Parte 3: Goal inference (valores numéricos)
        goal_values = []
        if isinstance(self.goal_inference, dict):
            # Extrai valores numéricos do goal_inference
            for key, value in self.goal_inference.items():
                if isinstance(value, (int, float)):
                    goal_values.append(float(value))
                elif isinstance(value, str) and value in [
                    "exploration",
                    "validation",
                    "uncertain",
                ]:
                    # Mapeia strings para números
                    mapping = {"exploration": 1.0, "validation": 0.0, "uncertain": 0.5}
                    goal_values.append(mapping.get(value, 0.5))
        goal_array = np.array(goal_values) if goal_values else np.array([])

        # Parte 4: Action pattern (valores numéricos)
        action_values = []
        if isinstance(self.action_pattern, dict):
            # Número de módulos ativos (normalizado)
            top_modules = self.action_pattern.get("top_active_modules", [])
            action_values.append(len(top_modules) / 5.0)  # Normaliza

            # Sincronização
            sync = self.action_pattern.get("module_synchronization", 0.5)
            action_values.append(float(sync))

            # Intensidade máxima
            intensities = self.action_pattern.get("activation_intensities", {})
            if intensities:
                max_intensity = max(intensities.values())
                action_values.append(float(max_intensity))
            else:
                action_values.append(0.0)
        action_array = np.array(action_values) if action_values else np.array([])

        # Concatena tudo
        features = np.concatenate(
            [
                mean_embedding,
                signature_values,
                goal_array,
                action_array,
            ]
        )

        return features


class EmbeddingNarrativeAnalyzer:
    """
    Analisa embeddings como narrativa sem reconstruir texto.

    Estratégia: embeddings SÃO a narrativa (comprimida).
    Extrai estrutura semântica, infere goal e actions como padrões numéricos.
    """

    def __init__(self):
        """Inicializa analyzer."""
        self.logger = logger

    async def analyze_cycle(
        self,
        cycle_result: ExtendedLoopCycleResult,
        previous_cycles: Optional[List[ExtendedLoopCycleResult]] = None,
    ) -> EmbeddingNarrative:
        """
        Analisa ciclo e extrai narrativa de embeddings.

        Args:
            cycle_result: Resultado do ciclo atual
            previous_cycles: Ciclos anteriores (para histórico)

        Returns:
            EmbeddingNarrative com estrutura extraída
        """
        if cycle_result.module_outputs is None or cycle_result.module_activations is None:
            raise ValueError("ExtendedLoopCycleResult deve ter module_outputs e module_activations")

        # 1. Extrair assinatura semântica
        semantic_signature = self._extract_semantic_signature(cycle_result.module_outputs)

        # 2. Inferir goal (numérico)
        goal_inference = await self._infer_goal_numeric(cycle_result)

        # 3. Extrair padrão de ações
        action_pattern = self._extract_action_pattern(cycle_result.module_activations)

        # 4. Construir histórico de embeddings
        embedding_history = []
        if previous_cycles:
            for prev_cycle in previous_cycles[-5:]:  # Últimos 5 ciclos
                # Verifica None explicitamente (não compara dict diretamente)
                if prev_cycle.module_outputs is not None:
                    embedding_history.append(prev_cycle.module_outputs)

        return EmbeddingNarrative(
            module_embeddings=cycle_result.module_outputs,
            module_activations=cycle_result.module_activations,
            semantic_signature=semantic_signature,
            goal_inference=goal_inference,
            action_pattern=action_pattern,
            embedding_history=embedding_history,
            cycle_index=cycle_result.cycle_number,
            raw_data=cycle_result,
        )

    def _extract_semantic_signature(
        self, module_outputs: Dict[str, np.ndarray]
    ) -> Dict[str, float]:
        """
        Extrai assinatura semântica dos embeddings.

        Não tenta decodificar para texto! Analisa a ESTRUTURA.

        Args:
            module_outputs: Embeddings dos módulos

        Returns:
            Dict com propriedades estruturais de cada módulo
        """
        signature = {}

        for module_name, embedding in module_outputs.items():
            # Propriedades estruturais (sem decodificação)
            signature[f"{module_name}_magnitude"] = float(np.linalg.norm(embedding))
            signature[f"{module_name}_entropy"] = self._calculate_entropy(embedding)
            signature[f"{module_name}_sparsity"] = float(np.sum(embedding == 0) / len(embedding))
            signature[f"{module_name}_mean"] = float(np.mean(embedding))
            signature[f"{module_name}_std"] = float(np.std(embedding))
            signature[f"{module_name}_max_activation"] = float(np.max(np.abs(embedding)))

        return signature

    async def _infer_goal_numeric(self, cycle_result: ExtendedLoopCycleResult) -> Dict[str, Any]:
        """
        Infere goal como padrão numérico, não texto.

        Args:
            cycle_result: Resultado do ciclo

        Returns:
            Dict com goal inferido (divergence, mode, scores)
        """
        if cycle_result.module_outputs is None:
            return {"mode": "unknown", "divergence": 0.0}

        expectation = cycle_result.module_outputs.get("expectation")
        sensory_input = cycle_result.module_outputs.get("sensory_input")
        # Não usar 'or' com arrays numpy! Usar verificação explícita de None
        meaning = cycle_result.module_outputs.get("meaning_maker")
        if meaning is None:
            meaning = cycle_result.module_outputs.get("meaning")

        # Verifica None explicitamente (não compara arrays)
        if expectation is None or sensory_input is None:
            return {"mode": "unknown", "divergence": 0.0}

        # Garante que são arrays numpy
        if not isinstance(expectation, np.ndarray):
            expectation = np.array(expectation)
        if not isinstance(sensory_input, np.ndarray):
            sensory_input = np.array(sensory_input)

        # 1. Divergência básica (L2 norm)
        divergence = np.linalg.norm(expectation - sensory_input)
        max_norm = max(np.linalg.norm(expectation), np.linalg.norm(sensory_input))
        # CORREÇÃO: Normalização que garante [0, 1]
        # Usar min para garantir que não exceda 1.0
        # A divergência pode ser maior que max_norm (triângulo desigualdade reversa)
        normalized_divergence = min(1.0, divergence / (max_norm + 1e-10))
        norm_div_float = float(normalized_divergence)  # type: ignore[arg-type]

        # 2. Interpretação
        if norm_div_float > 0.6:
            mode = "exploration"
        elif norm_div_float < 0.3:
            mode = "validation"
        else:
            mode = "uncertain"

        # 3. Contexto de meaning (confiança)
        meaning_confidence = 0.5
        if meaning is not None:
            # Garante que é array numpy
            if not isinstance(meaning, np.ndarray):
                meaning = np.array(meaning)
            meaning_entropy = self._calculate_entropy(meaning)
            meaning_confidence = 1.0 - min(1.0, meaning_entropy / 10.0)  # Normaliza

        return {
            "divergence": norm_div_float,
            "mode": mode,
            "exploration_score": min(1.0, norm_div_float),
            "validation_score": 1.0 - min(1.0, norm_div_float),
            "meaning_confidence": float(meaning_confidence),
        }

    def _extract_action_pattern(self, module_activations: Dict[str, float]) -> Dict[str, Any]:
        """
        Extrai padrão de ações a partir de ativações.

        Args:
            module_activations: Ativações dos módulos

        Returns:
            Dict com padrão de ações (top modules, sincronização, etc)
        """
        # Quais módulos estão mais ativos?
        sorted_modules = sorted(module_activations.items(), key=lambda x: x[1], reverse=True)

        # Top 3 módulos
        top_modules = [name for name, _ in sorted_modules[:3]]

        # Intensidade (quanto diferente de baseline 0.5?)
        intensities = {
            name: abs(activation - 0.5) * 2 for name, activation in module_activations.items()
        }

        # Sincronização (quanto os módulos trabalham juntos?)
        activations_list = list(module_activations.values())
        sync_score = 1.0 - float(np.std(activations_list))  # 0-1 (alto std = baixa sync)

        return {
            "top_active_modules": top_modules,
            "activation_intensities": intensities,
            "module_synchronization": float(np.clip(sync_score, 0.0, 1.0)),
            "dominant_module": sorted_modules[0][0] if sorted_modules else None,
        }

    def _calculate_entropy(self, embedding: np.ndarray) -> float:
        """
        Calcula entropia de Shannon do embedding.

        Args:
            embedding: Vetor de embedding

        Returns:
            float com entropia
        """
        # Normaliza para [0, 1]
        min_val = embedding.min()
        max_val = embedding.max()
        if max_val - min_val < 1e-10:
            return 0.0

        normalized = (embedding - min_val) / (max_val - min_val + 1e-10)

        # Shannon entropy
        # Evita log(0)
        normalized = np.clip(normalized, 1e-10, 1.0)
        entropy = -np.sum(normalized * np.log(normalized))

        return float(entropy)
