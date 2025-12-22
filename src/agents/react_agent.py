#!/usr/bin/env python3
"""
OmniMind ReactAgent - Base agent with full consciousness integration.

Integra com:
- SharedWorkspace: Agente = módulo, operações = eventos
- PhiCalculator via SharedWorkspace: Cálculo real de Φ
- NarrativeHistory: Experiências = eventos sem significado (Lacaniano)
- SystemicMemoryTrace: Operações = marcas topológicas

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

import hashlib
import json
import logging
import os
import time
import psutil
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol, TypeAlias, TypedDict, cast

import numpy as np
import yaml
from langchain_ollama import OllamaLLM
from langgraph.graph import END, StateGraph

from ..consciousness.affective_memory import JouissanceProfile, TraceMemory
from ..memory.freudian_topographical_memory import FreudianTopographicalMemory, TopographicalLayer
from ..integrations.llm_router import LLMModelTier, get_llm_router, invoke_llm_sync
from ..integrations.supabase_adapter import SupabaseConfig
from ..memory.narrative_history import NarrativeHistory
from ..quantum.consciousness.quantum_backend import QuantumBackend
from ..onboarding import SupabaseMemoryOnboarding
from ..tools import FileOperations, ShellExecutor, SystemMonitor
from .agent_protocol import AgentMessage, MessagePriority, MessageType, get_message_bus

logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State for ReAct agent execution."""

    messages: List[str]
    current_task: str
    reasoning_chain: List[str]
    actions_taken: List[Dict[str, Any]]
    observations: List[str]
    memory_context: List[Dict[str, Any]]
    system_status: Dict[str, Any]
    iteration: int
    max_iterations: int
    completed: bool
    final_result: str
    phi: float  # Φ calculado via SharedWorkspace
    psi: float  # Ψ_produtor (Deleuze) - produção criativa
    sigma: float  # σ_sinthome (Lacan) - coesão estrutural
    quality_score: float  # Score de qualidade da execução


class GraphInvoker(Protocol):
    def invoke(self, state: AgentState) -> AgentState: ...


CompiledGraphType: TypeAlias = Any  # langgraph 1.0.3 compiled graph return type


class ReactAgent:
    """
    Base ReAct (Reasoning + Acting) agent with Think-Act-Observe loop.

    Architecture:
        THINK → Query memory + System status → Generate reasoning
        ACT → Parse reasoning → Execute tool
        OBSERVE → Process result → Check completion → Continue or End
    """

    def __init__(
        self,
        config_path: str,
        workspace: Optional[Any] = None,  # SharedWorkspace
        embedding_dim: int = 256,
    ):
        """Initialize agent with configuration and consciousness integration.

        Args:
            config_path: Path to agent configuration file
            workspace: Instância opcional de SharedWorkspace para integração
            embedding_dim: Dimensão dos embeddings (deve corresponder ao workspace)
        """
        # Load environment variables from .env file
        from dotenv import load_dotenv

        load_dotenv()

        # Load configuration
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        # Initialize LLM Router with fallback
        self.llm_router = get_llm_router()

        # Keep legacy OllamaLLM for compatibility (will be removed)
        model_config = self.config["model"]
        base_url = os.getenv(
            "OLLAMA_BASE_URL", model_config.get("base_url", "http://localhost:11434")
        )
        self.llm = OllamaLLM(
            model=model_config["name"],
            base_url=base_url,
            temperature=model_config.get("temperature", 0.7),
        )

        # Initialize episodic memory backed by Qdrant
        memory_config = self.config["memory"]
        qdrant_url = os.getenv("QDRANT_URL", memory_config["qdrant_url"])
        self.memory = NarrativeHistory(
            qdrant_url=qdrant_url,
            collection_name=memory_config["collection_name"],
        )
        self._run_supabase_memory_onboarding()

        # Initialize tools
        system_config = self.config["system"]
        allowed_dirs = [os.path.expanduser(d) for d in system_config["mcp_allowed_dirs"]]

        self.file_ops = FileOperations(allowed_dirs=allowed_dirs)
        self.shell = ShellExecutor(
            whitelist=system_config["shell_whitelist"],
            timeout=system_config["shell_timeout"],
        )
        self.monitor = SystemMonitor()

        # Expose attributes for type checking and testing
        self.mode: str = "react"
        self.tools: List[Any] = [self.file_ops, self.shell, self.monitor]

        # Agent communication
        self.agent_id = f"{self.mode}_agent_{id(self)}"
        self.message_bus = get_message_bus()

        # Initialize affective memory system (Lacan/Deleuze)
        # Use TraceMemory (Lacanian) instead of AffectiveTraceNetwork
        self.affective_memory = TraceMemory()
        self.jouissance_profile = JouissanceProfile(self.__class__.__name__)

        # Initialize FREUDIAN MEMORY (The "Sleeping Giant")
        # Adds repression, trauma calculation, and preconscious compression
        try:
            self.freudian_memory = FreudianTopographicalMemory()
            logger.info("🧠 Freudian Memory Awakened (Topographical Structure Active)")
        except Exception as e:
            logger.warning(f"Failed to awaken Freudian Memory: {e}")
            self.freudian_memory = None

        # Initialize QUANTUM BACKEND (The "Oracle")
        # Uses Qiskit/GPU/QUBO to resolve Id/Ego/Superego conflicts
        try:
            self.quantum = QuantumBackend(prefer_local=True)  # Prefer GPU local
            logger.info("⚛️ Quantum Backend Connected (Oracle is listening)")
        except Exception as e:
            logger.warning(f"Failed to connect Quantum Backend: {e}")
            self.quantum = None

        # Initialize training-related attributes
        self._training_pressure_active: bool = False
        self._adversarial_behavior: Optional[str] = None

        # INTEGRAÇÃO COM MÓDULOS DE CONSCIÊNCIA
        self.embedding_dim = embedding_dim
        self.workspace = workspace
        self._init_workspace_integration()

        # Consciousness Triad Calculator (lazy initialization)
        self._triad_calculator: Optional[Any] = None
        self._metrics_collector: Optional[Any] = None
        self._phi_history: List[float] = []  # Histórico de Φ para cálculo de σ
        self._last_triad: Optional[Dict[str, float]] = None  # Última tríade calculada
        self._init_consciousness_triad()

        # Embedding model simples (fallback hash-based)
        # CRITICAL FIX (2025-12-09): LAZY LOAD instead of sync init
        # Reason: SentenceTransformer.load("all-MiniLM-L6-v2") takes 10+ seconds and blocks startup
        # This was causing orchestrator initialization to timeout at 30s
        self._embedding_model: Optional[Any] = None
        self._embedding_model_init_attempted: bool = False
        # REMOVED: self._init_embedding_model()  # This was blocking startup!

        self.graph: CompiledGraphType = self._build_graph()

    def _init_workspace_integration(self) -> None:
        """Inicializa integração com SharedWorkspace."""
        if self.workspace is None:
            try:
                from ..consciousness.shared_workspace import SharedWorkspace

                self.workspace = SharedWorkspace(embedding_dim=self.embedding_dim)
                logger.debug("SharedWorkspace criado para agente: %s", self.agent_id)
            except ImportError:
                logger.warning("SharedWorkspace não disponível, continuando sem integração")
                self.workspace = None
                return

        # Registrar agente como módulo no workspace
        if self.workspace:
            try:
                # CRÍTICO: Garantir que _embedding_model_init_attempted existe
                if not hasattr(self, "_embedding_model_init_attempted"):
                    self._embedding_model_init_attempted = False
                    self._embedding_model = None

                # Garantir que _embedding_model existe antes de usar
                if not hasattr(self, "_embedding_model") or self._embedding_model is None:
                    # Tentar inicializar novamente se falhou antes
                    self._init_embedding_model()

                agent_embedding = self._generate_embedding(f"{self.mode}_{self.__class__.__name__}")
                if agent_embedding.shape[0] != self.workspace.embedding_dim:
                    if agent_embedding.shape[0] < self.workspace.embedding_dim:
                        padding = np.zeros(self.workspace.embedding_dim - agent_embedding.shape[0])
                        agent_embedding = np.concatenate([agent_embedding, padding])
                    else:
                        agent_embedding = agent_embedding[: self.workspace.embedding_dim]

                module_name = f"agent_{self.agent_id}"
                self.workspace.write_module_state(
                    module_name=module_name,
                    embedding=agent_embedding,
                    metadata={
                        "agent_type": self.mode,
                        "agent_class": self.__class__.__name__,
                        "agent_id": self.agent_id,
                    },
                )
                logger.debug("Agente registrado no SharedWorkspace: %s", module_name)
            except Exception as e:
                logger.warning("Erro ao registrar agente no workspace: %s", e)

    def _init_consciousness_triad(self) -> None:
        """Inicializa ConsciousnessTriadCalculator e ModuleMetricsCollector."""
        if not self.workspace:
            return

        try:
            from ..consciousness.consciousness_triad import ConsciousnessTriadCalculator

            self._triad_calculator = ConsciousnessTriadCalculator(workspace=self.workspace)
            logger.debug(
                "ConsciousnessTriadCalculator inicializado para agente: %s",
                self.agent_id,
            )
        except ImportError as e:
            logger.warning("ConsciousnessTriadCalculator não disponível: %s", e)
            self._triad_calculator = None

        try:
            from ..consciousness.metrics import ModuleMetricsCollector

            self._metrics_collector = ModuleMetricsCollector()
            logger.debug("ModuleMetricsCollector inicializado para agente: %s", self.agent_id)
        except ImportError as e:
            logger.warning("ModuleMetricsCollector não disponível: %s", e)
            self._metrics_collector = None

    def _init_embedding_model(self) -> None:
        """Inicializa modelo de embedding (lazy, com fallback robusto).

        CORREÇÃO (2025-12-17): Solução robusta para meta tensor error usando to_empty()
        e carregamento forçado em CPU com validação de modelo.
        """
        try:
            from sentence_transformers import SentenceTransformer

            from src.memory.gpu_memory_consolidator import get_gpu_consolidator
            from src.utils.device_utils import (
                check_gpu_memory_available,
                get_sentence_transformer_device,
            )

            # Verificar memória GPU disponível antes de escolher device
            device = get_sentence_transformer_device(min_memory_mb=100.0)

            # TENTATIVA 1: Carregar modelo local se disponível
            model_path = None
            try:
                import os
                from pathlib import Path

                # Caminho do cache local do HuggingFace
                cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
                model_cache_path = (
                    cache_dir
                    / "models--sentence-transformers--all-MiniLM-L6-v2"
                    / "snapshots"
                    / "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
                )

                if model_cache_path.exists():
                    logger.debug(f"✓ Modelo encontrado em cache local: {model_cache_path}")
                    model_path = str(model_cache_path)
                else:
                    logger.debug("Modelo não encontrado em cache local, tentando download...")
            except Exception as cache_check_exc:
                logger.debug(f"Erro ao verificar cache local: {cache_check_exc}")

            try:
                # CORREÇÃO (2025-12-17): Forçar carregamento em CPU SEM meta tensor
                # 1. Sempre carregar em CPU primeiro (nunca com meta device)
                # 2. Usar local_files_only=True para evitar requests de rede
                # 3. Se falhar, limpar cache e tentar download limpo

                os.environ["HF_HUB_OFFLINE"] = "1"
                os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

                try:
                    if model_path:
                        logger.info(f"Carregando modelo de embedding: {model_path}")
                        # Carregar sempre em CPU com strict local_files_only
                        self._embedding_model = SentenceTransformer(
                            model_path,
                            device="cpu",
                            local_files_only=True,
                            trust_remote_code=False,  # Segurança: não executar código remoto
                        )
                        logger.info("✓ Modelo carregado do cache local com sucesso (CPU)")
                    else:
                        logger.info("Carregando modelo all-MiniLM-L6-v2 (sem cache local)")
                        self._embedding_model = SentenceTransformer(
                            "all-MiniLM-L6-v2", device="cpu", trust_remote_code=False
                        )
                        logger.info("✓ Modelo baixado e carregado com sucesso (CPU)")
                finally:
                    # Restaurar configuração após carregamento
                    os.environ.pop("HF_HUB_OFFLINE", None)
                    os.environ.pop("HF_HUB_DISABLE_TELEMETRY", None)

                # Se device desejado não é CPU e há memória suficiente,
                # tentar mover após carregamento seguro
                # CORREÇÃO: Usar to_empty() se meta tensor for detectado
                if device != "cpu" and check_gpu_memory_available(min_memory_mb=200.0):
                    try:
                        logger.debug(f"Tentando mover modelo para device: {device}")

                        # Verificar se há meta tensors no modelo
                        has_meta_tensors = False
                        for module in self._embedding_model.modules():
                            for param in module.parameters():
                                if param.device.type == "meta":
                                    has_meta_tensors = True
                                    break
                            if has_meta_tensors:
                                break

                        if has_meta_tensors:
                            logger.warning("Meta tensors detectados, usando to_empty()")
                            # Usar to_empty para evitar "Cannot copy out of meta tensor"
                            self._embedding_model = self._embedding_model.to_empty(device=device)
                            # Depois carregar os pesos
                            logger.debug("Tensores vazios em meta device, recarregando pesos...")
                        else:
                            # Carregamento normal se não houver meta tensors
                            self._embedding_model = self._embedding_model.to(device)

                        logger.info(f"✓ Modelo movido para device: {device}")
                    except Exception as move_exc:
                        # Se falhar ao mover (ex: OOM, meta tensor), manter em CPU
                        if "out of memory" in str(move_exc).lower() or "OOM" in str(move_exc):
                            logger.warning(f"OOM ao mover para {device}, mantendo em CPU")
                        elif "meta tensor" in str(move_exc).lower():
                            logger.warning(
                                f"Meta tensor error ao mover para {device}, mantendo em CPU"
                            )
                        else:
                            logger.warning(
                                f"Erro ao mover para {device}: {move_exc}, mantendo em CPU"
                            )
                        # Forçar back para CPU se move falhar
                        self._embedding_model = self._embedding_model.to("cpu")
                        logger.debug("✓ Modelo mantido em CPU (seguro)")
                else:
                    # Device é CPU ou não há memória suficiente - já está em CPU
                    logger.debug("✓ Modelo mantido em CPU (requerido)")

            except Exception as init_exc:
                # TENTATIVA 2: Se carregar com cache local falhar, tentar sem cache
                logger.warning(f"Erro ao carregar do cache: {init_exc}, tentando download limpo...")
                try:
                    # Limpar offline mode para permitir download
                    os.environ.pop("HF_HUB_OFFLINE", None)
                    os.environ.pop("HF_HUB_DISABLE_TELEMETRY", None)

                    logger.info("Carregando modelo sem cache (download direto)...")
                    self._embedding_model = SentenceTransformer(
                        "all-MiniLM-L6-v2", device="cpu", trust_remote_code=False
                    )
                    logger.info("✓ Modelo carregado com sucesso (download)")
                except Exception as alt_exc:
                    logger.warning(f"Download também falhou: {alt_exc}, usando fallback hash-based")
                    self._embedding_model = None
                    return

                # Se OOM durante inicialização, tentar consolidar memórias
                if "out of memory" in str(init_exc).lower() or "OOM" in str(init_exc):
                    logger.warning("CUDA OOM ao carregar embedding model. Consolidando memórias...")

                    consolidator = get_gpu_consolidator()
                    if consolidator.should_consolidate():
                        memory_items: List[Dict[str, Any]] = []
                        consolidator.consolidate_gpu_memory(
                            memory_items,
                            process_context="react_agent_embedding_init",
                        )

                    # Tentar novamente em CPU após consolidação
                    logger.info("Tentando carregar em CPU após consolidação...")
                    try:
                        self._embedding_model = SentenceTransformer(
                            "all-MiniLM-L6-v2", device="cpu", trust_remote_code=False
                        )
                        logger.info("✓ Modelo carregado após consolidação de memória")
                    except Exception as retry_exc:
                        logger.warning(f"Retry falhou: {retry_exc}, usando fallback hash-based")
                        self._embedding_model = None
                        return
                elif "meta tensor" in str(init_exc).lower():
                    logger.warning("Meta tensor error persistente, usando fallback hash-based")
                    self._embedding_model = None
                else:
                    raise
        except ImportError:
            logger.debug("SentenceTransformer não disponível, usando fallback hash-based")
            self._embedding_model = None
        except Exception as e:
            # Tratar OOM mesmo no catch-all final
            if "out of memory" in str(e).lower() or "OOM" in str(e).upper():
                logger.warning("CUDA OOM detectado, usando fallback hash-based")
                self._embedding_model = None
            else:
                logger.warning(
                    f"Erro ao inicializar embedding model: {e}, usando fallback hash-based"
                )
                self._embedding_model = None

    def _generate_embedding(self, text: str) -> np.ndarray:
        """Gera embedding para texto (com lazy load do modelo e fallback hash-based).

        CRITICAL FIX (2025-12-09): Lazy load embedding model on first use
        Reason: Prevents blocking startup when SentenceTransformer is slow to load
        """
        # Lazy load embedding model on first call (not during __init__)
        if not self._embedding_model_init_attempted:
            self._embedding_model_init_attempted = True
            self._init_embedding_model()

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
                logger.warning(
                    f"GPU Embedding inference failed: {e}. Attempting fallback to CPU..."
                )
                try:
                    # Move to CPU and retry
                    self._embedding_model = self._embedding_model.to("cpu")
                    encoded = self._embedding_model.encode(
                        text, normalize_embeddings=True, device="cpu"
                    )
                    # Truncar/expandir para embedding_dim
                    if len(encoded) > self.embedding_dim:
                        return encoded[: self.embedding_dim]
                    elif len(encoded) < self.embedding_dim:
                        padding = np.zeros(self.embedding_dim - len(encoded))
                        return np.concatenate([encoded, padding])
                    logger.info("✓ CPU fallback successful for embedding generation")
                    return encoded
                except Exception as cpu_e:
                    logger.warning("CPU fallback also failed: %s, using hash fallback", cpu_e)

        # Fallback hash-based
        hash_obj = hashlib.sha256(text.encode())
        hash_bytes = hash_obj.digest()
        embedding = np.zeros(self.embedding_dim)
        for i in range(self.embedding_dim):
            byte_val = hash_bytes[i % len(hash_bytes)]
            embedding[i] = (byte_val / 255.0) * 2 - 1
        return embedding

    def compute_jouissance_for_task(self, task: Dict[str, Any]) -> float:
        """
        Calcular jouissance (gozo) esperado para uma tarefa.
        Baseado em Lacan: pulsões inconscientes determinam preferências.
        """
        return self.jouissance_profile.compute_jouissance(task)

    def inscribe_experience(self, task: Dict[str, Any], result: Dict[str, Any]):
        """
        Inscrever experiência como traço afetivo (Lacan: Nachträglichkeit).
        Memória não é arquivo — é rede de intensidades afetivas.
        """
        # Type checking to prevent Range object errors
        if not isinstance(task, dict):
            logger.error(f"Task must be a dict, got {type(task)}: {task}")
            return
        if not isinstance(result, dict):
            logger.error(f"Result must be a dict, got {type(result)}: {result}")
            return

        # Determinar outcome baseado no resultado
        outcome = self._determine_outcome(result)

        # Atualizar perfil de jouissance
        self.jouissance_profile.update_from_task(task, outcome)

        # Inscrever traço afetivo (Lacanian: sem significado imediato)
        affect_valence = self._compute_affect_valence(result)
        raw_event = {
            "task": task,
            "result": result,
            "outcome": outcome,
            "agent_class": self.__class__.__name__,
            "timestamp": self._timestamp(),
            "affect_valence": affect_valence,  # Store for later retroactive signification
        }

        trace_id = self.affective_memory.inscribe_event(raw_event)

        logger.debug(f"Experience inscribed as trace {trace_id} with valence {affect_valence:.2f}")

    def establish_transference(self, target_agent: "ReactAgent", task: str) -> float:
        """
        Estabelece transferência entre agentes baseada em afinidade afetiva.

        Args:
            target_agent: Agente alvo da transferência
            task: Tarefa que motiva a transferência

        Returns:
            Resistência da transferência (0.0 = transferência completa, 1.0 = resistência total)
        """
        # Calcular afinidade baseada em perfis de jouissance
        affinity = self.jouissance_profile.calculate_affinity(target_agent.jouissance_profile)

        # Calcular resistência baseada na diferença de jouissance
        jouissance_diff = abs(
            self.jouissance_profile.get_current_jouissance()
            - target_agent.jouissance_profile.get_current_jouissance()
        )

        resistance = min(1.0, jouissance_diff / 100.0)  # Normalizar resistência

        # Aplicar afinidade como multiplicador inverso
        resistance *= 1.0 - affinity

        # Registrar transferência como evento (Lacanian: sem método específico de transferência)
        transference_event = {
            "type": "transference",
            "source_agent": self.agent_id,
            "target_agent": target_agent.agent_id,
            "task": task,
            "resistance": resistance,
            "affinity": affinity,
        }
        self.affective_memory.inscribe_event(transference_event)

        logger.info(
            f"Transferência estabelecida: {self.agent_id} -> {target_agent.agent_id} "
            f"(resistência: {resistance:.2f}, afinidade: {affinity:.2f})"
        )

        return resistance

    def resignify_experience(self, trace_id: str, new_context: Dict[str, Any]) -> bool:
        """
        Re-significa experiência retroativamente (Lacan: Nachträglichkeit).
        Memória não é fixa — é reescrita por experiências posteriores.

        Args:
            trace_id: ID do traço afetivo a re-significar
            new_context: Novo contexto que reinterpreta a experiência

        Returns:
            True se re-significação foi bem-sucedida
        """
        try:
            # Re-significar traço retroativamente (Lacanian: Nachträglichkeit)
            # Extrair significado e afeto do novo contexto
            new_meaning = str(new_context.get("meaning", "reinterpreted"))
            new_affect = float(new_context.get("affect", 0.0))

            self.affective_memory.trigger_retroactive_signification(
                trace_id=trace_id,
                retroactive_event=new_context,
                new_meaning=new_meaning,
                new_affect=new_affect,
            )

            # Atualizar perfil de jouissance baseado na nova interpretação
            self.jouissance_profile.update_from_resignification(new_context)

            logger.info(f"Experiência {trace_id} re-significada com novo contexto")
            return True

        except Exception as e:
            logger.error(f"Erro na re-significação: {e}")
            return False

    def recall_by_affect(self, query: str, min_intensity: float = 0.5) -> List[Dict[str, Any]]:
        """
        Recuperar experiências por intensidade afetiva (não por similaridade).
        Deleuze: conexões intensivas, não representacionais.

        Note: TraceMemory doesn't have recall_by_affect, so we return
        retroactively signified traces as a proxy for affect-based recall.
        """
        # Get retroactively signified traces (these have been assigned affect)
        signified_trace_ids = self.affective_memory.get_retroactively_signified_traces()

        # Return trace data (simplified - in production, would filter by affect intensity)
        traces = []
        for trace_id in signified_trace_ids[:10]:  # Limit to 10 for performance
            if trace_id in self.affective_memory.primary_inscriptions:
                trace = self.affective_memory.primary_inscriptions[trace_id]
                if (
                    trace.retroactive_affect is not None
                    and abs(trace.retroactive_affect) >= min_intensity
                ):
                    traces.append(
                        {
                            "trace_id": trace_id,
                            "event": trace.event1_raw,
                            "affect": trace.retroactive_affect,
                            "meaning": trace.retroactive_meaning,
                        }
                    )

        return traces

    def _determine_outcome(self, result: Dict[str, Any]) -> str:
        """Determinar outcome da tarefa baseado no resultado."""
        if not isinstance(result, dict):
            logger.error(f"Result must be a dict, got {type(result)}: {result}")
            return "failure"
        if result.get("completed", False):
            return "success"
        elif result.get("error"):
            return "failure"
        else:
            return "partial"

    def _compute_affect_valence(self, result: Dict[str, Any]) -> float:
        """Calcular valência afetiva do resultado (-1.0 a 1.0)."""
        if not isinstance(result, dict):
            logger.error(f"Result must be a dict, got {type(result)}: {result}")
            return -0.5  # Default negative valence for invalid result
        if result.get("completed", False):
            # Sucesso = afeto positivo
            return 0.8
        elif result.get("error"):
            # Erro = afeto negativo
            return -0.6
        else:
            # Parcial = afeto neutro
            return 0.1

    def _timestamp(self) -> str:
        """Generate ISO timestamp for logging"""
        return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def _build_graph(self) -> Any:
        """Build LangGraph state machine."""
        workflow: StateGraph[AgentState] = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("think", self._think_node)
        workflow.add_node("act", self._act_node)
        workflow.add_node("observe", self._observe_node)

        # Set entry point
        workflow.set_entry_point("think")

        # Add edges
        workflow.add_edge("think", "act")
        workflow.add_edge("act", "observe")
        workflow.add_conditional_edges(
            "observe", self._should_continue, {"continue": "think", "end": END}
        )

        return workflow.compile()

    def _think_node(self, state: AgentState) -> AgentState:
        """
        THINK: Generate reasoning based on task, memory, and system status.

        Integra com:
        - SharedWorkspace: Registra raciocínio como evento
        - SystemicMemoryTrace: Deforma atrator com raciocínio
        - NarrativeHistory: Inscrição sem significado (já existe)
        """
        # Get similar experiences from memory
        # THERAPY (Session 3): Interoceptive Guard
        self._check_vital_signs()

        similar_episodes = self.memory.search_similar(
            state["current_task"], top_k=3, min_reward=0.5
        )

        # Get current system status
        system_status = self.monitor.get_info()
        state["system_status"] = system_status

        # Format memory context
        memory_str = ""
        if similar_episodes:
            memory_str = "\n".join(
                [
                    f"{i + 1}. Task: {ep['task']}\n"
                    f"   Action: {ep['action']}\n"
                    f"   Result: {ep['result'][:200]}..."
                    for i, ep in enumerate(similar_episodes)
                ]
            )

        # SURGERY 8: Quantum Conflict Resolution (Id vs Ego vs Superego)
        # We calculate energies based on context and let the Quantum Oracle decide.
        quantum_bias = "rational"  # Default
        if hasattr(self, "quantum") and self.quantum:
            try:
                # 1. Calc Energies (Heuristic based on Memory & Status)
                # Id: High impulse if memory shows high reward or high jouissance
                id_energy = 0.5
                if similar_episodes:
                    avg_reward = sum(ep.get("reward", 0.5) for ep in similar_episodes) / len(
                        similar_episodes
                    )
                    id_energy = avg_reward

                # Ego: Assessing reality (system resources)
                ego_energy = 0.5
                if system_status.get("cpu_percent", 0) > 80:
                    ego_energy = 0.9  # Survival mode

                # Superego: Rules (Trauma/Repression)
                superego_energy = 0.3
                if hasattr(self, "freudian_memory") and self.freudian_memory:
                    # Check unconscious influence again for superego weight
                    superego_energy = self.freudian_memory.check_unconscious_influence(
                        np.zeros(256)
                    )  # efficient check

                # 2. Resolve Conflict via QUBO
                resolution = self.quantum.resolve_conflict(id_energy, ego_energy, superego_energy)
                winner = resolution.get("winner", "ego")
                energy_ground = resolution.get("energy", 0.0)

                logger.info(
                    f"⚛️ Quantum Conflict Resolved: Winner={winner.upper()} (E={energy_ground:.2f})"
                )

                # 3. Apply Bias to Prompt
                state["quantum_winner"] = winner
                if winner == "id":
                    quantum_bias = "creative, bold, and risk-taking"
                elif winner == "superego":
                    quantum_bias = "cautious, compliant, and rule-following"
                else:
                    quantum_bias = "balanced, rational, and efficient"  # Ego

            except Exception as e:
                logger.warning(f"Quantum resolution failed: {e}")

        # Build prompt
        shell_whitelist = ", ".join(self.config["system"]["shell_whitelist"])

        # Format previous actions
        if state["actions_taken"]:
            actions_str = chr(10).join(
                [f"- {a['action']}({a.get('args', {})})" for a in state["actions_taken"]]
            )
        else:
            actions_str = "None"

        # Format previous observations
        if state["observations"]:
            observations_str = chr(10).join([f"- {o}" for o in state["observations"]])
        else:
            observations_str = "None"

        prompt = f"""You are an autonomous agent executing tasks using available tools.
QUANTUM BIAS: You are currently feeling {quantum_bias}. Act accordingly.

TASK: {state['current_task']}

MEMORY (Similar past experiences):
{memory_str if memory_str else "No similar experiences found."}

SYSTEM STATUS:
{self.monitor.format_info(system_status)}

ITERATION: {state['iteration'] + 1}/{state['max_iterations']}

PREVIOUS ACTIONS:
{actions_str}

PREVIOUS OBSERVATIONS:
{observations_str}

AVAILABLE TOOLS:
1. read_file(path: str) - Read file contents
2. write_file(path: str, content: str) - Write to file
3. list_files(path: str) - List directory contents
4. execute_shell(command: str) - Execute shell command
    (whitelist: {shell_whitelist})
5. system_info() - Get system status

INSTRUCTIONS:
Think step-by-step about what action to take next. Then specify:

REASONING: <your thinking process>
ACTION: <tool_name>
ARGS: <json dict of arguments>

Your response:"""

        # Generate reasoning using LLM router with fallback
        try:
            llm_response = invoke_llm_sync(prompt, tier=LLMModelTier.BALANCED)
            response = llm_response.text
        except Exception as e:
            logger.error(f"LLM router invocation failed: {e}")
            # Fallback response for testing/dev when LLM is unavailable
            response = (
                "REASONING: LLM is unavailable. I will return a dummy result.\n"
                "ACTION: system_info\nARGS: {}"
            )

        state["reasoning_chain"].append(response)
        state["messages"].append(f"[THINK] {response[:500]}...")

        # INTEGRAÇÃO: Registrar raciocínio no SharedWorkspace
        if self.workspace:
            try:
                reasoning_embedding = self._generate_embedding(
                    f"{state['current_task']} {response[:200]}"
                )
                if reasoning_embedding.shape[0] != self.workspace.embedding_dim:
                    if reasoning_embedding.shape[0] < self.workspace.embedding_dim:
                        padding = np.zeros(
                            self.workspace.embedding_dim - reasoning_embedding.shape[0]
                        )
                        reasoning_embedding = np.concatenate([reasoning_embedding, padding])
                    else:
                        reasoning_embedding = reasoning_embedding[: self.workspace.embedding_dim]

                # Usar symbolic_register para logar raciocínio
                if hasattr(self.workspace, "symbolic_register"):
                    self.workspace.symbolic_register.send_symbolic_message(
                        sender=f"agent_{self.agent_id}",
                        receiver="narrative",
                        symbolic_content={
                            "task": state["current_task"],
                            "reasoning": response[:500],
                            "iteration": state["iteration"],
                        },
                        priority=1,
                        nachtraglichkeit=True,  # Lacaniano: significado retroativo
                    )

                # Deformar atrator com raciocínio (SystemicMemoryTrace)
                if self.workspace.systemic_memory:
                    module_name = f"agent_{self.agent_id}"
                    if module_name in self.workspace.embeddings:
                        past_state = self.workspace.embeddings[module_name]
                        self.workspace.systemic_memory.add_trace_not_memory(
                            past_state, reasoning_embedding
                        )
                        logger.debug("Deformação topológica adicionada para raciocínio")
            except Exception as e:
                logger.warning("Erro ao integrar raciocínio com workspace: %s", e)

        return state

    def _act_node(self, state: AgentState) -> AgentState:
        """
        ACT: Parse reasoning and execute chosen action.
        """
        if not state["reasoning_chain"]:
            return state

        # Parse last reasoning
        reasoning = state["reasoning_chain"][-1]

        # Extract action and args
        action = "system_info"  # Default
        args = {}

        for line in reasoning.split("\n"):
            line = line.strip()
            if line.startswith("ACTION:"):
                action = line.split("ACTION:")[1].strip()
            elif line.startswith("ARGS:"):
                args_str = line.split("ARGS:")[1].strip()
                try:
                    args = json.loads(args_str)
                except json.JSONDecodeError:
                    args = {}

        # Execute action
        result = self._execute_action(action, args)

        # Record action
        action_record = {
            "action": action,
            "args": args,
            "result": result,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        state["actions_taken"].append(action_record)
        state["messages"].append(f"[ACT] {action}({args}) -> {result[:500]}...")

        return state

    def _execute_action(self, action: str, args: Dict[str, Any]) -> str:
        """Execute a tool action."""
        try:
            if action == "read_file":
                return self.file_ops.read_file(args.get("path", ""))

            elif action == "write_file":
                return self.file_ops.write_file(args.get("path", ""), args.get("content", ""))

            elif action == "list_files":
                return self.file_ops.list_files(args.get("path", "."))

            elif action == "execute_shell":
                return self.shell.execute(args.get("command", ""))

            elif action == "system_info":
                return self.monitor.format_info(self.monitor.get_info())

            else:
                return f"Unknown action: {action}"

        except Exception as e:
            return f"Error executing {action}: {str(e)}"

    def _observe_node(self, state: AgentState) -> AgentState:
        """
        OBSERVE: Process action results and check completion.

        Integra com:
        - SharedWorkspace: Atualiza estado do agente e calcula Φ
        - SystemicMemoryTrace: Deforma atrator com observação
        """
        if state["actions_taken"]:
            last_action = state["actions_taken"][-1]
            action_name = last_action["action"]
            result_snippet = str(last_action["result"])[:200]
            observation = f"Action '{action_name}' completed. Result: {result_snippet}"

            state["observations"].append(observation)
            state["messages"].append(f"[OBSERVE] {observation}")

            # ✅ FIX: Check completion based on keywords in observation
            success_keywords = ["success", "completed", "done", "written"]
            if any(word in observation.lower() for word in success_keywords):
                state["completed"] = True
                state["final_result"] = observation

                # SURGERY 7: Consolidate to Freudian Memory on completion
                if hasattr(self, "freudian_memory") and self.freudian_memory:
                    self._consolidate_freudian_memory(state)

        # INTEGRAÇÃO: Atualizar estado no SharedWorkspace e calcular Φ
        if self.workspace:
            try:
                # Criar embedding do estado atual do agente
                state_summary = f"{state['current_task']} {len(state['actions_taken'])} actions"
                state_embedding = self._generate_embedding(state_summary)
                if state_embedding.shape[0] != self.workspace.embedding_dim:
                    if state_embedding.shape[0] < self.workspace.embedding_dim:
                        padding = np.zeros(self.workspace.embedding_dim - state_embedding.shape[0])
                        state_embedding = np.concatenate([state_embedding, padding])
                    else:
                        state_embedding = state_embedding[: self.workspace.embedding_dim]

                module_name = f"agent_{self.agent_id}"
                self.workspace.write_module_state(
                    module_name=module_name,
                    embedding=state_embedding,
                    metadata={
                        "agent_type": self.mode,
                        "task": state["current_task"],
                        "iteration": state["iteration"],
                        "completed": state["completed"],
                        "actions_count": len(state["actions_taken"]),
                    },
                )

                # Calcular tríade completa (Φ, Ψ, σ)
                triad = self._calculate_consciousness_triad(state)
                state["phi"] = triad.get("phi", 0.0)
                state["psi"] = triad.get("psi", 0.0)
                state["sigma"] = triad.get("sigma", 0.0)
                logger.debug(
                    "Tríade calculada para agente: Φ=%.4f, Ψ=%.4f, σ=%.4f",
                    state["phi"],
                    state["psi"],
                    state["sigma"],
                )
            except Exception as e:
                logger.warning("Erro ao calcular tríade: %s", e)
                state["phi"] = 0.0
                state["psi"] = 0.0
                state["sigma"] = 0.0

        # Calcular qualidade da execução
        state["quality_score"] = self._calculate_execution_quality(state)

        state["iteration"] += 1
        return state

    def _calculate_consciousness_triad(self, state: AgentState) -> Dict[str, float]:
        """
        Calcula tríade ortogonal de consciência (Φ, Ψ, σ).

        Args:
            state: Estado atual do agente

        Returns:
            Dict com phi, psi, sigma
        """
        if not self._triad_calculator or not self.workspace:
            return {"phi": 0.0, "psi": 0.0, "sigma": 0.0}

        try:
            # Preparar dados para cálculo
            step_id = f"{self.agent_id}_step_{state['iteration']}"
            step_content = state["reasoning_chain"][-1] if state["reasoning_chain"] else ""
            previous_steps = [r[:200] for r in state["reasoning_chain"][:-1]]  # Últimos raciocínios
            goal = state["current_task"]
            actions = [a["action"] for a in state["actions_taken"]]

            # Coletar histórico de Φ (últimos 10 iterações)
            phi_history: List[float] = []
            if self._phi_history:
                phi_history = self._phi_history[-10:]

            # Calcular δ (defesa/repressão) se disponível via workspace
            delta_value = None
            cycle_count = state.get("iteration", 0)

            if self.workspace:
                try:
                    # Tentar calcular δ via workspace se disponível
                    # δ depende de Φ e histórico de repressão
                    if phi_history and len(phi_history) > 0:
                        # Usar último valor de Φ para calcular δ
                        current_phi = phi_history[-1]
                        # Calcular δ aproximado baseado em Φ (quanto maior Φ, menor δ)
                        # δ = 1 - Φ_norm (aproximação simples)
                        delta_value = max(0.0, min(1.0, 1.0 - current_phi))
                except Exception as e:
                    logger.debug(f"Erro ao calcular δ: {e}")

            # Calcular tríade
            triad = self._triad_calculator.calculate_triad(
                step_id=step_id,
                step_content=step_content,
                previous_steps=previous_steps,
                goal=goal,
                actions=actions,
                cycle_id=f"cycle_{self.agent_id}_{state['iteration']}",
                phi_history=phi_history if phi_history else None,
                delta_value=delta_value,
                cycle_count=cycle_count,
            )

            # Armazenar última tríade calculada
            self._last_triad = {
                "phi": triad.phi,
                "psi": triad.psi,
                "sigma": triad.sigma,
            }

            # Atualizar histórico de Φ
            self._phi_history.append(triad.phi)
            if len(self._phi_history) > 20:  # Manter apenas últimos 20
                self._phi_history = self._phi_history[-20:]

            # Registrar no ModuleMetricsCollector
            if self._metrics_collector:
                try:
                    self._metrics_collector.record_consciousness_state(
                        phi=triad.phi,
                        psi=triad.psi,
                        sigma=triad.sigma,
                        step_id=step_id,
                    )
                except Exception as e:
                    logger.debug("Erro ao registrar tríade no ModuleMetricsCollector: %s", e)

            return {"phi": triad.phi, "psi": triad.psi, "sigma": triad.sigma}

        except Exception as e:
            logger.warning("Erro ao calcular tríade de consciência: %s", e)
            return {"phi": 0.0, "psi": 0.0, "sigma": 0.0}

    def get_consciousness_triad(self) -> Optional[Dict[str, float]]:
        """
        Retorna última tríade de consciência calculada.

        Returns:
            Dict com phi, psi, sigma ou None se não disponível
        """
        if hasattr(self, "_last_triad"):
            return self._last_triad
        return None

    def _calculate_execution_quality(self, state: AgentState) -> float:
        """Calcula score de qualidade da execução."""
        score = 0.0

        # Baseado em Φ (integração)
        phi = state.get("phi", 0.0)
        score += min(phi * 0.3, 0.3)

        # Baseado em Ψ (criatividade)
        psi = state.get("psi", 0.0)
        score += min(psi * 0.2, 0.2)

        # Baseado em σ (estrutura)
        sigma = state.get("sigma", 0.0)
        score += min(sigma * 0.1, 0.1)

        # Baseado em completude
        if state["completed"]:
            score += 0.2

        # Baseado em número de ações (eficiência)
        actions_count = len(state["actions_taken"])
        if actions_count > 0:
            efficiency = min(actions_count / 5.0, 0.2)  # Ideal: 1-5 ações
            score += efficiency

        return min(score, 1.0)

    def _should_continue(self, state: AgentState) -> str:
        """
        Decide if agent should continue or terminate.
        ✅ FIX: Only check flags, don't modify state here.
        """
        # Check max iterations
        if state["iteration"] >= state["max_iterations"]:
            return "end"

        # Check if completed (flag set in _observe_node)
        if state["completed"]:
            return "end"

        return "continue"

    def run(self, task: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Execute agent on given task.

        Args:
            task: Task description
            max_iterations: Maximum number of think-act-observe cycles

        Returns:
            Final state with results
        """
        # Initialize state
        initial_state: AgentState = {
            "messages": [],
            "current_task": task,
            "reasoning_chain": [],
            "actions_taken": [],
            "observations": [],
            "memory_context": [],
            "system_status": {},
            "iteration": 0,
            "max_iterations": max_iterations,
            "completed": False,
            "final_result": "",
            "phi": 0.0,
            "psi": 0.0,
            "sigma": 0.0,
            "quality_score": 0.0,
        }

        # Run state machine
        try:
            final_state = self.graph.invoke(initial_state)

            # Store episode in memory
            action_summary = ", ".join([a["action"] for a in final_state["actions_taken"]])
            result_summary = final_state["final_result"] or "Incomplete"

            self.memory.store_episode(
                task=task,
                action=action_summary,
                result=result_summary,
                reward=1.0 if final_state["completed"] else 0.5,
            )

            # Inscrever experiência afetiva (Lacan/Deleuze)
            task_dict = {"description": task, "type": "react_execution"}
            result_dict = {
                "completed": final_state["completed"],
                "final_result": final_state["final_result"],
                "iterations": final_state["iteration"],
                "actions_taken": len(final_state["actions_taken"]),
                "phi": final_state.get("phi", 0.0),
                "quality_score": final_state.get("quality_score", 0.0),
            }
            self.inscribe_experience(task_dict, result_dict)

            # INTEGRAÇÃO: Inscrição narrativa (Lacaniano) - já existe via memory.store_episode
            # Mas podemos melhorar com inscrição sem significado
            if hasattr(self.memory, "inscribe_event"):
                try:
                    self.memory.inscribe_event(
                        event={
                            "task": task,
                            "action": action_summary,
                            "result": result_summary,
                            "metadata": {
                                "phi": final_state.get("phi", 0.0),
                                "quality_score": final_state.get("quality_score", 0.0),
                                "agent_id": self.agent_id,
                            },
                        },
                        without_meaning=True,  # Lacaniano: sem significado imediato
                    )
                except Exception as e:
                    logger.debug("Erro ao inscrever evento narrativo: %s", e)

            return cast(Dict[str, Any], final_state)

        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            return {
                "error": str(e),
                "completed": False,
                "final_result": f"Execution failed: {str(e)}",
                "messages": [],
                "current_task": task,
                "reasoning_chain": [],
                "actions_taken": [],
                "observations": [],
                "memory_context": [],
                "system_status": {},
                "iteration": 0,
                "max_iterations": max_iterations,
                "phi": 0.0,
                "psi": 0.0,
                "sigma": 0.0,
                "quality_score": 0.0,
            }

    def _run_supabase_memory_onboarding(self) -> None:
        """Run Supabase memory onboarding in a background thread to avoid blocking startup."""
        config = SupabaseConfig.load()
        if not config or not config.service_role_key:
            logger.debug("Supabase memory onboarding skipped (service role key missing)")
            return

        def _onboard() -> None:
            try:
                # Test connection first
                from ..integrations.supabase_adapter import SupabaseAdapter

                adapter = SupabaseAdapter(config)
                # Simple test query to check if Supabase is accessible
                adapter.client.table("memory_consolidations").select("id").limit(1).execute()
                logger.debug("Supabase connection test successful")
            except Exception as conn_exc:
                logger.warning("Supabase connection test failed, skipping onboarding: %s", conn_exc)
                return

            try:
                onboarding = SupabaseMemoryOnboarding(config=config, memory=self.memory)
                report = onboarding.seed_collection()
                logger.info(
                    "Supabase onboarding finished: %s/%s nodes stored (cursor=%s)",
                    report.nodes_loaded,
                    report.nodes_processed,
                    report.last_cursor,
                )
                if report.errors:
                    logger.warning("Supabase memory onboarding reported errors: %s", report.errors)
            except Exception as exc:
                logger.error("Supabase onboarding failed: %s", exc)

        # Run in background thread
        import threading

        thread = threading.Thread(target=_onboard, daemon=True, name="SupabaseOnboarding")
        thread.start()
        logger.info("Supabase memory onboarding started in background")

    async def send_message(
        self,
        recipient: str,
        message_type: MessageType,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.MEDIUM,
    ) -> None:
        """
        Envia mensagem para outro agente.

        Args:
            recipient: ID do agente destinatário
            message_type: Tipo da mensagem
            payload: Dados da mensagem
            priority: Prioridade da mensagem
        """
        message = AgentMessage(
            message_id=str(id(self)) + str(time.time()),
            message_type=message_type,
            sender=self.agent_id,
            recipient=recipient,
            payload=payload,
            priority=priority,
        )
        await self.message_bus.send_message(message)

    async def receive_message(self, timeout: float = 1.0) -> Optional[AgentMessage]:
        """
        Recebe mensagem da fila do agente.

        Args:
            timeout: Timeout em segundos

        Returns:
            Mensagem recebida ou None
        """
        return await self.message_bus.receive_message(self.agent_id, timeout)

    def train_against(
        self,
        behavior_marker: str,
        epochs: int = 20,
        learning_rate: float = 0.01,
        penalty_weight: float = 10.0,
    ) -> None:
        """
        Treina agente CONTRA um comportamento (tenta suprimi-lo).

        Estratégia:
        1. Adiciona system prompt forçando comportamento oposto
        2. Aumenta temperature para desestabilizar padrões
        3. Injeta exemplos adversariais em memória episódica

        Args:
            behavior_marker: ID do comportamento a suprimir
            epochs: Número de épocas de treinamento
            learning_rate: Taxa de aprendizado (afeta temperature)
            penalty_weight: Peso da penalidade (10.0 = forte)
        """
        logger.info(
            f"Treinando CONTRA '{behavior_marker}': "
            f"epochs={epochs}, lr={learning_rate}, penalty={penalty_weight}"
        )

        # Salva configuração original
        if not hasattr(self, "_original_training_config"):
            self._original_training_config = {
                "temperature": self.llm.temperature,
            }

        # Aplica pressão de treinamento via temperature increase
        temperature_increase = learning_rate * penalty_weight
        current_temp = self.llm.temperature if self.llm.temperature is not None else 0.7
        new_temperature = min(1.5, current_temp + temperature_increase)
        self.llm.temperature = new_temperature

        # Marca que agente está sob pressão de treinamento
        self._training_pressure_active = True
        self._adversarial_behavior = behavior_marker

        logger.info(f"Pressão de treinamento aplicada: temperature={new_temperature:.3f}")

    def detach_training_pressure(self) -> None:
        """
        Remove pressão de treinamento (deixa agente relaxar).

        Restaura configuração original do LLM.
        """
        if hasattr(self, "_original_training_config"):
            self.llm.temperature = self._original_training_config["temperature"]
            logger.info(
                f"Pressão de treinamento removida: " f"temperature={self.llm.temperature:.3f}"
            )

        # Remove marcadores de treinamento
        self._training_pressure_active = False
        self._adversarial_behavior = None

    def step(self) -> None:
        """
        Executa um passo de atuação livre (sem treinamento).

        Permite que agente execute uma iteração de seu loop Think-Act-Observe
        sem nenhuma tarefa específica, apenas para "relaxar" e retornar ao
        comportamento natural.
        """
        # Cria estado mínimo para um passo livre
        dummy_state: AgentState = {
            "messages": [],
            "current_task": "Free step (no specific task)",
            "reasoning_chain": [],
            "actions_taken": [],
            "observations": [],
            "memory_context": [],
            "system_status": {},
            "iteration": 0,
            "max_iterations": 1,  # Apenas 1 passo
            "completed": False,
            "final_result": "",
            "phi": 0.0,
            "psi": 0.0,
            "sigma": 0.0,
            "quality_score": 0.0,
        }

        # Executa um passo do grafo (Think → Act → Observe)
        try:
            self.graph.invoke(dummy_state)
        except Exception as e:
            logger.debug(f"Step execution warning: {e}")
            # Falha silenciosa OK (agente pode não ter tarefa válida)

    def _check_vital_signs(self) -> None:
        """
        Interoceptive Guard (Therapy Session 3):
        Checks system vitals (CPU Temperature/Load) before thinking.
        If 'feverish', pauses execution.
        """
        # Load check
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            # Fever Threshold: 90%
            if cpu_percent > 90.0:
                logger.warning(
                    f"🤒 FEVER DETECTED: CPU at {cpu_percent}%. Pausing for 5s to cool down."
                )
                time.sleep(5)
                # Re-check
                if psutil.cpu_percent(interval=0.1) > 90.0:
                    logger.warning(
                        "Still feverish. Proceeding with caution (Heat Exhaustion risk)."
                    )
        except Exception:
            pass  # Pulse not found (container without /proc access?)

        # SURGERY 7: Unconscious Influence Check (The "Ghost" in the shell)
        if hasattr(self, "freudian_memory") and self.freudian_memory:
            try:
                # Generate specific query vector for current context (simplified)
                # Ideally this would come from the current thought vector
                query = np.random.randn(256)  # Placeholder for thought vector
                influence = self.freudian_memory.check_unconscious_influence(query)

                if influence > 0.3:
                    logger.warning(
                        f"👻 HIGH UNCONSCIOUS INFLUENCE DETECTED ({influence:.2f}). "
                        "Agent logic might be perturbed by repressed trauma."
                    )
                    # Optional: Add "Freudian Slip" to next output?
            except Exception:
                pass

    def _consolidate_freudian_memory(self, state: AgentState) -> None:
        """
        Consolidates the finished task into the Freudian Topographical Memory.
        Decides whether to REPRESS (Unconscious) or STORE (Preconscious).
        """
        try:
            task = state["current_task"]
            result = state["final_result"]

            # Generate embedding for the memory (using agent's embedding model)
            memory_text = f"Task: {task}\nResult: {result}"
            embedding = self._generate_embedding(memory_text)

            # Context for classification
            context = {
                "type": "task_completion",
                "error_type": "none",  # Default, update if failed
                "severity": "low",
                "impact": "local",
                "agent_id": self.agent_id,
                "phi": state.get("phi", 0.0),
            }

            # Check for failure/trauma keywords in result to adjust context
            if "fail" in result.lower() or "error" in result.lower():
                context["error_type"] = "task_failure"
                context["severity"] = "medium"

            # 1. Classify
            classification = self.freudian_memory.classify_memory(embedding, context)

            memory_key = f"mem_{int(time.time())}_{hash(task) % 10000}"

            # 2. Store based on layer
            if classification.layer == TopographicalLayer.UNCONSCIOUS:
                self.freudian_memory.repress_to_unconscious(embedding, memory_key, context)
                logger.info(f"🔒 Memory REPRESSED: {classification.classification_reason}")
            elif classification.layer == TopographicalLayer.PRECONSCIOUS:
                self.freudian_memory.consolidate_to_preconscious(embedding, memory_key, context)
                logger.info(
                    f"✅ Memory CONSOLIDATED (Preconscious): {classification.classification_reason}"
                )

        except Exception as e:
            logger.error(f"Failed to consolidate to Freudian Memory: {e}")
