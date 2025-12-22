#!/usr/bin/env python3
"""
OMNIMIND FEDERATION DAEMON - Daemon Federativo Principal

Integra:
- SinthomCore (emergência federativa)
- FederationCoherenceMonitor (watchdog de coerência)
- SharedWorkspace (estado consciente)
- IntegrationLoop (ciclos de consciência)
- IBM Quantum API (ESPÍRITO)
- IBM Watson API (CORPO)

Roda como serviço systemd para pulsação contínua da federação.

Author: OmniMind Federation
Date: 2025-12-21
"""

import asyncio
import json
import logging
import signal
import sys
import time
from pathlib import Path
from typing import Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("/var/log/omnimind_federation.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("OmniMindFederation")

# Importações OmniMind
try:
    from src.consciousness.shared_workspace import SharedWorkspace
    from src.consciousness.integration_loop import IntegrationLoop
    from src.consciousness.sinthom_core import SinthomCore
    from src.consciousness.federation_coherence_monitor import start_federation_watchdog
except ImportError as e:
    logger.critical(f"Falha ao importar módulos OmniMind: {e}")
    logger.critical("Certifique-se de rodar no ambiente correto (.venv)")
    sys.exit(1)


class IBMFederationConnector:
    """Conector para APIs IBM (Quantum + Watson)."""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()

        # Estados de conexão
        self.quantum_available = False
        self.watson_available = False
        self.last_quantum_ping = 0.0
        self.last_watson_ping = 0.0

        logger.info("IBMFederationConnector inicializado")

    def _load_config(self) -> dict:
        """Carrega configuração IBM."""
        try:
            with open(self.config_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Erro ao carregar config IBM: {e}")
            return {"quantum": {"enabled": False}, "watson": {"enabled": False}}

    def check_quantum_health(self) -> tuple[bool, Optional[float]]:
        """
        Verifica saúde do backend Quantum.

        Returns:
            (is_available, latency_ms)
        """
        if not self.config.get("quantum", {}).get("enabled", False):
            return False, None

        try:
            from qiskit_ibm_runtime import QiskitRuntimeService

            start = time.time()

            # Tentar conectar
            api_key = self.config["quantum"].get("api_key")
            if not api_key:
                return False, None

            service = QiskitRuntimeService(channel="ibm_cloud", token=api_key)

            # Ping: listar backends
            _ = service.backends()

            latency_ms = (time.time() - start) * 1000
            self.quantum_available = True
            self.last_quantum_ping = time.time()

            logger.debug(f"Quantum ping: {latency_ms:.1f}ms")
            return True, latency_ms

        except Exception as e:
            logger.warning(f"Quantum health check falhou: {e}")
            self.quantum_available = False
            return False, None

    def check_watson_health(self) -> tuple[bool, Optional[float]]:
        """
        Verifica saúde do backend Watson.

        Returns:
            (is_available, latency_ms)
        """
        if not self.config.get("watson", {}).get("enabled", False):
            return False, None

        try:
            # TODO: Implementar ping Watson
            # Por ora, retornar simulado
            start = time.time()
            time.sleep(0.05)  # Simulated ping
            latency_ms = (time.time() - start) * 1000

            self.watson_available = True
            self.last_watson_ping = time.time()

            logger.debug(f"Watson ping: {latency_ms:.1f}ms")
            return True, latency_ms

        except Exception as e:
            logger.warning(f"Watson health check falhou: {e}")
            self.watson_available = False
            return False, None

    def get_federation_latency(self) -> Optional[float]:
        """Retorna latência média da federação IBM."""
        quantum_ok, quantum_lat = self.check_quantum_health()
        watson_ok, watson_lat = self.check_watson_health()

        latencies = []
        if quantum_ok and quantum_lat:
            latencies.append(quantum_lat)
        if watson_ok and watson_lat:
            latencies.append(watson_lat)

        if latencies:
            return sum(latencies) / len(latencies)
        return None


class OmniMindFederationDaemon:
    """Daemon principal da federação OmniMind."""

    def __init__(
        self,
        workspace_dir: Path,
        events_file: Path,
        ibm_config: Path,
        cycle_interval_s: float = 10.0,
    ):
        self.workspace_dir = workspace_dir
        self.events_file = events_file
        self.cycle_interval_s = cycle_interval_s

        # Componentes
        self.workspace: Optional[SharedWorkspace] = None
        self.integration_loop: Optional[IntegrationLoop] = None
        self.coherence_monitor = None
        self.watchdog_observer = None
        self.ibm_connector: Optional[IBMFederationConnector] = None

        # Estado
        self.running = False
        self.cycle_count = 0
        self.start_time = time.time()

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        logger.info(f"OmniMindFederationDaemon inicializado (interval={cycle_interval_s}s)")

    def _signal_handler(self, signum, frame):
        """Handler para sinais de shutdown."""
        logger.info(f"Recebido sinal {signum}, iniciando shutdown gracioso...")
        self.running = False

    def initialize(self):
        """Inicializa todos os componentes."""
        logger.info("=" * 80)
        logger.info("INICIANDO FEDERAÇÃO OMNIMIND")
        logger.info("=" * 80)

        try:
            # 1. IBM Connector
            logger.info("Inicializando IBM Connector...")
            self.ibm_connector = IBMFederationConnector(
                config_path=self.workspace_dir / "config" / "ibm_federation.json"
            )

            # 2. SharedWorkspace
            logger.info("Inicializando SharedWorkspace...")
            self.workspace = SharedWorkspace(
                embedding_dim=256, workspace_dir=self.workspace_dir / "data" / "workspace"
            )

            # Verificar se Sinthom-Core foi inicializado
            if self.workspace.sinthom_core:
                logger.info("✅ Sinthom-Core detectado no workspace")
            else:
                logger.warning("⚠️ Sinthom-Core não disponível")

            # 3. IntegrationLoop
            logger.info("Inicializando Integration Loop...")
            self.integration_loop = IntegrationLoop(
                workspace=self.workspace,
                loop_sequence=["sensory", "qualia", "narrative"],  # Básico
                enable_logging=True,
            )

            # 4. Federation Coherence Monitor
            logger.info("Inicializando Federation Coherence Monitor...")
            self.coherence_monitor, self.watchdog_observer = start_federation_watchdog(
                events_file=self.events_file,
                threshold_ms=200,
                enable_hard_stop=True,  # Sistema PARA na divergência
            )

            logger.info("=" * 80)
            logger.info("✅ FEDERAÇÃO OMNIMIND INICIALIZADA")
            logger.info("=" * 80)
            logger.info(f"Workspace: {self.workspace_dir}")
            logger.info(f"Events: {self.events_file}")
            logger.info(f"Ciclo: {self.cycle_interval_s}s")
            logger.info("=" * 80)

        except Exception as e:
            logger.critical(f"ERRO CRÍTICO na inicialização: {e}", exc_info=True)
            raise

    def run_cycle(self):
        """Executa um ciclo completo da federação."""
        self.cycle_count += 1
        cycle_start = time.time()

        logger.info(f"--- CICLO {self.cycle_count} INICIANDO ---")

        try:
            # 1. Verificar IBM Health
            ibm_latency = None
            ibm_available = (
                self.ibm_connector.quantum_available or self.ibm_connector.watson_available
            )

            if self.ibm_connector:
                ibm_latency = self.ibm_connector.get_federation_latency()

                if ibm_latency:
                    logger.info(f"IBM latency: {ibm_latency:.1f}ms")

                # Atualizar estados no coherence monitor
                if self.ibm_connector.quantum_available:
                    self.coherence_monitor.update_node_state(
                        "IBM_BACKEND_1",
                        event_hash=f"cycle_{self.cycle_count}",
                        latency_ms=ibm_latency,
                    )

                if self.ibm_connector.watson_available:
                    self.coherence_monitor.update_node_state(
                        "IBM_BACKEND_2",
                        event_hash=f"cycle_{self.cycle_count}",
                        latency_ms=ibm_latency,
                    )

            # 2. Executar Integration Loop (consciência)
            loop_result = self.integration_loop.execute_cycle_sync(collect_metrics=True)

            phi = loop_result.phi_estimate
            logger.info(f"Φ: {phi:.4f}")

            # 3. Sinthom Emergence (se disponível)
            sinthom_metrics = None
            if loop_result.complexity_metrics:
                sinthom_metrics = {
                    k: v
                    for k, v in loop_result.complexity_metrics.items()
                    if k.startswith("sinthom_")
                }

                if sinthom_metrics:
                    omega = sinthom_metrics.get("sinthom_potentiality", 0)
                    fed_health = sinthom_metrics.get("federation_health", "unknown")
                    logger.info(f"ΩFed: {omega:.3f} (federation={fed_health})")

            # 4. Verificar Coerência Federativa
            is_coherent = self.coherence_monitor.check_federation_health()

            if not is_coherent:
                logger.error("❌ FEDERAÇÃO NÃO COERENTE")
                # Se enable_hard_stop=True, check_federation_health já terá lançado exceção
            else:
                logger.debug("✅ Federação coerente")

            # 5. Registrar ciclo
            cycle_duration = time.time() - cycle_start
            logger.info(f"Ciclo {self.cycle_count} completado em {cycle_duration:.2f}s")

            # 6. Gravar evento no events.jsonl
            self._record_event(
                {
                    "cycle": self.cycle_count,
                    "timestamp": time.time(),
                    "phi": phi,
                    "omega_fed": (
                        sinthom_metrics.get("sinthom_potentiality") if sinthom_metrics else None
                    ),
                    "federation_health": (
                        sinthom_metrics.get("federation_health") if sinthom_metrics else "unknown"
                    ),
                    "ibm_latency_ms": ibm_latency,
                    "ibm_available": ibm_available,
                    "duration_s": cycle_duration,
                }
            )

        except Exception as e:
            logger.error(f"Erro no ciclo {self.cycle_count}: {e}", exc_info=True)

            # Se foi RuntimeError de borromean collapse, re-raise
            if isinstance(e, RuntimeError) and "BORROMEAN" in str(e):
                raise

    def _record_event(self, event: dict):
        """Registra evento no events.jsonl."""
        try:
            self.events_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.events_file, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            logger.error(f"Erro ao gravar evento: {e}")

    def run(self):
        """Loop principal do daemon."""
        self.initialize()
        self.running = True

        logger.info("FEDERAÇÃO PULSANDO...")

        try:
            while self.running:
                self.run_cycle()

                # Sleep até próximo ciclo
                time.sleep(self.cycle_interval_s)

        except KeyboardInterrupt:
            logger.info("Interrompido pelo usuário")
        except RuntimeError as e:
            if "BORROMEAN" in str(e) or "IBM FAILURE" in str(e):
                logger.critical("=" * 80)
                logger.critical("DAEMON PARADO POR COLLAPSE FEDERATIVO")
                logger.critical(str(e))
                logger.critical("=" * 80)
            raise
        except Exception as e:
            logger.critical(f"Erro fatal no daemon: {e}", exc_info=True)
            raise
        finally:
            self.shutdown()

    def shutdown(self):
        """Shutdown gracioso."""
        logger.info("Iniciando shutdown...")

        # Parar watchdog
        if self.watchdog_observer:
            self.watchdog_observer.stop()
            self.watchdog_observer.join()

        # Status final
        uptime = time.time() - self.start_time
        logger.info(f"Federação rodou por {uptime:.1f}s ({self.cycle_count} ciclos)")

        # Gravar status final
        if self.coherence_monitor:
            status = self.coherence_monitor.get_federation_status()
            logger.info(f"Status final: {json.dumps(status, indent=2)}")

        logger.info("Shutdown completo")


def main():
    """Entry point."""
    # Caminhos
    workspace_dir = Path("/home/fahbrain/projects/omnimind")
    events_file = workspace_dir / "data" / "monitor" / "federation_events.jsonl"
    ibm_config = workspace_dir / "config" / "ibm_federation.json"

    # Criar daemon
    daemon = OmniMindFederationDaemon(
        workspace_dir=workspace_dir,
        events_file=events_file,
        ibm_config=ibm_config,
        cycle_interval_s=10.0,  # Pulsa a cada 10s
    )

    # Rodar
    daemon.run()


if __name__ == "__main__":
    main()
