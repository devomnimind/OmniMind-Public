"""
Sistema de Observabilidade Interna (Introspection Loop) para Orchestrator.

Implementa Seção 2 da Auditoria do Orchestrator:
- Monitoramento interno do estado do Orchestrator
- Detecção de anomalias internas
- Métricas de saúde do sistema
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class IntrospectionMetrics:
    """Métricas de introspecção."""

    timestamp: float
    component_health: Dict[str, bool]
    resource_usage: Dict[str, float]
    error_rate: float
    anomaly_detected: bool = False
    anomalies: List[str] = field(default_factory=list)


class IntrospectionLoop:
    """Loop de introspecção para observabilidade interna."""

    def __init__(self, orchestrator: Any, interval: float = 30.0) -> None:
        """Inicializa loop de introspecção.

        Args:
            orchestrator: Instância do OrchestratorAgent
            interval: Intervalo entre verificações (segundos)
        """
        self.orchestrator = orchestrator
        self.interval = interval
        self.metrics_history: List[IntrospectionMetrics] = []
        self.max_history = 100
        self.running = False
        self._task: Optional[Any] = None

        logger.info("IntrospectionLoop inicializado (interval: %.1fs)", interval)

    async def start(self) -> None:
        """Inicia loop de introspecção."""
        if self.running:
            logger.warning("IntrospectionLoop já está rodando")
            return

        self.running = True
        logger.info("IntrospectionLoop iniciado")

        # Criar task assíncrona
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        """Para loop de introspecção."""
        if not self.running:
            return

        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        logger.info("IntrospectionLoop parado")

    async def _loop(self) -> None:
        """Loop principal de introspecção."""
        while self.running:
            try:
                # Coletar métricas
                metrics = await self._collect_metrics()

                # Detectar anomalias
                anomalies = self._detect_anomalies(metrics)

                # Atualizar métricas com anomalias
                metrics.anomaly_detected = len(anomalies) > 0
                metrics.anomalies = anomalies

                # Adicionar ao histórico
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history.pop(0)

                # Log se anomalias detectadas
                if anomalies:
                    logger.warning("Anomalias detectadas: %s", ", ".join(anomalies))

                # Aguardar próximo ciclo
                await asyncio.sleep(self.interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Erro no loop de introspecção: %s", e, exc_info=True)
                await asyncio.sleep(self.interval)

    async def _collect_metrics(self) -> IntrospectionMetrics:
        """Coleta métricas do sistema.

        Returns:
            Métricas coletadas
        """
        # Coletar saúde dos componentes
        component_health: Dict[str, bool] = {}
        if self.orchestrator.agent_registry:
            health_status = await self.orchestrator.agent_registry.health_check_all()
            component_health = health_status

        # Coletar uso de recursos (simulado)
        resource_usage: Dict[str, float] = {
            "cpu": 0.0,
            "memory": 0.0,
            "disk": 0.0,
        }

        # Calcular taxa de erro
        error_rate = 0.0
        if hasattr(self.orchestrator, "metrics"):
            metrics_summary = self.orchestrator.metrics_summary()
            total = metrics_summary.get("total_operations", 0)
            errors = metrics_summary.get("failed_operations", 0)
            if total > 0:
                error_rate = errors / total

        return IntrospectionMetrics(
            timestamp=time.time(),
            component_health=component_health,
            resource_usage=resource_usage,
            error_rate=error_rate,
        )

    def _detect_anomalies(self, metrics: IntrospectionMetrics) -> List[str]:
        """Detecta anomalias nas métricas.

        Args:
            metrics: Métricas coletadas

        Returns:
            Lista de anomalias detectadas
        """
        anomalies: List[str] = []

        # Verificar saúde dos componentes
        unhealthy_components = [
            component for component, healthy in metrics.component_health.items() if not healthy
        ]
        if unhealthy_components:
            anomalies.append(f"Componentes não saudáveis: {', '.join(unhealthy_components)}")

        # Verificar taxa de erro
        if metrics.error_rate > 0.1:  # 10% de erro
            anomalies.append(f"Taxa de erro alta: {metrics.error_rate:.2%}")

        # Verificar uso de recursos
        if metrics.resource_usage.get("cpu", 0) > 0.9:  # 90% CPU
            anomalies.append("Uso de CPU muito alto")

        if metrics.resource_usage.get("memory", 0) > 0.9:  # 90% memória
            anomalies.append("Uso de memória muito alto")

        return anomalies

    def get_latest_metrics(self) -> Optional[IntrospectionMetrics]:
        """Obtém métricas mais recentes.

        Returns:
            Métricas mais recentes ou None
        """
        if not self.metrics_history:
            return None
        return self.metrics_history[-1]

    def get_metrics_history(self, limit: int = 10) -> List[IntrospectionMetrics]:
        """Obtém histórico de métricas.

        Args:
            limit: Número máximo de métricas a retornar

        Returns:
            Lista de métricas recentes
        """
        return self.metrics_history[-limit:]

    def get_introspection_summary(self) -> Dict[str, Any]:
        """Obtém resumo do sistema de introspecção.

        Returns:
            Dicionário com resumo
        """
        latest = self.get_latest_metrics()

        return {
            "running": self.running,
            "interval": self.interval,
            "total_metrics_collected": len(self.metrics_history),
            "latest_metrics": (
                {
                    "timestamp": latest.timestamp if latest else None,
                    "anomaly_detected": latest.anomaly_detected if latest else False,
                    "anomalies": latest.anomalies if latest else [],
                    "error_rate": latest.error_rate if latest else 0.0,
                }
                if latest
                else None
            ),
        }
