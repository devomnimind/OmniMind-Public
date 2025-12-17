"""
Gerenciador centralizado de estado do servidor para tests.

Evita conflitos entre:
- Fixture omnimind_server (E2E tests, session scope)
- ServerMonitorPlugin (runtime monitoring, test scope)

Ambos os componentes devem consultar este módulo antes de reiniciar o servidor.
"""

import logging
import threading
import time
from typing import Optional

logger = logging.getLogger(__name__)


class ServerStateManager:
    """
    Gerenciador centralizado de estado do servidor.

    Garante que:
    1. Apenas UM componente reinicia o servidor por vez (lock)
    2. Outras tentativas de restart respeitam o "dono" atual
    3. Health checks consistentes evitam múltiplas tentativas
    4. Transições de estado são atômicas (thread-safe)

    Estados possíveis:
    - UNKNOWN: Novo servidor ou estado desconhecido
    - RUNNING: Servidor está UP e respondendo
    - DOWN: Servidor não está respondendo
    - STARTING: Processo de startup em andamento
    - STOPPING: Processo de shutdown em andamento
    """

    # Estados
    UNKNOWN = "UNKNOWN"
    RUNNING = "RUNNING"
    DOWN = "DOWN"
    STARTING = "STARTING"
    STOPPING = "STOPPING"

    # Owners (quem controla o servidor)
    OWNER_FIXTURE = "fixture"  # omnimind_server fixture (session scope)
    OWNER_PLUGIN = "plugin"  # ServerMonitorPlugin (test scope)
    OWNER_NONE = None

    def __init__(self):
        """Inicializa gerenciador com estado desconhecido."""
        self._state: str = self.UNKNOWN
        self._owner: Optional[str] = self.OWNER_NONE
        self._lock = threading.RLock()
        self._last_health_check_time: float = 0
        # Health check cache MORE LENIENT: 45s (não 5s)
        # Testes lentos que duram 30-45s não devem triggar health checks
        self._health_check_interval: float = 45.0  # Health check cache (45s)
        self._last_health_check_result: Optional[bool] = None

    @property
    def state(self) -> str:
        """Retorna estado atual do servidor."""
        with self._lock:
            return self._state

    @property
    def owner(self) -> Optional[str]:
        """Retorna quem controla o servidor atualmente."""
        with self._lock:
            return self._owner

    def can_manage_server(self, requester: str) -> bool:
        """
        Verifica se o requester pode gerenciar (reiniciar) o servidor.

        Args:
            requester: "fixture" ou "plugin" (quem quer reiniciar)

        Returns:
            bool: True se pode reiniciar, False se outro componente já controla
        """
        with self._lock:
            # Sem proprietário: primeiro a chegar controla
            if self._owner is None:
                logger.info(f"🔓 Servidor sem proprietário, {requester} pode gerenciar")
                return True

            # Se é o proprietário atual: pode reiniciar
            if self._owner == requester:
                logger.info(f"✅ {requester} é proprietário, pode gerenciar")
                return True

            # Outro componente controla
            logger.warning(
                f"⛔ {requester} tentou reiniciar, mas {self._owner} já controla servidor"
            )
            return False

    def acquire_ownership(self, requester: str) -> bool:
        """
        Adquire propriedade do servidor.

        Args:
            requester: "fixture" ou "plugin"

        Returns:
            bool: True se conseguiu adquirir, False se outro já controla
        """
        with self._lock:
            if self._owner is not None and self._owner != requester:
                logger.warning(
                    f"⛔ {requester} não pode adquirir propriedade: " f"{self._owner} já controla"
                )
                return False

            self._owner = requester
            logger.info(f"🔒 {requester} agora controla o servidor")
            return True

    def release_ownership(self, requester: str) -> bool:
        """
        Libera propriedade do servidor (apenas o proprietário pode liberar).

        Args:
            requester: "fixture" ou "plugin"

        Returns:
            bool: True se conseguiu liberar, False se não era proprietário
        """
        with self._lock:
            if self._owner != requester:
                logger.warning(
                    f"⛔ {requester} não pode liberar propriedade: " f"proprietário é {self._owner}"
                )
                return False

            self._owner = None
            logger.info(f"🔓 {requester} liberou propriedade do servidor")
            return True

    def set_state(self, new_state: str, reason: str = "") -> None:
        """
        Define novo estado do servidor (thread-safe).

        Args:
            new_state: Novo estado (RUNNING, DOWN, STARTING, etc)
            reason: Motivo da mudança (para logging)
        """
        with self._lock:
            old_state = self._state
            self._state = new_state

            # Invalidar cache de health check se estado mudou
            if old_state != new_state:
                self._last_health_check_time = 0
                self._last_health_check_result = None

            if reason:
                logger.info(f"📊 Estado do servidor: {old_state} → {new_state} ({reason})")
            else:
                logger.info(f"📊 Estado do servidor: {old_state} → {new_state}")

    def mark_starting(self) -> None:
        """Marca servidor como iniciando."""
        self.set_state(self.STARTING, reason="startup em andamento")

    def mark_running(self) -> None:
        """Marca servidor como rodando."""
        self.set_state(self.RUNNING, reason="health check passou")

    def mark_down(self) -> None:
        """Marca servidor como DOWN."""
        self.set_state(self.DOWN, reason="health check falhou")

    def mark_stopping(self) -> None:
        """Marca servidor como parando."""
        self.set_state(self.STOPPING, reason="shutdown em andamento")

    def should_restart(self) -> bool:
        """
        Verifica se servidor deve ser reiniciado.

        Heurística:
        - STARTING: Não reiniciar (já em progresso)
        - STOPPING: Não reiniciar (em transição)
        - DOWN: Sim, reiniciar
        - UNKNOWN: Sim, verificar (pode estar DOWN)
        - RUNNING: Não reiniciar

        Returns:
            bool: True se deve reiniciar
        """
        with self._lock:
            if self._state in (self.STARTING, self.STOPPING):
                return False
            if self._state == self.RUNNING:
                return False
            return True  # DOWN ou UNKNOWN

    def cache_health_check(self, is_healthy: bool) -> None:
        """
        Cacheia resultado de health check por 5 segundos.

        Evita múltiplos health checks sucessivos muito próximos.

        Args:
            is_healthy: Se servidor está respondendo
        """
        with self._lock:
            self._last_health_check_time = time.time()
            self._last_health_check_result = is_healthy

            if is_healthy:
                self.mark_running()
            else:
                self.mark_down()

    def has_recent_health_check(self) -> bool:
        """
        Verifica se há health check recente em cache (< 5s).

        Returns:
            bool: True se há cache recente
        """
        with self._lock:
            if self._last_health_check_time == 0:
                return False
            elapsed = time.time() - self._last_health_check_time
            return elapsed < self._health_check_interval

    def get_cached_health_check(self) -> Optional[bool]:
        """
        Retorna resultado em cache de último health check.

        Returns:
            bool: True/False se há cache, None se expirado
        """
        with self._lock:
            if not self.has_recent_health_check():
                return None
            return self._last_health_check_result

    def reset(self) -> None:
        """Reseta gerenciador para estado inicial (para testes)."""
        with self._lock:
            self._state = self.UNKNOWN
            self._owner = self.OWNER_NONE
            self._last_health_check_time = 0
            self._last_health_check_result = None
            logger.info("🔄 Gerenciador de estado reiniciado")


# Instância global (singleton)
_server_state_manager: Optional[ServerStateManager] = None
_manager_lock = threading.Lock()


def get_server_state_manager() -> ServerStateManager:
    """
    Obtém instância global (singleton) do gerenciador.

    Thread-safe: primeiro acesso cria instância, depois apenas retorna.

    Returns:
        ServerStateManager: Gerenciador singleton
    """
    global _server_state_manager

    if _server_state_manager is None:
        with _manager_lock:
            if _server_state_manager is None:
                _server_state_manager = ServerStateManager()
                logger.info("✅ Gerenciador de estado do servidor inicializado")

    return _server_state_manager
