"""
Detector de Padrões Emergentes - Phase 19.

Detecta e analisa padrões emergentes em sistemas de enxame,
incluindo clustering, sincronização e auto-organização.

Author: OmniMind Project - Phase 19
License: MIT
"""

import time
from typing import List, Dict, Any, Optional
import logging

from src.swarm.types import EmergentPattern, EmergenceType
from src.swarm.config import EmergenceConfig
from src.swarm.utils import detect_clustering, calculate_diversity

logger = logging.getLogger(__name__)


class EmergenceDetector:
    """
    Detector de padrões emergentes em enxames.

    Features:
    - Detecção de clustering (formação de grupos)
    - Detecção de sincronização (comportamento coordenado)
    - Detecção de especialização (diferenciação de papéis)
    - Métricas de complexidade emergente
    """

    def __init__(self, config: Optional[EmergenceConfig] = None):
        """
        Inicializa detector de emergência.

        Args:
            config: Configuração de detecção (usa padrão se None)
        """
        self.config = config or EmergenceConfig()
        self.detected_patterns: List[EmergentPattern] = []
        self.pattern_history: Dict[str, List[EmergentPattern]] = {}

        logger.info("EmergenceDetector initialized")

    def detect_patterns(self, agent_states: List[Dict[str, Any]]) -> List[EmergentPattern]:
        """
        Detecta padrões emergentes a partir de estados de agentes.

        Args:
            agent_states: Estados atuais de todos os agentes
                Cada estado deve conter: 'position', 'velocity', 'fitness', etc.

        Returns:
            Lista de padrões emergentes detectados
        """
        if len(agent_states) < self.config.min_pattern_size:
            return []

        patterns = []

        # Extrai posições
        positions = [state.get("position", []) for state in agent_states]
        if not all(positions):
            return []

        # Detecta clustering
        clustering_pattern = self._detect_clustering(agent_states, positions)
        if clustering_pattern:
            patterns.append(clustering_pattern)

        # Detecta sincronização
        sync_pattern = self._detect_synchronization(agent_states)
        if sync_pattern:
            patterns.append(sync_pattern)

        # Detecta especialização
        spec_pattern = self._detect_specialization(agent_states)
        if spec_pattern:
            patterns.append(spec_pattern)

        # Armazena padrões detectados
        self.detected_patterns.extend(patterns)

        # Atualiza histórico
        for pattern in patterns:
            pattern_key = pattern.pattern_type.value
            if pattern_key not in self.pattern_history:
                self.pattern_history[pattern_key] = []
            self.pattern_history[pattern_key].append(pattern)

        if patterns:
            logger.info(f"Detected {len(patterns)} emergent patterns")

        return patterns

    def _detect_clustering(
        self, agent_states: List[Dict[str, Any]], positions: List[List[float]]
    ) -> Optional[EmergentPattern]:
        """
        Detecta formação de clusters.

        Args:
            agent_states: Estados dos agentes
            positions: Posições dos agentes

        Returns:
            Padrão de clustering se detectado, None caso contrário
        """
        has_clusters, clusters = detect_clustering(positions, self.config.clustering_threshold)

        if not has_clusters:
            return None

        # Verifica se há clusters significativos
        significant_clusters = [c for c in clusters if len(c) >= self.config.min_pattern_size]

        if not significant_clusters:
            return None

        # Calcula confiança baseado em número e tamanho de clusters
        num_agents = len(agent_states)
        agents_in_clusters = sum(len(c) for c in significant_clusters)
        confidence = min(agents_in_clusters / num_agents, 1.0)

        if confidence < self.config.confidence_threshold:
            return None

        # Identifica participantes
        participants = []
        for cluster in significant_clusters:
            for agent_idx in cluster:
                if agent_idx < len(agent_states):
                    agent_id = agent_states[agent_idx].get("id", str(agent_idx))
                    participants.append(agent_id)

        return EmergentPattern(
            pattern_type=EmergenceType.CLUSTERING,
            confidence=confidence,
            participants=participants,
            metrics={
                "num_clusters": len(significant_clusters),
                "avg_cluster_size": agents_in_clusters / len(significant_clusters),
                "cluster_ratio": agents_in_clusters / num_agents,
            },
            timestamp=time.time(),
        )

    def _detect_synchronization(
        self, agent_states: List[Dict[str, Any]]
    ) -> Optional[EmergentPattern]:
        """
        Detecta sincronização de comportamento.

        Sincronização = agentes com velocidades/direções similares

        Args:
            agent_states: Estados dos agentes

        Returns:
            Padrão de sincronização se detectado, None caso contrário
        """
        velocities = [state.get("velocity", []) for state in agent_states]

        # Filtra estados sem velocidade
        valid_velocities = [v for v in velocities if v]
        if len(valid_velocities) < self.config.min_pattern_size:
            return None

        # Calcula diversidade de velocidade (baixa = mais sincronizado)
        velocity_diversity = calculate_diversity(valid_velocities)

        # Normaliza diversidade (assumindo espaço [-10, 10])
        max_diversity = 20.0  # Range esperado
        normalized_diversity = min(velocity_diversity / max_diversity, 1.0)

        # Sincronização = 1 - diversidade
        synchronization = 1.0 - normalized_diversity

        if synchronization < self.config.sync_threshold:
            return None

        # Identifica participantes sincronizados
        participants = [
            state.get("id", str(i)) for i, state in enumerate(agent_states) if state.get("velocity")
        ]

        return EmergentPattern(
            pattern_type=EmergenceType.SYNCHRONIZATION,
            confidence=synchronization,
            participants=participants[: self.config.min_pattern_size * 2],
            metrics={
                "synchronization_level": synchronization,
                "velocity_diversity": velocity_diversity,
                "num_synchronized": len(participants),
            },
            timestamp=time.time(),
        )

    def _detect_specialization(
        self, agent_states: List[Dict[str, Any]]
    ) -> Optional[EmergentPattern]:
        """
        Detecta especialização de papéis.

        Especialização = agentes com fitness muito diferentes (nichos diferentes)

        Args:
            agent_states: Estados dos agentes

        Returns:
            Padrão de especialização se detectado, None caso contrário
        """
        fitnesses = [state.get("fitness") for state in agent_states]

        # Filtra estados sem fitness
        valid_fitnesses = [f for f in fitnesses if f is not None]
        if len(valid_fitnesses) < self.config.min_pattern_size:
            return None

        # Calcula variance/spread de fitness (alta = mais especialização)
        mean_fitness = sum(valid_fitnesses) / len(valid_fitnesses)
        variance = sum((f - mean_fitness) ** 2 for f in valid_fitnesses) / len(valid_fitnesses)

        # Normaliza variance (threshold empírico)
        specialization_score = min(variance / 100.0, 1.0)

        if specialization_score < 0.5:  # Threshold para especialização
            return None

        # Identifica agentes especializados (outliers)
        specialized_agents = []
        for i, state in enumerate(agent_states):
            fitness = state.get("fitness")
            if fitness is not None:
                deviation = abs(fitness - mean_fitness)
                if deviation > variance**0.5:  # > 1 std dev
                    specialized_agents.append(state.get("id", str(i)))

        if len(specialized_agents) < self.config.min_pattern_size:
            return None

        return EmergentPattern(
            pattern_type=EmergenceType.SPECIALIZATION,
            confidence=min(specialization_score, 1.0),
            participants=specialized_agents,
            metrics={
                "fitness_variance": variance,
                "fitness_mean": mean_fitness,
                "num_specialists": len(specialized_agents),
            },
            timestamp=time.time(),
        )

    def get_pattern_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo de padrões detectados.

        Returns:
            Dicionário com estatísticas de padrões
        """
        summary = {
            "total_patterns": len(self.detected_patterns),
            "by_type": {},
            "recent_patterns": [],
        }

        # Conta por tipo
        for pattern_type in EmergenceType:
            count = sum(1 for p in self.detected_patterns if p.pattern_type == pattern_type)
            if count > 0:
                summary["by_type"][pattern_type.value] = count

        # Últimos 5 padrões
        recent = sorted(self.detected_patterns, key=lambda p: p.timestamp, reverse=True)[:5]
        summary["recent_patterns"] = [
            {
                "type": p.pattern_type.value,
                "confidence": p.confidence,
                "num_participants": len(p.participants),
            }
            for p in recent
        ]

        return summary

    def clear_history(self) -> None:
        """Limpa histórico de padrões."""
        self.detected_patterns = []
        self.pattern_history = {}
        logger.info("Pattern history cleared")
