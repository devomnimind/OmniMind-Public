"""
CircuitBreaker - Proteção contra cascata de falhas em delegação de agentes.

Implementa recomendações da Seção 7 da AUDITORIA_ORCHESTRATOR_COMPLETA.md:
- Timeout para agentes que não respondem
- Circuit breaker para agentes falhando
- Proteção contra cascata de falhas
"""

from __future__ import annotations

import asyncio
import logging
import time
from enum import Enum
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Estados do circuit breaker."""

    CLOSED = "closed"  # Funcionando normalmente
    OPEN = "open"  # Circuito aberto, bloqueando chamadas
    HALF_OPEN = "half_open"  # Teste de recuperação


class CircuitBreakerOpen(Exception):
    """Exceção lançada quando circuit breaker está aberto."""


class AgentCircuitBreaker:
    """Circuit breaker para proteção de chamadas a agentes."""

    def __init__(
        self,
        failure_threshold: int = 3,
        timeout: float = 30.0,
        recovery_timeout: float = 60.0,
    ) -> None:
        """Inicializa circuit breaker.

        Args:
            failure_threshold: Número de falhas antes de abrir circuito
            timeout: Timeout em segundos para chamadas
            recovery_timeout: Tempo em segundos antes de tentar recuperação
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.recovery_timeout = recovery_timeout

        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time: Optional[float] = None
        self.last_success_time: Optional[float] = None

    def is_available(self) -> bool:
        """Verifica se circuito está disponível para chamadas.

        Returns:
            True se pode fazer chamadas, False caso contrário
        """
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Verificar se passou tempo suficiente para tentar recuperação
            if (
                self.last_failure_time
                and time.time() - self.last_failure_time >= self.recovery_timeout
            ):
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entrando em modo HALF_OPEN para teste")
                return True
            return False

        # HALF_OPEN - permitir uma tentativa
        return True

    def record_success(self) -> None:
        """Registra sucesso na chamada."""
        self.failure_count = 0
        self.last_success_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            logger.info("Circuit breaker fechado após sucesso em HALF_OPEN")

    def record_failure(self) -> None:
        """Registra falha na chamada."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                "Circuit breaker ABERTO após %d falhas consecutivas",
                self.failure_count,
            )

        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker voltou para OPEN após falha em HALF_OPEN")

    async def call_with_protection(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        """Executa função com proteção de circuit breaker e timeout.

        Args:
            func: Função a executar (pode ser async ou sync)
            args: Argumentos posicionais
            kwargs: Argumentos nomeados

        Returns:
            Resultado da função

        Raises:
            CircuitBreakerOpen: Se circuito está aberto
            asyncio.TimeoutError: Se função excedeu timeout
        """
        if not self.is_available():
            raise CircuitBreakerOpen(
                f"Circuit breaker está {self.state.value}, bloqueando chamadas"
            )

        try:
            # Executar com timeout
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(func(*args, **kwargs), timeout=self.timeout)
            else:
                # Função síncrona - executar em thread pool
                result = await asyncio.wait_for(
                    asyncio.to_thread(func, *args, **kwargs), timeout=self.timeout
                )

            self.record_success()
            return result

        except asyncio.TimeoutError:
            logger.error("Chamada excedeu timeout de %s segundos", self.timeout)
            self.record_failure()
            raise

        except Exception as e:
            logger.error("Falha na chamada: %s", e)
            self.record_failure()
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do circuit breaker.

        Returns:
            Dicionário com estatísticas
        """
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "timeout": self.timeout,
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
        }

    def reset(self) -> None:
        """Reseta circuit breaker para estado inicial."""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        logger.info("Circuit breaker resetado")
