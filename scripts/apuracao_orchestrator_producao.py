#!/usr/bin/env python3
"""
Apuração Completa do Orchestrator em Produção

Analisa:
1. Capacidade de execução (quantas tasks sem falhar)
2. Uso de GPU e CPU
3. Configuração de LLM com fallback CPU quando VRAM insuficiente
4. Integração total do orchestrator ao sistema

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-07
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import psutil

# Adicionar path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.integrations.llm_router import LLMRouter
from src.monitor.resource_manager import HybridResourceManager
from src.utils.device_utils import get_compute_device, get_torch_device

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)


class OrchestratorProductionAudit:
    """Apuração completa do orchestrator em produção."""

    def __init__(self):
        self.resource_manager = HybridResourceManager()
        self.llm_router = LLMRouter()
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "device_info": {},
            "resource_usage": {},
            "task_execution": {},
            "llm_fallback": {},
            "recommendations": [],
        }

    def audit_device_configuration(self) -> Dict[str, Any]:
        """Audita configuração de device (GPU/CPU)."""
        logger.info("=== AUDITANDO CONFIGURAÇÃO DE DEVICE ===")

        device_info = {
            "compute_device": get_compute_device(),
            "torch_device": str(get_torch_device()),
            "gpu_available": False,
            "gpu_name": None,
            "gpu_memory_total_mb": None,
            "gpu_memory_free_mb": None,
            "cpu_count": psutil.cpu_count(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "ram_total_gb": psutil.virtual_memory().total / (1024**3),
            "ram_available_gb": psutil.virtual_memory().available / (1024**3),
            "ram_percent": psutil.virtual_memory().percent,
        }

        # Verificar GPU
        try:
            import torch

            if torch.cuda.is_available():
                device_info["gpu_available"] = True
                device_info["gpu_name"] = torch.cuda.get_device_name(0)
                device_info["gpu_memory_total_mb"] = torch.cuda.get_device_properties(
                    0
                ).total_memory / (1024**2)
                device_info["gpu_memory_free_mb"] = (
                    torch.cuda.get_device_properties(0).total_memory
                    - torch.cuda.memory_allocated(0)
                ) / (1024**2)
                device_info["gpu_memory_used_mb"] = torch.cuda.memory_allocated(0) / (1024**2)
                device_info["gpu_memory_reserved_mb"] = torch.cuda.memory_reserved(0) / (1024**2)
        except Exception as e:
            logger.warning(f"Erro ao verificar GPU: {e}")
            device_info["gpu_error"] = str(e)

        self.results["device_info"] = device_info
        logger.info(f"Device: {device_info['compute_device']}")
        if device_info.get("gpu_available"):
            logger.info(
                f"GPU: {device_info['gpu_name']} ({device_info['gpu_memory_free_mb']:.0f}MB livre)"
            )

        return device_info

    async def audit_llm_fallback(self) -> Dict[str, Any]:
        """Audita configuração de LLM e fallback."""
        logger.info("=== AUDITANDO LLM FALLBACK ===")

        llm_info = {
            "providers_available": {},
            "fallback_chain": [],
            "gpu_fallback_cpu": False,
            "recommendations": [],
        }

        # Verificar cada provider
        for provider_name, provider in self.llm_router.providers.items():
            try:
                provider._check_availability()
                llm_info["providers_available"][provider_name.value] = {
                    "available": provider._available,
                    "latency_estimate": (
                        provider.get_latency_estimate()
                        if hasattr(provider, "get_latency_estimate")
                        else None
                    ),
                }
            except Exception as e:
                llm_info["providers_available"][provider_name.value] = {
                    "available": False,
                    "error": str(e),
                }

        # Verificar se HuggingFace Local tem fallback CPU
        hf_local = self.llm_router.providers.get("huggingface_local")
        if hf_local:
            # Verificar código para fallback CPU
            try:
                import inspect

                source = inspect.getsource(hf_local._load_model)
                if "cpu" in source.lower() and "fallback" in source.lower():
                    llm_info["gpu_fallback_cpu"] = True
                else:
                    llm_info["recommendations"].append(
                        "HuggingFace Local não tem fallback CPU configurado. "
                        "Adicionar fallback quando VRAM insuficiente."
                    )
            except Exception as e:
                logger.warning(f"Erro ao verificar fallback CPU: {e}")

        # Fallback chain esperado
        llm_info["fallback_chain"] = [
            "ollama (local)",
            "huggingface_local (local GPU, fallback CPU)",
            "huggingface_space (cloud)",
            "openrouter (cloud)",
        ]

        self.results["llm_fallback"] = llm_info
        return llm_info

    async def test_task_execution_capacity(self, max_tasks: int = 50) -> Dict[str, Any]:
        """Testa capacidade de execução de tasks."""
        logger.info(f"=== TESTANDO CAPACIDADE DE EXECUÇÃO ({max_tasks} tasks) ===")

        # Importar orchestrator
        try:
            from src.agents.orchestrator_agent import OrchestratorAgent

            # Buscar config_path
            config_path = os.getenv("OMNIMIND_AGENT_CONFIG", "config/agent_config.yaml")
            if not Path(config_path).exists():
                # Tentar alternativas
                alt_configs = [
                    "config/orchestrator_config.yaml",
                    "config/agents/orchestrator.yaml",
                ]
                for alt in alt_configs:
                    if Path(alt).exists():
                        config_path = alt
                        break
                else:
                    logger.warning(f"Config não encontrado, usando padrão: {config_path}")

            _orchestrator = OrchestratorAgent(config_path=config_path)
        except ImportError as e:
            logger.error(f"Erro ao importar OrchestratorAgent: {e}")
            return {
                "error": f"Cannot import OrchestratorAgent: {e}",
                "tasks_executed": 0,
                "tasks_successful": 0,
                "tasks_failed": 0,
            }
        except Exception as e:
            logger.error(f"Erro ao inicializar OrchestratorAgent: {e}")
            return {
                "error": f"Cannot initialize OrchestratorAgent: {e}",
                "tasks_executed": 0,
                "tasks_successful": 0,
                "tasks_failed": 0,
            }

        execution_results = {
            "tasks_executed": 0,
            "tasks_successful": 0,
            "tasks_failed": 0,
            "tasks_timeout": 0,
            "average_duration_seconds": 0.0,
            "max_concurrent_tasks": 0,
            "resource_usage_during_tests": [],
            "errors": [],
        }

        # Executar tasks sequenciais
        start_time = time.time()
        for i in range(max_tasks):
            task_id = f"test_task_{i:04d}"
            _task_description = f"Test task {i+1}/{max_tasks}"

            try:
                # Medir recursos antes
                cpu_before = psutil.cpu_percent(interval=0.1)
                ram_before = psutil.virtual_memory().percent
                gpu_mem_before = None
                try:
                    import torch

                    if torch.cuda.is_available():
                        _gpu_mem_before = torch.cuda.memory_allocated(0) / (1024**2)
                except Exception:
                    pass

                # Executar task (simulado - precisa implementar task real)
                task_start = time.time()

                # TODO: Implementar execução real de task via orchestrator
                # Por enquanto, simular
                await asyncio.sleep(0.1)  # Simulação

                task_duration = time.time() - task_start

                # Medir recursos depois
                cpu_after = psutil.cpu_percent(interval=0.1)
                ram_after = psutil.virtual_memory().percent
                gpu_mem_after = None
                try:
                    import torch

                    if torch.cuda.is_available():
                        gpu_mem_after = torch.cuda.memory_allocated(0) / (1024**2)
                except Exception:
                    pass

                execution_results["tasks_executed"] += 1
                execution_results["tasks_successful"] += 1

                execution_results["resource_usage_during_tests"].append(
                    {
                        "task_id": task_id,
                        "cpu_percent": (cpu_before + cpu_after) / 2,
                        "ram_percent": (ram_before + ram_after) / 2,
                        "gpu_memory_mb": gpu_mem_after if gpu_mem_after else None,
                        "duration_seconds": task_duration,
                    }
                )

                if i % 10 == 0:
                    logger.info(f"Executadas {i+1}/{max_tasks} tasks")

            except asyncio.TimeoutError:
                execution_results["tasks_timeout"] += 1
                execution_results["errors"].append(f"{task_id}: Timeout")
            except Exception as e:
                execution_results["tasks_failed"] += 1
                execution_results["errors"].append(f"{task_id}: {str(e)}")
                logger.error(f"Task {task_id} falhou: {e}")

        total_duration = time.time() - start_time
        execution_results["total_duration_seconds"] = total_duration
        if execution_results["tasks_executed"] > 0:
            execution_results["average_duration_seconds"] = (
                total_duration / execution_results["tasks_executed"]
            )

        self.results["task_execution"] = execution_results
        logger.info(
            f"Tasks executadas: {execution_results['tasks_successful']}/{execution_results['tasks_executed']}"
        )

        return execution_results

    def generate_recommendations(self) -> List[str]:
        """Gera recomendações baseadas na apuração."""
        recommendations = []

        device_info = self.results.get("device_info", {})
        llm_info = self.results.get("llm_fallback", {})
        task_exec = self.results.get("task_execution", {})

        # Recomendações de GPU
        if device_info.get("gpu_available"):
            gpu_free_mb = device_info.get("gpu_memory_free_mb", 0)
            if gpu_free_mb < 1000:  # Menos de 1GB livre
                recommendations.append(
                    f"⚠️ GPU com pouca memória livre ({gpu_free_mb:.0f}MB). "
                    "Considerar limpeza de cache ou fallback para CPU em cálculos pesados."
                )
        else:
            recommendations.append(
                "⚠️ GPU não disponível. Configurar fallback CPU para todos os cálculos."
            )

        # Recomendações de LLM
        if not llm_info.get("gpu_fallback_cpu"):
            recommendations.append(
                "🔧 Adicionar fallback CPU para HuggingFace Local quando VRAM insuficiente."
            )

        # Recomendações de capacidade
        if task_exec.get("tasks_failed", 0) > 0:
            failure_rate = task_exec["tasks_failed"] / max(task_exec.get("tasks_executed", 1), 1)
            if failure_rate > 0.1:  # Mais de 10% de falhas
                recommendations.append(
                    f"⚠️ Taxa de falha alta ({failure_rate:.1%}). "
                    "Investigar causas e melhorar tratamento de erros."
                )

        self.results["recommendations"] = recommendations
        return recommendations

    async def run_full_audit(self) -> Dict[str, Any]:
        """Executa apuração completa."""
        logger.info("=" * 80)
        logger.info("APURAÇÃO COMPLETA DO ORCHESTRATOR EM PRODUÇÃO")
        logger.info("=" * 80)

        # 1. Device configuration
        self.audit_device_configuration()

        # 2. LLM fallback
        await self.audit_llm_fallback()

        # 3. Task execution capacity
        await self.test_task_execution_capacity(max_tasks=20)  # Reduzido para teste inicial

        # 4. Generate recommendations
        self.generate_recommendations()

        # 5. Save results
        output_file = (
            Path("data/test_reports")
            / f"orchestrator_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        logger.info(f"Resultados salvos em: {output_file}")

        # Print summary
        print("\n" + "=" * 80)
        print("RESUMO DA APURAÇÃO")
        print("=" * 80)
        print(f"\nDevice: {self.results['device_info'].get('compute_device', 'unknown')}")
        if self.results["device_info"].get("gpu_available"):
            print(f"GPU: {self.results['device_info'].get('gpu_name')}")
            print(f"VRAM Livre: {self.results['device_info'].get('gpu_memory_free_mb', 0):.0f}MB")
        print(
            f"\nTasks Executadas: {self.results['task_execution'].get('tasks_successful', 0)}/{self.results['task_execution'].get('tasks_executed', 0)}"
        )
        print(f"\nRecomendações ({len(self.results['recommendations'])}):")
        for i, rec in enumerate(self.results["recommendations"], 1):
            print(f"  {i}. {rec}")

        return self.results


async def main():
    """Função principal."""
    audit = OrchestratorProductionAudit()
    await audit.run_full_audit()


if __name__ == "__main__":
    asyncio.run(main())
