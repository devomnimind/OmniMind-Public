"""
Freudian Topographical Memory Structure
Estrutura Tópica Freudiana: Consciente - Pré-Consciente - Inconsciente

Baseado na Primeira Tópica de Freud:
1. CONSCIENTE: Acessível diretamente (memória ativa na GPU)
2. PRÉ-CONSCIENTE: Não acessível no momento, mas pode ser trazido à consciência facilmente
   - Memórias não traumáticas
   - Comprimidas mas não criptografadas
   - Acessíveis ao Ego quando necessário
3. INCONSCIENTE: Reprimido, criptografado, inacessível ao Ego
   - Memórias traumáticas
   - Criptografadas (EncryptedUnconsciousLayer)
   - Influenciam decisões mas não são acessíveis diretamente

Classificação:
- Traumático (erro crítico, OOM, falha estrutural) → INCONSCIENTE
- Não traumático (consolidação normal, memória antiga) → PRÉ-CONSCIENTE
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import numpy as np

from ..consciousness.dynamic_trauma import DynamicTraumaCalculator
from ..lacanian.encrypted_unconscious import EncryptedUnconsciousLayer
from .soft_hair_encoding import SoftHairMemory

logger = logging.getLogger(__name__)


class TopographicalLayer(Enum):
    """Camadas da estrutura tópica freudiana."""

    CONSCIOUS = "conscious"  # Acessível diretamente
    PRECONSCIOUS = "preconscious"  # Não acessível agora, mas pode ser trazido à consciência
    UNCONSCIOUS = "unconscious"  # Reprimido, criptografado, inacessível ao Ego


@dataclass
class MemoryClassification:
    """Classificação de memória segundo estrutura tópica."""

    layer: TopographicalLayer
    is_traumatic: bool
    trauma_score: float  # 0.0 = não traumático, 1.0 = altamente traumático
    classification_reason: str
    metadata: Dict[str, Any]


class FreudianTopographicalMemory:
    """
    Sistema de memória baseado na estrutura tópica freudiana.

    Distingue entre:
    - PRÉ-CONSCIENTE: Memórias não traumáticas (comprimidas, acessíveis)
    - INCONSCIENTE: Memórias traumáticas (criptografadas, inacessíveis)
    """

    def __init__(self):
        """Inicializa sistema tópico de memória."""
        # Componentes
        self.soft_hair_memory = SoftHairMemory()  # Para pré-consciente (compressão)
        self.unconscious_layer = EncryptedUnconsciousLayer(
            security_level=128
        )  # Para inconsciente (criptografia)
        self.trauma_calculator = DynamicTraumaCalculator()  # Para classificar trauma

        # Armazenamento por camada
        self.preconscious_memories: Dict[str, Dict[str, Any]] = {}  # Hash → dados comprimidos
        self.unconscious_memories: Dict[str, bytes] = {}  # Hash → dados criptografados

        # Metadados
        self.memory_classifications: Dict[str, MemoryClassification] = {}

        logger.info(
            "FreudianTopographicalMemory inicializado (Consciente-Pré-Consciente-Inconsciente)"
        )

    def classify_memory(
        self,
        memory_data: np.ndarray,
        context: Dict[str, Any],
    ) -> MemoryClassification:
        """
        Classifica memória segundo estrutura tópica freudiana.

        Critérios:
        - Traumático (erro crítico, OOM, falha estrutural) → INCONSCIENTE
        - Não traumático (consolidação normal) → PRÉ-CONSCIENTE

        Args:
            memory_data: Dados da memória
            context: Contexto (tipo, erro, severidade, etc.)

        Returns:
            MemoryClassification com camada e razão
        """
        # 1. Calcular trauma score
        trauma_score = self._calculate_trauma_score(context)

        # 2. Determinar se é traumático
        is_traumatic = trauma_score > 0.5  # Threshold para trauma

        # 3. Classificar camada
        if is_traumatic:
            layer = TopographicalLayer.UNCONSCIOUS
            reason = (
                f"Memória traumática (score={trauma_score:.2f}): "
                f"{context.get('error_type', 'unknown')} - "
                f"{context.get('severity', 'unknown')}"
            )
        else:
            layer = TopographicalLayer.PRECONSCIOUS
            reason = (
                f"Memória não traumática (score={trauma_score:.2f}): "
                f"Consolidação normal de {context.get('type', 'memory')}"
            )

        classification = MemoryClassification(
            layer=layer,
            is_traumatic=is_traumatic,
            trauma_score=trauma_score,
            classification_reason=reason,
            metadata=context,
        )

        logger.debug(f"Classificação: {reason}")

        return classification

    def _calculate_trauma_score(self, context: Dict[str, Any]) -> float:
        """
        Calcula score de trauma (0.0 = não traumático, 1.0 = altamente traumático).

        Fatores:
        - Tipo de erro (OOM, crash, falha estrutural)
        - Severidade
        - Impacto no sistema
        """
        score = 0.0

        # Fator 1: Tipo de erro
        error_type = context.get("error_type", "").lower()
        if "oom" in error_type or "out of memory" in error_type:
            score += 0.4
        if "crash" in error_type or "fatal" in error_type:
            score += 0.5
        if "structural" in error_type or "failure" in error_type:
            score += 0.3

        # Fator 2: Severidade
        severity = context.get("severity", "").lower()
        if severity == "critical" or severity == "high":
            score += 0.3
        elif severity == "medium":
            score += 0.15

        # Fator 3: Impacto
        impact = context.get("impact", "low").lower()
        if impact == "high" or impact == "system_wide":
            score += 0.2

        # Normalizar para [0, 1]
        score = min(1.0, score)

        return score

    def consolidate_to_preconscious(
        self,
        memory_data: np.ndarray,
        memory_key: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Consolida memória para PRÉ-CONSCIENTE (comprimida, mas acessível).

        Processo:
        1. Comprimir usando SoftHair
        2. Armazenar comprimida (não criptografada)
        3. Ego pode acessar quando necessário

        Args:
            memory_data: Dados da memória
            memory_key: Chave única da memória
            metadata: Metadados

        Returns:
            Estatísticas de consolidação
        """
        # Comprimir
        # Converter ndarray para Sequence (lista) para compatibilidade com SoftHairMemory
        memory_data_seq = (
            memory_data.tolist() if isinstance(memory_data, np.ndarray) else memory_data
        )
        soft_hair = self.soft_hair_memory.store(memory_key, memory_data_seq)

        # Armazenar no pré-consciente
        content_hash = self._hash_memory(memory_data)
        self.preconscious_memories[content_hash] = {
            "soft_hair_key": memory_key,
            "compression_ratio": soft_hair.compression_ratio,
            "metadata": metadata,
            "consolidated_at": datetime.now().isoformat(),
            "accessible_to_ego": True,  # PRÉ-CONSCIENTE: Acessível ao Ego
        }

        logger.info(
            f"✅ Memória consolidada para PRÉ-CONSCIENTE: {memory_key} "
            f"(compressão {soft_hair.compression_ratio:.2f}x)"
        )

        return {
            "layer": "preconscious",
            "compression_ratio": soft_hair.compression_ratio,
            "accessible_to_ego": True,
        }

    def repress_to_unconscious(
        self,
        memory_data: np.ndarray,
        memory_key: str,
        metadata: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Reprime memória para INCONSCIENTE (criptografada, inacessível ao Ego).

        Processo:
        1. Reduzir dimensionalidade (amostra representativa)
        2. Criptografar usando EncryptedUnconsciousLayer
        3. Armazenar criptografada
        4. Ego NÃO pode acessar diretamente

        Args:
            memory_data: Dados da memória
            memory_key: Chave única da memória
            metadata: Metadados

        Returns:
            Estatísticas de repressão
        """
        # Preparar dados para repressão (reduzir dimensionalidade)
        if memory_data.size > 1000:
            # Amostra representativa
            flat = memory_data.flatten()
            step = max(1, len(flat) // 256)
            sample = flat[::step]
        else:
            sample = memory_data.flatten() if memory_data.size > 1 else memory_data

        # Normalizar
        if sample.size > 0:
            sample_norm = (sample - sample.min()) / (sample.max() - sample.min() + 1e-8)
            # Padding para tamanho fixo (256 dims)
            if len(sample_norm) < 256:
                padded = np.pad(sample_norm, (0, 256 - len(sample_norm)), mode="constant")
            else:
                padded = sample_norm[:256]

            # Reprimir (criptografar)
            encrypted_data = self.unconscious_layer.repress_memory(
                padded,
                metadata={
                    **metadata,
                    "type": "traumatic_memory",
                    "repressed_at": datetime.now().isoformat(),
                },
            )

            # Armazenar no inconsciente
            content_hash = self._hash_memory(memory_data)
            self.unconscious_memories[content_hash] = encrypted_data

            logger.warning(
                f"🔒 Memória REPRIMIDA para INCONSCIENTE: {memory_key} " f"(inacessível ao Ego)"
            )

            return {
                "layer": "unconscious",
                "encrypted": True,
                "accessible_to_ego": False,
            }

        return {"layer": "unconscious", "error": "failed_to_repress"}

    def retrieve_from_preconscious(self, content_hash: str) -> Optional[np.ndarray]:
        """
        Recupera memória do PRÉ-CONSCIENTE (Ego pode acessar).

        Args:
            content_hash: Hash da memória

        Returns:
            Dados descomprimidos ou None se não encontrado
        """
        if content_hash not in self.preconscious_memories:
            return None

        memory_info = self.preconscious_memories[content_hash]
        soft_hair_key = memory_info["soft_hair_key"]

        # Descomprimir
        data = self.soft_hair_memory.retrieve(soft_hair_key)

        if data is not None:
            logger.info(f"✅ Memória recuperada do PRÉ-CONSCIENTE: {content_hash}")
            # Converter Sequence de volta para ndarray
            if not isinstance(data, np.ndarray):
                data_array: np.ndarray = np.array(data)
            else:
                data_array = data
            return data_array

        return None

    def check_unconscious_influence(
        self,
        query_vector: np.ndarray,
    ) -> float:
        """
        Verifica influência do INCONSCIENTE (sem acessar diretamente).

        O Ego não pode acessar memórias inconscientes diretamente,
        mas pode sentir sua influência via operações homomórficas.

        Args:
            query_vector: Vetor de consulta

        Returns:
            Score de influência inconsciente (0.0-1.0)
        """
        if not self.unconscious_memories:
            return 0.0

        # Converter memórias inconscientes para lista de bytes
        encrypted_memories = list(self.unconscious_memories.values())

        # Calcular influência inconsciente (sem descriptografar)
        influence = self.unconscious_layer.unconscious_influence(
            encrypted_memories,
            query_vector,
        )

        # Normalizar para [0, 1]
        influence_score = max(0.0, min(1.0, abs(influence)))

        if influence_score > 0.1:
            logger.debug(
                f"🧠 Influência inconsciente detectada: {influence_score:.2f} "
                "(Ego não pode acessar diretamente)"
            )

        return influence_score

    def _hash_memory(self, data: np.ndarray) -> str:
        """Gera hash único para memória."""
        import hashlib

        return hashlib.sha256(data.tobytes()).hexdigest()

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema tópico."""
        return {
            "preconscious_count": len(self.preconscious_memories),
            "unconscious_count": len(self.unconscious_memories),
            "total_classifications": len(self.memory_classifications),
            "traumatic_memories": sum(
                1 for c in self.memory_classifications.values() if c.is_traumatic
            ),
            "non_traumatic_memories": sum(
                1 for c in self.memory_classifications.values() if not c.is_traumatic
            ),
        }
