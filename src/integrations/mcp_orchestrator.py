"""
MCP Orchestrator - Gerenciador centralizado de servidores MCP.

Este módulo gerencia o ciclo de vida, health checks, e roteamento de requests
para múltiplos servidores MCP, integrando com o sistema de auditoria do OmniMind.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from src.audit.immutable_audit import get_audit_system

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuração de um servidor MCP individual."""

    name: str
    enabled: bool
    priority: str  # "critical", "high", "medium", "low"
    tier: int  # 1, 2, 3
    command: str
    args: List[str]
    audit_category: str
    port: Optional[int] = None  # Porta individual do servidor (padrão: 4321)
    features: Dict[str, bool] = field(default_factory=dict)
    security: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MCPServerStatus:
    """Status atual de um servidor MCP."""

    name: str
    enabled: bool
    running: bool
    healthy: bool
    last_health_check: float
    uptime_seconds: float
    total_requests: int
    failed_requests: int
    avg_response_time_ms: float
    error_message: Optional[str] = None


class MCPOrchestratorError(Exception):
    """Erro no orquestrador de MCPs."""


class MCPOrchestrator:
    """
    Orquestrador centralizado para gerenciar múltiplos servidores MCP.

    Responsabilidades:
    - Lifecycle management (start/stop/restart)
    - Health monitoring
    - Request routing
    - Metrics collection
    - Audit integration
    """

    def __init__(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """
        Inicializa o orquestrador MCP.

        Args:
            config_path: Caminho para o arquivo de configuração JSON.
                        Se None, usa config/mcp_servers.json.
        """
        self.config_path = self._resolve_config_path(config_path)
        self.config = self._load_config()
        self.audit_system = get_audit_system()

        # Estado interno
        self.servers: Dict[str, MCPServerConfig] = {}
        self.processes: Dict[str, subprocess.Popen[bytes]] = {}
        self.status: Dict[str, MCPServerStatus] = {}
        self.metrics: Dict[str, Dict[str, Any]] = {}

        # Configurações globais
        self.global_settings = self.config.get("global_settings", {})
        self.audit_enabled = self.global_settings.get("audit_enabled", True)
        self.health_check_interval = self.global_settings.get(
            "health_check_interval_seconds", 60
        )

        # Background tasks
        self._health_check_task: Optional[asyncio.Task[None]] = None
        self._metrics_export_task: Optional[asyncio.Task[None]] = None

        # Carregar configurações de servidores
        self._load_server_configs()

        logger.info(
            "MCPOrchestrator inicializado com %d servidores configurados",
            len(self.servers),
        )

    def _resolve_config_path(self, config_path: Optional[Union[str, Path]]) -> Path:
        """Resolve o caminho do arquivo de configuração."""
        if config_path is None:
            base_path = Path(__file__).resolve().parents[2]
            config_path = base_path / "config" / "mcp_servers.json"
        return Path(config_path).expanduser().resolve()

    def _load_config(self) -> Dict[str, Any]:
        """Carrega a configuração do arquivo JSON."""
        if not self.config_path.exists():
            raise MCPOrchestratorError(
                f"Arquivo de configuração não encontrado: {self.config_path}"
            )

        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = json.load(f)
            logger.info("Configuração carregada de %s", self.config_path)
            return cast(Dict[str, Any], config)
        except json.JSONDecodeError as e:
            raise MCPOrchestratorError(f"Erro ao parsear configuração JSON: {e}") from e
        except Exception as e:
            raise MCPOrchestratorError(f"Erro ao carregar configuração: {e}") from e

    def _load_server_configs(self) -> None:
        """Carrega configurações de todos os servidores MCP."""
        mcp_servers = self.config.get("mcp_servers", {})

        for name, server_config in mcp_servers.items():
            if not isinstance(server_config, dict):
                logger.warning("Configuração inválida para servidor %s", name)
                continue

            config = MCPServerConfig(
                name=name,
                enabled=server_config.get("enabled", False),
                priority=server_config.get("priority", "medium"),
                tier=server_config.get("tier", 3),
                command=server_config.get("command", ""),
                args=server_config.get("args", []),
                audit_category=server_config.get("audit_category", f"mcp_{name}"),
                port=server_config.get(
                    "port", 4321
                ),  # Porta padrão 4321 se não especificada
                features=server_config.get("features", {}),
                security=server_config.get("security", {}),
                metadata=server_config,
            )

            self.servers[name] = config

            # Inicializar status
            self.status[name] = MCPServerStatus(
                name=name,
                enabled=config.enabled,
                running=False,
                healthy=False,
                last_health_check=0.0,
                uptime_seconds=0.0,
                total_requests=0,
                failed_requests=0,
                avg_response_time_ms=0.0,
            )

            logger.debug(
                "Servidor MCP configurado: %s (tier=%d, priority=%s, enabled=%s)",
                name,
                config.tier,
                config.priority,
                config.enabled,
            )

    def start_all_servers(self) -> Dict[str, bool]:
        """
        Inicia todos os servidores MCP habilitados.

        Returns:
            Dict com nome do servidor e status de sucesso (True/False).
        """
        results = {}

        # Ordenar por prioridade (critical primeiro)
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        sorted_servers = sorted(
            self.servers.items(),
            key=lambda x: (x[1].tier, priority_order.get(x[1].priority, 99)),
        )

        for name, config in sorted_servers:
            if not config.enabled:
                logger.info("Servidor %s desabilitado, pulando", name)
                results[name] = False
                continue

            try:
                success = self.start_server(name)
                results[name] = success

                if self.audit_enabled:
                    self.audit_system.log_action(
                        action="server_start",
                        details={
                            "server_name": name,
                            "success": success,
                            "tier": config.tier,
                            "priority": config.priority,
                        },
                        category=config.audit_category,
                    )
            except Exception as e:
                logger.error("Erro ao iniciar servidor %s: %s", name, e)
                results[name] = False

        logger.info(
            "Iniciados %d/%d servidores MCP",
            sum(results.values()),
            len(results),
        )
        return results

    def start_server(self, name: str) -> bool:
        """
        Inicia um servidor MCP específico.

        Args:
            name: Nome do servidor MCP.

        Returns:
            True se iniciado com sucesso, False caso contrário.
        """
        if name not in self.servers:
            raise MCPOrchestratorError(f"Servidor MCP não encontrado: {name}")

        config = self.servers[name]

        if not config.enabled:
            logger.warning("Tentativa de iniciar servidor desabilitado: %s", name)
            return False

        if name in self.processes and self.processes[name].poll() is None:
            logger.warning("Servidor %s já está rodando", name)
            return True

        try:
            # Construir comando completo
            cmd = [config.command] + config.args
            logger.info("Iniciando servidor MCP %s: %s", name, " ".join(cmd))

            # Preparar variáveis de ambiente com porta individual
            env = os.environ.copy()
            env["MCP_PORT"] = str(config.port)
            env["MCP_HOST"] = "127.0.0.1"  # Sempre localhost para segurança
            env["MCP_SERVER_NAME"] = name

            # Iniciar processo
            # Note: Em produção, considerar usar asyncio.create_subprocess_exec
            # para melhor integração com async/await
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,  # Passar variáveis de ambiente
                # Não usar stdin para evitar bloqueios
            )

            self.processes[name] = process

            # Aguardar um pouco para verificar se iniciou corretamente
            time.sleep(0.5)

            if process.poll() is not None:
                # Processo terminou imediatamente (erro)
                _, stderr = process.communicate(timeout=1)
                error_msg = stderr.decode("utf-8") if stderr else "Unknown error"
                logger.error("Servidor %s falhou ao iniciar: %s", name, error_msg)

                self.status[name].running = False
                self.status[name].healthy = False
                self.status[name].error_message = error_msg
                return False

            # Processo parece estar rodando
            self.status[name].running = True
            self.status[name].uptime_seconds = 0.0
            logger.info(
                "Servidor MCP %s iniciado com sucesso (PID=%d)", name, process.pid
            )
            return True

        except FileNotFoundError:
            error_msg = f"Comando não encontrado: {config.command}"
            logger.error("Erro ao iniciar servidor %s: %s", name, error_msg)
            self.status[name].error_message = error_msg
            return False
        except Exception as e:
            error_msg = str(e)
            logger.error("Erro ao iniciar servidor %s: %s", name, error_msg)
            self.status[name].error_message = error_msg
            return False

    def stop_server(self, name: str, timeout: int = 10) -> bool:
        """
        Para um servidor MCP específico.

        Args:
            name: Nome do servidor MCP.
            timeout: Timeout em segundos para terminação graceful.

        Returns:
            True se parado com sucesso, False caso contrário.
        """
        if name not in self.processes:
            logger.warning("Servidor %s não está rodando", name)
            return True

        process = self.processes[name]

        try:
            # Tentar terminação graceful primeiro
            process.terminate()

            # Aguardar terminação
            try:
                process.wait(timeout=timeout)
                logger.info("Servidor MCP %s parado gracefully", name)
            except subprocess.TimeoutExpired:
                # Forçar terminação
                logger.warning("Servidor %s não respondeu, forçando terminação", name)
                process.kill()
                process.wait(timeout=5)

            # Remover do tracking
            del self.processes[name]
            self.status[name].running = False
            self.status[name].healthy = False

            if self.audit_enabled:
                config = self.servers[name]
                self.audit_system.log_action(
                    action="server_stop",
                    details={"server_name": name},
                    category=config.audit_category,
                )

            return True

        except Exception as e:
            logger.error("Erro ao parar servidor %s: %s", name, e)
            return False

    def stop_all_servers(self, timeout: int = 10) -> Dict[str, bool]:
        """
        Para todos os servidores MCP em execução.

        Args:
            timeout: Timeout em segundos para cada servidor.

        Returns:
            Dict com nome do servidor e status de sucesso.
        """
        results = {}

        for name in list(self.processes.keys()):
            results[name] = self.stop_server(name, timeout=timeout)

        logger.info("Parados %d servidores MCP", len(results))
        return results

    def restart_server(self, name: str) -> bool:
        """
        Reinicia um servidor MCP.

        Args:
            name: Nome do servidor MCP.

        Returns:
            True se reiniciado com sucesso, False caso contrário.
        """
        logger.info("Reiniciando servidor MCP %s", name)

        # Parar servidor
        self.stop_server(name)

        # Aguardar um pouco antes de reiniciar
        time.sleep(1)

        # Iniciar novamente
        return self.start_server(name)

    def get_server_status(self, name: str) -> MCPServerStatus:
        """
        Obtém o status atual de um servidor MCP.

        Args:
            name: Nome do servidor MCP.

        Returns:
            Status do servidor.
        """
        if name not in self.status:
            raise MCPOrchestratorError(f"Servidor MCP não encontrado: {name}")

        return self.status[name]

    def get_all_statuses(self) -> Dict[str, MCPServerStatus]:
        """
        Obtém o status de todos os servidores MCP.

        Returns:
            Dict com nome do servidor e seu status.
        """
        return dict(self.status)

    def check_server_health(self, name: str) -> bool:
        """
        Verifica a saúde de um servidor MCP.

        Args:
            name: Nome do servidor MCP.

        Returns:
            True se saudável, False caso contrário.

        Note:
            Implementação atual verifica apenas se o processo está rodando.
            TODO: Implementar health check via endpoint HTTP/gRPC para verificação
            real de responsividade do servidor (Issue #TBD).
        """
        if name not in self.processes:
            self.status[name].healthy = False
            return False

        process = self.processes[name]

        # Verificar se processo está rodando
        if process.poll() is not None:
            # Processo terminou
            self.status[name].running = False
            self.status[name].healthy = False
            logger.warning("Servidor MCP %s não está mais rodando", name)
            return False

        # Verificar se a porta está em uso (indica que o servidor HTTP está ativo)
        config = self.servers.get(name)
        if config and config.port:
            try:
                import socket

                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex(("127.0.0.1", config.port))
                sock.close()
                if result == 0:
                    # Porta está aberta e aceitando conexões
                    self.status[name].healthy = True
                    self.status[name].last_health_check = time.time()
                    return True
                else:
                    # Porta não está respondendo, mas processo está rodando
                    # Marcar como não saudável mas não reiniciar imediatamente
                    logger.debug(
                        "Servidor %s: porta %d não está respondendo", name, config.port
                    )
                    self.status[name].healthy = False
                    self.status[name].last_health_check = time.time()
                    return False
            except Exception as e:
                logger.debug("Erro ao verificar porta do servidor %s: %s", name, e)
                # Em caso de erro, assumir que está saudável se processo está rodando
                self.status[name].healthy = True
                self.status[name].last_health_check = time.time()
                return True

        # Se não tem porta configurada, apenas verificar se processo está rodando
        self.status[name].healthy = True
        self.status[name].last_health_check = time.time()
        return True

    async def health_check_loop(self) -> None:
        """Loop de health checks periódicos."""
        logger.info("Iniciando loop de health checks")

        while True:
            try:
                for name in list(self.processes.keys()):
                    healthy = self.check_server_health(name)

                    if not healthy and self.servers[name].enabled:
                        # Verificar se o processo ainda está rodando antes de reiniciar
                        if name in self.processes:
                            process = self.processes[name]
                            if process.poll() is None:
                                # Processo ainda está rodando, apenas não saudável
                                # Não reiniciar imediatamente - pode ser um problema temporário
                                logger.debug(
                                    "Servidor %s não saudável mas processo ainda rodando, aguardando próximo check",
                                    name,
                                )
                                continue
                        # Processo não está rodando, reiniciar
                        logger.warning(
                            "Servidor %s não está rodando, tentando reiniciar", name
                        )
                        self.restart_server(name)

                await asyncio.sleep(self.health_check_interval)

            except Exception as e:
                logger.error("Erro no health check loop: %s", e)
                await asyncio.sleep(5)

    def export_metrics(self) -> Dict[str, Any]:
        """
        Exporta métricas de todos os servidores MCP.

        Returns:
            Dict com métricas agregadas.
        """
        servers: Dict[str, Dict[str, Any]] = {}
        metrics = {
            "timestamp": time.time(),
            "total_servers": len(self.servers),
            "enabled_servers": sum(1 for s in self.servers.values() if s.enabled),
            "running_servers": sum(1 for s in self.status.values() if s.running),
            "healthy_servers": sum(1 for s in self.status.values() if s.healthy),
            "servers": servers,
        }

        for name, status in self.status.items():
            servers[name] = {
                "enabled": status.enabled,
                "running": status.running,
                "healthy": status.healthy,
                "uptime_seconds": status.uptime_seconds,
                "total_requests": status.total_requests,
                "failed_requests": status.failed_requests,
                "error_rate": (
                    status.failed_requests / status.total_requests
                    if status.total_requests > 0
                    else 0.0
                ),
                "avg_response_time_ms": status.avg_response_time_ms,
            }

        return metrics

    def __enter__(self) -> MCPOrchestrator:
        """Context manager entry."""
        self.start_all_servers()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.stop_all_servers()
