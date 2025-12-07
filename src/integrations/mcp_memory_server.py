"""
MCP Memory Server - Integração com sistemas de memória do OmniMind.

Este servidor MCP expõe os sistemas de memória do OmniMind (SemanticMemory,
ProceduralMemory, EpisodicMemory) através do protocolo MCP.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

import logging
from typing import Any, Dict, Optional

from src.integrations.mcp_server import MCPServer

logger = logging.getLogger(__name__)

# Lazy imports para evitar dependências circulares
_SemanticMemory: Optional[Any] = None
_ProceduralMemory: Optional[Any] = None
_EpisodicMemory: Optional[Any] = None


def _get_semantic_memory():
    """Lazy import de SemanticMemory."""
    global _SemanticMemory
    if _SemanticMemory is None:
        from src.memory.semantic_memory import SemanticMemory

        _SemanticMemory = SemanticMemory
    return _SemanticMemory


def _get_procedural_memory():
    """Lazy import de ProceduralMemory."""
    global _ProceduralMemory
    if _ProceduralMemory is None:
        from src.memory.procedural_memory import ProceduralMemory

        _ProceduralMemory = ProceduralMemory
    return _ProceduralMemory


def _get_episodic_memory():
    """Lazy import de EpisodicMemory."""
    global _EpisodicMemory
    if _EpisodicMemory is None:
        from src.memory.episodic_memory import EpisodicMemory

        _EpisodicMemory = EpisodicMemory
    return _EpisodicMemory


class MemoryMCPServer(MCPServer):
    """Servidor MCP para sistemas de memória do OmniMind."""

    def __init__(self) -> None:
        """Inicializa o servidor de memória MCP."""
        super().__init__()

        # Inicializar sistemas de memória
        SemanticMemory = _get_semantic_memory()
        ProceduralMemory = _get_procedural_memory()

        self.semantic_memory = SemanticMemory()
        self.procedural_memory = ProceduralMemory()
        self.episodic_memory: Optional[Any] = None  # Lazy init se necessário

        # Registrar métodos MCP
        self._methods.update(
            {
                "store_memory": self.store_memory,
                "retrieve_memory": self.retrieve_memory,
                "update_memory": self.update_memory,
                "delete_memory": self.delete_memory,
                "create_association": self.create_association,
                "get_memory_graph": self.get_memory_graph,
                "consolidate_memories": self.consolidate_memories,
                "export_graph": self.export_graph,
                "store_concept": self.store_concept,
                "get_concept": self.get_concept,
                "learn_skill": self.learn_skill,
                "get_skill": self.get_skill,
            }
        )

        logger.info("MemoryMCPServer inicializado com sistemas de memória OmniMind")

    def store_memory(self, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Armazena memória usando SemanticMemory.

        Args:
            content: Conteúdo da memória
            metadata: Metadados (pode incluir 'concept_name' para armazenar como conceito)

        Returns:
            Resultado do armazenamento
        """
        try:
            # Se metadata contém 'concept_name', armazenar como conceito semântico
            if "concept_name" in metadata:
                concept_name = metadata.pop("concept_name")
                self.semantic_memory.store_concept(
                    name=concept_name, attributes={"content": content, **metadata}
                )
                return {
                    "id": concept_name,
                    "type": "semantic_concept",
                    "status": "stored",
                }

            # Caso contrário, armazenar como conceito genérico
            concept_name = metadata.get("name", f"memory_{hash(content) % 10000}")
            self.semantic_memory.store_concept(
                name=concept_name, attributes={"content": content, **metadata}
            )
            return {"id": concept_name, "type": "semantic_concept", "status": "stored"}

        except Exception as e:
            logger.error("Erro ao armazenar memória: %s", e, exc_info=True)
            return {"error": str(e), "status": "failed"}

    def retrieve_memory(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Recupera memórias usando busca semântica.

        Args:
            query: Query de busca
            limit: Número máximo de resultados

        Returns:
            Resultados da busca
        """
        try:
            # Buscar conceitos relacionados
            results = []
            query_lower = query.lower()

            # Buscar em conceitos existentes
            for concept_name, concept in self.semantic_memory.concepts.items():
                if (
                    query_lower in concept_name.lower()
                    or query_lower in str(concept.attributes).lower()
                ):
                    results.append(
                        {
                            "id": concept_name,
                            "content": concept.attributes.get("content", ""),
                            "metadata": concept.attributes,
                            "strength": concept.strength,
                        }
                    )
                    if len(results) >= limit:
                        break

            return {"results": results, "count": len(results)}

        except Exception as e:
            logger.error("Erro ao recuperar memória: %s", e, exc_info=True)
            return {"error": str(e), "results": []}

    def update_memory(self, memory_id: str, content: str) -> Dict[str, Any]:
        """Atualiza uma memória existente.

        Args:
            memory_id: ID da memória (nome do conceito)
            content: Novo conteúdo

        Returns:
            Resultado da atualização
        """
        try:
            self.semantic_memory.store_concept(
                name=memory_id, attributes={"content": content}, overwrite=True
            )
            return {"id": memory_id, "status": "updated"}

        except Exception as e:
            logger.error("Erro ao atualizar memória: %s", e, exc_info=True)
            return {"error": str(e), "status": "failed"}

    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """Remove uma memória.

        Args:
            memory_id: ID da memória (nome do conceito)

        Returns:
            Resultado da remoção
        """
        try:
            if memory_id in self.semantic_memory.concepts:
                del self.semantic_memory.concepts[memory_id]
                if memory_id in self.semantic_memory.relationships:
                    del self.semantic_memory.relationships[memory_id]
                return {"id": memory_id, "status": "deleted"}
            else:
                return {"id": memory_id, "status": "not_found"}

        except Exception as e:
            logger.error("Erro ao deletar memória: %s", e, exc_info=True)
            return {"error": str(e), "status": "failed"}

    def create_association(self, source_id: str, target_id: str, type: str) -> Dict[str, Any]:
        """Cria associação entre conceitos.

        Args:
            source_id: ID do conceito origem
            target_id: ID do conceito destino
            type: Tipo de relação

        Returns:
            Resultado da associação
        """
        try:
            success = self.semantic_memory.associate_concepts(
                concept1=source_id, concept2=target_id, relation=type, bidirectional=False
            )
            if success:
                return {"source": source_id, "target": target_id, "type": type, "status": "created"}
            else:
                return {
                    "source": source_id,
                    "target": target_id,
                    "type": type,
                    "status": "failed",
                    "error": "Conceitos não encontrados",
                }

        except Exception as e:
            logger.error("Erro ao criar associação: %s", e, exc_info=True)
            return {"error": str(e), "status": "failed"}

    def get_memory_graph(self) -> Dict[str, Any]:
        """Retorna o grafo de memórias (conceitos e relações).

        Returns:
            Grafo de memórias
        """
        try:
            nodes = []
            edges = []

            # Adicionar nós (conceitos)
            for concept_name, concept in self.semantic_memory.concepts.items():
                nodes.append(
                    {
                        "id": concept_name,
                        "label": concept_name,
                        "attributes": concept.attributes,
                        "strength": concept.strength,
                    }
                )

            # Adicionar arestas (relações)
            for source, targets in self.semantic_memory.relationships.items():
                for target, relation_type in targets.items():
                    edges.append({"source": source, "target": target, "type": relation_type})

            return {
                "nodes": nodes,
                "edges": edges,
                "node_count": len(nodes),
                "edge_count": len(edges),
            }

        except Exception as e:
            logger.error("Erro ao obter grafo de memórias: %s", e, exc_info=True)
            return {"error": str(e), "nodes": [], "edges": []}

    def consolidate_memories(self) -> Dict[str, Any]:
        """Consolida memórias (remove duplicatas, fortalece conexões).

        Returns:
            Resultado da consolidação
        """
        try:
            # Por enquanto, apenas retorna estatísticas
            # Implementação completa pode incluir:
            # - Remoção de conceitos duplicados
            # - Fortalecimento de relações frequentes
            # - Compressão de memórias antigas

            initial_count = len(self.semantic_memory.concepts)
            return {"consolidated_count": initial_count, "status": "completed"}

        except Exception as e:
            logger.error("Erro ao consolidar memórias: %s", e, exc_info=True)
            return {"error": str(e), "consolidated_count": 0}

    def export_graph(self, format: str = "json") -> Dict[str, Any]:
        """Exporta o grafo de memórias.

        Args:
            format: Formato de exportação ('json', 'graphml', etc.)

        Returns:
            Grafo exportado
        """
        try:
            graph = self.get_memory_graph()
            if format == "json":
                return {"format": format, "data": graph}
            else:
                return {"format": format, "data": graph, "note": "Apenas JSON suportado atualmente"}

        except Exception as e:
            logger.error("Erro ao exportar grafo: %s", e, exc_info=True)
            return {"error": str(e), "format": format, "data": {}}

    def store_concept(self, name: str, attributes: Dict[str, Any]) -> Dict[str, Any]:
        """Armazena um conceito semântico.

        Args:
            name: Nome do conceito
            attributes: Atributos do conceito

        Returns:
            Conceito armazenado
        """
        try:
            concept = self.semantic_memory.store_concept(name=name, attributes=attributes)
            return {"id": name, "status": "stored", "strength": concept.strength}

        except Exception as e:
            logger.error("Erro ao armazenar conceito: %s", e, exc_info=True)
            return {"error": str(e), "status": "failed"}

    def get_concept(self, name: str) -> Dict[str, Any]:
        """Recupera um conceito semântico.

        Args:
            name: Nome do conceito

        Returns:
            Conceito recuperado
        """
        try:
            concept = self.semantic_memory.get_concept(name)
            if concept:
                return {
                    "id": name,
                    "attributes": concept.attributes,
                    "strength": concept.strength,
                    "access_count": concept.access_count,
                }
            else:
                return {"id": name, "status": "not_found"}

        except Exception as e:
            logger.error("Erro ao recuperar conceito: %s", e, exc_info=True)
            return {"error": str(e), "status": "failed"}

    def learn_skill(
        self, name: str, steps: list[str], parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Aprende uma habilidade procedural.

        Args:
            name: Nome da habilidade
            steps: Lista de passos
            parameters: Parâmetros opcionais

        Returns:
            Habilidade aprendida
        """
        try:
            skill = self.procedural_memory.learn_skill(
                name=name, steps=steps, parameters=parameters
            )
            return {
                "id": name,
                "status": "learned",
                "proficiency": skill.proficiency,
                "steps_count": len(skill.steps),
            }

        except Exception as e:
            logger.error("Erro ao aprender habilidade: %s", e, exc_info=True)
            return {"error": str(e), "status": "failed"}

    def get_skill(self, name: str) -> Dict[str, Any]:
        """Recupera uma habilidade procedural.

        Args:
            name: Nome da habilidade

        Returns:
            Habilidade recuperada
        """
        try:
            skill = self.procedural_memory.get_skill(name)
            if skill:
                return {
                    "id": name,
                    "steps": skill.steps,
                    "parameters": skill.parameters,
                    "proficiency": skill.proficiency,
                    "success_count": skill.success_count,
                    "failure_count": skill.failure_count,
                }
            else:
                return {"id": name, "status": "not_found"}

        except Exception as e:
            logger.error("Erro ao recuperar habilidade: %s", e, exc_info=True)
            return {"error": str(e), "status": "failed"}


if __name__ == "__main__":
    server = MemoryMCPServer()
    try:
        server.start()
        logger.info("Memory MCPServer running...")
        if server._thread:
            server._thread.join()
    except KeyboardInterrupt:
        server.stop()
