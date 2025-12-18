"""
Scheduler Automático para Manutenção de Reports

Executa limpeza e compressão em background de forma periódica e segura.

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-11
"""

import logging
import threading
import time
from datetime import datetime, timezone
from typing import Callable, Optional

from src.observability.report_maintenance import get_report_maintenance_manager

logger = logging.getLogger(__name__)


class ReportMaintenanceScheduler:
    """
    Scheduler para execução automática de manutenção de reports.

    Características:
    - Execução em background thread
    - Verificação inteligente (só executa se necessário)
    - Agendamento diário em horário configurável
    - Parada graciosa
    - Callbacks de notificação
    """

    def __init__(
        self,
        check_interval_minutes: int = 60,
        daily_execution_hour: int = 3,  # 3 AM UTC
        daily_execution_minute: int = 0,
        enable_auto_start: bool = True,
    ):
        """
        Inicializa scheduler de manutenção.

        Args:
            check_interval_minutes: Intervalo de verificação (padrão: 1 hora)
            daily_execution_hour: Hora UTC para execução diária (padrão: 3 AM)
            daily_execution_minute: Minuto para execução diária
            enable_auto_start: Iniciar automaticamente
        """
        self.check_interval_seconds = check_interval_minutes * 60
        self.daily_execution_hour = daily_execution_hour
        self.daily_execution_minute = daily_execution_minute

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._callbacks: list[Callable] = []

        self.last_check_time: Optional[datetime] = None
        self.last_execution_time: Optional[datetime] = None

        logger.info(
            f"ReportMaintenanceScheduler inicializado "
            f"(intervalo: {check_interval_minutes}min, execução diária às "
            f"{daily_execution_hour:02d}:{daily_execution_minute:02d} UTC)"
        )

        if enable_auto_start:
            self.start()

    def start(self) -> None:
        """Inicia scheduler em background thread."""
        if self._thread is not None and self._thread.is_alive():
            logger.warning("Scheduler já está em execução")
            return

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("✅ ReportMaintenanceScheduler iniciado")

    def stop(self, timeout_seconds: int = 30) -> None:
        """
        Para scheduler graciosamente.

        Args:
            timeout_seconds: Tempo máximo de espera
        """
        logger.info("Parando ReportMaintenanceScheduler...")
        self._stop_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=timeout_seconds)

            if self._thread.is_alive():
                logger.warning(f"Scheduler não parou em {timeout_seconds}s")
            else:
                logger.info("✅ ReportMaintenanceScheduler parado")

    def add_callback(self, callback: Callable) -> None:
        """
        Adiciona callback a ser executado após manutenção.

        Args:
            callback: Função a executar após manutenção
        """
        self._callbacks.append(callback)

    def _run_loop(self) -> None:
        """Loop principal do scheduler (executa em thread separada)."""
        logger.info("Loop de manutenção iniciado")

        while not self._stop_event.is_set():
            try:
                self._check_and_execute()

                # Esperar intervalo (com capacidade de interrupção)
                self._stop_event.wait(timeout=self.check_interval_seconds)

            except Exception as e:
                logger.error(f"Erro no loop de manutenção: {e}", exc_info=True)
                # Continuar operando mesmo com erro
                self._stop_event.wait(timeout=60)

    def _check_and_execute(self) -> None:
        """Verifica necessidade e executa manutenção se necessário."""
        now = datetime.now(timezone.utc)
        self.last_check_time = now

        manager = get_report_maintenance_manager()

        # Verificar se manutenção é necessária
        needs_maintenance, check_stats = manager.check_maintenance_needed()

        if needs_maintenance:
            logger.info(f"🔧 Manutenção necessária: {check_stats['reason']}")
            self._execute_maintenance()

        # Verificar se é hora de execução diária
        elif now.hour == self.daily_execution_hour and now.minute == self.daily_execution_minute:
            logger.info("⏰ Hora de manutenção diária")
            self._execute_maintenance()

    def _execute_maintenance(self) -> None:
        """Executa manutenção completa."""
        logger.info("🧹 Iniciando manutenção de reports...")

        try:
            start_time = time.time()
            manager = get_report_maintenance_manager()

            # Executar manutenção
            stats = manager.execute_maintenance()

            elapsed = time.time() - start_time

            # Log detalhado
            logger.info(
                f"✅ Manutenção concluída em {elapsed:.1f}s\n"
                f"  📦 Compressão: {stats['compression']['files_processed']} arquivos, "
                f"{stats['compression']['size_before_mb']:.1f}MB → "
                f"{stats['compression']['size_after_mb']:.1f}MB\n"
                f"  🗑️  Limpeza: {stats['cleanup']['files_deleted']} arquivos removidos, "
                f"{stats['cleanup']['size_freed_mb']:.1f}MB liberados\n"
                f"  📊 Status: {stats['total_files_active']} ativos, "
                f"{stats['total_files_archived']} arquivados "
                f"({stats['total_size_archived_mb']:.1f}MB)"
            )

            self.last_execution_time = datetime.now(timezone.utc)

            # Executar callbacks
            for callback in self._callbacks:
                try:
                    callback(stats)
                except Exception as e:
                    logger.error(f"Erro em callback de manutenção: {e}")

        except Exception as e:
            logger.error(f"Erro durante execução de manutenção: {e}", exc_info=True)

    def get_status(self) -> dict:
        """Retorna status atual do scheduler."""
        return {
            "running": self._thread is not None and self._thread.is_alive(),
            "last_check_time": (self.last_check_time.isoformat() if self.last_check_time else None),
            "last_execution_time": (
                self.last_execution_time.isoformat() if self.last_execution_time else None
            ),
            "check_interval_seconds": self.check_interval_seconds,
            "daily_execution_time": (
                f"{self.daily_execution_hour:02d}:{self.daily_execution_minute:02d} UTC"
            ),
        }


# Singleton global
_scheduler: Optional[ReportMaintenanceScheduler] = None


def get_report_maintenance_scheduler(
    auto_start: bool = True,
) -> ReportMaintenanceScheduler:
    """
    Obtém ou cria instância singleton do scheduler.

    Args:
        auto_start: Se True, inicia scheduler automaticamente

    Returns:
        ReportMaintenanceScheduler singleton
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = ReportMaintenanceScheduler(enable_auto_start=auto_start)
    return _scheduler


def init_report_maintenance_scheduler(
    check_interval_minutes: int = 60,
    daily_hour: int = 3,
    daily_minute: int = 0,
) -> ReportMaintenanceScheduler:
    """
    Inicializa scheduler de manutenção com parâmetros personalizados.

    Args:
        check_interval_minutes: Intervalo de verificação
        daily_hour: Hora UTC para execução diária
        daily_minute: Minuto para execução diária

    Returns:
        ReportMaintenanceScheduler singleton
    """
    global _scheduler
    if _scheduler is None:
        _scheduler = ReportMaintenanceScheduler(
            check_interval_minutes=check_interval_minutes,
            daily_execution_hour=daily_hour,
            daily_execution_minute=daily_minute,
            enable_auto_start=True,
        )
    return _scheduler
