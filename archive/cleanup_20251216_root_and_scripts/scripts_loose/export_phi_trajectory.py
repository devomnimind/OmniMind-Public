#!/usr/bin/env python
"""
Exporta trajetória de Φ (phi) a partir de snapshots de consciência.

Fonte primária: Supabase (tabela public.consciousness_snapshots).
Fallback: arquivo local JSONL usado por ConsciousnessStateManager.

Uso:
    python scripts/export_phi_trajectory.py --hours 24
    python scripts/export_phi_trajectory.py --hours 24 --rich

Gera um arquivo JSON em `data/test_reports/phi_trajectory_YYYYMMDD_HHMMSS.json`
com lista ordenada de:
    {"timestamp": "...", "phi_value": ...}  # formato simples
    ou (com --rich):
    {
        "timestamp": "...",
        "phi_value": ...,
        "attention_state": {"coherence": ..., "marker_integration": ..., ...},
        "integration_level": ...,
        "episode_id": "..."
    }
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv  # type: ignore[import-untyped]


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env", override=False)


def get_phi_trajectory(hours: int, rich: bool = False) -> List[dict] | List[Tuple[datetime, float]]:
    import sys

    # Garantir que `src/` esteja no path para imports relativos
    sys.path.append(str(BASE_DIR / "src"))

    from memory.consciousness_state_manager import ConsciousnessStateManager  # type: ignore

    manager = ConsciousnessStateManager()
    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=hours)

    if rich:
        return manager.get_phi_trajectory_rich(start, end, limit=1000)
    else:
        return manager.get_phi_trajectory(start, end, limit=1000)


def main() -> None:
    parser = argparse.ArgumentParser(description="Exportar trajetória de Φ (phi).")
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Janela em horas para trás a partir de agora (default: 24).",
    )
    parser.add_argument(
        "--rich",
        action="store_true",
        help="Incluir campos adicionais: attention_state, integration_level, episode_id",
    )
    args = parser.parse_args()

    trajectory = get_phi_trajectory(args.hours, rich=args.rich)
    if not trajectory:
        print("Nenhum ponto de Φ encontrado na janela especificada.")
        return

    data_dir = Path("data/test_reports")
    data_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    suffix = "_rich" if args.rich else ""
    out_path = data_dir / f"phi_trajectory{suffix}_{ts}.json"

    if args.rich:
        # Rich format: already a list of dicts
        serializable = trajectory
    else:
        # Simple format: convert tuples to dicts
        serializable = [
            {"timestamp": t.isoformat(), "phi_value": float(phi)} for t, phi in trajectory
        ]

    out_path.write_text(json.dumps(serializable, indent=2))

    format_type = "rico" if args.rich else "simples"
    print(f"Trajetória {format_type} com {len(serializable)} pontos exportada para {out_path}")


if __name__ == "__main__":
    main()
