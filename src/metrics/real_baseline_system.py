"""
Real Baseline Comparison System - Comparação com baselines reais.

Substitui comparações hardcoded por análise real baseada em:
- Histórico de métricas coletado
- Estatísticas de referência
- Tendências de longo prazo

Author: This work was conceived by Fabrício da Silva and implemented with AI assistance
from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code review
and debugging across various models including Gemini and Perplexity AI, under
theoretical coordination by the author.
Date: November 2025
"""

from __future__ import annotations

import json
import logging
import statistics
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class BaselineStats:
    """Estatísticas de baseline para uma métrica."""

    mean: float
    std_dev: float
    min_value: float
    max_value: float
    sample_count: int
    last_updated: datetime


@dataclass
class BaselineComparison:
    """Comparação de uma métrica com seu baseline."""

    metric_name: str
    current_value: float
    baseline_value: float
    change: float  # Percentual de mudança
    change_type: str  # "improvement", "degradation", "stable"
    significance: str  # "high", "moderate", "low"


class RealBaselineSystem:
    """Sistema de baseline real baseado em dados históricos."""

    def __init__(self):
        self.baselines: Dict[str, BaselineStats] = {}
        self.baseline_file = Path("data/metrics/baselines.json")
        self.history_file = Path("data/metrics/history.jsonl")

        # Garante que os diretórios existem
        self.baseline_file.parent.mkdir(parents=True, exist_ok=True)
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        # Carrega baselines existentes
        self._load_baselines()

        logger.info("RealBaselineSystem initialized")

    def _load_baselines(self) -> None:
        """Carrega baselines do arquivo."""
        if not self.baseline_file.exists():
            return

        try:
            with open(self.baseline_file, "r") as f:
                data = json.load(f)

            for metric_name, stats_data in data.items():
                stats_data["last_updated"] = datetime.fromisoformat(stats_data["last_updated"])
                self.baselines[metric_name] = BaselineStats(**stats_data)

            logger.info(f"Loaded baselines for {len(self.baselines)} metrics")

        except Exception as e:
            logger.error(f"Error loading baselines: {e}")

    def _save_baselines(self) -> None:
        """Salva baselines no arquivo."""
        try:
            data = {}
            for metric_name, stats in self.baselines.items():
                data[metric_name] = {
                    "mean": stats.mean,
                    "std_dev": stats.std_dev,
                    "min_value": stats.min_value,
                    "max_value": stats.max_value,
                    "sample_count": stats.sample_count,
                    "last_updated": stats.last_updated.isoformat(),
                }

            with open(self.baseline_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Error saving baselines: {e}")

    def record_metric(self, metric_name: str, value: float) -> None:
        """Registra uma nova medição para cálculo de baseline."""
        # Salva no histórico
        self._save_to_history(metric_name, value)

        # Atualiza baseline se necessário
        self._update_baseline(metric_name, value)

    def _save_to_history(self, metric_name: str, value: float) -> None:
        """Salva medição no histórico."""
        try:
            entry = {"timestamp": datetime.now().isoformat(), "metric": metric_name, "value": value}

            with open(self.history_file, "a") as f:
                json.dump(entry, f)
                f.write("\n")

        except Exception as e:
            logger.error(f"Error saving to history: {e}")

    def _update_baseline(self, metric_name: str, new_value: float) -> None:
        """Atualiza baseline para uma métrica."""
        # Carrega histórico recente (últimos 30 dias)
        history = self._load_metric_history(metric_name, days=30)

        if len(history) < 10:  # Precisa de pelo menos 10 amostras
            return

        # Calcula estatísticas
        values = [entry["value"] for entry in history]

        try:
            mean = statistics.mean(values)
            std_dev = statistics.stdev(values) if len(values) > 1 else 0.0
            min_value = min(values)
            max_value = max(values)

            self.baselines[metric_name] = BaselineStats(
                mean=mean,
                std_dev=std_dev,
                min_value=min_value,
                max_value=max_value,
                sample_count=len(values),
                last_updated=datetime.now(),
            )

            # Salva baselines atualizadas
            self._save_baselines()

        except Exception as e:
            logger.error(f"Error updating baseline for {metric_name}: {e}")

    def _load_metric_history(self, metric_name: str, days: int = 30) -> List[Dict[str, Any]]:
        """Carrega histórico de uma métrica."""
        history = []

        if not self.history_file.exists():
            return history

        cutoff_time = datetime.now() - timedelta(days=days)

        try:
            with open(self.history_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entry = json.loads(line)
                        entry_time = datetime.fromisoformat(entry["timestamp"])

                        if entry["metric"] == metric_name and entry_time > cutoff_time:
                            history.append(entry)

        except Exception as e:
            logger.error(f"Error loading metric history: {e}")

        return history

    def compare_with_baseline(self, metric_name: str, current_value: float) -> BaselineComparison:
        """Compara valor atual com baseline."""

        if metric_name not in self.baselines:
            # Sem baseline, retorna comparação neutra
            return BaselineComparison(
                metric_name=metric_name,
                current_value=current_value,
                baseline_value=current_value,  # Usa valor atual como baseline
                change=0.0,
                change_type="stable",
                significance="low",
            )

        baseline = self.baselines[metric_name]

        # Calcula mudança percentual
        if baseline.mean != 0:
            change = ((current_value - baseline.mean) / abs(baseline.mean)) * 100
        else:
            change = 0.0

        # Determina tipo de mudança
        if abs(change) < 5:
            change_type = "stable"
        elif change > 0:
            change_type = "improvement"
        else:
            change_type = "degradation"

        # Determina significância baseada no desvio padrão
        if baseline.std_dev > 0:
            z_score = abs(current_value - baseline.mean) / baseline.std_dev
            if z_score > 2.0:
                significance = "high"
            elif z_score > 1.0:
                significance = "moderate"
            else:
                significance = "low"
        else:
            significance = "low"

        return BaselineComparison(
            metric_name=metric_name,
            current_value=current_value,
            baseline_value=baseline.mean,
            change=change,
            change_type=change_type,
            significance=significance,
        )

    def get_all_baseline_comparisons(
        self, current_metrics: Dict[str, float]
    ) -> Dict[str, Dict[str, Any]]:
        """Retorna comparações de baseline para todas as métricas."""

        comparisons = {}

        for metric_name, current_value in current_metrics.items():
            comparison = self.compare_with_baseline(metric_name, current_value)

            comparisons[metric_name] = {
                "current": comparison.current_value,
                "baseline": comparison.baseline_value,
                "change": comparison.change,
                "change_type": comparison.change_type,
                "significance": comparison.significance,
            }

        return comparisons

    def get_baseline_stats(self, metric_name: str) -> Optional[Dict[str, Any]]:
        """Retorna estatísticas de baseline para uma métrica."""

        if metric_name not in self.baselines:
            return None

        baseline = self.baselines[metric_name]

        return {
            "mean": baseline.mean,
            "std_dev": baseline.std_dev,
            "min_value": baseline.min_value,
            "max_value": baseline.max_value,
            "sample_count": baseline.sample_count,
            "last_updated": baseline.last_updated.isoformat(),
        }

    def reset_baseline(self, metric_name: str) -> None:
        """Reseta baseline para uma métrica."""
        if metric_name in self.baselines:
            del self.baselines[metric_name]
            self._save_baselines()
            logger.info(f"Reset baseline for {metric_name}")


# Instância global do sistema de baseline
real_baseline_system = RealBaselineSystem()


def compare_with_baselines(current_metrics: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
    """
    Função wrapper para comparar métricas atuais com baselines.

    Args:
        current_metrics: Dicionário com métricas atuais

    Returns:
        Dicionário com comparações de baseline
    """
    return real_baseline_system.get_all_baseline_comparisons(current_metrics)
