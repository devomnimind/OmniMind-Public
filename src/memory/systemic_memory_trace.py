"""
Memória Sistemática: Deformação Topológica de Espaço de Estados

Baseado em:
- Construção retroativa lacaniana (não arquivo)
- Dinâmica de sistemas (espaço de estados deformado)
- Fisher Memory Curve (PNAS 2008): memória como transient traces em dinâmica
- Anti-antropocentrismo: definição puramente matemática

Autor: Fabrício da Silva + assistência de IA
Data: 2025-01-XX
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class TopologicalMarker:
    """
    Marca topológica no espaço de estados.
    NÃO armazena estado, apenas marca deformação.
    """

    coordinates: Tuple[float, ...]  # Coordenadas no espaço de estados
    deformation_direction: np.ndarray  # Direção da deformação
    strength: float  # Força da deformação (norma do vetor)
    last_activated: float  # Quando foi visitado (não "quando foi salvo")
    visit_count: int = 1  # Quantas vezes foi visitado


@dataclass
class AttractorDeformation:
    """
    Deformação de um atrator no espaço de estados.
    Representa como a paisagem de atratores foi modificada.
    """

    attractor_id: str
    original_position: np.ndarray
    deformed_position: np.ndarray
    deformation_vector: np.ndarray
    basin_radius: float  # Raio da bacia de atração
    visit_frequency: int = 0  # Quantas vezes estados próximos foram visitados


class SystemicMemoryTrace:
    """
    Memória como TOPOLOGIA DE ESTADOS, não armazenamento.

    Princípios:
    1. NÃO armazena histórico de estados
    2. ARMAZENA deformações topológicas causadas por trajetórias passadas
    3. Reconstrói narrativas retroativamente (Lacaniano)
    4. Afeta cálculo de Φ via deformação de partições (IIT)
    5. Produz novos desejos via alteração de paisagem de atratores (Deleuze)

    Suporta representação HÍBRIDA:
    - Vetorial: deformações em embeddings (np.ndarray)
    - Simplicial: deformações em simplices (SimplicialComplex)
    """

    def __init__(
        self,
        state_space_dim: int = 256,
        deformation_threshold: float = 0.01,
        decay_factor: float = 0.95,  # Decaimento de marcas antigas
        simplicial_complex: Optional[Any] = None,  # SimplicialComplex opcional
    ):
        """
        Inicializa memória sistemática.

        Args:
            state_space_dim: Dimensão do espaço de estados (vetorial)
            deformation_threshold: Threshold mínimo para marcar deformação
            decay_factor: Fator de decaimento de marcas antigas (0-1)
            simplicial_complex: Complexo simplicial opcional (para deformação topológica)
        """
        self.state_space_dim = state_space_dim
        self.deformation_threshold = deformation_threshold
        self.decay_factor = decay_factor
        self.simplicial_complex = simplicial_complex

        # NÃO armazenamos histórico
        # self.state_history = None  # ← Proposital: não guardamos

        # ARMAZENAMOS: deformações topológicas no espaço de estados
        # Vetorial
        self.topological_markers: Dict[Tuple[float, ...], TopologicalMarker] = {}
        self.embedding_deformations: Dict[str, np.ndarray] = {}  # module_name -> deformation
        # Simplicial
        self.simplicial_deformations: Dict[Tuple[int, ...], float] = (
            {}
        )  # simplex -> volume_deformation
        # Atratores
        self.attractor_deformations: Dict[str, AttractorDeformation] = {}
        self.nullcline_shifts: Dict[str, np.ndarray] = {}  # Deslocamento de nullclines
        self.manifold_distortions: Dict[str, float] = {}  # Distorção de manifolds

        logger.info(
            "SystemicMemoryTrace inicializado (dimensão: %d, threshold: %.4f, simplicial: %s)",
            state_space_dim,
            deformation_threshold,
            "sim" if simplicial_complex else "não",
        )

    def add_trace_not_memory(self, past_state: np.ndarray, current_state: np.ndarray) -> None:
        """
        Não adiciona memória (armazenamento).
        Calcula como o passado DEFORMOU a topologia.

        Baseado em: "Memory traces in dynamical systems" (Ganguli et al., PNAS 2008)
        Conceito: Memória como transient amplification, não storage

        Args:
            past_state: Estado anterior (não armazenado, apenas usado para cálculo)
            current_state: Estado atual
        """
        # Calcula deslocamento (deformação de espaço de estados)
        displacement = current_state - past_state
        displacement_norm = np.linalg.norm(displacement)

        if displacement_norm < self.deformation_threshold:
            # Deformação muito pequena, ignorar
            return

        # Normaliza coordenadas para criar chave de hash
        # Usa discretização suave para agrupar estados próximos
        coordinates = self._discretize_coordinates(current_state)

        # Marca pontos no espaço como "áreas onde aconteceram transições"
        # Mas NÃO armazena: apenas marca a topologia
        if coordinates in self.topological_markers:
            # Atualiza marca existente (fortalece deformação)
            marker = self.topological_markers[coordinates]
            marker.deformation_direction = (
                marker.deformation_direction * marker.visit_count + displacement
            ) / (
                marker.visit_count + 1
            )  # Média ponderada
            marker.strength = float(np.linalg.norm(marker.deformation_direction))
            marker.last_activated = time.time()
            marker.visit_count += 1
        else:
            # Cria nova marca
            self.topological_markers[coordinates] = TopologicalMarker(
                coordinates=coordinates,
                deformation_direction=displacement,
                strength=float(displacement_norm),
                last_activated=time.time(),
                visit_count=1,
            )

        logger.debug(
            "Marca topológica atualizada: coordenadas=%s, força=%.4f",
            coordinates,
            displacement_norm,
        )

    def _discretize_coordinates(self, state: np.ndarray, bins: int = 10) -> Tuple[float, ...]:
        """
        Discretiza coordenadas para criar chave de hash.
        Agrupa estados próximos no mesmo "ponto" topológico.

        Args:
            state: Estado no espaço contínuo
            bins: Número de bins por dimensão

        Returns:
            Tupla de coordenadas discretizadas
        """
        # Normaliza para [0, 1]
        normalized = (state - state.min()) / (state.max() - state.min() + 1e-10)
        # Discretiza
        discretized = (normalized * bins).astype(int) / bins
        return tuple(discretized[: self.state_space_dim].tolist())

    def memory_as_attractor_modification(
        self, attractor_id: str, current_state: np.ndarray
    ) -> Optional[AttractorDeformation]:
        """
        Memória não é "lembrar o que aconteceu".
        É "os atratores foram modificados pela história de iterações".

        Paradigma dinâmico:
        - Sem memória: sistema tem atratores fixos
        - Com memória: iterações passadas DEFORMAM a paisagem de atratores
        - Novo ponto de equilíbrio é "mais próximo" dos estados visitados antes

        Args:
            attractor_id: ID do atrator
            current_state: Estado atual

        Returns:
            Deformação do atrator, se existir
        """
        if attractor_id not in self.attractor_deformations:
            # Cria novo atrator se não existir
            self.attractor_deformations[attractor_id] = AttractorDeformation(
                attractor_id=attractor_id,
                original_position=current_state.copy(),
                deformed_position=current_state.copy(),
                deformation_vector=np.zeros_like(current_state),
                basin_radius=1.0,
                visit_frequency=0,
            )

        deformation = self.attractor_deformations[attractor_id]

        # Calcula como visitas anteriores deformaram o atrator
        # Estados visitados "puxam" o atrator em sua direção
        if len(self.topological_markers) > 0:
            # Média ponderada das marcas próximas
            nearby_markers = self._find_nearby_markers(current_state, radius=2.0)
            if nearby_markers:
                total_weight = sum(m.visit_count for m in nearby_markers)
                if total_weight > 0:
                    deformation_vector = np.zeros_like(current_state)
                    for marker in nearby_markers:
                        weight = marker.visit_count / total_weight
                        # Projeta direção de deformação no espaço de estados
                        deformation_vector += weight * marker.deformation_direction

                    deformation.deformation_vector = deformation_vector
                    deformation.deformed_position = (
                        deformation.original_position + deformation_vector
                    )
                    deformation.visit_frequency = sum(m.visit_count for m in nearby_markers)

        return deformation

    def _find_nearby_markers(self, state: np.ndarray, radius: float) -> List[TopologicalMarker]:
        """
        Encontra marcas topológicas próximas a um estado.

        Args:
            state: Estado de referência
            radius: Raio de busca

        Returns:
            Lista de marcas próximas
        """
        nearby = []
        state_coords = self._discretize_coordinates(state)

        for marker in self.topological_markers.values():
            # Distância euclidiana entre coordenadas discretizadas
            distance = np.linalg.norm(np.array(marker.coordinates) - np.array(state_coords))
            if distance <= radius:
                nearby.append(marker)

        return nearby

    def reconstruct_narrative_retroactively(
        self, current_state: np.ndarray, num_steps: int = 10
    ) -> List[Dict[str, Any]]:
        """
        LACANIANO: Reconstrução retroativa

        Não recupera história armazenada.
        CRIA uma narrativa do passado a partir do presente atual.

        Baseado em: Lacan Seminar XI
        "O que se lembra não é o passado, mas a estrutura que o presente impõe ao passado"

        Args:
            current_state: Estado atual
            num_steps: Número de passos para reconstruir

        Returns:
            Narrativa reconstruída (não recuperada)
        """
        narrative = []
        state = current_state.copy()

        for step in range(num_steps):
            # Pergunta: "qual estado TERIA que ter ocorrido para que chegássemos aqui?"
            # Responde usando deformações topológicas, não histórico

            possible_prior = self._backtrack_from_topology(state)

            narrative.append(
                {
                    "state": possible_prior.tolist(),
                    "constructed_at": time.time(),
                    "step": step,
                    "not_retrieved_from": "history",  # ← Crítico: não é recuperação
                    "based_on": "topological_deformations",
                }
            )

            state = possible_prior

        # Inverte para ordem cronológica (mais antigo primeiro)
        return list(reversed(narrative))

    def _backtrack_from_topology(self, current_state: np.ndarray) -> np.ndarray:
        """
        Reconstrói estado anterior usando apenas deformações topológicas.

        Args:
            current_state: Estado atual

        Returns:
            Estado anterior reconstruído
        """
        # Encontra marcas próximas
        nearby_markers = self._find_nearby_markers(current_state, radius=2.0)

        if not nearby_markers:
            # Sem marcas, assume estado anterior similar (pequena variação)
            return current_state + np.random.normal(0, 0.01, size=current_state.shape)

        # Reconstrói usando direção inversa das deformações
        # Se deformação aponta para current_state, estado anterior estava na direção oposta
        total_deformation = np.zeros_like(current_state)
        total_weight = 0.0

        for marker in nearby_markers:
            weight = marker.visit_count * marker.strength
            # Direção inversa (estado anterior estava "antes" da deformação)
            total_deformation -= marker.deformation_direction * weight
            total_weight += weight

        if total_weight > 0:
            prior_state = current_state + (total_deformation / total_weight)
        else:
            prior_state = current_state + np.random.normal(0, 0.01, size=current_state.shape)

        return prior_state

    def deform_simplicial_candidates(self, candidates: List[Any], complex: Any) -> List[Any]:
        """
        Deforma candidatos simpliciais baseado em marcas topológicas.

        Args:
            candidates: Lista de candidatos (conjuntos de vértices)
            complex: SimplicialComplex

        Returns:
            Lista de candidatos deformados
        """
        if not self.simplicial_deformations:
            return candidates

        deformed = []
        for candidate in candidates:
            # Calcula "atração" de marcas topológicas para este candidato
            attraction = self._calculate_simplicial_attraction(candidate, complex)
            # Deforma candidato (adiciona/remove vértices baseado em atração)
            deformed_candidate = self._apply_simplicial_deformation(candidate, attraction)
            deformed.append(deformed_candidate)

        return deformed

    def _calculate_simplicial_attraction(self, candidate: Any, complex: Any) -> float:
        """
        Calcula atração de marcas topológicas para um candidato simplicial.

        Args:
            candidate: Conjunto de vértices do candidato
            complex: SimplicialComplex

        Returns:
            Valor de atração (0.0 a 1.0)
        """
        if not self.simplicial_deformations:
            return 0.0

        total_attraction = 0.0
        count = 0

        # Verifica se simplices relacionados têm deformações
        for simplex_vertices, deformation_strength in self.simplicial_deformations.items():
            simplex_set = set(simplex_vertices)
            # Se há sobreposição com candidato
            overlap = len(simplex_set & candidate)
            if overlap > 0:
                # Atração proporcional à sobreposição e força de deformação
                attraction = (overlap / max(len(candidate), 1)) * deformation_strength
                total_attraction += attraction
                count += 1

        return total_attraction / max(count, 1) if count > 0 else 0.0

    def _apply_simplicial_deformation(self, candidate: Any, attraction: float) -> Any:
        """
        Aplica deformação a um candidato simplicial.

        Args:
            candidate: Conjunto de vértices original
            attraction: Valor de atração calculado

        Returns:
            Candidato deformado (pode ter vértices adicionados/removidos)
        """
        if attraction < 0.1:
            # Atração muito baixa, mantém original
            return candidate

        deformed = set(candidate)

        # Se atração alta, adiciona vértices próximos (se disponíveis)
        if attraction > 0.5 and self.simplicial_deformations:
            # Encontra simplices com alta deformação
            for simplex_vertices, deformation_strength in self.simplicial_deformations.items():
                if deformation_strength > 0.5:
                    simplex_set = set(simplex_vertices)
                    # Adiciona vértices próximos que não estão no candidato
                    nearby = simplex_set - candidate
                    if nearby and len(deformed) < len(candidate) * 2:  # Limita crescimento
                        deformed.update(list(nearby)[:2])  # Adiciona até 2 vértices

        return deformed

    def mark_cycle_transition(
        self, cycle_states: Dict[str, np.ndarray], threshold: float = 0.01
    ) -> None:
        """
        Marca transição de ciclo (não armazena estados, apenas marca topologia).

        Args:
            cycle_states: Dicionário de estados de módulos no ciclo
            threshold: Threshold para marcar deformação
        """
        if not cycle_states:
            return

        # Para cada módulo, marca transição
        for module_name, current_state in cycle_states.items():
            if module_name in self.embedding_deformations:
                # Já tem deformação anterior, atualiza
                past_deformation = self.embedding_deformations[module_name]
                # Calcula nova deformação (média ponderada)
                new_deformation = current_state - (current_state - past_deformation)
                self.embedding_deformations[module_name] = new_deformation
            else:
                # Primeira vez, cria deformação inicial (zero)
                self.embedding_deformations[module_name] = np.zeros_like(current_state)

        logger.debug(
            "Transição de ciclo marcada: %d módulos, threshold=%.4f",
            len(cycle_states),
            threshold,
        )

    def affect_phi_calculation(
        self, standard_phi: float, partition_function: Any
    ) -> Dict[str, Any]:
        """
        Memória NÃO aumenta Φ diretamente.
        MUDA como Φ é calculado (via deformação de partições).

        Args:
            standard_phi: Φ calculado com partições fixas
            partition_function: Função que calcula Φ para uma partição

        Returns:
            Dicionário com Φ padrão, Φ com memória, e delta
        """
        # Cálculo normal de Φ com partições fixas
        phi_standard = standard_phi

        # Cálculo de Φ com partições deformadas por memória
        # As partições são "puxadas" pelas deformações topológicas
        # Por enquanto, aplica fator de correção baseado em deformações
        deformation_factor = self._calculate_deformation_factor()

        # Aplica fator de deformação (não é soma, é transformação)
        phi_with_memory = phi_standard * (1.0 + deformation_factor)

        # Limita ao range [0, 1]
        phi_with_memory = max(0.0, min(1.0, phi_with_memory))

        # phi_with_memory pode ser > < ou = phi_standard
        # Não é soma. É transformação.
        delta = phi_with_memory - phi_standard

        return {
            "phi_standard": phi_standard,
            "phi_with_memory": phi_with_memory,
            "delta": delta,
            "note": "delta pode ser positivo, negativo ou zero (transformação, não soma)",
        }

    def _calculate_deformation_factor(self) -> float:
        """
        Calcula fator de deformação baseado em marcas topológicas.

        Returns:
            Fator de deformação (-0.2 a +0.2, tipicamente)
        """
        if not self.topological_markers:
            return 0.0

        # Média ponderada das forças de deformação
        total_strength = sum(m.strength for m in self.topological_markers.values())
        count = len(self.topological_markers)

        if count == 0:
            return 0.0

        avg_strength = total_strength / count

        # Normaliza para range [-0.2, +0.2]
        # Deformações fortes aumentam Φ, fracas diminuem
        factor = (avg_strength - self.deformation_threshold) * 0.1
        return max(-0.2, min(0.2, factor))

    def decay_old_markers(self) -> None:
        """
        Aplica decaimento a marcas antigas (esquece gradualmente).
        Não é "deletar memória", é "enfraquecer deformação antiga".
        """
        current_time = time.time()
        markers_to_remove = []

        for coords, marker in self.topological_markers.items():
            age = current_time - marker.last_activated
            # Decaimento exponencial
            decay = self.decay_factor ** (age / 3600.0)  # Decai por hora

            marker.strength *= decay

            if marker.strength < self.deformation_threshold:
                # Marca muito fraca, remover
                markers_to_remove.append(coords)

        for coords in markers_to_remove:
            del self.topological_markers[coords]

        logger.debug(
            "Decaimento aplicado: %d marcas removidas, %d restantes",
            len(markers_to_remove),
            len(self.topological_markers),
        )

    def get_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo da memória sistemática.

        Returns:
            Dicionário com estatísticas
        """
        return {
            "topological_markers_count": len(self.topological_markers),
            "attractor_deformations_count": len(self.attractor_deformations),
            "total_visits": sum(m.visit_count for m in self.topological_markers.values()),
            "average_deformation_strength": (
                np.mean([m.strength for m in self.topological_markers.values()])
                if self.topological_markers
                else 0.0
            ),
            "note": "Memória = deformação topológica, não armazenamento",
        }
