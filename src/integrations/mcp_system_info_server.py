"""
MCP System Info Server - Servidor MCP para informações do sistema.

Este servidor MCP fornece informações sobre hardware e recursos do sistema:
- GPU info (CUDA, VRAM disponível)
- CPU info (threads, load)
- Memória RAM disponível
- Disco (espaço livre)
- Temperatura (se disponível)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-01-XX
"""

import logging
import platform
from pathlib import Path
from typing import Any, Dict, Optional

import psutil

from src.integrations.mcp_server import MCPServer

logger = logging.getLogger(__name__)


class SystemInfoMCPServer(MCPServer):
    """Servidor MCP para informações do sistema."""

    def __init__(self) -> None:
        """Inicializa o servidor de informações do sistema."""
        super().__init__()

        # Registrar métodos MCP
        self._methods.update(
            {
                "get_gpu_info": self.get_gpu_info,
                "get_cpu_info": self.get_cpu_info,
                "get_memory_info": self.get_memory_info,
                "get_disk_info": self.get_disk_info,
                "get_temperature": self.get_temperature,
                "get_system_summary": self.get_system_summary,
            }
        )

        logger.info("SystemInfoMCPServer inicializado")

    def get_gpu_info(self) -> Dict[str, Any]:
        """Obtém informações da GPU.

        Returns:
            Dict com informações da GPU (CUDA, VRAM, etc.)
        """
        try:
            gpu_info: Dict[str, Any] = {
                "available": False,
                "name": "Unknown",
                "vram_gb": 0.0,
                "vram_used_gb": 0.0,
                "vram_free_gb": 0.0,
                "cuda_available": False,
                "cuda_version": None,
            }

            # Tentar detectar NVIDIA GPU via nvidia-smi
            try:
                import subprocess

                result = subprocess.run(
                    [
                        "nvidia-smi",
                        "--query-gpu=name,memory.total,memory.used,memory.free",
                        "--format=csv,noheader,nounits",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5.0,
                )

                if result.returncode == 0 and result.stdout.strip():
                    lines = result.stdout.strip().split("\n")
                    if lines:
                        parts = lines[0].split(",")
                        if len(parts) >= 4:
                            gpu_info["available"] = True
                            gpu_info["name"] = parts[0].strip()
                            gpu_info["vram_gb"] = float(parts[1].strip()) / 1024.0
                            gpu_info["vram_used_gb"] = float(parts[2].strip()) / 1024.0
                            gpu_info["vram_free_gb"] = float(parts[3].strip()) / 1024.0
            except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
                logger.debug("nvidia-smi não disponível: %s", e)

            # Verificar CUDA via PyTorch se disponível
            try:
                import torch

                if torch.cuda.is_available():
                    gpu_info["cuda_available"] = True
                    gpu_info["cuda_version"] = torch.version.cuda
                    if torch.cuda.device_count() > 0:
                        gpu_info["device_count"] = torch.cuda.device_count()
                        gpu_info["current_device"] = torch.cuda.current_device()
                        gpu_info["device_name"] = torch.cuda.get_device_name(0)
            except ImportError:
                logger.debug("PyTorch não disponível para verificação CUDA")

            return gpu_info

        except Exception as e:
            logger.error("Erro ao obter informações da GPU: %s", e)
            return {
                "available": False,
                "error": str(e),
            }

    def get_cpu_info(self) -> Dict[str, Any]:
        """Obtém informações da CPU.

        Returns:
            Dict com informações da CPU
        """
        try:
            cpu_info = {
                "model": platform.processor() or "Unknown",
                "cores_physical": psutil.cpu_count(logical=False) or psutil.cpu_count(),
                "cores_logical": psutil.cpu_count(logical=True),
                "frequency_mhz": (psutil.cpu_freq().current if psutil.cpu_freq() else None),
                "usage_percent": psutil.cpu_percent(interval=0.1),
                "usage_per_core": psutil.cpu_percent(interval=0.1, percpu=True),
                "load_average": (
                    list(psutil.getloadavg()) if hasattr(psutil, "getloadavg") else None
                ),
                "architecture": platform.machine(),
            }

            return cpu_info

        except Exception as e:
            logger.error("Erro ao obter informações da CPU: %s", e)
            return {
                "model": "Unknown",
                "cores_physical": 0,
                "cores_logical": 0,
                "error": str(e),
            }

    def get_memory_info(self) -> Dict[str, Any]:
        """Obtém informações de memória RAM.

        Returns:
            Dict com informações de memória
        """
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            return {
                "total_gb": round(mem.total / (1024**3), 2),
                "available_gb": round(mem.available / (1024**3), 2),
                "used_gb": round(mem.used / (1024**3), 2),
                "percent": mem.percent,
                "swap_total_gb": round(swap.total / (1024**3), 2),
                "swap_used_gb": round(swap.used / (1024**3), 2),
                "swap_percent": swap.percent,
            }

        except Exception as e:
            logger.error("Erro ao obter informações de memória: %s", e)
            return {
                "total_gb": 0.0,
                "available_gb": 0.0,
                "error": str(e),
            }

    def get_disk_info(self, path: Optional[str] = None) -> Dict[str, Any]:
        """Obtém informações de disco.

        Args:
            path: Caminho do disco (padrão: raiz do projeto)

        Returns:
            Dict com informações de disco
        """
        try:
            disk_path = Path(path) if path else self.project_root
            disk = psutil.disk_usage(str(disk_path))

            return {
                "path": str(disk_path),
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percent": round((disk.used / disk.total) * 100, 2),
            }

        except Exception as e:
            logger.error("Erro ao obter informações de disco: %s", e)
            return {
                "total_gb": 0.0,
                "free_gb": 0.0,
                "error": str(e),
            }

    def get_temperature(self) -> Dict[str, Any]:
        """Obtém informações de temperatura (se disponível).

        Returns:
            Dict com temperaturas
        """
        try:
            temps: Dict[str, Any] = {
                "cpu_c": None,
                "gpu_c": None,
                "available": False,
            }

            # Tentar obter temperaturas via psutil
            if hasattr(psutil, "sensors_temperatures"):
                sensors = psutil.sensors_temperatures()
                if sensors:
                    temps["available"] = True
                    # Procurar temperatura da CPU
                    for name, entries in sensors.items():
                        if "cpu" in name.lower() or "core" in name.lower():
                            if entries:
                                temps["cpu_c"] = entries[0].current
                                break

            # Tentar obter temperatura da GPU via nvidia-smi
            try:
                import subprocess

                result = subprocess.run(
                    [
                        "nvidia-smi",
                        "--query-gpu=temperature.gpu",
                        "--format=csv,noheader,nounits",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5.0,
                )

                if result.returncode == 0 and result.stdout.strip():
                    temps["gpu_c"] = float(result.stdout.strip())
                    temps["available"] = True
            except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
                pass

            return temps

        except Exception as e:
            logger.debug("Erro ao obter temperatura: %s", e)
            return {
                "cpu_c": None,
                "gpu_c": None,
                "available": False,
            }

    def get_system_summary(self) -> Dict[str, Any]:
        """Obtém resumo completo do sistema.

        Returns:
            Dict com resumo de todos os recursos
        """
        try:
            return {
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "python_version": platform.python_version(),
                "cpu": self.get_cpu_info(),
                "memory": self.get_memory_info(),
                "disk": self.get_disk_info(),
                "gpu": self.get_gpu_info(),
                "temperature": self.get_temperature(),
            }

        except Exception as e:
            logger.error("Erro ao obter resumo do sistema: %s", e)
            return {
                "error": str(e),
            }


if __name__ == "__main__":
    server = SystemInfoMCPServer()
    try:
        server.start()
        logger.info("SystemInfo MCPServer running...")
        if server._thread:
            server._thread.join()
    except KeyboardInterrupt:
        server.stop()
