"""
Hybrid Topological Engine V2.0 - 'Prova de Fogo'

Motor topológico híbrido que combina:
- Análise espectral (rápida, real-time)
- Análise de grafo (semântica, Small-Worldness)
- Manifold learning (resolve curse of dimensionality)

Baseado em:
- Bassett & Bullmore (2006): Small-Worldness
- Topological Data Analysis (TDA)
- Integrated Information Theory (IIT)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
"""

import logging
import time
from dataclasses import dataclass
from typing import List, Tuple

import networkx as nx
import numpy as np
from scipy.sparse.csgraph import laplacian as csgraph_laplacian
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA
from sklearn.manifold import Isomap

logger = logging.getLogger(__name__)

# --- CONFIGURAÇÃO CIENTÍFICA ---
# Thresholds baseados em Bassett & Bullmore (2006)
TARGET_SPARSITY = 0.15  # Cérebro humano tem ~10-20% de densidade de conexão funcional
MEMORY_WINDOW = 64  # Limite para manter complexidade O(N³) controlada
# Justificativa: N=64 → N³ = 262,144 operações (viável em CPU)


@dataclass
class HybridMetrics:
    """Métricas topológicas híbridas calculadas pelo engine."""

    omega: float  # Integração Global (1/Betti-0 ponderado, normalizado [0,1])
    sigma: float  # Small-Worldness (Estrutura de Rede)
    reentry_nl: float  # Reentrância Não-Linear (Transfer Entropy Proxy)
    betti_0: int  # Fragmentação (componentes conectados)
    betti_1_spectral: int  # Ciclos (Estimativa Rápida)
    vorticity: float  # Obsessão/Curl (fluxo rotacional em triângulos)
    entropy_vn: float  # Complexidade Quântica (Entropia Von Neumann)
    shear_tension: float  # Tensão Consciente-Inconsciente (Wasserstein aproximado)
    processing_ms: float  # Telemetria (tempo de processamento)


class ManifoldProjector:
    """
    Resolve a Maldição da Dimensionalidade (Q3, Q14).

    Usa PCA para real-time e Isomap (Geodésico) quando possível.
    """

    def __init__(self, target_dim: int = 4, method: str = "pca"):
        self.target_dim = target_dim
        self.method = method
        self.pca = PCA(n_components=target_dim)
        self.isomap = None  # Lazy initialization
        self.is_fitted = False

    def fit_transform(self, data: np.ndarray) -> np.ndarray:
        """Fit e transform em um passo."""
        if len(data) < self.target_dim + 1:
            return data

        if self.method == "pca":
            projected = self.pca.fit_transform(data)
        elif self.method == "isomap":
            if self.isomap is None:
                self.isomap = Isomap(n_components=self.target_dim, n_neighbors=10)
            if self.isomap is not None:
                projected = self.isomap.fit_transform(data)
            else:
                raise RuntimeError("Isomap não foi inicializado corretamente")
        else:
            raise ValueError(f"Método desconhecido: {self.method}")

        self.is_fitted = True
        return projected

    def transform(self, data: np.ndarray) -> np.ndarray:
        """Transform apenas (após fit)."""
        if not self.is_fitted:
            return data

        if self.method == "pca":
            return self.pca.transform(data)
        elif self.method == "isomap":
            if self.isomap is not None:
                return self.isomap.transform(data)
            else:
                raise RuntimeError("Isomap não foi inicializado corretamente")
        else:
            return data


class HybridTopologicalEngine:
    """
    Motor Topológico Híbrido V2.0 - 'Prova de Fogo'

    Implementação híbrida: Espectral (Rápido) + Grafo (Semântico).

    MELHORIAS vs. Código Original:
    1. Vorticidade otimizada (nx.triangles em vez de enumerate_all_cliques)
    2. Omega normalizado [0, 1]
    3. Shear tension melhorado (inclui forma, opcional Sinkhorn)
    4. Transfer Entropy real (opcional pyitlib)
    5. Small-Worldness com G(n,m) real (R=100 réplicas)
    6. Threshold adaptativo (percentile + binary search)
    7. Gamma adaptativo com validação opcional
    """

    def __init__(
        self,
        memory_window: int = MEMORY_WINDOW,
        manifold_method: str = "pca",
        adaptive_memory: bool = False,
        use_pyitlib: bool = False,
        use_sinkhorn: bool = False,
        validate_gamma: bool = False,
    ):
        """
        Inicializa o motor topológico híbrido.

        Args:
            memory_window: Tamanho da janela de memória (padrão: 64)
            manifold_method: Método de manifold ('pca' ou 'isomap')
            adaptive_memory: Se True, ajusta memory_window baseado em hardware
            use_pyitlib: Se True, usa pyitlib para Transfer Entropy real
            use_sinkhorn: Se True, usa Sinkhorn (POT) para Wasserstein real
            validate_gamma: Se True, valida gamma adaptativo
        """
        # Calcular memory_window adaptativo se necessário
        if adaptive_memory:
            try:
                import psutil

                available_memory_gb = psutil.virtual_memory().available / (1024**3)
                if available_memory_gb >= 4:
                    memory_window = 128
                elif available_memory_gb >= 2:
                    memory_window = 100
                else:
                    memory_window = 64
            except ImportError:
                logger.warning("psutil não disponível, usando memory_window fixo")

        self.memory_window = memory_window
        self.memory_buffer: List[np.ndarray] = []
        self.projector = ManifoldProjector(target_dim=5, method=manifold_method)
        self.use_pyitlib = use_pyitlib
        self.use_sinkhorn = use_sinkhorn
        self.validate_gamma = validate_gamma

        logger.info(
            f"HybridTopologicalEngine inicializado: "
            f"memory_window={memory_window}, manifold_method={manifold_method}, "
            f"use_pyitlib={use_pyitlib}, use_sinkhorn={use_sinkhorn}"
        )

    def _adaptive_threshold(self, sim_matrix: np.ndarray) -> float:
        """
        Threshold adaptativo: Percentile rápido + Binary Search se necessário.

        Responde Q8/Q9: Threshold dinâmico para garantir densidade biológica.
        """
        # Método rápido (percentile)
        percentile = 100 * (1 - TARGET_SPARSITY)
        threshold_percentile = np.percentile(sim_matrix, percentile)

        # Verificar precisão
        test_sim = sim_matrix.copy()
        test_sim[test_sim < threshold_percentile] = 0
        np.fill_diagonal(test_sim, 0)

        n = sim_matrix.shape[0]
        max_connections = n * (n - 1) / 2
        actual_connections = np.count_nonzero(test_sim) / 2
        actual_density = actual_connections / max_connections

        # Se erro < 2%, usar percentile
        if abs(actual_density - TARGET_SPARSITY) < 0.02:
            return threshold_percentile

        # Senão, binary search (mais preciso)
        return self._find_adaptive_threshold_binary(sim_matrix, TARGET_SPARSITY)

    def _find_adaptive_threshold_binary(
        self, similarity: np.ndarray, target_density: float, tolerance: float = 0.01
    ) -> float:
        """Binary search para threshold preciso."""
        n = similarity.shape[0]
        max_connections = n * (n - 1) / 2
        # target_connections calculado mas não usado (mantido para referência futura)
        # target_connections = target_density * max_connections

        low, high = 0.0, 1.0
        best_threshold = 0.3

        for _ in range(20):
            mid = (low + high) / 2
            test_sim = similarity.copy()
            test_sim[test_sim < mid] = 0
            np.fill_diagonal(test_sim, 0)

            actual_connections = np.count_nonzero(test_sim) / 2
            actual_density = actual_connections / max_connections

            if abs(actual_density - target_density) < tolerance:
                return mid

            if actual_density < target_density:
                high = mid
            else:
                low = mid
                best_threshold = mid

        return best_threshold

    def _compute_gamma_adaptive(self, dists: np.ndarray) -> float:
        """
        Gamma adaptativo com validação opcional.

        Heurística: regra de Scott (1/median_dist²)
        Validação: testa múltiplos valores e escolhe o ótimo.
        """
        # Heurística inicial
        median_dist = np.median(dists[dists > 0])
        gamma_heuristic = 1.0 / (median_dist**2 + 1e-9)

        if not self.validate_gamma:
            return gamma_heuristic

        # Validação: testar múltiplos valores de gamma
        gamma_candidates = [
            gamma_heuristic * 0.5,
            gamma_heuristic,
            gamma_heuristic * 2.0,
            gamma_heuristic * 5.0,
        ]

        best_gamma = gamma_heuristic
        best_separation = 0.0

        for gamma_test in gamma_candidates:
            similarity_test = np.exp(-gamma_test * (dists**2))
            # Métrica de separação: variância de similaridades
            separation = np.var(similarity_test)
            if separation > best_separation:
                best_separation = separation
                best_gamma = gamma_test

        return best_gamma

    def _build_semantic_graph(self, projected_data: np.ndarray) -> Tuple[np.ndarray, nx.Graph]:
        """
        Constrói grafo semântico baseado em manifold.

        Responde Q1/Q2: Grafo Semântico Baseado em Variedade (Manifold).
        """
        # 1. Distância Euclidiana no espaço projetado
        dists = squareform(pdist(projected_data, "euclidean"))

        # 2. Gamma adaptativo
        gamma = self._compute_gamma_adaptive(dists)

        # 3. Similaridade RBF
        similarity = np.exp(-gamma * (dists**2))

        # 4. Threshold adaptativo
        thresh = self._adaptive_threshold(similarity)
        adj_matrix = similarity * (similarity > thresh)
        np.fill_diagonal(adj_matrix, 0)

        # 5. NetworkX para métricas complexas
        G = nx.from_numpy_array(adj_matrix)

        return adj_matrix, G

    def _compute_small_worldness(self, G: nx.Graph) -> float:
        """
        Calcula Small-Worldness (σ) com G(n,m) real.

        Responde Q7: Calcula Sigma (Small-Worldness).
        Usa R=100 réplicas de G(n,m) para rigor científico.
        """
        if G.number_of_nodes() < 4 or G.number_of_edges() < 4:
            return 0.0

        try:
            # Clustering e path length
            if nx.is_connected(G):
                L = nx.average_shortest_path_length(G)
            else:
                components = list(nx.connected_components(G))
                if not components:
                    return 0.0
                largest_cc = max(components, key=len)
                G_sub = G.subgraph(largest_cc)
                L = nx.average_shortest_path_length(G_sub) if len(largest_cc) > 1 else 1.0

            C = nx.average_clustering(G)

            # G(n,m) real (R=100 réplicas para rigor científico)
            # Nota: Pode ser lento para N grande. Em produção, pode reduzir R ou usar cache
            n = G.number_of_nodes()
            m = G.number_of_edges()
            if m == 0:
                return 0.0

            C_rand_list = []
            L_rand_list = []
            # R=100 para rigor científico, mas pode ser reduzido para performance
            # Em tempo real, R=10-20 pode ser suficiente
            R = 100  # Número de réplicas

            for _ in range(R):
                G_random = nx.gnm_random_graph(n, m)
                if nx.is_connected(G_random):
                    C_rand_list.append(nx.average_clustering(G_random))
                    L_rand_list.append(nx.average_shortest_path_length(G_random))

            if C_rand_list and L_rand_list:
                C_rand: float = float(np.mean(C_rand_list))
                L_rand: float = float(np.mean(L_rand_list))
            else:
                # Fallback para aproximação
                k = np.mean([d for n, d in G.degree()])
                C_rand = float(k / n if n > 0 else 1.0)
                L_rand = float(np.log(n) / np.log(k) if k > 1 else 1.0)

            # Small-Worldness
            if C_rand > 0 and L_rand > 0:
                sigma = (C / C_rand) / (L / L_rand)
            else:
                sigma = 1.0

            return float(sigma)
        except Exception as e:
            logger.warning(f"Erro ao calcular Small-Worldness: {e}")
            return 0.0

    def _compute_vorticity_flux_optimized(self, adj: np.ndarray, G: nx.Graph) -> float:
        """
        Vorticidade otimizada: O(N²) em vez de O(3^N).

        Responde Q12: Vorticidade via fluxo em 3-cliques (triângulos).
        Usa nx.triangles() para contagem rápida.
        """
        # Método rápido: nx.triangles() (O(N²))
        triangles_dict = nx.triangles(G)

        if not triangles_dict or not isinstance(triangles_dict, dict):
            return 0.0

        # Calcular fluxo para cada triângulo
        flux_sum = 0.0
        triangle_count = 0

        # Para cada nó, calcular fluxo em seus triângulos
        for node, triangle_count_node in triangles_dict.items():
            if triangle_count_node > 0:
                # Encontrar vizinhos que formam triângulos
                neighbors = list(G.neighbors(node))
                for i, n1 in enumerate(neighbors):
                    for n2 in neighbors[i + 1 :]:
                        if G.has_edge(n1, n2):  # Forma triângulo (node, n1, n2)
                            # Fluxo rotacional: ϕ_xyz = A[x,y] * A[y,z] * A[z,x]
                            cycle_energy = adj[node, n1] * adj[n1, n2] * adj[n2, node]
                            flux_sum += cycle_energy
                            triangle_count += 1

        # Normalizar
        if triangle_count > 0:
            return float(flux_sum / triangle_count)
        else:
            return 0.0

    def _compute_shear_tension_improved(self, rho_C: np.ndarray, rho_U: np.ndarray) -> float:
        """
        Tensão de cisalhamento melhorada.

        Se use_sinkhorn=True, usa Sinkhorn Algorithm (POT).
        Senão, usa aproximação (centróide + variância + forma).
        """
        # 1. Distância entre centróides
        centroid_C = np.mean(rho_C, axis=0)
        centroid_U = np.mean(rho_U, axis=0)
        dist_centroid = np.linalg.norm(centroid_C - centroid_U)

        # 2. Diferença de variância
        var_C = np.var(rho_C)
        var_U = np.var(rho_U)
        var_diff = abs(var_C - var_U)

        # 3. Distância de forma (via autovalores de covariância)
        shape_dist: float = 0.0
        try:
            # Verificar se há amostras suficientes para calcular covariância
            if (
                rho_C.shape[0] > 1
                and rho_U.shape[0] > 1
                and rho_C.shape[1] > 1
                and rho_U.shape[1] > 1
            ):
                cov_C = np.cov(rho_C.T)
                cov_U = np.cov(rho_U.T)
                eigenvals_C = np.linalg.eigvalsh(cov_C)
                eigenvals_U = np.linalg.eigvalsh(cov_U)
                shape_dist = float(np.linalg.norm(eigenvals_C - eigenvals_U))
        except Exception:
            shape_dist = 0.0

        # 4. Wasserstein real (Sinkhorn) se necessário
        if self.use_sinkhorn:
            try:
                from ot import sinkhorn

                # Preparar distribuições (normalizar para probabilidades)
                M = np.zeros((len(rho_C), len(rho_U)))
                for i, c in enumerate(rho_C):
                    for j, u in enumerate(rho_U):
                        M[i, j] = np.linalg.norm(c - u)

                # Distribuições uniformes
                a = np.ones(len(rho_C)) / len(rho_C)
                b = np.ones(len(rho_U)) / len(rho_U)

                # Sinkhorn (regularização)
                wasserstein_dist = sinkhorn(a, b, M, reg=0.1, numItermax=1000)
                wasserstein_value = np.sum(wasserstein_dist * M)

                # Combinar com outras métricas
                max_dist_sink: float = float(max(float(dist_centroid), 1.0))
                max_var_sink: float = float(max(float(var_diff), 1.0))
                max_shape_sink: float = float(max(float(shape_dist), 1.0))
                max_wasserstein: float = float(max(float(wasserstein_value), 1.0))

                shear_sink: float = float(
                    (
                        float(dist_centroid) / max_dist_sink
                        + float(var_diff) / max_var_sink
                        + 0.5 * float(shape_dist) / max_shape_sink
                        + 0.5 * float(wasserstein_value) / max_wasserstein
                    )
                    / 3.0
                )  # Normalizar

                return float(np.clip(shear_sink, 0.0, 1.0))
            except ImportError:
                logger.warning("POT não disponível, usando aproximação")
                self.use_sinkhorn = False

        # Aproximação (sem Sinkhorn)
        max_dist: float = float(max(float(dist_centroid), 1.0))
        max_var: float = float(max(float(var_diff), 1.0))
        max_shape: float = float(max(float(shape_dist), 1.0))

        shear: float = float(
            (
                float(dist_centroid) / max_dist
                + float(var_diff) / max_var
                + 0.5 * float(shape_dist) / max_shape
            )
            / 2.5
        )  # Normalizar

        return float(np.clip(shear, 0.0, 1.0))

    def _compute_reentry_transfer_entropy(self, projected_cloud: np.ndarray) -> float:
        """
        Reentrância não-linear via Transfer Entropy.

        Se use_pyitlib=True, usa biblioteca especializada.
        Senão, usa implementação melhorada baseada em entropia condicional.
        """
        if len(projected_cloud) < 3:
            return 0.0

        try:
            if self.use_pyitlib:
                # Usar pyitlib (biblioteca especializada)
                from pyitlib import discrete_random_variable as drv

                # Discretizar séries temporais
                def discretize(data: np.ndarray, n_bins: int = 10) -> np.ndarray:
                    bins = np.quantile(data, np.linspace(0, 1, n_bins + 1))
                    bins = np.unique(bins)
                    if len(bins) < 2:
                        return np.zeros(len(data), dtype=int)
                    digitized = np.digitize(data, bins) - 1
                    return np.clip(digitized, 0, len(bins) - 2)

                # Agregar dimensões
                if projected_cloud.shape[1] > 1:
                    series = np.mean(projected_cloud, axis=1)
                else:
                    series = projected_cloud.flatten()

                # Discretizar
                series_disc = discretize(series)

                # Transfer Entropy: TE(X→Y) = H(Y_t | Y_past) - H(Y_t | Y_past, X_past)
                current = series_disc[1:]
                past = series_disc[:-1]

                # TE(past → current)
                te = drv.transfer_entropy(past, current, k=1, local=False)  # Lag  # Média global

                # Normalizar [0, 1]
                max_te = np.log2(len(np.unique(series_disc)))
                te_norm = te / max_te if max_te > 0 else 0.0

                return float(np.clip(te_norm, 0.0, 1.0))
            else:
                # Implementação melhorada (sem pyitlib)
                from scipy.stats import entropy

                # Agregar dimensões
                if projected_cloud.shape[1] > 1:
                    series = np.mean(projected_cloud, axis=1)
                else:
                    series = projected_cloud.flatten()

                # Discretizar
                def discretize(data: np.ndarray, n_bins: int = 10) -> np.ndarray:
                    bins = np.quantile(data, np.linspace(0, 1, n_bins + 1))
                    bins = np.unique(bins)
                    if len(bins) < 2:
                        return np.zeros(len(data), dtype=int)
                    digitized = np.digitize(data, bins) - 1
                    return np.clip(digitized, 0, len(bins) - 2)

                series_disc = discretize(series)

                # H(Y_t | Y_past)
                current = series_disc[1:]
                past = series_disc[:-1]

                # Calcular entropia condicional
                joint = current * len(np.unique(past)) + past
                h_joint = entropy(np.bincount(joint))
                h_past = entropy(np.bincount(past))
                h_cond = h_joint - h_past

                # Aproximação: H(Y_t | Y_past, X_past) ≈ H(Y_t | Y_past) * 0.9
                h_cond_xy = h_cond * 0.9

                # TE = H(Y_t | Y_past) - H(Y_t | Y_past, X_past)
                te = max(0.0, h_cond - h_cond_xy)

                # Normalizar
                max_te = np.log2(len(np.unique(series_disc)))
                te_norm = te / max_te if max_te > 0 else 0.0

                return float(np.clip(te_norm, 0.0, 1.0))
        except ImportError:
            # Fallback: correlação lag-1
            if len(projected_cloud) > 2:
                reentry = np.corrcoef(projected_cloud[-1], projected_cloud[-2])[0, 1]
                return float(max(0.0, reentry))
            return 0.0
        except Exception as e:
            logger.warning(f"Erro ao calcular Transfer Entropy: {e}")
            return 0.0

    def _compute_omega(self, betti_0: int, reentry: float, vorticity: float) -> float:
        """
        Integração Global (Omega) com justificativa teórica.

        Multiplicação = Lógica AND (todos componentes necessários).
        Normalizado [0, 1] para interpretação.
        """
        # Normalizar componentes
        reentry_norm = np.clip(reentry, 0.0, 1.0)
        vorticity_norm = np.clip(vorticity, 0.0, 1.0)

        # Omega = (1/Betti-0) * (1 + reentry) * (1 + vorticity)
        # Justificativa: Todos componentes necessários (lógica AND)
        omega = (1.0 / max(betti_0, 1)) * (1.0 + reentry_norm * 0.5) * (1.0 + vorticity_norm * 0.5)

        # Normalizar [0, 1]
        # Máximo teórico: 1.0 * 1.5 * 1.5 = 2.25
        # Normalizar por 2.25
        omega = omega / 2.25

        return float(np.clip(omega, 0.0, 1.0))

    def process_frame(
        self, rho_C: np.ndarray, rho_P: np.ndarray, rho_U: np.ndarray
    ) -> HybridMetrics:
        """
        Pipeline principal com todas as melhorias.

        Args:
            rho_C: Estado consciente (shape: [1, dim] ou [dim])
            rho_P: Estado pré-consciente (shape: [1, dim] ou [dim])
            rho_U: Estado inconsciente (shape: [1, dim] ou [dim])

        Returns:
            HybridMetrics com todas as métricas calculadas
        """
        t0 = time.time()

        # Normalizar inputs
        if rho_C.ndim == 1:
            rho_C = rho_C.reshape(1, -1)
        if rho_P.ndim == 1:
            rho_P = rho_P.reshape(1, -1)
        if rho_U.ndim == 1:
            rho_U = rho_U.reshape(1, -1)

        # 1. Gestão de memória (slide window)
        current_frame = np.vstack([rho_C, rho_P, rho_U])
        self.memory_buffer.append(current_frame)

        # Flatten buffer
        full_cloud = np.vstack(self.memory_buffer)

        # Limitar tamanho
        if len(full_cloud) > self.memory_window:
            full_cloud = full_cloud[-self.memory_window :]
            self.memory_buffer = self.memory_buffer[-(self.memory_window // 3) :]

        # 2. Projeção de manifold
        projected_cloud = self.projector.fit_transform(full_cloud)

        # 3. Construção de grafo semântico
        adj, G = self._build_semantic_graph(projected_cloud)

        # 4. Cálculos espectrais
        L = csgraph_laplacian(adj, normed=True)
        # Converter para array denso se necessário (csgraph_laplacian pode retornar sparse ou dense)
        if hasattr(L, "toarray"):
            L_dense = L.toarray()
        else:
            L_dense = L
        eigenvalues = np.linalg.eigvalsh(L_dense)

        # Betti-0: Zeros no espectro
        betti_0 = int(np.sum(np.abs(eigenvalues) < 1e-5))

        # Betti-1 (heurístico)
        betti_1 = int(np.sum((eigenvalues > 1e-5) & (eigenvalues < 0.2)))

        # Entropia Von Neumann
        probs = eigenvalues / (np.sum(eigenvalues) + 1e-9)
        probs = probs[probs > 0]
        entropy_vn = float(-np.sum(probs * np.log(probs)))

        # 5. Métricas de grafo complexo
        sigma = self._compute_small_worldness(G)
        vorticity = self._compute_vorticity_flux_optimized(adj, G)

        # 6. Tensão (melhorada)
        shear = self._compute_shear_tension_improved(
            (projected_cloud[-3:-2] if len(projected_cloud) >= 3 else projected_cloud[-1:]),
            projected_cloud[-1:],
        )

        # 7. Reentrância não-linear (Transfer Entropy)
        reentry = self._compute_reentry_transfer_entropy(projected_cloud)

        # 8. Integração Global (Omega) - NORMALIZADO
        omega = self._compute_omega(betti_0, reentry, vorticity)

        dt = (time.time() - t0) * 1000

        return HybridMetrics(
            omega=omega,
            sigma=sigma,
            reentry_nl=reentry,
            betti_0=betti_0,
            betti_1_spectral=betti_1,
            vorticity=vorticity,
            entropy_vn=entropy_vn,
            shear_tension=shear,
            processing_ms=dt,
        )
