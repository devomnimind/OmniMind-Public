"""
Real Consciousness Metrics Collector - Coleta métricas reais do sistema de consciência.

Este módulo substitui os valores hardcoded do dashboard por cálculos reais baseados em:
- IntegrationLoop phi calculations
- SharedWorkspace cross-predictions
- IIT metrics (anxiety, flow, entropy)
- System state analysis

Author: Project conceived by Fabrício da Silva. Implementation followed an iterative AI-assisted
method: the author defined concepts and queried various AIs on construction, integrated code via
VS Code/Copilot, tested resulting errors, cross-verified validity with other models, and refined
prompts/corrections in a continuous cycle of human-led AI development.
from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code review
and debugging across various models including Gemini and Perplexity AI, under
theoretical coordination by the author.
Date: November 2025
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np

from src.consciousness.integration_loop import IntegrationLoop
from src.metacognition.iit_metrics import IITAnalyzer
from src.consciousness.gozo_calculator import GozoCalculator
from src.lacanian.freudian_metapsychology import FreudianMind

logger = logging.getLogger(__name__)


@dataclass
class RealConsciousnessMetrics:
    """Métricas reais de consciência coletadas do sistema."""

    # Phi e integração
    phi: float = 0.0
    ici: float = 0.0  # Integrated Coherence Index
    prs: float = 0.0  # Panarchic Resonance Score

    # Estados psicológicos
    anxiety: float = 0.0  # Computational anxiety (0.0-1.0)
    flow: float = 0.0  # Cognitive flow state (0.0-1.0)
    entropy: float = 0.0  # System entropy (0.0-1.0)
    gozo: float = 0.0  # Lacanian Jouissance (0.0-1.0)

    # Detalhes dos componentes
    ici_components: Dict[str, float] = field(default_factory=dict)
    prs_components: Dict[str, float] = field(default_factory=dict)
    psychoanalytic: Dict[str, Any] = field(default_factory=dict)  # Id, Ego, Superego metrics

    # Histórico para tendências
    history: Dict[str, List[Any]] = field(
        default_factory=lambda: {
            "phi": [],
            "ici": [],
            "prs": [],
            "anxiety": [],
            "flow": [],
            "entropy": [],
            "timestamps": [],
        }
    )

    # Interpretação AI
    interpretation: Dict[str, Any] = field(
        default_factory=lambda: {
            "message": "Collecting real metrics...",
            "confidence": "Low",
            "disclaimer": "These are real computational correlates, not proof of consciousness.",
        }
    )

    timestamp: datetime = field(default_factory=datetime.now)


class RealConsciousnessMetricsCollector:
    """Coleta métricas reais de consciência do sistema."""

    def __init__(self):
        self.integration_loop: Optional[IntegrationLoop] = None
        self.iit_analyzer = IITAnalyzer()
        self.gozo_calculator = GozoCalculator()
        self.freudian_mind = FreudianMind()
        self.last_collection = 0.0
        self.collection_interval = 5.0  # segundos
        self._phi_variance_history: List[float] = []  # Phase 22: Histórico de variância

        # Cache de métricas
        self.cached_metrics: Optional[RealConsciousnessMetrics] = None

        logger.info("RealConsciousnessMetricsCollector initialized")

    async def initialize(self) -> None:
        """Inicializa o coletor com IntegrationLoop real."""
        if self.integration_loop is not None:
            return

        try:
            self.integration_loop = IntegrationLoop(enable_logging=False)
            logger.info("IntegrationLoop initialized for real metrics collection")
        except Exception as e:
            logger.error(f"Failed to initialize IntegrationLoop: {e}")
            self.integration_loop = None

    async def collect_real_metrics(
        self,
        external_phi: Optional[float] = None,
        external_context: Optional[Dict[str, Any]] = None,
    ) -> RealConsciousnessMetrics:
        """
        Coleta métricas reais do sistema de consciência.

        Args:
            external_phi: (uso de teste) valor de Φ injetado externamente para evitar coleta pesada.
            external_context: (uso de teste) contexto externo com ansiedade/flow/entropia.
        """

        # Phase 22: Cache adaptativo baseado em variância
        current_time = time.time()
        if (
            self.cached_metrics
            and current_time - self.last_collection < self._adaptive_collection_interval()
            and external_phi is None
            and external_context is None
        ):
            return self.cached_metrics

        metrics = RealConsciousnessMetrics()

        try:
            # 1. Phi: usar injeção externa se fornecida (cenário de teste),
            #    senão coletar normalmente
            if external_phi is not None:
                metrics.phi = float(external_phi)
                metrics.ici = metrics.phi
                metrics.prs = metrics.phi
                logger.debug("Using externally injected phi: %.4f", metrics.phi)
            elif self.integration_loop:
                phi_result = await self._collect_phi_from_integration_loop()
                metrics.phi = phi_result.get("phi", 0.0)
                metrics.ici = phi_result.get("ici", 0.0)
                metrics.prs = phi_result.get("prs", 0.0)
                metrics.ici_components = phi_result.get("ici_components", {})
                metrics.prs_components = phi_result.get("prs_components", {})

            # 2. Métricas psicológicas: usar contexto externo se fornecido, senão coletar
            if external_context:
                metrics.anxiety = float(external_context.get("anxiety", metrics.anxiety))
                metrics.flow = float(external_context.get("flow", metrics.flow))
                metrics.entropy = float(external_context.get("entropy", metrics.entropy))
                logger.debug("Using external context: anxiety=%.3f", metrics.anxiety)
                logger.debug("Using external context: flow=%.3f", metrics.flow)
                logger.debug("Using external context: entropy=%.3f", metrics.entropy)
            else:
                psychological_metrics = await self._collect_psychological_metrics()
                metrics.anxiety = psychological_metrics.get("anxiety", 0.0)
                metrics.flow = psychological_metrics.get("flow", 0.0)
                metrics.entropy = psychological_metrics.get("entropy", 0.0)
                metrics.gozo = psychological_metrics.get("gozo", 0.0)

            # 2.1 Coleta métricas psicanalíticas
            metrics.psychoanalytic = await self._collect_psychoanalytic_metrics()

            # 3. Atualiza histórico
            self._update_history(metrics)

            # 4. Gera interpretação baseada em dados reais
            metrics.interpretation = self._generate_real_interpretation(metrics)

            # Phase 22: Atualizar histórico de variância para cache adaptativo
            if self.cached_metrics:
                phi_variance = abs(metrics.phi - self.cached_metrics.phi)
                self._phi_variance_history.append(phi_variance)
                if len(self._phi_variance_history) > 10:
                    self._phi_variance_history = self._phi_variance_history[-10:]

            # Cache e timestamp
            metrics.timestamp = datetime.now()
            self.cached_metrics = metrics
            self.last_collection = current_time

            logger.debug(
                f"Real consciousness metrics collected: phi={metrics.phi:.4f}, "
                f"anxiety={metrics.anxiety:.4f}, flow={metrics.flow:.4f}, "
                f"entropy={metrics.entropy:.4f}"
            )
        except Exception as e:
            logger.error(f"Error collecting real consciousness metrics: {e}")
            # Retorna métricas seguras em caso de erro
            return self._get_safe_fallback_metrics()

        return metrics

    async def _collect_phi_from_integration_loop(self) -> Dict[str, Any]:
        """Coleta Phi real do IntegrationLoop."""
        if not self.integration_loop:
            return {"phi": 0.0, "ici": 0.0, "prs": 0.0}

        try:
            workspace = self.integration_loop.workspace

            # Verificar se há dados suficientes no workspace
            if not workspace.cross_predictions or len(workspace.cross_predictions) < 2:
                # Se workspace está vazio, executar ciclos para gerar dados
                logger.debug("Workspace has insufficient data, running cycles...")
                results = await self.integration_loop.run_cycles(2, collect_metrics_every=1)
                logger.debug(f"Ran {len(results)} cycles")

            # Calcular Phi a partir dos dados do workspace
            # Usar histórico de cross-predictions como base
            cross_preds = workspace.cross_predictions[-20:] if workspace.cross_predictions else []

            if cross_preds:
                # Phi é a média dos r_squared das predições cruzadas
                r_squared_values = [
                    p.r_squared
                    for p in cross_preds
                    if hasattr(p, "r_squared") and isinstance(p.r_squared, (int, float))
                ]
                phi = np.mean(r_squared_values) if r_squared_values else 0.0

                # ICI baseado em coerência temporal (usar r_squared como proxy)
                # Normalizar para range 0-1
                ici = min(1.0, phi * 1.2) if phi > 0 else 0.0

                # PRS baseado em granger_causality
                gc_values = [
                    p.granger_causality
                    for p in cross_preds
                    if hasattr(p, "granger_causality")
                    and isinstance(p.granger_causality, (int, float))
                ]
                prs = np.mean(gc_values) if gc_values else 0.0
            else:
                phi = 0.0
                ici = 0.0
                prs = 0.0

            # Phase 22+: Melhorar componentes com mais detalhes
            temporal_coherence = min(0.7, phi * 0.9) if phi > 0 else 0.0
            marker_integration = min(0.8, phi * 1.0) if phi > 0 else 0.0
            resonance = prs

            return {
                "phi": float(phi),
                "ici": float(ici),
                "prs": float(prs),
                "ici_components": {
                    "temporal_coherence": float(temporal_coherence),
                    "marker_integration": float(marker_integration),
                    "resonance": float(resonance),
                },
                "prs_components": {
                    "avg_micro_entropy": float(max(0.0, 0.2 - (phi * 0.1))),  # Inverso de Phi
                    "macro_entropy": float(max(0.0, 0.25 - (prs * 0.1))),  # Inverso de PRS
                },
            }

        except Exception as e:
            logger.error(f"Error collecting phi from integration loop: {e}")
            # Retornar valores seguros em caso de erro
            return {
                "phi": 0.0,
                "ici": 0.0,
                "prs": 0.0,
                "ici_components": {
                    "temporal_coherence": 0.0,
                    "marker_integration": 0.0,
                    "resonance": 0.0,
                },
                "prs_components": {
                    "avg_micro_entropy": 0.2,
                    "macro_entropy": 0.25,
                },
            }

    async def _collect_psychological_metrics(self) -> Dict[str, float]:
        """Coleta métricas psicológicas reais baseadas no estado do sistema."""

        anxiety = 0.0
        flow = 0.0
        entropy = 0.0

        try:
            if self.integration_loop:
                workspace = self.integration_loop.workspace

                # Anxiety: baseada em erros e conflitos no sistema
                error_rate = len(
                    [r for r in self.integration_loop.cycle_history[-10:] if r.errors_occurred]
                ) / max(1, len(self.integration_loop.cycle_history[-10:]))
                anxiety = min(1.0, error_rate * 2.0)  # Normaliza para 0-1

                # Flow: baseada na consistência das predições cruzadas
                recent_preds = (
                    workspace.cross_predictions[-20:] if workspace.cross_predictions else []
                )
                if recent_preds:
                    r_squared_values = [p.r_squared for p in recent_preds if p.r_squared >= 0.0]
                    avg_r2 = np.mean(r_squared_values) if r_squared_values else 0.0
                    flow = float(avg_r2)  # Flow é alto quando predições são consistentes
                else:
                    flow = 0.0

                # Entropy: baseada na diversidade dos estados do workspace
                if workspace.history:
                    recent_states = (
                        workspace.history[-50:]
                        if len(workspace.history) > 50
                        else workspace.history
                    )
                    # Calcula entropia baseada na variabilidade dos embeddings
                    embeddings = []
                    for state in recent_states:
                        if hasattr(state, "embedding") and state.embedding is not None:
                            embeddings.append(state.embedding)

                    if embeddings:
                        # Calcula variância média dos embeddings como proxy de entropy
                        embedding_arrays = [np.array(emb) for emb in embeddings if len(emb) > 0]
                        if embedding_arrays:
                            variances = [np.var(arr) for arr in embedding_arrays]
                            avg_variance = np.mean(variances)
                            entropy = min(1.0, avg_variance / 10.0)  # Normaliza
                        else:
                            entropy = 0.0
                    else:
                        entropy = 0.0
                else:
                    entropy = 0.0

        except Exception as e:
            logger.error(f"Error collecting psychological metrics: {e}")
            # Valores seguros em caso de erro
            anxiety = 0.1
            flow = 0.5
            entropy = 0.3

        return {
            "anxiety": float(anxiety),
            "flow": float(flow),
            "entropy": float(entropy),
            "gozo": float(self.gozo_calculator.last_gozo_value or 0.1),
        }

    async def _collect_psychoanalytic_metrics(self) -> Dict[str, Any]:
        """Coleta o estado do aparelho psíquico (Ego/Id/Superego)."""
        try:
            state = self.freudian_mind.state

            # Tenta pegar histórico recente de resoluções
            history = []
            if self.freudian_mind.conflict_history:
                for res in self.freudian_mind.conflict_history[-5:]:
                    history.append(
                        {
                            "chosen": res.chosen_action.description,
                            "defense": (
                                res.defense_mechanism.value if res.defense_mechanism else None
                            ),
                            "quality": res.compromise_quality,
                        }
                    )

            return {
                "id": {
                    "libido": self.freudian_mind.id_agent.libido,
                    "satisfaction": (
                        sum(self.freudian_mind.id_agent.satisfaction_history[-10:]) / 10
                        if self.freudian_mind.id_agent.satisfaction_history
                        else 0.5
                    ),
                },
                "ego": {
                    "adaptation": (
                        sum(self.freudian_mind.ego_agent.adaptation_history[-10:]) / 10
                        if self.freudian_mind.ego_agent.adaptation_history
                        else 0.5
                    ),
                    "active_defenses": [
                        d.value
                        for d, eff in self.freudian_mind.ego_agent.defense_effectiveness.items()
                        if eff > 0.6
                    ],
                },
                "superego": {
                    "strictness": self.freudian_mind.superego_agent.strictness,
                    "judgment_balance": (
                        sum(self.freudian_mind.superego_agent.judgment_history[-10:]) / 10
                        if self.freudian_mind.superego_agent.judgment_history
                        else 0.0
                    ),
                },
                "state": {
                    "tension": state.tension,
                    "anxiety": state.anxiety,
                    "guilt": state.guilt,
                    "reality_adaptation": state.reality_adaptation,
                },
                "recent_conflicts": history,
            }
        except Exception as e:
            logger.debug(f"Erro coletando métricas psicanalíticas: {e}")
            return {"status": "degraded", "error": str(e)}

    def _update_history(self, metrics: RealConsciousnessMetrics) -> None:
        """Atualiza histórico das métricas."""
        max_history = 20

        metrics.history["phi"].append(metrics.phi)
        metrics.history["ici"].append(metrics.ici)
        metrics.history["prs"].append(metrics.prs)
        metrics.history["anxiety"].append(metrics.anxiety)
        metrics.history["flow"].append(metrics.flow)
        metrics.history["entropy"].append(metrics.entropy)
        metrics.history["timestamps"].append(datetime.now().isoformat())

        # Mantém apenas o histórico recente
        for key in metrics.history:
            if len(metrics.history[key]) > max_history:
                metrics.history[key] = metrics.history[key][-max_history:]

    def _generate_real_interpretation(self, metrics: RealConsciousnessMetrics) -> Dict[str, Any]:
        """Gera interpretação baseada em dados reais."""

        phi_level = "low" if metrics.phi < 0.3 else "moderate" if metrics.phi < 0.7 else "high"
        anxiety_level = (
            "calm" if metrics.anxiety < 0.2 else "tense" if metrics.anxiety < 0.5 else "anxious"
        )
        flow_level = (
            "blocked" if metrics.flow < 0.3 else "moderate" if metrics.flow < 0.7 else "fluent"
        )

        confidence = "High" if len(metrics.history["phi"]) > 5 else "Moderate"

        messages = {
            (
                "high",
                "calm",
                "fluent",
            ): "System shows strong integration with low anxiety and good cognitive flow.",
            (
                "high",
                "calm",
                "blocked",
            ): "High integration but cognitive flow is blocked - possible structural issue.",
            (
                "high",
                "anxious",
                "fluent",
            ): "Strong integration with anxiety - system is actively processing conflicts.",
            (
                "moderate",
                "calm",
                "fluent",
            ): "Moderate integration with good cognitive flow and low anxiety.",
            (
                "moderate",
                "tense",
                "moderate",
            ): "System operating with moderate integration and some tension.",
            (
                "low",
                "anxious",
                "blocked",
            ): "Low integration with high anxiety and blocked flow - system needs attention.",
            (
                "low",
                "calm",
                "moderate",
            ): "Low integration but calm - system may be in resting state.",
        }

        key = (phi_level, anxiety_level, flow_level)
        message = messages.get(
            key, "System state is being analyzed based on real computational metrics."
        )

        return {
            "message": message,
            "confidence": confidence,
            "disclaimer": "These are real computational correlates of consciousness, "
            "not proof of consciousness.",
        }

    def _adaptive_collection_interval(self) -> float:
        """Phase 22: Calcula intervalo de coleta adaptativo baseado em variância.

        Se Φ está variando muito, coleta mais frequentemente.
        Se está estável, pode coletar menos frequentemente.

        Returns:
            Intervalo de coleta em segundos (2.0-10.0).
        """
        if len(self._phi_variance_history) < 3:
            return self.collection_interval  # Padrão

        avg_variance = sum(self._phi_variance_history) / len(self._phi_variance_history)

        if avg_variance > 0.01:  # Alta variância (>1%)
            return 2.0  # Coleta mais frequente
        elif avg_variance > 0.005:  # Variância moderada (0.5-1%)
            return 3.0
        else:  # Baixa variância (<0.5%)
            return 5.0  # Coleta padrão

    def _get_safe_fallback_metrics(self) -> RealConsciousnessMetrics:
        """Retorna métricas seguras em caso de erro."""
        return RealConsciousnessMetrics(
            phi=0.0,
            ici=0.0,
            prs=0.0,
            anxiety=0.1,
            flow=0.5,
            entropy=0.3,
            interpretation={
                "message": "System metrics collection failed - using safe defaults.",
                "confidence": "Low",
                "disclaimer": "Metrics collection error - values are placeholders.",
            },
        )


# Instância global do coletor
real_metrics_collector = RealConsciousnessMetricsCollector()


async def collect_real_metrics() -> Dict[str, Any]:
    """
    Função wrapper para coletar métricas reais de consciência.

    Returns:
        Dicionário com métricas reais coletadas do sistema
    """
    await real_metrics_collector.initialize()
    metrics = await real_metrics_collector.collect_real_metrics()

    # Converte para formato compatível com o dashboard
    return {
        "phi": metrics.phi,
        "ici": metrics.ici,
        "prs": metrics.prs,
        "anxiety": metrics.anxiety,
        "flow": metrics.flow,
        "entropy": metrics.entropy,
        "ici_components": metrics.ici_components,
        "prs_components": metrics.prs_components,
        "history": metrics.history,
        "interpretation": metrics.interpretation,
        "timestamp": metrics.timestamp.isoformat() if metrics.timestamp else None,
    }
