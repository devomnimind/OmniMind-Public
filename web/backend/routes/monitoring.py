"""
API routes para monitoramento e alertas
"""

from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter(prefix="/api/monitoring", tags=["monitoring"])


@router.get("/health")
async def get_monitor_health() -> Dict[str, Any]:
    """Obter status de saúde do monitor.

    Returns:
        Status de CPU, RAM, Disco
    """
    try:
        from src.monitor import get_resource_protector

        protector = await get_resource_protector()
        return protector.get_resource_status()
    except Exception as e:
        return {"error": str(e), "status": "unavailable"}


@router.get("/alerts/active")
async def get_active_alerts() -> Dict[str, Any]:
    """Obter alertas ativos não-lidos.

    Returns:
        Lista de alertas críticos
    """
    try:
        from src.monitor import get_alert_system

        alerts = await get_alert_system()
        return {
            "critical": alerts.get_critical_alerts(),
            "recent": alerts.get_recent_alerts(limit=20),
            "total": len(alerts.alerts),
        }
    except Exception as e:
        return {"error": str(e), "status": "unavailable"}


@router.post("/alerts/acknowledge/{alert_id}")
async def acknowledge_alert(alert_id: str) -> Dict[str, Any]:
    """Marcar alerta como lido.

    Args:
        alert_id: ID do alerta

    Returns:
        Status da operação
    """
    try:
        from src.monitor import get_progressive_monitor

        monitor = await get_progressive_monitor()
        # Parse alert_id para obter índice
        # Format: "timestamp_type"
        matching_alerts = [a for a in monitor.alerts if a.title.lower() in alert_id.lower()]
        if matching_alerts:
            idx = monitor.alerts.index(matching_alerts[0])
            success = monitor.acknowledge_alert(idx)
            return {"success": success, "alert_id": alert_id}
        return {"success": False, "message": "Alert not found"}
    except Exception as e:
        return {"error": str(e), "success": False}


@router.get("/snapshots/recent")
async def get_recent_snapshots(minutes: int = 5) -> Dict[str, Any]:
    """Obter snapshots do sistema dos últimos N minutos.

    Args:
        minutes: Minutos para voltar

    Returns:
        Lista de snapshots
    """
    try:
        from src.monitor import get_progressive_monitor

        monitor = await get_progressive_monitor()
        return {
            "snapshots": monitor.get_recent_snapshots(minutes=minutes),
            "count": len(monitor.snapshots),
        }
    except Exception as e:
        return {"error": str(e), "snapshots": []}


@router.get("/status")
async def get_monitoring_status() -> Dict[str, Any]:
    """Obter status completo do monitoramento.

    Returns:
        Status integrado
    """
    try:
        from src.monitor import (
            get_alert_system,
            get_progressive_monitor,
            get_resource_protector,
        )

        monitor = await get_progressive_monitor()
        protector = await get_resource_protector()
        alerts = await get_alert_system()

        return {
            "monitor": {
                "level": monitor.level.value,
                "running": monitor.running,
                "snapshots_count": len(monitor.snapshots),
                "alerts_count": len(monitor.alerts),
                "current": monitor.get_current_snapshot(),
            },
            "protector": {
                "mode": protector.mode,
                "resources": protector.get_resource_status(),
            },
            "alerts": {
                "total": len(alerts.alerts),
                "critical": len(alerts.get_critical_alerts()),
                "recent": alerts.get_recent_alerts(limit=10),
            },
        }
    except Exception as e:
        return {"error": str(e), "status": "unavailable"}
