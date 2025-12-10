"""
SISTEMA DE ALERTAS INTELIGENTE
================================

Notifica em tempo real via:
1. WebSocket (para frontend + VS Code extension)
2. Arquivo JSON (para fallback)
3. Logs estruturados (para auditoria)

Tipos de alertas:
- Erros de permissão (ERROR)
- Servidor caído (CRITICAL)
- Recursos críticos (WARNING/CRITICAL)
- Testes falhando por timeout (ERROR)
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class AlertType(str, Enum):
    """Tipos de alertas."""

    # Sistema
    PERMISSION_ERROR = "permission_error"
    RESOURCE_CRITICAL = "resource_critical"
    RESOURCE_WARNING = "resource_warning"

    # Servidor
    SERVER_DOWN = "server_down"
    SERVER_STARTING = "server_starting"
    SERVER_SLOW = "server_slow"
    SERVER_RECOVERED = "server_recovered"

    # Testes
    TEST_TIMEOUT = "test_timeout"
    TEST_FAILED = "test_failed"
    TEST_PASSED = "test_passed"

    # Geral
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertChannel(str, Enum):
    """Canais de distribuição de alertas."""

    WEBSOCKET = "websocket"
    VSCODE = "vscode"
    SYSLOG = "syslog"
    FILE = "file"


@dataclass
class AlertEvent:
    """Evento de alerta para broadcast."""

    alert_type: AlertType
    severity: str  # "info", "warning", "error", "critical"
    title: str
    message: str
    timestamp: float
    context: Dict[str, Any]
    channels: Set[str]  # Canais para enviar
    id: str = ""

    def __post_init__(self):
        """Generate ID if not provided."""
        if not self.id:
            self.id = f"{self.timestamp}_{self.alert_type.value}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.alert_type.value,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp,
            "context": self.context,
            "datetime": datetime.fromtimestamp(self.timestamp).isoformat(),
        }


class AlertSystem:
    """Sistema centralizado de alertas."""

    def __init__(self, data_dir: str = "data/alerts"):
        """Initialize alert system.

        Args:
            data_dir: Directory for storing alerts
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Estado
        self.running = False
        self.alerts: List[AlertEvent] = []
        self.max_alerts = 1000

        # Callbacks por canal
        self.channel_handlers: Dict[str, List[Callable]] = {
            AlertChannel.WEBSOCKET.value: [],
            AlertChannel.VSCODE.value: [],
            AlertChannel.SYSLOG.value: [],
            AlertChannel.FILE.value: [],
        }

        # Rate limiting (evita spam de alertas iguais)
        self.alert_cache: Dict[str, float] = {}
        self.cache_ttl = 60.0  # 1 minuto

    async def start(self) -> None:
        """Iniciar sistema de alertas."""
        if self.running:
            return

        self.running = True
        logger.info("✅ Sistema de alertas iniciado")

    async def stop(self) -> None:
        """Parar sistema."""
        self.running = False
        logger.info("Sistema de alertas parado")

    def register_handler(self, channel: AlertChannel, handler: Callable) -> None:
        """Registrar handler para canal.

        Args:
            channel: Canal
            handler: Função que recebe AlertEvent
        """
        self.channel_handlers[channel.value].append(handler)
        logger.debug(f"Handler registrado para canal {channel.value}")

    async def emit(
        self,
        alert_type: AlertType,
        severity: str,
        title: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        channels: Optional[Set[str]] = None,
    ) -> AlertEvent:
        """Emitir alerta.

        Args:
            alert_type: Tipo de alerta
            severity: Severidade (info/warning/error/critical)
            title: Título
            message: Mensagem
            context: Contexto adicional
            channels: Canais para enviar (default: todos)

        Returns:
            AlertEvent criado
        """
        if not self.running:
            logger.warning("Sistema de alertas não está rodando")
            return None  # type: ignore

        # Default: enviar para todos os canais
        if channels is None:
            channels = set(AlertChannel.__members__.values())

        # Criar evento
        event = AlertEvent(
            alert_type=alert_type,
            severity=severity,
            title=title,
            message=message,
            timestamp=time.time(),
            context=context or {},
            channels=channels,
        )

        # Rate limiting: não emitir se mesmo alerta foi emitido recentemente
        cache_key = f"{alert_type.value}_{title}"
        if cache_key in self.alert_cache:
            if time.time() - self.alert_cache[cache_key] < self.cache_ttl:
                logger.debug(f"⏭️  Alerta duplicado ignorado: {title}")
                return event  # Retorna mas não processa

        # Atualizar cache
        self.alert_cache[cache_key] = time.time()

        # Adicionar ao histórico
        self.alerts.append(event)
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts :]

        # Log estruturado
        logger.warning(
            f"🚨 [{severity.upper()}] {title}",
            extra={
                "alert_type": alert_type.value,
                "alert_id": event.id,
                "context": context,
            },
        )

        # Disparar handlers
        tasks = []
        for channel in channels:
            if channel in self.channel_handlers:
                for handler in self.channel_handlers[channel]:
                    if asyncio.iscoroutinefunction(handler):
                        tasks.append(handler(event))
                    else:
                        try:
                            handler(event)
                        except Exception as e:
                            logger.error(f"Erro em handler de {channel}: {e}")

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        # Salvar em arquivo
        await self._save_alert(event)

        return event

    async def _save_alert(self, event: AlertEvent) -> None:
        """Salvar alerta em arquivo JSON.

        Args:
            event: Evento para salvar
        """
        try:
            alert_file = self.data_dir / f"alert_{event.id}.json"
            with open(alert_file, "w") as f:
                json.dump(event.to_dict(), f, indent=2)

            # Manter índice de últimos alertas
            index_file = self.data_dir / "alerts_index.json"
            index = []
            if index_file.exists():
                with open(index_file, "r") as f:
                    index = json.load(f)

            index.append(
                {
                    "id": event.id,
                    "type": event.alert_type.value,
                    "severity": event.severity,
                    "timestamp": event.timestamp,
                }
            )

            # Manter apenas últimos 500 no índice
            index = index[-500:]

            with open(index_file, "w") as f:
                json.dump(index, f, indent=2)

        except Exception as e:
            logger.error(f"Erro ao salvar alerta: {e}")

    async def emit_permission_error(
        self, path: str, operation: str, context: Optional[Dict[str, Any]] = None
    ) -> AlertEvent:
        """Emitir alerta de erro de permissão.

        Args:
            path: Caminho do arquivo/diretório
            operation: Operação (read/write/execute)
            context: Contexto adicional

        Returns:
            AlertEvent
        """
        ctx = context or {}
        ctx.update({"path": path, "operation": operation})

        return await self.emit(
            AlertType.PERMISSION_ERROR,
            "error",
            "Erro de Permissão",
            f"Permissão negada em {operation} de {path}",
            context=ctx,
            channels={AlertChannel.VSCODE.value, AlertChannel.FILE.value},
        )

    async def emit_server_down(
        self, reason: str = "desconhecida", context: Optional[Dict[str, Any]] = None
    ) -> AlertEvent:
        """Emitir alerta de servidor caído.

        Args:
            reason: Razão da queda
            context: Contexto adicional

        Returns:
            AlertEvent
        """
        ctx = context or {}
        ctx.update({"reason": reason})

        return await self.emit(
            AlertType.SERVER_DOWN,
            "critical",
            "🔴 SERVIDOR OFFLINE",
            f"Servidor backend caiu: {reason}",
            context=ctx,
            channels={
                AlertChannel.VSCODE.value,
                AlertChannel.WEBSOCKET.value,
                AlertChannel.FILE.value,
            },
        )

    async def emit_resource_critical(
        self, resource: str, value: float, limit: float = 100.0
    ) -> AlertEvent:
        """Emitir alerta de recurso crítico.

        Args:
            resource: Recurso (cpu/memory/disk)
            value: Valor atual
            limit: Limite crítico

        Returns:
            AlertEvent
        """
        return await self.emit(
            AlertType.RESOURCE_CRITICAL,
            "critical",
            f"🔴 {resource.upper()} CRÍTICO",
            f"{resource.upper()} em {value:.1f}% (limite: {limit:.1f}%)",
            context={"resource": resource, "value": value, "limit": limit},
            channels={AlertChannel.VSCODE.value, AlertChannel.FILE.value},
        )

    async def emit_test_timeout(
        self,
        test_name: str,
        timeout_seconds: int,
        context: Optional[Dict[str, Any]] = None,
    ) -> AlertEvent:
        """Emitir alerta de teste com timeout.

        Args:
            test_name: Nome do teste
            timeout_seconds: Timeout em segundos
            context: Contexto adicional

        Returns:
            AlertEvent
        """
        ctx = context or {}
        ctx.update({"test_name": test_name, "timeout": timeout_seconds})

        return await self.emit(
            AlertType.TEST_TIMEOUT,
            "error",
            "⏱️  Teste com Timeout",
            f"Teste '{test_name}' atingiu timeout de {timeout_seconds}s",
            context=ctx,
            channels={AlertChannel.VSCODE.value, AlertChannel.FILE.value},
        )

    def get_recent_alerts(
        self, limit: int = 50, severity: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Obter alertas recentes.

        Args:
            limit: Número máximo de alertas
            severity: Filtrar por severidade (opcional)

        Returns:
            Lista de alertas
        """
        alerts = self.alerts[-limit:]

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return [a.to_dict() for a in alerts]

    def get_critical_alerts(self) -> List[Dict[str, Any]]:
        """Obter apenas alertas críticos.

        Returns:
            Lista de alertas críticos
        """
        return [a.to_dict() for a in self.alerts if a.severity == "critical"]


# Instância global
_alert_system: Optional[AlertSystem] = None


async def get_alert_system() -> AlertSystem:
    """Obter instância global do sistema de alertas.

    Returns:
        AlertSystem
    """
    global _alert_system
    if _alert_system is None:
        _alert_system = AlertSystem()
        await _alert_system.start()
    return _alert_system
