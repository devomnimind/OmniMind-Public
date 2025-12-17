#!/usr/bin/env python3
"""
Health Check Script para Métricas de Consciência

Conforme Task 2.5.1, valida:
1. Φ dentro de range esperado (0.001-1.0 nats)
2. Todas as métricas críticas presentes
3. Nenhum módulo silent (sem dados >N minutos)
4. Detecção de anomalias simples

Output: JSON com status de cada componente

Author: OmniMind Team
Date: 2025-12-11
"""

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logger = logging.getLogger(__name__)


@dataclass
class ModuleHealth:
    """Status de saúde de um módulo."""
    
    module_name: str
    status: str  # "healthy", "warning", "critical", "silent"
    last_update: float
    age_seconds: float
    metrics_present: List[str]
    metrics_missing: List[str]
    anomalies: List[str]
    details: Dict[str, Any]


@dataclass
class SystemHealth:
    """Status de saúde geral do sistema."""
    
    status: str  # "healthy", "degraded", "critical"
    timestamp: float
    phi_status: str
    phi_value: Optional[float]
    total_modules: int
    healthy_modules: int
    warning_modules: int
    critical_modules: int
    silent_modules: int
    modules: List[ModuleHealth]
    recommendations: List[str]


class MetricsHealthChecker:
    """Verificador de saúde das métricas do sistema."""
    
    def __init__(
        self,
        phi_min: float = 0.001,
        phi_max: float = 1.0,
        silent_threshold_minutes: int = 5,
        anomaly_std_multiplier: float = 3.0
    ):
        """
        Inicializa verificador de saúde.
        
        Args:
            phi_min: Valor mínimo aceitável de Φ (nats)
            phi_max: Valor máximo aceitável de Φ (nats)
            silent_threshold_minutes: Minutos sem atualização para considerar silent
            anomaly_std_multiplier: Multiplicador de desvio padrão para anomalias
        """
        self.phi_min = phi_min
        self.phi_max = phi_max
        self.silent_threshold_seconds = silent_threshold_minutes * 60
        self.anomaly_std_multiplier = anomaly_std_multiplier
        
        # Métricas críticas esperadas por módulo
        self.expected_metrics = {
            "shared_workspace": [
                "cross_prediction_error",
                "embedding_variance",
                "convergence_rate",
                "module_count",
                "active_modules"
            ],
            "symbolic_register": [
                "message_count_per_cycle",
                "symbol_diversity",
                "narrative_coherence",
                "message_latency_ms"
            ],
            "systemic_memory": [
                "trace_length",
                "topological_distance",
                "simplicial_dimension",
                "memory_utilization_mb"
            ],
            "rhizome": [
                "flows_per_cycle",
                "average_intensity",
                "source_diversity",
                "flow_rate"
            ]
        }
    
    def check_phi_health(self, phi_value: Optional[float]) -> Tuple[str, List[str]]:
        """
        Verifica saúde do valor de Φ.
        
        Args:
            phi_value: Valor de Φ em nats
            
        Returns:
            Tupla (status, anomalies)
        """
        if phi_value is None:
            return "critical", ["Φ não disponível"]
        
        anomalies = []
        
        if phi_value < self.phi_min:
            anomalies.append(f"Φ abaixo do mínimo: {phi_value:.6f} < {self.phi_min}")
            status = "critical"
        elif phi_value > self.phi_max:
            anomalies.append(f"Φ acima do máximo: {phi_value:.6f} > {self.phi_max}")
            status = "warning"
        else:
            status = "healthy"
        
        # Verificar se está muito próximo de zero (desintegração)
        if phi_value < 0.01 and phi_value >= self.phi_min:
            anomalies.append(f"Φ muito baixo (possível desintegração): {phi_value:.6f}")
            status = "warning"
        
        return status, anomalies
    
    def check_module_health(
        self,
        module_name: str,
        metrics: Dict[str, Any],
        timestamp: float
    ) -> ModuleHealth:
        """
        Verifica saúde de um módulo específico.
        
        Args:
            module_name: Nome do módulo
            metrics: Métricas do módulo
            timestamp: Timestamp atual
            
        Returns:
            ModuleHealth com status do módulo
        """
        # Obter timestamp da última atualização
        last_update = metrics.get("timestamp", 0.0)
        age_seconds = timestamp - last_update
        
        # Verificar se está silent
        if age_seconds > self.silent_threshold_seconds:
            return ModuleHealth(
                module_name=module_name,
                status="silent",
                last_update=last_update,
                age_seconds=age_seconds,
                metrics_present=[],
                metrics_missing=self.expected_metrics.get(module_name, []),
                anomalies=[f"Sem atualizações há {age_seconds:.0f}s"],
                details={}
            )
        
        # Verificar métricas presentes/ausentes
        expected = self.expected_metrics.get(module_name, [])
        present = [m for m in expected if m in metrics]
        missing = [m for m in expected if m not in metrics]
        
        # Detectar anomalias
        anomalies = []
        details = {}
        
        for metric_name in present:
            value = metrics[metric_name]
            
            # Verificar valores inválidos (NaN, inf, negativo onde não deveria)
            if isinstance(value, (int, float)):
                if value < 0 and metric_name not in ["cross_prediction_error"]:
                    anomalies.append(f"{metric_name} negativo: {value}")
                
                import math
                if math.isnan(value):
                    anomalies.append(f"{metric_name} é NaN")
                elif math.isinf(value):
                    anomalies.append(f"{metric_name} é infinito")
                
                details[metric_name] = value
        
        # Determinar status
        if missing:
            status = "warning"
            anomalies.append(f"Métricas ausentes: {', '.join(missing)}")
        elif anomalies:
            status = "warning"
        else:
            status = "healthy"
        
        return ModuleHealth(
            module_name=module_name,
            status=status,
            last_update=last_update,
            age_seconds=age_seconds,
            metrics_present=present,
            metrics_missing=missing,
            anomalies=anomalies,
            details=details
        )
    
    def check_system_health(self, metrics_data: Dict[str, Any]) -> SystemHealth:
        """
        Verifica saúde geral do sistema.
        
        Args:
            metrics_data: Dados completos de métricas
            
        Returns:
            SystemHealth com status geral
        """
        timestamp = time.time()
        
        # Verificar Φ
        phi_value = None
        phi_status = "unknown"
        phi_anomalies = []
        
        if "phi" in metrics_data:
            phi_data = metrics_data["phi"]
            phi_value = phi_data.get("value_nats")
            phi_status, phi_anomalies = self.check_phi_health(phi_value)
        
        # Verificar módulos
        modules_health = []
        if "modules" in metrics_data:
            for module_name, module_metrics in metrics_data["modules"].items():
                health = self.check_module_health(module_name, module_metrics, timestamp)
                modules_health.append(health)
        
        # Contadores
        total_modules = len(modules_health)
        healthy_modules = len([m for m in modules_health if m.status == "healthy"])
        warning_modules = len([m for m in modules_health if m.status == "warning"])
        critical_modules = len([m for m in modules_health if m.status == "critical"])
        silent_modules = len([m for m in modules_health if m.status == "silent"])
        
        # Determinar status geral
        if critical_modules > 0 or phi_status == "critical":
            overall_status = "critical"
        elif warning_modules > 0 or phi_status == "warning":
            overall_status = "degraded"
        elif silent_modules > 0:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        # Gerar recomendações
        recommendations = []
        
        if phi_value and phi_value < 0.01:
            recommendations.append(
                "Φ muito baixo - considerar aumentar integração entre módulos"
            )
        
        if silent_modules > 0:
            silent_names = [m.module_name for m in modules_health if m.status == "silent"]
            recommendations.append(
                f"Módulos silent detectados: {', '.join(silent_names)} - "
                f"verificar se estão executando corretamente"
            )
        
        if critical_modules > 0:
            critical_names = [m.module_name for m in modules_health if m.status == "critical"]
            recommendations.append(
                f"Módulos críticos: {', '.join(critical_names)} - "
                f"requer atenção imediata"
            )
        
        # Adicionar anomalias de Φ às recomendações
        recommendations.extend(phi_anomalies)
        
        return SystemHealth(
            status=overall_status,
            timestamp=timestamp,
            phi_status=phi_status,
            phi_value=phi_value,
            total_modules=total_modules,
            healthy_modules=healthy_modules,
            warning_modules=warning_modules,
            critical_modules=critical_modules,
            silent_modules=silent_modules,
            modules=modules_health,
            recommendations=recommendations
        )
    
    def load_metrics_from_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Carrega métricas de um arquivo JSON.
        
        Args:
            filepath: Caminho do arquivo
            
        Returns:
            Dicionário de métricas
        """
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {filepath}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            return {}
    
    def save_health_report(self, health: SystemHealth, output_path: Path) -> None:
        """
        Salva relatório de saúde em JSON.
        
        Args:
            health: Status de saúde do sistema
            output_path: Caminho do arquivo de saída
        """
        # Converter para dict
        health_dict = asdict(health)
        
        # Salvar JSON
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(health_dict, f, indent=2)
        
        logger.info(f"Relatório de saúde salvo em: {output_path}")


def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description="Health Check para Métricas de Consciência OmniMind"
    )
    parser.add_argument(
        "--metrics-file",
        type=Path,
        default=Path("data/metrics/metrics_snapshot_latest.json"),
        help="Arquivo de métricas para verificar"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/metrics/health_report_latest.json"),
        help="Arquivo de saída para relatório de saúde"
    )
    parser.add_argument(
        "--phi-min",
        type=float,
        default=0.001,
        help="Valor mínimo aceitável de Φ (nats)"
    )
    parser.add_argument(
        "--phi-max",
        type=float,
        default=1.0,
        help="Valor máximo aceitável de Φ (nats)"
    )
    parser.add_argument(
        "--silent-threshold",
        type=int,
        default=5,
        help="Minutos sem atualização para considerar módulo silent"
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
    
    # Criar checker
    checker = MetricsHealthChecker(
        phi_min=args.phi_min,
        phi_max=args.phi_max,
        silent_threshold_minutes=args.silent_threshold
    )
    
    # Carregar métricas
    logger.info(f"Carregando métricas de: {args.metrics_file}")
    metrics_data = checker.load_metrics_from_file(args.metrics_file)
    
    if not metrics_data:
        logger.error("Nenhuma métrica carregada - impossível realizar health check")
        sys.exit(1)
    
    # Realizar health check
    logger.info("Realizando health check...")
    health = checker.check_system_health(metrics_data)
    
    # Salvar relatório
    checker.save_health_report(health, args.output)
    
    # Imprimir resumo
    print("\n" + "="*60)
    print("HEALTH CHECK REPORT")
    print("="*60)
    print(f"Status Geral: {health.status.upper()}")
    print(f"Φ: {health.phi_value:.6f} nats ({health.phi_status})" if health.phi_value else "Φ: N/A")
    print(f"Módulos: {health.total_modules} total, "
          f"{health.healthy_modules} healthy, "
          f"{health.warning_modules} warning, "
          f"{health.critical_modules} critical, "
          f"{health.silent_modules} silent")
    
    if health.recommendations:
        print("\nRecomendações:")
        for i, rec in enumerate(health.recommendations, 1):
            print(f"  {i}. {rec}")
    
    print("\nDetalhes dos Módulos:")
    for module in health.modules:
        status_icon = {
            "healthy": "✓",
            "warning": "⚠",
            "critical": "✗",
            "silent": "○"
        }.get(module.status, "?")
        
        print(f"  {status_icon} {module.module_name}: {module.status}")
        if module.anomalies:
            for anomaly in module.anomalies:
                print(f"      - {anomaly}")
    
    print("="*60)
    
    # Exit code baseado no status
    exit_code = {
        "healthy": 0,
        "degraded": 1,
        "critical": 2
    }.get(health.status, 3)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
