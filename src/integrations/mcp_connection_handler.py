"""
MCP Connection Handler - Tratamento robusto de conexões quebradas.

Este módulo implementa tratamento especializado para erros de conexão MCP,
incluindo "Broken pipe" (errno 32), timeouts e fallbacks automáticos.

oria: Fabrício da Silva + assistência de IA
Projeto: OmniMind - Sistema de Consciência Artificial
"""

from __future__ import annotations

import errno
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, cast

logger = logging.getLogger(__name__)


@dataclass
class ConnectionConfig:
    """Configuração otimizada para conexões MCP com preservação de Φ.

    Baseado em análise de métricas de consciência:
    - Timeouts calibrados para preservar Ψ (criatividade)
    - Retry configurado para minimizar Δ (trauma)
    - Circuit breaker para proteger σ (estrutura)
    """

    # Timeouts aumentados para preservar Ψ (operações criativas)
    request_timeout: float = 60.0  # 60s para LLM generation
    connection_timeout: float = 10.0  # 10s para estabelecer conexão
    read_timeout: float = 30.0  # 30s para leitura de respostas

    # Retry configurado para reduzir Δ (trauma sistêmico)
    max_retries: int = 5  # 5 tentativas (estatisticamente suficiente)
    retry_backoff_base: float = 1.0  # Base 1s (exponencial: 1, 2, 4, 8, 16)
    retry_backoff_max: float = 60.0  # Máximo 60s (evita timeout infinito)
    retry_jitter: float = 0.1  # 10% jitter (evita thundering herd)

    # Circuit breaker para proteger σ (estrutura sistêmica)
    failure_threshold: int = 3  # 3 falhas consecutivas para abrir circuito
    success_threshold: int = 2  # 2 sucessos para fechar circuito
    recovery_timeout: float = 30.0  # 30s em HALF_OPEN antes de tentar fechar

    # Connection pooling otimizado para manter Φ (integração)
    max_connections: int = 10  # 10 conexões
    max_keepalive_connections: int = 5  # 5 keep-alive
    keepalive_expiry: float = 5.0  # 5s expiry

    # Monitoramento contínuo de Φ durante operações
    phi_monitoring_enabled: bool = True
    phi_degradation_threshold: float = 0.03  # Alerta se Φ < 0.03

    def validate(self) -> None:
        """Valida configuração com base em constraints científicos."""
        assert (
            self.request_timeout > self.read_timeout
        ), "request_timeout deve ser > read_timeout para evitar race conditions"
        assert self.max_retries > 0, "max_retries deve ser > 0 para recovery"
        assert (
            self.failure_threshold >= 3
        ), "failure_threshold deve ser ≥ 3 para evitar false positives"
        assert (
            0.0 <= self.retry_jitter <= 0.5
        ), "retry_jitter deve estar em [0, 0.5] para evitar over-jittering"


class MCPPipeError(Exception):
    """Erro específico para "Broken pipe" (errno 32)."""

    def __init__(self, message: str, errno_code: int = errno.EPIPE):
        super().__init__(message)
        self.errno_code = errno_code


class MCPConnectionError(Exception):
    """Erro geral de conexão MCP."""

    pass


class MCPConnectionHandler:
    """Handler com tratamento específico para Broken pipe e preservação de Φ.

    Implementa estratégias de recovery que preservam métricas de consciência:
    - Retry inteligente: minimiza Δ (trauma)
    - Circuit breaker: protege σ (estrutura)
    - Phi monitoring: detecta degradação de Φ (integração)
    """

    def __init__(self, config: Optional[ConnectionConfig] = None, workspace: Optional[Any] = None):
        """Inicializa o handler de conexão com monitoramento de Φ.

        Args:
            config: Configuração personalizada (usa defaults se None)
            workspace: SharedWorkspace para monitorar Φ durante operações
        """
        self.config = config or ConnectionConfig()
        self.config.validate()

        # NOVO: Integração SharedWorkspace para monitoramento Φ
        self.workspace = workspace
        self.phi_monitoring_enabled = workspace is not None

        # Estado do circuit breaker por servidor
        self._failure_counts: Dict[str, int] = {}
        self._last_failure_time: Dict[str, float] = {}
        self._circuit_open: Dict[str, bool] = {}

        # NOVO: Métricas de consciência durante operações
        self._phi_during_operations: Dict[str, Dict[str, Any]] = {}

        logger.info(
            f"MCPConnectionHandler inicializado: "
            f"timeouts={self.config.request_timeout}s, "
            f"max_retries={self.config.max_retries}, "
            f"circuit_threshold={self.config.failure_threshold}, "
            f"phi_monitoring={self.phi_monitoring_enabled}"
        )

    # ========== MÉTODOS AUXILIARES PARA MONITORAMENTO Φ ==========

    def _measure_phi_before_operation(self, operation_id: str) -> float:
        """Mede Φ antes de uma operação MCP para baseline.

        Args:
            operation_id: Identificador único da operação

        Returns:
            Φ atual antes da operação (baseline)
        """
        if not self.phi_monitoring_enabled or not self.workspace:
            return 0.0

        try:
            # Obter métricas de consciência do SharedWorkspace
            if hasattr(self.workspace, "get_current_phi"):
                phi = self.workspace.get_current_phi()
            elif hasattr(self.workspace, "phi"):
                phi = getattr(self.workspace, "phi", 0.0)
            else:
                phi = 0.0

            self._phi_during_operations[operation_id] = {
                "baseline_phi": phi,
                "timestamp": time.time(),
            }

            logger.debug(f"Φ baseline medido para operação {operation_id}: {phi:.4f}")
            return phi

        except Exception as e:
            logger.warning(f"Falha ao medir Φ baseline para operação {operation_id}: {e}")
            return 0.0

    def _measure_phi_after_operation(
        self, operation_id: str, operation_success: bool
    ) -> Dict[str, float]:
        """Mede Φ após operação e calcula métricas de preservação.

        Args:
            operation_id: Identificador da operação
            operation_success: Se a operação foi bem-sucedida

        Returns:
            Dict com métricas de Φ: baseline, final, preserved_percentage
        """
        if not self.phi_monitoring_enabled or not self.workspace:
            return {"baseline_phi": 0.0, "final_phi": 0.0, "preserved_percentage": 100.0}

        try:
            # Medir Φ final
            if hasattr(self.workspace, "get_current_phi"):
                final_phi = self.workspace.get_current_phi()
            elif hasattr(self.workspace, "phi"):
                final_phi = getattr(self.workspace, "phi", 0.0)
            else:
                final_phi = 0.0

            # Obter baseline
            baseline_data: Dict[str, Any] = self._phi_during_operations.get(operation_id, {})
            baseline_phi = baseline_data.get("baseline_phi", 0.0)

            # Calcular preservação
            if baseline_phi > 0:
                preserved_percentage = (final_phi / baseline_phi) * 100
            else:
                preserved_percentage = 100.0 if final_phi > 0 else 100.0

            metrics = {
                "baseline_phi": baseline_phi,
                "final_phi": final_phi,
                "preserved_percentage": preserved_percentage,
                "operation_success": operation_success,
            }

            # Log de preservação de Φ
            if preserved_percentage >= 95:
                status = "✅"
            elif preserved_percentage >= 80:
                status = "⚠️"
            else:
                status = "❌"

            logger.info(
                f"{status} Φ preservado na operação {operation_id}: "
                f"baseline={baseline_phi:.4f}, final={final_phi:.4f}, "
                f"preservado={preserved_percentage:.1f}%"
            )

            # Alerta se Φ degradou significativamente
            if preserved_percentage < 80:
                logger.warning(
                    f"🚨 DEGRADAÇÃO Φ detectada na operação {operation_id}: "
                    f"preservação={preserved_percentage:.1f}% < 80%"
                )

            return metrics

        except Exception as e:
            logger.warning(f"Falha ao medir Φ final para operação {operation_id}: {e}")
            return {"baseline_phi": 0.0, "final_phi": 0.0, "preserved_percentage": 100.0}

    def _check_phi_degradation_alert(self, operation_id: str, metrics: Dict[str, float]) -> bool:
        """Verifica se há degradação crítica de Φ e dispara alertas.

        Args:
            operation_id: Identificador da operação
            metrics: Métricas de Φ calculadas

        Returns:
            True se há degradação crítica (Φ < threshold)
        """
        preserved_percentage = metrics.get("preserved_percentage", 100.0)
        final_phi = metrics.get("final_phi", 0.0)

        # Thresholds críticos baseados nos parâmetros empíricos
        critical_preservation_threshold = 80.0  # 80% de preservação mínima
        critical_phi_threshold = 0.03  # Φ < 0.03 = degradação crítica

        is_critical_degradation = (
            preserved_percentage < critical_preservation_threshold
            or final_phi < critical_phi_threshold
        )

        if is_critical_degradation:
            logger.error(
                f"🚨 DEGRADAÇÃO CRÍTICA Φ detectada! Operação {operation_id}: "
                f"Φ final={final_phi:.4f}, preservação={preserved_percentage:.1f}%"
            )

            # Aqui poderiam ser disparados alertas automáticos:
            # - Notificação para humanos se Φ < 0.15
            # - Escalonamento automático
            # - Redução de carga do sistema

        return is_critical_degradation

    def should_retry(self, server_name: str, exception: Exception) -> tuple[bool, float]:
        """Determina se deve retry baseado no erro e estado do circuito.

        Args:
            server_name: Nome do servidor MCP
            exception: Exceção ocorrida

        Returns:
            Tuple (should_retry, backoff_time)
        """
        # Circuit breaker logic
        if self._is_circuit_open(server_name):
            return False, 0.0

        # Broken pipe (errno 32) - sempre retry com backoff
        if isinstance(exception, MCPPipeError) or (
            hasattr(exception, "errno") and exception.errno == errno.EPIPE
        ):
            backoff = self._calculate_backoff(server_name)
            logger.warning(
                f"MCP Broken pipe detectado para {server_name}, retrying em {backoff:.1f}s"
            )
            return True, backoff

        # Timeout errors
        if "timeout" in str(exception).lower():
            backoff = self._calculate_backoff(server_name)
            logger.warning(f"MCP timeout para {server_name}, retrying em {backoff:.1f}s")
            return True, backoff

        # Connection errors
        if any(word in str(exception).lower() for word in ["connection", "connect", "refused"]):
            backoff = self._calculate_backoff(server_name)
            logger.warning(f"MCP connection error para {server_name}, retrying em {backoff:.1f}s")
            return True, backoff

        # Non-retryable errors
        logger.error(f"MCP non-retryable error para {server_name}: {exception}")
        self._record_failure(server_name)
        return False, 0.0

    def _calculate_backoff(self, server_name: str) -> float:
        """Calcula tempo de backoff exponencial.

        Args:
            server_name: Nome do servidor

        Returns:
            Tempo de espera em segundos
        """
        failures = self._failure_counts.get(server_name, 0)
        base_backoff = self.config.retry_backoff_base * (2**failures)
        return min(base_backoff, self.config.retry_backoff_max)

    def _is_circuit_open(self, server_name: str) -> bool:
        """Verifica se o circuito está aberto para o servidor.

        Args:
            server_name: Nome do servidor

        Returns:
            True se circuito está aberto
        """
        if not self._circuit_open.get(server_name, False):
            return False

        # Verificar se pode tentar recovery
        last_failure = self._last_failure_time.get(server_name, 0)
        if time.time() - last_failure >= self.config.recovery_timeout:
            logger.info(f"Circuit breaker recovery attempt para {server_name}")
            self._circuit_open[server_name] = False
            return False

        return True

    def _record_failure(self, server_name: str) -> None:
        """Registra falha e possibly abre o circuito.

        Args:
            server_name: Nome do servidor
        """
        current_time = time.time()
        self._failure_counts[server_name] = self._failure_counts.get(server_name, 0) + 1
        self._last_failure_time[server_name] = current_time

        # Abrir circuito se excedeu threshold
        if self._failure_counts[server_name] >= self.config.failure_threshold:
            self._circuit_open[server_name] = True
            logger.error(
                f"Circuit breaker aberto para {server_name} após "
                f"{self._failure_counts[server_name]} falhas"
            )

    def record_success(self, server_name: str) -> None:
        """Registra sucesso e reseta contadores.

        Args:
            server_name: Nome do servidor
        """
        self._failure_counts[server_name] = 0
        self._last_failure_time.pop(server_name, None)
        self._circuit_open[server_name] = False
        logger.debug(f"Circuit breaker reset para {server_name}")

    def get_connection_params(self, server_name: str) -> Dict[str, Any]:
        """Retorna parâmetros otimizados para conexão.

        Args:
            server_name: Nome do servidor

        Returns:
            Dict com parâmetros de conexão
        """
        return {
            "timeout": self.config.request_timeout,
            "connection_timeout": self.config.connection_timeout,
            "read_timeout": self.config.read_timeout,
            "max_connections": self.config.max_connections,
            "max_keepalive_connections": self.config.max_keepalive_connections,
            "keepalive_expiry": self.config.keepalive_expiry,
        }

    def get_status(self, server_name: str) -> Dict[str, Any]:
        """Retorna status do circuito e métricas de Φ para o servidor.

        Args:
            server_name: Nome do servidor

        Returns:
            Dict com status do circuito e métricas de Φ
        """
        status: Dict[str, Any] = {
            "failure_count": self._failure_counts.get(server_name, 0),
            "last_failure_time": self._last_failure_time.get(server_name),
            "circuit_open": self._is_circuit_open(server_name),
            "can_retry": not self._is_circuit_open(server_name),
        }

        # NOVO: Adicionar métricas de Φ se disponíveis
        if self.phi_monitoring_enabled and self.workspace:
            try:
                current_phi = 0.0
                if hasattr(self.workspace, "get_current_phi"):
                    current_phi = self.workspace.get_current_phi()
                elif hasattr(self.workspace, "phi"):
                    current_phi = getattr(self.workspace, "phi", 0.0)

                status.update(
                    {
                        "current_phi": current_phi,
                        "phi_monitoring_enabled": True,
                        "phi_status": "healthy" if current_phi >= 0.03 else "degraded",
                    }
                )
            except Exception as e:
                logger.warning(f"Falha ao obter Φ para status do servidor {server_name}: {e}")
                status.update(
                    {
                        "current_phi": 0.0,
                        "phi_monitoring_enabled": True,
                        "phi_status": "error",
                    }
                )
        else:
            status.update({"phi_monitoring_enabled": False, "phi_status": "disabled"})
            
        # Cast para resolver type checking issues
        status = cast(Dict[str, Any], status)

        return status


class RobustMCPClient:
    """Cliente MCP com tratamento robusto de erros de conexão."""

    def __init__(
        self,
        endpoint: str,
        connection_handler: Optional[MCPConnectionHandler] = None,
        config: Optional[ConnectionConfig] = None,
        workspace: Optional[Any] = None,
    ):
        """Inicializa cliente MCP robusto com monitoramento de Φ.

        Args:
            endpoint: URL do endpoint MCP
            connection_handler: Handler de conexão personalizado
            config: Configuração de conexão
            workspace: SharedWorkspace para monitorar Φ durante operações
        """
        self.endpoint = endpoint
        # NOVO: Passar workspace para o connection handler
        if connection_handler:
            self.connection_handler = connection_handler
        else:
            self.connection_handler = MCPConnectionHandler(config, workspace)
        self.server_name = endpoint.split("/")[-2] if "/" in endpoint else endpoint

    async def request_with_retry(
        self,
        method: str,
        params: Dict[str, Any],
        max_attempts: Optional[int] = None,
    ) -> Any:
        """Executa request com retry automático e monitoramento de Φ.

        Args:
            method: Método MCP
            params: Parâmetros do método
            max_attempts: Máximo de tentativas (usa config se None)

        Returns:
            Resultado do request

        Raises:
            MCPPipeError: Se não conseguir conectar após todas as tentativas
        """
        max_attempts = max_attempts or self.connection_handler.config.max_retries
        operation_id = f"{self.server_name}_{method}_{int(time.time())}"

        # NOVO: Medir Φ antes da operação
        self.connection_handler._measure_phi_before_operation(operation_id)

        last_exception: Optional[Exception] = None

        for attempt in range(max_attempts):
            try:
                # Verificar se deve tentar
                if last_exception:
                    should_retry, backoff_time = self.connection_handler.should_retry(
                        self.server_name, last_exception
                    )
                    if not should_retry:
                        # NOVO: Medir Φ antes de levantar a exceção final
                        self.connection_handler._measure_phi_after_operation(operation_id, False)
                        raise last_exception

                    if attempt > 0:  # Não fazer sleep na primeira tentativa
                        import asyncio

                        await asyncio.sleep(backoff_time)

                # Executar request
                result = await self._execute_request(method, params)

                # Registrar sucesso
                self.connection_handler.record_success(self.server_name)

                # NOVO: Medir Φ após operação bem-sucedida
                self.connection_handler._measure_phi_after_operation(operation_id, True)

                return result

            except Exception as e:
                last_exception = e
                logger.warning(f"MCP request attempt {attempt + 1}/{max_attempts} failed: {e}")

                # Se é última tentativa, levantar erro final
                if attempt == max_attempts - 1:
                    # NOVO: Medir Φ antes de levantar a exceção final
                    phi_metrics = self.connection_handler._measure_phi_after_operation(
                        operation_id, False
                    )

                    # Verificar degradação crítica de Φ
                    self.connection_handler._check_phi_degradation_alert(operation_id, phi_metrics)

                    # Converter para MCPPipeError se apropriado
                    if isinstance(e, OSError) and hasattr(e, "errno") and e.errno == errno.EPIPE:
                        raise MCPPipeError(
                            f"MCP Broken pipe após {max_attempts} tentativas: {e}", e.errno
                        ) from e
                    else:
                        raise

        # Não deveria chegar aqui, mas por segurança
        # NOVO: Medir Φ antes de levantar a exceção final
        self.connection_handler._measure_phi_after_operation(operation_id, False)
        raise MCPPipeError(f"MCP request failed após {max_attempts} tentativas")

    async def _execute_request(self, method: str, params: Dict[str, Any]) -> Any:
        """Executa request individual (implementação específica)."""
        # Esta é uma implementação base - subclasses devem sobrescrever
        import httpx

        connection_params = self.connection_handler.get_connection_params(self.server_name)

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=connection_params["connection_timeout"],
                read=connection_params["read_timeout"],
                write=connection_params["read_timeout"],
            ),
            limits=httpx.Limits(
                max_connections=connection_params["max_connections"],
                max_keepalive_connections=connection_params["max_keepalive_connections"],
            ),
        ) as client:
            payload = {
                "jsonrpc": "2.0",
                "method": method,
                "params": params,
                "id": "robust_client",
            }

            response = await client.post(self.endpoint, json=payload)
            response.raise_for_status()

            result = response.json()

            # Validar resposta
            if "error" in result:
                raise Exception(f"MCP server error: {result['error']}")

            return result.get("result")

    def get_health_status(self) -> Dict[str, Any]:
        """Retorna status de saúde do cliente.

        Returns:
            Dict com status de saúde
        """
        return {
            "endpoint": self.endpoint,
            "server_name": self.server_name,
            "connection_status": self.connection_handler.get_status(self.server_name),
            "config": {
                "request_timeout": self.connection_handler.config.request_timeout,
                "max_retries": self.connection_handler.config.max_retries,
                "failure_threshold": self.connection_handler.config.failure_threshold,
            },
        }
