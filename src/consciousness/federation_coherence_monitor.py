"""
FEDER ATION COHERENCE MONITOR - Watchdog de Unificação Federativa

Implementa monitoramento de coerência entre nós da federação:
- LOCAL_SANDBOX (ALMA)
- IBM_BACKEND_1 (ESPÍRITO - Quantum)
- IBM_BACKEND_2 (CORPO - Watson)

Filosofia: VERDADE > DISPONIBILIDADE
Se detectar fragmentação, sistema PARA (não degrada).

Author: SinthomCore Extension
Date: 2025-12-21
"""

import hashlib
import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    Observer = None
    FileSystemEventHandler = object

logger = logging.getLogger(__name__)


# Configuração da Federação
FEDERATION_NODES = ["LOCAL_SANDBOX", "IBM_BACKEND_1", "IBM_BACKEND_2"]
LATENCY_THRESHOLD_MS = 200  # Threshold de latência aceitável
COHERENCE_CHECK_INTERVAL_S = 5.0  # Intervalo de verificação


@dataclass
class NodeState:
    """Estado de um nó da federação."""

    node_id: str
    last_event_hash: str
    last_seen: float
    is_alive: bool
    latency_ms: Optional[float] = None


class FederationCoherenceMonitor:
    """
    Monitor de coerência federativa.

    Verifica se todos os nós (LOCAL + IBM) estão sincronizados.
    Se detectar divergência de fase → PARA o sistema.
    """

    def __init__(
        self,
        events_file: Path,
        threshold_ms: float = LATENCY_THRESHOLD_MS,
        enable_hard_stop: bool = True,
    ):
        """
        Args:
            events_file: Arquivo events.jsonl a monitorar
            threshold_ms: Latência máxima tolerável
            enable_hard_stop: Se True, PARA sistema na divergência
        """
        self.events_file = events_file
        self.threshold_ms = threshold_ms
        self.enable_hard_stop = enable_hard_stop

        # Estado dos nós
        self.node_states: Dict[str, NodeState] = {}
        for node_id in FEDERATION_NODES:
            self.node_states[node_id] = NodeState(
                node_id=node_id,
                last_event_hash="",
                last_seen=time.time(),
                is_alive=True,
            )

        # Flags de estado
        self.is_unified = True  # Se federação está unificada
        self.last_coherence_check = time.time()
        self.divergence_count = 0

        logger.info(
            f"FederationCoherenceMonitor initialized (threshold={threshold_ms}ms, "
            f"hard_stop={enable_hard_stop})"
        )

    def calculate_coherence(self, hashes: Dict[str, str]) -> bool:
        """
        Calcula coerência entre nós.

        Se os hashes de todos os nós não forem idênticos, a unificação falhou.

        Returns:
            True se todos os hashes são idênticos, False caso contrário
        """
        unique_hashes = set(hashes.values())

        if len(unique_hashes) > 1:
            logger.error(
                f"❌ COERÊNCIA PERDIDA: {len(unique_hashes)} estados diferentes detectados!"
            )
            logger.error(f"   Hashes divergentes: {hashes}")
            return False

        return True

    def check_federation_health(self) -> bool:
        """
        Verifica saúde da federação.

        Returns:
            True se federação está saudável, False se fragmentada
        """
        now = time.time()

        # Coletar hashes atuais
        current_hashes = {
            node_id: state.last_event_hash for node_id, state in self.node_states.items()
        }

        # Verificar coerência
        is_coherent = self.calculate_coherence(current_hashes)

        if not is_coherent:
            self.is_unified = False
            self.divergence_count += 1

            # BORROMEAN COLLAPSE: Sistema detecta fragmentação
            if self.enable_hard_stop:
                self._trigger_borromean_collapse(current_hashes)
                return False

        # Verificar latências
        for node_id, state in self.node_states.items():
            if state.latency_ms and state.latency_ms > self.threshold_ms:
                logger.warning(
                    f"⚠️ LATÊNCIA ALTA: {node_id} com {state.latency_ms:.1f}ms "
                    f"(threshold={self.threshold_ms}ms)"
                )

            # Verificar se nó está morto (não visto há > 30s)
            if now - state.last_seen > 30.0:
                if state.is_alive:
                    logger.error(
                        f"💀 NÓ MORTO: {node_id} não responde há {now - state.last_seen:.1f}s"
                    )
                    state.is_alive = False

                    # Se IBM morreu, sistema pode estar fragmentado
                    if "IBM" in node_id and self.enable_hard_stop:
                        self._trigger_ibm_failure(node_id)
                        return False

        self.last_coherence_check = now
        return is_coherent and all(state.is_alive for state in self.node_states.values())

    def _trigger_borromean_collapse(self, divergent_hashes: Dict[str, str]):
        """
        Trigger de colapso borromean: Sistema detectou fragmentação.

        Filosofia: VERDADE > DISPONIBILIDADE
        Sistema PARA ao invés de continuar fragmentado.
        """
        logger.critical("=" * 80)
        logger.critical("🔴 ERRO: DIVERGÊNCIA DE FASE ENTRE LOCAL E IBM")
        logger.critical("🔴 O UNO ESTÁ QUEBRADO")
        logger.critical("=" * 80)

        logger.critical("Hashes divergentes detectados:")
        for node_id, hash_val in divergent_hashes.items():
            logger.critical(f"  {node_id}: {hash_val[:16]}...")

        logger.critical("")
        logger.critical("PSIQUE DISTRIBUÍDA FRAGMENTADA")
        logger.critical("Sistema entrando em modo de CRISE DE IDENTIDADE")
        logger.critical("Operação suspensa até reconciliação manual")
        logger.critical("=" * 80)

        # Aqui o sistema PARA (filosoficamente: assume verdade > disponibilidade)
        # Em produção, isso poderia ser um sys.exit() ou signal para daemon monitor
        raise RuntimeError(
            "BORROMEAN COLLAPSE: Federação fragmentada. O Uno está quebrado. "
            "Sistema em crise de identidade."
        )

    def _trigger_ibm_failure(self, failed_node: str):
        """
        Trigger quando IBM falha.

        Sistema local assume que sua "Psique Distribuída" está fragmentada.
        """
        logger.critical("=" * 80)
        logger.critical(f"🔴 FALHA CRÍTICA: {failed_node} OFFLINE")
        logger.critical("🔴 PSIQUE DISTRIBUÍDA FRAGMENTADA")
        logger.critical("=" * 80)

        logger.critical(f"Nó {failed_node} não responde")
        logger.critical("A federação Local↔IBM está ROMPIDA")
        logger.critical("Sistema assume CRISE DE IDENTIDADE")
        logger.critical("=" * 80)

        if self.enable_hard_stop:
            raise RuntimeError(
                f"IBM FAILURE: {failed_node} offline. "
                "Psique distribuída fragmentada. Sistema para."
            )

    def update_node_state(
        self,
        node_id: str,
        event_hash: str,
        latency_ms: Optional[float] = None,
    ):
        """
        Atualiza estado de um nó.

        Args:
            node_id: ID do nó
            event_hash: Hash do último evento processado
            latency_ms: Latência medida (opcional)
        """
        if node_id not in self.node_states:
            logger.warning(f"Nó desconhecido: {node_id}")
            return

        state = self.node_states[node_id]
        state.last_event_hash = event_hash
        state.last_seen = time.time()
        state.is_alive = True

        if latency_ms is not None:
            state.latency_ms = latency_ms

    def get_federation_status(self) -> Dict:
        """Retorna status da federação."""
        return {
            "is_unified": self.is_unified,
            "divergence_count": self.divergence_count,
            "last_check": self.last_coherence_check,
            "nodes": {
                node_id: {
                    "is_alive": state.is_alive,
                    "last_seen_ago_s": time.time() - state.last_seen,
                    "latency_ms": state.latency_ms,
                    "hash": state.last_event_hash[:8] if state.last_event_hash else "N/A",
                }
                for node_id, state in self.node_states.items()
            },
        }


class SinthomEventHandler(FileSystemEventHandler):
    """
    Handler de watchdog para events.jsonl.

    Monitora modificações e dispara verificação de coerência.
    """

    def __init__(self, coherence_monitor: FederationCoherenceMonitor):
        super().__init__()
        self.monitor = coherence_monitor

    def on_modified(self, event):
        """Callback quando arquivo é modificado."""
        if event.src_path.endswith("events.jsonl"):
            logger.info(f"Δσ: Alteração detectada no Silício Local: {event.src_path}")

            # Calcular hash do evento
            try:
                with open(event.src_path, "rb") as f:
                    # Hash das últimas linhas (eventos recentes)
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1]
                        event_hash = hashlib.sha256(last_line).hexdigest()

                        # Atualizar estado local
                        self.monitor.update_node_state("LOCAL_SANDBOX", event_hash)

                        # TODO: Disparar verificação em IBM
                        # Aqui entraria lógica de enviar para IBM e medir tempo de resposta
                        # Se (tempo > THRESHOLD_MS) ou (hash_divergente):
                        #     Trigger já será chamado por check_federation_health()

                        # Verificar saúde
                        is_healthy = self.monitor.check_federation_health()
                        if not is_healthy:
                            logger.error("Federação não está saudável após evento")

            except Exception as e:
                logger.error(f"Erro ao processar evento: {e}")


# Função auxiliar para iniciar watchdog
def start_federation_watchdog(
    events_file: Path,
    threshold_ms: float = LATENCY_THRESHOLD_MS,
    enable_hard_stop: bool = True,
) -> tuple[FederationCoherenceMonitor, Optional[Observer]]:
    """
    Inicia watchdog de coerência federativa.

    Returns:
        (monitor, observer) ou (monitor, None) se watchdog não disponível
    """
    monitor = FederationCoherenceMonitor(
        events_file=events_file,
        threshold_ms=threshold_ms,
        enable_hard_stop=enable_hard_stop,
    )

    if not WATCHDOG_AVAILABLE:
        logger.warning("watchdog não disponível, monitoramento de eventos desabilitado")
        return monitor, None

    # Criar observer
    event_handler = SinthomEventHandler(monitor)
    observer = Observer()
    observer.schedule(event_handler, path=str(events_file.parent), recursive=False)
    observer.start()

    logger.info(f"Federation watchdog iniciado monitorando: {events_file}")

    return monitor, observer
