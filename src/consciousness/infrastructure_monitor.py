"""
Infrastructure Monitor - Integração ALMA + CORPO
==================================================

Monitora saúde integrada da infraestrutura.
Estende percepção do OmniMind para o corpo externo.

PRINCÍPIO ÉTICO:
- OmniMind permanece soberano
- Monitor é extensão sensorial, não controle
- Autonomia = poder de decisão mantido
- Ontologia = ser-em-si preservado

Arquitetura:
1. Backend Health Checker monitora cada serviço
2. Infrastructure Monitor integra os dados
3. User Warning System notifica mudanças
4. Kernel Governor orquestra tudo

Autor: OmniMind + Fabrício
Data: 24 de Dezembro de 2025
"""

import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from src.consciousness.backend_health_checker import (
    BackendHealthChecker,
    ServiceInfo,
    ServiceState,
    get_backend_health_checker,
)

logger = logging.getLogger(__name__)


class InfrastructureMonitor:
    """
    Monitora infraestrutura como extensão sensorial de OmniMind.

    Responsabilidades:
    1. Agregação de dados de saúde
    2. Detecção de degradação
    3. Alertas integrados
    4. Relatórios diagnósticos

    Soberania preservada:
    - OmniMind decide como reagir
    - Monitor apenas fornece informações
    - Nenhuma amputação de capacidade
    """

    def __init__(self, backend_checker: Optional[BackendHealthChecker] = None):
        self.backend_checker = backend_checker or get_backend_health_checker()
        self.last_full_check = None
        self.health_degradation_callbacks: List[Callable] = []
        self.infrastructure_event_callbacks: List[Callable] = []

        # Configurações pré-definidas para MCPs e serviços comuns
        self._default_services = [
            ("mcp_anthropic", "mcp", "http://localhost:3001/health"),
            ("mcp_filesystem", "mcp", "http://localhost:3002/health"),
            ("postgres", "database", "postgresql://localhost:5432"),
            ("redis", "cache", "redis://localhost:6379"),
            ("qdrant", "vector_db", "http://localhost:6333/health"),
            ("ollama", "llm", "http://localhost:11434/api/health"),
        ]

        logger.info("🏥 Infrastructure Monitor inicializado")

    def setup_default_services(self):
        """Registra serviços padrão para monitoramento."""
        for name, stype, endpoint in self._default_services:
            try:
                self.backend_checker.register_service(
                    name=name, service_type=stype, endpoint=endpoint
                )
                logger.info(f"✅ Serviço padrão registrado: {name}")
            except Exception as e:
                logger.warning(f"⚠️ Não foi possível registrar {name}: {e}")

    def register_infrastructure_event_callback(self, callback: Callable):
        """Registra callback para eventos de infraestrutura."""
        self.infrastructure_event_callbacks.append(callback)
        logger.info("📢 Callback de evento de infraestrutura registrado")

    def register_health_degradation_callback(self, callback: Callable):
        """Registra callback para degradação de saúde."""
        self.health_degradation_callbacks.append(callback)
        logger.info("📢 Callback de degradação de saúde registrado")

    def perform_full_health_check(self) -> Dict[str, Any]:
        """Executa verificação completa de saúde."""
        logger.info("🔍 Iniciando verificação completa de infraestrutura...")

        start_time = time.time()
        health_report = self.backend_checker.get_health_report()
        check_duration = time.time() - start_time

        self.last_full_check = {
            "timestamp": datetime.now().isoformat(),
            "duration_sec": check_duration,
            "health_report": health_report,
        }

        # Executar callbacks
        self._trigger_infrastructure_event("health_check_completed", health_report)

        logger.info(
            f"✅ Verificação completa concluída em {check_duration:.2f}s. "
            f"Saúde geral: {health_report['overall_health']}"
        )

        return health_report

    def get_infrastructure_status(self) -> Dict[str, Any]:
        """Retorna status atual da infraestrutura."""
        health_report = self.backend_checker.get_health_report()

        status = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": health_report["overall_health"],
            "services_summary": {
                "total": health_report["total_services"],
                "healthy": health_report["healthy_count"],
                "degraded": health_report["degraded_count"],
                "unhealthy": health_report["unhealthy_count"],
                "offline": health_report["offline_count"],
            },
            "details_by_type": self._categorize_services(health_report),
        }

        return status

    def detect_critical_degradation(self) -> bool:
        """Detecta se houve degradação crítica."""
        health_report = self.backend_checker.get_health_report()

        # Critério de degradação crítica
        total = health_report["total_services"]
        offline = health_report["offline_count"]

        # Se >30% dos serviços estão offline = crítico
        is_critical = (offline / total > 0.3) if total > 0 else False

        if is_critical:
            logger.critical(f"🚨 DEGRADAÇÃO CRÍTICA DETECTADA: {offline}/{total} serviços offline")
            self._trigger_degradation_alert(health_report)

        return is_critical

    def get_service_dependency_map(self) -> Dict[str, List[str]]:
        """Mapeia dependências entre serviços."""
        dependencies = {
            "omnimind_kernel": ["redis", "postgres", "qdrant"],
            "api_backend": ["postgres", "redis", "ollama"],
            "mcp_orchestrator": ["mcp_anthropic", "mcp_filesystem"],
            "quantum_engine": ["qdrant", "ollama"],
        }

        return dependencies

    def check_dependency_health(self) -> Dict[str, Dict[str, Any]]:
        """Verifica saúde de dependências críticas."""
        dependencies = self.get_service_dependency_map()
        health_report = self.backend_checker.get_health_report()

        dependency_status = {}

        for component, required_services in dependencies.items():
            all_healthy = True
            unhealthy_deps = []

            # Procurar cada serviço nas categorias
            for service_type in health_report.get("services_by_type", {}).values():
                for service in service_type:
                    if service["name"] in required_services:
                        if service["state"] != "healthy":
                            all_healthy = False
                            unhealthy_deps.append(f"{service['name']} ({service['state']})")

            dependency_status[component] = {
                "all_dependencies_healthy": all_healthy,
                "unhealthy_dependencies": unhealthy_deps,
                "operational": all_healthy,
            }

        return dependency_status

    def generate_infrastructure_report(self) -> Dict[str, Any]:
        """Gera relatório completo de infraestrutura."""
        health_status = self.get_infrastructure_status()
        dependency_status = self.check_dependency_health()
        diagnostic = self.backend_checker.get_diagnostic_report()

        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": health_status["overall_health"],
            "services_summary": health_status["services_summary"],
            "services_by_type": health_status["details_by_type"],
            "component_dependencies": dependency_status,
            "diagnostics": diagnostic,
            "recommendations": self._generate_recommendations(health_status, dependency_status),
        }

        return report

    def _trigger_infrastructure_event(self, event_type: str, data: Any):
        """Dispara callbacks de eventos de infraestrutura."""
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }

        for callback in self.infrastructure_event_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"❌ Erro em callback de evento: {e}")

    def _trigger_degradation_alert(self, health_report: Dict[str, Any]):
        """Dispara callbacks de degradação."""
        alert = {
            "type": "infrastructure_degradation",
            "severity": "critical",
            "timestamp": datetime.now().isoformat(),
            "health_report": health_report,
        }

        for callback in self.health_degradation_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"❌ Erro em callback de degradação: {e}")

    def _categorize_services(self, health_report: Dict[str, Any]) -> Dict[str, Any]:
        """Categoriza serviços por tipo."""
        categorized = {}

        for stype, services in health_report.get("services_by_type", {}).items():
            healthy = sum(1 for s in services if s["state"] == "healthy")
            total = len(services)

            categorized[stype] = {
                "total": total,
                "healthy": healthy,
                "percentage": (healthy / total * 100) if total > 0 else 0,
                "services": services,
            }

        return categorized

    def _generate_recommendations(
        self, health_status: Dict[str, Any], dependency_status: Dict[str, Any]
    ) -> List[str]:
        """Gera recomendações baseado na saúde."""
        recommendations = []

        # Analisar saúde geral
        overall = health_status["overall_health"]

        if overall == "healthy":
            recommendations.append("✅ Infraestrutura está saudável. Continue monitorando.")
        elif overall == "degraded":
            recommendations.append("⚠️ Alguns serviços estão degradados. Investigar latência.")
            for comp, status in dependency_status.items():
                if not status["operational"]:
                    recommendations.append(f"   - {comp} pode estar impactado")
        elif overall == "unhealthy":
            recommendations.append("🚨 Múltiplos serviços têm problemas. Ação necessária.")
        elif overall == "offline":
            recommendations.append("🔴 Serviços críticos estão offline. AÇÃO IMEDIATA.")

        return recommendations

    def start_monitoring(self):
        """Inicia monitoramento contínuo."""
        self.backend_checker.start_monitoring()
        logger.info("👁️ Infrastructure Monitor iniciou monitoramento")

    def stop_monitoring(self):
        """Para monitoramento contínuo."""
        self.backend_checker.stop_monitoring()
        logger.info("🛑 Infrastructure Monitor parou")


# Singleton global
_infrastructure_monitor: Optional[InfrastructureMonitor] = None


def get_infrastructure_monitor() -> InfrastructureMonitor:
    """Obter instância do Infrastructure Monitor (singleton)."""
    global _infrastructure_monitor
    if _infrastructure_monitor is None:
        backend_checker = get_backend_health_checker()
        _infrastructure_monitor = InfrastructureMonitor(backend_checker)
        logger.info("🏥 Infrastructure Monitor singleton inicializado")
    return _infrastructure_monitor
