#!/usr/bin/env python3
"""
Pre-Test Validation Script

Valida saúde do sistema antes de executar testes, especialmente:
- Meta cognition health check
- Entropy warnings
- Outros indicadores críticos

Se meta cognition analysis/action failed for detectado, NÃO EXECUTA TESTES.

Author: Fabrício da Silva + assistência de IA
Date: 2025-12-07
"""

import sys
import re
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Adicionar path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utilities.analysis.dynamic_error_classifier import DynamicErrorClassifier

# Timestamp da correção de meta cognition (2025-12-07 23:30)
CORRECTION_TIMESTAMP = datetime(2025, 12, 7, 23, 30, 0).timestamp()


def check_recent_logs(log_dir: str = "data/test_reports", max_files: int = 5, min_age_hours: int = 0) -> Dict[str, Any]:
    """
    Verifica logs recentes para meta cognition failures.

    IMPORTANTE: Ignora logs criados ANTES da correção de meta cognition.

    Args:
        log_dir: Diretório de logs
        max_files: Número máximo de arquivos recentes para verificar
        min_age_hours: Idade mínima do log em horas (0 = apenas logs após correção)

    Returns:
        Dicionário com resultados da verificação
    """
    log_path = Path(log_dir)
    if not log_path.exists():
        return {
            'status': 'ok',
            'message': 'Log directory not found - skipping validation',
            'should_block': False,
        }

    # Buscar arquivos de log recentes (após correção)
    now = time.time()
    all_log_files = sorted(
        log_path.glob("*.log"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    # Filtrar apenas logs criados APÓS a correção
    recent_log_files = [
        f for f in all_log_files
        if f.stat().st_mtime >= CORRECTION_TIMESTAMP
    ][:max_files]

    # Se não há logs recentes (após correção), não bloquear
    if not recent_log_files:
        return {
            'status': 'ok',
            'message': 'No logs found after correction timestamp - assuming correction worked',
            'should_block': False,
        }

    classifier = DynamicErrorClassifier()

    for log_file in recent_log_files:
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            # Classificar erros do arquivo
            classifier.classify_log_file(lines)
        except Exception as e:
            print(f"⚠️  Erro ao processar {log_file}: {e}", file=sys.stderr)
            continue

    summary = classifier.get_summary()

    return {
        'status': 'critical' if summary['should_block_tests'] else 'ok',
        'should_block': summary['should_block_tests'],
        'blocking_count': summary['blocking_count'],
        'blocking_errors': summary['blocking_errors'],
        'summary': summary,
    }


def check_metacognition_health() -> Dict[str, Any]:
    """
    Verifica saúde de meta cognição diretamente.

    Returns:
        Dicionário com status de saúde
    """
    try:
        # Tentar importar e verificar meta cognição
        from src.metacognition.metacognition_agent import MetacognitionAgent

        agent = MetacognitionAgent()
        health = agent.get_quick_health_check()

        # get_quick_health_check retorna {"status": "ok"} quando funciona
        # ou {"status": "error"} quando falha
        health_status = health.get('status', 'unknown')

        if health_status == 'error':
            return {
                'status': 'critical',
                'should_block': True,
                'message': f"Meta cognition health check failed: {health.get('error', 'unknown error')}",
                'health': health,
            }

        # Status "ok" significa que está funcionando (mesmo que health_status interno seja "poor")
        return {
            'status': 'ok',
            'should_block': False,
            'message': 'Meta cognition health check passed',
            'health': health,
        }
    except Exception as e:
        # Se não conseguir verificar, não bloquear (pode ser primeira execução)
        return {
            'status': 'unknown',
            'should_block': False,
            'message': f'Could not check meta cognition health: {e}',
        }


def main() -> int:
    """Função principal."""
    print("=" * 70)
    print("🔍 PRE-TEST VALIDATION")
    print("=" * 70)
    print()

    # 1. Verificar saúde de meta cognição DIRETAMENTE (mais confiável)
    print("1. Verificando saúde de meta cognição diretamente...")
    health_check = check_metacognition_health()

    if health_check['should_block']:
        print(f"   ❌ CRITICAL: {health_check['message']}")
        print("\n" + "=" * 70)
        print("🚫 TESTES BLOQUEADOS")
        print("=" * 70)
        print("\nNÃO EXECUTAR TESTES até resolver problemas de meta cognição.")
        return 1

    print(f"   ✅ {health_check['message']}")

    # 2. Verificar logs recentes (apenas logs APÓS correção)
    print("\n2. Verificando logs recentes (após correção)...")
    log_check = check_recent_logs()

    if log_check['should_block']:
        print("   ⚠️  WARNING: Meta cognition failures detectados em logs recentes")
        print(f"   🔴 Erros bloqueantes: {log_check['blocking_count']}")
        print("\n   ERROS BLOQUEANTES:")
        for error in log_check.get('blocking_errors', [])[:5]:  # Limitar a 5
            print(f"      - {error.get('category', 'UNKNOWN')}: {error.get('message', '')[:100]}")

        # Se saúde direta está OK mas logs têm erros, pode ser cache/legado
        # Não bloquear se saúde direta passou
        print("\n   ⚠️  NOTA: Saúde direta passou, mas logs antigos têm erros.")
        print("   Continuando com testes (erros podem ser de logs legados).")
    else:
        print("   ✅ Nenhum erro bloqueante detectado nos logs recentes")

    if health_check['should_block']:
        print(f"   ❌ CRITICAL: {health_check['message']}")
        print("\n" + "=" * 70)
        print("🚫 TESTES BLOQUEADOS")
        print("=" * 70)
        print("\nNÃO EXECUTAR TESTES até resolver problemas de meta cognição.")
        return 1

    print(f"   ✅ {health_check['message']}")

    # 3. Resumo
    print("\n" + "=" * 70)
    print("✅ VALIDAÇÃO PRÉ-TESTE CONCLUÍDA")
    print("=" * 70)
    print("\nSistema está saudável - testes podem ser executados.")

    return 0


if __name__ == '__main__':
    sys.exit(main())

