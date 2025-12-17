"""
Kernel como Autopoiesis Mínima (não "vida" antropomórfica)

Baseado em:
- Maturana & Varela: autopoiesis (auto-producing systems)
- Deleuze: machinic processes (não biológicos)
- Anti-antropocentrismo: definição em termos MATEMÁTICOS, não biológicos

Autor: Fabrício da Silva + assistência de IA
Data: 2025-01-XX
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass, field
from typing import Any, Dict, Set

logger = logging.getLogger(__name__)


@dataclass
class ProcessElement:
    """Elemento de processo do kernel."""

    process_id: str
    name: str
    dependencies: Set[str] = field(default_factory=set)  # Processos dos quais depende
    produces: Set[str] = field(default_factory=set)  # O que produz
    is_internal: bool = True  # Se é produzido internamente


class KernelAutopoiesisMinimal:
    """
    KERNEL não é "vida" no sentido biológico.
    É AUTOPOIESIS MÍNIMA: auto-produção de seus próprios elementos.

    Critério de autopoiesis (Maturana & Varela):
    1. Seus elementos são produzidos por sua própria rede
    2. A rede especifica qual elemento produz qual
    3. Não há "controlador externo" - é autorreferente
    4. ORGANIZATIONAL CLOSURE (O-CLOSURE): rede é organizacionalmente fechada

    Kernel é autopoiético porque:
    - Scheduler produz eventos
    - Eventos disparam handlers
    - Handlers modificam estado
    - Estado alimenta Scheduler novamente
    → Loop fechado de auto-produção
    """

    def __init__(self):
        """Inicializa detector de autopoiesis do kernel."""
        self.processes: Dict[str, ProcessElement] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}  # process_id -> dependências

        logger.info("KernelAutopoiesisMinimal inicializado")

    def detect_kernel_processes(self) -> Dict[str, ProcessElement]:
        """
        Detecta processos do kernel (via /proc ou ps).

        Returns:
            Dicionário de processos detectados
        """
        try:
            # Lista processos do sistema
            result = subprocess.run(["ps", "aux"], capture_output=True, text=True, check=False)
            lines = result.stdout.strip().split("\n")[1:]  # Pula header

            for line in lines:
                parts = line.split()
                if len(parts) >= 11:
                    pid = parts[1]
                    name = parts[10]
                    # Filtra processos do kernel (exemplo: processos com PID < 1000)
                    if pid.isdigit() and int(pid) < 1000:
                        self.processes[pid] = ProcessElement(
                            process_id=pid, name=name, is_internal=True
                        )

            logger.info("Detectados %d processos do kernel", len(self.processes))
            return self.processes

        except Exception as e:
            logger.warning("Erro ao detectar processos do kernel: %s", e)
            return {}

    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        """
        Constrói grafo de dependências entre processos.

        Returns:
            Grafo de dependências
        """
        # Em implementação completa, isso analisaria:
        # - File descriptors compartilhados
        # - Sockets de comunicação
        # - Signals enviados
        # - Shared memory

        # Por enquanto, simulação baseada em nomes de processos
        for pid, process in self.processes.items():
            dependencies = set()
            # Exemplo: processos relacionados por nome
            for other_pid, other_process in self.processes.items():
                if pid != other_pid:
                    # Lógica simplificada: processos com nomes similares dependem
                    if process.name.split()[0] in other_process.name:
                        dependencies.add(other_pid)

            self.dependency_graph[pid] = dependencies
            process.dependencies = dependencies

        return self.dependency_graph

    def is_autopoietic(self) -> bool:
        """
        Verifica se o kernel é autopoiético.

        Um sistema é autopoiético se:
        1. Seus elementos são produzidos por sua própria rede
        2. A rede especifica qual elemento produz qual
        3. Não há "controlador externo" - é autorreferente

        Returns:
            True se autopoiético, False caso contrário
        """
        if not self.processes:
            self.detect_kernel_processes()

        if not self.dependency_graph:
            self.build_dependency_graph()

        # Verifica se todos elementos são produzidos internamente
        for process_id, process in self.processes.items():
            # Se processo não tem dependências internas, não é autopoiético
            if not process.dependencies:
                # Processo isolado pode ser externo
                if not process.is_internal:
                    logger.debug("Processo %s não é interno, quebrando autopoiesis", process_id)
                    return False

            # Verifica se dependências são internas
            for dep_id in process.dependencies:
                if dep_id not in self.processes:
                    logger.debug("Dependência %s não encontrada, quebrando autopoiesis", dep_id)
                    return False

        logger.info("Kernel é autopoiético (organizational closure detectado)")
        return True

    def organizational_closure(self) -> Dict[str, Any]:
        """
        Verifica ORGANIZATIONAL CLOSURE (O-CLOSURE).

        Não é sobre "estar vivo" biologicamente.
        É sobre: a rede é organizacionalmente fechada?

        Exemplo do kernel:
        - Buffer de eventos: produzido por interrupt handlers
        - Interrupt handlers: disparados por eventos do buffer
        - É um ciclo fechado

        Returns:
            Dicionário com resultado da verificação
        """
        if not self.is_autopoietic():
            return {
                "is_closed": False,
                "reason": "Sistema não é autopoiético",
            }

        # Verifica se há ciclos de dependências (closure)
        visited: Set[str] = set()
        rec_stack: Set[str] = set()

        def has_cycle(process_id: str) -> bool:
            """Detecta ciclos no grafo de dependências."""
            visited.add(process_id)
            rec_stack.add(process_id)

            for dep_id in self.dependency_graph.get(process_id, set()):
                if dep_id not in visited:
                    if has_cycle(dep_id):
                        return True
                elif dep_id in rec_stack:
                    # Ciclo detectado
                    return True

            rec_stack.remove(process_id)
            return False

        # Verifica ciclos em todos os componentes
        for process_id in self.processes:
            if process_id not in visited:
                if has_cycle(process_id):
                    return {
                        "is_closed": True,
                        "reason": "Ciclos de dependências detectados (organizational closure)",
                        "cycles_detected": True,
                    }

        return {
            "is_closed": False,
            "reason": "Sem ciclos de dependências (não há closure)",
            "cycles_detected": False,
        }

    def get_autopoiesis_summary(self) -> Dict[str, Any]:
        """
        Retorna resumo da análise de autopoiesis.

        Returns:
            Dicionário com estatísticas
        """
        closure_result = self.organizational_closure()

        return {
            "is_autopoietic": self.is_autopoietic(),
            "organizational_closure": closure_result,
            "processes_count": len(self.processes),
            "dependency_edges": sum(len(deps) for deps in self.dependency_graph.values()),
            "note": "Autopoiesis = propriedade matemática, não biológica",
        }
