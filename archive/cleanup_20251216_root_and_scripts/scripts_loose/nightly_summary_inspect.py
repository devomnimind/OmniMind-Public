#!/usr/bin/env python
"""
Helper para inspecionar rapidamente o resumo das rotinas noturnas.

Lê `logs/nightly/nightly_summary.json` e imprime as últimas entradas com filtros:
- --limit N: número de registros a exibir (default: 10)
- --only-errors: mostra apenas entradas com algum status não OK
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


LOG_DIR = Path("logs/nightly")
SUMMARY_PATH = LOG_DIR / "nightly_summary.json"


@dataclass
class NightlyEntry:
    timestamp: str
    qdrant_status: str | None
    qdrant_mode: str | None
    supabase_status: str | None
    fast_test_status: str | None
    consolidation_status: str | None

    @property
    def has_error(self) -> bool:
        if self.qdrant_status not in (None, "up"):
            return True
        if self.supabase_status not in (None, "up", "missing_config"):
            return True
        if self.fast_test_status not in (None, "ok"):
            return True
        if self.consolidation_status not in (None, "ok", "skipped"):
            return True
        return False


def load_entries() -> List[NightlyEntry]:
    if not SUMMARY_PATH.exists():
        return []

    try:
        raw: List[Dict[str, Any]] = json.loads(SUMMARY_PATH.read_text())
    except Exception:
        return []

    entries: List[NightlyEntry] = []
    for row in raw:
        entries.append(
            NightlyEntry(
                timestamp=row.get("timestamp", ""),
                qdrant_status=row.get("qdrant_status"),
                qdrant_mode=row.get("qdrant_mode"),
                supabase_status=row.get("supabase_status"),
                fast_test_status=row.get("fast_test_status"),
                consolidation_status=row.get("consolidation_status"),
            )
        )
    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspeção rápida de nightly_summary.json")
    parser.add_argument("--limit", type=int, default=10, help="Número de registros a exibir")
    parser.add_argument(
        "--only-errors",
        action="store_true",
        help="Mostrar apenas execuções com algum status não OK",
    )
    args = parser.parse_args()

    entries = load_entries()
    if not entries:
        print("Nenhuma entrada encontrada em logs/nightly/nightly_summary.json")
        return

    # Ordena por timestamp crescente e aplica limit no final
    def _ts(e: NightlyEntry) -> datetime:
        try:
            return datetime.fromisoformat(e.timestamp)
        except Exception:
            return datetime.min

    entries_sorted = sorted(entries, key=_ts)[-args.limit :]

    if args.only_errors:
        entries_sorted = [e for e in entries_sorted if e.has_error]
        if not entries_sorted:
            print("Nenhuma execução com erro nos últimos registros.")
            return

    for e in entries_sorted:
        print(f"- {e.timestamp}")
        print(f"  Qdrant:   {e.qdrant_status} (mode={e.qdrant_mode})")
        print(f"  Supabase: {e.supabase_status}")
        print(f"  FastTest: {e.fast_test_status}")
        print(f"  Consol.:  {e.consolidation_status}")
        print()


if __name__ == "__main__":
    main()


