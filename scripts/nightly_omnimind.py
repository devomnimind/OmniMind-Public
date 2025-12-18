#!/usr/bin/env python
"""
Nightly OmniMind Tasks - simples e seguros (não inicia serviços pesados).

Fluxo:
- Registra início/fim no log.
- Executa verificação leve do Qdrant (local → cloud fallback).
- Executa verificação leve do Supabase (se configurado).
- Opcional: roda teste rápido de memória semântica.
- Opcional: executa consolidação leve de snapshots em memória semântica.
- Gera um relatório JSON básico com status das tarefas.

Uso:
    python scripts/nightly_omnimind.py --run-tests --consolidate
Agenda externa (cron/systemd) deve chamar este script.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv  # type: ignore[import-untyped]

BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env", override=False)

LOG_DIR = Path("logs/nightly")
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("nightly")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOG_DIR / "nightly.log")
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(handler)
logger.addHandler(logging.StreamHandler())


def _update_nightly_summary(report: Dict[str, Any], max_entries: int = 30) -> None:
    """
    Atualiza arquivo de resumo `nightly_summary.json` com últimos N relatórios.

    Mantém apenas dados agregados (status por serviço/tarefa) para inspeção rápida.
    """

    summary_path = LOG_DIR / "nightly_summary.json"
    try:
        if summary_path.exists():
            existing: List[Dict[str, Any]] = json.loads(summary_path.read_text())
        else:
            existing = []
    except Exception:
        existing = []

    tasks = report.get("tasks", [])

    def _find_task(name: str) -> Dict[str, Any]:
        for t in tasks:
            if t.get("task") == name:
                return t
        return {}

    qdrant = _find_task("qdrant_health")
    supabase = _find_task("supabase_health")
    fast_test = _find_task("fast_test")
    consolidation = _find_task("consolidation")

    entry = {
        "timestamp": report.get("timestamp"),
        "qdrant_status": qdrant.get("status"),
        "qdrant_mode": qdrant.get("mode"),
        "supabase_status": supabase.get("status"),
        "fast_test_status": fast_test.get("status"),
        "consolidation_status": consolidation.get("status"),
        "consolidation_episodes": consolidation.get("episodes"),
        "consolidation_concepts_created": consolidation.get("concepts_created"),
        "consolidation_concepts_updated": consolidation.get("concepts_updated"),
        "consolidation_relationships_created": consolidation.get("relationships_created"),
    }

    existing.append(entry)
    # Mantém ordenado por timestamp e limita a max_entries
    existing_sorted = sorted(existing, key=lambda e: e.get("timestamp") or "")[-max_entries:]

    summary_path.write_text(json.dumps(existing_sorted, indent=2))


def check_qdrant_health() -> Dict:
    """
    Verifica Qdrant local primeiro; se falhar, tenta Qdrant Cloud (se configurado).
    """

    try:
        from qdrant_client import QdrantClient
    except Exception as e:  # pragma: no cover
        return {"status": "down", "error": f"qdrant-client import failed: {e}"}

    # Local first
    try:
        local_client = QdrantClient(host="localhost", port=6333)
        local_client.get_collections()
        return {"status": "up", "mode": "local"}
    except Exception as local_err:  # pragma: no cover - depende de serviço externo
        cloud_url = os.environ.get("OMNIMIND_QDRANT_CLOUD_URL")
        cloud_key = os.environ.get("OMNIMIND_QDRANT_API_KEY")
        if not cloud_url or not cloud_key:
            return {"status": "down", "mode": "local", "error": str(local_err)}

        # Cloud fallback
        try:
            cloud_client = QdrantClient(url=cloud_url, api_key=cloud_key)
            cloud_client.get_collections()
            return {"status": "up", "mode": "cloud"}
        except Exception as cloud_err:
            return {
                "status": "down",
                "mode": "cloud",
                "error": f"local={local_err}; cloud={cloud_err}",
            }


def check_supabase_health() -> Dict:
    """
    Health check leve do Supabase, sem depender de imports internos de src/.
    Usa supabase-py diretamente com OMNIMIND_SUPABASE_URL/ANON_KEY.
    """

    try:
        from supabase import Client, create_client  # type: ignore[import-untyped]
    except Exception as e:  # pragma: no cover - lib ausente
        return {"status": "down", "error": f"supabase-py import failed: {e}"}

    url = os.environ.get("OMNIMIND_SUPABASE_URL")
    anon_key = os.environ.get("OMNIMIND_SUPABASE_ANON_KEY")
    if not url or not anon_key:
        return {"status": "missing_config"}

    try:
        client: Client = create_client(url, anon_key)
        client.table("consciousness_snapshots").select("*").limit(1).execute()
        return {"status": "up"}
    except Exception as e:  # pragma: no cover - ambiente externo
        return {"status": "down", "error": str(e)}


def load_snapshots_for_consolidation(limit: int = 100) -> List[Dict]:
    """
    Carrega snapshots recentes do Supabase para consolidação.

    Espera tabela public.consciousness_snapshots com colunas:
    snapshot_id, timestamp, phi_value, qualia_signature (json),
    attention_state (json), integration_level, metadata (json).
    """

    try:
        from supabase import Client, create_client  # type: ignore[import-untyped]
    except Exception as e:  # pragma: no cover
        logger.warning("Supabase indisponível para consolidação: %s", e)
        return []

    url = os.environ.get("OMNIMIND_SUPABASE_URL")
    anon_key = os.environ.get("OMNIMIND_SUPABASE_ANON_KEY")
    if not url or not anon_key:
        logger.info("OMNIMIND_SUPABASE_URL/ANON_KEY não configurados; sem consolidação.")
        return []

    client: Client = create_client(url, anon_key)
    try:
        resp = (
            client.table("consciousness_snapshots")
            .select(
                "snapshot_id,timestamp,phi_value,qualia_signature,attention_state,"
                "integration_level,metadata"
            )
            .order("timestamp", desc=True)
            .limit(limit)
            .execute()
        )
    except Exception as e:  # pragma: no cover
        logger.warning("Falha ao carregar snapshots do Supabase: %s", e)
        return []

    rows = resp.data or []
    episodes: List[Dict] = []

    for row in rows:
        qualia = row.get("qualia_signature") or {}
        attention = row.get("attention_state") or {}
        metadata = row.get("metadata") or {}

        # Texto simples representando o estado de consciência
        content_parts = [
            f"phi={row.get('phi_value')}",
            f"integration={row.get('integration_level')}",
            f"qualia={qualia}",
            f"attention={attention}",
        ]
        content = " | ".join(str(p) for p in content_parts)

        tags: List[str] = []
        tags.extend(list(attention.keys()))
        tags.extend(list(qualia.keys()))
        extra_tags = metadata.get("tags") if isinstance(metadata, dict) else None
        if isinstance(extra_tags, list):
            tags.extend(str(t) for t in extra_tags)

        episodes.append(
            {
                "content": content,
                "tags": tags,
            }
        )

    return episodes


def run_consolidation_job(batch_size: int = 100) -> Dict:
    """
    Roda consolidação leve usando MemoryConsolidator + SemanticMemory.
    Não altera Qdrant; atua apenas em memória semântica local.
    """

    import sys

    sys.path.append(str(BASE_DIR / "src"))

    from memory.memory_consolidator import MemoryConsolidator
    from memory.semantic_memory import SemanticMemory

    episodes = load_snapshots_for_consolidation(limit=batch_size)
    if not episodes:
        return {"status": "skipped", "reason": "no_episodes"}

    semantic = SemanticMemory()
    consolidator = MemoryConsolidator(semantic)

    stats = consolidator.consolidate(episodes)
    rels = consolidator.extract_relationships(episodes)

    return {
        "status": "ok",
        "episodes": len(episodes),
        "concepts_created": stats.get("concepts_created", 0),
        "concepts_updated": stats.get("concepts_updated", 0),
        "relationships_created": rels,
    }


def run_fast_tests() -> Dict:
    cmd = [
        "pytest",
        "tests/memory/test_phase_24_basic.py::TestSemanticMemoryLayer::test_retrieve_similar",
        "-q",
        "--maxfail=1",
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return {
            "status": "ok" if res.returncode == 0 else "failed",
            "stdout": res.stdout,
            "stderr": res.stderr,
        }
    except Exception as e:  # pragma: no cover
        return {"status": "error", "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Nightly OmniMind tasks (leve).")
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Executa teste rápido de memória semântica.",
    )
    parser.add_argument(
        "--consolidate",
        action="store_true",
        help="Executa consolidação leve de snapshots recentes em memória semântica.",
    )
    args = parser.parse_args()

    tasks: List[Dict] = []

    logger.info("Iniciando rotina noturna leve.")

    qdrant_status = check_qdrant_health()
    tasks.append({"task": "qdrant_health", **qdrant_status})
    logger.info("Qdrant: %s", qdrant_status)

    supabase_status = check_supabase_health()
    tasks.append({"task": "supabase_health", **supabase_status})
    logger.info("Supabase: %s", supabase_status)

    if args.run_tests:
        test_res = run_fast_tests()
        tasks.append({"task": "fast_test", **test_res})
        logger.info("Testes: %s", test_res["status"])

    if args.consolidate:
        consolid_res = run_consolidation_job()
        tasks.append({"task": "consolidation", **consolid_res})
        logger.info("Consolidação: %s", consolid_res)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tasks": tasks,
    }
    report_path = LOG_DIR / (
        f"nightly_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    )
    report_path.write_text(json.dumps(report, indent=2))
    _update_nightly_summary(report)
    logger.info("Relatório salvo em %s", report_path)
    logger.info("Rotina noturna concluída.")


if __name__ == "__main__":
    main()
