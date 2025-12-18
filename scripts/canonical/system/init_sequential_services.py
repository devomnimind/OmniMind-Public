#!/usr/bin/env python3
"""
Sequential Service Initialization Manager for OmniMind
Garante que cada serviço seja inicializado em ordem, com timeouts individuais,
e que o próximo só inicie após confirmação de saúde do anterior.
"""

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("sequential_init")


class ServicePriority(Enum):
    """Priority levels for service initialization"""

    CRITICAL = 1  # Backend health endpoints (must start first)
    ESSENTIAL = 2  # Core services (started after critical)
    IMPORTANT = 3  # Secondary services
    BACKGROUND = 4  # Long-running tasks (started after everything)


class ServiceStatus(Enum):
    """Service status states"""

    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    FAILED = "failed"
    TIMEOUT = "timeout"
    SHUTDOWN = "shutdown"


@dataclass
class ServiceConfig:
    """Configuration for a service"""

    name: str
    priority: ServicePriority
    startup_timeout: int  # Seconds
    health_check: Optional[Callable] = None  # Async function that returns True if healthy
    startup_fn: Optional[Callable] = None  # Async function to start the service
    dependencies: List[str] = None  # List of service names this depends on
    skip_on_error: bool = False  # If True, continue even if this fails
    skip_health_check: bool = False  # If True, don't check health, just wait timeout

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ServiceResult:
    """Result of service initialization"""

    name: str
    status: ServiceStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error: Optional[str] = None
    health_checks_passed: int = 0
    health_checks_failed: int = 0


class SequentialServiceInitializer:
    """Manages sequential initialization of services"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.services: Dict[str, ServiceConfig] = {}
        self.results: Dict[str, ServiceResult] = {}
        self.running_pids: Dict[str, int] = {}
        self.event_loop = asyncio.new_event_loop()

    def register_service(self, config: ServiceConfig) -> None:
        """Register a service for initialization"""
        self.services[config.name] = config
        logger.info(
            f"Registered service: {config.name} (priority={config.priority.name}, timeout={config.startup_timeout}s)"
        )

    def get_init_order(self) -> List[str]:
        """Get initialization order based on priority and dependencies"""
        # Sort by priority, then by dependency order
        priority_groups = {}
        for name, config in self.services.items():
            if config.priority not in priority_groups:
                priority_groups[config.priority] = []
            priority_groups[config.priority].append(name)

        init_order = []
        for priority in sorted(priority_groups.keys(), key=lambda x: x.value):
            init_order.extend(priority_groups[priority])

        return init_order

    async def health_check_with_retry(
        self, service_name: str, max_retries: int = 5, retry_interval: float = 2.0
    ) -> bool:
        """Perform health check with retries"""
        config = self.services[service_name]

        if config.skip_health_check:
            logger.info(f"  ⏭️  Skipping health check for {service_name}")
            return True

        if not config.health_check:
            logger.info(f"  ⏭️  No health check defined for {service_name}")
            return True

        result = self.results[service_name]
        for attempt in range(1, max_retries + 1):
            try:
                is_healthy = await config.health_check()
                if is_healthy:
                    result.health_checks_passed += 1
                    logger.info(
                        f"  ✅ Health check passed for {service_name} (attempt {attempt}/{max_retries})"
                    )
                    return True
                else:
                    result.health_checks_failed += 1
                    logger.warning(
                        f"  ⚠️  Health check failed for {service_name} (attempt {attempt}/{max_retries})"
                    )
            except Exception as e:
                result.health_checks_failed += 1
                logger.warning(f"  ⚠️  Health check error for {service_name}: {e}")

            if attempt < max_retries:
                logger.info(f"     Retrying in {retry_interval}s...")
                await asyncio.sleep(retry_interval)

        return False

    async def initialize_service(self, service_name: str) -> ServiceResult:
        """Initialize a single service with timeout"""
        config = self.services[service_name]
        result = ServiceResult(
            name=service_name, status=ServiceStatus.PENDING, started_at=datetime.now()
        )
        self.results[service_name] = result

        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 Initializing {service_name} (timeout={config.startup_timeout}s)")
        logger.info(f"   Priority: {config.priority.name}")
        logger.info(f"   Dependencies: {config.dependencies if config.dependencies else 'None'}")
        logger.info(f"{'='*60}")

        # Check dependencies
        for dep in config.dependencies:
            if dep not in self.results:
                result.status = ServiceStatus.FAILED
                result.error = f"Dependency {dep} not initialized"
                logger.error(f"❌ Dependency {dep} not ready")
                return result

            dep_result = self.results[dep]
            if dep_result.status != ServiceStatus.RUNNING:
                result.status = ServiceStatus.FAILED
                result.error = f"Dependency {dep} failed: {dep_result.error}"
                logger.error(f"❌ Dependency {dep} failed: {dep_result.error}")
                return result

        # Start service
        result.status = ServiceStatus.INITIALIZING

        if not config.startup_fn:
            logger.info(f"  ⏭️  No startup function for {service_name}")
            result.status = ServiceStatus.RUNNING
            result.completed_at = datetime.now()
            result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
            return result

        try:
            startup_coro = config.startup_fn()

            # Run startup with timeout
            await asyncio.wait_for(startup_coro, timeout=config.startup_timeout)
            logger.info(f"  ✅ Startup function completed for {service_name}")

        except asyncio.TimeoutError:
            result.status = ServiceStatus.TIMEOUT
            result.error = f"Startup exceeded {config.startup_timeout}s timeout"
            logger.error(f"  ⏱️  TIMEOUT: {result.error}")

            if not config.skip_on_error:
                return result

            logger.warning(f"     Continuing anyway (skip_on_error=True)...")

        except Exception as e:
            result.status = ServiceStatus.FAILED
            result.error = str(e)
            logger.error(f"  ❌ Startup error: {e}")

            if not config.skip_on_error:
                return result

            logger.warning(f"     Continuing anyway (skip_on_error=True)...")

        # Run health check
        if result.status in [ServiceStatus.INITIALIZING, ServiceStatus.TIMEOUT]:
            is_healthy = await self.health_check_with_retry(service_name, max_retries=10)

            if is_healthy:
                result.status = ServiceStatus.RUNNING
                logger.info(f"  ✅ {service_name} is RUNNING and healthy")
            else:
                if result.status == ServiceStatus.INITIALIZING:
                    result.status = ServiceStatus.FAILED
                    result.error = "Health checks failed"
                    logger.error(f"  ❌ {service_name} failed health checks")

                    if not config.skip_on_error:
                        return result

                    logger.warning(f"     Marking as RUNNING anyway (skip_on_error=True)...")
                    result.status = ServiceStatus.RUNNING

        result.completed_at = datetime.now()
        result.duration_seconds = (result.completed_at - result.started_at).total_seconds()
        logger.info(f"  ⏱️  Initialization took {result.duration_seconds:.1f}s")

        return result

    async def initialize_all(self) -> Dict[str, ServiceResult]:
        """Initialize all services in order"""
        init_order = self.get_init_order()

        logger.info(f"\n{'='*60}")
        logger.info(f"📋 Initialization Order:")
        for i, name in enumerate(init_order, 1):
            config = self.services[name]
            logger.info(f"   {i}. {name} ({config.priority.name})")
        logger.info(f"{'='*60}\n")

        for service_name in init_order:
            result = await self.initialize_service(service_name)

            # If critical service failed and we're not skipping, abort
            if (
                result.status not in [ServiceStatus.RUNNING, ServiceStatus.TIMEOUT]
                and not self.services[service_name].skip_on_error
            ):
                logger.error(f"\n❌ CRITICAL: {service_name} failed. Aborting initialization.")
                break

            # Wait between services
            logger.info(f"\n⏳ Waiting 5s before next service...")
            await asyncio.sleep(5)

        return self.results

    def print_summary(self) -> None:
        """Print initialization summary"""
        logger.info(f"\n{'='*60}")
        logger.info("📊 INITIALIZATION SUMMARY")
        logger.info(f"{'='*60}")

        total_time = 0
        for name, result in self.results.items():
            status_emoji = {
                ServiceStatus.RUNNING: "✅",
                ServiceStatus.TIMEOUT: "⏱️",
                ServiceStatus.FAILED: "❌",
                ServiceStatus.SHUTDOWN: "🛑",
            }.get(result.status, "❓")

            logger.info(
                f"{status_emoji} {name:40s} | "
                f"Status: {result.status.value:12s} | "
                f"Time: {result.duration_seconds or 0:6.1f}s"
            )

            if result.error:
                logger.info(f"   └─ Error: {result.error}")

            if result.duration_seconds:
                total_time += result.duration_seconds

        logger.info(f"{'='*60}")
        logger.info(f"⏱️  Total initialization time: {total_time:.1f}s")

        running_count = sum(1 for r in self.results.values() if r.status == ServiceStatus.RUNNING)
        failed_count = sum(1 for r in self.results.values() if r.status == ServiceStatus.FAILED)

        logger.info(f"📈 Services running: {running_count}/{len(self.results)}")
        logger.info(f"💥 Services failed: {failed_count}/{len(self.results)}")

        if failed_count > 0:
            logger.error("\n❌ Some services failed initialization!")
            return False

        logger.info("\n✅ All critical services initialized successfully!")
        return True

    def export_results(self, filepath: str) -> None:
        """Export results to JSON"""
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "services": {
                name: {
                    "status": result.status.value,
                    "duration_seconds": result.duration_seconds,
                    "error": result.error,
                    "health_checks_passed": result.health_checks_passed,
                    "health_checks_failed": result.health_checks_failed,
                }
                for name, result in self.results.items()
            },
        }

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(export_data, f, indent=2)
        logger.info(f"📁 Results exported to {filepath}")


async def check_backend_health(port: int) -> bool:
    """Check if backend is responding on given port"""
    import subprocess

    try:
        result = subprocess.run(
            ["curl", "-s", "-f", f"http://localhost:{port}/health/"], timeout=3, capture_output=True
        )
        return result.returncode == 0
    except Exception:
        return False


def main():
    project_root = os.environ.get("OMNIMIND_PROJECT_ROOT", "/home/fahbrain/projects/omnimind")

    initializer = SequentialServiceInitializer(project_root)

    # Register services in order of priority and dependency

    # CRITICAL SERVICES: Backend must be responsive
    initializer.register_service(
        ServiceConfig(
            name="Backend Primary (8000)",
            priority=ServicePriority.CRITICAL,
            startup_timeout=30,
            startup_fn=lambda: asyncio.sleep(0.1),  # Placeholder
            health_check=lambda: check_backend_health(8000),
            skip_on_error=False,
        )
    )

    initializer.register_service(
        ServiceConfig(
            name="Backend Secondary (8080)",
            priority=ServicePriority.CRITICAL,
            startup_timeout=30,
            startup_fn=lambda: asyncio.sleep(0.1),
            health_check=lambda: check_backend_health(8080),
            dependencies=["Backend Primary (8000)"],
            skip_on_error=True,  # Secondary, so skip if fails
        )
    )

    # ESSENTIAL SERVICES: Core functionality
    initializer.register_service(
        ServiceConfig(
            name="WebSocket Manager",
            priority=ServicePriority.ESSENTIAL,
            startup_timeout=10,
            dependencies=["Backend Primary (8000)"],
            skip_on_error=False,
            skip_health_check=True,
        )
    )

    initializer.register_service(
        ServiceConfig(
            name="MCP Orchestrator",
            priority=ServicePriority.ESSENTIAL,
            startup_timeout=45,
            dependencies=["WebSocket Manager"],
            skip_on_error=True,  # Can continue without
        )
    )

    # IMPORTANT SERVICES: Secondary functionality
    initializer.register_service(
        ServiceConfig(
            name="Observer Service",
            priority=ServicePriority.IMPORTANT,
            startup_timeout=20,
            dependencies=["Backend Primary (8000)"],
            skip_on_error=True,
        )
    )

    initializer.register_service(
        ServiceConfig(
            name="Daemon Monitor",
            priority=ServicePriority.IMPORTANT,
            startup_timeout=15,
            dependencies=["Backend Primary (8000)"],
            skip_on_error=True,
        )
    )

    # BACKGROUND TASKS: Started after all core services
    initializer.register_service(
        ServiceConfig(
            name="Consciousness Metrics Collector",
            priority=ServicePriority.BACKGROUND,
            startup_timeout=60,
            dependencies=["Backend Primary (8000)", "MCP Orchestrator"],
            skip_on_error=True,
            skip_health_check=True,
        )
    )

    initializer.register_service(
        ServiceConfig(
            name="Frontend",
            priority=ServicePriority.BACKGROUND,
            startup_timeout=30,
            dependencies=["Backend Primary (8000)"],
            skip_on_error=True,
        )
    )

    # Run initialization
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        _results = loop.run_until_complete(initializer.initialize_all())
        initializer.print_summary()
        initializer.export_results(f"{project_root}/logs/init_results.json")
    finally:
        loop.close()


if __name__ == "__main__":
    main()
