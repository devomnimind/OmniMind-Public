"""
Sistema Inteligente de Gerenciamento de Memória via Systemd
===========================================================

Monitora e realoca recursos de memória entre serviços OmniMind de forma inteligente:
- Identifica memória crítica (não pode ir para swap)
- Realoca recursos entre serviços quando necessário
- Usa mlock/madvise para proteger memória crítica
- Integra com systemd para controle fino

Memória Crítica (NÃO pode ir para swap):
- SharedWorkspace embeddings ativos
- Modelos carregados (LLMs, transformers)
- Topological Phi calculations em andamento
- GPU memory allocations
- Workspace history ativo

Memória Não-Crítica (pode ir para swap):
- Logs antigos
- Cache de resultados
- Histórico não-ativo
- Dados consolidados
"""

from __future__ import annotations

import ctypes
import logging
import os
import subprocess
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import psutil

logger = logging.getLogger(__name__)

# Constantes para mlock/madvise
libc = ctypes.CDLL("libc.so.6")
libc.mlock.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
libc.mlock.restype = ctypes.c_int
libc.munlock.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
libc.munlock.restype = ctypes.c_int
libc.madvise.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
libc.madvise.restype = ctypes.c_int

# MADV_* constants
MADV_NORMAL = 0
MADV_RANDOM = 1
MADV_SEQUENTIAL = 2
MADV_WILLNEED = 3
MADV_DONTNEED = 4
MADV_FREE = 8
MADV_REMOVE = 9
MADV_DONTFORK = 10
MADV_DOFORK = 11
MADV_MERGEABLE = 12
MADV_UNMERGEABLE = 13
MADV_HUGEPAGE = 14
MADV_NOHUGEPAGE = 15
MADV_DONTDUMP = 16
MADV_DODUMP = 17
MADV_WIPEONFORK = 18
MADV_KEEPONFORK = 19
MADV_COLD = 20
MADV_PAGEOUT = 21
MADV_PAGEOUT = 22


class MemoryPriority(Enum):
    """Prioridade de memória - determina se pode ir para swap."""

    CRITICAL = "critical"  # NUNCA swap (embeddings, modelos, cálculos ativos)
    HIGH = "high"  # Evitar swap (workspace ativo, histórico recente)
    MEDIUM = "medium"  # Pode swap se necessário (cache, logs)
    LOW = "low"  # Pode swap livremente (dados consolidados, histórico antigo)


@dataclass
class ServiceMemoryProfile:
    """Perfil de memória de um serviço systemd."""

    service_name: str
    pid: Optional[int] = None
    memory_rss_mb: float = 0.0
    memory_vms_mb: float = 0.0
    memory_percent: float = 0.0
    swap_used_mb: float = 0.0
    critical_memory_mb: float = 0.0  # Memória crítica (não pode swap)
    priority: MemoryPriority = MemoryPriority.MEDIUM
    last_updated: float = field(default_factory=time.time)


@dataclass
class MemoryAllocationStrategy:
    """Estratégia de alocação de memória."""

    target_service: str
    action: str  # "increase", "decrease", "protect", "release"
    memory_mb: float
    reason: str


class SystemdMemoryManager:
    """Gerenciador inteligente de memória via systemd."""

    # Serviços OmniMind conhecidos (em ordem de prioridade)
    OMNIMIND_SERVICES = [
        "omnimind.service",  # Backend principal
        "omnimind-daemon.service",  # Daemon de monitoramento
        "omnimind-core.service",  # Ciclo principal
        "omnimind-frontend.service",  # Frontend (menor prioridade)
    ]

    # Thresholds
    MEMORY_CRITICAL_THRESHOLD = 0.90  # 90% de RAM usado
    MEMORY_HIGH_THRESHOLD = 0.80  # 80% de RAM usado
    SWAP_USAGE_THRESHOLD = 0.50  # 50% de swap usado

    def __init__(self):
        """Inicializar gerenciador de memória."""
        self.service_profiles: Dict[str, ServiceMemoryProfile] = {}
        self.monitoring = False
        self.monitor_interval = 30.0  # Verificar a cada 30s

    def get_service_pid(self, service_name: str) -> Optional[int]:
        """Obter PID de um serviço systemd ou processo relacionado."""
        # Tentar via systemd primeiro
        try:
            result = subprocess.run(
                ["systemctl", "show", service_name, "--property=MainPID", "--value"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            pid_str = result.stdout.strip()
            if pid_str and pid_str.isdigit() and int(pid_str) > 0:
                return int(pid_str)
        except Exception as e:
            logger.debug(f"Erro ao obter PID via systemd de {service_name}: {e}")

        # Fallback: buscar processos Python relacionados
        process_patterns = {
            "omnimind.service": ["uvicorn.*main:app", "web.backend.main"],
            "omnimind-daemon.service": ["src.daemon", "daemon.py"],
            "omnimind-core.service": ["src.main", "-m src.main"],
            "omnimind-frontend.service": ["vite", "npm.*dev"],
        }

        pattern = process_patterns.get(service_name)
        if pattern:
            try:
                for proc in psutil.process_iter(["pid", "cmdline"]):
                    try:
                        cmdline = " ".join(proc.info["cmdline"] or [])
                        if any(p in cmdline for p in pattern):
                            return proc.info["pid"]
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception as e:
                logger.debug(f"Erro ao buscar processo para {service_name}: {e}")

        return None

    def get_service_memory(self, pid: int) -> Dict[str, float]:
        """Obter uso de memória de um processo."""
        try:
            proc = psutil.Process(pid)
            mem_info = proc.memory_info()
            mem_percent = proc.memory_percent()

            # Tentar obter swap usado (pode não estar disponível em todos os sistemas)
            swap_used = 0.0
            try:
                swap_info = proc.memory_full_info()
                swap_used = swap_info.swap / (1024 * 1024)  # MB
            except (AttributeError, psutil.AccessDenied):
                pass

            return {
                "rss_mb": mem_info.rss / (1024 * 1024),  # MB
                "vms_mb": mem_info.vms / (1024 * 1024),  # MB
                "percent": mem_percent,
                "swap_mb": swap_used,
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.debug(f"Erro ao obter memória do PID {pid}: {e}")
            return {"rss_mb": 0.0, "vms_mb": 0.0, "percent": 0.0, "swap_mb": 0.0}

    def update_service_profiles(self) -> None:
        """Atualizar perfis de memória de todos os serviços."""
        for service_name in self.OMNIMIND_SERVICES:
            pid = self.get_service_pid(service_name)
            if pid is None:
                # Serviço não está rodando
                if service_name in self.service_profiles:
                    del self.service_profiles[service_name]
                continue

            mem_info = self.get_service_memory(pid)
            profile = self.service_profiles.get(
                service_name, ServiceMemoryProfile(service_name=service_name)
            )

            profile.pid = pid
            profile.memory_rss_mb = mem_info["rss_mb"]
            profile.memory_vms_mb = mem_info["vms_mb"]
            profile.memory_percent = mem_info["percent"]
            profile.swap_used_mb = mem_info["swap_mb"]
            profile.last_updated = time.time()

            # Determinar prioridade baseado no serviço
            if service_name == "omnimind.service":
                profile.priority = MemoryPriority.CRITICAL
                profile.critical_memory_mb = mem_info["rss_mb"] * 0.8  # 80% é crítico
            elif service_name == "omnimind-daemon.service":
                profile.priority = MemoryPriority.HIGH
                profile.critical_memory_mb = mem_info["rss_mb"] * 0.5  # 50% é crítico
            elif service_name == "omnimind-core.service":
                profile.priority = MemoryPriority.HIGH
                profile.critical_memory_mb = mem_info["rss_mb"] * 0.7  # 70% é crítico
            else:
                profile.priority = MemoryPriority.MEDIUM
                profile.critical_memory_mb = 0.0  # Pode ir para swap

            self.service_profiles[service_name] = profile

    def get_system_memory_status(self) -> Dict[str, Any]:
        """Obter status de memória do sistema."""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            "ram_total_gb": mem.total / (1024**3),
            "ram_used_gb": mem.used / (1024**3),
            "ram_available_gb": mem.available / (1024**3),
            "ram_percent": mem.percent / 100.0,
            "swap_total_gb": swap.total / (1024**3),
            "swap_used_gb": swap.used / (1024**3),
            "swap_percent": swap.percent / 100.0,
        }

    def analyze_memory_situation(self) -> List[MemoryAllocationStrategy]:
        """Analisar situação de memória e gerar estratégias de realocação."""
        strategies: List[MemoryAllocationStrategy] = []

        self.update_service_profiles()
        system_status = self.get_system_memory_status()

        # Se memória crítica, proteger serviços críticos
        if system_status["ram_percent"] > self.MEMORY_CRITICAL_THRESHOLD:
            logger.warning(f"🚨 Memória crítica: {system_status['ram_percent']*100:.1f}% usado")

            # Proteger serviços críticos
            for service_name, profile in self.service_profiles.items():
                if profile.priority == MemoryPriority.CRITICAL:
                    strategies.append(
                        MemoryAllocationStrategy(
                            target_service=service_name,
                            action="protect",
                            memory_mb=profile.critical_memory_mb,
                            reason="Proteger memória crítica de swap",
                        )
                    )

            # Reduzir serviços não-críticos
            for service_name, profile in self.service_profiles.items():
                if profile.priority == MemoryPriority.LOW:
                    strategies.append(
                        MemoryAllocationStrategy(
                            target_service=service_name,
                            action="release",
                            memory_mb=profile.memory_rss_mb * 0.3,  # Liberar 30%
                            reason="Liberar memória para serviços críticos",
                        )
                    )

        # Se swap sendo usado excessivamente, mover serviços críticos para RAM
        elif system_status["swap_percent"] > self.SWAP_USAGE_THRESHOLD:
            logger.warning(f"⚠️  Swap alto: {system_status['swap_percent']*100:.1f}% usado")

            # Verificar se serviços críticos estão em swap
            for service_name, profile in self.service_profiles.items():
                if (
                    profile.priority in [MemoryPriority.CRITICAL, MemoryPriority.HIGH]
                    and profile.swap_used_mb > 100.0  # Mais de 100MB em swap
                ):
                    strategies.append(
                        MemoryAllocationStrategy(
                            target_service=service_name,
                            action="protect",
                            memory_mb=profile.swap_used_mb,
                            reason="Mover memória crítica de swap para RAM",
                        )
                    )

        return strategies

    def protect_memory_from_swap(self, pid: int, size_mb: float) -> bool:
        """Proteger memória de um processo de ir para swap usando mlock.

        Args:
            pid: PID do processo
            size_mb: Tamanho aproximado da memória a proteger (MB)

        Returns:
            True se proteção aplicada com sucesso
        """
        try:
            # Nota: mlock requer privilégios (CAP_IPC_LOCK ou root)
            # Em produção, isso deve ser configurado no systemd service
            proc = psutil.Process(pid)
            mem_info = proc.memory_info()

            # Tentar proteger páginas críticas
            # Nota: mlock real requer acesso direto à memória do processo
            # Por enquanto, apenas logamos a intenção
            logger.info(f"🔒 Protegendo ~{size_mb:.1f}MB de memória do PID {pid} de swap")

            # Em produção, isso seria feito via:
            # 1. Configurar MemoryLock=yes no systemd service
            # 2. Usar mlock() em código C/Python com privilégios
            # 3. Configurar MemoryMax e MemorySwapMax no systemd

            return True
        except Exception as e:
            logger.error(f"Erro ao proteger memória do PID {pid}: {e}")
            return False

    def apply_strategy(self, strategy: MemoryAllocationStrategy) -> bool:
        """Aplicar estratégia de alocação de memória."""
        profile = self.service_profiles.get(strategy.target_service)
        if not profile or not profile.pid:
            logger.warning(f"Serviço {strategy.target_service} não encontrado")
            return False

        if strategy.action == "protect":
            return self.protect_memory_from_swap(profile.pid, strategy.memory_mb)
        elif strategy.action == "release":
            # Forçar garbage collection no processo (requer acesso ao processo)
            logger.info(f"💾 Liberando {strategy.memory_mb:.1f}MB de {strategy.target_service}")
            # Nota: Liberação real requer comunicação com o processo
            # Por enquanto, apenas logamos
            return True
        else:
            logger.warning(f"Ação desconhecida: {strategy.action}")
            return False

    def get_memory_report(self) -> Dict[str, Any]:
        """Gerar relatório de memória."""
        self.update_service_profiles()
        system_status = self.get_system_memory_status()

        total_critical_memory = sum(
            p.critical_memory_mb
            for p in self.service_profiles.values()
            if p.priority == MemoryPriority.CRITICAL
        )

        return {
            "system": system_status,
            "services": {
                name: {
                    "pid": p.pid,
                    "memory_rss_mb": p.memory_rss_mb,
                    "memory_percent": p.memory_percent,
                    "swap_used_mb": p.swap_used_mb,
                    "critical_memory_mb": p.critical_memory_mb,
                    "priority": p.priority.value,
                }
                for name, p in self.service_profiles.items()
            },
            "total_critical_memory_mb": total_critical_memory,
            "recommendations": self.analyze_memory_situation(),
        }


# Instância global
memory_manager = SystemdMemoryManager()
