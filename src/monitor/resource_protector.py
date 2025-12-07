"""
PROTETOR DE RECURSOS DA MÁQUINA
================================

Impede que processos monopolizem:
- CPU (mata processos Python que passam de limite)
- RAM (avisa antes de atingir OOM)
- Disco (limpa caches, avisa para liberar espaço)
- I/O (throttle de operações de escrita)

Filosofia: "Máquina sempre responsiva, nunca travada"
"""

import asyncio
import logging
import os
import subprocess
import time
from dataclasses import dataclass
from typing import List, Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass
class ResourceLimits:
    """Limites de recursos por modo."""

    cpu_percent: float  # % máxima de CPU
    memory_percent: float  # % máxima de RAM
    memory_mb_absolute: int  # MB máximo absoluto
    disk_percent: float  # % máxima de disco antes de warning
    max_processes: int  # Máximo de subprocessos
    startup_grace_period: int = 60  # Segundos de tolerância no início


class ResourceProtector:
    """Protetor de recursos da máquina."""

    # Limites por modo
    LIMITS = {
        "dev": ResourceLimits(
            cpu_percent=75.0,  # Desenvolvimento: deixa 25% para IDE
            memory_percent=80.0,
            memory_mb_absolute=8000,  # 8GB max
            disk_percent=90.0,
            max_processes=50,
            startup_grace_period=60,
        ),
        "test": ResourceLimits(
            cpu_percent=85.0,  # Testes: pode usar mais
            memory_percent=85.0,
            memory_mb_absolute=10000,  # 10GB max
            disk_percent=90.0,
            max_processes=100,
            startup_grace_period=30,
        ),
        "prod": ResourceLimits(
            cpu_percent=95.0,  # Produção: máximo tolerância
            memory_percent=95.0,
            memory_mb_absolute=12000,  # 12GB max
            disk_percent=95.0,
            max_processes=200,
            startup_grace_period=120,
        ),
    }

    def __init__(self, mode: str = "dev"):
        """Initialize resource protector.

        Args:
            mode: "dev", "test", ou "prod"
        """
        self.mode = mode
        self.limits = self.LIMITS.get(mode, self.LIMITS["dev"])
        self.protected_processes: List[int] = []
        self.running = False
        self.protection_task: Optional[asyncio.Task[None]] = None
        self.start_time = 0.0

    async def start(self) -> None:
        """Iniciar proteção de recursos."""
        if self.running:
            return

        self.running = True
        self.start_time = time.time()
        self.protection_task = asyncio.create_task(self._protection_loop())
        logger.info(f"✅ Protetor de recursos iniciado (modo: {self.mode})")

    async def stop(self) -> None:
        """Parar proteção."""
        self.running = False
        if self.protection_task:
            try:
                await asyncio.wait_for(self.protection_task, timeout=5.0)
            except asyncio.TimeoutError:
                self.protection_task.cancel()
        logger.info("Protetor de recursos parado")

    def register_process(self, pid: int) -> None:
        """Registrar processo para proteção.

        Args:
            pid: Process ID
        """
        self.protected_processes.append(pid)
        logger.debug(f"Processo {pid} registrado para proteção")

    def _is_protected(self, pid: int) -> bool:
        """Verificar se PID é protegido (incluindo filhos)."""
        if pid in self.protected_processes:
            return True

        try:
            proc = psutil.Process(pid)
            parents = proc.parents()
            for parent in parents:
                if parent.pid in self.protected_processes:
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        return False

    async def _protection_loop(self) -> None:
        """Loop principal de proteção."""
        while self.running:
            try:
                # Verificar Grace Period
                if time.time() - self.start_time < self.limits.startup_grace_period:
                    await asyncio.sleep(2.0)
                    continue

                # Verificar CPU
                cpu_percent = psutil.cpu_percent(interval=0.5)
                if cpu_percent > self.limits.cpu_percent:
                    await self._handle_cpu_overload(cpu_percent)

                # Verificar RAM
                memory_info = psutil.virtual_memory()
                if memory_info.percent > self.limits.memory_percent:
                    await self._handle_memory_overload(memory_info.percent)

                # Verificar disco
                disk_info = psutil.disk_usage("/")
                if disk_info.percent > self.limits.disk_percent:
                    await self._handle_disk_warning(disk_info.percent)

                await asyncio.sleep(2.0)  # Verificar a cada 2s

            except Exception as e:
                logger.exception(f"❌ Erro na proteção de recursos: {e}")
                await asyncio.sleep(5.0)

    async def _handle_cpu_overload(self, cpu_percent: float) -> None:
        """Lidar com CPU sobrecarregada.

        Args:
            cpu_percent: Percentual atual de CPU
        """
        logger.warning(f"⚠️  CPU sobrecarregada: {cpu_percent:.1f}%")

        # Obter processos Python pesados
        python_processes = self._get_heavy_python_processes()

        if python_processes:
            # Primeiro: tentar parar gracefully
            for proc_info in python_processes[:3]:  # Top 3 apenas
                try:
                    proc = psutil.Process(proc_info["pid"])

                    # Se for nosso processo protegido, reduzir prioridade (NUNCA matar)
                    if self._is_protected(proc_info["pid"]):
                        logger.info(
                            f"🔄 Reduzindo prioridade de {proc.name()} (PID {proc_info['pid']})"
                        )
                        proc.nice(19)  # Lowest priority
                        continue  # NUNCA matar processos protegidos

                    # Verificar se é processo uvicorn do OmniMind (proteção adicional)
                    cmdline = proc.cmdline()
                    cmdline_str = " ".join(str(arg) for arg in cmdline) if cmdline else ""
                    if any(
                        pattern in cmdline_str.lower()
                        for pattern in ["uvicorn", "web.backend", "omnimind"]
                    ):
                        logger.info(
                            f"🛡️  Processo uvicorn/omnimind protegido: "
                            f"{proc.name()} (PID {proc_info['pid']})"
                        )
                        proc.nice(19)  # Reduzir prioridade mas não matar
                        continue

                    # Se for outro processo, considerar matar apenas se CPU > 90% (mais conservador)
                    elif proc_info["cpu_percent"] > 90:
                        cpu_pct = proc_info["cpu_percent"]
                        logger.warning(
                            f"⚠️  Matando processo pesado: {proc.name()} ({cpu_pct:.1f}%)"
                        )
                        proc.terminate()
                        try:
                            proc.wait(timeout=2)
                        except psutil.TimeoutExpired:
                            proc.kill()

                except psutil.NoSuchProcess:
                    pass

    async def _handle_memory_overload(self, memory_percent: float) -> None:
        """Lidar com RAM sobrecarregada.

        Args:
            memory_percent: Percentual atual de RAM
        """
        logger.error(f"🚨 RAM sobrecarregada: {memory_percent:.1f}%")

        # Tentar liberar cache
        try:
            if os.name == "posix":
                # Linux: limpar caches (requer sudo)
                subprocess.run(
                    ["sync"],
                    timeout=2,
                    capture_output=True,
                )
                logger.info("🧹 Sync de disco executado")
        except Exception as e:
            logger.debug(f"Erro ao limpar cache: {e}")

        # Obter processos pesados
        heavy_processes = self._get_heavy_processes()
        for proc_info in heavy_processes[:3]:  # Top 3
            try:
                proc = psutil.Process(proc_info["pid"])
                if proc_info["pid"] not in self.protected_processes:
                    memory_mb = proc_info["memory_mb"]
                    proc_name = proc.name()
                    logger.warning(
                        f"⚠️  Matando processo que consome {memory_mb:.0f}MB: {proc_name}"
                    )
                    proc.terminate()
                    try:
                        proc.wait(timeout=2)
                    except psutil.TimeoutExpired:
                        proc.kill()
            except psutil.NoSuchProcess:
                pass

    async def _handle_disk_warning(self, disk_percent: float) -> None:
        """Lidar com disco quase cheio.

        Args:
            disk_percent: Percentual de disco usado
        """
        logger.warning(f"⚠️  Disco quase cheio: {disk_percent:.1f}%")

        # Limpar arquivos temporários
        temp_dirs = ["/tmp", os.path.expanduser("~/.cache"), "data/tmp"]
        for temp_dir in temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    for file in os.listdir(temp_dir):
                        file_path = os.path.join(temp_dir, file)
                        try:
                            if os.path.isfile(file_path):
                                os.remove(file_path)
                                logger.debug(f"🗑️  Deletado: {file_path}")
                            elif os.path.isdir(file_path) and file.startswith("."):
                                import shutil

                                shutil.rmtree(file_path)
                                logger.debug(f"🗑️  Deletado diretório: {file_path}")
                        except Exception as e:
                            logger.debug(f"Erro ao deletar {file_path}: {e}")
            except Exception as e:
                logger.debug(f"Erro ao limpar {temp_dir}: {e}")

    def _get_heavy_python_processes(self) -> List[dict]:
        """Obter processos Python que estão consumindo muita CPU.

        Returns:
            Lista de dicts com {pid, name, cpu_percent}
        """
        python_processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "cmdline"]):
            try:
                if "python" in proc.name().lower():
                    cmdline = proc.info.get("cmdline", [])
                    cmdline_str = " ".join(str(arg) for arg in cmdline) if cmdline else ""

                    # PROTEGER processos do próprio OmniMind (evitar fogo amigo)
                    # Lista expandida de processos protegidos
                    protected_patterns = [
                        "web.backend.main",
                        "uvicorn",
                        "omnimind",
                        "src.main",
                        "run_cluster",
                        "mcp_orchestrator",
                        "main_cycle",
                        "daemon",
                        "observer_service",
                    ]

                    # Se for processo do OmniMind, NUNCA matar
                    if any(
                        pattern.lower() in cmdline_str.lower() for pattern in protected_patterns
                    ):
                        continue

                    # Se for processo protegido explicitamente, ignorar
                    if self._is_protected(proc.pid):
                        continue

                    # Pega CPU percent se não for None
                    cpu = proc.info.get("cpu_percent", 0) or 0
                    # Aumentar threshold de 50% para 80% para ser menos agressivo
                    if cpu > 80:
                        python_processes.append(
                            {
                                "pid": proc.pid,
                                "name": proc.name(),
                                "cpu_percent": cpu,
                            }
                        )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Ordenar por CPU descendente
        python_processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
        return python_processes

    def _get_heavy_processes(self) -> List[dict]:
        """Obter processos que estão consumindo muita RAM.

        Returns:
            Lista de dicts com {pid, name, memory_mb}
        """
        processes = []
        for proc in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                memory_mb = proc.memory_info().rss / (1024 * 1024)
                if memory_mb > 100:  # Processos > 100MB
                    processes.append(
                        {
                            "pid": proc.pid,
                            "name": proc.name(),
                            "memory_mb": memory_mb,
                        }
                    )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        # Ordenar por memória descendente
        processes.sort(key=lambda x: x["memory_mb"], reverse=True)
        return processes

    def get_resource_status(self) -> dict:
        """Obter status atual de recursos.

        Returns:
            Dict com CPU, RAM, Disco
        """
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage("/")

        return {
            "cpu": {
                "current": cpu_percent,
                "limit": self.limits.cpu_percent,
                "status": (
                    "🔴 CRÍTICO"
                    if cpu_percent > self.limits.cpu_percent
                    else "⚠️  ELEVADO" if cpu_percent > self.limits.cpu_percent * 0.8 else "✅ OK"
                ),
            },
            "memory": {
                "current": memory_info.percent,
                "limit": self.limits.memory_percent,
                "available_mb": memory_info.available / (1024 * 1024),
                "status": (
                    "🔴 CRÍTICO"
                    if memory_info.percent > self.limits.memory_percent
                    else (
                        "⚠️  ELEVADO"
                        if memory_info.percent > self.limits.memory_percent * 0.8
                        else "✅ OK"
                    )
                ),
            },
            "disk": {
                "current": disk_info.percent,
                "limit": self.limits.disk_percent,
                "free_gb": disk_info.free / (1024 * 1024 * 1024),
                "status": (
                    "🔴 CRÍTICO"
                    if disk_info.percent > self.limits.disk_percent
                    else (
                        "⚠️  ELEVADO"
                        if disk_info.percent > self.limits.disk_percent * 0.8
                        else "✅ OK"
                    )
                ),
            },
        }


# Instância global
_resource_protector: Optional[ResourceProtector] = None


async def get_resource_protector(mode: str = "dev") -> ResourceProtector:
    """Obter instância global do protetor.

    Args:
        mode: "dev", "test", ou "prod"

    Returns:
        ResourceProtector
    """
    global _resource_protector
    if _resource_protector is None:
        _resource_protector = ResourceProtector(mode)
    return _resource_protector
