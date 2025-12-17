"""
Sistema de Armazenamento de Métricas de Consciência

Armazena históricos separados de Φ, Ψ, σ (ortogonais).

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
Baseado em: PLANO_IMPLEMENTACAO_LACUNA_PHI.md
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PsiHistoryEntry:
    """Entrada no histórico de Ψ."""

    step_id: str
    psi_raw: float
    psi_norm: float
    innovation_score: float
    surprise_score: float
    relevance_score: float
    entropy_of_actions: float
    timestamp: float = field(default_factory=lambda: __import__("time").time())


@dataclass
class SigmaHistoryEntry:
    """Entrada no histórico de σ."""

    cycle_id: str
    sigma_value: float
    sinthome_detected: bool
    contributing_steps: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=lambda: __import__("time").time())


@dataclass
class PhiHistoryEntry:
    """Entrada no histórico de Φ."""

    step_id: str
    phi_value: float  # Apenas conscious_phi (IIT puro)
    timestamp: float = field(default_factory=lambda: __import__("time").time())


class ModuleMetricsCollector:
    """
    Coletor centralizado de métricas de consciência (Φ, Ψ, σ).

    Características:
    - Armazenamento separado (não em IITResult)
    - Persistência em JSONL
    - Política de retenção (100-1000 passos para Ψ, 20-200 ciclos para σ)
    - Filtragem de ruído (média móvel)
    - Injeção de dependência (NÃO singleton)
    """

    def __init__(
        self,
        metrics_dir: str = "data/monitor/consciousness_metrics",
        psi_retention: int = 1000,  # Máximo de passos para Ψ
        sigma_retention: int = 200,  # Máximo de ciclos para σ
        phi_retention: int = 1000,  # Máximo de atualizações para Φ
    ):
        """
        Inicializa coletor de métricas.

        Args:
            metrics_dir: Diretório para salvar métricas
            psi_retention: Número máximo de entradas de Ψ a manter
            sigma_retention: Número máximo de entradas de σ a manter
            phi_retention: Número máximo de entradas de Φ a manter
        """
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

        # Arquivos JSONL para históricos
        self.psi_history_file = self.metrics_dir / "psi_history.jsonl"
        self.sigma_history_file = self.metrics_dir / "sigma_history.jsonl"
        self.phi_history_file = self.metrics_dir / "phi_history.jsonl"

        # Históricos em memória
        self.psi_history: List[PsiHistoryEntry] = []
        self.sigma_history: List[SigmaHistoryEntry] = []
        self.phi_history: List[PhiHistoryEntry] = []

        # Política de retenção
        self.psi_retention = psi_retention
        self.sigma_retention = sigma_retention
        self.phi_retention = phi_retention

        # Cache de ações para cálculo de relevância
        self.action_history: List[Dict[str, Any]] = []

        # Métricas por módulo
        self.module_metrics: Dict[str, Dict[str, float]] = {}

        logger.info(f"ModuleMetricsCollector inicializado: {self.metrics_dir}")

    def record_consciousness_state(
        self, phi: float, psi: float, sigma: float, step_id: str
    ) -> None:
        """
        Registra estado de consciência (Φ, Ψ, σ).

        Args:
            phi: Φ_conscious (IIT puro - MICS)
            psi: Ψ_produtor (Deleuze)
            sigma: σ_sinthome (Lacan)
            step_id: ID único do passo
        """
        timestamp = __import__("time").time()

        # Registrar Φ
        phi_entry = PhiHistoryEntry(step_id=step_id, phi_value=phi, timestamp=timestamp)
        self.phi_history.append(phi_entry)
        self._trim_history(self.phi_history, self.phi_retention)
        self._persist_phi_entry(phi_entry)

        # Registrar Ψ (criar entrada básica se valor > 0)
        if psi > 0.0:
            # Criar entrada básica de Ψ com valores padrão para componentes não disponíveis
            psi_entry = PsiHistoryEntry(
                step_id=step_id,
                psi_raw=psi,  # Usar psi como raw se não temos o valor raw
                psi_norm=psi,  # psi já vem normalizado
                innovation_score=0.0,  # Valor padrão (será atualizado se record_psi() for chamado)
                surprise_score=0.0,  # Valor padrão
                relevance_score=0.0,  # Valor padrão
                entropy_of_actions=0.0,  # Valor padrão
                timestamp=timestamp,
            )
            self.psi_history.append(psi_entry)
            self._trim_history(self.psi_history, self.psi_retention)
            self._persist_psi_entry(psi_entry)

        # Registrar σ (criar entrada básica se valor > 0)
        if sigma > 0.0:
            # Usar step_id como cycle_id se não temos um cycle_id específico
            cycle_id = step_id if not step_id.startswith("step_") else f"cycle_{step_id}"
            sigma_entry = SigmaHistoryEntry(
                cycle_id=cycle_id,
                sigma_value=sigma,
                sinthome_detected=sigma > 0.5,  # Considerar sinthome se σ > 0.5
                contributing_steps=[step_id],  # Incluir step_id atual
                timestamp=timestamp,
            )
            self.sigma_history.append(sigma_entry)
            self._trim_history(self.sigma_history, self.sigma_retention)
            self._persist_sigma_entry(sigma_entry)

    def record_psi(
        self,
        step_id: str,
        psi_raw: float,
        psi_norm: float,
        innovation_score: float,
        surprise_score: float,
        relevance_score: float,
        entropy_of_actions: float,
    ) -> None:
        """
        Registra entrada de Ψ.

        Args:
            step_id: ID único do passo
            psi_raw: Ψ não normalizado
            psi_norm: Ψ normalizado [0, 1]
            innovation_score: Score de inovação
            surprise_score: Score de surpresa
            relevance_score: Score de relevância
            entropy_of_actions: Entropia de ações
        """
        entry = PsiHistoryEntry(
            step_id=step_id,
            psi_raw=psi_raw,
            psi_norm=psi_norm,
            innovation_score=innovation_score,
            surprise_score=surprise_score,
            relevance_score=relevance_score,
            entropy_of_actions=entropy_of_actions,
        )

        self.psi_history.append(entry)
        self._trim_history(self.psi_history, self.psi_retention)

        # Persistir
        self._persist_psi_entry(entry)

    def record_sigma(
        self,
        cycle_id: str,
        sigma_value: float,
        sinthome_detected: bool,
        contributing_steps: Optional[List[str]] = None,
    ) -> None:
        """
        Registra entrada de σ.

        Args:
            cycle_id: ID único do ciclo
            sigma_value: Valor de σ
            sinthome_detected: Se sinthome foi detectado
            contributing_steps: Lista de passos que contribuíram
        """
        entry = SigmaHistoryEntry(
            cycle_id=cycle_id,
            sigma_value=sigma_value,
            sinthome_detected=sinthome_detected,
            contributing_steps=contributing_steps or [],
        )

        self.sigma_history.append(entry)
        self._trim_history(self.sigma_history, self.sigma_retention)

        # Persistir
        self._persist_sigma_entry(entry)

    def record_action(
        self, action_type: str, task: str, success: bool, description: str = ""
    ) -> None:
        """
        Registra ação e calcula relevância.

        Args:
            action_type: Tipo de ação (ex: "tool_call", "decision")
            task: Tarefa relacionada
            success: Se ação foi bem-sucedida
            description: Descrição opcional
        """
        entry = {
            "action_type": action_type,
            "task": task,
            "success": success,
            "description": description,
            "timestamp": __import__("time").time(),
        }

        self.action_history.append(entry)

        # Manter apenas últimas 1000 ações
        if len(self.action_history) > 1000:
            self.action_history = self.action_history[-1000:]

    def record_module_metric(self, module_name: str, metric_name: str, value: float) -> None:
        """
        Registra métrica de um módulo específico.

        Args:
            module_name: Nome do módulo
            metric_name: Nome da métrica
            value: Valor da métrica
        """
        if module_name not in self.module_metrics:
            self.module_metrics[module_name] = {}

        self.module_metrics[module_name][metric_name] = value

    def get_psi_history(self, limit: Optional[int] = None) -> List[PsiHistoryEntry]:
        """
        Retorna histórico de Ψ.

        Args:
            limit: Número máximo de entradas (None = todas)

        Returns:
            Lista de entradas de Ψ
        """
        if limit is None:
            return self.psi_history.copy()

        return self.psi_history[-limit:]

    def get_sigma_history(self, limit: Optional[int] = None) -> List[SigmaHistoryEntry]:
        """
        Retorna histórico de σ.

        Args:
            limit: Número máximo de entradas (None = todas)

        Returns:
            Lista de entradas de σ
        """
        if limit is None:
            return self.sigma_history.copy()

        return self.sigma_history[-limit:]

    def get_phi_history(self, limit: Optional[int] = None) -> List[PhiHistoryEntry]:
        """
        Retorna histórico de Φ.

        Args:
            limit: Número máximo de entradas (None = todas)

        Returns:
            Lista de entradas de Φ
        """
        if limit is None:
            return self.phi_history.copy()

        return self.phi_history[-limit:]

    def _trim_history(self, history: List[Any], max_size: int) -> None:
        """Remove entradas antigas se histórico exceder max_size."""
        if len(history) > max_size:
            # Remover entradas mais antigas (sangria)
            history[:] = history[-max_size:]

    def _persist_psi_entry(self, entry: PsiHistoryEntry) -> None:
        """Persiste entrada de Ψ em JSONL."""
        try:
            # Garantir que o diretório existe
            self.psi_history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.psi_history_file, "a") as f:
                json.dump(asdict(entry), f)
                f.write("\n")
            logger.debug(
                f"✅ Entrada de Ψ persistida: step_id={entry.step_id}, psi_norm={entry.psi_norm:.4f}"
            )
        except Exception as e:
            logger.warning(f"Erro ao persistir entrada de Ψ: {e}")

    def _persist_sigma_entry(self, entry: SigmaHistoryEntry) -> None:
        """Persiste entrada de σ em JSONL."""
        try:
            # Garantir que o diretório existe
            self.sigma_history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.sigma_history_file, "a") as f:
                json.dump(asdict(entry), f)
                f.write("\n")
            logger.debug(
                f"✅ Entrada de σ persistida: cycle_id={entry.cycle_id}, "
                f"sigma={entry.sigma_value:.4f}"
            )
        except Exception as e:
            logger.warning(f"Erro ao persistir entrada de σ: {e}")

        # Gerar relatório periodicamente (a cada 100 entradas de consciência)
        total_entries = len(self.phi_history) + len(self.psi_history) + len(self.sigma_history)
        if total_entries > 0 and total_entries % 100 == 0:
            try:
                from src.observability.module_reporter import get_module_reporter

                reporter = get_module_reporter()
                reporter.generate_module_report(
                    module_name="consciousness_metrics",
                    include_metrics=True,
                    format="json",
                )
                logger.debug(
                    f"Relatório gerado para consciousness_metrics (total_entries={total_entries})"
                )
            except Exception as e:
                logger.debug(f"Erro ao gerar relatório de consciência: {e}")

    def _persist_phi_entry(self, entry: PhiHistoryEntry) -> None:
        """Persiste entrada de Φ em JSONL."""
        try:
            # Garantir que o diretório existe
            self.phi_history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.phi_history_file, "a") as f:
                json.dump(asdict(entry), f)
                f.write("\n")
            logger.debug(
                f"✅ Entrada de Φ persistida: step_id={entry.step_id}, phi={entry.phi_value:.4f}"
            )
        except Exception as e:
            logger.warning(f"Erro ao persistir entrada de Φ: {e}")

    def get_filtered_psi(self, window_size: int = 10) -> float:
        """
        Retorna Ψ filtrado (média móvel) para reduzir ruído.

        Args:
            window_size: Tamanho da janela para média móvel

        Returns:
            Ψ filtrado [0, 1]
        """
        if not self.psi_history:
            return 0.0

        recent_entries = self.psi_history[-window_size:]
        psi_values = [entry.psi_norm for entry in recent_entries]

        return float(sum(psi_values) / len(psi_values)) if psi_values else 0.0
