"""
Neural Component Metrics Collector - Phase 20.

Coleta métricas de latência, throughput e health status dos backends neurais.
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Optional
from collections import deque
import statistics

logger = logging.getLogger(__name__)


@dataclass
class BackendMetrics:
    """Métricas de um backend neural."""

    backend_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_seconds: float = 0.0
    latencies: deque = field(default_factory=lambda: deque(maxlen=1000))
    last_error: Optional[str] = None
    last_success_timestamp: float = 0.0
    last_failure_timestamp: float = 0.0

    @property
    def success_rate(self) -> float:
        """Taxa de sucesso (0-1)."""
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests

    @property
    def average_latency(self) -> float:
        """Latência média em segundos."""
        if self.total_requests == 0:
            return 0.0
        return self.total_latency_seconds / self.total_requests

    @property
    def p50_latency(self) -> float:
        """Mediana de latência (percentil 50)."""
        if not self.latencies:
            return 0.0
        return statistics.median(self.latencies)

    @property
    def p95_latency(self) -> float:
        """Percentil 95 de latência."""
        if not self.latencies:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        idx = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[min(idx, len(sorted_latencies) - 1)]

    @property
    def p99_latency(self) -> float:
        """Percentil 99 de latência."""
        if not self.latencies:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        idx = int(len(sorted_latencies) * 0.99)
        return sorted_latencies[min(idx, len(sorted_latencies) - 1)]

    def is_healthy(self) -> bool:
        """Verifica se backend está saudável (>90% sucesso nos últimos requests)."""
        return self.success_rate >= 0.9


class NeuralMetricsCollector:
    """
    Coleta e agrega métricas de todos os backends neurais.

    Features:
    - Latência (p50, p95, p99)
    - Taxa de erro
    - Throughput
    - Health status
    """

    def __init__(self):
        """Inicializa o coletor de métricas."""
        self.backends: Dict[str, BackendMetrics] = {
            "ollama": BackendMetrics(backend_name="ollama"),
            "huggingface": BackendMetrics(backend_name="huggingface"),
            "hf_space": BackendMetrics(backend_name="hf_space"),
            "stub": BackendMetrics(backend_name="stub"),
        }
        self.global_start_time = time.time()

    def record_request(
        self,
        backend: str,
        latency_seconds: float,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """
        Registra uma requisição.

        Args:
            backend: Nome do backend (ollama, huggingface, hf_space, stub)
            latency_seconds: Latência da requisição em segundos
            success: Se a requisição foi bem-sucedida
            error: Mensagem de erro (se falhou)
        """
        if backend not in self.backends:
            logger.warning(f"Backend desconhecido: {backend}")
            return

        metrics = self.backends[backend]
        metrics.total_requests += 1
        metrics.total_latency_seconds += latency_seconds
        metrics.latencies.append(latency_seconds)

        if success:
            metrics.successful_requests += 1
            metrics.last_success_timestamp = time.time()
        else:
            metrics.failed_requests += 1
            metrics.last_error = error
            metrics.last_failure_timestamp = time.time()

        # Log se latência muito alta (>5s)
        if latency_seconds > 5.0:
            logger.warning(
                f"High latency detected: {backend} took {latency_seconds:.2f}s"
            )

    def get_backend_metrics(self, backend: str) -> Optional[BackendMetrics]:
        """Retorna métricas de um backend específico."""
        return self.backends.get(backend)

    def get_all_metrics(self) -> Dict[str, BackendMetrics]:
        """Retorna métricas de todos os backends."""
        return self.backends.copy()

    def get_summary(self) -> Dict[str, any]:
        """
        Retorna resumo consolidado de métricas.

        Returns:
            Dict com métricas agregadas
        """
        uptime_seconds = time.time() - self.global_start_time
        total_requests = sum(m.total_requests for m in self.backends.values())
        total_successful = sum(m.successful_requests for m in self.backends.values())

        return {
            "uptime_seconds": uptime_seconds,
            "total_requests": total_requests,
            "total_successful": total_successful,
            "global_success_rate": (
                (total_successful / total_requests) if total_requests > 0 else 1.0
            ),
            "backends": {
                name: {
                    "requests": m.total_requests,
                    "success_rate": m.success_rate,
                    "avg_latency_ms": m.average_latency * 1000,
                    "p50_latency_ms": m.p50_latency * 1000,
                    "p95_latency_ms": m.p95_latency * 1000,
                    "p99_latency_ms": m.p99_latency * 1000,
                    "is_healthy": m.is_healthy(),
                    "last_error": m.last_error,
                }
                for name, m in self.backends.items()
                if m.total_requests > 0  # Apenas backends com requests
            },
        }

    def reset(self) -> None:
        """Reseta todas as métricas."""
        for backend in self.backends.values():
            backend.total_requests = 0
            backend.successful_requests = 0
            backend.failed_requests = 0
            backend.total_latency_seconds = 0.0
            backend.latencies.clear()
            backend.last_error = None

        self.global_start_time = time.time()
        logger.info("Metrics reset")

    def log_summary(self) -> None:
        """Loga resumo das métricas."""
        summary = self.get_summary()
        logger.info("=" * 60)
        logger.info(
            f"NEURAL METRICS SUMMARY (uptime: {summary['uptime_seconds']:.0f}s)"
        )
        logger.info(f"Total Requests: {summary['total_requests']}")
        logger.info(f"Success Rate: {summary['global_success_rate']:.2%}")
        logger.info("-" * 60)

        for backend_name, metrics in summary["backends"].items():
            logger.info(f"\n{backend_name.upper()}:")
            logger.info(f"  Requests: {metrics['requests']}")
            logger.info(f"  Success Rate: {metrics['success_rate']:.2%}")
            logger.info(
                f"  Latency (ms): avg={metrics['avg_latency_ms']:.0f}, "
                f"p50={metrics['p50_latency_ms']:.0f}, "
                f"p95={metrics['p95_latency_ms']:.0f}, "
                f"p99={metrics['p99_latency_ms']:.0f}"
            )
            logger.info(f"  Healthy: {'✅' if metrics['is_healthy'] else '❌'}")
            if metrics.get("last_error"):
                logger.info(f"  Last Error: {metrics['last_error'][:50]}...")

        logger.info("=" * 60)


# Singleton global
_metrics_collector = NeuralMetricsCollector()


def get_metrics_collector() -> NeuralMetricsCollector:
    """Retorna a instância global do coletor de métricas."""
    return _metrics_collector
