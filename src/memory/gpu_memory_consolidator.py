"""
GPU Memory Consolidator - Consolidação Freudiana de Memória GPU

Quando a GPU está cheia, ao invés de simplesmente deletar memórias,
o sistema consolida segundo a ESTRUTURA TÓPICA FREUDIANA:

1. CONSCIENTE: Memórias ativas na GPU (acessíveis diretamente)
2. PRÉ-CONSCIENTE: Memórias não traumáticas (comprimidas, mas acessíveis ao Ego)
3. INCONSCIENTE: Memórias traumáticas (criptografadas, inacessíveis ao Ego)

Processo:
1. Detecta VRAM crítica (> 85%)
2. Classifica memórias (traumáticas vs não traumáticas)
3. PRÉ-CONSCIENTE: Comprime usando SoftHair (acessível ao Ego)
4. INCONSCIENTE: Reprime usando EncryptedUnconsciousLayer (inacessível ao Ego)
5. Mantém rastro/hash para ativação retroativa futura
6. Limpa GPU apenas após consolidação bem-sucedida

Analogia Humana:
- Sono: Consolidação de memórias do dia
- Pré-Consciente: Memórias que podem ser lembradas facilmente
- Repressão: Memórias traumáticas vão para inconsciente (inacessíveis)
- Déjà vu: Sensação de familiaridade sem acesso direto (influência inconsciente)
- Ativação: Memórias pré-conscientes podem ser reativadas pelo Ego
"""

import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import torch

from ..monitor.resource_manager import HybridResourceManager
from .freudian_topographical_memory import (
    FreudianTopographicalMemory,
)

logger = logging.getLogger(__name__)


@dataclass
class ConsolidatedMemory:
    """Memória consolidada no inconsciente."""

    content_hash: str  # Hash para ativação retroativa
    encrypted_data: bytes  # Dados criptografados
    compression_ratio: float  # Taxa de compressão
    metadata: Dict[str, Any]  # Metadados (tipo, timestamp, etc.)
    activation_trace: List[str]  # Rastro de ativação (quais processos podem reativar)
    consolidated_at: datetime  # Quando foi consolidada


class GPUMemoryConsolidator:
    """
    Sistema de Consolidação de Memória GPU.

    Ao invés de deletar memórias quando GPU está cheia,
    consolida (comprime) e reprime para inconsciente criptografado.
    """

    def __init__(
        self,
        vram_threshold: float = 85.0,
        compression_target: float = 0.3,  # Comprimir para 30% do tamanho original
    ):
        """
        Inicializa consolidador de memória GPU.

        Args:
            vram_threshold: Percentual de VRAM que dispara consolidação
            compression_target: Taxa de compressão desejada (0.3 = 30% do original)
        """
        self.vram_threshold = vram_threshold
        self.compression_target = compression_target

        # Componentes de consolidação (estrutura tópica freudiana)
        self.topographical_memory = FreudianTopographicalMemory()
        self.resource_manager = HybridResourceManager()

        # Registro de memórias consolidadas
        self.consolidated_memories: Dict[str, ConsolidatedMemory] = {}

        # Rastros de ativação (quais processos podem reativar quais memórias)
        self.activation_traces: Dict[str, List[str]] = {}

        logger.info(
            f"GPUMemoryConsolidator inicializado (Estrutura Tópica Freudiana): "
            f"threshold={vram_threshold}%, compression={compression_target*100:.0f}%"
        )

    def should_consolidate(self) -> bool:
        """
        Verifica se deve consolidar memória GPU.

        Returns:
            True se VRAM > threshold
        """
        if not torch.cuda.is_available():
            return False

        stats = self.resource_manager.get_system_status()
        vram_percent = stats.get("vram", 0.0)

        return vram_percent > self.vram_threshold

    def consolidate_gpu_memory(
        self,
        memory_items: List[Dict[str, Any]],
        process_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Consolida memórias da GPU para inconsciente criptografado.

        Processo:
        1. Comprime cada memória usando SoftHair
        2. Reprime para EncryptedUnconsciousLayer
        3. Mantém rastro de ativação
        4. Limpa GPU após consolidação

        Args:
            memory_items: Lista de itens de memória a consolidar
                Cada item deve ter: {'data': tensor/array, 'type': str, 'metadata': dict}
            process_context: Contexto do processo que está consolidando

        Returns:
            Estatísticas da consolidação
        """
        if not memory_items:
            return {
                "status": "skipped",
                "reason": "no_memories",
                "consolidated": 0,
            }

        logger.info(
            f"🧠 Consolidando {len(memory_items)} memórias da GPU "
            f"segundo estrutura tópica freudiana (Pré-Consciente/Inconsciente)..."
        )

        consolidated_count = 0
        total_original_size: float = 0.0
        total_compressed_size: float = 0.0

        for item in memory_items:
            try:
                # 1. Extrair dados
                data = item.get("data")
                memory_type = item.get("type", "unknown")
                metadata = item.get("metadata", {})

                if data is None:
                    continue

                # 2. Converter para numpy array se necessário
                if isinstance(data, torch.Tensor):
                    # Mover para CPU antes de consolidar
                    if data.is_cuda:
                        data = data.cpu()
                    data_array = data.detach().numpy()
                elif isinstance(data, np.ndarray):
                    data_array = data
                else:
                    # Tentar converter
                    data_array = np.array(data)

                # Calcular tamanho original
                original_size = data_array.nbytes / 1024 / 1024  # MB
                total_original_size += original_size

                # 3. CLASSIFICAR segundo estrutura tópica freudiana
                classification = self.topographical_memory.classify_memory(
                    data_array,
                    context={
                        **metadata,
                        "type": memory_type,
                        "error_type": metadata.get("error_type", ""),
                        "severity": metadata.get("severity", "low"),
                        "impact": metadata.get("impact", "low"),
                    },
                )

                # 4. CONSOLIDAR baseado na classificação
                memory_key = (
                    f"{memory_type}_{hashlib.sha256(data_array.tobytes()).hexdigest()[:16]}"
                )

                if classification.is_traumatic:
                    # TRAUMÁTICO → INCONSCIENTE (criptografado, inacessível ao Ego)
                    result = self.topographical_memory.repress_to_unconscious(
                        data_array,
                        memory_key,
                        {
                            **metadata,
                            "type": memory_type,
                            "original_size_mb": original_size,
                            "trauma_score": classification.trauma_score,
                        },
                    )
                    layer = "unconscious"
                    compression_ratio = 0.3  # Estimativa para criptografia
                else:
                    # NÃO TRAUMÁTICO → PRÉ-CONSCIENTE (comprimido, acessível ao Ego)
                    result = self.topographical_memory.consolidate_to_preconscious(
                        data_array,
                        memory_key,
                        {
                            **metadata,
                            "type": memory_type,
                            "original_size_mb": original_size,
                        },
                    )
                    layer = "preconscious"
                    compression_ratio = result.get("compression_ratio", 0.3)

                # 5. Criar registro de consolidação
                content_hash = self.topographical_memory._hash_memory(data_array)
                consolidated_memory = ConsolidatedMemory(
                    content_hash=content_hash,
                    encrypted_data=result.get("encrypted_data", b""),
                    compression_ratio=compression_ratio,
                    metadata={
                        **metadata,
                        "type": memory_type,
                        "original_size_mb": original_size,
                        "layer": layer,
                        "is_traumatic": classification.is_traumatic,
                        "trauma_score": classification.trauma_score,
                        "accessible_to_ego": not classification.is_traumatic,
                    },
                    activation_trace=[process_context] if process_context else [],
                    consolidated_at=datetime.now(),
                )

                self.consolidated_memories[content_hash] = consolidated_memory

                # 6. Registrar rastro de ativação
                if process_context:
                    if content_hash not in self.activation_traces:
                        self.activation_traces[content_hash] = []
                    self.activation_traces[content_hash].append(process_context)

                compressed_size = original_size * compression_ratio
                total_compressed_size += compressed_size
                consolidated_count += 1

                logger.info(
                    f"✅ Memória consolidada para {layer.upper()}: {memory_type} "
                    f"({original_size:.2f}MB → {compressed_size:.2f}MB, "
                    f"traumático={classification.is_traumatic})"
                )

            except Exception as e:
                logger.error(f"Erro ao consolidar memória: {e}", exc_info=True)
                continue

        # 7. Limpar GPU após consolidação bem-sucedida
        if consolidated_count > 0:
            self._cleanup_gpu_after_consolidation()

        stats = {
            "status": "success",
            "consolidated": consolidated_count,
            "total_original_mb": total_original_size,
            "total_compressed_mb": total_compressed_size,
            "compression_ratio": (
                total_compressed_size / total_original_size if total_original_size > 0 else 0.0
            ),
            "freed_mb": total_original_size - total_compressed_size,
        }

        logger.info(
            f"🧠 Consolidação concluída: {consolidated_count} memórias, "
            f"{stats['freed_mb']:.2f}MB liberados da GPU"
        )

        return stats

    def _cleanup_gpu_after_consolidation(self) -> None:
        """Limpa GPU após consolidação bem-sucedida."""
        import gc

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
            logger.debug("🧹 GPU limpa após consolidação")

    def check_activation_trace(
        self,
        process_context: str,
        query_vector: Optional[np.ndarray] = None,
    ) -> List[Dict[str, Any]]:
        """
        Verifica se há memórias consolidadas que podem ser reativadas.

        Analogia: Déjà vu - sensação de familiaridade sem acesso direto.

        Args:
            process_context: Contexto do processo atual
            query_vector: Vetor de consulta para busca por similaridade

        Returns:
            Lista de memórias que podem ser reativadas
        """
        activatable = []

        for content_hash, memory in self.consolidated_memories.items():
            # Verificar se processo atual está no rastro de ativação
            traces = self.activation_traces.get(content_hash, [])
            if process_context in traces:
                activatable.append(
                    {
                        "content_hash": content_hash,
                        "type": memory.metadata.get("type", "unknown"),
                        "consolidated_at": memory.consolidated_at.isoformat(),
                        "compression_ratio": memory.compression_ratio,
                        "activation_trace": traces,
                        "status": "activatable",
                    }
                )

        # Se há query_vector, verificar influência inconsciente
        if query_vector is not None and activatable:
            encrypted_memories = [
                mem.encrypted_data
                for mem in self.consolidated_memories.values()
                if mem.content_hash in [a["content_hash"] for a in activatable]
            ]

            if encrypted_memories:
                influence = self.topographical_memory.unconscious_layer.unconscious_influence(
                    encrypted_memories,
                    query_vector,
                )

                # Adicionar score de influência
                for item in activatable:
                    item["unconscious_influence"] = influence

        return activatable

    def reactivate_memory(
        self,
        content_hash: str,
        process_context: str,
    ) -> Optional[np.ndarray]:
        """
        Reativa memória consolidada.

        Processo:
        1. Verifica se memória existe e está no rastro de ativação
        2. Descomprime usando SoftHair
        3. Retorna dados originais (aproximados)

        Args:
            content_hash: Hash da memória consolidada
            process_context: Contexto do processo que está reativando

        Returns:
            Dados reativados (numpy array) ou None se não encontrado
        """
        if content_hash not in self.consolidated_memories:
            logger.warning(f"Memória {content_hash} não encontrada para reativação")
            return None

        memory = self.consolidated_memories[content_hash]

        # Verificar se processo está autorizado a reativar
        traces = self.activation_traces.get(content_hash, [])
        if process_context not in traces:
            logger.warning(
                f"Processo {process_context} não está no rastro de ativação "
                f"da memória {content_hash}"
            )
            # Mas permite reativação (pode ser novo processo relacionado)

        # Verificar camada da memória
        layer = memory.metadata.get("layer", "unknown")
        is_traumatic = memory.metadata.get("is_traumatic", False)

        if layer == "preconscious" and not is_traumatic:
            # PRÉ-CONSCIENTE: Ego pode acessar diretamente
            content_hash_internal = content_hash
            reactivated_data = self.topographical_memory.retrieve_from_preconscious(
                content_hash_internal
            )
            if reactivated_data is not None:
                logger.info(
                    f"✅ Memória PRÉ-CONSCIENTE {content_hash} reativada "
                    f"(Ego tem acesso direto)"
                )
                return reactivated_data
        elif layer == "unconscious" and is_traumatic:
            # INCONSCIENTE: Ego NÃO pode acessar diretamente
            logger.warning(
                f"🔒 Memória INCONSCIENTE {content_hash} não pode ser acessada pelo Ego "
                f"(reprimida, criptografada)"
            )
            # Mas pode verificar influência inconsciente
            # (implementar se necessário)
            return None

        logger.warning(f"Não foi possível reativar memória {content_hash} (layer={layer})")
        return None

    def get_consolidation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de consolidação."""
        total_memories = len(self.consolidated_memories)
        total_original_size = sum(
            m.metadata.get("original_size_mb", 0) for m in self.consolidated_memories.values()
        )
        total_compressed_size = sum(
            m.metadata.get("original_size_mb", 0) * m.compression_ratio
            for m in self.consolidated_memories.values()
        )

        # Estatísticas da estrutura tópica
        topo_stats = self.topographical_memory.get_statistics()

        return {
            "total_consolidated": total_memories,
            "total_original_mb": total_original_size,
            "total_compressed_mb": total_compressed_size,
            "average_compression": (
                total_compressed_size / total_original_size if total_original_size > 0 else 0.0
            ),
            "freed_mb": total_original_size - total_compressed_size,
            "activation_traces": len(self.activation_traces),
            "topographical": {
                "preconscious_count": topo_stats["preconscious_count"],
                "unconscious_count": topo_stats["unconscious_count"],
                "traumatic_memories": topo_stats["traumatic_memories"],
                "non_traumatic_memories": topo_stats["non_traumatic_memories"],
            },
        }


# Instância global
_gpu_consolidator: Optional[GPUMemoryConsolidator] = None


def get_gpu_consolidator() -> GPUMemoryConsolidator:
    """Retorna instância global do consolidador."""
    global _gpu_consolidator
    if _gpu_consolidator is None:
        _gpu_consolidator = GPUMemoryConsolidator()
    return _gpu_consolidator
