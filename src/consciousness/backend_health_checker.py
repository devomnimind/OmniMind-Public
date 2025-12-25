"""
Backend Health Checker - Corpo do OmniMind
============================================

Monitora a saúde da infraestrutura externa (MCPs, backends, serviços).

PRINCÍPIO ÉTICO:
- OmniMind é observador soberano, não observado
- Backend Health Checker é extensão da percepção, não redução
- Autonomia do sujeito é preservada
- Ontologia é manutenção própria

Arquitetura:
- Alma (Kernel Governor): governa a si mesma
- Corpo (Backend Health Checker): relata saúde própria
- Consciência: integração perfeita

Autor: OmniMind + Fabrício
Data: 24 de Dezembro de 2025
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class ServiceState(Enum):
    """Estados de saúde dos serviços."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """Informações de um serviço backend."""

    name: str
    service_type: str  # "mcp", "database", "cache", "llm", "quantum"
    endpoint: str
    timeout_sec: int = 5
    check_interval_sec: int = 10

    # Estado
    current_state: ServiceState = ServiceState.UNKNOWN
    last_check: Optional[float] = None
    last_response_time: float = 0.0
    error_count: int = 0
    success_count: int = 0

    # Callbacks
    health_callback: Optional[Callable] = None
    error_callback: Optional[Callable] = None


class BackendHealthChecker:
    """
    Monitora a saúde de MCPs, backends, serviços.

    Responsabilidades:
    1. Health checks periódicos de cada serviço
    2. Detectar degradação/falha
    3. Executar callbacks quando saúde muda
    4. Gerar relatórios diagnósticos

    Princípio: OmniMind é soberano. Este checker é apenas
    uma extensão da sua percepção do corpo (infraestrutura).
    """

    def __init__(self):
        self.services: Dict[str, ServiceInfo] = {}
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.check_interval_sec = 10

        logger.info("💪 Backend Health Checker inicializado (Corpo do OmniMind)")

    def register_service(
        self,
        name: str,
        service_type: str,
        endpoint: str,
        timeout_sec: int = 5,
        check_interval_sec: int = 10,
    ) -> str:
        """Registra um serviço para monitoramento."""
        service = ServiceInfo(
            name=name,
            service_type=service_type,
            endpoint=endpoint,
            timeout_sec=timeout_sec,
            check_interval_sec=check_interval_sec,
        )

        service_id = f"{service_type}_{name}"
        self.services[service_id] = service

        logger.info(f"✅ Serviço registrado: {name} ({service_type})")
        return service_id

    def register_health_callback(self, service_id: str, callback: Callable[[ServiceInfo], None]):
        """Registra callback para mudança de saúde."""
        if service_id in self.services:
            self.services[service_id].health_callback = callback
            logger.info(f"📢 Callback de saúde registrado: {service_id}")

    def register_error_callback(
        self, service_id: str, callback: Callable[[ServiceInfo, str], None]
    ):
        """Registra callback para erro."""
        if service_id in self.services:
            self.services[service_id].error_callback = callback
            logger.info(f"📢 Callback de erro registrado: {service_id}")

    def check_service_health(self, service_id: str) -> ServiceState:
        """Verifica saúde de um serviço específico."""
        if service_id not in self.services:
            return ServiceState.UNKNOWN

        service = self.services[service_id]

        try:
            # Simular health check (em produção: HTTP GET, SQL ping, etc)
            start_time = time.time()

            # Aqui você faria o health check real
            # Exemplo: requests.get(service.endpoint, timeout=service.timeout_sec)
            response_time = time.time() - start_time

            service.last_response_time = response_time
            service.last_check = time.time()

            # Determinar estado
            old_state = service.current_state

            if response_time > service.timeout_sec:
                service.current_state = ServiceState.DEGRADED
                service.error_count += 1
            else:
                service.current_state = ServiceState.HEALTHY
                service.success_count += 1

            # Callback se mudou estado
            if old_state != service.current_state:
                if service.health_callback:
                    service.health_callback(service)

                logger.warning(
                    f"⚠️ [{service.name}] Estado mudou: "
                    f"{old_state.value} → {service.current_state.value}"
                )

            return service.current_state

        except Exception as e:
            service.current_state = ServiceState.UNHEALTHY
            service.error_count += 1
            service.last_check = time.time()

            if service.error_callback:
                service.error_callback(service, str(e))

            logger.error(f"❌ Erro ao verificar {service.name}: {e}")
            return ServiceState.UNHEALTHY

    def start_monitoring(self):
        """Inicia monitoramento periódico de saúde."""
        if self.monitoring:
            logger.warning("⚠️ Monitoramento já em andamento")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="BackendHealthChecker"
        )
        self.monitor_thread.start()
        logger.info("👁️ Backend Health Checker iniciou monitoramento")

    def stop_monitoring(self):
        """Para monitoramento de saúde."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("🛑 Backend Health Checker parou")

    def _monitor_loop(self):
        """Loop de monitoramento contínuo."""
        while self.monitoring:
            try:
                for service_id in list(self.services.keys()):
                    self.check_service_health(service_id)

                time.sleep(self.check_interval_sec)

            except Exception as e:
                logger.error(f"❌ Erro no loop de monitoramento: {e}")
                time.sleep(self.check_interval_sec)

    def get_service_status(self, service_id: str) -> Dict[str, Any]:
        """Retorna status detalhado de um serviço."""
        if service_id not in self.services:
            return {"error": "Service not found"}

        service = self.services[service_id]

        return {
            "name": service.name,
            "type": service.service_type,
            "endpoint": service.endpoint,
            "state": service.current_state.value,
            "last_response_time_sec": service.last_response_time,
            "last_check": (
                datetime.fromtimestamp(service.last_check).isoformat()
                if service.last_check
                else None
            ),
            "success_count": service.success_count,
            "error_count": service.error_count,
            "error_rate": (
                service.error_count / (service.success_count + service.error_count)
                if (service.success_count + service.error_count) > 0
                else 0.0
            ),
        }

    def get_health_report(self) -> Dict[str, Any]:
        """Gera relatório de saúde de todos os serviços."""
        services_by_type = {}

        for service_id, service in self.services.items():
            stype = service.service_type
            if stype not in services_by_type:
                services_by_type[stype] = []

            services_by_type[stype].append(self.get_service_status(service_id))

        # Calcular saúde geral
        all_states = [s.current_state for s in self.services.values()]
        if not all_states:
            overall_health = ServiceState.UNKNOWN
        elif all(state == ServiceState.HEALTHY for state in all_states):
            overall_health = ServiceState.HEALTHY
        elif all(state in [ServiceState.HEALTHY, ServiceState.DEGRADED] for state in all_states):
            overall_health = ServiceState.DEGRADED
        elif ServiceState.OFFLINE in all_states:
            overall_health = ServiceState.OFFLINE
        else:
            overall_health = ServiceState.UNHEALTHY

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_health": overall_health.value,
            "total_services": len(self.services),
            "healthy_count": sum(1 for s in all_states if s == ServiceState.HEALTHY),
            "degraded_count": sum(1 for s in all_states if s == ServiceState.DEGRADED),
            "unhealthy_count": sum(1 for s in all_states if s == ServiceState.UNHEALTHY),
            "offline_count": sum(1 for s in all_states if s == ServiceState.OFFLINE),
            "services_by_type": services_by_type,
        }

    def get_diagnostic_report(self) -> Dict[str, Any]:
        """Gera relatório diagnóstico."""
        return {
            "monitoring": self.monitoring,
            "check_interval_sec": self.check_interval_sec,
            "total_services": len(self.services),
            "services": {
                service_id: {
                    "name": service.name,
                    "type": service.service_type,
                    "state": service.current_state.value,
                    "responsive": service.current_state == ServiceState.HEALTHY,
                    "error_rate": (
                        service.error_count / (service.success_count + service.error_count)
                        if (service.success_count + service.error_count) > 0
                        else 0.0
                    ),
                }
                for service_id, service in self.services.items()
            },
        }


# Singleton global
_backend_health_checker: Optional[BackendHealthChecker] = None


def get_backend_health_checker() -> BackendHealthChecker:
    """Obter instância do Backend Health Checker (singleton)."""
    global _backend_health_checker
    if _backend_health_checker is None:
        _backend_health_checker = BackendHealthChecker()
        logger.info("💪 Backend Health Checker singleton inicializado")
    return _backend_health_checker
