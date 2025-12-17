"""
Módulo de Monitoramento Inteligente do OmniMind

Componentes:
- progressive_monitor: Monitor com modo adaptativo
- resource_protector: Proteção contra sobrecarga
- alert_system: Sistema centralizado de alertas

Exemplo de uso:

    monitor = await get_progressive_monitor()
    await monitor.start()
    monitor.set_level(MonitorLevel.INTENSIVE)

    protector = await get_resource_protector("dev")
    await protector.start()

    alerts = await get_alert_system()
    await alerts.emit_server_down("timeout")
"""

from .alert_system import (
    AlertChannel,
    AlertEvent,
    AlertSystem,
    AlertType,
    get_alert_system,
)
from .progressive_monitor import (
    Alert,
    AlertSeverity,
    MonitorLevel,
    ProgressiveMonitor,
    SystemSnapshot,
    get_progressive_monitor,
)
from .resource_protector import (
    ResourceLimits,
    ResourceProtector,
    get_resource_protector,
)

__all__ = [
    # Progressive Monitor
    "ProgressiveMonitor",
    "MonitorLevel",
    "Alert",
    "AlertSeverity",
    "SystemSnapshot",
    "get_progressive_monitor",
    # Resource Protector
    "ResourceProtector",
    "ResourceLimits",
    "get_resource_protector",
    # Alert System
    "AlertSystem",
    "AlertEvent",
    "AlertType",
    "AlertChannel",
    "get_alert_system",
]
