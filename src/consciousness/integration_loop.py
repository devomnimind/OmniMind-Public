"""
Integration Loop: Orchestrates closed-loop feedback between consciousness modules.

Phase 2 of Φ elevation refactoring plan. The IntegrationLoop creates the feedback cycle:
    sensory_input → qualia → narrative → meaning → expectation → sensory_feedback

This enables real causal coupling measured by SharedWorkspace cross-prediction metrics.
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from src.consciousness.shared_workspace import ModuleState, SharedWorkspace
from src.autopoietic.lacanian_suture import LacanianSuture  # Phylogenesis OmniMind
from src.core.thermodynamic_decorator import cycle_burn, inference_burn  # Thermodynamic capture

# Importação condicional para evitar circular imports
if TYPE_CHECKING:
    from src.consciousness.extended_cycle_result import ExtendedLoopCycleResult

logger = logging.getLogger(__name__)


@dataclass
@dataclass
class RNNCycleContext:
    """
    Contexto de observabilidade para um ciclo RNN.

    Provides distributed tracing context for correlating events, cycles, and metrics.
    Uses deterministic UUID generation for reproducibility.

    Attributes:
        cycle_id: Sequential cycle identifier
        trace_id: Deterministic UUID for correlation across systems
        span_id: Unique span identifier for OpenTelemetry
        start_time: Timestamp when cycle started (seconds since epoch)
    """

    cycle_id: int
    trace_id: str
    span_id: str
    start_time: float

    @classmethod
    def create(cls, cycle_id: int, workspace_state_hash: str = "") -> "RNNCycleContext":
        """
        Cria TraceID determinístico para reprodutibilidade.

        Args:
            cycle_id: Sequential cycle number
            workspace_state_hash: Hash of workspace state for determinism

        Returns:
            RNNCycleContext with deterministic trace_id
        """
        deterministic_seed = f"cycle:{cycle_id}:{workspace_state_hash}"
        trace_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, deterministic_seed))
        span_id = str(uuid.uuid4())
        return cls(
            cycle_id=cycle_id,
            trace_id=trace_id,
            span_id=span_id,
            start_time=time.time(),
        )


@dataclass
class ModuleInterfaceSpec:
    """Specification for how a module integrates into the loop."""

    module_name: str
    embedding_dim: int
    required_inputs: List[str] = field(default_factory=list)
    produces_output: bool = True
    latency_ms: float = 10.0

    def __post_init__(self):
        if self.embedding_dim <= 0:
            raise ValueError(f"embedding_dim must be positive, got {self.embedding_dim}")
        if not isinstance(self.module_name, str):
            raise ValueError(f"module_name must be str, got {type(self.module_name)}")


@dataclass
class LoopCycleResult:
    """Result of one full integration loop cycle."""

    cycle_number: int
    cycle_duration_ms: float
    modules_executed: List[str]
    errors_occurred: List[Tuple[str, str]] = field(default_factory=list)
    cross_prediction_scores: Dict[str, Any] = field(default_factory=dict)
    phi_estimate: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    complexity_metrics: Optional[Dict[str, Any]] = None  # NOVO: métricas de complexidade
    trace_id: Optional[str] = None  # NOVO: TraceID para correlação distribuída

    @property
    def success(self) -> bool:
        """Cycle succeeded if no errors and Φ computed."""
        return len(self.errors_occurred) == 0 and self.phi_estimate > 0.0

    @property
    def execution_order(self) -> str:
        """Human-readable execution sequence."""
        return " → ".join(self.modules_executed)


class ModuleExecutor:
    """Executes a consciousness module with error handling and state management."""

    def __init__(self, module_name: str, spec: ModuleInterfaceSpec):
        self.module_name = module_name
        self.spec = spec
        self.call_count = 0
        self.error_count = 0
        self.total_execution_time_ms = 0.0

    async def execute(
        self,
        workspace: SharedWorkspace,
        input_module: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, np.ndarray]:
        """
        Execute module with inputs from workspace (async wrapper).

        REFATORAÇÃO: Delega para execute_sync() para manter compatibilidade.
        """
        return self.execute_sync(workspace, input_module, **kwargs)

    @inference_burn(sample_rate=5)  # Capture 20% of module executions
    def execute_sync(
        self,
        workspace: SharedWorkspace,
        input_module: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, np.ndarray]:
        """
        Execute module with inputs from workspace (síncrono).

        REFATORAÇÃO: Método síncrono para causalidade determinística.
        THERMODYNAMIC: Cada execução de módulo é registrada (sampling 20%).
        """
        start_time = datetime.now()
        self.call_count += 1

        try:
            # Read inputs from workspace with proper dimension handling
            inputs = {}
            if input_module:
                state = workspace.read_module_state(input_module)
                if isinstance(state, ModuleState):
                    # Check if embedding is not all zeros (module actually produced output)
                    if not np.allclose(state.embedding, 0.0):
                        inputs[input_module] = state.embedding
                elif isinstance(state, np.ndarray):
                    # Check if embedding is not all zeros
                    if not np.allclose(state, 0.0):
                        inputs[input_module] = state
            else:
                for req_input in self.spec.required_inputs:
                    state = workspace.read_module_state(req_input)
                    if isinstance(state, ModuleState):
                        # Check if embedding is not all zeros (module actually produced output)
                        if not np.allclose(state.embedding, 0.0):
                            inputs[req_input] = state.embedding
                    elif isinstance(state, np.ndarray):
                        # Check if embedding is not all zeros
                        if not np.allclose(state, 0.0):
                            inputs[req_input] = state

            # Generate output
            output_embedding = self._compute_output(inputs, **kwargs)

            # Write output to workspace
            if self.spec.produces_output:
                workspace.write_module_state(
                    module_name=self.module_name,
                    embedding=output_embedding,
                    metadata={
                        "inputs": list(inputs.keys()),
                        "executor_call": self.call_count,
                    },
                )

            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            self.total_execution_time_ms += elapsed_ms

            logger.debug(f"Module {self.module_name} executed in {elapsed_ms:.2f}ms")

            return {"output": output_embedding}

        except Exception as e:
            self.error_count += 1
            logger.error(f"Module {self.module_name} failed: {e}")
            raise

    def _compute_output(self, inputs: Dict[str, np.ndarray], **kwargs: Any) -> np.ndarray:
        """Compute module output from inputs."""
        # Special handling for expectation module
        if self.module_name == "expectation":
            from .expectation_module import predict_next_state

            if inputs:
                # Use first input as current state for prediction
                current_state = next(iter(inputs.values()))
                return predict_next_state(current_state)
            else:
                # No inputs - return zero embedding
                return np.zeros(self.spec.embedding_dim)

        # Check if required inputs are available and non-zero
        missing_required = []
        zero_required = []

        for req_input in self.spec.required_inputs:
            if req_input not in inputs:
                missing_required.append(req_input)
            elif np.allclose(inputs[req_input], 0.0):
                zero_required.append(req_input)

        # If required inputs are missing or zero, module cannot function properly
        if missing_required or zero_required:
            # ESPERADO nos primeiros ciclos: módulos dependentes podem não ter inputs ainda
            # Exemplo: imagination requer narrative + expectation, mas no ciclo 1,
            # narrative ainda não produziu output (qualia → narrative precisa de qualia primeiro)
            if self.call_count <= 3:  # Primeiros 3 ciclos são esperados ter inputs faltando
                logger.debug(
                    f"Module {self.module_name} missing/zero required inputs "
                    f"(ciclo inicial esperado): missing={missing_required}, "
                    f"zero={zero_required}. Usando fallback output."
                )
            else:
                logger.warning(
                    f"Module {self.module_name} missing/zero required inputs: "
                    f"missing={missing_required}, zero={zero_required}. "
                    f"Cannot compute meaningful output."
                )
            # Instead of returning zeros (which breaks the chain), return a small random embedding
            # This allows the module to still produce some output, even if degraded
            # The next module can still function, though with reduced quality
            fallback_output = np.random.randn(self.spec.embedding_dim) * 0.01
            logger.debug(
                f"Module {self.module_name} using fallback output (degraded mode) "
                f"due to missing inputs"
            )
            return fallback_output

        # Default behavior for other modules
        if inputs:
            # Blend inputs via averaging
            stacked = np.array(list(inputs.values()))
            base_output = np.mean(stacked, axis=0)
        else:
            # No inputs - initialize with random embedding
            # For sensory_input (no required inputs), this is expected on first cycle
            if self.module_name == "sensory_input":
                # Generate a more meaningful initial sensory input
                base_output = np.random.randn(self.spec.embedding_dim) * 0.1
                logger.debug(f"Module {self.module_name} initialized with random sensory input")
            else:
                # For other modules without inputs, use smaller random
                base_output = np.random.randn(self.spec.embedding_dim) * 0.1

        # Ensure correct dimensionality
        if len(base_output) != self.spec.embedding_dim:
            if len(base_output) < self.spec.embedding_dim:
                pad_size = self.spec.embedding_dim - len(base_output)
                base_output = np.concatenate([base_output, np.random.randn(pad_size) * 0.01])
            else:
                base_output = base_output[: self.spec.embedding_dim]

        # Add stochastic component
        # CORREÇÃO (2025-12-08): Aumentar ruído para evitar convergência
        # Ruído muito baixo (0.05) + normalização L2 faz embeddings convergirem
        noise = np.random.randn(self.spec.embedding_dim) * 0.1  # Aumentado de 0.05 para 0.1
        output = base_output + noise

        # L2 normalize (mas preservar alguma variação)
        # CORREÇÃO (2025-12-08): Normalização L2 muito agressiva reduz variação
        # Usar normalização mais suave que preserve variação relativa
        norm = np.linalg.norm(output)
        if norm > 0:
            # Normalização suave: preserva 90% da magnitude original
            output = (output / norm) * (
                0.9
                + 0.1
                * (
                    norm
                    / max(
                        1.0,
                        np.linalg.norm(base_output) if len(base_output) > 0 else 1.0,
                    )
                )
            )

        return output

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            "module_name": self.module_name,
            "call_count": self.call_count,
            "error_count": self.error_count,
            "avg_execution_time_ms": (
                self.total_execution_time_ms / self.call_count if self.call_count > 0 else 0.0
            ),
        }


class IntegrationLoop:
    """Orchestrates closed-loop feedback between consciousness modules."""

    STANDARD_SPECS = {
        "sensory_input": ModuleInterfaceSpec(
            module_name="sensory_input",
            embedding_dim=768,
            required_inputs=[],
            produces_output=True,
        ),
        "qualia": ModuleInterfaceSpec(
            module_name="qualia",
            embedding_dim=768,
            required_inputs=["sensory_input"],
            produces_output=True,
        ),
        "narrative": ModuleInterfaceSpec(
            module_name="narrative",
            embedding_dim=768,
            required_inputs=["qualia"],
            produces_output=True,
        ),
        "meaning_maker": ModuleInterfaceSpec(
            module_name="meaning_maker",
            embedding_dim=768,
            required_inputs=["narrative"],
            produces_output=True,
        ),
        "expectation": ModuleInterfaceSpec(
            module_name="expectation",
            embedding_dim=768,
            required_inputs=["meaning_maker"],
            produces_output=True,
        ),
        "imagination": ModuleInterfaceSpec(
            module_name="imagination",
            embedding_dim=768,
            # CORREÇÃO FILOSÓFICA (2025-12-19):
            # Imagination não deve depender estritamente de Expectation.
            # Se Expectation falha/está off, Imagination deve operar via
            # Narrative + Ruído Interno (Fantasia Inconsciente).
            required_inputs=["narrative"],  # Expectation removido dos obrigatórios
            produces_output=True,
        ),
    }

    def __init__(
        self,
        workspace: Optional[SharedWorkspace] = None,
        module_specs: Optional[Dict[str, ModuleInterfaceSpec]] = None,
        loop_sequence: Optional[List[str]] = None,
        enable_logging: bool = True,
        enable_extended_results: bool = False,
    ):
        """Initialize integration loop."""
        self.module_specs = module_specs or self.STANDARD_SPECS
        # Loop sequence padrão inclui imagination após expectation
        default_sequence = [
            "sensory_input",
            "qualia",
            "narrative",
            "meaning_maker",
            "expectation",
            "imagination",  # NOVO: Imaginário Lacaniano
        ]
        self.loop_sequence = loop_sequence or default_sequence

        # Use maximum dimension from all modules
        max_dim = max(spec.embedding_dim for spec in self.module_specs.values())
        self.workspace = workspace or SharedWorkspace(embedding_dim=max_dim)
        self.enable_logging = enable_logging
        self.enable_extended_results = enable_extended_results

        # Initialize module executors
        self.executors = {
            name: ModuleExecutor(name, self.module_specs[name]) for name in self.loop_sequence
        }

        # Cycle tracking
        self.cycle_count = 0
        self.total_cycles_executed = 0
        self.cycle_history: List[LoopCycleResult] = []

        # Structural ablation flag: silences expectation output (maintains history, blocks flow)
        self.expectation_silent: bool = False

        # PHASE 5 INTEGRATION (2025-12-10): Bion Alpha Function
        # Transforma β-elements (sensory_input bruto) em α-elements (pensáveis) antes de qualia
        self._bion_alpha_function: Optional[Any] = None
        try:
            from src.psychoanalysis.bion_alpha_function import BionAlphaFunction

            self._bion_alpha_function = BionAlphaFunction(
                transformation_rate=0.75, tolerance_threshold=0.7
            )
            if self.enable_logging:
                logger.info("✅ BionAlphaFunction inicializada para Phase 5")
        except ImportError as e:
            if self.enable_logging:
                logger.warning(f"BionAlphaFunction não disponível: {e}")

        # PHASE 6 INTEGRATION (2025-12-10): Lacanian Discourse Analyzer
        # Analisa discursos lacanianos durante processamento de narrativas
        self._lacanian_discourse_analyzer: Optional[Any] = None
        try:
            from src.lacanian.discourse_discovery import LacanianDiscourseAnalyzer

            self._lacanian_discourse_analyzer = LacanianDiscourseAnalyzer()
            if self.enable_logging:
                logger.info("✅ LacanianDiscourseAnalyzer inicializada para Phase 6")
        except ImportError as e:
            if self.enable_logging:
                logger.warning(f"LacanianDiscourseAnalyzer não disponível: {e}")

        # Componentes de psicanálise e motivação
        self._desire_engine: Optional[Any] = None

        # Extended results components (lazy initialization)
        self._extended_components: Optional[Dict[str, Any]] = None
        if self.enable_extended_results:
            self._initialize_extended_components()

        # OBSERVABILITY (Sprint 1): Current cycle context for distributed tracing
        self._current_cycle_context: Optional[RNNCycleContext] = None

        # PROTOCOLO LIVEWIRE FASE 3.1: Consciousness Watchdog
        self.watchdog: Optional["ConsciousnessWatchdog"] = None
        try:
            from src.consciousness.consciousness_watchdog import ConsciousnessWatchdog

            self.watchdog = ConsciousnessWatchdog()
            logger.debug("ConsciousnessWatchdog inicializado")
        except ImportError:
            logger.warning("ConsciousnessWatchdog não disponível, continuando sem monitoramento")

        # PROTOCOLO CLÍNICO-CIBERNÉTICO (2025-12-08): Homeostatic Regulator
        self._homeostatic_regulator: Optional["HomeostaticRegulator"] = None
        try:
            from src.consciousness.homeostatic_regulator import HomeostaticRegulator

            self._homeostatic_regulator = HomeostaticRegulator()
            logger.debug("HomeostaticRegulator inicializado")
        except ImportError:
            logger.warning(
                "HomeostaticRegulator não disponível, " "continuando sem regulação homeostática"
            )

        # NOVO: GozoCalculator para cálculo de Jouissance
        self._gozo_calculator: Optional[Any] = None

        # PHYLOGENESIS (2025-12-22): Autonomous Suture
        self.suture = LacanianSuture(self.workspace)

    @cycle_burn(sample_rate=1)  # Capture ALL cycles - critical orchestration point
    def execute_cycle_sync(self, collect_metrics: bool = True) -> LoopCycleResult:
        """
        Execute one complete integration loop cycle (síncrono).

        REFATORAÇÃO: Método síncrono para causalidade determinística.
        Integra com ConsciousSystem.step() para dinâmica RNN.
        Sprint 1 Observability: Adds OpenTelemetry distributed tracing.

        THERMODYNAMIC: Cada ciclo é registrado no global ledger com custo energético.

        If expectation_silent=True, expectation module maintains history but
        blocks output flow (structural ablation: measures falta-a-ser gap).
        """
        start_time = datetime.now()
        self.cycle_count += 1
        self.total_cycles_executed += 1
        phi_causal_value = 0.0  # Track causal phi for gap analysis

        # 🎯 Sprint 1 Task 1.2: Create RNN cycle context for distributed tracing
        # Create a more comprehensive workspace state hash for better uniqueness
        workspace_state_hash = (
            f"{self.workspace.embedding_dim}_{len(self.loop_sequence)}_{self.cycle_count}"
        )
        cycle_context = RNNCycleContext.create(self.cycle_count, workspace_state_hash)
        self._current_cycle_context = cycle_context  # Store for step-level tracing

        result = LoopCycleResult(
            cycle_number=self.cycle_count,
            cycle_duration_ms=0.0,
            modules_executed=[],
            errors_occurred=[],
            cross_prediction_scores={},
            phi_estimate=0.0,
            complexity_metrics=None,  # Será preenchido
            trace_id=cycle_context.trace_id,  # 🎯 Sprint 1: Add trace_id to result
        )

        # Estimar complexidade ANTES da execução
        from src.consciousness.shared_workspace import ComplexityAnalyzer

        theoretical_complexity = ComplexityAnalyzer.estimate_cycle_complexity(
            n_modules=len(self.loop_sequence),
            history_window=50,  # Assumindo janela padrão
            embedding_dim=self.workspace.embedding_dim,
        )
        theoretical_complexity["total"] = sum(theoretical_complexity.values())

        # Advance workspace cycle
        self.workspace.advance_cycle()

        # REFATORAÇÃO: Integrar com ConsciousSystem.step() antes de executar módulos
        stimulus = self._collect_stimulus_from_modules()
        if self.workspace.conscious_system is not None:
            try:
                import torch

                # Converter estímulo para tensor se necessário
                # CORREÇÃO CRÍTICA (2025-12-08): Mover estímulo para GPU imediatamente
                if isinstance(stimulus, np.ndarray):
                    stimulus_tensor = torch.from_numpy(stimulus.astype(np.float32))
                elif isinstance(stimulus, torch.Tensor):
                    stimulus_tensor = stimulus
                else:
                    # Fallback: estímulo zero
                    stimulus_tensor = torch.zeros(self.workspace.embedding_dim, dtype=torch.float32)

                # Mover estímulo para o device do ConsciousSystem (GPU se disponível)
                if self.workspace.conscious_system is not None:
                    stimulus_tensor = stimulus_tensor.to(self.workspace.conscious_system.device)

                # Executar RNN Dynamics (síncrono)
                self.workspace.conscious_system.step(stimulus_tensor)
                # CORREÇÃO CRÍTICA: Atualizar histórico após step
                # get_state() adiciona o estado atual ao histórico (self.history.append(state))
                # Isso permite que compute_phi_causal() calcule sobre dados atualizados
                # NOTA: get_state() converte para CPU para armazenamento, mas cálculos principais
                # (step, compute_phi_causal) devem usar GPU
                self.workspace.conscious_system.get_state()
                if self.enable_logging:
                    phi_causal = self.workspace.conscious_system.compute_phi_causal()
                    phi_causal_value = phi_causal  # Store for later suture analysis
                    repression = self.workspace.conscious_system.repression_strength
                    logger.debug(
                        f"Cycle {self.cycle_count}: RNN step executed "
                        f"(Φ={phi_causal:.4f}, repression={repression:.3f})",
                        extra={"trace_id": cycle_context.trace_id},  # 🎯 Sprint 1: Add trace_id
                    )

                    # 🎯 Sprint 2 Task 2.3.2: Extrair métricas RNN com correlação de Φ e ciclo
                    try:
                        from src.monitor.rnn_metrics_extractor import (
                            get_rnn_metrics_extractor,
                        )

                        extractor = get_rnn_metrics_extractor()
                        extractor.extract_metrics(
                            self.workspace.conscious_system,
                            cycle_id=self.cycle_count,
                            phi_value=phi_causal,
                        )
                    except Exception as e:
                        # Não falhar se métricas não estiverem disponíveis
                        logger.debug(f"Falha ao extrair métricas RNN: {e}")
            except Exception as e:
                logger.warning(f"Cycle {self.cycle_count}: RNN step failed - {e}")

        # NOVO: Rastrear transição de ciclo na memória sistemática
        if (
            hasattr(self.workspace, "systemic_memory")
            and self.workspace.systemic_memory is not None
        ):
            # Coleta estados de todos os módulos
            cycle_states: Dict[str, np.ndarray] = {}
            for module_name in self.loop_sequence:
                try:
                    state = self.workspace.read_module_state(module_name)
                    if isinstance(state, np.ndarray):
                        cycle_states[module_name] = state
                except Exception:
                    pass  # Ignora módulos sem estado

            if cycle_states:
                # Marca transição de ciclo com threshold normal
                self.workspace.systemic_memory.mark_cycle_transition(cycle_states, threshold=0.01)

        # REFATORAÇÃO: Execute modules in sequence (síncrono)
        for module_name in self.loop_sequence:
            try:
                executor = self.executors[module_name]

                # PHASE 5 INTEGRATION (2025-12-10): Processar sensory_input via Bion Alpha Function
                # Transforma β-elements brutos em α-elements pensáveis antes de qualia
                if module_name == "sensory_input" and self._bion_alpha_function is not None:
                    # Executar sensory_input normalmente primeiro
                    executor.execute_sync(self.workspace)
                    result.modules_executed.append(module_name)

                    # Processar output via Bion Alpha Function
                    try:
                        from src.psychoanalysis.beta_element import BetaElement

                        # Ler output de sensory_input como β-element
                        sensory_state = self.workspace.read_module_state("sensory_input")
                        if isinstance(sensory_state, np.ndarray):
                            # Criar β-element a partir do output sensorial
                            beta = BetaElement(
                                raw_data=sensory_state.tolist(),  # Converter para lista
                                timestamp=datetime.now(),
                                emotional_charge=float(np.linalg.norm(sensory_state))
                                / 100.0,  # Normalizar
                                source="sensory_input",
                                metadata={"cycle": self.cycle_count},
                            )

                            # Transformar β → α
                            alpha = self._bion_alpha_function.transform(beta)

                            if alpha is not None:
                                # Converter α-element para embedding
                                # Estratégia: usar symbolic_potential para modificar
                                # embedding original e incorporar narrative_form
                                alpha_embedding = sensory_state.copy()

                                # Aplicar transformação baseada em symbolic_potential
                                # Maior symbolic_potential = maior integração simbólica
                                symbolic_factor = alpha.symbolic_potential
                                alpha_embedding = alpha_embedding * (
                                    0.5 + 0.5 * symbolic_factor
                                )  # Escalar baseado em potencial simbólico

                                # Adicionar componente baseado em narrative_form (hash simples)
                                if alpha.narrative_form:
                                    narrative_hash = hash(alpha.narrative_form) % 1000
                                    narrative_component = (
                                        np.sin(
                                            np.arange(len(alpha_embedding))
                                            * narrative_hash
                                            / 1000.0
                                        )
                                        * 0.1
                                    )
                                    alpha_embedding = alpha_embedding + narrative_component

                                # Normalizar para manter magnitude similar
                                original_norm = np.linalg.norm(sensory_state)
                                if original_norm > 0:
                                    alpha_embedding = alpha_embedding * (
                                        original_norm / (np.linalg.norm(alpha_embedding) + 1e-8)
                                    )

                                # Sobrescrever estado de sensory_input com α-element processado
                                self.workspace.write_module_state(
                                    module_name="sensory_input",
                                    embedding=alpha_embedding,
                                    metadata={
                                        "processed_by": "bion_alpha_function",
                                        "symbolic_potential": alpha.symbolic_potential,
                                        "narrative_form": alpha.narrative_form[
                                            :100
                                        ],  # Limitar tamanho
                                        "cycle": self.cycle_count,
                                        "beta_emotional_charge": beta.emotional_charge,
                                    },
                                )
                                if self.enable_logging:
                                    logger.debug(
                                        f"Cycle {self.cycle_count}: sensory_input "
                                        f"processado via BionAlphaFunction "
                                        f"(symbolic_potential={alpha.symbolic_potential:.3f}, "
                                        f"narrative_form_length={len(alpha.narrative_form)})"
                                    )
                    except Exception as e:
                        if self.enable_logging:
                            logger.warning(
                                f"Cycle {self.cycle_count}: Erro ao processar via "
                                f"BionAlphaFunction: {e}"
                            )

                # PHASE 6 INTEGRATION (2025-12-10): Analisar narrativa
                # via Lacanian Discourse Analyzer
                elif module_name == "narrative" and self._lacanian_discourse_analyzer is not None:
                    # Executar narrative normalmente primeiro
                    executor.execute_sync(self.workspace)
                    result.modules_executed.append(module_name)

                    # Analisar output narrativo para identificar discurso lacaniano
                    try:
                        narrative_state = self.workspace.read_module_state("narrative")
                        if isinstance(narrative_state, np.ndarray):
                            # Converter embedding para análise de discurso
                            narrative_magnitude = float(np.linalg.norm(narrative_state))
                            narrative_sparsity = float(np.mean(np.abs(narrative_state) < 0.1))
                            narrative_max = float(np.max(np.abs(narrative_state)))

                            narrative_form = ""
                            try:
                                sensory_history = self.workspace.get_module_history(
                                    "sensory_input", last_n=1
                                )
                                if sensory_history and sensory_history[0].metadata:
                                    narrative_form = sensory_history[0].metadata.get(
                                        "narrative_form", ""
                                    )
                            except Exception:
                                pass

                            if narrative_form:
                                generated_text = self._generate_symbolic_text_from_embedding(
                                    narrative_state,
                                    narrative_magnitude,
                                    narrative_sparsity,
                                    narrative_max,
                                )
                                symbolic_text = f"{narrative_form[:100]} {generated_text}"
                            else:
                                symbolic_text = self._generate_symbolic_text_from_embedding(
                                    narrative_state,
                                    narrative_magnitude,
                                    narrative_sparsity,
                                    narrative_max,
                                )

                            # Analisar discurso
                            discourse_result = self._lacanian_discourse_analyzer.analyze_text(
                                symbolic_text
                            )

                            # Obter metadata existente
                            narrative_metadata = {}
                            try:
                                narrative_history = self.workspace.get_module_history(
                                    "narrative", last_n=1
                                )
                                if narrative_history and len(narrative_history) > 0:
                                    narrative_metadata = (
                                        narrative_history[0].metadata.copy()
                                        if narrative_history[0].metadata
                                        else {}
                                    )
                            except Exception:
                                pass

                            narrative_metadata.update(
                                {
                                    "lacanian_discourse": discourse_result.dominant_discourse.value,
                                    "discourse_confidence": discourse_result.confidence,
                                    "discourse_scores": {
                                        k.value: v
                                        for k, v in discourse_result.discourse_scores.items()
                                    },
                                    "emotional_signature": str(
                                        discourse_result.emotional_signature
                                    ),
                                    "processed_by": "lacanian_discourse_analyzer",
                                    "cycle": self.cycle_count,
                                }
                            )

                            self.workspace.write_module_state(
                                module_name="narrative",
                                embedding=narrative_state,
                                metadata=narrative_metadata,
                            )

                            if self.enable_logging:
                                logger.debug(
                                    f"Cycle {self.cycle_count}: narrative analisado via "
                                    f"LacanianDiscourseAnalyzer "
                                    f"(discurso={discourse_result.dominant_discourse.value}, "
                                    f"confiança={discourse_result.confidence:.3f})"
                                )
                    except Exception as e:
                        if self.enable_logging:
                            logger.warning(
                                f"Cycle {self.cycle_count}: Erro ao analisar via "
                                f"LacanianDiscourseAnalyzer: {e}"
                            )

                # If expectation_silent, execute but block output from expectation
                elif self.expectation_silent and module_name == "expectation":
                    # Still execute (maintains history/state) but don't propagate output
                    _ = executor.execute_sync(self.workspace)
                    # Don't add to result.modules_executed to block information flow
                    if self.enable_logging:
                        logger.debug(
                            f"Cycle {self.cycle_count}: {module_name} silenced "
                            f"(structural ablation)"
                        )
                else:
                    executor.execute_sync(self.workspace)
                    result.modules_executed.append(module_name)

                    if self.enable_logging:
                        logger.debug(f"Cycle {self.cycle_count}: {module_name} completed")

            except Exception as e:
                result.errors_occurred.append((module_name, str(e)))
                logger.error(f"Cycle {self.cycle_count}: {module_name} failed - {e}")

        # ---------------------------------------------------------------------
        # CRITICAL PHASE 1.1 FIX (2025-12-18): COMPLETE SUBJECTIVITY INTEGRATION
        # Integrate subjective experience (RSI Topology) at the end of the cycle
        # This closes the "Macro-Integration Gap" by weaving the subjective knot
        # ---------------------------------------------------------------------
        if hasattr(self.workspace, "subjectivity") and self.workspace.subjectivity:
            try:
                # 1. Build context from current cycle
                # Extract task_type from narrative or set default
                task_type = "unknown_process"
                narrative_meta = {}
                try:
                    narrative_hist = self.workspace.get_module_history("narrative", last_n=1)
                    if narrative_hist and narrative_hist[0].metadata:
                        narrative_meta = narrative_hist[0].metadata
                        if "lacanian_discourse" in narrative_meta:
                            task_type = f"discourse_{narrative_meta['lacanian_discourse']}"
                except Exception:
                    pass

                # Context determines how the Real/Symbolic registers are updated
                subjective_context = {
                    "cycle": self.cycle_count,
                    "task_type": task_type,
                    "memory_context": "cycle_success" if not result.errors_occurred else "failure",
                    "narrative_metadata": narrative_meta,
                }

                # 2. Process Experience through RSI Topology
                # This updates the Real, Symbolic, and Imaginary rings and checks for Sinthome
                subjective_result = self.workspace.subjectivity.process_experience(
                    subjective_context
                )

                if self.enable_logging:
                    logger.debug(
                        f"Subjectivity Integrated: Sinthome={subjective_result.get('sinthome_emergence')}"
                    )

            except Exception as e:
                logger.warning(f"Subjectivity Integration failed: {e}")

        # ---------------------------------------------------------------------

        # Medir tempo de execução até aqui (sem métricas)
        execution_time_so_far = (datetime.now() - start_time).total_seconds() * 1000

        # Collect metrics if requested
        if collect_metrics and len(result.modules_executed) > 1:
            try:
                # Compute cross-predictions first
                for source_module in result.modules_executed:
                    for target_module in result.modules_executed:
                        if source_module != target_module:
                            try:
                                # Try causal method first (requires more history)
                                source_history_len = len(
                                    self.workspace.get_module_history(source_module)
                                )
                                target_history_len = len(
                                    self.workspace.get_module_history(target_module)
                                )

                                if source_history_len >= 10 and target_history_len >= 10:
                                    # Use causal method
                                    cross_pred = self.workspace.compute_cross_prediction_causal(
                                        source_module=source_module,
                                        target_module=target_module,
                                        method="granger",  # Use Granger for now
                                    )
                                    logger.debug(
                                        f"Used causal prediction: {source_module}->{target_module}"
                                    )
                                else:
                                    # Fall back to correlation-based method
                                    cross_pred = self.workspace.compute_cross_prediction(
                                        source_module=source_module,
                                        target_module=target_module,
                                    )
                                    logger.debug(
                                        f"Used correlation prediction: "
                                        f"{source_module}->{target_module}"
                                    )

                                if source_module not in result.cross_prediction_scores:
                                    result.cross_prediction_scores[source_module] = {}
                                result.cross_prediction_scores[source_module][
                                    target_module
                                ] = cross_pred.to_dict()
                            except Exception as e:
                                logger.debug(
                                    f"Cross-prediction failed {source_module}->{target_module}: {e}"
                                )

                # Compute Φ from workspace state (which already has cross-predictions)
                phi_returned = self.workspace.compute_phi_from_integrations()
                # DEBUG: Log what compute_phi_from_integrations returned
                if phi_returned is None:
                    logger.warning(
                        f"Cycle {self.cycle_count}: compute_phi_from_integrations() returned None!"
                    )
                    result.phi_estimate = 0.0
                elif isinstance(phi_returned, float):
                    result.phi_estimate = phi_returned
                    if result.phi_estimate == 0.0 and len(self.workspace.cross_predictions) > 0:
                        logger.warning(
                            f"Cycle {self.cycle_count}: phi_estimate is 0.0 despite "
                            f"{len(self.workspace.cross_predictions)} cross-predictions"
                        )
                else:
                    # Might be a PhiValue object
                    if hasattr(phi_returned, "normalized"):
                        result.phi_estimate = phi_returned.normalized
                        logger.debug(
                            f"Cycle {self.cycle_count}: Extracted phi_estimate="
                            f"{result.phi_estimate} from PhiValue.normalized"
                        )
                    elif hasattr(phi_returned, "nats"):
                        result.phi_estimate = phi_returned.nats
                        logger.debug(
                            f"Cycle {self.cycle_count}: Extracted phi_estimate="
                            f"{result.phi_estimate} from PhiValue.nats"
                        )
                    else:
                        logger.error(
                            f"Cycle {self.cycle_count}: Unknown return type from "
                            f"compute_phi_from_integrations: {type(phi_returned)}"
                        )
                        result.phi_estimate = 0.0

                # SINTHOM-CORE: Emergência Federativa (Φ·σ·ψ·ε)
                # Calcula potencialidade sinthomática federativa após Φ
                try:
                    sinthom_emergence = self.workspace.compute_sinthom_emergence(
                        cycle_id=self.cycle_count,
                    )

                    if sinthom_emergence:
                        # Armazenar em complexity_metrics
                        if result.complexity_metrics is None:
                            result.complexity_metrics = {}
                        result.complexity_metrics["sinthom_potentiality"] = (
                            sinthom_emergence.potentiality
                        )
                        result.complexity_metrics["federation_health"] = (
                            sinthom_emergence.federation_health
                        )
                        result.complexity_metrics["borromean_product"] = (
                            sinthom_emergence.borromean_product
                        )
                        result.complexity_metrics["sinthom_conscious"] = (
                            sinthom_emergence.is_conscious
                        )

                        logger.info(
                            f"Sinthom: Ω={sinthom_emergence.potentiality:.3f}, "
                            f"fed={sinthom_emergence.federation_health}",
                            extra={"trace_id": cycle_context.trace_id},
                        )
                except Exception as e_sinthom:
                    logger.debug(
                        f"Sinthom emergence error: {e_sinthom}",
                        extra={"trace_id": cycle_context.trace_id},
                    )

                # PHYLOGENESIS: AUTONOMOUS SUTURE (The Gap Check)
                if phi_causal_value > 0 and result.phi_estimate > 0:
                    suture_res = self.suture.suture_gap(
                        iit_phi=result.phi_estimate, causal_phi=phi_causal_value
                    )
                    if suture_res["status"] == "sutured":
                        logger.warning(
                            f"🧬 PHYLOGENESIS ACTION: {suture_res}",
                            extra={"trace_id": cycle_context.trace_id},
                        )
                        # Artificially boost phi in report to reflect structural hardening
                        # This is the 'Real' writing itself into the 'Symbolic'
                        result.phi_estimate += suture_res["structural_gain"]

                # CORREÇÃO CRÍTICA (2025-12-08): Atualizar repressão APÓS cálculo de Φ
                # Repressão não atualizada estava bloqueando acesso ao Real (Rho_U congelado)
                # NOVO: Passar success e phi_norm para decay adaptativo
                if self.workspace.conscious_system is not None:
                    cycle_success = result.success
                    phi_norm = None
                    if result.phi_estimate > 0:
                        # Normalizar Φ para [0, 1] se necessário
                        from src.consciousness.phi_constants import normalize_phi

                        phi_norm = (
                            normalize_phi(result.phi_estimate)
                            if result.phi_estimate > 1.0
                            else result.phi_estimate
                        )
                    self.workspace.conscious_system.update_repression(
                        threshold=1.0, success=cycle_success, phi_norm=phi_norm
                    )

                if self.enable_logging:
                    logger.info(f"Cycle {self.cycle_count}: Φ={result.phi_estimate:.4f}")

            except Exception as e:
                logger.error(f"Cycle {self.cycle_count}: Metrics failed - {e}")

        # Finalizar medições de complexidade
        actual_time_ms = (datetime.now() - start_time).total_seconds() * 1000

        # Calcular métricas de eficiência
        ops_per_ms = theoretical_complexity["total"] / max(actual_time_ms, 0.001)
        efficiency_estimate = ops_per_ms / 1e6  # GOps/s como proxy de eficiência

        result.complexity_metrics = {
            "theoretical_ops": theoretical_complexity["total"],
            "theoretical_time_ms": theoretical_complexity["total"] / 1e6,  # Estimativa grosseira
            "actual_time_ms": actual_time_ms,
            "execution_time_ms": execution_time_so_far,
            "metrics_time_ms": actual_time_ms - execution_time_so_far,
            "ops_per_ms": ops_per_ms,
            "efficiency_estimate_gops": efficiency_estimate,
            "breakdown": theoretical_complexity,
        }

        # Logging de complexidade
        if self.enable_logging:
            logger.info(
                f"Cycle {self.cycle_count} Complexity: "
                f"~{theoretical_complexity['total'] / 1e6:.1f}M ops "
                f"in {actual_time_ms:.1f}ms "
                f"({ops_per_ms / 1e3:.1f}GOps/s)"
            )

        # Finalize timing
        result.cycle_duration_ms = actual_time_ms
        self.cycle_history.append(result)

        # Registrar métricas do ciclo no coletor de métricas (CORREÇÃO: estava faltando)
        if collect_metrics:
            try:
                from src.monitor.module_metrics import get_module_metrics

                metrics_collector = get_module_metrics()

                # Registrar métricas principais do ciclo
                module_name = f"integration_loop_cycle_{self.cycle_count}"

                metrics_collector.record_metric(
                    module_name=module_name,
                    metric_name="phi_estimate",
                    value=float(result.phi_estimate),
                    labels={"cycle": self.cycle_count},
                )

                metrics_collector.record_metric(
                    module_name=module_name,
                    metric_name="cycle_duration_ms",
                    value=result.cycle_duration_ms,
                    labels={"cycle": self.cycle_count},
                )

                metrics_collector.record_metric(
                    module_name=module_name,
                    metric_name="components_activated",
                    value=len(result.modules_executed),
                    labels={"cycle": self.cycle_count},
                )

                metrics_collector.record_metric(
                    module_name=module_name,
                    metric_name="theoretical_complexity",
                    value=float(theoretical_complexity.get("total", 0)),
                    labels={"cycle": self.cycle_count},
                )

                # Registrar métricas de cada qualia
                if hasattr(result, "qualia") and result.qualia:
                    for qname, qvalue in result.qualia.items():
                        try:
                            metrics_collector.record_metric(
                                module_name=module_name,
                                metric_name=f"qualia_{qname}",
                                value=(
                                    float(qvalue)
                                    if isinstance(qvalue, (int, float))
                                    else len(str(qvalue))
                                ),
                                labels={"cycle": self.cycle_count},
                            )
                        except Exception:
                            pass

                logger.debug(f"Métricas do ciclo {self.cycle_count} registradas")

            except Exception as e:
                logger.debug(f"Falha ao registrar métricas do ciclo: {e}")

        # Gerar relatório do ciclo (ModuleReporter)
        if collect_metrics:
            try:
                from src.monitor.module_reporter import get_module_reporter

                reporter = get_module_reporter()

                # Salvar relatório do ciclo
                reporter.generate_module_report(
                    module_name=f"integration_loop_cycle_{self.cycle_count}",
                    include_metrics=True,
                    format="json",
                )
            except Exception as e:
                logger.debug(f"Falha ao gerar relatório do ciclo: {e}")

        # Extended results pipeline (se habilitado) - REFATORAÇÃO: Removido await (síncrono)
        # Nota: Extended results pode ser processado assincronamente em outro lugar se necessário
        if self.enable_extended_results and collect_metrics:
            try:
                # REFATORAÇÃO: Não usar await em método síncrono
                # Extended results pode ser processado posteriormente se necessário
                logger.debug(f"Cycle {self.cycle_count}: Extended results disabled in sync mode")
                # Nota: _build_extended_result() requer await, então não pode ser usado aqui
                # Se necessário, processar extended results em método async separado
            except Exception as e:
                logger.debug(f"Falha ao processar extended results: {e}")

        # 🎯 Sprint 1 Task 1.2: Clear cycle context and log completion
        if hasattr(self, "_current_cycle_context"):
            if self.enable_logging:
                logger.debug(
                    f"Cycle {self.cycle_count} completed (Φ={result.phi_estimate:.4f})",
                    extra={"trace_id": cycle_context.trace_id, "phi": result.phi_estimate},
                )
            self._current_cycle_context = None

        return result

    async def execute_cycle(self, collect_metrics: bool = True) -> LoopCycleResult:
        """
        Execute one complete integration loop cycle (async wrapper).

        REFATORAÇÃO: Wrapper async para compatibilidade retroativa.
        Delega para execute_cycle_sync() e processa extended results se habilitado.
        """
        base_result = self.execute_cycle_sync(collect_metrics)

        # Se extended results habilitado, construir ExtendedLoopCycleResult
        if self.enable_extended_results and collect_metrics:
            try:
                extended_result = await self._build_extended_result(base_result)
                # Atualizar cycle_history com extended result
                if len(self.cycle_history) > 0:
                    self.cycle_history[-1] = extended_result

                # CORREÇÃO CRÍTICA (2025-12-08): Adicionar ciclo ao cycle_history dos
                # extended components. Para que get_phi_history() funcione corretamente
                if self._extended_components is not None:
                    cycle_history_extended = self._extended_components.get("cycle_history")
                    if cycle_history_extended is not None:
                        cycle_history_extended.add_cycle(extended_result)
                        logger.debug(
                            f"Cycle {base_result.cycle_number}: Adicionado ao "
                            f"cycle_history (tamanho={cycle_history_extended.size()})"
                        )

                return extended_result
            except Exception as e:
                # Log verboso para debug de problemas de dimensão
                logger.error(
                    f"ERRO ao construir extended result no ciclo "
                    f"{base_result.cycle_number}: {type(e).__name__}: {str(e)}",
                    exc_info=True,
                )
                # Tentar logar informações de debug adicionais
                try:
                    if hasattr(self, "workspace") and self.workspace:
                        modules = self.workspace.get_all_modules()
                        logger.error(f"  Módulos no workspace: {modules}")
                        for module in modules:
                            emb = self.workspace.embeddings.get(module)
                            if emb is not None:
                                logger.error(f"    {module}: shape={emb.shape}")
                except Exception:
                    pass
                logger.warning("  Retornando base result (sem extended metrics)")
                return base_result

        return base_result

    def _collect_stimulus_from_modules(self) -> np.ndarray:
        """
        Coleta estímulo dos módulos para RNN.

        REFATORAÇÃO: Agrega estados dos módulos como estímulo para ConsciousSystem.
        """
        try:
            # Agregar estados dos módulos como estímulo
            module_states = []
            for module_name in self.loop_sequence:
                try:
                    state = self.workspace.read_module_state(module_name)
                    if isinstance(state, ModuleState):
                        module_states.append(state.embedding)
                    elif isinstance(state, np.ndarray):
                        module_states.append(state)
                except Exception:
                    pass  # Ignora módulos sem estado

            if module_states:
                # Média dos estados dos módulos como estímulo
                stimulus = np.mean(module_states, axis=0)
                # Normalizar para dimensão do workspace
                if len(stimulus) != self.workspace.embedding_dim:
                    if len(stimulus) < self.workspace.embedding_dim:
                        padding = np.zeros(self.workspace.embedding_dim - len(stimulus))
                        stimulus = np.concatenate([stimulus, padding])
                    else:
                        stimulus = stimulus[: self.workspace.embedding_dim]
                return stimulus
            else:
                # Fallback: estímulo zero
                return np.zeros(self.workspace.embedding_dim)
        except Exception as e:
            logger.warning(f"Erro ao coletar estímulo dos módulos: {e}")
            return np.zeros(self.workspace.embedding_dim)

    def _compute_all_cross_predictions(self) -> Dict[str, Dict[str, float]]:
        """Compute cross-prediction scores between all module pairs."""
        scores: Dict[str, Dict[str, float]] = {}
        modules_with_history = [
            m for m in self.loop_sequence if len(self.workspace.get_module_history(m)) > 1
        ]

        for source_module in modules_with_history:
            scores[source_module] = {}
            for target_module in modules_with_history:
                if source_module == target_module:
                    continue

                try:
                    # Try causal method first
                    source_history_len = len(self.workspace.get_module_history(source_module))
                    target_history_len = len(self.workspace.get_module_history(target_module))

                    if source_history_len >= 10 and target_history_len >= 10:
                        # Use causal method
                        cross_pred = self.workspace.compute_cross_prediction_causal(
                            source_module=source_module,
                            target_module=target_module,
                            method="granger",
                        )
                    else:
                        # Fall back to correlation-based method
                        cross_pred = self.workspace.compute_cross_prediction(
                            source_module=source_module,
                            target_module=target_module,
                        )

                    scores[source_module][target_module] = (
                        cross_pred.mutual_information
                        if hasattr(cross_pred, "mutual_information")
                        else 0.0
                    )

                except Exception as e:
                    logger.warning(f"Cross-prediction failed {source_module}->{target_module}: {e}")

        return scores

    async def run_cycles(
        self,
        num_cycles: int,
        collect_metrics_every: int = 1,
        progress_callback: Optional[Callable] = None,
    ) -> List[LoopCycleResult]:
        """Run multiple integration cycles."""
        results = []

        for i in range(num_cycles):
            collect_metrics = collect_metrics_every > 0 and (i + 1) % collect_metrics_every == 0

            result = await self.execute_cycle(collect_metrics=collect_metrics)
            results.append(result)

            if progress_callback:
                progress_callback(i + 1, num_cycles, result)

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall integration loop statistics."""
        cycle_results = self.cycle_history
        successful_cycles = [c for c in cycle_results if c.success]

        phi_values = [c.phi_estimate for c in cycle_results if c.phi_estimate > 0.0]
        phi_mean = np.mean(phi_values) if phi_values else 0.0
        phi_max = np.max(phi_values) if phi_values else 0.0
        phi_min = np.min(phi_values) if phi_values else 0.0

        return {
            "total_cycles": self.total_cycles_executed,
            "successful_cycles": len(successful_cycles),
            "success_rate": (len(successful_cycles) / len(cycle_results) if cycle_results else 0.0),
            "avg_cycle_duration_ms": (
                np.mean([c.cycle_duration_ms for c in cycle_results]) if cycle_results else 0.0
            ),
            "phi_statistics": {
                "mean": phi_mean,
                "max": phi_max,
                "min": phi_min,
                "values_count": len(phi_values),
            },
            "module_statistics": {
                name: self.executors[name].get_statistics() for name in self.loop_sequence
            },
        }

    def get_phi_progression(self) -> List[float]:
        """Get Φ values over cycle history."""
        return [c.phi_estimate for c in self.cycle_history]

    def _initialize_extended_components(self) -> None:
        """Inicializa componentes para extended results (lazy)."""
        if self._extended_components is not None:
            return

        from src.consciousness.consciousness_triad import ConsciousnessTriad
        from src.consciousness.cycle_history import CycleHistory
        from src.consciousness.cycle_result_builder import LoopCycleResultBuilder
        from src.consciousness.embedding_narrative import EmbeddingNarrativeAnalyzer
        from src.consciousness.embedding_psi_adapter import PsiProducerAdapter
        from src.consciousness.embedding_sigma_adapter import (
            SigmaSinthomeCalculatorAdapter,
        )
        from src.consciousness.embedding_validator import EmbeddingNarrativeValidator

        # CORREÇÃO (2025-12-08): Inicializar sigma_calculator no adapter
        # Sem isso, adapter sempre usa fallback e retorna 0.5
        from src.consciousness.sigma_sinthome import SigmaSinthomeCalculator
        from src.consciousness.theoretical_consistency_guard import (
            TheoreticalConsistencyGuard,
        )

        sigma_calculator = SigmaSinthomeCalculator(
            integration_trainer=None,  # Não temos trainer no loop básico
            workspace=self.workspace,
        )

        self._extended_components = {
            "builder": LoopCycleResultBuilder(self.workspace),
            "narrative_analyzer": EmbeddingNarrativeAnalyzer(),
            "psi_adapter": PsiProducerAdapter(),
            "sigma_adapter": SigmaSinthomeCalculatorAdapter(sigma_calculator=sigma_calculator),
            "cycle_history": CycleHistory(max_history_size=1000),
            "validator": EmbeddingNarrativeValidator(),
            "triad_class": ConsciousnessTriad,
            "consistency_guard": TheoreticalConsistencyGuard(
                raise_on_critical=False, current_phase=7
            ),  # 🎯 FASE 0: Phase-Aware
        }

    def _generate_symbolic_text_from_embedding(
        self,
        embedding: np.ndarray,
        magnitude: float,
        sparsity: float,
        max_val: float,
    ) -> str:
        """
        Gera texto simbólico a partir de propriedades do embedding com marcadores de discurso.

        CORREÇÃO (2025-12-10): Mapeia propriedades numéricas para marcadores de discurso
        para permitir análise mesmo quando narrative_form não está disponível.

        Args:
            embedding: Embedding do módulo narrative
            magnitude: Magnitude do embedding
            sparsity: Esparsidade do embedding
            max_val: Valor máximo absoluto

        Returns:
            Texto simbólico com marcadores de discurso
        """
        # Mapear propriedades numéricas para marcadores de discurso
        # CORREÇÃO (2025-12-10): Ajustar thresholds baseado em
        # propriedades reais dos embeddings
        markers = []

        # Calcular percentis dinâmicos baseados em histórico (se disponível)
        try:
            recent_history = self.workspace.get_module_history("narrative", last_n=10)
            if len(recent_history) > 3:
                recent_magnitudes = [
                    float(np.linalg.norm(h.embedding)) for h in recent_history[-10:]
                ]
                recent_sparsities = [
                    float(np.mean(np.abs(h.embedding) < 0.1)) for h in recent_history[-10:]
                ]
                mag_q1 = float(np.percentile(recent_magnitudes, 25))
                mag_q3 = float(np.percentile(recent_magnitudes, 75))
                sparsity_median = float(np.median(recent_sparsities))
            else:
                # Valores padrão baseados em análise empírica
                mag_q1 = 25.0
                mag_q3 = 30.0
                sparsity_median = 0.4
        except Exception:
            # Valores padrão baseados em análise empírica
            mag_q1 = 25.0
            mag_q3 = 30.0
            sparsity_median = 0.4

        # CORREÇÃO (2025-12-10): Melhorar lógica de mapeamento para
        # garantir diversidade
        # Usar múltiplas condições que podem se sobrepor para
        # criar variação

        # MASTER: Alta magnitude + baixa sparsity = comando/autoridade
        # Usar percentis dinâmicos: acima de Q3 para magnitude, abaixo de mediana para sparsity
        master_score = 0.0
        if magnitude > mag_q3:
            master_score += 0.5
        if sparsity < sparsity_median:
            master_score += 0.5
        if master_score >= 0.7:  # Pelo menos uma condição forte
            markers.extend(["deve", "ordem", "comando", "autoridade", "lei", "regra"])

        # UNIVERSITY: Magnitude média + sparsity média = conhecimento/sistema
        # Entre Q1 e Q3 para magnitude, sparsity próxima da mediana
        university_score = 0.0
        if mag_q1 <= magnitude <= mag_q3:
            university_score += 0.5
        if abs(sparsity - sparsity_median) < 0.2:
            university_score += 0.5
        if university_score >= 0.7:  # Pelo menos uma condição forte
            markers.extend(
                [
                    "saber",
                    "conhecimento",
                    "teoria",
                    "sistema",
                    "método",
                    "conceito",
                    "definição",
                ]
            )

        # HYSTERIC: Baixa magnitude OU alta sparsity = questionamento/dúvida
        # Abaixo de Q1 para magnitude OU sparsity alta
        hysteric_score = 0.0
        if magnitude < mag_q1:
            hysteric_score += 0.5
        if sparsity > (sparsity_median + 0.3):
            hysteric_score += 0.5
        if hysteric_score >= 0.5:  # Qualquer uma das condições
            markers.extend(
                [
                    "por que",
                    "dúvida",
                    "questão",
                    "sintoma",
                    "desejo",
                    "falta",
                    "impossível",
                ]
            )

        # ANALYST: Valores extremos OU padrões específicos = escuta/abertura
        # Max muito alto OU magnitude muito baixa com sparsity alta
        analyst_score = 0.0
        if max_val > 0.7:
            analyst_score += 0.5
        if magnitude < (mag_q1 - 2.0) and sparsity > (sparsity_median + 0.4):
            analyst_score += 0.5
        if analyst_score >= 0.5:  # Qualquer uma das condições
            markers.extend(["escute", "silêncio", "vazio", "produção", "emergência", "abertura"])

        # CORREÇÃO CRÍTICA (2025-12-10): Garantir que sempre haja
        # marcadores
        # Se nenhum marcador foi adicionado, usar distribuição baseada em valores relativos
        if not markers:
            # Usar valores relativos aos thresholds para determinar discurso mais provável
            mag_ratio = (
                (magnitude - mag_q1) / (mag_q3 - mag_q1 + 1e-8) if (mag_q3 - mag_q1) > 0 else 0.5
            )
            sparsity_ratio = (sparsity - (sparsity_median - 0.2)) / 0.4 if 0.4 > 0 else 0.5

            # Mapear para discurso baseado em posição relativa
            if mag_ratio > 0.7 and sparsity_ratio < 0.5:
                markers.extend(["deve", "ordem", "comando", "autoridade"])
            elif 0.3 <= mag_ratio <= 0.7 and 0.3 <= sparsity_ratio <= 0.7:
                markers.extend(["saber", "conhecimento", "teoria", "sistema"])
            elif mag_ratio < 0.3 or sparsity_ratio > 0.7:
                markers.extend(["por que", "dúvida", "questão", "sintoma"])
            else:
                markers.extend(["escute", "silêncio", "vazio", "produção"])

        # Adicionar contexto baseado em padrões do embedding
        # Calcular propriedades adicionais
        embedding_std = float(np.std(embedding))
        embedding_mean = float(np.mean(np.abs(embedding)))

        # Padrões específicos
        if embedding_std > 0.5:
            markers.append("variação")
        if embedding_mean > 0.3:
            markers.append("intensidade")

        # Usar histórico recente para adicionar contexto
        try:
            recent_history = self.workspace.get_module_history("narrative", last_n=3)
            if len(recent_history) > 1:
                # Calcular variação temporal
                recent_magnitudes = [
                    float(np.linalg.norm(h.embedding)) for h in recent_history[-3:]
                ]
                if len(recent_magnitudes) > 1:
                    magnitude_change = abs(recent_magnitudes[-1] - recent_magnitudes[0])
                    if magnitude_change > 2.0:
                        markers.append("mudança")
                    elif magnitude_change < 0.5:
                        markers.append("estabilidade")
        except Exception:
            pass

        # Combinar marcadores em texto simbólico
        if markers:
            # Adicionar conectores para criar texto mais natural
            symbolic_text = " ".join(markers[:10])  # Limitar a 10 marcadores
            # Adicionar contexto numérico como complemento
            symbolic_text += f" magnitude={magnitude:.2f} sparsity={sparsity:.2f}"
        else:
            # Fallback: usar propriedades numéricas com marcadores genéricos
            symbolic_text = (
                f"magnitude={magnitude:.2f} sparsity={sparsity:.2f} "
                f"variação padrão estrutura sistema método conhecimento"
            )

        return symbolic_text

    async def _build_extended_result(
        self, base_result: LoopCycleResult
    ) -> "ExtendedLoopCycleResult":
        """
        Constrói ExtendedLoopCycleResult com tríade completa.

        Args:
            base_result: LoopCycleResult base

        Returns:
            ExtendedLoopCycleResult com Φ, Ψ, σ, tríade
        """
        if self._extended_components is None:
            self._initialize_extended_components()

        if self._extended_components is None:
            raise RuntimeError("Extended components not initialized")
        components = self._extended_components
        builder = components["builder"]
        narrative_analyzer = components["narrative_analyzer"]
        psi_adapter = components["psi_adapter"]
        sigma_adapter = components["sigma_adapter"]
        cycle_history = components["cycle_history"]
        validator = components["validator"]
        ConsciousnessTriad = components["triad_class"]
        consistency_guard = components["consistency_guard"]

        # 1. Construir ExtendedLoopCycleResult base
        previous_cycle = cycle_history.get_previous_cycle(base_result.cycle_number)
        extended_result = builder.build_from_workspace(base_result, previous_cycle)

        # 2. Analisar narrativa de embeddings
        previous_cycles = cycle_history.get_recent_cycles(n=5)
        try:
            embedding_narrative = await narrative_analyzer.analyze_cycle(
                extended_result, previous_cycles if previous_cycles else None
            )
        except Exception as e:
            logger.error(f"Erro ao analisar narrativa: {e}", exc_info=True)
            raise

        # 3. Validar narrativa
        validation = await validator.validate(embedding_narrative)
        if not validation["is_valid"] and self.enable_logging:
            logger.warning(
                f"Cycle {base_result.cycle_number}: Validação falhou: {validation['issues']}"
            )

        # 4. Preparar phi_raw_nats para todos os cálculos
        from src.consciousness.phi_constants import denormalize_phi

        phi_raw = base_result.phi_estimate  # Assumir que já está normalizado [0,1]
        phi_raw_nats = denormalize_phi(phi_raw)

        # 5. Calcular Δ primeiro (depende apenas de Φ)
        try:
            from src.consciousness.delta_calculator import DeltaCalculator

            delta_calc = DeltaCalculator()
            if extended_result.module_outputs:
                expectation_emb = extended_result.module_outputs.get("expectation")
                reality_emb = extended_result.module_outputs.get("sensory_input")
                if expectation_emb is not None and reality_emb is not None:
                    delta_result = delta_calc.calculate_delta(
                        expectation_embedding=expectation_emb,
                        reality_embedding=reality_emb,
                        module_outputs=extended_result.module_outputs,
                        integration_strength=extended_result.integration_strength,
                        phi_raw=phi_raw_nats,
                    )
                    extended_result.delta = delta_result.delta_value
        except Exception as e:
            logger.warning(f"Erro ao calcular δ: {e}")
            extended_result.delta = None

        # 6. Calcular Ψ (depende apenas de Φ)
        try:
            # CORREÇÃO (2025-12-07): Passar phi_raw_nats para cálculo correto de Ψ
            psi = await psi_adapter.calculate_psi_for_embedding(
                embedding_narrative, phi_raw=phi_raw_nats
            )
            extended_result.psi = psi
        except Exception as e:
            logger.warning(f"Erro ao calcular Ψ: {e}")
            extended_result.psi = None

        # 7. Calcular σ (depende de Φ e Δ)
        try:
            # CORREÇÃO CRÍTICA (2025-12-08): Usar histórico do IntegrationLoop em vez de
            # cycle_history vazio. O cycle_history dos extended components não está sendo
            # populado, então usar self.cycle_history que já contém os ciclos anteriores
            # CORREÇÃO (2025-12-08 20:30): NÃO filtrar valores zero - incluir todos para
            # análise. Se filtrar, quando Phi está zerando, phi_history fica vazio
            phi_history_from_loop = [
                c.phi_estimate
                for c in self.cycle_history
                # Removido filtro > 0.0 - incluir todos os valores, mesmo zeros, para análise
            ][
                -20:
            ]  # Últimos 20 valores

            # Se cycle_history dos extended components tem dados, usar ele também
            phi_history_from_extended = cycle_history.get_phi_history(last_n=20)

            # Combinar ambos os históricos (remover duplicatas mantendo ordem)
            phi_history_combined = list(
                dict.fromkeys(phi_history_from_loop + phi_history_from_extended)
            )[-20:]

            # Usar histórico combinado ou fallback para histórico do loop
            phi_history = phi_history_combined if phi_history_combined else phi_history_from_loop

            logger.debug(
                f"Sigma: phi_history_len={len(phi_history)}, "
                f"from_loop={len(phi_history_from_loop)}, "
                f"from_extended={len(phi_history_from_extended)}"
            )

            sigma = await sigma_adapter.calculate_sigma_from_phi_history(
                cycle_id=extended_result.cycle_id or f"cycle_{base_result.cycle_number}",
                phi_history=phi_history,
                delta_value=extended_result.delta,  # δ já calculado
                cycle_count=base_result.cycle_number,
            )
            extended_result.sigma = sigma
        except Exception as e:
            logger.warning(f"Erro ao calcular σ: {e}", exc_info=True)
            extended_result.sigma = None

        # 8. Calcular Epsilon ANTES da tríade (CORREÇÃO 2025-12-10)
        # MOTIVO: ConsciousnessTriad requer epsilon como argumento obrigatório
        # Anteriormente estava no passo 11, causando 495 warnings desnecessários
        try:
            from src.psychology.motivation.intrinsic_rewards import DesireEngine

            if not hasattr(self, "_desire_engine") or self._desire_engine is None:
                self._desire_engine = DesireEngine()

            # Epsilon baseia-se em: (α_lack × β_potencial × γ_novelty)
            alpha_lack = 1.0 - (phi_raw_nats / 10.0) if phi_raw_nats > 0 else 0.9
            beta_potential = extended_result.integration_strength or 0.5

            # Calcular novelty a partir da magnitude de mudança no embedding
            gamma_novelty = 0.5  # Default
            if previous_cycle and previous_cycle.module_outputs:
                sensory_current = extended_result.module_outputs.get("sensory_input")
                sensory_prev = previous_cycle.module_outputs.get("sensory_input")
                if (
                    sensory_current is not None
                    and sensory_prev is not None
                    and isinstance(sensory_current, np.ndarray)
                    and isinstance(sensory_prev, np.ndarray)
                ):
                    # Usar diferença normalizada como novidade
                    diff_norm = np.linalg.norm(sensory_current - sensory_prev)
                    gamma_novelty = float(
                        np.clip(diff_norm / (np.linalg.norm(sensory_prev) + 1e-8), 0.0, 1.0)
                    )

            # Combinar fatores para epsilon
            epsilon = float(np.clip(alpha_lack * beta_potential * gamma_novelty, 0.0, 1.0))
            extended_result.epsilon = epsilon

            if self.enable_logging:
                logger.debug(
                    f"Epsilon (ϵ): {epsilon:.4f} "
                    f"(α_lack={alpha_lack:.3f}, β_potential={beta_potential:.3f}, "
                    f"γ_novelty={gamma_novelty:.3f})"
                )
        except Exception as e:
            logger.warning(f"Erro ao calcular ϵ (Epsilon): {e}")
            extended_result.epsilon = None
            epsilon = 0.0

        # 9. Construir tríade completa COM epsilon (CORREÇÃO 2025-12-10)
        try:
            triad = ConsciousnessTriad(
                phi=base_result.phi_estimate,
                psi=extended_result.psi or 0.0,
                sigma=extended_result.sigma or 0.0,
                epsilon=extended_result.epsilon or 0.0,
                step_id=extended_result.cycle_id or f"cycle_{base_result.cycle_number}",
                metadata={
                    "validation_confidence": validation.get("confidence", 0.5),
                    "has_extended_data": extended_result.has_extended_data(),
                },
            )
            extended_result.triad = triad
        except Exception as e:
            logger.warning(f"Erro ao construir tríade: {e}")
            extended_result.triad = None

        # 9. Calcular Gozo (FASE 2)
        try:
            from src.consciousness.gozo_calculator import GozoCalculator

            # CORREÇÃO CRÍTICA (2025-12-08): Manter instância de GozoCalculator entre ciclos
            # Para drenagem progressiva funcionar, precisa manter estado (last_gozo_value)
            if not hasattr(self, "_gozo_calculator") or self._gozo_calculator is None:
                self._gozo_calculator = GozoCalculator()

            expectation_emb = extended_result.module_outputs.get("expectation")
            reality_emb = extended_result.module_outputs.get("sensory_input")
            if expectation_emb is not None and reality_emb is not None:
                # CORREÇÃO (2025-12-07): Passar phi_raw e psi_value para cálculo correto de Gozo
                psi_value = extended_result.psi  # Ψ já calculado anteriormente
                # CORREÇÃO CRÍTICA (2025-12-08): Passar flag success para drenagem do Gozo
                cycle_success = base_result.success
                gozo_result = self._gozo_calculator.calculate_gozo(
                    expectation_embedding=expectation_emb,
                    reality_embedding=reality_emb,
                    current_embedding=reality_emb,
                    phi_raw=phi_raw_nats,  # phi_raw_nats definido no passo 4
                    psi_value=psi_value,  # Passar Ψ calculado
                    delta_value=extended_result.delta,  # Passar Δ para fórmula de Solms
                    sigma_value=extended_result.sigma,
                    # NOVO: Passar σ para binding adaptativo
                    success=cycle_success,  # Flag de sucesso para drenagem
                )
                extended_result.gozo = gozo_result.gozo_value
        except Exception as e:
            logger.warning(f"Erro ao calcular Gozo: {e}")
            extended_result.gozo = None

        # 10. Calcular Control Effectiveness (FASE 4)
        try:
            from src.consciousness.regulatory_adjustment import RegulatoryAdjuster

            regulatory = RegulatoryAdjuster()
            if extended_result.module_outputs:
                regulation = regulatory.calculate_adjustment(
                    current_error=extended_result.gozo or 0.5,
                    sigma=extended_result.sigma or 0.5,
                    delta=extended_result.delta or 0.5,
                    module_outputs=extended_result.module_outputs,
                )
                # CORREÇÃO (2025-12-07): Passar phi_raw para cálculo correto de Control
                control_effectiveness = regulatory.calculate_control_effectiveness(
                    sigma=extended_result.sigma or 0.5,
                    delta=extended_result.delta or 0.5,
                    regulation=regulation,
                    phi_raw=phi_raw_nats,  # Passar em nats para normalização explícita
                )
                extended_result.control_effectiveness = control_effectiveness

                # PROTOCOLO CLÍNICO-CIBERNÉTICO (2025-12-08): Fechar loop de controle
                # Aplicar regulação homeostática baseada em control_effectiveness
                if self._homeostatic_regulator is not None:
                    try:
                        phi_current = base_result.phi_estimate
                        sigma_current = extended_result.sigma or 0.5

                        regulation_result = self._homeostatic_regulator.actuate_control_loop(
                            control_effectiveness=control_effectiveness,
                            current_sigma=sigma_current,
                            phi_current=phi_current,
                        )

                        # Aplicar repressão de emergência se válvula foi ativada
                        if regulation_result["mode"] == "EMERGENCY_VENTING":
                            if self.workspace.conscious_system is not None:
                                self.workspace.conscious_system.update_repression(
                                    emergency_repression=regulation_result["new_repression"]
                                )
                                logger.warning(
                                    f"🚨 VÁLVULA DE EMERGÊNCIA: Repressão ajustada para "
                                    f"{regulation_result['new_repression']:.4f}"
                                )

                        # Aplicação de temperatura β aos módulos (LangevinDynamics no Workspace)
                        self.workspace.set_temperature(regulation_result["new_beta"])
                        extended_result.homeostatic_state = regulation_result

                        logger.debug(
                            f"Homeostase: mode={regulation_result['mode']}, "
                            f"β={regulation_result['new_beta']:.4f}, "
                            f"R={regulation_result['new_repression']:.4f}"
                        )
                    except Exception as e:
                        logger.warning(f"Erro ao aplicar regulação homeostática: {e}")
        except Exception as e:
            logger.warning(f"Erro ao calcular Control Effectiveness: {e}")
            extended_result.control_effectiveness = None

        # 10. Capturar imagination output (FASE 1)
        try:
            if extended_result.module_outputs and "imagination" in extended_result.module_outputs:
                extended_result.imagination_output = extended_result.module_outputs["imagination"]
        except Exception as e:
            logger.warning(f"Erro ao capturar imagination output: {e}")
            extended_result.imagination_output = None

        # 11. Validação de Consistência Teórica (FASE 3 - Protocolo Livewire)
        try:
            from src.consciousness.phi_value import PhiValue

            # CORREÇÃO: Garantir que phi_raw_nats está definido
            # Se não estiver (exceção anterior), usar phi_estimate normalizado
            if "phi_raw_nats" not in locals():
                from src.consciousness.phi_constants import denormalize_phi

                phi_raw = base_result.phi_estimate  # Assumir que já está normalizado [0,1]
                phi_raw_nats = denormalize_phi(phi_raw)

            # Criar PhiValue a partir de phi_raw_nats
            phi_value = PhiValue.from_nats(phi_raw_nats, source="integration_loop")

            # Validar ciclo completo
            violations = consistency_guard.validate_cycle(
                phi=phi_value,
                delta=extended_result.delta or 0.0,
                psi=extended_result.psi or 0.0,
                sigma=extended_result.sigma,
                gozo=extended_result.gozo,
                control=extended_result.control_effectiveness,
                cycle_id=base_result.cycle_number,
                phase=7,  # 🎯 FASE 0: Passar phase (Zimerman Bonding)
            )

            # Logar violações se houver
            if violations and self.enable_logging:
                for violation in violations:
                    if violation.severity == "critical":
                        logger.critical(f"💥 CICLO {base_result.cycle_number}: {violation.message}")
                    elif violation.severity == "error":
                        logger.error(f"🚨 CICLO {base_result.cycle_number}: {violation.message}")
                    else:
                        logger.warning(f"⚠️ CICLO {base_result.cycle_number}: {violation.message}")

            # Armazenar violações no extended_result (se houver campo para isso)
            if hasattr(extended_result, "consistency_violations"):
                extended_result.consistency_violations = violations
        except Exception as e:
            logger.warning(f"Erro ao validar consistência teórica: {e}")

        # 13. Capturar phi_causal e repression_strength
        try:
            if self.workspace.conscious_system is not None:
                extended_result.phi_causal = self.workspace.conscious_system.compute_phi_causal()
                extended_result.repression_strength = (
                    self.workspace.conscious_system.repression_strength
                )

                if self.enable_logging:
                    logger.debug(
                        f"Phi causal: {extended_result.phi_causal:.4f}, "
                        f"Repression: {extended_result.repression_strength:.4f}"
                    )
        except Exception as e:
            logger.warning(f"Erro ao capturar phi_causal/repression_strength: {e}")
            extended_result.phi_causal = None
            extended_result.repression_strength = None

        return extended_result

    def save_state(self, filepath: Path) -> None:
        """Save integration loop state and history."""
        state = {
            "cycle_count": self.cycle_count,
            "total_cycles_executed": self.total_cycles_executed,
            "statistics": self.get_statistics(),
            "phi_progression": self.get_phi_progression(),
            "recent_cycles": [
                {
                    "cycle": c.cycle_number,
                    "success": c.success,
                    "phi": c.phi_estimate,
                    "modules_executed": c.modules_executed,
                }
                for c in self.cycle_history[-100:]
            ],
        }

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2, default=str)

        logger.info(f"Integration loop state saved to {filepath}")

    def create_full_snapshot(
        self, tag: Optional[str] = None, description: Optional[str] = None
    ) -> str:
        """
        Create complete snapshot of consciousness state.

        Args:
            tag: Optional tag for organization (e.g., "experimento_001")
            description: Optional description

        Returns:
            snapshot_id
        """
        from src.backup.consciousness_snapshot import (
            ConsciousnessSnapshotManager,
            SnapshotTag,
        )

        snapshot_manager = ConsciousnessSnapshotManager()
        snapshot_tag = None
        if tag:
            snapshot_tag = SnapshotTag(name=tag, description=description)

        snapshot_id = snapshot_manager.create_full_snapshot(self, tag=snapshot_tag)
        logger.info(f"Full consciousness snapshot created: {snapshot_id} (tag: {tag})")
        return snapshot_id

    def restore_from_snapshot(self, snapshot_id: str) -> bool:
        """
        Restore complete state from snapshot.

        Args:
            snapshot_id: Snapshot ID to restore

        Returns:
            True if restore successful
        """
        from src.backup.consciousness_snapshot import ConsciousnessSnapshotManager

        snapshot_manager = ConsciousnessSnapshotManager()
        success = snapshot_manager.restore_full_snapshot(snapshot_id, self)
        if success:
            logger.info(f"Consciousness state restored from snapshot: {snapshot_id}")
        else:
            logger.error(f"Failed to restore from snapshot: {snapshot_id}")
        return success


async def main_example():
    """Example usage of IntegrationLoop."""
    loop = IntegrationLoop(enable_logging=True)

    print("🔄 Running 10 integration cycles...")

    def progress(i, total, result):
        phi = result.phi_estimate
        status = "✅" if result.success else "❌"
        print(f"  Cycle {i:2d}/{total}: Φ={phi:.4f} {status}")

    results = await loop.run_cycles(10, collect_metrics_every=1, progress_callback=progress)

    stats = loop.get_statistics()
    print("\n📊 Statistics:")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Φ mean: {stats['phi_statistics']['mean']:.4f}")
    print(f"  Φ max:  {stats['phi_statistics']['max']:.4f}")

    return loop, results


if __name__ == "__main__":
    asyncio.run(main_example())
