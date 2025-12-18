#!/usr/bin/env python3
"""
Script para Coletar Métricas Baseline - Otimização de Memória

Coleta métricas atuais do sistema ANTES das otimizações:
- Uso de memória por agente
- Latência de execução
- Model load times
- Cache statistics (se existir)
- Qdrant usage

Autor: Fabrício da Silva + assistência de IA
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

import psutil

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Imports após path setup (E402 aceitável para scripts)
from src.agents.code_agent import CodeAgent  # noqa: E402
from src.integrations.llm_router import get_llm_router  # noqa: E402
from src.integrations.qdrant_adapter import QdrantAdapter, QdrantConfig  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaselineMetricsCollector:
    """Coleta métricas baseline do sistema atual."""

    def __init__(self, output_dir: str = "data/metrics/baseline"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metrics: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "baseline": True,
            "memory": {},
            "latency": {},
            "models": {},
            "qdrant": {},
            "cache": {},
        }

    def collect_all(self) -> Dict[str, Any]:
        """Coleta todas as métricas baseline."""
        logger.info("=" * 80)
        logger.info("COLETANDO MÉTRICAS BASELINE - OTIMIZAÇÃO DE MEMÓRIA")
        logger.info("=" * 80)

        # 1. Memória do sistema
        logger.info("1. Coletando métricas de memória...")
        self.metrics["memory"] = self._collect_memory_metrics()

        # 2. Latência de agentes
        logger.info("2. Coletando métricas de latência...")
        self.metrics["latency"] = asyncio.run(self._collect_latency_metrics())

        # 3. Model loading
        logger.info("3. Coletando métricas de modelos...")
        self.metrics["models"] = self._collect_model_metrics()

        # 4. Qdrant usage
        logger.info("4. Coletando métricas do Qdrant...")
        self.metrics["qdrant"] = self._collect_qdrant_metrics()

        # 5. Cache statistics (se existir)
        logger.info("5. Coletando estatísticas de cache...")
        self.metrics["cache"] = self._collect_cache_metrics()

        # Salvar métricas (serializar Enums e objetos não-JSON)
        output_file = self.output_dir / f"baseline_{int(time.time())}.json"
        serializable_metrics = self._make_json_serializable(self.metrics)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(serializable_metrics, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Métricas baseline salvas em: {output_file}")
        logger.info("=" * 80)

        return self.metrics

    def _collect_memory_metrics(self) -> Dict[str, Any]:
        """Coleta métricas de memória do sistema."""
        process = psutil.Process()
        memory_info = process.memory_info()

        # Memória do sistema
        system_memory = psutil.virtual_memory()

        return {
            "process_memory_mb": memory_info.rss / (1024 * 1024),
            "process_memory_gb": memory_info.rss / (1024 * 1024 * 1024),
            "system_total_gb": system_memory.total / (1024 * 1024 * 1024),
            "system_available_gb": system_memory.available / (1024 * 1024 * 1024),
            "system_used_percent": system_memory.percent,
            "num_threads": process.num_threads(),
            "num_fds": process.num_fds() if hasattr(process, "num_fds") else None,
        }

    async def _collect_latency_metrics(self) -> Dict[str, Any]:
        """Coleta métricas de latência de agentes (versão rápida - sem execução completa)."""
        latencies = {
            "note": "Latência completa será coletada em testes separados",
            "agent_initialization": {},
        }

        # Apenas medir tempo de inicialização (não execução completa)
        config_path = "config/agent_config.yaml"

        # Teste inicialização CodeAgent
        try:
            logger.info("  Testando inicialização CodeAgent...")
            start_time = time.time()
            CodeAgent(config_path)  # Apenas inicializar, não usar
            init_time = time.time() - start_time

            latencies["agent_initialization"]["code_agent"] = {
                "init_time_seconds": init_time,
                "init_time_ms": init_time * 1000,
            }
            logger.info("    ✅ CodeAgent init: %.2fs", init_time)

        except Exception as e:
            logger.error("    ❌ CodeAgent init falhou: %s", e)
            latencies["agent_initialization"]["code_agent"] = {"error": str(e)}

        return latencies

    def _collect_model_metrics(self) -> Dict[str, Any]:
        """Coleta métricas de modelos."""
        metrics = {
            "llm_router": {},
            "ollama": {},
        }

        # LLM Router
        try:
            router = get_llm_router()
            metrics["llm_router"] = {
                "available": True,
                "providers": list(router.providers.keys()),
                "metrics": router.metrics.copy() if hasattr(router, "metrics") else {},
            }
        except Exception as e:
            logger.warning(f"LLM Router não disponível: {e}")
            metrics["llm_router"] = {"available": False, "error": str(e)}

        # Ollama (verificar se está rodando)
        try:
            import requests

            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get("models", [])
                metrics["ollama"] = {
                    "available": True,
                    "models": [m.get("name", "unknown") for m in models],
                    "model_count": len(models),
                }
            else:
                metrics["ollama"] = {"available": False, "status_code": response.status_code}
        except Exception as e:
            logger.warning(f"Ollama não disponível: {e}")
            metrics["ollama"] = {"available": False, "error": str(e)}

        return metrics

    def _collect_qdrant_metrics(self) -> Dict[str, Any]:
        """Coleta métricas do Qdrant."""
        metrics = {
            "available": False,
            "collections": [],
            "collection_sizes": {},
        }

        try:
            config = QdrantConfig.from_env()
            if not config:
                logger.warning("Qdrant config não encontrada")
                return metrics

            adapter = QdrantAdapter(config)
            collections = adapter.list_collections()

            metrics["available"] = True
            metrics["collections"] = collections

            # Tentar obter tamanhos das coleções
            try:
                from qdrant_client import QdrantClient

                client = QdrantClient(url=config.url, api_key=config.api_key)
                for collection in collections:
                    try:
                        info = client.get_collection(collection)
                        metrics["collection_sizes"][collection] = {
                            "points_count": (
                                info.points_count if hasattr(info, "points_count") else None
                            ),
                            "vectors_count": (
                                info.vectors_count if hasattr(info, "vectors_count") else None
                            ),
                        }
                    except Exception as e:
                        logger.warning(f"Erro ao obter info da coleção {collection}: {e}")

            except Exception as e:
                logger.warning(f"Erro ao conectar ao Qdrant para métricas: {e}")

        except Exception as e:
            logger.warning(f"Qdrant não disponível: {e}")
            metrics["error"] = str(e)

        return metrics

    def _collect_cache_metrics(self) -> Dict[str, Any]:
        """Coleta estatísticas de cache existente."""
        metrics = {
            "neural_response_cache": {},
            "mcp_cache": {},
        }

        # Neural Response Cache
        try:
            from src.neurosymbolic.response_cache import get_response_cache

            cache = get_response_cache()
            stats = cache.get_stats()
            metrics["neural_response_cache"] = {
                "available": True,
                "stats": stats,
            }
        except Exception as e:
            logger.debug(f"Neural Response Cache não disponível: {e}")
            metrics["neural_response_cache"] = {"available": False}

        # MCP Cache (se existir)
        # TODO: Adicionar quando MCP cache estiver disponível

        return metrics

    def _make_json_serializable(self, obj: Any) -> Any:
        """Converte objetos não-JSON serializáveis para tipos básicos."""
        if isinstance(obj, dict):
            return {k: self._make_json_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif hasattr(obj, "value"):  # Enum
            return obj.value
        elif hasattr(obj, "__dict__"):
            return self._make_json_serializable(obj.__dict__)
        else:
            return obj

    def print_summary(self) -> None:
        """Imprime resumo das métricas coletadas."""
        print("\n" + "=" * 80)
        print("RESUMO DAS MÉTRICAS BASELINE")
        print("=" * 80)

        # Memória
        memory = self.metrics.get("memory", {})
        print("\n💾 MEMÓRIA:")
        mem_gb = memory.get("process_memory_gb", 0)
        mem_percent = memory.get("system_used_percent", 0)
        print(f"  Processo: {mem_gb:.2f} GB")
        print(f"  Sistema: {mem_percent:.1f}% usado")

        # Latência
        latency = self.metrics.get("latency", {})
        print("\n⏱️  LATÊNCIA:")
        if "code_agent" in latency and "latency_seconds" in latency["code_agent"]:
            code_lat = latency["code_agent"]["latency_seconds"]
            print(f"  CodeAgent: {code_lat:.2f}s")
        if "orchestrator_agent" in latency and "latency_seconds" in latency["orchestrator_agent"]:
            orch_lat = latency["orchestrator_agent"]["latency_seconds"]
            print(f"  OrchestratorAgent: {orch_lat:.2f}s")

        # Qdrant
        qdrant = self.metrics.get("qdrant", {})
        print("\n🗄️  QDRANT:")
        qdrant_avail = qdrant.get("available", False)
        qdrant_cols = len(qdrant.get("collections", []))
        print(f"  Disponível: {qdrant_avail}")
        print(f"  Coleções: {qdrant_cols}")

        # Cache
        cache = self.metrics.get("cache", {})
        print("\n💿 CACHE:")
        if cache.get("neural_response_cache", {}).get("available"):
            stats = cache["neural_response_cache"].get("stats", {})
            hit_rate = stats.get("hit_rate", "N/A")
            print(f"  Neural Response Cache: Hit rate {hit_rate}")

        print("\n" + "=" * 80)


def main():
    """Função principal."""
    collector = BaselineMetricsCollector()
    metrics = collector.collect_all()
    collector.print_summary()

    return metrics


if __name__ == "__main__":
    main()
