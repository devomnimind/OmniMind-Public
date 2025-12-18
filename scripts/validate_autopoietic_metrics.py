#!/usr/bin/env python3
"""
Script de Validação de Métricas Autopoiéticas

Verifica que AutopoieticManager está capturando todas as métricas necessárias
e compara com o padrão do integration_loop.

Sprint 2 - Task 2.1.2

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-11
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Set

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Métricas esperadas para AutopoieticManager (Sprint 2)
EXPECTED_AUTOPOIETIC_METRICS = {
    "phi_before",
    "phi_after",
    "phi_delta",
    "components_synthesized",
    "strategy",
    "synthesis_time_ms",  # NOVO
    "validation_success",  # NOVO
    "rollback_count",  # NOVO
    "memory_delta_mb",  # NOVO
}

# Métricas esperadas para IntegrationLoop (para comparação)
EXPECTED_INTEGRATION_METRICS = {
    "phi_estimate",
    "cycle_duration_ms",
    "components_activated",
    "theoretical_complexity",
}


def load_snapshot(snapshot_path: Path) -> Dict[str, Any]:
    """
    Carrega snapshot de métricas.

    Args:
        snapshot_path: Caminho para snapshot.json

    Returns:
        Dados do snapshot ou dict vazio se não existir
    """
    if not snapshot_path.exists():
        logger.warning(f"Snapshot não encontrado: {snapshot_path}")
        return {}

    try:
        with open(snapshot_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"Snapshot carregado: {snapshot_path}")
        return data
    except Exception as e:
        logger.error(f"Erro ao carregar snapshot: {e}")
        return {}


def extract_module_metrics(snapshot: Dict[str, Any], module_prefix: str) -> Dict[str, Set[str]]:
    """
    Extrai métricas de módulos que começam com o prefixo especificado.

    Args:
        snapshot: Dados do snapshot
        module_prefix: Prefixo do módulo (ex: "autopoietic_cycle_", "integration_loop_cycle_")

    Returns:
        Dicionário {module_name: set(metric_names)}
    """
    module_metrics: Dict[str, Set[str]] = {}

    for module_name, module_data in snapshot.items():
        if module_name.startswith(module_prefix):
            metrics = module_data.get("metrics", {})
            metric_names = set(metrics.keys())
            module_metrics[module_name] = metric_names

    return module_metrics


def validate_autopoietic_metrics(snapshot: Dict[str, Any]) -> bool:
    """
    Valida que AutopoieticManager está capturando todas as métricas necessárias.

    Args:
        snapshot: Dados do snapshot

    Returns:
        True se todas as métricas estão presentes, False caso contrário
    """
    logger.info("\n" + "=" * 80)
    logger.info("VALIDAÇÃO: AutopoieticManager Metrics")
    logger.info("=" * 80)

    autopoietic_modules = extract_module_metrics(snapshot, "autopoietic_cycle_")

    if not autopoietic_modules:
        logger.error("❌ Nenhum ciclo autopoiético encontrado no snapshot!")
        return False

    logger.info(f"✅ Encontrados {len(autopoietic_modules)} ciclos autopoiéticos")

    all_valid = True
    for module_name, metrics in autopoietic_modules.items():
        logger.info(f"\n  Módulo: {module_name}")
        logger.info(f"  Métricas encontradas: {len(metrics)}")

        missing_metrics = EXPECTED_AUTOPOIETIC_METRICS - metrics
        extra_metrics = metrics - EXPECTED_AUTOPOIETIC_METRICS

        if missing_metrics:
            logger.error(f"  ❌ Métricas faltando: {missing_metrics}")
            all_valid = False
        else:
            logger.info(f"  ✅ Todas as métricas esperadas estão presentes!")

        if extra_metrics:
            logger.info(f"  ℹ️  Métricas extras (não esperadas): {extra_metrics}")

        # Mostrar detalhes de cada métrica
        module_data = snapshot.get(module_name, {})
        metrics_data = module_data.get("metrics", {})
        for metric_name in sorted(EXPECTED_AUTOPOIETIC_METRICS):
            if metric_name in metrics_data:
                metric_value = metrics_data[metric_name].get("value", "N/A")
                logger.info(f"    • {metric_name}: {metric_value}")

    return all_valid


def compare_with_integration_loop(snapshot: Dict[str, Any]) -> None:
    """
    Compara padrão de captura de métricas entre AutopoieticManager e IntegrationLoop.

    Args:
        snapshot: Dados do snapshot
    """
    logger.info("\n" + "=" * 80)
    logger.info("COMPARAÇÃO: AutopoieticManager vs IntegrationLoop")
    logger.info("=" * 80)

    autopoietic_modules = extract_module_metrics(snapshot, "autopoietic_cycle_")
    integration_modules = extract_module_metrics(snapshot, "integration_loop_cycle_")

    logger.info(f"\nAutopoietic cycles: {len(autopoietic_modules)}")
    logger.info(f"Integration cycles: {len(integration_modules)}")

    if autopoietic_modules and integration_modules:
        # Pegar primeiro módulo de cada tipo para comparação
        auto_module = list(autopoietic_modules.keys())[0]
        integ_module = list(integration_modules.keys())[0]

        auto_metrics = autopoietic_modules[auto_module]
        integ_metrics = integration_modules[integ_module]

        logger.info(f"\nExemplo AutopoieticManager ({auto_module}):")
        logger.info(f"  Métricas: {len(auto_metrics)}")
        logger.info(f"  {sorted(auto_metrics)}")

        logger.info(f"\nExemplo IntegrationLoop ({integ_module}):")
        logger.info(f"  Métricas: {len(integ_metrics)}")
        logger.info(f"  {sorted(integ_metrics)}")

        # Análise de padrões
        logger.info("\n📊 Análise de Padrões:")
        logger.info(f"  AutopoieticManager captura {len(auto_metrics)} métricas por ciclo")
        logger.info(f"  IntegrationLoop captura {len(integ_metrics)} métricas por ciclo")

        if len(auto_metrics) >= len(EXPECTED_AUTOPOIETIC_METRICS):
            logger.info("  ✅ AutopoieticManager está capturando métricas em padrão adequado")
        else:
            logger.warning("  ⚠️  AutopoieticManager pode não estar capturando todas as métricas")


def main() -> int:
    """
    Função principal do script de validação.

    Returns:
        0 se validação passou, 1 caso contrário
    """
    logger.info("🔍 Iniciando validação de métricas autopoiéticas...")

    # Caminho para snapshot de métricas
    snapshot_path = Path("data/monitor/module_metrics/snapshot.json")

    # Carregar snapshot
    snapshot = load_snapshot(snapshot_path)

    if not snapshot:
        logger.error("❌ Falha ao carregar snapshot. Verifique se o sistema está executando.")
        return 1

    # Validar métricas do AutopoieticManager
    validation_passed = validate_autopoietic_metrics(snapshot)

    # Comparar com IntegrationLoop
    compare_with_integration_loop(snapshot)

    # Resultado final
    logger.info("\n" + "=" * 80)
    if validation_passed:
        logger.info("✅ VALIDAÇÃO PASSOU: Todas as métricas estão sendo capturadas!")
        logger.info("=" * 80)
        return 0
    else:
        logger.error("❌ VALIDAÇÃO FALHOU: Algumas métricas estão faltando!")
        logger.info("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
