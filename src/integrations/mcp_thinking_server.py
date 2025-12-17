"""
MCP Thinking Server - Sistema de pensamento sequencial INTEGRADO com OmniMind.

Este servidor MCP implementa um sistema de pensamento sequencial que se integra
com toda a arquitetura OmniMind:
- SharedWorkspace: Sessão = módulo, passos = eventos
- PhiCalculator via SharedWorkspace: Cálculo real de Φ
- NarrativeHistory: Passos = eventos sem significado (Lacaniano)
- SystemicMemoryTrace: Cada passo = marca topológica
- OrchestratorAgent: Sessão hierárquica (compartilhada + sub-sessões)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import numpy as np

from src.integrations.mcp_cache import get_mcp_cache
from src.integrations.mcp_server import MCPServer

logger = logging.getLogger(__name__)


@dataclass
class ThinkingStep:
    """Um passo em uma sessão de pensamento."""

    step_id: str
    session_id: str
    content: str
    step_type: str  # "observation", "thought", "action", "result"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_step_id: Optional[str] = None
    phi: float = 0.0  # Φ calculado via SharedWorkspace (IIT puro)
    quality_score: float = 0.0  # Score de qualidade do passo
    psi_producer: float = 0.0  # Ψ_produtor (Deleuze) - produção criativa
    psi_norm: float = 0.0  # Ψ normalizado [0, 1]
    psi_components: Optional[Dict[str, float]] = None  # Componentes de Ψ


@dataclass
class ThinkingSession:
    """Uma sessão de pensamento sequencial."""

    session_id: str
    goal: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    steps: List[ThinkingStep] = field(default_factory=list)
    parent_session_id: Optional[str] = None
    status: str = "active"  # "active", "completed", "paused", "merged"
    metadata: Dict[str, Any] = field(default_factory=dict)
    total_phi: float = 0.0  # Φ total da sessão via SharedWorkspace (IIT puro)
    total_psi: float = 0.0  # Ψ total da sessão (Deleuze)
    psi_history: List[float] = field(default_factory=list)  # Histórico de Ψ por passo


class ThinkingMCPServer(MCPServer):
    """Servidor MCP para pensamento sequencial integrado com OmniMind."""

    def __init__(
        self,
        workspace: Optional[Any] = None,  # SharedWorkspace
        narrative_history: Optional[Any] = None,  # NarrativeHistory
        systemic_memory: Optional[Any] = None,  # SystemicMemoryTrace
        embedding_dim: int = 256,
    ) -> None:
        """Inicializa o servidor de pensamento MCP integrado.

        Args:
            workspace: Instância opcional de SharedWorkspace para integração
            narrative_history: Instância opcional de NarrativeHistory para narrativas retroativas
            systemic_memory: Instância opcional de SystemicMemoryTrace para deformações topológicas
            embedding_dim: Dimensão dos embeddings (deve corresponder ao workspace)
        """
        super().__init__()

        # Initialize cache
        self.cache = get_mcp_cache()

        # Armazenamento em memória
        self._sessions: Dict[str, ThinkingSession] = {}
        self._session_counter = 0

        # Componentes integrados (opcionais)
        self.workspace = workspace
        self.narrative_history = narrative_history
        self.systemic_memory = systemic_memory
        self.embedding_dim = embedding_dim

        # Embedding model simples (fallback hash-based)
        self._embedding_model: Optional[Any] = None
        self._init_embedding_model()

        # PsiProducer para cálculo de Ψ (Deleuze)
        self._psi_producer: Optional[Any] = None
        self._init_psi_producer()

        # UnconsciousStructuralEffectMeasurer para efeito estrutural
        self._structural_measurer: Optional[Any] = None
        self._init_structural_measurer()

        # ModuleMetricsCollector para persistência de métricas
        self._metrics_collector: Optional[Any] = None
        self._init_metrics_collector()

        # SigmaSinthomeCalculator para cálculo de σ (Lacan)
        self._sigma_calculator: Optional[Any] = None

        # Registrar métodos MCP
        self._methods.update(
            {
                "start_session": self.start_session,
                "add_step": self.add_step,
                "get_history": self.get_history,
                "branch_thinking": self.branch_thinking,
                "merge_branches": self.merge_branches,
                "evaluate_quality": self.evaluate_quality,
                "export_chain": self.export_chain,
                "resume_session": self.resume_session,
            }
        )

        logger.info(
            "ThinkingMCPServer inicializado (workspace=%s, narrative=%s, systemic=%s)",
            "✅" if workspace else "❌",
            "✅" if narrative_history else "❌",
            "✅" if systemic_memory else "❌",
        )

    def _init_embedding_model(self) -> None:
        """Inicializa modelo de embedding (lazy, com fallback robusto)."""
        try:
            from sentence_transformers import SentenceTransformer

            from src.utils.device_utils import get_sentence_transformer_device

            device = get_sentence_transformer_device()
            self._embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
            logger.debug(f"Modelo de embedding carregado: all-MiniLM-L6-v2 (device={device})")
        except ImportError:
            logger.debug("SentenceTransformer não disponível, usando fallback hash-based")
            self._embedding_model = None
        except (AttributeError, KeyError, Exception) as e:
            # Tratar erros de incompatibilidade de versão, cache corrompido, etc.
            logger.warning(
                "Erro ao carregar modelo de embedding (incompatibilidade/cache corrompido): %s. "
                "Usando fallback hash-based",
                e,
            )
            self._embedding_model = None

    def _init_psi_producer(self) -> None:
        """Inicializa PsiProducer para cálculo de Ψ."""
        try:
            from src.consciousness.psi_producer import PsiProducer
            from src.embeddings.code_embeddings import OmniMindEmbeddings

            # Criar OmniMindEmbeddings se não fornecido
            embedding_model = None
            if self._embedding_model:
                try:
                    embedding_model = OmniMindEmbeddings(model=self._embedding_model)
                except Exception:
                    pass

            self._psi_producer = PsiProducer(embedding_model=embedding_model)
            logger.debug("PsiProducer inicializado")
        except ImportError as e:
            logger.warning("PsiProducer não disponível: %s", e)
            self._psi_producer = None

    def _init_structural_measurer(self) -> None:
        """Inicializa UnconsciousStructuralEffectMeasurer."""
        try:
            from src.consciousness.unconscious_structural_effect import (
                UnconsciousStructuralEffectMeasurer,
            )

            self._structural_measurer = UnconsciousStructuralEffectMeasurer()
            logger.debug("UnconsciousStructuralEffectMeasurer inicializado")
        except ImportError as e:
            logger.warning("UnconsciousStructuralEffectMeasurer não disponível: %s", e)
            self._structural_measurer = None

    def _init_metrics_collector(self) -> None:
        """Inicializa ModuleMetricsCollector."""
        try:
            from src.consciousness.metrics import ModuleMetricsCollector

            self._metrics_collector = ModuleMetricsCollector()
            logger.debug("ModuleMetricsCollector inicializado")
        except ImportError as e:
            logger.warning("ModuleMetricsCollector não disponível: %s", e)
            self._metrics_collector = None

    def _generate_embedding(self, text: str) -> np.ndarray:
        """Gera embedding para texto (com fallback hash-based)."""
        if self._embedding_model:
            try:
                encoded = self._embedding_model.encode(text, normalize_embeddings=True)
                # Truncar/expandir para embedding_dim
                if len(encoded) > self.embedding_dim:
                    return encoded[: self.embedding_dim]
                elif len(encoded) < self.embedding_dim:
                    padding = np.zeros(self.embedding_dim - len(encoded))
                    return np.concatenate([encoded, padding])
                return encoded
            except Exception as e:
                logger.warning("Erro ao gerar embedding com modelo: %s, usando fallback", e)

        # Fallback hash-based
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        embedding = np.zeros(self.embedding_dim)
        for i in range(self.embedding_dim):
            byte_val = hash_bytes[i % len(hash_bytes)]
            embedding[i] = (byte_val / 255.0) * 2 - 1
        return embedding

    def start_session(self, goal: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Inicia uma nova sessão de pensamento.

        Integra com SharedWorkspace: Sessão = módulo.

        Args:
            goal: Objetivo da sessão de pensamento
            metadata: Metadados opcionais da sessão

        Returns:
            Informações da sessão criada
        """
        try:
            session_id = f"think_{uuid.uuid4().hex[:12]}"
            session = ThinkingSession(
                session_id=session_id,
                goal=goal,
                metadata=metadata or {},
            )

            self._sessions[session_id] = session
            self._session_counter += 1

            # INTEGRAÇÃO: Registrar sessão como módulo no SharedWorkspace
            if self.workspace:
                try:
                    # Criar embedding do goal
                    goal_embedding = self._generate_embedding(goal)
                    # Garantir dimensão correta
                    if goal_embedding.shape[0] != self.workspace.embedding_dim:
                        # Redimensionar se necessário
                        if goal_embedding.shape[0] < self.workspace.embedding_dim:
                            padding = np.zeros(
                                self.workspace.embedding_dim - goal_embedding.shape[0]
                            )
                            goal_embedding = np.concatenate([goal_embedding, padding])
                        else:
                            goal_embedding = goal_embedding[: self.workspace.embedding_dim]

                    module_name = f"thinking_session_{session_id}"
                    self.workspace.write_module_state(
                        module_name=module_name,
                        embedding=goal_embedding,
                        metadata={
                            "goal": goal,
                            "session_id": session_id,
                            "created_at": session.created_at.isoformat(),
                            **(metadata or {}),
                        },
                    )
                    logger.debug("Sessão registrada no SharedWorkspace: %s", module_name)
                except Exception as e:
                    logger.warning("Erro ao registrar sessão no workspace: %s", e)

            logger.info("Nova sessão de pensamento criada: %s (goal: %s)", session_id, goal[:50])

            return {
                "session_id": session_id,
                "goal": goal,
                "created_at": session.created_at.isoformat(),
                "status": session.status,
            }
        except Exception as e:
            logger.error("Erro ao criar sessão de pensamento: %s", e)
            raise

    def add_step(
        self,
        session_id: str,
        content: str,
        step_type: str = "thought",
        metadata: Optional[Dict[str, Any]] = None,
        parent_step_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Adiciona um passo à sessão de pensamento.

        Integra com:
        - SharedWorkspace: Passo = evento (via symbolic_register)
        - NarrativeHistory: Passo = evento sem significado (Lacaniano)
        - SystemicMemoryTrace: Passo = marca topológica

        Args:
            session_id: ID da sessão
            content: Conteúdo do passo
            step_type: Tipo do passo ("observation", "thought", "action", "result")
            metadata: Metadados opcionais
            parent_step_id: ID do passo pai (para branching)

        Returns:
            Informações do passo criado
        """
        try:
            # Check cache first
            cache_key = f"think_step_{session_id}_{content[:50]}"
            try:
                if hasattr(self.cache, "_get_sync"):
                    cached_result = self.cache._get_sync(cache_key)
                    if cached_result:
                        return cached_result
            except Exception:
                pass

            if session_id not in self._sessions:
                raise ValueError(f"Sessão não encontrada: {session_id}")

            session = self._sessions[session_id]

            if session.status != "active":
                raise ValueError(f"Sessão não está ativa: {session.status}")

            step_id = f"step_{uuid.uuid4().hex[:12]}"
            step = ThinkingStep(
                step_id=step_id,
                session_id=session_id,
                content=content,
                step_type=step_type,
                metadata=metadata or {},
                parent_step_id=parent_step_id,
            )

            session.steps.append(step)
            session.updated_at = datetime.now()

            # INTEGRAÇÃO 1: SharedWorkspace - Logar passo como evento simbólico
            if self.workspace:
                try:
                    # Criar embedding do passo
                    step_embedding = self._generate_embedding(content)
                    if step_embedding.shape[0] != self.workspace.embedding_dim:
                        if step_embedding.shape[0] < self.workspace.embedding_dim:
                            padding = np.zeros(
                                self.workspace.embedding_dim - step_embedding.shape[0]
                            )
                            step_embedding = np.concatenate([step_embedding, padding])
                        else:
                            step_embedding = step_embedding[: self.workspace.embedding_dim]

                    # Usar symbolic_register para logar evento
                    if hasattr(self.workspace, "symbolic_register"):
                        self.workspace.symbolic_register.send_symbolic_message(
                            sender=f"thinking_session_{session_id}",
                            receiver="narrative",
                            symbolic_content={
                                "step_id": step_id,
                                "content": content,
                                "step_type": step_type,
                                "timestamp": step.timestamp.isoformat(),
                            },
                            priority=1,
                            nachtraglichkeit=True,  # Lacaniano: significado retroativo
                        )
                except Exception as e:
                    logger.warning("Erro ao logar passo no workspace: %s", e)

            # INTEGRAÇÃO 2: NarrativeHistory - Inscrição sem significado (Lacaniano)
            if self.narrative_history:
                try:
                    self.narrative_history.inscribe_event(
                        event={
                            "task": f"thinking_step_{step_id}",
                            "action": step_type,
                            "result": content,
                            "metadata": {
                                "session_id": session_id,
                                "step_id": step_id,
                                "parent_step_id": parent_step_id,
                                **(metadata or {}),
                            },
                        },
                        without_meaning=True,  # Lacaniano: sem significado imediato
                    )
                    logger.debug("Passo inscrito no NarrativeHistory: %s", step_id)
                except Exception as e:
                    logger.warning("Erro ao inscrever passo no NarrativeHistory: %s", e)

            # INTEGRAÇÃO 3: SystemicMemoryTrace - Deformação topológica
            if self.systemic_memory:
                try:
                    # Criar embedding para deformação
                    step_embedding = self._generate_embedding(content)
                    if step_embedding.shape[0] != self.systemic_memory.state_space_dim:
                        if step_embedding.shape[0] < self.systemic_memory.state_space_dim:
                            padding = np.zeros(
                                self.systemic_memory.state_space_dim - step_embedding.shape[0]
                            )
                            step_embedding = np.concatenate([step_embedding, padding])
                        else:
                            step_embedding = step_embedding[: self.systemic_memory.state_space_dim]

                    # Obter estado anterior da sessão (se existir)
                    session_module = f"thinking_session_{session_id}"
                    if self.workspace and session_module in self.workspace.embeddings:
                        past_state = self.workspace.embeddings[session_module]
                        # Adicionar traço (deformação topológica)
                        self.systemic_memory.add_trace_not_memory(past_state, step_embedding)
                        logger.debug("Deformação topológica adicionada para passo: %s", step_id)
                except Exception as e:
                    logger.warning("Erro ao adicionar deformação topológica: %s", e)

            # INTEGRAÇÃO 4: Calcular Φ via SharedWorkspace
            if self.workspace:
                try:
                    # Atualizar estado da sessão no workspace
                    session_embedding = self._generate_embedding(
                        f"{session.goal} {' '.join([s.content[:50] for s in session.steps[-3:]])}"
                    )
                    if session_embedding.shape[0] != self.workspace.embedding_dim:
                        if session_embedding.shape[0] < self.workspace.embedding_dim:
                            padding = np.zeros(
                                self.workspace.embedding_dim - session_embedding.shape[0]
                            )
                            session_embedding = np.concatenate([session_embedding, padding])
                        else:
                            session_embedding = session_embedding[: self.workspace.embedding_dim]

                    module_name = f"thinking_session_{session_id}"
                    self.workspace.write_module_state(
                        module_name=module_name,
                        embedding=session_embedding,
                        metadata={
                            "goal": session.goal,
                            "total_steps": len(session.steps),
                            "last_step": step_id,
                        },
                    )

                    # Calcular Φ (IIT puro)
                    phi = self.workspace.compute_phi_from_integrations()
                    step.phi = phi
                    session.total_phi = phi
                    logger.debug("Φ calculado para passo: %.4f", phi)
                except Exception as e:
                    logger.warning("Erro ao calcular Φ: %s", e)
                    phi = 0.0
            else:
                phi = 0.0

            # INTEGRAÇÃO 5: Calcular Ψ (Deleuze) via PsiProducer
            psi_result = None
            if self._psi_producer:
                try:
                    # Coletar passos anteriores para contexto
                    previous_steps = [s.content for s in session.steps[:-1]]

                    # Coletar ações (se disponíveis no metadata)
                    actions = []
                    if metadata and "actions" in metadata:
                        actions = metadata["actions"]
                    elif step.metadata and "actions" in step.metadata:
                        actions = step.metadata["actions"]

                    # Calcular Ψ
                    # Converter actions para List[str] (esperado por calculate_psi_for_step)
                    actions_str = []
                    if actions:
                        for a in actions:
                            if isinstance(a, str):
                                actions_str.append(a)
                            elif isinstance(a, dict) and "action" in a:
                                actions_str.append(str(a["action"]))
                            else:
                                actions_str.append(str(a))

                    psi_result = self._psi_producer.calculate_psi_for_step(
                        step_content=content,
                        previous_steps=previous_steps,
                        goal=session.goal,
                        actions=actions_str,
                        step_id=step_id,
                    )

                    # Armazenar em ThinkingStep
                    step.psi_producer = psi_result.psi_raw
                    step.psi_norm = psi_result.psi_norm
                    step.psi_components = {
                        "innovation_score": psi_result.components.innovation_score,
                        "surprise_score": psi_result.components.surprise_score,
                        "relevance_score": psi_result.components.relevance_score,
                        "entropy_of_actions": psi_result.components.entropy_of_actions,
                    }

                    # Atualizar sessão
                    session.psi_history.append(psi_result.psi_norm)
                    session.total_psi = (
                        sum(session.psi_history) / len(session.psi_history)
                        if session.psi_history
                        else 0.0
                    )

                    logger.debug(
                        "Ψ calculado para passo: %.4f (norm: %.4f)",
                        step.psi_producer,
                        step.psi_norm,
                    )

                    # Registrar em ModuleMetricsCollector
                    if self._metrics_collector:
                        self._metrics_collector.record_psi(
                            step_id=step_id,
                            psi_raw=psi_result.psi_raw,
                            psi_norm=psi_result.psi_norm,
                            innovation_score=psi_result.components.innovation_score,
                            surprise_score=psi_result.components.surprise_score,
                            relevance_score=psi_result.components.relevance_score,
                            entropy_of_actions=psi_result.components.entropy_of_actions,
                        )
                except Exception as e:
                    logger.warning("Erro ao calcular Ψ: %s", e)

            # INTEGRAÇÃO 6: Calcular σ (Lacan) via SigmaSinthomeCalculator
            sigma_result = None
            if self.workspace:
                try:
                    from src.consciousness.sigma_sinthome import SigmaSinthomeCalculator

                    # Coletar histórico de Φ (últimos 10 passos)
                    phi_history = [s.phi for s in session.steps[-10:]] if session.steps else [phi]

                    # Criar calculador (lazy initialization)
                    if not hasattr(self, "_sigma_calculator") or self._sigma_calculator is None:
                        # IntegrationTrainer pode não estar disponível aqui
                        # Usar apenas workspace
                        self._sigma_calculator = SigmaSinthomeCalculator(
                            integration_trainer=None, workspace=self.workspace
                        )

                    # Calcular σ para o ciclo atual
                    cycle_id = f"cycle_{session_id}_{len(session.steps)}"
                    sigma_result = self._sigma_calculator.calculate_sigma_for_cycle(
                        cycle_id=cycle_id,
                        phi_history=phi_history,
                        contributing_steps=[step_id],
                    )

                    # Armazenar σ no metadata do passo (para uso futuro)
                    step.metadata["sigma_value"] = sigma_result.sigma_value
                    step.metadata["sinthome_detected"] = sigma_result.components.sinthome_detected

                    logger.debug(
                        (
                            "σ calculado para passo: %.4f "
                            "(removability=%.4f, stability=%.4f, flexibility=%.4f)"
                        ),
                        sigma_result.sigma_value,
                        sigma_result.components.removability_score,
                        sigma_result.components.stability_score,
                        sigma_result.components.flexibility_score,
                    )

                    # Registrar em ModuleMetricsCollector
                    if self._metrics_collector:
                        self._metrics_collector.record_sigma(
                            cycle_id=cycle_id,
                            sigma_value=sigma_result.sigma_value,
                            sinthome_detected=sigma_result.components.sinthome_detected,
                            contributing_steps=[step_id],
                        )
                except Exception as e:
                    logger.warning("Erro ao calcular σ: %s", e)
                    sigma_result = None

            # INTEGRAÇÃO 7: Registrar estado para efeito estrutural
            if self._structural_measurer:
                try:
                    # Usar σ calculado ou default
                    sigma = sigma_result.sigma_value if sigma_result else 0.5  # Default neutro

                    # Registrar estado (Φ, Ψ, σ)
                    self._structural_measurer.record_state(
                        phi=phi,
                        psi=step.psi_norm if psi_result else 0.0,
                        sigma=sigma,
                    )

                    # Avaliar efeito estrutural a cada 10 passos
                    if len(session.steps) % 10 == 0:
                        report = self._structural_measurer.compute_structural_effect_report()
                        diagnosis = self._structural_measurer.diagnose()
                        logger.info(
                            "Efeito estrutural: %s (Δ=%.3f, efficiency=%.1%%)",
                            diagnosis,
                            report.despotentialization,
                            report.efficiency,
                        )
                except Exception as e:
                    logger.warning("Erro ao registrar efeito estrutural: %s", e)

            # Registrar Φ, Ψ, σ em ModuleMetricsCollector
            if self._metrics_collector:
                try:
                    sigma_value = sigma_result.sigma_value if sigma_result else 0.5
                    self._metrics_collector.record_consciousness_state(
                        phi=phi,
                        psi=step.psi_norm if psi_result else 0.0,
                        sigma=sigma_value,
                        step_id=step_id,
                    )
                    logger.debug(
                        "✅ Métricas de consciência registradas: Φ=%.4f, Ψ=%.4f, σ=%.4f",
                        phi,
                        step.psi_norm if psi_result else 0.0,
                        sigma_value,
                    )
                except Exception as e:
                    logger.warning("Erro ao registrar estado de consciência: %s", e)

            # Calcular qualidade do passo
            step.quality_score = self._calculate_step_quality(step, session)

            logger.debug(
                "Passo adicionado à sessão %s: %s (type: %s, Φ: %.4f, Ψ: %.4f, quality: %.4f)",
                session_id,
                step_id,
                step_type,
                step.phi,
                step.psi_norm,
                step.quality_score,
            )

            return {
                "step_id": step_id,
                "session_id": session_id,
                "step_type": step_type,
                "timestamp": step.timestamp.isoformat(),
                "step_index": len(session.steps) - 1,
                "phi": round(step.phi, 4),
                "psi_producer": round(step.psi_producer, 4),
                "psi_norm": round(step.psi_norm, 4),
                "quality_score": round(step.quality_score, 4),
            }
        except Exception as e:
            logger.error("Erro ao adicionar passo: %s", e)
            raise

    def _calculate_step_quality(self, step: ThinkingStep, session: ThinkingSession) -> float:
        """Calcula score de qualidade do passo."""
        score = 0.0

        # Baseado em Φ
        score += min(step.phi * 0.4, 0.4)

        # Baseado em comprimento (conteúdo substancial)
        content_score = min(len(step.content) / 200.0, 0.3)
        score += content_score

        # Baseado em diversidade de tipos
        if session.steps:
            type_diversity = len(set(s.step_type for s in session.steps)) / max(
                len(session.steps), 1
            )
            score += type_diversity * 0.3

        return min(score, 1.0)

    def get_history(self, session_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Recupera o histórico de uma sessão de pensamento.

        Args:
            session_id: ID da sessão
            limit: Limite de passos a retornar (None = todos)

        Returns:
            Histórico da sessão
        """
        try:
            if session_id not in self._sessions:
                raise ValueError(f"Sessão não encontrada: {session_id}")

            session = self._sessions[session_id]
            steps = session.steps

            if limit is not None and limit > 0:
                steps = steps[-limit:]

            return {
                "session_id": session_id,
                "goal": session.goal,
                "status": session.status,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "total_steps": len(session.steps),
                "total_phi": round(session.total_phi, 4),
                "total_psi": round(session.total_psi, 4),
                "steps": [
                    {
                        "step_id": step.step_id,
                        "content": step.content,
                        "step_type": step.step_type,
                        "timestamp": step.timestamp.isoformat(),
                        "metadata": step.metadata,
                        "parent_step_id": step.parent_step_id,
                        "phi": round(step.phi, 4),
                        "quality_score": round(step.quality_score, 4),
                    }
                    for step in steps
                ],
            }
        except Exception as e:
            logger.error("Erro ao recuperar histórico: %s", e)
            raise

    def branch_thinking(
        self, session_id: str, step_id: str, goal: Optional[str] = None
    ) -> Dict[str, Any]:
        """Cria um branch (ramificação) de pensamento a partir de um passo.

        Args:
            session_id: ID da sessão original
            step_id: ID do passo a partir do qual fazer branch
            goal: Novo objetivo para o branch (opcional)

        Returns:
            Informações da nova sessão (branch)
        """
        try:
            if session_id not in self._sessions:
                raise ValueError(f"Sessão não encontrada: {session_id}")

            parent_session = self._sessions[session_id]

            # Encontrar o passo
            step = None
            for s in parent_session.steps:
                if s.step_id == step_id:
                    step = s
                    break

            if step is None:
                raise ValueError(f"Passo não encontrado: {step_id}")

            # Criar nova sessão como branch
            new_session_id = f"think_{uuid.uuid4().hex[:12]}"
            new_goal = goal or f"Branch from {parent_session.goal}"

            branch_session = ThinkingSession(
                session_id=new_session_id,
                goal=new_goal,
                parent_session_id=session_id,
                metadata={
                    "branch_from_step": step_id,
                    "branch_from_session": session_id,
                },
            )

            # Copiar passos até o ponto de branch (incluindo o passo de branch)
            for s in parent_session.steps:
                if s.step_id == step_id:
                    # Incluir o passo original como primeiro passo do branch
                    original_step_copy = ThinkingStep(
                        step_id=s.step_id,  # Manter mesmo ID para rastreabilidade
                        session_id=new_session_id,  # Atualizar session_id
                        content=s.content,
                        step_type=s.step_type,
                        timestamp=s.timestamp,
                        metadata={**s.metadata, "branch_origin": True},
                        parent_step_id=s.parent_step_id,
                        phi=s.phi,
                        quality_score=s.quality_score,
                        psi_producer=s.psi_producer,
                        psi_norm=s.psi_norm,
                        psi_components=s.psi_components,
                    )
                    branch_session.steps.append(original_step_copy)
                    break
                branch_session.steps.append(s)

            # Adicionar o passo de registro do branch como segundo passo
            branch_step = ThinkingStep(
                step_id=f"step_{uuid.uuid4().hex[:12]}",
                session_id=new_session_id,
                content=f"Branch from step {step_id}: {step.content[:100]}",
                step_type="thought",
                metadata={"branch_from": step_id, "branch_registration": True},
            )
            branch_session.steps.append(branch_step)

            self._sessions[new_session_id] = branch_session

            # Registrar branch no workspace
            if self.workspace:
                try:
                    goal_embedding = self._generate_embedding(new_goal)
                    if goal_embedding.shape[0] != self.workspace.embedding_dim:
                        if goal_embedding.shape[0] < self.workspace.embedding_dim:
                            padding = np.zeros(
                                self.workspace.embedding_dim - goal_embedding.shape[0]
                            )
                            goal_embedding = np.concatenate([goal_embedding, padding])
                        else:
                            goal_embedding = goal_embedding[: self.workspace.embedding_dim]

                    module_name = f"thinking_session_{new_session_id}"
                    self.workspace.write_module_state(
                        module_name=module_name,
                        embedding=goal_embedding,
                        metadata={
                            "goal": new_goal,
                            "session_id": new_session_id,
                            "parent_session": session_id,
                            "branch_from_step": step_id,
                        },
                    )
                except Exception as e:
                    logger.warning("Erro ao registrar branch no workspace: %s", e)

            logger.info(
                "Branch criado: %s a partir de %s (step: %s)",
                new_session_id,
                session_id,
                step_id,
            )

            return {
                "new_session_id": new_session_id,
                "parent_session": session_id,
                "branch_from_step": step_id,
                "goal": new_goal,
                "created_at": branch_session.created_at.isoformat(),
            }
        except Exception as e:
            logger.error("Erro ao criar branch: %s", e)
            raise

    def merge_branches(
        self, session_ids: List[str], merge_strategy: str = "sequential"
    ) -> Dict[str, Any]:
        """Mescla múltiplas sessões de pensamento.

        Args:
            session_ids: Lista de IDs de sessões para mesclar
            merge_strategy: Estratégia de merge ("sequential", "parallel", "weighted")

        Returns:
            Informações da sessão mesclada
        """
        try:
            if len(session_ids) < 2:
                raise ValueError("Precisa de pelo menos 2 sessões para mesclar")

            # Verificar que todas as sessões existem
            sessions_to_merge = []
            for sid in session_ids:
                if sid not in self._sessions:
                    raise ValueError(f"Sessão não encontrada: {sid}")
                sessions_to_merge.append(self._sessions[sid])

            # Criar nova sessão mesclada
            merged_session_id = f"think_{uuid.uuid4().hex[:12]}"
            merged_goal = f"Merged: {', '.join([s.goal[:30] for s in sessions_to_merge])}"

            merged_session = ThinkingSession(
                session_id=merged_session_id,
                goal=merged_goal,
                metadata={
                    "merged_from": session_ids,
                    "merge_strategy": merge_strategy,
                },
            )

            # Mesclar passos conforme estratégia
            if merge_strategy == "sequential":
                # Apenas concatenar passos em ordem
                for session in sessions_to_merge:
                    merged_session.steps.extend(session.steps)
            elif merge_strategy == "parallel":
                # Intercalar passos por timestamp
                all_steps: List[ThinkingStep] = []
                for session in sessions_to_merge:
                    all_steps.extend(session.steps)
                all_steps.sort(key=lambda s: s.timestamp)
                merged_session.steps = all_steps
            else:  # weighted ou default
                # Mesclar sequencialmente (padrão)
                for session in sessions_to_merge:
                    merged_session.steps.extend(session.steps)

            # Calcular Φ total mesclado
            if sessions_to_merge:
                merged_session.total_phi = sum(s.total_phi for s in sessions_to_merge) / len(
                    sessions_to_merge
                )

            self._sessions[merged_session_id] = merged_session

            # Registrar sessão mesclada no workspace
            if self.workspace:
                try:
                    goal_embedding = self._generate_embedding(merged_goal)
                    if goal_embedding.shape[0] != self.workspace.embedding_dim:
                        if goal_embedding.shape[0] < self.workspace.embedding_dim:
                            padding = np.zeros(
                                self.workspace.embedding_dim - goal_embedding.shape[0]
                            )
                            goal_embedding = np.concatenate([goal_embedding, padding])
                        else:
                            goal_embedding = goal_embedding[: self.workspace.embedding_dim]

                    module_name = f"thinking_session_{merged_session_id}"
                    self.workspace.write_module_state(
                        module_name=module_name,
                        embedding=goal_embedding,
                        metadata={
                            "goal": merged_goal,
                            "merged_from": session_ids,
                            "total_steps": len(merged_session.steps),
                            "total_phi": merged_session.total_phi,
                        },
                    )
                except Exception as e:
                    logger.warning("Erro ao registrar merge no workspace: %s", e)

            logger.info(
                "Sessões mescladas: %s criada a partir de %d sessões",
                merged_session_id,
                len(session_ids),
            )

            return {
                "merged_session_id": merged_session_id,
                "merged_from": session_ids,
                "total_steps": len(merged_session.steps),
                "total_phi": round(merged_session.total_phi, 4),
                "goal": merged_goal,
            }
        except Exception as e:
            logger.error("Erro ao mesclar branches: %s", e)
            raise

    def evaluate_quality(self, session_id: str) -> Dict[str, Any]:
        """Avalia a qualidade de uma sessão de pensamento.

        Args:
            session_id: ID da sessão

        Returns:
            Avaliação da qualidade
        """
        try:
            if session_id not in self._sessions:
                raise ValueError(f"Sessão não encontrada: {session_id}")

            session = self._sessions[session_id]

            # Métricas de qualidade
            total_steps = len(session.steps)
            step_types = [s.step_type for s in session.steps]

            # Diversidade de tipos de passos
            type_diversity = len(set(step_types)) / max(len(step_types), 1)

            # Comprimento médio dos passos
            avg_length = sum(len(s.content) for s in session.steps) / max(total_steps, 1)

            # Score baseado em métricas + Φ
            score = 0.0
            if total_steps > 0:
                score += min(total_steps / 10.0, 0.3)  # Até 30% por número de passos
                score += type_diversity * 0.2  # 20% por diversidade
                score += min(avg_length / 200.0, 0.2)  # 20% por comprimento médio
                score += min(session.total_phi, 0.3)  # 30% por Φ (integração)

            score = min(score, 1.0)

            # Feedback baseado no score
            if score >= 0.8:
                feedback = "Excelente pensamento sequencial com alta integração (Φ) e diversidade"
            elif score >= 0.6:
                feedback = "Bom pensamento sequencial, pode melhorar integração ou diversidade"
            elif score >= 0.4:
                feedback = "Pensamento básico, precisa mais passos, diversidade ou integração"
            else:
                feedback = "Pensamento muito simples, precisa desenvolvimento significativo"

            return {
                "session_id": session_id,
                "score": round(score, 3),
                "feedback": feedback,
                "metrics": {
                    "total_steps": total_steps,
                    "type_diversity": round(type_diversity, 3),
                    "avg_step_length": round(avg_length, 1),
                    "total_phi": round(session.total_phi, 4),
                    "step_types": dict((t, step_types.count(t)) for t in set(step_types)),
                },
            }
        except Exception as e:
            logger.error("Erro ao avaliar qualidade: %s", e)
            raise

    def export_chain(self, session_id: str, format: str = "json") -> Dict[str, Any]:
        """Exporta a cadeia de pensamento de uma sessão.

        Args:
            session_id: ID da sessão
            format: Formato de exportação ("json", "text", "markdown")

        Returns:
            Cadeia de pensamento exportada
        """
        try:
            if session_id not in self._sessions:
                raise ValueError(f"Sessão não encontrada: {session_id}")

            session = self._sessions[session_id]

            chain: Union[Dict[str, Any], str]
            if format == "json":
                chain = {
                    "session_id": session.session_id,
                    "goal": session.goal,
                    "created_at": session.created_at.isoformat(),
                    "total_phi": round(session.total_phi, 4),
                    "steps": [
                        {
                            "step_id": step.step_id,
                            "content": step.content,
                            "step_type": step.step_type,
                            "timestamp": step.timestamp.isoformat(),
                            "metadata": step.metadata,
                            "phi": round(step.phi, 4),
                            "quality_score": round(step.quality_score, 4),
                        }
                        for step in session.steps
                    ],
                }
            elif format == "text":
                lines = [
                    f"Goal: {session.goal}",
                    f"Session: {session.session_id}",
                    f"Total Φ: {session.total_phi:.4f}",
                    "",
                ]
                for i, step in enumerate(session.steps, 1):
                    lines.append(
                        f"{i}. [{step.step_type.upper()}] {step.content} (Φ: {step.phi:.4f})"
                    )
                chain = "\n".join(lines)
            elif format == "markdown":
                lines = [
                    f"# {session.goal}",
                    f"**Session ID:** {session.session_id}",
                    f"**Total Φ:** {session.total_phi:.4f}",
                    "",
                ]
                for i, step in enumerate(session.steps, 1):
                    lines.append(f"## Step {i}: {step.step_type} (Φ: {step.phi:.4f})")
                    lines.append(step.content)
                    lines.append("")
                chain = "\n".join(lines)
            else:
                raise ValueError(f"Formato não suportado: {format}")

            return {
                "session_id": session_id,
                "format": format,
                "chain": chain,
                "total_steps": len(session.steps),
            }
        except Exception as e:
            logger.error("Erro ao exportar cadeia: %s", e)
            raise

    def resume_session(self, session_id: str) -> Dict[str, Any]:
        """Retoma uma sessão de pensamento pausada.

        Args:
            session_id: ID da sessão

        Returns:
            Status da sessão retomada
        """
        try:
            if session_id not in self._sessions:
                raise ValueError(f"Sessão não encontrada: {session_id}")

            session = self._sessions[session_id]

            if session.status == "active":
                return {"status": "already_active", "session_id": session_id}

            session.status = "active"
            session.updated_at = datetime.now()

            logger.info("Sessão retomada: %s", session_id)

            return {
                "status": "resumed",
                "session_id": session_id,
                "updated_at": session.updated_at.isoformat(),
            }
        except Exception as e:
            logger.error("Erro ao retomar sessão: %s", e)
            raise


if __name__ == "__main__":
    server = ThinkingMCPServer()
    try:
        server.start()
        logger.info("Thinking MCPServer running...")
        if server._thread:
            server._thread.join()
    except KeyboardInterrupt:
        server.stop()
