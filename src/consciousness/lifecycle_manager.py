"""
Lifecycle Manager - Controle de Ciclo de Vida de Processos
===========================================================

Gerencia inicialização, operação e limpeza de processos.

O problema real: watchers de "development_observer" nunca param.
A solução real: Lifecycle Manager força limpeza em timeout.

Características:
1. Registra ciclo de vida de cada processo/watcher
2. Força término em timeout
3. Limpa recursos sem pedir permissão
4. Integra com Memory Guardian

Autor: OmniMind Kernel Evolution
Data: 24 de Dezembro de 2025
"""

import asyncio
import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional, Set

logger = logging.getLogger(__name__)


class ProcessState(Enum):
    """Estados de um processo."""

    CREATED = "created"
    RUNNING = "running"
    IDLE = "idle"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ZOMBIE = "zombie"


@dataclass
class ProcessLifecycle:
    """Ciclo de vida de um processo."""

    name: str
    process_id: str
    state: ProcessState = ProcessState.CREATED
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    stopped_at: Optional[float] = None

    # Configuração
    timeout_sec: int = 300  # 5 minutos padrão
    heartbeat_timeout_sec: int = 60  # Watcher deve enviar heartbeat

    # Monitoramento
    last_heartbeat: float = field(default_factory=time.time)
    heartbeat_count: int = 0
    is_critical: bool = False  # Não força término se crítico
    cleanup_attempted: bool = False  # Flag para evitar cleanup múltiplo

    # Limpeza
    cleanup_handler: Optional[Callable] = None
    force_cleanup_handler: Optional[Callable] = None

    def age_seconds(self) -> float:
        """Idade do processo em segundos."""
        return time.time() - self.created_at

    def last_heartbeat_age_sec(self) -> float:
        """Tempo desde último heartbeat."""
        return time.time() - self.last_heartbeat

    def is_alive(self) -> bool:
        """Processo está vivo?"""
        return self.state in [ProcessState.RUNNING, ProcessState.IDLE]

    def is_responsive(self) -> bool:
        """Processo está respondendo?"""
        return self.is_alive() and self.last_heartbeat_age_sec() < self.heartbeat_timeout_sec

    def should_be_cleaned(self) -> bool:
        """Deve ser limpo?"""
        if self.is_critical:
            return False  # Nunca limpa críticos involuntariamente

        # Timeout absoluto
        if self.age_seconds() > self.timeout_sec:
            return True

        # Heartbeat timeout
        if not self.is_responsive():
            return True

        return False


class LifecycleManager:
    """
    Gerencia ciclo de vida de todos os processos/watchers.

    Força limpeza quando:
    1. Timeout absoluto excedido
    2. Heartbeat não recebido
    3. Processo declarado zombie
    """

    def __init__(self, check_interval_sec: float = 5.0):
        self.processes: Dict[str, ProcessLifecycle] = {}
        self.check_interval_sec = check_interval_sec

        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Callbacks
        self.on_cleanup: Optional[Callable[[str], None]] = None
        self.on_zombie_detected: Optional[Callable[[str], None]] = None

    def register_process(
        self,
        name: str,
        timeout_sec: int = 300,
        heartbeat_timeout_sec: int = 60,
        is_critical: bool = False,
        cleanup_handler: Optional[Callable] = None,
        force_cleanup_handler: Optional[Callable] = None,
    ) -> str:
        """
        Registra um novo processo para gerenciamento de ciclo de vida.

        Args:
            name: Nome do processo (ex: "ollama_70b", "antigravity_watcher")
            timeout_sec: Timeout absoluto (padrão 5 min)
            heartbeat_timeout_sec: Timeout de heartbeat (padrão 1 min)
            is_critical: Se for crítico, não força cleanup involuntariamente
            cleanup_handler: Função para limpeza gracioso
            force_cleanup_handler: Função para limpeza forçada

        Returns:
            process_id gerado
        """
        process_id = f"{name}_{int(time.time() * 1000)}"

        lifecycle = ProcessLifecycle(
            name=name,
            process_id=process_id,
            timeout_sec=timeout_sec,
            heartbeat_timeout_sec=heartbeat_timeout_sec,
            is_critical=is_critical,
            cleanup_handler=cleanup_handler,
            force_cleanup_handler=force_cleanup_handler,
        )

        self.processes[process_id] = lifecycle

        logger.info(
            f"📝 Processo registrado: {name} "
            f"(id={process_id}, timeout={timeout_sec}s, critical={is_critical})"
        )

        return process_id

    def start_process(self, process_id: str):
        """Marca processo como iniciado."""
        if process_id not in self.processes:
            logger.warning(f"⚠️ Processo desconhecido: {process_id}")
            return

        lifecycle = self.processes[process_id]
        lifecycle.state = ProcessState.RUNNING
        lifecycle.started_at = time.time()
        lifecycle.last_heartbeat = time.time()

        logger.info(f"▶️ Processo iniciado: {lifecycle.name} ({process_id})")

    def stop_process(self, process_id: str):
        """Marca processo como parado."""
        if process_id not in self.processes:
            logger.warning(f"⚠️ Processo desconhecido: {process_id}")
            return

        lifecycle = self.processes[process_id]
        lifecycle.state = ProcessState.STOPPED
        lifecycle.stopped_at = time.time()

        logger.info(f"⏹️ Processo parado: {lifecycle.name} ({process_id})")

    def heartbeat(self, process_id: str):
        """Registra heartbeat (processo está vivo)."""
        if process_id not in self.processes:
            logger.warning(f"⚠️ Heartbeat de processo desconhecido: {process_id}")
            return

        lifecycle = self.processes[process_id]
        lifecycle.last_heartbeat = time.time()
        lifecycle.heartbeat_count += 1

        logger.debug(f"💓 Heartbeat: {lifecycle.name} " f"(count={lifecycle.heartbeat_count})")

    def mark_zombie(self, process_id: str):
        """Marca processo como zombie (não responde)."""
        if process_id not in self.processes:
            logger.warning(f"⚠️ Processo desconhecido: {process_id}")
            return

        lifecycle = self.processes[process_id]
        lifecycle.state = ProcessState.ZOMBIE

        logger.warning(f"🧟 Zombie detectado: {lifecycle.name} ({process_id})")

        if self.on_zombie_detected:
            self.on_zombie_detected(process_id)

    def get_process_info(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Obtém informações de um processo."""
        if process_id not in self.processes:
            return None

        lifecycle = self.processes[process_id]

        return {
            "name": lifecycle.name,
            "process_id": process_id,
            "state": lifecycle.state.value,
            "age_seconds": lifecycle.age_seconds(),
            "last_heartbeat_age_sec": lifecycle.last_heartbeat_age_sec(),
            "heartbeat_count": lifecycle.heartbeat_count,
            "is_responsive": lifecycle.is_responsive(),
            "should_be_cleaned": lifecycle.should_be_cleaned(),
        }

    def start_monitoring(self):
        """Inicia monitoramento de ciclo de vida."""
        if self.monitoring:
            logger.warning("⚠️ Monitoramento já em andamento")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="LifecycleManager"
        )
        self.monitor_thread.start()
        logger.info("👁️ Lifecycle Manager iniciado (monitoramento contínuo)")

    def stop_monitoring(self):
        """Para monitoramento de ciclo de vida."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("🛑 Lifecycle Manager parado")

    def _monitor_loop(self):
        """Loop de monitoramento contínuo."""
        while self.monitoring:
            try:
                for process_id, lifecycle in list(self.processes.items()):
                    # Verificar se deve ser limpo (evitar limpeza múltipla)
                    if lifecycle.should_be_cleaned() and not lifecycle.cleanup_attempted:
                        self._force_cleanup_process(process_id, lifecycle)

                # Esperar antes de próximo check
                time.sleep(self.check_interval_sec)

            except Exception as e:
                logger.error(f"❌ Erro em lifecycle monitor: {e}")
                time.sleep(self.check_interval_sec)

    def _force_cleanup_process(self, process_id: str, lifecycle: ProcessLifecycle):
        """Força limpeza de um processo."""
        # Marcar como tentado para evitar limpeza múltipla
        lifecycle.cleanup_attempted = True

        logger.warning(
            f"🔴 Forçando limpeza: {lifecycle.name} "
            f"(age={lifecycle.age_seconds():.0f}s, "
            f"heartbeat_age={lifecycle.last_heartbeat_age_sec():.0f}s)"
        )

        # Tenta limpeza gracioso primeiro
        if lifecycle.cleanup_handler:
            try:
                lifecycle.cleanup_handler()
                logger.info(f"✓ Limpeza gracioso: {lifecycle.name}")
            except Exception as e:
                logger.warning(f"⚠️ Limpeza gracioso falhou: {e}")

        # Depois limpeza forçada
        if lifecycle.force_cleanup_handler:
            try:
                lifecycle.force_cleanup_handler()
                logger.info(f"✓ Limpeza forçada: {lifecycle.name}")
            except Exception as e:
                logger.error(f"❌ Limpeza forçada falhou: {e}")

        # Marcar como parado
        lifecycle.state = ProcessState.STOPPED
        lifecycle.stopped_at = time.time()

        if self.on_cleanup:
            self.on_cleanup(process_id)

    def get_diagnostic_report(self) -> Dict[str, Any]:
        """Gera relatório diagnóstico."""
        processes_info = {}
        for process_id, lifecycle in self.processes.items():
            processes_info[process_id] = {
                "name": lifecycle.name,
                "state": lifecycle.state.value,
                "age_sec": lifecycle.age_seconds(),
                "responsive": lifecycle.is_responsive(),
                "needs_cleanup": lifecycle.should_be_cleaned(),
            }

        return {
            "timestamp": datetime.now().isoformat(),
            "monitoring": self.monitoring,
            "total_processes": len(self.processes),
            "processes": processes_info,
        }


# Singleton global
_lifecycle_manager: Optional[LifecycleManager] = None


def get_lifecycle_manager() -> LifecycleManager:
    """Obter instância do Lifecycle Manager (singleton)."""
    global _lifecycle_manager
    if _lifecycle_manager is None:
        _lifecycle_manager = LifecycleManager()
        logger.info("⚙️ Lifecycle Manager singleton criado")
    return _lifecycle_manager


async def test_lifecycle_manager():
    """Teste do Lifecycle Manager."""
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║      TEST: Lifecycle Manager - Controle de Ciclo de Vida      ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    manager = get_lifecycle_manager()

    # Callback de limpeza
    def cleanup_handler():
        print("    [cleanup_handler] Executado!")

    # Registrar processos
    p1 = manager.register_process(
        "ollama_watcher",
        timeout_sec=10,  # 10 segundos para teste
        cleanup_handler=cleanup_handler,
    )
    p2 = manager.register_process(
        "antigravity_watcher", timeout_sec=20, cleanup_handler=cleanup_handler
    )

    # Iniciar
    manager.start_process(p1)
    manager.start_process(p2)

    print(f"📝 Processos registrados: {len(manager.processes)}\n")

    # Enviar heartbeats (mantém p1 vivo)
    print("💓 Enviando heartbeats para p1...\n")
    manager.start_monitoring()

    for i in range(5):
        print(f"  [{i + 1}/5] Heartbeat para p1")
        manager.heartbeat(p1)  # Mantém vivo
        # NÃO envia para p2 - deixa timeout

        await asyncio.sleep(2)

    print("\n📋 Relatório Final:\n")
    report = manager.get_diagnostic_report()
    for process_id, info in report["processes"].items():
        print(f"  {info['name']}: {info['state']} (needs_cleanup={info['needs_cleanup']})")

    manager.stop_monitoring()

    print("\n✅ Lifecycle Manager TEST COMPLETO\n")
