from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import structlog
import yaml
from .external_ai_providers import ( from .task_isolation import IsolatedTask, TaskIsolationEngine


"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Task Delegation Manager - OmniMind
Gerenciamento de delegação segura de tarefas para provedores externos de IA

Coordena seleção de provedores, isolamento de tarefas e execução distribuída.
"""




    CopilotProvider,
    ExternalAIProvider,
    GeminiProvider,
    OpenRouterProvider,
    TaskResult,
    TaskSpec,
    TaskType,
)

logger = structlog.get_logger(__name__)


@dataclass
class ProviderSelection:
    """Resultado da seleção de provedor"""

    provider_name: str
    model_name: str
    confidence_score: float
    reasoning: str
    estimated_cost: float
    estimated_latency: float


@dataclass
class DelegationResult:
    """Resultado completo da delegação"""

    task_id: str
    success: bool
    provider_used: str
    execution_result: Optional[TaskResult] = None
    selection_reasoning: Optional[str] = None
    isolation_report: Optional[Dict[str, Any]] = None
    total_cost: float = 0.0
    total_latency: float = 0.0
    fallback_used: bool = False


class TaskDelegationManager:
    """
    Gerenciador de delegação de tarefas para provedores externos.

    Coordena seleção inteligente de provedores, isolamento de contexto
    e execução distribuída mantendo segurança e controle.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa gerenciador de delegação.

        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.config = self._load_config(config_path)
        self.providers: Dict[str, ExternalAIProvider] = {}
        self.isolation_engine = TaskIsolationEngine(self.config.get("isolation", {}))
        self.task_history: List[Dict[str, Any]] = []

        # Carrega provedores configurados
        self._initialize_providers()

        logger.info(
            "Task delegation manager initialized",
            providers_count=len(self.providers),
            isolation_level=self.config.get("isolation", {}).get("level"),
        )

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Carrega configuração de provedores externos"""
        if not config_path:
            # Usa caminho padrão
            config_path = "/home/fahbrain/projects/omnimind/config/external_ai_providers.yaml"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error("Failed to load external AI config", error=str(e))
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão mínima"""
        return {
            "providers": {
                "gemini": {"enabled": False},
                "copilot": {"enabled": False},
                "openrouter": {"enabled": False},
            },
            "task_delegation": {"enabled": False},
            "isolation": {"level": "strict"},
        }

    def _initialize_providers(self) -> None:
        """Inicializa provedores configurados"""
        provider_classes = {
            "gemini": GeminiProvider,
            "copilot": CopilotProvider,
            "openrouter": OpenRouterProvider,
        }

        for provider_name, provider_config in self.config.get("providers", {}).items():
            if not provider_config.get("enabled", False):
                continue

            try:
                provider_class = provider_classes.get(provider_name)
                if provider_class:
                    provider = provider_class(provider_config)
                    self.providers[provider_name] = provider
                    logger.info(f"Provider {provider_name} initialized")
                else:
                    logger.warning(f"Unknown provider type: {provider_name}")

            except Exception as e:
                logger.error(f"Failed to initialize provider {provider_name}", error=str(e))

    async def initialize_providers(self) -> None:
        """Inicializa conexões dos provedores"""
        init_tasks = []
        for provider in self.providers.values():
            init_tasks.append(provider.initialize())

        if init_tasks:
            await asyncio.gather(*init_tasks, return_exceptions=True)
            logger.info("All providers initialized")

    async def delegate_task(self, task_spec: Any) -> DelegationResult:
        """
        Delega tarefa para provedor externo apropriado.

        Args:
            task_spec: Especificação da tarefa

        Returns:
            Resultado da delegação
        """
        start_time = time.time()
        task_id = getattr(task_spec, "task_id", "unknown")

        logger.info("Delegating task to external provider", task_id=task_id)

        try:
            # Passo 1: Isola contexto da tarefa
            isolated_task = await self.isolation_engine.isolate_context(task_spec)

            # Passo 2: Seleciona provedor apropriado
            selection = await self._select_provider(isolated_task)

            if not selection:
                return DelegationResult(
                    task_id=task_id,
                    success=False,
                    provider_used="none",
                    selection_reasoning="No suitable provider available",
                )

            # Passo 3: Executa tarefa no provedor selecionado
            execution_result = await self._execute_on_provider(selection, isolated_task)

            # Passo 4: Gera relatório de isolamento
            isolation_report = self.isolation_engine.get_isolation_report(task_spec, isolated_task)

            # Passo 5: Registra resultado
            total_latency = time.time() - start_time
            delegation_result = DelegationResult(
                task_id=task_id,
                success=execution_result.success,
                provider_used=selection.provider_name,
                execution_result=execution_result,
                selection_reasoning=selection.reasoning,
                isolation_report=isolation_report,
                total_cost=execution_result.cost_estimate or 0.0,
                total_latency=total_latency,
                fallback_used=False,
            )

            # Registra no histórico
            self._record_delegation(delegation_result)

            logger.info(
                "Task delegation completed",
                task_id=task_id,
                provider=selection.provider_name,
                success=execution_result.success,
                cost=execution_result.cost_estimate,
                latency=total_latency,
            )

            return delegation_result

        except Exception as e:
            logger.error("Task delegation failed", task_id=task_id, error=str(e))

            return DelegationResult(
                task_id=task_id,
                success=False,
                provider_used="error",
                selection_reasoning=f"Delegation error: {str(e)}",
            )

    async def _select_provider(self, isolated_task: IsolatedTask) -> Optional[ProviderSelection]:
        """
        Seleciona provedor mais apropriado para a tarefa.

        Args:
            isolated_task: Tarefa isolada

        Returns:
            Seleção de provedor ou None se nenhum disponível
        """
        if not self.providers:
            return None

        # Obtém tipo de tarefa
        task_type = self._infer_task_type(isolated_task)

        # Regras de seleção da configuração
        selection_rules = self.config.get("task_delegation", {}).get("provider_selection_rules", {})
        task_rule = selection_rules.get(task_type.value, {})

        # Ordem de prioridade
        priority_order = task_rule.get("priority_order", list(self.providers.keys()))

        # Critérios de seleção
        criteria = self.config.get("task_delegation", {}).get(
            "selection_criteria",
            {"cost_priority": 0.3, "speed_priority": 0.3, "quality_priority": 0.4},
        )

        best_selection = None
        best_score = -1

        for provider_name in priority_order:
            if provider_name not in self.providers:
                continue

            provider = self.providers[provider_name]

            # Verifica se provedor suporta o tipo de tarefa
            capabilities = provider.get_capabilities()
            if task_type not in capabilities.supported_task_types:
                continue

            # Verifica rate limits
            rate_limits = await provider.check_rate_limits()
            if not self._can_use_provider(rate_limits):
                continue

            # Calcula score baseado em critérios
            score = self._calculate_provider_score(provider, task_type, criteria)

            if score > best_score:
                best_score = score

                # Seleciona modelo específico
                model_name = self._select_model_for_provider(provider_name, task_type)

                best_selection = ProviderSelection(
                    provider_name=provider_name,
                    model_name=model_name,
                    confidence_score=score,
                    reasoning=self._generate_selection_reasoning(provider_name, task_type, score),
                    estimated_cost=self._estimate_cost(provider_name, model_name),
                    estimated_latency=self._estimate_latency(provider_name),
                )

        return best_selection

    def _infer_task_type(self, isolated_task: IsolatedTask) -> TaskType:
        """Infere tipo de tarefa baseado no conteúdo"""
        prompt_lower = isolated_task.prompt.lower()

        # Regras simples de inferência
        if any(
            keyword in prompt_lower for keyword in ["código", "code", "função", "function", "class"]
        ):
            if any(
                keyword in prompt_lower for keyword in ["review", "revisar", "analisar", "analyze"]
            ):
                return TaskType.CODE_REVIEW
            else:
                return TaskType.CODE_GENERATION

        elif any(
            keyword in prompt_lower for keyword in ["document", "doc", "readme", "comentário"]
        ):
            return TaskType.DOCUMENTATION

        elif any(
            keyword in prompt_lower
            for keyword in ["analyze", "analisar", "investigar", "investigate"]
        ):
            return TaskType.ANALYSIS

        elif any(
            keyword in prompt_lower for keyword in ["optimize", "otimizar", "melhorar", "improve"]
        ):
            return TaskType.OPTIMIZATION

        elif any(
            keyword in prompt_lower for keyword in ["debug", "depurar", "erro", "error", "fix"]
        ):
            return TaskType.DEBUGGING

        else:
            return TaskType.ANALYSIS  # Default

    def _can_use_provider(self, rate_limits: Dict[str, Any]) -> bool:
        """Verifica se provedor pode ser usado baseado em rate limits"""
        # Lógica simples: verifica se há requests restantes
        requests_remaining = rate_limits.get("requests_remaining", 0)
        return requests_remaining > 0

    def _calculate_provider_score(
        self,
        provider: ExternalAIProvider,
        task_type: TaskType,
        criteria: Dict[str, float],
    ) -> float:
        """Calcula score de adequação do provedor"""
        # Score baseado em histórico de performance
        performance_score = self._get_historical_performance(provider, task_type)

        # Score baseado em custo (inverte, custo menor = score maior)
        cost_score = 1.0 / (1.0 + self._estimate_cost_relative(provider))

        # Score baseado em velocidade (inverte, latência menor = score maior)
        speed_score = 1.0 / (1.0 + self._estimate_latency_relative(provider))

        # Score combinado
        total_score = (
            performance_score * criteria.get("quality_priority", 0.4)
            + cost_score * criteria.get("cost_priority", 0.3)
            + speed_score * criteria.get("speed_priority", 0.3)
        )

        return total_score

    def _get_historical_performance(
        self, provider: ExternalAIProvider, task_type: TaskType
    ) -> float:
        """Obtém performance histórica do provedor para tipo de tarefa"""
        # Busca no histórico
        relevant_history = [
            entry
            for entry in self.task_history
            if (
                entry.get("provider_used") == getattr(provider, "config", {}).get("name", "unknown")
                and entry.get("task_type") == task_type.value
            )
        ]

        if not relevant_history:
            return 0.5  # Score neutro para provedores sem histórico

        # Calcula taxa de sucesso
        success_count = sum(1 for entry in relevant_history if entry.get("success", False))
        return success_count / len(relevant_history)

    def _estimate_cost_relative(self, provider: ExternalAIProvider) -> float:
        """Estima custo relativo do provedor (0-1, menor = melhor)"""
        provider_name = getattr(provider, "config", {}).get("name", "unknown")

        # Custos relativos aproximados (menor = melhor)
        cost_map = {
            "copilot": 0.0,  # Gratuito
            "gemini": 0.3,  # Barato
            "openrouter": 0.7,  # Mais caro
        }

        return cost_map.get(provider_name, 0.5)

    def _estimate_latency_relative(self, provider: ExternalAIProvider) -> float:
        """Estima latência relativa do provedor (0-1, menor = melhor)"""
        provider_name = getattr(provider, "config", {}).get("name", "unknown")

        # Latências relativas aproximadas (menor = melhor)
        latency_map = {
            "copilot": 0.2,  # Rápido
            "gemini": 0.4,  # Médio
            "openrouter": 0.6,  # Mais lento (mais modelos)
        }

        return latency_map.get(provider_name, 0.5)

    def _select_model_for_provider(self, provider_name: str, task_type: TaskType) -> str:
        """Seleciona modelo específico para o provedor e tipo de tarefa"""
        provider_config = self.config.get("providers", {}).get(provider_name, {})
        models = provider_config.get("models", {})

        # Mapeamento de tarefa para modelo
        task_model_map = {
            TaskType.CODE_GENERATION: "code_generation",
            TaskType.CODE_REVIEW: "code_review",
            TaskType.ANALYSIS: "analysis",
            TaskType.DOCUMENTATION: "documentation",
            TaskType.OPTIMIZATION: "optimization",
            TaskType.DEBUGGING: "debugging",
        }

        preferred_model = task_model_map.get(task_type, "default")

        # Retorna modelo preferido ou primeiro disponível
        if preferred_model in models:
            return preferred_model

        return list(models.keys())[0] if models else "default"

    def _generate_selection_reasoning(
        self, provider_name: str, task_type: TaskType, score: float
    ) -> str:
        """Gera explicação para seleção do provedor"""
        return f"Selected {provider_name} for {task_type.value} (score: {score:.2f})"

    def _estimate_cost(self, provider_name: str, model_name: str) -> float:
        """Estima custo por requisição"""
        provider_config = self.config.get("providers", {}).get(provider_name, {})
        models = provider_config.get("models", {})

        if model_name in models:
            model_config = models[model_name]
            # Custo aproximado por 1K tokens
            input_cost = model_config.get("cost_per_1k_input", 0.001)
            output_cost = model_config.get("cost_per_1k_output", 0.005)
            return (input_cost + output_cost) / 2  # Média

        return 0.002  # Custo padrão

    def _estimate_latency(self, provider_name: str) -> float:
        """Estima latência em segundos"""
        latency_map = {"copilot": 2.0, "gemini": 3.0, "openrouter": 4.0}
        return latency_map.get(provider_name, 3.0)

    async def _execute_on_provider(
        self, selection: ProviderSelection, isolated_task: IsolatedTask
    ) -> TaskResult:
        """Executa tarefa no provedor selecionado"""
        provider = self.providers.get(selection.provider_name)

        if not provider:
            return TaskResult(
                task_id=isolated_task.task_id,
                success=False,
                error_message=f"Provider {selection.provider_name} not available",
                provider_used=selection.provider_name,
            )

        # Converte tarefa isolada para TaskSpec
        task_spec = TaskSpec(
            task_id=isolated_task.task_id,
            task_type=self._infer_task_type(isolated_task),
            prompt=isolated_task.prompt,
            context=isolated_task.context,
            files=isolated_task.files,
            metadata=isolated_task.metadata,
        )

        # Executa tarefa
        return await provider.execute_task(task_spec)

    def _record_delegation(self, result: DelegationResult) -> None:
        """Registra delegação no histórico"""
        history_entry = {
            "task_id": result.task_id,
            "provider_used": result.provider_used,
            "success": result.success,
            "cost": result.total_cost,
            "latency": result.total_latency,
            "timestamp": time.time(),
            "fallback_used": result.fallback_used,
        }

        # Adiciona tipo de tarefa se disponível
        if result.execution_result and hasattr(result.execution_result, "task_type"):
            task_type = getattr(result.execution_result, "task_type", None)
            if task_type and hasattr(task_type, "value"):
                history_entry["task_type"] = task_type.value
            elif task_type:
                history_entry["task_type"] = str(task_type)

        self.task_history.append(history_entry)

        # Mantém histórico limitado
        if len(self.task_history) > 1000:
            self.task_history = self.task_history[-500:]  # Mantém últimos 500

    async def get_delegation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de delegação"""
        if not self.task_history:
            return {
                "total_delegations": 0,
                "success_rate": 0.0,
                "provider_usage": {},
                "total_cost": 0.0,
                "average_latency": 0.0,
                "active_providers": list(self.providers.keys()),
            }

        total_delegations = len(self.task_history)
        successful_delegations = sum(
            1 for entry in self.task_history if entry.get("success", False)
        )

        provider_usage = {}
        for entry in self.task_history:
            provider = entry.get("provider_used", "unknown")
            provider_usage[provider] = provider_usage.get(provider, 0) + 1

        total_cost = sum(entry.get("cost", 0) for entry in self.task_history)
        avg_latency = (
            sum(entry.get("latency", 0) for entry in self.task_history) / total_delegations
        )

        return {
            "total_delegations": total_delegations,
            "success_rate": successful_delegations / total_delegations,
            "provider_usage": provider_usage,
            "total_cost": total_cost,
            "average_latency": avg_latency,
            "active_providers": list(self.providers.keys()),
        }

    async def close(self) -> None:
        """Fecha conexões de todos os provedores"""
        close_tasks = []
        for provider in self.providers.values():
            close_tasks.append(provider.close())

        if close_tasks:
            await asyncio.gather(*close_tasks, return_exceptions=True)

        logger.info("Task delegation manager closed")
