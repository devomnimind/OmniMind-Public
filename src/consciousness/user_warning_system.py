"""
User Warning System - Avisos Transparentes ao Usuário
======================================================

Sistema que avisa o usuário ANTES do kernel tomar ações de proteção.

Princípio:
- Usuário entende que processo bloqueado = proteção do kernel
- Não é bug, é SISTEMA funcionando corretamente
- Avisos transparentes antes de qualquer ação
- Kernel protege sua própria integridade

Tipos de avisos:
1. Prevenção: "Processo será encerrado em X segundos"
2. Ação: "Memória crítica - iniciando limpeza"
3. Resultado: "Processo X foi forçado a parar (proteção do kernel)"

Autor: OmniMind Kernel Evolution
Data: 24 de Dezembro de 2025
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, Optional

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Níveis de severidade de avisos."""

    INFO = "INFO"  # Informativo
    WARNING = "WARNING"  # Aviso
    URGENT = "URGENT"  # Urgente
    CRITICAL = "CRITICAL"  # Crítico


class AlertType(Enum):
    """Tipos de avisos."""

    PROCESS_TIMEOUT = "process_timeout"  # Watcher vai expirar
    MEMORY_WARNING = "memory_warning"  # RAM em 80%+
    MEMORY_CRITICAL = "memory_critical"  # RAM em 95%+
    CLEANUP_IMMINENT = "cleanup_imminent"  # Limpeza vai ser forçada
    CLEANUP_EXECUTED = "cleanup_executed"  # Limpeza foi executada
    PROCESS_TERMINATED = "process_terminated"  # Processo foi parado
    ZOMBIE_DETECTED = "zombie_detected"  # Processo não responde
    KERNEL_PROTECTING = "kernel_protecting"  # Kernel protegendo


@dataclass
class UserAlert:
    """Alerta para o usuário."""

    timestamp: datetime
    level: AlertLevel
    alert_type: AlertType
    title: str
    message: str
    process_name: Optional[str] = None
    action_countdown_sec: Optional[int] = None
    detailed_reason: Optional[str] = None


class UserWarningSystem:
    """
    Sistema de avisos para usuários.

    Responsabilidades:
    1. Gerar avisos ANTES de ações do kernel
    2. Explicar por que ação será tomada
    3. Dar tempo para usuário preparar (countdown)
    4. Informar resultado da ação
    5. Deixar claro que é proteção do kernel
    """

    def __init__(self):
        self.alerts: Dict[str, UserAlert] = {}
        self.alert_callbacks: Dict[AlertLevel, Callable] = {}

        # Callbacks padrão (podem ser overridados)
        self.alert_callbacks[AlertLevel.INFO] = self._default_info_handler
        self.alert_callbacks[AlertLevel.WARNING] = self._default_warning_handler
        self.alert_callbacks[AlertLevel.URGENT] = self._default_urgent_handler
        self.alert_callbacks[AlertLevel.CRITICAL] = self._default_critical_handler

    def register_alert_callback(self, level: AlertLevel, callback: Callable[[UserAlert], None]):
        """Registra callback para nível de alerta."""
        self.alert_callbacks[level] = callback
        logger.info(f"✅ Callback registrado para {level.value}")

    def alert_process_timeout_warning(
        self, process_name: str, timeout_sec: int, countdown_sec: int = 30
    ):
        """Avisa que processo vai expirar."""
        alert = UserAlert(
            timestamp=datetime.now(),
            level=AlertLevel.WARNING,
            alert_type=AlertType.PROCESS_TIMEOUT,
            title=f"⏰ Processo '{process_name}' vai expirar",
            message=(
                f"O processo '{process_name}' não respondeu ao heartbeat.\n"
                f"Será encerrado em {countdown_sec} segundos se não responder.\n"
                f"(Timeout configurado: {timeout_sec}s)"
            ),
            process_name=process_name,
            action_countdown_sec=countdown_sec,
            detailed_reason="Proteção do kernel: processo inativo",
        )

        self._emit_alert(alert)

    def alert_memory_warning(self, ram_percent: float, threshold: int = 80):
        """Avisa que memória está em WARNING."""
        alert = UserAlert(
            timestamp=datetime.now(),
            level=AlertLevel.WARNING,
            alert_type=AlertType.MEMORY_WARNING,
            title="📊 Memória em nível WARNING",
            message=(
                f"RAM em {ram_percent:.1f}% (limite: {threshold}%)\n"
                f"Kernel iniciará limpeza adaptativa.\n"
                f"Feche abas/processos não-críticos."
            ),
            detailed_reason="Proteção do kernel: memória acima de threshold",
        )

        self._emit_alert(alert)

    def alert_memory_critical(self, ram_percent: float, threshold: int = 95):
        """Avisa que memória está CRÍTICA."""
        alert = UserAlert(
            timestamp=datetime.now(),
            level=AlertLevel.CRITICAL,
            alert_type=AlertType.MEMORY_CRITICAL,
            title="🔴 MEMÓRIA CRÍTICA",
            message=(
                f"RAM em {ram_percent:.1f}% (limite: {threshold}%)\n"
                f"AÇÃO IMEDIATA: Limpeza forçada iniciada!\n"
                f"Watchers inativoss serão encerrados."
            ),
            detailed_reason="Proteção do kernel: memória crítica",
        )

        self._emit_alert(alert)

    def alert_cleanup_imminent(self, process_name: str, timeout_sec: int):
        """Avisa que cleanup será executado."""
        alert = UserAlert(
            timestamp=datetime.now(),
            level=AlertLevel.URGENT,
            alert_type=AlertType.CLEANUP_IMMINENT,
            title=f"⚠️ Limpeza forçada: {process_name}",
            message=(
                f"Processo '{process_name}' será encerrado.\n"
                f"Razão: Timeout de {timeout_sec}s excedido.\n"
                f"Ação: Cleanup forçado iniciado."
            ),
            process_name=process_name,
            action_countdown_sec=0,
            detailed_reason="Proteção do kernel: processo expirou",
        )

        self._emit_alert(alert)

    def alert_cleanup_executed(self, process_name: str, reason: str):
        """Avisa que cleanup foi executado."""
        alert = UserAlert(
            timestamp=datetime.now(),
            level=AlertLevel.INFO,
            alert_type=AlertType.CLEANUP_EXECUTED,
            title=f"✅ Processo encerrado: {process_name}",
            message=(
                f"Processo '{process_name}' foi encerrado pelo kernel.\n"
                f"Razão: {reason}\n"
                f"Isto é proteção do sistema."
            ),
            process_name=process_name,
            detailed_reason="Ação de proteção concluída",
        )

        self._emit_alert(alert)

    def alert_process_terminated(self, process_name: str, reason: str, was_critical: bool = False):
        """Avisa que processo foi terminado."""
        level = AlertLevel.URGENT if not was_critical else AlertLevel.INFO
        title = f"⏹️  Processo terminado: {process_name}"
        if was_critical:
            title = f"🛡️ Proteção: {process_name} foi protegido"

        alert = UserAlert(
            timestamp=datetime.now(),
            level=level,
            alert_type=AlertType.PROCESS_TERMINATED,
            title=title,
            message=(
                f"Processo '{process_name}' foi encerrado.\n"
                f"Razão: {reason}\n"
                f"Tipo: {'Crítico (protegido)' if was_critical else 'Normal'}"
            ),
            process_name=process_name,
            detailed_reason="Ação executada pelo Kernel Governor",
        )

        self._emit_alert(alert)

    def alert_zombie_detected(self, process_name: str, age_sec: float):
        """Avisa que zombie foi detectado."""
        alert = UserAlert(
            timestamp=datetime.now(),
            level=AlertLevel.URGENT,
            alert_type=AlertType.ZOMBIE_DETECTED,
            title=f"🧟 Zombie detectado: {process_name}",
            message=(
                f"Processo '{process_name}' está inativo.\n"
                f"Idade: {age_sec:.1f}s sem responder.\n"
                f"Ação: Será terminado em breve."
            ),
            process_name=process_name,
            detailed_reason="Proteção do kernel: processo inativo",
        )

        self._emit_alert(alert)

    def alert_kernel_protecting(self, reason: str, action: str, impact: Optional[str] = None):
        """Aviso genérico de proteção do kernel."""
        alert = UserAlert(
            timestamp=datetime.now(),
            level=AlertLevel.WARNING,
            alert_type=AlertType.KERNEL_PROTECTING,
            title="🛡️ Kernel em modo de proteção",
            message=(
                f"Razão: {reason}\n" f"Ação: {action}\n" f"{f'Impacto: {impact}' if impact else ''}"
            ),
            detailed_reason="Proteção automática do kernel",
        )

        self._emit_alert(alert)

    def _emit_alert(self, alert: UserAlert):
        """Emite alerta via callback registrado."""
        self.alerts[f"{alert.timestamp.isoformat()}_{alert.alert_type.value}"] = alert

        # Log para servidor
        logger.warning(f"🔔 [{alert.level.value}] {alert.title}")
        logger.warning(f"   {alert.message}")

        # Callback
        callback = self.alert_callbacks.get(alert.level)
        if callback:
            callback(alert)

    def _default_info_handler(self, alert: UserAlert):
        """Handler padrão para INFO."""
        print(f"ℹ️  {alert.title}")

    def _default_warning_handler(self, alert: UserAlert):
        """Handler padrão para WARNING."""
        print(f"⚠️  {alert.title}")

    def _default_urgent_handler(self, alert: UserAlert):
        """Handler padrão para URGENT."""
        print(f"🟠 {alert.title}")

    def _default_critical_handler(self, alert: UserAlert):
        """Handler padrão para CRITICAL."""
        print(f"🔴 {alert.title}")

    def get_recent_alerts(self, count: int = 10) -> list:
        """Retorna últimos N avisos."""
        sorted_alerts = sorted(self.alerts.values(), key=lambda x: x.timestamp, reverse=True)
        return sorted_alerts[:count]

    def get_alerts_by_process(self, process_name: str) -> list:
        """Retorna avisos sobre um processo específico."""
        return [alert for alert in self.alerts.values() if alert.process_name == process_name]

    def get_diagnostic_summary(self) -> Dict[str, any]:
        """Retorna sumário diagnóstico."""
        total = len(self.alerts)

        by_level = {}
        for level in AlertLevel:
            count = sum(1 for a in self.alerts.values() if a.level == level)
            by_level[level.value] = count

        return {
            "total_alerts": total,
            "by_level": by_level,
            "recent_alerts": [
                {
                    "timestamp": alert.timestamp.isoformat(),
                    "level": alert.level.value,
                    "type": alert.alert_type.value,
                    "title": alert.title,
                }
                for alert in self.get_recent_alerts(5)
            ],
        }


# Singleton global
_user_warning_system: Optional[UserWarningSystem] = None


def get_user_warning_system() -> UserWarningSystem:
    """Obter instância do User Warning System (singleton)."""
    global _user_warning_system
    if _user_warning_system is None:
        _user_warning_system = UserWarningSystem()
        logger.info("📢 User Warning System inicializado")
    return _user_warning_system


async def test_user_warning_system():
    """Teste do User Warning System."""
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║          TEST: User Warning System - Avisos Transparentes     ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    system = get_user_warning_system()

    print("📢 Gerando avisos de teste...\n")

    # Teste 1: Timeout warning
    system.alert_process_timeout_warning("antigravity_watcher", timeout_sec=60, countdown_sec=30)

    # Teste 2: Memory warning
    system.alert_memory_warning(ram_percent=82.5, threshold=80)

    # Teste 3: Cleanup imminent
    system.alert_cleanup_imminent("ollama_process", timeout_sec=300)

    # Teste 4: Cleanup executed
    system.alert_cleanup_executed("ollama_process", reason="Timeout excedido")

    # Teste 5: Critical memory
    system.alert_memory_critical(ram_percent=96.0, threshold=95)

    # Teste 6: Zombie detected
    system.alert_zombie_detected("qiskit_backend_monitor", age_sec=125.3)

    print("\n📋 Sumário de Avisos Gerados:\n")
    summary = system.get_diagnostic_summary()
    print(f"  Total: {summary['total_alerts']}")
    for level, count in summary["by_level"].items():
        print(f"    {level}: {count}")

    print("\n📜 Últimos avisos:\n")
    for alert in system.get_recent_alerts(3):
        print(f"  [{alert.level.value}] {alert.title}")
        print(f"      {alert.message[:60]}...")

    print("\n✅ User Warning System TEST COMPLETO\n")
