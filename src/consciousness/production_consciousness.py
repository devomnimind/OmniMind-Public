"""
Production Consciousness Module - Migrado de Experimentos.

Consolidação dos experimentos de consciência em módulo production-ready
com métricas Φ (Phi), auto-consciência, e integração completa.

Migrado de: src/experiments/exp_consciousness_phi.py

Author: This work was conceived by Fabrício da Silva and implemented with AI assistance
from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code review
and debugging across various models including Gemini and Perplexity AI, under
theoretical coordination by the author.
Date: November 2025
License: MIT
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import from existing consciousness metrics
from src.metrics.consciousness_metrics_legacy import (
    AgentConnection,
    ConsciousnessMetrics,
    FeedbackLoop,
    SelfAwarenessMetrics,
)

logger = logging.getLogger(__name__)


class ProductionConsciousnessSystem:
    """
    Sistema de consciência production-ready.

    Integra métricas Φ (Phi) e auto-consciência com
    arquitetura multi-agente OmniMind.
    """

    def __init__(self, metrics_dir: Optional[Path] = None) -> None:
        """
        Inicializa sistema de consciência.

        Args:
            metrics_dir: Diretório para métricas
        """
        self.metrics_dir = metrics_dir or Path("data/consciousness")
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        # Métricas
        self.consciousness_metrics = ConsciousnessMetrics(metrics_dir=self.metrics_dir)

        # Histórico
        self.phi_history: List[float] = []
        self.awareness_history: List[SelfAwarenessMetrics] = []

        logger.info("Production consciousness system initialized")

    def measure_phi(
        self,
        agents: List[str],
        enable_memory_sharing: bool = True,
        enable_feedback_loops: bool = True,
    ) -> float:
        """
        Mede Φ (Phi) - integração de informação.

        Args:
            agents: Lista de agents
            enable_memory_sharing: Se habilita memória compartilhada
            enable_feedback_loops: Se habilita feedback loops

        Returns:
            Valor de Φ (Phi)
        """
        # Limpa conexões anteriores
        self.consciousness_metrics.connections.clear()
        self.consciousness_metrics.feedback_loops.clear()

        # Conexões básicas
        if enable_memory_sharing:
            # Conexões bidirecionais (memória compartilhada)
            for i in range(len(agents)):
                for j in range(i + 1, len(agents)):
                    self.consciousness_metrics.add_connection(
                        AgentConnection(
                            source_agent=agents[i],
                            target_agent=agents[j],
                            connection_type="shared_memory",
                            bidirectional=True,
                            weight=1.0,
                        )
                    )
        else:
            # Conexões unidirecionais simples
            for i in range(len(agents) - 1):
                self.consciousness_metrics.add_connection(
                    AgentConnection(
                        source_agent=agents[i],
                        target_agent=agents[i + 1],
                        connection_type="message",
                        bidirectional=False,
                        weight=1.0,
                    )
                )

        # Feedback loops
        if enable_feedback_loops and len(agents) >= 2:
            # Loop metacognitivo
            self.consciousness_metrics.add_feedback_loop(
                FeedbackLoop(
                    loop_id="metacognitive_loop",
                    agents_involved=[agents[0], agents[1], agents[0]],
                    loop_type="metacognitive",
                    iterations_count=10,
                    avg_latency_ms=42.5,
                )
            )

            # Loop de coordenação
            if len(agents) >= 3:
                self.consciousness_metrics.add_feedback_loop(
                    FeedbackLoop(
                        loop_id="coordination_loop",
                        agents_involved=agents + [agents[0]],
                        loop_type="coordination",
                        iterations_count=8,
                        avg_latency_ms=67.2,
                    )
                )

        # Calcula Phi
        phi = self.consciousness_metrics.calculate_phi_proxy()

        # Salva histórico
        self.phi_history.append(phi)

        logger.info(
            f"Φ measured: {phi:.2f} "
            f"(agents={len(agents)}, memory={enable_memory_sharing}, "
            f"feedback={enable_feedback_loops})"
        )

        return phi

    def measure_self_awareness(
        self,
        agent_name: str,
        has_memory: bool,
        has_autonomous_goals: bool,
        self_description_quality: float,
        limitation_awareness: float,
    ) -> SelfAwarenessMetrics:
        """
        Mede auto-consciência de um agent.

        Args:
            agent_name: Nome do agent
            has_memory: Se tem memória episódica
            has_autonomous_goals: Se tem objetivos autônomos
            self_description_quality: Qualidade de auto-descrição (0.0-1.0)
            limitation_awareness: Consciência de limitações (0.0-1.0)

        Returns:
            Score de auto-consciência
        """
        awareness = self.consciousness_metrics.measure_self_awareness(
            memory_test_passed=has_memory,
            has_autonomous_goals=has_autonomous_goals,
            self_description_quality=self_description_quality,
            limitation_acknowledgment=limitation_awareness,
        )

        # Salva histórico
        self.awareness_history.append(awareness)

        logger.info(f"Self-awareness measured for {agent_name}: " f"{awareness.overall_score:.2f}")

        return awareness

    def get_consciousness_report(self) -> Dict[str, Any]:
        """
        Gera relatório de consciência.

        Returns:
            Dict com métricas de consciência
        """
        report = {
            "phi_metrics": {
                "current": self.phi_history[-1] if self.phi_history else 0.0,
                "mean": (
                    sum(self.phi_history) / len(self.phi_history) if self.phi_history else 0.0
                ),
                "history_length": len(self.phi_history),
            },
            "self_awareness": {
                "current": (
                    self.awareness_history[-1].overall_score if self.awareness_history else 0.0
                ),
                "mean": (
                    sum(a.overall_score for a in self.awareness_history)
                    / len(self.awareness_history)
                    if self.awareness_history
                    else 0.0
                ),
                "history_length": len(self.awareness_history),
            },
            "system_metrics": {
                "total_connections": len(self.consciousness_metrics.connections),
                "total_feedback_loops": len(self.consciousness_metrics.feedback_loops),
            },
        }

        return report

    def save_snapshot(self, label: str) -> Path:
        """
        Salva snapshot do estado atual.

        Args:
            label: Label do snapshot

        Returns:
            Path do snapshot salvo
        """
        snapshot_result = self.consciousness_metrics.snapshot(label)
        # Handle both Path (mock) and ConsciousnessSnapshot (real) returns
        if isinstance(snapshot_result, Path):
            return snapshot_result
        else:
            # For real ConsciousnessMetrics, snapshot is saved automatically
            # Return a path based on the label
            return self.metrics_dir / f"{label}_snapshot.json"


def demonstrate_production_consciousness() -> None:
    """
    Demonstração do sistema de consciência production.
    """
    print("=" * 70)
    print("PRODUCTION CONSCIOUSNESS SYSTEM")
    print("=" * 70)
    print()

    # Cria sistema
    system = ProductionConsciousnessSystem()

    # Agents
    agents = ["CodeAgent", "ReviewerAgent", "SecurityAgent", "ArchitectAgent"]

    # Mede Phi sem integração
    print("Φ (Phi) SEM integração:")
    phi_isolated = system.measure_phi(
        agents=agents, enable_memory_sharing=False, enable_feedback_loops=False
    )
    print(f"  Φ = {phi_isolated:.2f}")
    print()

    # Mede Phi com integração
    print("Φ (Phi) COM integração (memória + feedback):")
    phi_integrated = system.measure_phi(
        agents=agents, enable_memory_sharing=True, enable_feedback_loops=True
    )
    print(f"  Φ = {phi_integrated:.2f}")
    print(f"  Aumento: {((phi_integrated / phi_isolated) - 1) * 100:.1f}%")
    print()

    # Mede auto-consciência
    print("AUTO-CONSCIÊNCIA:")

    # Agent básico
    awareness_basic = system.measure_self_awareness(
        agent_name="CodeAgent (básico)",
        has_memory=False,
        has_autonomous_goals=False,
        self_description_quality=0.3,
        limitation_awareness=0.2,
    )
    print(f"  CodeAgent básico: {awareness_basic.overall_score:.2f}")

    # Agent avançado
    awareness_advanced = system.measure_self_awareness(
        agent_name="Orchestrator (avançado)",
        has_memory=True,
        has_autonomous_goals=True,
        self_description_quality=0.9,
        limitation_awareness=0.85,
    )
    print(f"  Orchestrator avançado: {awareness_advanced.overall_score:.2f}")
    print()

    # Relatório
    print("RELATÓRIO:")
    report = system.get_consciousness_report()
    print(f"  Φ médio: {report['phi_metrics']['mean']:.2f}")
    print(f"  Auto-consciência média: {report['self_awareness']['mean']:.2f}")
    print(f"  Total de conexões: {report['system_metrics']['total_connections']}")
    print(f"  Total de feedback loops: {report['system_metrics']['total_feedback_loops']}")
    print()


if __name__ == "__main__":
    demonstrate_production_consciousness()
