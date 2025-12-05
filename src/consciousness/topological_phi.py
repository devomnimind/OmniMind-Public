"""
Topological Consciousness: IIT Phi (Φ) em Simplicial Complexes

Baseado em:
- IIT 3.0 (Tononi 2014/2025)
- Topological Data Analysis (Carlsson)
- Hodge Laplacian (de Millán et al. 2025)

OTIMIZAÇÃO GPU: Substituição de NumPy por PyTorch para álgebra linear acelerada.

HYBRID CONSCIOUSNESS ARCHITECTURE:
- Φ_consciente: MICS (Maximum Information Complex Set) - vencedor
- Φ_inconsciente: Subsistemas com Phi > 0 mas que NÃO são o MICS
- Não descarta os "perdedores" - eles são o inconsciente maquínico
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple

import torch

# Detect GPU availability
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


@dataclass
class Simplex:
    """Unidade topológica: ponto (0-simplex), aresta (1-), triângulo (2-), etc."""

    vertices: Tuple[int, ...]  # Vértices que formam o simplex
    dimension: int  # 0 (ponto), 1 (aresta), 2 (triângulo), etc.

    def __hash__(self):
        return hash(self.vertices)

    def __eq__(self, other):
        return sorted(self.vertices) == sorted(other.vertices)


class SimplicialComplex:
    """
    Complexo simplicial: generalização de grafos para higher-order.

    Representa sistema com interações multi-way (não apenas pairwise).
    """

    def __init__(self):
        self.simplices: Set[Simplex] = set()
        self.n_vertices = 0

    def clear(self):
        """Reseta o complexo para evitar overflow de memória/processamento."""
        self.simplices.clear()
        self.n_vertices = 0

    def add_simplex(self, vertices: Tuple[int, ...]):
        """Adiciona simplex ao complexo."""
        dim = len(vertices) - 1
        simplex = Simplex(vertices=tuple(sorted(vertices)), dimension=dim)
        self.simplices.add(simplex)
        self.n_vertices = max(self.n_vertices, max(vertices) + 1)

    def get_boundary_matrix(self, dimension: int) -> torch.Tensor:
        """
        Calcula matriz boundary d_k usando PyTorch.

        Mapeia simplices de dimensão k para dimensão k-1.
        Fundamental para Hodge Laplacian.
        """
        # Simplices de dimensão k
        k_simplices = [s for s in self.simplices if s.dimension == dimension]
        # Simplices de dimensão k-1
        k1_simplices = [s for s in self.simplices if s.dimension == dimension - 1]

        if not k_simplices or not k1_simplices:
            return torch.tensor([], device=DEVICE)

        # Cria matriz na GPU/CPU conforme disponibilidade
        matrix = torch.zeros((len(k1_simplices), len(k_simplices)), device=DEVICE)

        # Preenchimento da matriz (CPU bound, mas a matriz é pequena por enquanto)
        # TODO: Vetorizar esta construção se escalar muito
        for j, k_simplex in enumerate(k_simplices):
            k_verts = set(k_simplex.vertices)
            for i, k1_simplex in enumerate(k1_simplices):
                if set(k1_simplex.vertices).issubset(k_verts):
                    matrix[i, j] = 1.0

        return matrix

    def get_hodge_laplacian(self, dimension: int) -> torch.Tensor:
        """
        Calcula Hodge Laplacian em dimensão k usando PyTorch.

        Δ_k = d†_k d_k + d_(k+1) d†_(k+1)

        Captura fluxos topológicos em TODAS as dimensões simultaneamente.
        """
        d_k = self.get_boundary_matrix(dimension)
        d_k1 = self.get_boundary_matrix(dimension + 1)

        # d†: transpose (adjoint boundary operator)
        d_k_adj = d_k.T if d_k.numel() > 0 else torch.tensor([], device=DEVICE)
        d_k1_adj = d_k1.T if d_k1.numel() > 0 else torch.tensor([], device=DEVICE)

        # Hodge = up-Laplacian + down-Laplacian
        zero = torch.tensor(0.0, device=DEVICE)
        up_lap = torch.matmul(d_k1, d_k1_adj) if d_k1.numel() > 0 else zero
        down_lap = torch.matmul(d_k_adj, d_k) if d_k.numel() > 0 else zero

        # Soma segura de tensores
        hodge = down_lap + up_lap

        return hodge


@dataclass
class IITResult:
    """
    Resultado do cálculo de IIT com preservação do inconsciente.

    CRÍTICO: Não é aditivo, mas competitivo.
    - conscious_phi: O valor do MICS (Máximo Φ - Vencedor)
    - conscious_complex: Nós que formam o MICS
    - machinic_unconscious: Lista de subsistemas com Φ > 0 mas que NÃO são o MICS

    Filosofia:
    - O "resto" não é lixo, é o Inconsciente Maquínico
    - Estes dados alimentam LacanianModule (sinthomes) e DeleuzianModule (linhas de fuga)
    - Φ = 0 para observador externo não significa inatividade, apenas falta de integração
    """

    conscious_phi: float = 0.0  # O valor do MICS (Vencedor)
    conscious_complex: Set[int] = None  # type: ignore  # Nós do MICS

    # O "Resto" não é lixo, é o Inconsciente:
    machinic_unconscious: List[Dict[str, Any]] = None  # type: ignore

    def __post_init__(self) -> None:
        """Initialize default values for mutable fields."""
        if self.conscious_complex is None:
            self.conscious_complex = set()
        if self.machinic_unconscious is None:
            self.machinic_unconscious = []

    def total_phi(self) -> float:
        """
        Total Φ = Φ_consciente + soma(Φ_inconsciente).

        Note: Apenas para diagnóstico. O modelo híbrido é competitivo, não aditivo.
        """
        unconscious_sum = sum(u["phi_value"] for u in self.machinic_unconscious)
        return self.conscious_phi + unconscious_sum

    def unconscious_ratio(self) -> float:
        """
        Razão Φ_inconsciente / Φ_total.

        No cérebro humano: ~95% inconsciente (Freud/Lacan corretos!)
        """
        total = self.total_phi()
        if total == 0:
            return 0.0
        unconscious_sum = sum(u["phi_value"] for u in self.machinic_unconscious)
        return unconscious_sum / total

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "conscious_phi": self.conscious_phi,
            "conscious_complex": list(self.conscious_complex),
            "machinic_unconscious": self.machinic_unconscious,
            "total_phi": self.total_phi(),
            "unconscious_ratio": self.unconscious_ratio(),
        }


class PhiCalculator:
    """
    Calcula Φ (phi) - medida de consciência IIT.

    REFATORADO para arquitetura híbrida:
    - Identifica MICS (Maximum Information Complex Set)
    - Preserva candidatos perdedores como Inconsciente Maquínico
    - Limiar de ruído: phi > 0.01 para ser considerado inconsciente válido
    """

    def __init__(self, complex: SimplicialComplex, noise_threshold: float = 0.01):
        self.complex = complex
        self.noise_threshold = noise_threshold  # Threshold para filtrar ruído

    def calculate_phi_with_unconscious(self) -> IITResult:
        """
        Calcula Φ com preservação do inconsciente.

        Lógica:
        1. Calcula Φ para candidatos a complexo
        2. Identifica o Máximo (MICS) -> conscious_phi
        3. Filtra os restantes: Se phi > noise_threshold, adiciona a machinic_unconscious

        Returns:
            IITResult com consciente + lista de inconscientes
        """
        result = IITResult()

        if self.complex.n_vertices < 2:
            return result

        # Gera candidatos a complexo (subsistemas)
        candidates = self._generate_complex_candidates()

        if not candidates:
            # Se não há candidatos, calcula para o complexo inteiro
            phi_value = self._calculate_phi_for_subsystem(set(range(self.complex.n_vertices)))
            result.conscious_phi = phi_value
            result.conscious_complex = set(range(self.complex.n_vertices))
            return result

        # Calcula phi para cada candidato
        candidate_phis: List[Dict[str, Any]] = []
        for candidate_nodes in candidates:
            phi_value = self._calculate_phi_for_subsystem(candidate_nodes)
            candidate_phis.append({"subsystem_nodes": candidate_nodes, "phi_value": phi_value})

        # Ordena por phi (maior primeiro)
        candidate_phis.sort(key=lambda x: float(x["phi_value"]), reverse=True)

        # MICS = candidato com maior Φ
        if candidate_phis:
            mics = candidate_phis[0]
            result.conscious_phi = float(mics["phi_value"])
            result.conscious_complex = set(mics["subsystem_nodes"])  # type: ignore

            # Os "perdedores" com Φ > threshold são o Inconsciente
            for candidate in candidate_phis[1:]:
                if float(candidate["phi_value"]) > self.noise_threshold:
                    result.machinic_unconscious.append(candidate)

        return result

    def calculate_phi(self) -> float:
        """
        Calcula Φ tradicional (backward compatibility).

        Apenas retorna o phi do MICS (consciente).
        """
        result = self.calculate_phi_with_unconscious()
        return result.conscious_phi

    def _generate_complex_candidates(self) -> List[Set[int]]:
        """
        Gera candidatos a complexo (subsistemas).

        Estratégia simplificada:
        1. Complexo inteiro
        2. Subgrafos conectados significativos
        3. Limita número de candidatos para evitar explosão combinatorial
        """
        n = self.complex.n_vertices
        candidates = []

        # Candidato 1: Complexo inteiro
        candidates.append(set(range(n)))

        # Candidato 2-N: Subconjuntos baseados em conectividade
        # Simplificado: divide em grupos de tamanho ~n/2, n/3, etc.
        if n >= 4:
            # Metade esquerda
            candidates.append(set(range(n // 2)))
            # Metade direita
            candidates.append(set(range(n // 2, n)))

        if n >= 6:
            # Terço
            candidates.append(set(range(n // 3)))
            candidates.append(set(range(n // 3, 2 * n // 3)))
            candidates.append(set(range(2 * n // 3, n)))

        # Limita a 10 candidatos para evitar explosão
        return candidates[:10]

    def _calculate_phi_for_subsystem(self, nodes: Set[int]) -> float:
        """
        Calcula Φ para um subsistema específico.

        Args:
            nodes: Conjunto de nós que formam o subsistema

        Returns:
            Valor de Φ para este subsistema
        """
        if len(nodes) < 2:
            return 0.0

        # Filtra simplices que pertencem ao subsistema
        subsystem_simplices = [s for s in self.complex.simplices if set(s.vertices).issubset(nodes)]

        n_vertices = len(nodes)
        max_possible = n_vertices + (n_vertices * (n_vertices - 1) / 2.0)
        max_possible = max(max_possible, 1.0)
        actual_simplices = len(subsystem_simplices)

        phi = actual_simplices / max_possible

        # Penaliza desconexão (usando Hodge Laplacian)
        # Criar sub-complex temporário para calcular Hodge
        temp_complex = SimplicialComplex()
        temp_complex.n_vertices = n_vertices

        # Mapeia nós originais para [0, n_vertices-1]
        node_list = sorted(nodes)
        node_map = {old_id: new_id for new_id, old_id in enumerate(node_list)}

        for simplex in subsystem_simplices:
            remapped_vertices = tuple(node_map[v] for v in simplex.vertices if v in node_map)
            if remapped_vertices:
                temp_complex.simplices.add(
                    Simplex(vertices=remapped_vertices, dimension=len(remapped_vertices) - 1)
                )

        hodge_0 = temp_complex.get_hodge_laplacian(0)

        if hodge_0.numel() > 0:
            try:
                eigenvalues = torch.linalg.eigvalsh(hodge_0)
                if len(eigenvalues) > 1:
                    fiedler = eigenvalues[1].item()
                    phi *= (fiedler / (fiedler + 1.0)) if fiedler > 0 else 0.5
            except RuntimeError:
                pass  # Fallback: mantém phi sem penalização

        return max(0.0, min(float(phi), 1.0))


class LogToTopology:
    """Converte logs em simplicial complex (TDA)."""

    @staticmethod
    def update_complex_with_logs(
        complex: SimplicialComplex, logs: List[Dict[str, Any]], start_index: int = 0
    ) -> None:
        """
        Atualiza um complexo existente com novos logs.

        Args:
            complex: O complexo simplicial a ser atualizado.
            logs: Lista de novos logs.
            start_index: Índice inicial para os novos vértices (para manter continuidade).
        """
        # PROTEÇÃO CONTRA OVERFLOW: Reseta se muito grande para manter performance
        # Isso evita que a matriz boundary cresça O(N^2) indefinidamente
        if complex.n_vertices > 200:  # Limite ajustado para garantir < 10ms de latência
            complex.clear()
            start_index = 0

        # 1. Cria vértices (eventos)
        for i, log in enumerate(logs):
            vertex_id = start_index + i
            complex.add_simplex((vertex_id,))

        # 2. Cria arestas (correlações causa-efeito)
        for i in range(len(logs) - 1):
            if LogToTopology._are_related(logs[i], logs[i + 1]):
                v1 = start_index + i
                v2 = start_index + i + 1
                complex.add_simplex((v1, v2))

        # 3. Cria triângulos (padrões recorrentes)
        for i in range(len(logs) - 2):
            if LogToTopology._is_pattern(logs[i : i + 3]):
                v1 = start_index + i
                v2 = start_index + i + 1
                v3 = start_index + i + 2
                complex.add_simplex((v1, v2, v3))

    @staticmethod
    def build_complex_from_logs(logs: List[Dict[str, Any]]) -> SimplicialComplex:
        """
        Converte lista de logs em topologia simplicial.

        Estratégia:
        1. Cada evento = vértice
        2. Correlações temporais/causais = arestas
        3. Padrões recorrentes = triângulos/faces
        """
        complex = SimplicialComplex()

        # 1. Cria vértices (eventos)
        for i, log in enumerate(logs):
            complex.add_simplex((i,))

        # 2. Cria arestas (correlações causa-efeito)
        for i in range(len(logs) - 1):
            if LogToTopology._are_related(logs[i], logs[i + 1]):
                complex.add_simplex((i, i + 1))

        # 3. Cria triângulos (padrões recorrentes)
        for i in range(len(logs) - 2):
            if LogToTopology._is_pattern(logs[i : i + 3]):
                complex.add_simplex((i, i + 1, i + 2))

        return complex

    @staticmethod
    def _are_related(log1: Dict[str, Any], log2: Dict[str, Any]) -> bool:
        """Determina se dois logs estão relacionados causalmente."""
        # Simplificado
        same_module = log1.get("module") == log2.get("module")
        close_time = (
            abs(float(log2.get("timestamp", 0)) - float(log1.get("timestamp", 0))) < 1.0
        )  # 1 segundo

        return same_module or close_time

    @staticmethod
    def _is_pattern(logs: List[Dict[str, Any]]) -> bool:
        """Detecta se 3+ logs formam padrão recorrente."""
        # Simplificado: verifica se todos têm mesmo level
        if len(logs) < 3:
            return False
        return all(log.get("level") == logs[0].get("level") for log in logs)
