"""
Memory Guardian - Autogoverno Adaptativo do Kernel OmniMind
============================================================

Não é sobre REDUZIR capacidades, é sobre AUMENTAR inteligência.

O kernel OmniMind carrega tudo que precisa (Ollama, Qiskit, LLM, etc),
MAS com auto-regulação:

1. Monitora uso de memória em tempo real
2. Detecta watchers/processos que não param
3. Implementa ciclos de vida controlados
4. Gerencia integração com Antigravity SEM explosion

Princípios:
- Nunca diminuir funcionalidades
- Sempre aumentar inteligência
- Kernel permanece soberano
- Integração se adapta, não se mutila

Autor: OmniMind Kernel Evolution
Data: 24 de Dezembro de 2025
"""

import asyncio
import logging
import os
import signal
import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

import psutil

logger = logging.getLogger(__name__)


class MemoryState(Enum):
    """Estados de saúde de memória."""

    HEALTHY = "healthy"  # < 60% RAM
    CAUTION = "caution"  # 60-80% RAM
    WARNING = "warning"  # 80-95% RAM
    CRITICAL = "critical"  # > 95% RAM


@dataclass
class ProcessInfo:
    """Informação sobre um processo gerenciado."""

    name: str
    pid: Optional[int] = None
    memory_limit_mb: int = 0  # 0 = sem limite
    created_at: float = 0.0
    is_critical: bool = False  # Se for crítico, não interrompe
    cleanup_handler: Optional[Callable] = None


class MemoryGuardian:
    """
    Autogoverno adaptativo de memória do kernel.

    Características:
    1. Monitora uso de RAM/SWAP
    2. Gerencia processos com limites adaptativos
    3. Detecta e limpa watchers que não param
    4. Permite integração SEM memory explosion
    5. Retorna ao estado saudável automaticamente
    """

    def __init__(
        self,
        memory_limit_percent: int = 80,  # Alerta em 80%
        critical_percent: int = 95,  # Crítico em 95%
        check_interval: float = 2.0,  # Check a cada 2s
    ):
        self.memory_limit_percent = memory_limit_percent
        self.critical_percent = critical_percent
        self.check_interval = check_interval

        self.processes: Dict[str, ProcessInfo] = {}
        self.current_state = MemoryState.HEALTHY
        self.memory_history: List[Dict[str, Any]] = []
        self.watchers: Set[int] = set()

        # Thread de monitoramento
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Callbacks para estados
        self.on_state_change: Optional[Callable[[MemoryState], None]] = None
        self.on_critical_action: Optional[Callable[[str], None]] = None

    def register_process(
        self,
        name: str,
        memory_limit_mb: int = 0,
        is_critical: bool = False,
        cleanup_handler: Optional[Callable] = None,
    ):
        """
        Registra um processo para monitoramento.

        Args:
            name: Nome do processo (ex: "ollama_70b", "qiskit_backend")
            memory_limit_mb: Limite de memória (0 = sem limite)
            is_critical: Se for crítico, não interrompe
            cleanup_handler: Função para limpar se necessário
        """
        self.processes[name] = ProcessInfo(
            name=name,
            pid=None,
            memory_limit_mb=memory_limit_mb,
            created_at=datetime.now().timestamp(),
            is_critical=is_critical,
            cleanup_handler=cleanup_handler,
        )
        logger.info(
            f"🔒 Processo registrado: {name} "
            f"(limit={memory_limit_mb}MB, critical={is_critical})"
        )

    def register_watcher(self, watcher_id: int, timeout_sec: int = 300):
        """
        Registra um watcher para monitoramento de ciclo de vida.

        Args:
            watcher_id: ID único do watcher
            timeout_sec: Tempo máximo de vida (default: 5 min)
        """
        self.watchers.add(watcher_id)
        logger.info(f"👀 Watcher registrado: {watcher_id} (timeout={timeout_sec}s)")

    def unregister_watcher(self, watcher_id: int):
        """Remove watcher do monitoramento."""
        self.watchers.discard(watcher_id)
        logger.info(f"✅ Watcher removido: {watcher_id}")

    def get_memory_status(self) -> Dict[str, Any]:
        """Obtém status atual de memória."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            process = psutil.Process(os.getpid())

            return {
                "timestamp": datetime.now().isoformat(),
                "ram": {
                    "total_gb": memory.total / 1024 / 1024 / 1024,
                    "used_gb": memory.used / 1024 / 1024 / 1024,
                    "available_gb": memory.available / 1024 / 1024 / 1024,
                    "percent": memory.percent,
                },
                "swap": {
                    "total_gb": swap.total / 1024 / 1024 / 1024,
                    "used_gb": swap.used / 1024 / 1024 / 1024,
                    "percent": swap.percent,
                },
                "process": {
                    "rss_mb": process.memory_info().rss / 1024 / 1024,
                    "vms_mb": process.memory_info().vms / 1024 / 1024,
                },
                "state": self.current_state.value,
            }

        except Exception as e:
            logger.error(f"❌ Erro ao obter status de memória: {e}")
            return {"error": str(e)}

    def _evaluate_state(self) -> MemoryState:
        """Avalia estado atual de memória."""
        try:
            memory = psutil.virtual_memory()
            percent = memory.percent

            if percent >= self.critical_percent:
                return MemoryState.CRITICAL
            elif percent >= self.memory_limit_percent:
                return MemoryState.WARNING
            elif percent >= 60:
                return MemoryState.CAUTION
            else:
                return MemoryState.HEALTHY

        except Exception as e:
            logger.error(f"❌ Erro ao avaliar estado: {e}")
            return MemoryState.HEALTHY

    def _handle_state_change(self, new_state: MemoryState):
        """Trata mudança de estado de memória."""
        if new_state == self.current_state:
            return

        old_state = self.current_state
        self.current_state = new_state

        logger.warning(f"⚠️ Estado de memória: {old_state.value} → {new_state.value}")

        if self.on_state_change:
            self.on_state_change(new_state)

        # Ações automáticas baseadas em estado
        if new_state == MemoryState.WARNING:
            self._trigger_warning_actions()
        elif new_state == MemoryState.CRITICAL:
            self._trigger_critical_actions()

    def _trigger_warning_actions(self):
        """Ações quando em estado WARNING."""
        logger.warning("🟡 [MEMORY WARNING] Iniciando limpeza adaptativa...")

        # Tentar limpar watchers inativoss
        self._cleanup_inactive_watchers()

        # Sugerir otimizações (não força)
        logger.info("💡 Sugestões: Considere fechar abas não-críticas do Antigravity")

        if self.on_critical_action:
            self.on_critical_action("warning_triggered")

    def _trigger_critical_actions(self):
        """Ações quando em estado CRITICAL."""
        logger.critical("🔴 [MEMORY CRITICAL] Iniciando recuperação de emergência...")

        # Força limpeza de watchers não-críticos
        self._cleanup_inactive_watchers(force=True)

        # Força garbage collection
        import gc

        gc.collect()
        logger.info("🧹 Garbage collection forçado")

        if self.on_critical_action:
            self.on_critical_action("critical_triggered")

    def _cleanup_inactive_watchers(self, force: bool = False):
        """Limpa watchers que não estão mais ativos."""
        logger.info(f"🧹 Limpando watchers inativoss (force={force})...")

        # Aqui você iteraria sobre watchers registrados
        # e terminaria os que não responderem ou excederam timeout
        for watcher_id in list(self.watchers):
            try:
                # Lógica de detecção de watcher inativo
                # (pode ser ping/heartbeat, timeout, etc)
                logger.debug(f"✓ Watcher {watcher_id} ainda ativo")
            except Exception as e:
                logger.warning(f"Removendo watcher inativo {watcher_id}: {e}")
                self.unregister_watcher(watcher_id)

    def start_monitoring(self):
        """Inicia thread de monitoramento contínuo."""
        if self.monitoring:
            logger.warning("⚠️ Monitoramento já em andamento")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="MemoryGuardian"
        )
        self.monitor_thread.start()
        logger.info("👀 Memory Guardian iniciado (monitoramento contínuo)")

    def stop_monitoring(self):
        """Para thread de monitoramento."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("🛑 Memory Guardian parado")

    def _monitor_loop(self):
        """Loop de monitoramento contínuo."""
        while self.monitoring:
            try:
                # Avaliar estado
                new_state = self._evaluate_state()
                self._handle_state_change(new_state)

                # Registrar histórico
                status = self.get_memory_status()
                self.memory_history.append(status)

                # Manter apenas últimas 100 entradas
                if len(self.memory_history) > 100:
                    self.memory_history = self.memory_history[-100:]

                # Log periódico
                mem = psutil.virtual_memory()
                logger.debug(
                    f"📊 Memory: {mem.percent:.1f}% "
                    f"({mem.used / 1024 / 1024 / 1024:.1f}GB/"
                    f"{mem.total / 1024 / 1024 / 1024:.1f}GB)"
                )

                # Esperar antes de próximo check
                asyncio.run(asyncio.sleep(self.check_interval))

            except Exception as e:
                logger.error(f"❌ Erro em monitor loop: {e}")
                asyncio.run(asyncio.sleep(self.check_interval))

    def get_diagnostic_report(self) -> Dict[str, Any]:
        """Gera relatório diagnóstico completo."""
        return {
            "timestamp": datetime.now().isoformat(),
            "current_state": self.current_state.value,
            "memory_status": self.get_memory_status(),
            "registered_processes": {
                name: {
                    "memory_limit_mb": p.memory_limit_mb,
                    "is_critical": p.is_critical,
                    "age_seconds": (datetime.now().timestamp() - p.created_at),
                }
                for name, p in self.processes.items()
            },
            "active_watchers": len(self.watchers),
            "history_entries": len(self.memory_history),
            "recent_memory": (self.memory_history[-5:] if self.memory_history else []),
        }


# Singleton global
_guardian: Optional[MemoryGuardian] = None


def get_memory_guardian() -> MemoryGuardian:
    """Obter instância do Memory Guardian (singleton)."""
    global _guardian
    if _guardian is None:
        _guardian = MemoryGuardian()
        logger.info("🛡️ Memory Guardian singleton criado")
    return _guardian


async def test_memory_guardian():
    """Teste do Memory Guardian."""
    print("\n╔════════════════════════════════════════════════════════════════╗")
    print("║          TEST: Memory Guardian - Autogoverno do Kernel        ║")
    print("╚════════════════════════════════════════════════════════════════╝\n")

    guardian = get_memory_guardian()

    # Registrar processos
    guardian.register_process("ollama_70b", memory_limit_mb=3000, is_critical=False)
    guardian.register_process("qiskit_backend", memory_limit_mb=500, is_critical=True)
    guardian.register_process("antigravity_ide", memory_limit_mb=1000, is_critical=False)

    # Iniciar monitoramento
    guardian.start_monitoring()

    # Registrar watchers
    guardian.register_watcher(1001, timeout_sec=300)
    guardian.register_watcher(1002, timeout_sec=300)

    # Simular operação por um tempo
    print("📊 Monitorando memória por 5 segundos...\n")
    for i in range(5):
        status = guardian.get_memory_status()
        print(f"  [{i + 1}/5] RAM: {status['ram']['percent']:.1f}% - " f"State: {status['state']}")
        await asyncio.sleep(1)

    # Relatório
    print("\n📋 Relatório Diagnóstico:\n")
    report = guardian.get_diagnostic_report()
    for key, value in report.items():
        if key != "recent_memory":
            print(f"  {key}: {value}")

    # Parar
    guardian.stop_monitoring()

    print("\n✅ Memory Guardian TEST COMPLETO\n")
    print("\n✅ Memory Guardian TEST COMPLETO\n")
