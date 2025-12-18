#!/usr/bin/env python3
"""Verifica saúde do sistema baseado em métricas de Φ.

Monitora se o sistema está mantendo Φ acima do threshold e alerta
se houver degradação ou colapsos frequentes.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

PHI_THRESHOLD = 0.3
PHI_WARNING_THRESHOLD = 0.4  # Alerta se Φ estiver abaixo disso


def check_current_phi(metrics_path: Path) -> Optional[float]:
    """Verifica Φ atual do sistema."""
    if not metrics_path.exists():
        return None

    try:
        with metrics_path.open("r", encoding="utf-8") as f:
            metrics = json.load(f)
            return float(metrics.get("phi", 0.0))
    except Exception as e:
        logger.warning("Erro ao ler métricas: %s", e)
        return None


def check_cycle_history(history_path: Path) -> Dict[str, Any]:
    """Analisa histórico de ciclos para detectar problemas."""
    if not history_path.exists():
        return {"status": "no_history", "message": "Nenhum histórico encontrado"}

    cycles = []
    try:
        with history_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    cycles.append(json.loads(line))
    except Exception as e:
        return {"status": "error", "message": f"Erro ao ler histórico: {e}"}

    if not cycles:
        return {"status": "empty", "message": "Histórico vazio"}

    # Analisar últimos 10 ciclos
    recent_cycles = cycles[-10:]
    low_phi_count = 0
    rollback_count = 0
    rejected_count = 0

    for cycle in recent_cycles:
        phi_before = cycle.get("phi_before")
        phi_after = cycle.get("phi_after")
        synthesized = cycle.get("synthesized_components", [])

        if phi_before is not None and phi_before < PHI_THRESHOLD:
            rejected_count += 1
        if phi_after is not None and phi_after < PHI_THRESHOLD:
            if len(synthesized) > 0:
                rollback_count += 1
            low_phi_count += 1

    # Determinar status
    if rollback_count > 2:
        status = "critical"
        message = f"⚠️ CRÍTICO: {rollback_count} rollbacks nos últimos 10 ciclos"
    elif rejected_count > 5:
        status = "warning"
        message = f"⚠️ ATENÇÃO: {rejected_count} ciclos rejeitados (Φ baixo)"
    elif low_phi_count > 3:
        status = "warning"
        message = f"⚠️ ATENÇÃO: {low_phi_count} ciclos com Φ abaixo do threshold"
    else:
        status = "healthy"
        message = "✅ Sistema saudável"

    return {
        "status": status,
        "message": message,
        "total_cycles": len(cycles),
        "recent_cycles": len(recent_cycles),
        "rollbacks": rollback_count,
        "rejected": rejected_count,
        "low_phi": low_phi_count,
    }


def main():
    """Função principal."""
    project_root = Path(__file__).parent.parent.parent
    metrics_path = project_root / "data" / "monitor" / "real_metrics.json"
    history_path = project_root / "data" / "autopoietic" / "cycle_history.jsonl"

    print("=" * 70)
    print("VERIFICAÇÃO DE SAÚDE - SISTEMA AUTOPOIÉTICO (PHASE 22)")
    print("=" * 70)
    print()

    # Verificar Φ atual
    current_phi = check_current_phi(metrics_path)
    if current_phi is not None:
        print(f"📊 Φ Atual: {current_phi:.4f}")
        if current_phi < PHI_THRESHOLD:
            print(f"   ❌ CRÍTICO: Φ abaixo do threshold ({PHI_THRESHOLD})")
            sys.exit(1)
        elif current_phi < PHI_WARNING_THRESHOLD:
            print(f"   ⚠️  ATENÇÃO: Φ abaixo do nível de alerta ({PHI_WARNING_THRESHOLD})")
        else:
            print(f"   ✅ Φ saudável (threshold: {PHI_THRESHOLD})")
    else:
        print("   ⚠️  Métricas não disponíveis")

    print()

    # Verificar histórico
    history_status = check_cycle_history(history_path)
    print(f"📈 Status do Histórico: {history_status['message']}")
    if "rollbacks" in history_status:
        print(f"   Rollbacks recentes: {history_status['rollbacks']}")
        print(f"   Rejeitados recentes: {history_status['rejected']}")
        print(f"   Total de ciclos: {history_status['total_cycles']}")

    print()
    print("=" * 70)

    # Exit code baseado no status
    if history_status.get("status") == "critical":
        sys.exit(1)
    elif history_status.get("status") == "warning":
        sys.exit(0)  # Warning não é fatal
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
