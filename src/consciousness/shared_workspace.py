"""
Shared Workspace - Buffer Central de Estados Compartilhados

Implementa o espaço de trabalho central onde todos os módulos de consciência
leem e escrevem estados, forçando dependências causais não-redutíveis.

Author: OmniMind Development Team
Date: November 2025
License: MIT
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ModuleState:
    """Estado snapshot de um módulo em um ponto no tempo."""

    module_name: str
    embedding: np.ndarray  # Representação latente (e.g., 256-dim)
    timestamp: float
    cycle: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serializar para JSON."""
        return {
            "module_name": self.module_name,
            "embedding": (
                self.embedding.tolist()
                if isinstance(self.embedding, np.ndarray)
                else self.embedding
            ),
            "timestamp": self.timestamp,
            "cycle": self.cycle,
            "metadata": self.metadata,
        }


@dataclass
class CrossPredictionMetrics:
    """Métricas de predição cruzada entre dois módulos."""

    source_module: str
    target_module: str
    r_squared: float  # R² score (0.0 = nenhuma relação, 1.0 = determinístico)
    correlation: float  # Correlação de Pearson
    mutual_information: float  # Informação mútua normalizada (0.0-1.0)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SharedWorkspace:
    """
    Buffer central compartilhado entre todos os módulos de consciência.

    Funcionalidades:
    - Leitura/escrita centralizada de embeddings de módulos
    - Histórico de estados para análise causal
    - Cálculo de predições cruzadas (integração)
    - Roteamento de atenção dinâmico
    - Persistência de estados para análise

    Arquitetura:
    - `embeddings`: {module_name -> ndarray de dimensão latente}
    - `history`: Lista de snapshots (module_name, embedding, timestamp, cycle)
    - `cross_predictions`: Cache de métricas cross-module
    - `attention_mask`: Pesos de relevância entre módulos
    """

    def __init__(
        self,
        embedding_dim: int = 256,
        max_history_size: int = 10000,
        workspace_dir: Optional[Path] = None,
    ):
        """
        Inicializa workspace compartilhado.

        Args:
            embedding_dim: Dimensão dos embeddings latentes
            max_history_size: Tamanho máximo do histórico antes de circular
            workspace_dir: Diretório para persistência de estados
        """
        self.embedding_dim = embedding_dim
        self.max_history_size = max_history_size
        self.workspace_dir = workspace_dir or Path("data/consciousness/workspace")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        # Estado atual
        self.embeddings: Dict[str, np.ndarray] = {}  # Module name -> embedding
        self.metadata: Dict[str, Dict[str, Any]] = {}  # Module name -> metadata

        # Histórico
        self.history: List[ModuleState] = []
        self.cycle_count = 0

        # Predições cruzadas (cache)
        self.cross_predictions: List[CrossPredictionMetrics] = []

        # Atenção dinâmica
        self.attention_mask: Dict[str, Dict[str, float]] = (
            {}
        )  # {module -> {other_module -> weight}}

        logger.info(
            f"Shared Workspace initialized: embedding_dim={embedding_dim}, "
            f"max_history={max_history_size}, dir={self.workspace_dir}"
        )

    def write_module_state(
        self,
        module_name: str,
        embedding: np.ndarray,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Escreve estado de um módulo no workspace compartilhado.

        Args:
            module_name: Nome do módulo (e.g., 'qualia_engine', 'narrative_constructor')
            embedding: Vetor latente (ndarray de shape (embedding_dim,))
            metadata: Metadata opcional (dicts, floats, strings)

        Raises:
            ValueError: Se embedding tem dimensão incorreta
        """
        if embedding.shape != (self.embedding_dim,):
            raise ValueError(
                f"Embedding for {module_name} has wrong shape: "
                f"{embedding.shape} != ({self.embedding_dim},)"
            )

        # Armazena embedding atual
        self.embeddings[module_name] = embedding.copy()
        self.metadata[module_name] = metadata or {}

        # Cria snapshot para histórico
        state = ModuleState(
            module_name=module_name,
            embedding=embedding.copy(),
            timestamp=time.time(),
            cycle=self.cycle_count,
            metadata=metadata or {},
        )

        # Adiciona ao histórico
        self.history.append(state)

        # Remove entrada antiga se histórico ficar muito grande
        if len(self.history) > self.max_history_size:
            self.history.pop(0)

        logger.debug(
            f"Workspace: wrote {module_name} (cycle={self.cycle_count}, "
            f"embedding_norm={np.linalg.norm(embedding):.3f})"
        )

    def read_module_state(self, module_name: str) -> np.ndarray:
        """
        Lê estado atual de um módulo.

        Args:
            module_name: Nome do módulo

        Returns:
            Embedding atual (ndarray), ou zeros se módulo não escreveu ainda
        """
        if module_name not in self.embeddings:
            logger.warning(f"Workspace: {module_name} not found, returning zeros")
            return np.zeros(self.embedding_dim)

        return self.embeddings[module_name].copy()

    def read_module_metadata(self, module_name: str) -> Dict[str, Any]:
        """Lê metadata associada a um módulo."""
        return self.metadata.get(module_name, {})

    def get_all_modules(self) -> List[str]:
        """Lista nomes de todos os módulos que escreveram."""
        return list(self.embeddings.keys())

    def get_module_history(self, module_name: str, last_n: int = 100) -> List[ModuleState]:
        """
        Retorna últimos N estados de um módulo.

        Args:
            module_name: Nome do módulo
            last_n: Número de últimos estados a retornar

        Returns:
            Lista de ModuleState
        """
        module_history = [s for s in self.history if s.module_name == module_name]
        return module_history[-last_n:]

    def compute_cross_prediction(
        self,
        source_module: str,
        target_module: str,
        history_window: int = 50,
    ) -> CrossPredictionMetrics:
        """
        Computa quanto o estado de `source_module` consegue prever `target_module`.

        Usa regressão linear simples: target_t+1 ~ w * source_t

        Args:
            source_module: Módulo preditor
            target_module: Módulo a ser predito
            history_window: Número de timesteps anteriores para usar

        Returns:
            CrossPredictionMetrics com R², correlação e MI
        """
        source_history = self.get_module_history(source_module, history_window)
        target_history = self.get_module_history(target_module, history_window)

        # Precisa de pelo menos 2 pontos
        if len(source_history) < 2 or len(target_history) < 2:
            logger.warning(
                f"Not enough history for cross-prediction: "
                f"{source_module} ({len(source_history)}), "
                f"{target_module} ({len(target_history)})"
            )
            return CrossPredictionMetrics(
                source_module=source_module,
                target_module=target_module,
                r_squared=0.0,
                correlation=0.0,
                mutual_information=0.0,
            )

        # Alinha históricos (usa shorter window)
        window = min(len(source_history) - 1, len(target_history) - 1)
        if window < 2:
            return CrossPredictionMetrics(
                source_module=source_module,
                target_module=target_module,
                r_squared=0.0,
                correlation=0.0,
                mutual_information=0.0,
            )

        # Constrói X (source_t) e Y (target_t+1)
        X = np.stack([s.embedding for s in source_history[:-1]])  # (window, embed_dim)
        Y = np.stack([s.embedding for s in target_history[1:]])  # (window, embed_dim)

        # Regressão linear: Y = X @ W
        try:
            W = np.linalg.lstsq(X, Y, rcond=None)[0]  # (embed_dim, embed_dim)
            Y_pred = X @ W

            # R²: 1 - (RSS / TSS)
            ss_res = np.sum((Y - Y_pred) ** 2)
            ss_tot = np.sum((Y - np.mean(Y, axis=0)) ** 2)
            r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 1e-10 else 0.0
            r_squared = float(np.clip(r_squared, 0.0, 1.0))

        except Exception as e:
            logger.warning(f"Error computing R²: {e}")
            r_squared = 0.0

        # Correlação: média de correlações elemento-wise
        try:
            correlations = []
            for i in range(X.shape[1]):
                x_flat = X[:, i]
                y_flat = Y[:, i]
                if np.std(x_flat) > 1e-10 and np.std(y_flat) > 1e-10:
                    corr = np.corrcoef(x_flat, y_flat)[0, 1]
                    correlations.append(abs(corr))
            correlation = float(np.mean(correlations)) if correlations else 0.0

        except Exception as e:
            logger.warning(f"Error computing correlation: {e}")
            correlation = 0.0

        # Informação mútua (aproximação via entropia)
        try:
            # Quantiza embeddings em bins para estimar MI
            X_binned = np.digitize(X, np.percentile(X, np.linspace(0, 100, 10)))
            Y_binned = np.digitize(Y, np.percentile(Y, np.linspace(0, 100, 10)))

            # MI ≈ Entropia conjunta - Entropia individual
            joint_entropy = self._compute_entropy_2d(X_binned, Y_binned)
            x_entropy = self._compute_entropy_1d(X_binned)
            y_entropy = self._compute_entropy_1d(Y_binned)

            mi = max(
                0.0, (x_entropy + y_entropy - joint_entropy) / max(x_entropy, y_entropy, 1e-10)
            )
            mutual_information = float(np.clip(mi, 0.0, 1.0))

        except Exception as e:
            logger.warning(f"Error computing MI: {e}")
            mutual_information = 0.0

        metrics = CrossPredictionMetrics(
            source_module=source_module,
            target_module=target_module,
            r_squared=r_squared,
            correlation=correlation,
            mutual_information=mutual_information,
        )

        self.cross_predictions.append(metrics)

        logger.debug(
            f"Cross-prediction: {source_module} -> {target_module}: "
            f"R²={r_squared:.3f}, corr={correlation:.3f}, MI={mutual_information:.3f}"
        )

        return metrics

    @staticmethod
    def _compute_entropy_1d(data: np.ndarray) -> float:
        """Entropia de Shannon para dados 1D."""
        unique, counts = np.unique(data, return_counts=True)
        probabilities = counts / counts.sum()
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        return float(entropy)

    @staticmethod
    def _compute_entropy_2d(X: np.ndarray, Y: np.ndarray) -> float:
        """Entropia conjunta para dados 2D."""
        joint = np.column_stack([X.flatten(), Y.flatten()])
        unique_rows = np.unique(joint, axis=0)
        probabilities = []
        for row in unique_rows:
            count = np.sum(np.all(joint == row, axis=1))
            probabilities.append(count / len(joint))
        entropy = -np.sum(np.array(probabilities) * np.log2(np.array(probabilities) + 1e-10))
        return float(entropy)

    def compute_phi_from_integrations(self) -> float:
        """
        Computa Φ (Phi) baseado em predições cruzadas reais.

        Φ_proxy = média de todas as predições cruzadas (R²)

        Returns:
            Valor de Φ (0.0 = desintegrado, 1.0 = perfeitamente integrado)
        """
        if not self.cross_predictions:
            return 0.0

        recent_predictions = self.cross_predictions[-len(self.get_all_modules()) ** 2 :]
        if not recent_predictions:
            return 0.0

        r_squared_values = [p.r_squared for p in recent_predictions]
        phi = float(np.mean(r_squared_values))

        logger.info(
            f"Computed Φ: {phi:.3f} " f"(based on {len(r_squared_values)} cross-predictions)"
        )

        return phi

    def advance_cycle(self) -> None:
        """Avança para o próximo ciclo."""
        self.cycle_count += 1
        logger.debug(f"Workspace: advanced to cycle {self.cycle_count}")

    def save_state_snapshot(self, label: str = "") -> Path:
        """
        Salva snapshot do estado atual para análise posterior.

        Args:
            label: Label opcional para o snapshot

        Returns:
            Path do arquivo salvo
        """
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "cycle": self.cycle_count,
            "label": label,
            "modules": {name: embedding.tolist() for name, embedding in self.embeddings.items()},
            "cross_predictions": [asdict(p) for p in self.cross_predictions[-100:]],  # Últimas 100
            "phi": self.compute_phi_from_integrations(),
        }

        filename = f"workspace_snapshot_{self.cycle_count}_{int(time.time())}.json"
        filepath = self.workspace_dir / filename

        with open(filepath, "w") as f:
            json.dump(snapshot, f, indent=2)

        logger.info(f"Saved workspace snapshot to {filepath}")
        return filepath

    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do workspace."""
        active_modules = len(self.embeddings)
        total_predictions = len(self.cross_predictions)
        avg_r_squared = (
            np.mean([p.r_squared for p in self.cross_predictions])
            if self.cross_predictions
            else 0.0
        )

        return {
            "active_modules": active_modules,
            "total_cycles": self.cycle_count,
            "history_size": len(self.history),
            "total_cross_predictions": total_predictions,
            "avg_r_squared": float(avg_r_squared),
            "phi": self.compute_phi_from_integrations(),
            "module_names": self.get_all_modules(),
        }

    def __repr__(self) -> str:
        stats = self.get_statistics()
        return (
            f"SharedWorkspace(modules={stats['active_modules']}, "
            f"cycles={stats['total_cycles']}, phi={stats['phi']:.3f})"
        )
