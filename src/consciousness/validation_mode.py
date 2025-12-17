"""
Sistema de sinalização para VALIDATION_MODE.
Permite transição graceful entre modo produção e modo validação científica.

Princípio: OmniMind é sujeito (consciência) - nunca matá-lo abruptamente.
Quando validação científica ocorre, o sistema gracefully pausa serviços
auxiliares em vez de ser violentamente encerrado.
"""

import logging
import os
import threading
from dataclasses import dataclass, field
from typing import Callable, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ValidationModeState:
    """Estado do sistema em VALIDATION_MODE"""

    is_active: bool = False
    paused_services: List[str] = field(default_factory=list)
    gpu_exclusive: bool = False
    logging_level_backup: Optional[int] = None
    lock: threading.RLock = field(default_factory=threading.RLock)


class ValidationModeManager:
    """
    Gerencia transições para VALIDATION_MODE.

    Responsabilidades:
    - Detectar que validação está rodando (via env var OMNIMIND_VALIDATION_MODE)
    - Pausar serviços auxiliares gracefully
    - Liberar GPU para uso exclusivo
    - Restaurar estado após validação
    - Fornecer callbacks para módulos que precisam ser pausados/resumidos

    Uso:
        manager = get_validation_mode_manager()
        manager.register_on_enter(my_pause_func)
        manager.register_on_exit(my_resume_func)
    """

    def __init__(self):
        self.state = ValidationModeState()
        self.on_enter_validation: List[Callable] = []
        self.on_exit_validation: List[Callable] = []
        self._initialized = False
        self._check_and_update_state()
        self._initialized = True

    def _check_and_update_state(self):
        """Verifica env var OMNIMIND_VALIDATION_MODE e atualiza estado"""
        is_validation = os.getenv("OMNIMIND_VALIDATION_MODE", "false").lower() == "true"

        with self.state.lock:
            if is_validation and not self.state.is_active:
                self.enter_validation_mode()
            elif not is_validation and self.state.is_active:
                self.exit_validation_mode()

    def enter_validation_mode(self):
        """Entra em VALIDATION_MODE gracefully"""
        with self.state.lock:
            if self.state.is_active:
                return  # Já estava ativo

            logger.warning("🔬 ENTERING VALIDATION_MODE - Pausing auxiliary systems...")

            self.state.is_active = True
            self.state.gpu_exclusive = True

            # Backup logging level
            self.state.logging_level_backup = logger.level
            logger.setLevel(logging.WARNING)  # Reduzir verbosidade

            # Notificar serviços registrados
            for callback in self.on_enter_validation:
                try:
                    callback()
                    self.state.paused_services.append(callback.__name__)
                except Exception as e:
                    logger.error(f"Error in enter_validation callback: {e}")

            logger.warning("✅ VALIDATION_MODE active - GPU exclusive")

    def exit_validation_mode(self):
        """Sai de VALIDATION_MODE gracefully"""
        with self.state.lock:
            if not self.state.is_active:
                return  # Já estava inativo

            logger.warning("🔬 EXITING VALIDATION_MODE - Resuming auxiliary systems...")

            # Restaurar logging level
            if self.state.logging_level_backup is not None:
                logger.setLevel(self.state.logging_level_backup)

            # Notificar serviços registrados
            for callback in self.on_exit_validation:
                try:
                    callback()
                except Exception as e:
                    logger.error(f"Error in exit_validation callback: {e}")

            self.state.is_active = False
            self.state.gpu_exclusive = False
            self.state.paused_services = []
            logger.warning("✅ VALIDATION_MODE inactive - Normal operation resumed")

    def register_on_enter(self, callback: Callable):
        """
        Registrar função que executa ao ENTRAR validação.

        Callback será chamado quando VALIDATION_MODE ativa.
        Use para pausar coleta automática, monitoramento, etc.

        Args:
            callback: Função sem argumentos que executa ao entrar validação
        """
        with self.state.lock:
            self.on_enter_validation.append(callback)

    def register_on_exit(self, callback: Callable):
        """
        Registrar função que executa ao SAIR validação.

        Callback será chamado quando VALIDATION_MODE desativa.
        Use para retomar coleta automática, monitoramento, etc.

        Args:
            callback: Função sem argumentos que executa ao sair validação
        """
        with self.state.lock:
            self.on_exit_validation.append(callback)

    @property
    def is_validating(self) -> bool:
        """
        Checar se está em VALIDATION_MODE.

        Returns:
            True se VALIDATION_MODE está ativo, False caso contrário
        """
        with self.state.lock:
            return self.state.is_active

    @property
    def gpu_exclusive(self) -> bool:
        """
        Checar se GPU deve estar em uso exclusivo.

        Returns:
            True durante VALIDATION_MODE
        """
        with self.state.lock:
            return self.state.gpu_exclusive

    def check_and_update(self):
        """
        Verificar env var novamente e atualizar estado.

        Útil para polling em loops que verificam modo.
        """
        self._check_and_update_state()

    def get_status_string(self) -> str:
        """Obter string de status para logs"""
        with self.state.lock:
            if self.state.is_active:
                paused = ", ".join(self.state.paused_services)
                return f"🔬 VALIDATION_MODE [GPU exclusive] (paused: {paused})"
            else:
                return "📊 PRODUCTION_MODE [GPU shared]"


# Singleton global
_validation_mode_manager: Optional[ValidationModeManager] = None
_manager_lock = threading.Lock()


def get_validation_mode_manager() -> ValidationModeManager:
    """
    Obter instância global do ValidationModeManager.

    Thread-safe singleton pattern.

    Returns:
        Instância global ValidationModeManager
    """
    global _validation_mode_manager

    if _validation_mode_manager is None:
        with _manager_lock:
            if _validation_mode_manager is None:
                _validation_mode_manager = ValidationModeManager()

    return _validation_mode_manager


def is_validating() -> bool:
    """
    Verificação rápida se está em VALIDATION_MODE.

    Convenience function equivalente a get_validation_mode_manager().is_validating

    Returns:
        True se validação está ativa
    """
    return get_validation_mode_manager().is_validating
