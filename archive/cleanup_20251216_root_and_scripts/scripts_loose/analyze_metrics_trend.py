#!/usr/bin/env python3
"""
Análise de Tendências de Métricas

Conforme Task 2.5.2, analisa:
1. Φ crescendo ou caindo?
2. Ciclos ficando mais rápidos?
3. Componentes sintetizados aumentando?
4. Padrões periódicos?

Output: Recomendações automáticas

Author: OmniMind Team
Date: 2025-12-11
"""

import argparse
import json
import logging
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logger = logging.getLogger(__name__)


@dataclass
class TrendAnalysis:
    """Análise de tendência de uma métrica."""
    
    metric_name: str
    trend: str  # "increasing", "decreasing", "stable", "insufficient_data"
    slope: float  # Inclinação da linha de tendência
    r_squared: float  # R² do ajuste linear
    mean_value: float
    std_value: float
    min_value: float
    max_value: float
    data_points: int
    confidence: str  # "high", "medium", "low"


@dataclass
class PeriodicityAnalysis:
    """Análise de periodicidade de uma métrica."""
    
    metric_name: str
    has_periodicity: bool
    period_estimate: Optional[float]  # Em ciclos/segundos
    confidence: str  # "high", "medium", "low"
    details: Dict[str, Any]


@dataclass
class SystemTrendReport:
    """Relatório completo de tendências do sistema."""
    
    timestamp: float
    timespan_minutes: float
    total_cycles_analyzed: int
    
    # Análises de Φ
    phi_trend: Optional[TrendAnalysis]
    phi_increasing: bool
    phi_stable: bool
    
    # Análises de performance
    cycle_time_trend: Optional[TrendAnalysis]
    cycles_getting_faster: bool
    
    # Análises de componentes
    modules_trend: Optional[TrendAnalysis]
    components_increasing: bool
    
    # Periodicidade
    periodic_patterns: List[PeriodicityAnalysis]
    
    # Recomendações
    recommendations: List[str]
    warnings: List[str]


class MetricsTrendAnalyzer:
    """Analisador de tendências de métricas."""
    
    def __init__(
        self,
        min_data_points: int = 10,
        stability_threshold: float = 0.05,
        confidence_r_squared_high: float = 0.7,
        confidence_r_squared_medium: float = 0.4
    ):
        """
        Inicializa analisador de tendências.
        
        Args:
            min_data_points: Mínimo de pontos para análise
            stability_threshold: Threshold para considerar métrica estável (slope relativo)
            confidence_r_squared_high: R² mínimo para confiança alta
            confidence_r_squared_medium: R² mínimo para confiança média
        """
        self.min_data_points = min_data_points
        self.stability_threshold = stability_threshold
        self.confidence_r_squared_high = confidence_r_squared_high
        self.confidence_r_squared_medium = confidence_r_squared_medium
    
    def analyze_trend(
        self,
        metric_name: str,
        values: List[float],
        timestamps: Optional[List[float]] = None
    ) -> TrendAnalysis:
        """
        Analisa tendência de uma métrica.
        
        Args:
            metric_name: Nome da métrica
            values: Lista de valores
            timestamps: Lista opcional de timestamps
            
        Returns:
            TrendAnalysis com resultado
        """
        if len(values) < self.min_data_points:
            return TrendAnalysis(
                metric_name=metric_name,
                trend="insufficient_data",
                slope=0.0,
                r_squared=0.0,
                mean_value=np.mean(values) if values else 0.0,
                std_value=np.std(values) if values else 0.0,
                min_value=min(values) if values else 0.0,
                max_value=max(values) if values else 0.0,
                data_points=len(values),
                confidence="low"
            )
        
        # Converter para numpy
        values_np = np.array(values)
        
        # Usar índices como x se timestamps não fornecidos
        if timestamps is None:
            x = np.arange(len(values))
        else:
            # Normalizar timestamps para começar de 0
            timestamps_np = np.array(timestamps)
            x = timestamps_np - timestamps_np[0]
        
        # Regressão linear
        coeffs = np.polyfit(x, values_np, 1)
        slope, intercept = coeffs
        
        # Calcular R²
        y_pred = slope * x + intercept
        ss_res = np.sum((values_np - y_pred) ** 2)
        ss_tot = np.sum((values_np - np.mean(values_np)) ** 2)
        r_squared = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        # Calcular estatísticas
        mean_val = float(np.mean(values_np))
        std_val = float(np.std(values_np))
        min_val = float(np.min(values_np))
        max_val = float(np.max(values_np))
        
        # Determinar tendência
        # Normalizar slope pelo valor médio para ter uma medida relativa
        relative_slope = abs(slope) / mean_val if mean_val != 0 else abs(slope)
        
        if relative_slope < self.stability_threshold:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        # Determinar confiança
        if r_squared >= self.confidence_r_squared_high:
            confidence = "high"
        elif r_squared >= self.confidence_r_squared_medium:
            confidence = "medium"
        else:
            confidence = "low"
        
        return TrendAnalysis(
            metric_name=metric_name,
            trend=trend,
            slope=float(slope),
            r_squared=float(r_squared),
            mean_value=mean_val,
            std_value=std_val,
            min_value=min_val,
            max_value=max_val,
            data_points=len(values),
            confidence=confidence
        )
    
    def detect_periodicity(
        self,
        metric_name: str,
        values: List[float],
        timestamps: Optional[List[float]] = None
    ) -> PeriodicityAnalysis:
        """
        Detecta periodicidade em uma métrica usando FFT.
        
        Args:
            metric_name: Nome da métrica
            values: Lista de valores
            timestamps: Lista opcional de timestamps
            
        Returns:
            PeriodicityAnalysis com resultado
        """
        if len(values) < self.min_data_points:
            return PeriodicityAnalysis(
                metric_name=metric_name,
                has_periodicity=False,
                period_estimate=None,
                confidence="low",
                details={"reason": "insufficient_data"}
            )
        
        # Converter para numpy e remover média (detrend simples)
        values_np = np.array(values)
        values_detrended = values_np - np.mean(values_np)
        
        # FFT
        fft = np.fft.fft(values_detrended)
        freqs = np.fft.fftfreq(len(values_detrended))
        
        # Magnitude (apenas metade positiva)
        magnitude = np.abs(fft[:len(fft)//2])
        freqs_positive = freqs[:len(freqs)//2]
        
        # Encontrar pico dominante (excluindo DC component)
        if len(magnitude) > 1:
            dominant_idx = np.argmax(magnitude[1:]) + 1  # +1 para compensar slice
            dominant_freq = freqs_positive[dominant_idx]
            dominant_magnitude = magnitude[dominant_idx]
            
            # Calcular período (em unidades de x)
            if abs(dominant_freq) > 1e-6:
                period_estimate = 1.0 / abs(dominant_freq)
            else:
                period_estimate = None
            
            # Determinar se há periodicidade significativa
            # Comparar magnitude do pico com magnitude média
            mean_magnitude = np.mean(magnitude[1:])
            
            if dominant_magnitude > mean_magnitude * 3:  # Pico >3x a média
                has_periodicity = True
                confidence = "high" if dominant_magnitude > mean_magnitude * 5 else "medium"
            else:
                has_periodicity = False
                confidence = "low"
            
            details = {
                "dominant_frequency": float(dominant_freq),
                "dominant_magnitude": float(dominant_magnitude),
                "mean_magnitude": float(mean_magnitude),
                "magnitude_ratio": float(dominant_magnitude / mean_magnitude) if mean_magnitude > 0 else 0.0
            }
        else:
            has_periodicity = False
            period_estimate = None
            confidence = "low"
            details = {"reason": "insufficient_frequency_bins"}
        
        return PeriodicityAnalysis(
            metric_name=metric_name,
            has_periodicity=has_periodicity,
            period_estimate=period_estimate,
            confidence=confidence,
            details=details
        )
    
    def analyze_metrics_history(
        self,
        metrics_history: List[Dict[str, Any]]
    ) -> SystemTrendReport:
        """
        Analisa histórico completo de métricas.
        
        Args:
            metrics_history: Lista de snapshots de métricas
            
        Returns:
            SystemTrendReport com análises completas
        """
        import time
        
        # Extrair séries temporais
        phi_values = []
        phi_timestamps = []
        module_counts = []
        cycle_numbers = []
        
        for snapshot in metrics_history:
            timestamp = snapshot.get("timestamp", 0.0)
            
            # Φ
            if "phi" in snapshot:
                phi_data = snapshot["phi"]
                phi_value = phi_data.get("value_nats")
                if phi_value is not None:
                    phi_values.append(phi_value)
                    phi_timestamps.append(timestamp)
            
            # Ciclos e módulos
            cycle = snapshot.get("cycle", 0)
            cycle_numbers.append(cycle)
            
            if "modules" in snapshot and "shared_workspace" in snapshot["modules"]:
                ws_metrics = snapshot["modules"]["shared_workspace"]
                module_count = ws_metrics.get("module_count", 0)
                module_counts.append(module_count)
        
        # Analisar Φ
        phi_trend = None
        phi_increasing = False
        phi_stable = False
        
        if phi_values:
            phi_trend = self.analyze_trend("phi", phi_values, phi_timestamps)
            phi_increasing = phi_trend.trend == "increasing"
            phi_stable = phi_trend.trend == "stable"
        
        # Analisar tempo de ciclo (se timestamps disponíveis)
        cycle_time_trend = None
        cycles_getting_faster = False
        
        if len(phi_timestamps) >= 2:
            # Calcular intervalos entre ciclos
            cycle_times = [phi_timestamps[i] - phi_timestamps[i-1] 
                          for i in range(1, len(phi_timestamps))]
            if cycle_times:
                cycle_time_trend = self.analyze_trend("cycle_time", cycle_times)
                # Ciclos ficando mais rápidos = tempo diminuindo
                cycles_getting_faster = cycle_time_trend.trend == "decreasing"
        
        # Analisar módulos
        modules_trend = None
        components_increasing = False
        
        if module_counts:
            modules_trend = self.analyze_trend("module_count", module_counts)
            components_increasing = modules_trend.trend == "increasing"
        
        # Detectar periodicidade
        periodic_patterns = []
        
        if phi_values:
            phi_periodicity = self.detect_periodicity("phi", phi_values, phi_timestamps)
            if phi_periodicity.has_periodicity:
                periodic_patterns.append(phi_periodicity)
        
        if module_counts:
            modules_periodicity = self.detect_periodicity("module_count", module_counts)
            if modules_periodicity.has_periodicity:
                periodic_patterns.append(modules_periodicity)
        
        # Calcular timespan
        if phi_timestamps:
            timespan_seconds = phi_timestamps[-1] - phi_timestamps[0]
            timespan_minutes = timespan_seconds / 60.0
        else:
            timespan_minutes = 0.0
        
        # Gerar recomendações
        recommendations = []
        warnings = []
        
        if phi_trend:
            if phi_trend.trend == "decreasing" and phi_trend.confidence in ["high", "medium"]:
                warnings.append(
                    f"⚠️ Φ em declínio (slope={phi_trend.slope:.6f}, R²={phi_trend.r_squared:.2f}) - "
                    f"sistema pode estar desintegrando"
                )
                recommendations.append(
                    "Considerar aumentar integração entre módulos ou revisar parâmetros de Langevin"
                )
            elif phi_trend.trend == "increasing" and phi_trend.confidence in ["high", "medium"]:
                recommendations.append(
                    f"✓ Φ crescendo (slope={phi_trend.slope:.6f}, R²={phi_trend.r_squared:.2f}) - "
                    f"sistema integrando bem"
                )
            elif phi_trend.trend == "stable":
                recommendations.append(
                    f"✓ Φ estável (mean={phi_trend.mean_value:.4f}, std={phi_trend.std_value:.4f}) - "
                    f"sistema em equilíbrio"
                )
        
        if cycle_time_trend:
            if cycles_getting_faster:
                recommendations.append(
                    f"✓ Ciclos ficando mais rápidos (tempo médio diminuindo) - "
                    f"otimização em andamento"
                )
            elif cycle_time_trend.trend == "increasing":
                warnings.append(
                    f"⚠️ Ciclos ficando mais lentos - verificar gargalos de performance"
                )
        
        if components_increasing:
            recommendations.append(
                f"✓ Número de módulos aumentando - sistema expandindo capacidades"
            )
        
        for periodicity in periodic_patterns:
            if periodicity.confidence in ["high", "medium"]:
                recommendations.append(
                    f"🔄 Padrão periódico detectado em {periodicity.metric_name}: "
                    f"período ~{periodicity.period_estimate:.1f} ciclos"
                )
        
        return SystemTrendReport(
            timestamp=time.time(),
            timespan_minutes=timespan_minutes,
            total_cycles_analyzed=len(metrics_history),
            phi_trend=phi_trend,
            phi_increasing=phi_increasing,
            phi_stable=phi_stable,
            cycle_time_trend=cycle_time_trend,
            cycles_getting_faster=cycles_getting_faster,
            modules_trend=modules_trend,
            components_increasing=components_increasing,
            periodic_patterns=periodic_patterns,
            recommendations=recommendations,
            warnings=warnings
        )
    
    def load_metrics_history(self, filepath: Path) -> List[Dict[str, Any]]:
        """
        Carrega histórico de métricas de arquivo JSONL.
        
        Args:
            filepath: Caminho do arquivo JSONL
            
        Returns:
            Lista de snapshots de métricas
        """
        metrics_history = []
        
        try:
            with open(filepath, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            snapshot = json.loads(line)
                            metrics_history.append(snapshot)
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {filepath}")
        
        return metrics_history
    
    def save_trend_report(self, report: SystemTrendReport, output_path: Path) -> None:
        """
        Salva relatório de tendências em JSON.
        
        Args:
            report: Relatório de tendências
            output_path: Caminho do arquivo de saída
        """
        # Converter para dict
        report_dict = asdict(report)
        
        # Salvar JSON
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(report_dict, f, indent=2)
        
        logger.info(f"Relatório de tendências salvo em: {output_path}")


def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description="Análise de Tendências de Métricas OmniMind"
    )
    parser.add_argument(
        "--metrics-file",
        type=Path,
        default=Path("data/metrics/metrics.jsonl"),
        help="Arquivo JSONL com histórico de métricas"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/metrics/trend_report_latest.json"),
        help="Arquivo de saída para relatório de tendências"
    )
    parser.add_argument(
        "--min-points",
        type=int,
        default=10,
        help="Mínimo de pontos de dados para análise"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Modo verbose (log detalhado)"
    )
    
    args = parser.parse_args()
    
    # Configurar logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Criar analyzer
    analyzer = MetricsTrendAnalyzer(min_data_points=args.min_points)
    
    # Carregar histórico de métricas
    logger.info(f"Carregando histórico de métricas de: {args.metrics_file}")
    metrics_history = analyzer.load_metrics_history(args.metrics_file)
    
    if not metrics_history:
        logger.error("Nenhum histórico de métricas carregado - impossível realizar análise")
        sys.exit(1)
    
    logger.info(f"Carregados {len(metrics_history)} snapshots de métricas")
    
    # Realizar análise de tendências
    logger.info("Analisando tendências...")
    report = analyzer.analyze_metrics_history(metrics_history)
    
    # Salvar relatório
    analyzer.save_trend_report(report, args.output)
    
    # Imprimir resumo
    print("\n" + "="*60)
    print("TREND ANALYSIS REPORT")
    print("="*60)
    print(f"Período Analisado: {report.timespan_minutes:.1f} minutos")
    print(f"Ciclos Analisados: {report.total_cycles_analyzed}")
    
    if report.phi_trend:
        print(f"\nΦ (Phi):")
        print(f"  Tendência: {report.phi_trend.trend}")
        print(f"  Média: {report.phi_trend.mean_value:.6f} nats")
        print(f"  Desvio Padrão: {report.phi_trend.std_value:.6f}")
        print(f"  Slope: {report.phi_trend.slope:.6f}")
        print(f"  R²: {report.phi_trend.r_squared:.3f}")
        print(f"  Confiança: {report.phi_trend.confidence}")
    
    if report.cycle_time_trend:
        print(f"\nTempo de Ciclo:")
        print(f"  Tendência: {report.cycle_time_trend.trend}")
        print(f"  Média: {report.cycle_time_trend.mean_value:.3f}s")
    
    if report.modules_trend:
        print(f"\nMódulos Ativos:")
        print(f"  Tendência: {report.modules_trend.trend}")
        print(f"  Média: {report.modules_trend.mean_value:.1f}")
    
    if report.periodic_patterns:
        print(f"\nPadrões Periódicos Detectados:")
        for pattern in report.periodic_patterns:
            print(f"  - {pattern.metric_name}: "
                  f"período ~{pattern.period_estimate:.1f} ciclos "
                  f"(confiança: {pattern.confidence})")
    
    if report.warnings:
        print(f"\n⚠️ AVISOS:")
        for warning in report.warnings:
            print(f"  {warning}")
    
    if report.recommendations:
        print(f"\n📋 RECOMENDAÇÕES:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")
    
    print("="*60)
    
    # Exit code: 0 se sem warnings, 1 se há warnings
    sys.exit(1 if report.warnings else 0)


if __name__ == "__main__":
    main()
