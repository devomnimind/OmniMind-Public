"""
Utilitários para módulo de Swarm Intelligence - Phase 19.

Fornece funções auxiliares para cálculos de distância, estruturas de vizinhança,
e operações tensoriais otimizadas.

Author: OmniMind Project - Phase 19
License: MIT
"""

import math
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


def euclidean_distance(point1: List[float], point2: List[float]) -> float:
    """
    Calcula distância euclidiana entre dois pontos.

    Args:
        point1: Primeiro ponto
        point2: Segundo ponto

    Returns:
        Distância euclidiana

    Raises:
        ValueError: Se pontos têm dimensões diferentes
    """
    if len(point1) != len(point2):
        raise ValueError(f"Pontos devem ter mesma dimensão: {len(point1)} != {len(point2)}")

    return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(point1, point2)))


def manhattan_distance(point1: List[float], point2: List[float]) -> float:
    """
    Calcula distância Manhattan entre dois pontos.

    Args:
        point1: Primeiro ponto
        point2: Segundo ponto

    Returns:
        Distância Manhattan

    Raises:
        ValueError: Se pontos têm dimensões diferentes
    """
    if len(point1) != len(point2):
        raise ValueError(f"Pontos devem ter mesma dimensão: {len(point1)} != {len(point2)}")

    return sum(abs(p1 - p2) for p1, p2 in zip(point1, point2))


def find_k_nearest_neighbors(
    positions: List[List[float]], k: int, distance_metric: str = "euclidean"
) -> List[List[int]]:
    """
    Encontra k vizinhos mais próximos para cada ponto.

    Args:
        positions: Lista de posições
        k: Número de vizinhos
        distance_metric: Métrica de distância ('euclidean' ou 'manhattan')

    Returns:
        Lista de listas com índices dos k vizinhos para cada ponto

    Raises:
        ValueError: Se k inválido ou métrica desconhecida
    """
    if k < 0 or k >= len(positions):
        raise ValueError(f"k deve estar em [0, {len(positions)})")

    if distance_metric == "euclidean":
        dist_func = euclidean_distance
    elif distance_metric == "manhattan":
        dist_func = manhattan_distance
    else:
        raise ValueError(f"Métrica desconhecida: {distance_metric}")

    neighbors = []
    for i, pos in enumerate(positions):
        # Calcula distâncias para todos os outros pontos
        distances = []
        for j, other_pos in enumerate(positions):
            if i != j:
                dist = dist_func(pos, other_pos)
                distances.append((j, dist))

        # Ordena por distância e pega k menores
        distances.sort(key=lambda x: x[1])
        neighbors.append([idx for idx, _ in distances[:k]])

    return neighbors


def calculate_diversity(positions: List[List[float]]) -> float:
    """
    Calcula diversidade do enxame baseado em dispersão de posições.

    Diversidade = spread médio em cada dimensão

    Args:
        positions: Posições dos agentes

    Returns:
        Métrica de diversidade (maior = mais disperso)
    """
    if not positions or not positions[0]:
        return 0.0

    dimension = len(positions[0])
    total_spread = 0.0

    for d in range(dimension):
        values = [pos[d] for pos in positions]
        spread = max(values) - min(values)
        total_spread += spread

    return total_spread / dimension


def calculate_convergence(current_fitness: List[float], best_fitness: float) -> float:
    """
    Calcula métrica de convergência do enxame.

    Convergência = 1 - (std_dev / mean) se todos próximos do best

    Args:
        current_fitness: Fitness de todos agentes
        best_fitness: Melhor fitness global

    Returns:
        Métrica de convergência (0-1, maior = mais convergido)
    """
    if not current_fitness:
        return 0.0

    # Calcula desvio padrão e média
    mean = sum(current_fitness) / len(current_fitness)
    variance = sum((f - mean) ** 2 for f in current_fitness) / len(current_fitness)
    std_dev = math.sqrt(variance)

    # Evita divisão por zero
    if mean == 0:
        return 1.0 if std_dev == 0 else 0.0

    # Convergência inversamente proporcional à variação
    convergence = 1.0 - min(std_dev / abs(mean), 1.0)

    return max(0.0, min(1.0, convergence))


def clamp_velocity(velocity: List[float], max_velocity: float) -> List[float]:
    """
    Limita velocidade ao máximo permitido.

    Args:
        velocity: Vetor velocidade
        max_velocity: Velocidade máxima

    Returns:
        Velocidade limitada
    """
    return [max(-max_velocity, min(max_velocity, v)) for v in velocity]


def detect_clustering(
    positions: List[List[float]], threshold: float = 0.7
) -> Tuple[bool, List[List[int]]]:
    """
    Detecta se agentes estão formando clusters.

    Args:
        positions: Posições dos agentes
        threshold: Threshold para considerar cluster (0-1)

    Returns:
        Tupla (tem_clusters, lista_de_clusters)
    """
    if len(positions) < 3:
        return False, []

    # Calcula distância média global
    all_distances = []
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            dist = euclidean_distance(positions[i], positions[j])
            all_distances.append(dist)

    avg_distance = sum(all_distances) / len(all_distances)
    cluster_threshold = avg_distance * (1 - threshold)

    # Identifica clusters (agrupamento simples baseado em distância)
    clusters = []
    visited = set()

    for i in range(len(positions)):
        if i in visited:
            continue

        cluster = [i]
        visited.add(i)

        for j in range(len(positions)):
            if j not in visited:
                dist = euclidean_distance(positions[i], positions[j])
                if dist < cluster_threshold:
                    cluster.append(j)
                    visited.add(j)

        if len(cluster) >= 2:  # Mínimo 2 agentes para cluster
            clusters.append(cluster)

    has_clusters = len(clusters) > 0
    return has_clusters, clusters


def estimate_memory_usage(num_agents: int, dimension: int) -> float:
    """
    Estima uso de memória em MB para configuração de enxame.

    Args:
        num_agents: Número de agentes
        dimension: Dimensionalidade

    Returns:
        Estimativa de memória (MB)
    """
    # Cada agente tem:
    # - position: dimension floats
    # - velocity: dimension floats
    # - best_position: dimension floats
    # - metadata: ~100 bytes
    bytes_per_float = 8
    bytes_per_agent = (dimension * 3 * bytes_per_float) + 100

    total_bytes = num_agents * bytes_per_agent
    total_mb = total_bytes / (1024 * 1024)

    # Overhead estimado (estruturas auxiliares)
    overhead_factor = 1.5
    return total_mb * overhead_factor
