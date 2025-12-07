"""
Delegation Manager para Orchestrator.

Responsabilidades:
1. Gerenciar timeout de delegações
2. Proteger contra agentes falhando (circuit breaker)
3. Monitorar heartbeat de agentes
4. Auditar todas as delegações
5. Calcular métricas por agente
"""

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class DelegationStatus(Enum):
    """Status de uma delegação."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    TIMEOUT = "timeout"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CircuitState(Enum):
    """Estados do circuit breaker para agentes."""

    CLOSED = "closed"  # Normal, aceita chamadas
    OPEN = "open"  # Rejeitando chamadas, agente com problema
    HALF_OPEN = "half_open"  # Testando agente


@dataclass
class DelegationRecord:
    """Registro de uma delegação."""

    id: str
    agent_name: str
    task_description: str
    status: DelegationStatus = DelegationStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class AgentMetrics:
    """Métricas de um agente."""

    name: str
    total_delegations: int = 0
    successful_delegations: int = 0
    failed_delegations: int = 0
    timeout_count: int = 0
    average_duration_seconds: float = 0.0
    last_check_time: Optional[str] = None
    circuit_breaker_state: CircuitState = CircuitState.CLOSED
    circuit_failure_count: int = 0
    last_failure_time: Optional[str] = None


class DelegationManager:
    """Gerencia delegações com proteções."""

    def __init__(self, orchestrator, timeout_seconds: float = 30.0):
        """
        Inicializa Delegation Manager.

        Args:
            orchestrator: Instância do OrchestratorAgent
            timeout_seconds: Timeout padrão para delegações
        """
        self.orchestrator = orchestrator
        self.default_timeout = timeout_seconds
        self.delegation_records: List[DelegationRecord] = []
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.circuit_breakers: Dict[str, CircuitState] = {}
        self.circuit_failure_counts: Dict[str, int] = {}
        self.circuit_reset_times: Dict[str, float] = {}
        self.delegation_counter: int = 0

    async def delegate_with_protection(
        self,
        agent_name: str,
        task_description: str,
        task_callable: Callable,
        timeout_seconds: Optional[float] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Delega tarefa com proteções (timeout, circuit breaker, retry).

        Args:
            agent_name: Nome do agente
            task_description: Descrição da tarefa
            task_callable: Função async da tarefa
            timeout_seconds: Timeout customizado (default: self.default_timeout)
            max_retries: Máximo de tentativas

        Returns:
            Resultado da delegação

        Raises:
            TimeoutError: Se tarefa exceder timeout
            RuntimeError: Se circuit breaker está aberto
        """
        timeout = timeout_seconds or self.default_timeout
        delegation_id = f"del_{self.delegation_counter:06d}"
        self.delegation_counter += 1

        # Criar registro
        record = DelegationRecord(
            id=delegation_id,
            agent_name=agent_name,
            task_description=task_description,
            max_retries=max_retries,
        )

        try:
            # 1. Verificar circuit breaker
            if not self._check_circuit_breaker(agent_name):
                error_msg = f"Circuit breaker OPEN for {agent_name}"
                logger.warning(error_msg)
                record.status = DelegationStatus.FAILED
                record.error_message = error_msg
                self._record_delegation(record)
                return {
                    "success": False,
                    "error": error_msg,
                    "delegation_id": delegation_id,
                    "status": "failed",
                }

            # 2. Executar com retry
            for attempt in range(max_retries):
                try:
                    logger.info(
                        f"Delegating {delegation_id} to {agent_name} "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )

                    record.retry_count = attempt
                    record.status = DelegationStatus.RUNNING
                    record.started_at = datetime.now().isoformat()

                    # 3. Executar com timeout
                    result = await asyncio.wait_for(task_callable(), timeout=timeout)

                    # Sucesso!
                    record.status = DelegationStatus.SUCCESS
                    record.result = result
                    record.completed_at = datetime.now().isoformat()
                    record.duration_seconds = self._calculate_duration(record)

                    # Limpar falhas
                    self._reset_circuit_breaker_on_success(agent_name)

                    logger.info(
                        f"✅ Delegation {delegation_id} completed "
                        f"in {record.duration_seconds:.2f}s"
                    )

                    self._record_delegation(record)
                    self._update_metrics(record)
                    return result

                except asyncio.TimeoutError:
                    logger.warning(
                        f"⏱️ Timeout for {delegation_id} " f"(attempt {attempt + 1}/{max_retries})"
                    )
                    record.status = DelegationStatus.TIMEOUT
                    record.error_message = "Task timeout"

                    # Incrementar falhas no circuit breaker
                    self._record_circuit_breaker_failure(agent_name)

                    if attempt < max_retries - 1:
                        # Backoff exponencial com jitter
                        base_delay = 1.0
                        exponential_delay = base_delay * (2**attempt)
                        jitter = random.uniform(0, exponential_delay * 0.1)  # 10% de jitter
                        delay = exponential_delay + jitter
                        logger.debug(
                            f"Backoff exponencial: tentativa {attempt + 1}, "
                            f"delay={delay:.2f}s (base={exponential_delay:.2f}s, "
                            f"jitter={jitter:.2f}s)"
                        )
                        await asyncio.sleep(delay)
                        continue
                    else:
                        # Última tentativa falhou, retornar erro
                        record.completed_at = datetime.now().isoformat()
                        record.duration_seconds = self._calculate_duration(record)
                        self._record_delegation(record)
                        self._update_metrics(record)
                        return {
                            "success": False,
                            "error": "Task timeout",
                            "delegation_id": delegation_id,
                            "status": "timeout",
                        }

                except Exception as e:
                    logger.error(f"❌ Error in delegation {delegation_id}: {e}")

                    # Analisar erro estruturalmente se ErrorAnalyzer disponível
                    if (
                        hasattr(self.orchestrator, "error_analyzer")
                        and self.orchestrator.error_analyzer
                    ):
                        try:
                            context = {
                                "agent_name": agent_name,
                                "task_description": task_description,
                                "delegation_id": delegation_id,
                                "retry_count": record.retry_count,
                            }
                            error_analysis = self.orchestrator.error_analyzer.analyze_error(
                                e, context
                            )
                            logger.info(
                                f"Erro de delegação analisado: "
                                f"{error_analysis.error_type.value} → "
                                f"{error_analysis.recovery_strategy.value} "
                                f"(confiança: {error_analysis.confidence:.2f})"
                            )

                            # Aprender da solução se aplicável
                            if record.retry_count < record.max_retries:
                                # Tentar estratégia sugerida
                                logger.debug(f"Ações sugeridas: {error_analysis.suggested_actions}")
                        except Exception as analysis_error:
                            logger.warning(f"Erro ao analisar erro de delegação: {analysis_error}")
                    record.status = DelegationStatus.FAILED
                    record.error_message = str(e)

                    # Incrementar falhas no circuit breaker
                    self._record_circuit_breaker_failure(agent_name)

                    if attempt < max_retries - 1:
                        # Backoff exponencial com jitter
                        base_delay = 0.5
                        exponential_delay = base_delay * (2**attempt)
                        jitter = random.uniform(0, exponential_delay * 0.1)  # 10% de jitter
                        delay = exponential_delay + jitter
                        logger.debug(
                            f"Backoff exponencial: tentativa {attempt + 1}, "
                            f"delay={delay:.2f}s (base={exponential_delay:.2f}s, "
                            f"jitter={jitter:.2f}s)"
                        )
                        await asyncio.sleep(delay)
                        continue
                    else:
                        # Última tentativa falhou, retornar erro
                        record.completed_at = datetime.now().isoformat()
                        record.duration_seconds = self._calculate_duration(record)
                        self._record_delegation(record)
                        self._update_metrics(record)
                        return {
                            "success": False,
                            "error": str(e),
                            "delegation_id": delegation_id,
                            "status": "failed",
                        }

            # Fallback: se loop terminou sem retornar (não deveria acontecer)
            logger.error(
                f"⚠️ Loop de retry terminou sem retorno para {delegation_id}. "
                f"Isso não deveria acontecer."
            )
            record.status = DelegationStatus.FAILED
            record.error_message = "All retry attempts exhausted without return"
            record.completed_at = datetime.now().isoformat()
            record.duration_seconds = self._calculate_duration(record)
            self._record_delegation(record)
            self._update_metrics(record)
            return {
                "success": False,
                "error": "All retry attempts exhausted without return",
                "delegation_id": delegation_id,
                "status": "failed",
            }

        except Exception as e:
            record.status = DelegationStatus.FAILED
            record.error_message = str(e)
            record.completed_at = datetime.now().isoformat()
            record.duration_seconds = self._calculate_duration(record)
            self._record_delegation(record)
            self._update_metrics(record)
            # Retornar resultado de falha em vez de apenas raise
            return {
                "success": False,
                "error": str(e),
                "delegation_id": delegation_id,
                "status": "failed",
            }

    def _check_circuit_breaker(self, agent_name: str) -> bool:
        """Verifica se circuit breaker permite chamada."""
        if agent_name not in self.circuit_breakers:
            self.circuit_breakers[agent_name] = CircuitState.CLOSED
            self.circuit_failure_counts[agent_name] = 0
            return True

        state = self.circuit_breakers[agent_name]

        # Se CLOSED, permite
        if state == CircuitState.CLOSED:
            return True

        # Se OPEN, verificar se tempo de reset
        if state == CircuitState.OPEN:
            last_failure = self.circuit_reset_times.get(agent_name, 0)
            if time.time() - last_failure > 60.0:  # 1 minuto
                logger.info(f"Circuit breaker HALF_OPEN for {agent_name}, testing...")
                self.circuit_breakers[agent_name] = CircuitState.HALF_OPEN
                return True
            return False

        # Se HALF_OPEN, permite teste
        if state == CircuitState.HALF_OPEN:
            return True

        return False

    def _record_circuit_breaker_failure(self, agent_name: str):
        """Registra falha para circuit breaker."""
        if agent_name not in self.circuit_failure_counts:
            self.circuit_failure_counts[agent_name] = 0

        self.circuit_failure_counts[agent_name] += 1
        self.circuit_reset_times[agent_name] = time.time()

        # Se 3 falhas consecutivas, abrir circuit
        if self.circuit_failure_counts[agent_name] >= 3:
            logger.warning(
                f"🔴 Circuit breaker OPEN for {agent_name} "
                f"({self.circuit_failure_counts[agent_name]} failures)"
            )
            self.circuit_breakers[agent_name] = CircuitState.OPEN

    def _reset_circuit_breaker_on_success(self, agent_name: str):
        """Reseta circuit breaker após sucesso."""
        if self.circuit_breakers.get(agent_name) == CircuitState.HALF_OPEN:
            logger.info(f"✅ Circuit breaker CLOSED for {agent_name}")
            self.circuit_breakers[agent_name] = CircuitState.CLOSED
            self.circuit_failure_counts[agent_name] = 0

    def _record_delegation(self, record: DelegationRecord):
        """Registra delegação."""
        self.delegation_records.append(record)

        # Salvar em arquivo
        try:
            with open("logs/delegations.jsonl", "a") as f:
                record_dict = {
                    "id": record.id,
                    "agent": record.agent_name,
                    "task": record.task_description,
                    "status": record.status.value,
                    "duration_seconds": record.duration_seconds,
                    "created_at": record.created_at,
                }
                f.write(json.dumps(record_dict) + "\n")
        except Exception as e:
            logger.error(f"Error saving delegation record: {e}")

    def _update_metrics(self, record: DelegationRecord):
        """Atualiza métricas do agente."""
        agent_name = record.agent_name

        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = AgentMetrics(name=agent_name)

        metrics = self.agent_metrics[agent_name]
        metrics.total_delegations += 1
        metrics.last_check_time = datetime.now().isoformat()

        if record.status == DelegationStatus.SUCCESS:
            metrics.successful_delegations += 1
            # Atualizar média de duração
            total_duration = (
                metrics.average_duration_seconds * (metrics.successful_delegations - 1)
                + record.duration_seconds
            )
            metrics.average_duration_seconds = total_duration / metrics.successful_delegations

        elif record.status == DelegationStatus.TIMEOUT:
            metrics.timeout_count += 1
            metrics.failed_delegations += 1
            metrics.last_failure_time = datetime.now().isoformat()

        elif record.status == DelegationStatus.FAILED:
            metrics.failed_delegations += 1
            metrics.last_failure_time = datetime.now().isoformat()

        # Atualizar estado do circuit breaker
        metrics.circuit_breaker_state = self.circuit_breakers.get(agent_name, CircuitState.CLOSED)
        metrics.circuit_failure_count = self.circuit_failure_counts.get(agent_name, 0)

    def _calculate_duration(self, record: DelegationRecord) -> float:
        """Calcula duração da delegação."""
        if record.started_at and record.completed_at:
            start = datetime.fromisoformat(record.started_at)
            end = datetime.fromisoformat(record.completed_at)
            return (end - start).total_seconds()
        return 0.0

    def get_metrics(self, agent_name: Optional[str] = None) -> Dict[str, AgentMetrics]:
        """Retorna métricas."""
        if agent_name:
            return {agent_name: self.agent_metrics.get(agent_name, AgentMetrics(name=agent_name))}
        return self.agent_metrics

    def get_recent_delegations(self, limit: int = 10) -> List[DelegationRecord]:
        """Retorna delegações recentes."""
        return self.delegation_records[-limit:]

    def get_failed_delegations(self) -> List[DelegationRecord]:
        """Retorna delegações que falharam."""
        return [
            r
            for r in self.delegation_records
            if r.status in [DelegationStatus.FAILED, DelegationStatus.TIMEOUT]
        ]


class HeartbeatMonitor:
    """Monitora heartbeat de agentes."""

    def __init__(self, orchestrator, check_interval_seconds: float = 30.0):
        """
        Inicializa Heartbeat Monitor.

        Args:
            orchestrator: Instância do OrchestratorAgent
            check_interval_seconds: Intervalo entre checks
        """
        self.orchestrator = orchestrator
        self.check_interval = check_interval_seconds
        self.agent_health: Dict[str, bool] = {}
        self.last_check_time: Dict[str, float] = {}

    async def start_monitoring(self):
        """Inicia monitoramento contínuo."""
        logger.info("Starting heartbeat monitoring...")

        while True:
            try:
                await self._check_all_agents()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in heartbeat monitoring: {e}")
                await asyncio.sleep(self.check_interval)

    async def _check_all_agents(self):
        """Verifica saúde de todos os agentes."""
        try:
            # Usar AgentRegistry se disponível
            if hasattr(self.orchestrator, "registry"):
                health_results = await self.orchestrator.registry.health_check_all()
                self.agent_health.update(health_results)

                # Atualizar tempos de check
                for agent_name in health_results:
                    self.last_check_time[agent_name] = time.time()

                # Log de agentes não saudáveis
                unhealthy = [name for name, healthy in health_results.items() if not healthy]
                if unhealthy:
                    logger.warning(f"⚠️ Unhealthy agents detected: {', '.join(unhealthy)}")

        except Exception as e:
            logger.error(f"Error checking agent health: {e}")

    async def get_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde dos agentes."""
        return {
            "agent_health": self.agent_health,
            "last_check_time": {
                name: datetime.fromtimestamp(t).isoformat()
                for name, t in self.last_check_time.items()
            },
            "timestamp": datetime.now().isoformat(),
        }

    def is_agent_healthy(self, agent_name: str) -> bool:
        """Verifica se agente está saudável."""
        return self.agent_health.get(agent_name, True)
