"""
MCP Context Server - Sistema de gerenciamento de contexto INTEGRADO com OmniMind.

Este servidor MCP implementa um sistema de gerenciamento de contexto hierárquico que se integra
com toda a arquitetura OmniMind:
- SemanticMemoryLayer: Armazenamento persistente de contexto
- SharedWorkspace: Contexto compartilhado entre módulos
- ConsciousnessStateManager: Snapshots de contexto
- Níveis hierárquicos: project, session, task, code, memory, audit, ephemeral

Autor: Fabrício da Silva + assistência de IA
Data: 2025-01-XX
"""

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.integrations.mcp_server import MCPServer

logger = logging.getLogger(__name__)

# Níveis de contexto suportados
CONTEXT_LEVELS = [
    "project",  # Contexto do projeto inteiro
    "session",  # Contexto de uma sessão de trabalho
    "task",  # Contexto de uma tarefa específica
    "code",  # Contexto de código/arquivos
    "memory",  # Contexto de memória episódica/semântica
    "audit",  # Contexto de auditoria
    "ephemeral",  # Contexto temporário (não persistido)
]


@dataclass
class ContextEntry:
    """Uma entrada de contexto."""

    context_id: str
    level: str
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    compressed: bool = False
    compressed_size: Optional[int] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None


@dataclass
class ContextSnapshot:
    """Snapshot de contexto em um momento específico."""

    snapshot_id: str
    timestamp: datetime
    contexts: Dict[str, List[ContextEntry]]  # level -> entries
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextMCPServer(MCPServer):
    """Servidor MCP para gerenciamento de contexto integrado com OmniMind."""

    def __init__(
        self,
        workspace: Optional[Any] = None,  # SharedWorkspace
        semantic_memory: Optional[Any] = None,  # SemanticMemoryLayer
        state_manager: Optional[Any] = None,  # ConsciousnessStateManager
        storage_dir: Optional[Path] = None,
    ) -> None:
        """Inicializa o servidor de contexto MCP integrado.

        Args:
            workspace: Instância opcional de SharedWorkspace para contexto compartilhado
            semantic_memory: Instância opcional de SemanticMemoryLayer para persistência
            state_manager: Instância opcional de ConsciousnessStateManager para snapshots
            storage_dir: Diretório para armazenamento local de contexto
        """
        super().__init__()

        # Armazenamento em memória (por nível)
        self._contexts: Dict[str, List[ContextEntry]] = {level: [] for level in CONTEXT_LEVELS}

        # Snapshots
        self._snapshots: Dict[str, ContextSnapshot] = {}

        # Componentes integrados (opcionais)
        self.workspace = workspace
        self.semantic_memory = semantic_memory
        self.state_manager = state_manager

        # Armazenamento local
        self.storage_dir = storage_dir or Path("data/context")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Registrar métodos MCP (preserva initialize())
        self.register_methods(
            {
                "store_context": self.store_context,
                "retrieve_context": self.retrieve_context,
                "compress_context": self.compress_context,
                "snapshot_context": self.snapshot_context,
                "list_contexts": self.list_contexts,
                "delete_context": self.delete_context,
            }
        )

        logger.info(
            "ContextMCPServer inicializado (workspace=%s, semantic=%s, state=%s)",
            "✅" if workspace else "❌",
            "✅" if semantic_memory else "❌",
            "✅" if state_manager else "❌",
        )

    def store_context(self, level: str, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Armazena contexto em um nível específico.

        Args:
            level: Nível do contexto (project, session, task, code, memory, audit, ephemeral)
            content: Conteúdo do contexto
            metadata: Metadados adicionais

        Returns:
            Dict com status e context_id
        """
        if level not in CONTEXT_LEVELS:
            return {
                "status": "error",
                "error": f"Nível inválido: {level}. Níveis válidos: {CONTEXT_LEVELS}",
            }

        try:
            # Gerar ID único
            context_id = str(uuid.uuid4())

            # Criar entrada
            entry = ContextEntry(
                context_id=context_id,
                level=level,
                content=content,
                metadata=metadata,
            )

            # Armazenar em memória
            self._contexts[level].append(entry)

            # Persistir em SemanticMemoryLayer se disponível (exceto ephemeral)
            if level != "ephemeral" and self.semantic_memory:
                try:
                    episode_text = f"Context [{level}]: {content[:200]}"
                    episode_data = {
                        "context_id": context_id,
                        "level": level,
                        "content": content,
                        "metadata": json.dumps(metadata),
                    }
                    self.semantic_memory.store_episode(
                        episode_text=episode_text,
                        episode_data=episode_data,
                    )
                except Exception as e:
                    logger.warning("Erro ao persistir contexto no SemanticMemory: %s", e)

            # Registrar no SharedWorkspace se disponível
            if self.workspace:
                try:
                    # Criar embedding simples do conteúdo
                    content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
                    module_name = f"context_{level}_{content_hash}"
                    # Usar hash como embedding simples (fallback)
                    embedding = [float(int(c, 16)) / 15.0 for c in content_hash[:16]]
                    # Preencher até embedding_dim se necessário
                    if hasattr(self.workspace, "embedding_dim"):
                        while len(embedding) < self.workspace.embedding_dim:
                            embedding.append(0.0)
                        embedding = embedding[: self.workspace.embedding_dim]

                    self.workspace.write_module_state(
                        module_name=module_name,
                        embedding=embedding,
                        metadata={
                            "context_id": context_id,
                            "level": level,
                            "content_preview": content[:100],
                        },
                    )
                except Exception as e:
                    logger.debug("Erro ao registrar contexto no workspace: %s", e)

            # Persistir localmente (exceto ephemeral)
            if level != "ephemeral":
                self._persist_context_local(entry)

            logger.debug(f"✅ Contexto armazenado: level={level}, id={context_id}")

            return {
                "status": "stored",
                "level": level,
                "context_id": context_id,
                "timestamp": entry.timestamp.isoformat(),
            }

        except Exception as e:
            logger.error(f"Erro ao armazenar contexto: {e}")
            return {"status": "error", "error": str(e), "level": level}

    def retrieve_context(self, level: str, query: str = "", limit: int = 10) -> Dict[str, Any]:
        """Recupera contexto de um nível específico.

        Args:
            level: Nível do contexto
            query: Query opcional para filtrar conteúdo
            limit: Número máximo de resultados

        Returns:
            Dict com conteúdo e metadados
        """
        if level not in CONTEXT_LEVELS:
            return {
                "status": "error",
                "error": f"Nível inválido: {level}",
                "content": "",
            }

        try:
            # Buscar em memória
            entries = self._contexts.get(level, [])

            # Filtrar por query se fornecida
            if query:
                query_lower = query.lower()
                entries = [
                    e
                    for e in entries
                    if query_lower in e.content.lower()
                    or query_lower in json.dumps(e.metadata).lower()
                ]

            # Limitar resultados
            entries = entries[-limit:] if limit > 0 else entries

            # Atualizar contadores de acesso
            for entry in entries:
                entry.access_count += 1
                entry.last_accessed = datetime.now(timezone.utc)

            # Buscar em SemanticMemory se disponível e query fornecida
            semantic_results = []
            if query and self.semantic_memory:
                try:
                    semantic_results = self.semantic_memory.retrieve_similar(
                        query_text=query, top_k=limit
                    )
                except Exception as e:
                    logger.debug("Erro ao buscar em SemanticMemory: %s", e)

            # Combinar resultados
            all_content = []
            for entry in entries:
                all_content.append(
                    {
                        "context_id": entry.context_id,
                        "content": entry.content,
                        "metadata": entry.metadata,
                        "timestamp": entry.timestamp.isoformat(),
                        "access_count": entry.access_count,
                    }
                )

            # Adicionar resultados semânticos
            for result in semantic_results:
                if isinstance(result, dict) and "payload" in result:
                    payload = result["payload"]
                    if isinstance(payload, dict) and payload.get("level") == level:
                        all_content.append(
                            {
                                "context_id": payload.get("context_id", "unknown"),
                                "content": payload.get("content", ""),
                                "metadata": json.loads(payload.get("metadata", "{}")),
                                "timestamp": payload.get("timestamp", ""),
                                "similarity": result.get("score", 0.0),
                            }
                        )

            # Ordenar por timestamp (mais recente primeiro)
            all_content.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)

            logger.debug(f"✅ Contexto recuperado: level={level}, count={len(all_content)}")

            return {
                "status": "success",
                "level": level,
                "content": all_content,
                "count": len(all_content),
            }

        except Exception as e:
            logger.error(f"Erro ao recuperar contexto: {e}")
            return {
                "status": "error",
                "error": str(e),
                "level": level,
                "content": [],
            }

    def compress_context(self, level: str, ratio: float = 0.5) -> Dict[str, Any]:
        """Comprime contexto de um nível específico.

        Args:
            level: Nível do contexto
            ratio: Razão de compressão (0.0-1.0, onde 0.5 = 50% do tamanho original)

        Returns:
            Dict com status e ratio de compressão
        """
        if level not in CONTEXT_LEVELS:
            return {
                "status": "error",
                "error": f"Nível inválido: {level}",
                "ratio": 1.0,
            }

        try:
            entries = self._contexts.get(level, [])
            if not entries:
                return {
                    "status": "no_content",
                    "level": level,
                    "ratio": 1.0,
                    "message": "Nenhum contexto para comprimir",
                }

            # Calcular tamanhos
            original_size = sum(len(e.content.encode()) for e in entries)

            # Estratégia simples: manter apenas entradas mais acessadas e recentes
            # Ordenar por (access_count * 0.5 + recency_score * 0.5)
            now = datetime.now(timezone.utc)
            for entry in entries:
                if entry.last_accessed:
                    age_hours = (now - entry.last_accessed).total_seconds() / 3600
                    recency_score = max(0.0, 1.0 - age_hours / 24.0)  # Decai em 24h
                else:
                    recency_score = 0.0

                # Score combinado
                entry.metadata["_compress_score"] = entry.access_count * 0.5 + recency_score * 0.5

            # Ordenar e manter apenas top N
            entries_sorted = sorted(
                entries,
                key=lambda e: e.metadata.get("_compress_score", 0.0),
                reverse=True,
            )
            keep_count = max(1, int(len(entries) * ratio))
            entries_to_keep = entries_sorted[:keep_count]
            entries_to_remove = entries_sorted[keep_count:]

            # Remover entradas antigas
            for entry in entries_to_remove:
                self._contexts[level].remove(entry)

            # Marcar como comprimido
            for entry in entries_to_keep:
                entry.compressed = True
                entry.compressed_size = len(entry.content.encode())

            compressed_size = sum(len(e.content.encode()) for e in entries_to_keep)
            actual_ratio = compressed_size / original_size if original_size > 0 else 1.0

            logger.info(
                f"✅ Contexto comprimido: level={level}, "
                f"original={len(entries)}, kept={keep_count}, ratio={actual_ratio:.2f}"
            )

            return {
                "status": "compressed",
                "level": level,
                "ratio": actual_ratio,
                "original_count": len(entries),
                "compressed_count": keep_count,
            }

        except Exception as e:
            logger.error(f"Erro ao comprimir contexto: {e}")
            return {
                "status": "error",
                "error": str(e),
                "level": level,
                "ratio": 1.0,
            }

    def snapshot_context(self) -> Dict[str, Any]:
        """Cria um snapshot de todo o contexto atual.

        Returns:
            Dict com snapshot_id e metadados
        """
        try:
            snapshot_id = str(uuid.uuid4())
            timestamp = datetime.now(timezone.utc)

            # Criar snapshot
            snapshot = ContextSnapshot(
                snapshot_id=snapshot_id,
                timestamp=timestamp,
                contexts={level: self._contexts[level].copy() for level in CONTEXT_LEVELS},
                metadata={
                    "total_entries": sum(len(entries) for entries in self._contexts.values()),
                    "levels": CONTEXT_LEVELS,
                },
            )

            # Armazenar snapshot
            self._snapshots[snapshot_id] = snapshot

            # Persistir em ConsciousnessStateManager se disponível
            if self.state_manager:
                try:
                    # Criar snapshot de consciência com contexto
                    self.state_manager.take_snapshot(
                        phi_value=0.0,  # Contexto não tem Φ direto
                        qualia_signature={
                            "snapshot_type": "context",
                            "snapshot_id": snapshot_id,
                            "total_entries": snapshot.metadata["total_entries"],
                        },
                        attention_state={
                            "context_levels": len(CONTEXT_LEVELS),
                            "total_entries": snapshot.metadata["total_entries"],
                        },
                        integration_level=0.0,
                        metadata={
                            "context_snapshot_id": snapshot_id,
                            "timestamp": timestamp.isoformat(),
                        },
                    )
                except Exception as e:
                    logger.debug("Erro ao persistir snapshot no StateManager: %s", e)

            # Persistir localmente
            self._persist_snapshot_local(snapshot)

            logger.info(f"✅ Snapshot de contexto criado: {snapshot_id}")

            return {
                "status": "success",
                "snapshot_id": snapshot_id,
                "timestamp": timestamp.isoformat(),
                "metadata": snapshot.metadata,
            }

        except Exception as e:
            logger.error(f"Erro ao criar snapshot: {e}")
            return {"status": "error", "error": str(e), "snapshot_id": ""}

    def list_contexts(self, level: Optional[str] = None) -> Dict[str, Any]:
        """Lista todos os contextos ou de um nível específico.

        Args:
            level: Nível opcional para filtrar

        Returns:
            Dict com lista de contextos
        """
        try:
            if level:
                if level not in CONTEXT_LEVELS:
                    return {
                        "status": "error",
                        "error": f"Nível inválido: {level}",
                        "contexts": [],
                    }
                contexts = {level: self._contexts[level]}
            else:
                contexts = self._contexts

            result = {}
            for ctx_level, entries in contexts.items():
                result[ctx_level] = [
                    {
                        "context_id": e.context_id,
                        "content_preview": e.content[:100],
                        "metadata": e.metadata,
                        "timestamp": e.timestamp.isoformat(),
                        "access_count": e.access_count,
                        "compressed": e.compressed,
                    }
                    for e in entries
                ]

            return {
                "status": "success",
                "contexts": result,
                "total_levels": len(result),
                "total_entries": sum(len(entries) for entries in result.values()),
            }

        except Exception as e:
            logger.error(f"Erro ao listar contextos: {e}")
            return {"status": "error", "error": str(e), "contexts": {}}

    def delete_context(self, level: str, context_id: Optional[str] = None) -> Dict[str, Any]:
        """Deleta contexto de um nível específico.

        Args:
            level: Nível do contexto
            context_id: ID específico do contexto (opcional, se não fornecido, deleta todos)

        Returns:
            Dict com status
        """
        if level not in CONTEXT_LEVELS:
            return {
                "status": "error",
                "error": f"Nível inválido: {level}",
            }

        try:
            entries = self._contexts.get(level, [])

            if context_id:
                # Deletar entrada específica
                entries_to_remove = [e for e in entries if e.context_id == context_id]
                for entry in entries_to_remove:
                    entries.remove(entry)
                deleted_count = len(entries_to_remove)
            else:
                # Deletar todas as entradas do nível
                deleted_count = len(entries)
                entries.clear()

            logger.info(f"✅ Contexto deletado: level={level}, count={deleted_count}")

            return {
                "status": "success",
                "level": level,
                "deleted_count": deleted_count,
            }

        except Exception as e:
            logger.error(f"Erro ao deletar contexto: {e}")
            return {"status": "error", "error": str(e), "level": level}

    def _persist_context_local(self, entry: ContextEntry) -> None:
        """Persiste contexto localmente em arquivo JSONL."""
        try:
            file_path = self.storage_dir / f"context_{entry.level}.jsonl"
            with open(file_path, "a") as f:
                f.write(
                    json.dumps(
                        {
                            "context_id": entry.context_id,
                            "level": entry.level,
                            "content": entry.content,
                            "metadata": entry.metadata,
                            "timestamp": entry.timestamp.isoformat(),
                        }
                    )
                    + "\n"
                )
        except Exception as e:
            logger.debug("Erro ao persistir contexto localmente: %s", e)

    def _persist_snapshot_local(self, snapshot: ContextSnapshot) -> None:
        """Persiste snapshot localmente."""
        try:
            file_path = self.storage_dir / f"snapshot_{snapshot.snapshot_id}.json"
            with open(file_path, "w") as f:
                # Converter para dict serializável
                snapshot_dict = {
                    "snapshot_id": snapshot.snapshot_id,
                    "timestamp": snapshot.timestamp.isoformat(),
                    "metadata": snapshot.metadata,
                    "contexts": {
                        level: [
                            {
                                "context_id": e.context_id,
                                "level": e.level,
                                "content": e.content,
                                "metadata": e.metadata,
                                "timestamp": e.timestamp.isoformat(),
                            }
                            for e in entries
                        ]
                        for level, entries in snapshot.contexts.items()
                    },
                }
                json.dump(snapshot_dict, f, indent=2)
        except Exception as e:
            logger.debug("Erro ao persistir snapshot localmente: %s", e)


if __name__ == "__main__":
    server = ContextMCPServer()
    try:
        server.start()
        logger.info("Context MCPServer running...")
        if server._thread:
            server._thread.join()
    except KeyboardInterrupt:
        server.stop()
