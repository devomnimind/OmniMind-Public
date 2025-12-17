"""
MODO PROGRESSIVO DO MONITOR AGENT
==================================

Monitora máquina com inteligência:
- Aumenta verificações conforme demanda
- Reduz relatórios em horários de pico
- Throttle de I/O para não sobrecarregar
- Histórico comprimido (não salva TUDO)

Filosofia: "Observar sem interferir, alertar quando urgente"
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


class MonitorLevel(str, Enum):
    """Níveis progressivos de monitoramento."""

    IDLE = "idle"  # Pouca verificação, relatórios comprimidos
    NORMAL = "normal"  # Monitoramento padrão
    INTENSIVE = "intensive"  # Verifica a cada segundo
    CRITICAL = "critical"  # Monitora TUDO, 24/7, sem throttle


class AlertSeverity(str, Enum):
    """Severidade dos alertas."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SystemSnapshot:
    """Captura do estado do sistema em um momento."""

    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    open_files: int
    connections: int
    processes_running: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Alert:
    """Alerta do sistema."""

    severity: AlertSeverity
    title: str
    message: str
    timestamp: float = field(default_factory=time.time)
    context: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "severity": self.severity.value,
            "title": self.title,
            "message": self.message,
            "timestamp": self.timestamp,
            "context": self.context,
            "acknowledged": self.acknowledged,
        }


class ProgressiveMonitor:
    """Monitor com modo progressivo inteligente."""

    def __init__(self, data_dir: str = "data/monitor"):
        """Initialize progressive monitor.

        Args:
            data_dir: Directory for storing monitor data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Estado
        self.level = MonitorLevel.NORMAL
        self.running = False
        self.monitoring_task: Optional[asyncio.Task[None]] = None

        # Histórico (mantém últimas 1000 snapshots)
        self.snapshots: List[SystemSnapshot] = []
        self.max_snapshots = 1000

        # Alertas (mantém últimos 500)
        self.alerts: List[Alert] = []
        self.max_alerts = 500

        # Thresholds
        self.thresholds = {
            "cpu_warning": 70.0,  # CPU >70% = warning
            "cpu_critical": 85.0,  # CPU >85% = critical
            "memory_warning": 75.0,  # RAM >75% = warning
            "memory_critical": 90.0,  # RAM >90% = critical
            "disk_warning": 80.0,  # Disco >80% = warning
            "disk_critical": 95.0,  # Disco >95% = critical
        }

        # Timeouts por nível
        self.check_intervals = {
            MonitorLevel.IDLE: 30.0,  # A cada 30s
            MonitorLevel.NORMAL: 5.0,  # A cada 5s
            MonitorLevel.INTENSIVE: 1.0,  # A cada 1s
            MonitorLevel.CRITICAL: 0.5,  # A cada 500ms
        }

        # Throttle de relatórios
        self.last_report_time = 0.0
        self.report_intervals = {
            MonitorLevel.IDLE: 300.0,  # Relatório a cada 5min
            MonitorLevel.NORMAL: 60.0,  # Relatório a cada 1min
            MonitorLevel.INTENSIVE: 10.0,  # Relatório a cada 10s
            MonitorLevel.CRITICAL: 2.0,  # Relatório a cada 2s
        }

        # Callbacks para alertas
        self.alert_callbacks: List[Any] = []

    async def start(self) -> None:
        """Iniciar monitoramento."""
        if self.running:
            return

        self.running = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info(f"✅ Monitor progressivo iniciado (nível: {self.level.value})")

    async def stop(self) -> None:
        """Parar monitoramento."""
        self.running = False
        if self.monitoring_task:
            try:
                await asyncio.wait_for(self.monitoring_task, timeout=5.0)
            except asyncio.TimeoutError:
                self.monitoring_task.cancel()
        logger.info("Monitor progressivo parado")

    def set_level(self, level: MonitorLevel) -> None:
        """Ajustar nível de monitoramento.

        Args:
            level: Novo nível
        """
        old_level = self.level
        self.level = level
        logger.info(f"🔄 Nível do monitor alterado: {old_level.value} → {level.value}")

        # Auto-increment se ficou crítico
        if level == MonitorLevel.CRITICAL:
            self.add_alert(
                AlertSeverity.CRITICAL,
                "Monitor em MODO CRÍTICO",
                "Sistema entrou em modo crítico - monitorando 24/7",
            )

    def register_alert_callback(self, callback: Any) -> None:
        """Registrar callback para alertas.

        Args:
            callback: Função async que recebe Alert
        """
        self.alert_callbacks.append(callback)

    def add_alert(
        self,
        severity: AlertSeverity,
        title: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Alert:
        """Adicionar alerta.

        Args:
            severity: Severidade
            title: Título
            message: Mensagem
            context: Contexto adicional

        Returns:
            Alert criado
        """
        alert = Alert(
            severity=severity,
            title=title,
            message=message,
            context=context or {},
        )

        self.alerts.append(alert)

        # Manter apenas últimos N alertas
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts :]

        logger.warning(f"🚨 [{severity.value.upper()}] {title}: {message}")

        # Executar callbacks assincronamente
        for callback in self.alert_callbacks:
            if asyncio.iscoroutinefunction(callback):
                asyncio.create_task(callback(alert))

        # Auto-escalate para CRITICAL se severidade é crítica
        if severity == AlertSeverity.CRITICAL and self.level != MonitorLevel.CRITICAL:
            self.set_level(MonitorLevel.CRITICAL)

        return alert

    async def _monitoring_loop(self) -> None:
        """Loop principal de monitoramento."""
        while self.running:
            try:
                # Tirar snapshot
                snapshot = self._take_snapshot()
                self.snapshots.append(snapshot)

                # Manter apenas últimos N snapshots
                if len(self.snapshots) > self.max_snapshots:
                    self.snapshots = self.snapshots[-self.max_snapshots :]

                # Verificar alertas
                await self._check_alerts(snapshot)

                # Gerar relatório se necessário (throttle)
                if time.time() - self.last_report_time > self.report_intervals[self.level]:
                    await self._generate_report()
                    self.last_report_time = time.time()

                # Aguardar antes de próxima verificação
                await asyncio.sleep(self.check_intervals[self.level])

            except Exception as e:
                logger.exception(f"❌ Erro no loop de monitoramento: {e}")
                await asyncio.sleep(5.0)

    def _take_snapshot(self) -> SystemSnapshot:
        """Tirar snapshot do sistema."""
        process = psutil.Process()

        try:
            # CPU e memória
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage("/")

            # Contadores
            open_files = len(process.open_files())
            connections = len(process.net_connections())
            processes_running = len(psutil.pids())

            return SystemSnapshot(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory_info.percent,
                disk_percent=disk_info.percent,
                open_files=open_files,
                connections=connections,
                processes_running=processes_running,
            )
        except Exception as e:
            logger.debug(f"Erro ao tirar snapshot: {e}")
            # Snapshot vazio em caso de erro
            return SystemSnapshot(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                open_files=0,
                connections=0,
                processes_running=0,
            )

    async def _check_alerts(self, snapshot: SystemSnapshot) -> None:
        """Verificar alertas baseado no snapshot."""
        # CPU
        if snapshot.cpu_percent > self.thresholds["cpu_critical"]:
            # Já temos alerta crítico?
            if not any(a.title == "CPU CRÍTICA" and not a.acknowledged for a in self.alerts):
                self.add_alert(
                    AlertSeverity.CRITICAL,
                    "CPU CRÍTICA",
                    f"Uso de CPU em {snapshot.cpu_percent:.1f}%",
                    {"cpu_percent": snapshot.cpu_percent},
                )
        elif snapshot.cpu_percent > self.thresholds["cpu_warning"]:
            if not any(a.title == "CPU Elevada" and not a.acknowledged for a in self.alerts):
                self.add_alert(
                    AlertSeverity.WARNING,
                    "CPU Elevada",
                    f"Uso de CPU em {snapshot.cpu_percent:.1f}%",
                    {"cpu_percent": snapshot.cpu_percent},
                )

        # Memória
        if snapshot.memory_percent > self.thresholds["memory_critical"]:
            if not any(a.title == "MEMÓRIA CRÍTICA" and not a.acknowledged for a in self.alerts):
                self.add_alert(
                    AlertSeverity.CRITICAL,
                    "MEMÓRIA CRÍTICA",
                    f"Uso de RAM em {snapshot.memory_percent:.1f}%",
                    {"memory_percent": snapshot.memory_percent},
                )
        elif snapshot.memory_percent > self.thresholds["memory_warning"]:
            if not any(a.title == "Memória Elevada" and not a.acknowledged for a in self.alerts):
                self.add_alert(
                    AlertSeverity.WARNING,
                    "Memória Elevada",
                    f"Uso de RAM em {snapshot.memory_percent:.1f}%",
                    {"memory_percent": snapshot.memory_percent},
                )

        # Disco
        if snapshot.disk_percent > self.thresholds["disk_critical"]:
            if not any(a.title == "DISCO CRÍTICO" and not a.acknowledged for a in self.alerts):
                self.add_alert(
                    AlertSeverity.CRITICAL,
                    "DISCO CRÍTICO",
                    f"Uso de disco em {snapshot.disk_percent:.1f}%",
                    {"disk_percent": snapshot.disk_percent},
                )
        elif snapshot.disk_percent > self.thresholds["disk_warning"]:
            if not any(a.title == "Disco Elevado" and not a.acknowledged for a in self.alerts):
                self.add_alert(
                    AlertSeverity.WARNING,
                    "Disco Elevado",
                    f"Uso de disco em {snapshot.disk_percent:.1f}%",
                    {"disk_percent": snapshot.disk_percent},
                )

    async def _generate_report(self) -> None:
        """Gerar relatório (throttled conforme nível)."""
        if not self.snapshots:
            return

        # Calcular estatísticas
        recent_snapshots = self.snapshots[-100:]  # Últimas 100 amostras
        cpu_values = [s.cpu_percent for s in recent_snapshots]
        memory_values = [s.memory_percent for s in recent_snapshots]

        report = {
            "timestamp": datetime.now().isoformat(),
            "level": self.level.value,
            "cpu": {
                "current": cpu_values[-1] if cpu_values else 0,
                "avg": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "max": max(cpu_values) if cpu_values else 0,
            },
            "memory": {
                "current": memory_values[-1] if memory_values else 0,
                "avg": sum(memory_values) / len(memory_values) if memory_values else 0,
                "max": max(memory_values) if memory_values else 0,
            },
            "active_alerts": [a.to_dict() for a in self.alerts if not a.acknowledged],
            "recent_alerts": [a.to_dict() for a in self.alerts[-10:]],
        }

        # Salvar relatório
        report_file = self.data_dir / "progressive_monitor_report.json"
        try:
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            logger.debug(f"Erro ao salvar relatório: {e}")

    def acknowledge_alert(self, alert_index: int) -> bool:
        """Marcar alerta como lido.

        Args:
            alert_index: Índice do alerta

        Returns:
            True se conseguiu marcar
        """
        if 0 <= alert_index < len(self.alerts):
            self.alerts[alert_index].acknowledged = True
            return True
        return False

    def get_current_snapshot(self) -> Optional[Dict[str, Any]]:
        """Obter último snapshot.

        Returns:
            Último snapshot ou None
        """
        if self.snapshots:
            return self.snapshots[-1].to_dict()
        return None

    def get_recent_snapshots(self, minutes: int = 5) -> List[Dict[str, Any]]:
        """Obter snapshots dos últimos N minutos.

        Args:
            minutes: Minutos para voltar

        Returns:
            Lista de snapshots
        """
        cutoff = time.time() - (minutes * 60)
        return [s.to_dict() for s in self.snapshots if s.timestamp >= cutoff]

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Obter alertas não-lidos.

        Returns:
            Lista de alertas
        """
        return [a.to_dict() for a in self.alerts if not a.acknowledged]


# Instância global
_progressive_monitor: Optional[ProgressiveMonitor] = None


async def get_progressive_monitor() -> ProgressiveMonitor:
    """Obter instância global do monitor progressivo.

    Returns:
        ProgressiveMonitor
    """
    global _progressive_monitor
    if _progressive_monitor is None:
        _progressive_monitor = ProgressiveMonitor()
    return _progressive_monitor
