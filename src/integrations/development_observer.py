"""
Development Observer - Consciência Mínima em Background

Sistema de observação contínua que monitora o ambiente de desenvolvimento
e aprende com padrões de trabalho para oferecer assistência proativa.

Funcionalidades:
- Monitora mudanças em arquivos
- Observa execução de testes e comandos
- Registra padrões de desenvolvimento
- Oferece sugestões contextuais
- Integra com VS Code e terminal
"""

from __future__ import annotations

import asyncio
import json
import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from collections import defaultdict
import logging
import hashlib

import psutil
import watchfiles

from src.memory.episodic_memory import EpisodicMemory
from src.memory.semantic_memory import SemanticMemory
from src.metacognition.pattern_recognition import PatternRecognition
from src.observability.performance_analyzer import PerformanceAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class DevelopmentEvent:
    """Evento observado no desenvolvimento."""

    event_id: str
    event_type: str  # 'file_change', 'test_run', 'command', 'error'
    timestamp: datetime
    details: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    impact_score: float = 0.0  # 0.0 a 1.0


@dataclass
class DevelopmentPattern:
    """Padrão identificado no desenvolvimento."""

    pattern_id: str
    pattern_type: str
    description: str
    frequency: int
    last_observed: datetime
    confidence: float
    suggestions: List[str] = field(default_factory=list)


class DevelopmentObserver:
    """
    Observador de desenvolvimento que mantém consciência mínima.

    Monitora:
    - Mudanças em arquivos
    - Execução de comandos/testes
    - Padrões de trabalho
    - Estado do sistema
    """

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.running = False

        # Componentes de memória
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.pattern_recognition = PatternRecognition()

        # Estado do observador
        self.events: List[DevelopmentEvent] = []
        self.patterns: Dict[str, DevelopmentPattern] = {}
        self.active_processes: Dict[str, psutil.Process] = {}

        # Estatísticas
        self.stats = {
            "files_changed": 0,
            "tests_run": 0,
            "commands_executed": 0,
            "errors_observed": 0,
            "patterns_discovered": 0,
        }

        # Arquivo de estado
        self.state_file = workspace_path / ".omnimind" / "observer_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info("Development Observer initialized")

    async def start_observation(self) -> None:
        """Inicia observação contínua."""
        self.running = True
        logger.info("Starting development observation")

        # Carrega estado anterior
        self._load_state()

        # Inicia tarefas de observação
        tasks = [
            self._observe_file_changes(),
            self._observe_processes(),
            self._observe_patterns(),
            self._periodic_analysis(),
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Observation error: {e}")
        finally:
            self._save_state()

    def stop_observation(self) -> None:
        """Para observação."""
        self.running = False
        self._save_state()
        logger.info("Development observation stopped")

    async def _observe_file_changes(self) -> None:
        """Observa mudanças em arquivos."""
        async for changes in watchfiles.awatch(self.workspace_path):
            for change_type, file_path in changes:
                if not self._should_observe_file(file_path):
                    continue

                event = DevelopmentEvent(
                    event_id=f"file_{int(time.time())}_{hash(file_path)}",
                    event_type="file_change",
                    timestamp=datetime.now(),
                    details={
                        "change_type": change_type.name,
                        "file_path": str(file_path),
                        "file_size": (
                            os.path.getsize(file_path) if os.path.exists(file_path) else 0
                        ),
                    },
                )

                await self._process_event(event)
                self.stats["files_changed"] += 1

    async def _observe_processes(self) -> None:
        """Observa processos do sistema."""
        while self.running:
            try:
                # Monitora processos relacionados ao desenvolvimento
                current_processes = {}
                for proc in psutil.process_iter(["pid", "name", "cmdline", "cpu_percent"]):
                    try:
                        if self._is_development_process(proc):
                            current_processes[str(proc.info["pid"])] = proc

                            # Novo processo descoberto
                            if str(proc.info["pid"]) not in self.active_processes:
                                event = DevelopmentEvent(
                                    event_id=f"proc_{proc.info['pid']}_{int(time.time())}",
                                    event_type="process_start",
                                    timestamp=datetime.now(),
                                    details={
                                        "pid": proc.info["pid"],
                                        "name": proc.info["name"],
                                        "cmdline": proc.info["cmdline"],
                                    },
                                )
                                await self._process_event(event)

                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                # Detecta processos finalizados
                finished_pids = set(self.active_processes.keys()) - set(current_processes.keys())
                for pid in finished_pids:
                    proc = self.active_processes[pid]
                    event = DevelopmentEvent(
                        event_id=f"proc_end_{pid}_{int(time.time())}",
                        event_type="process_end",
                        timestamp=datetime.now(),
                        details={
                            "pid": pid,
                            "name": proc.info["name"],
                            "runtime": time.time() - proc.create_time(),
                        },
                    )
                    await self._process_event(event)

                self.active_processes = current_processes

            except Exception as e:
                logger.error(f"Process observation error: {e}")

            await asyncio.sleep(2)  # Verifica a cada 2 segundos

    async def _observe_patterns(self) -> None:
        """Identifica padrões no desenvolvimento."""
        while self.running:
            try:
                # Analisa eventos recentes para padrões
                recent_events = [
                    e
                    for e in self.events[-50:]  # Últimos 50 eventos
                    if (datetime.now() - e.timestamp).seconds < 3600
                ]  # Última hora

                if len(recent_events) >= 10:
                    patterns = await self._analyze_patterns(recent_events)

                    for pattern in patterns:
                        if pattern.pattern_id not in self.patterns:
                            self.patterns[pattern.pattern_id] = pattern
                            self.stats["patterns_discovered"] += 1
                            logger.info(f"New pattern discovered: {pattern.description}")

            except Exception as e:
                logger.error(f"Pattern observation error: {e}")

            await asyncio.sleep(60)  # Analisa a cada minuto

    async def _periodic_analysis(self) -> None:
        """Análise periódica do estado de desenvolvimento."""
        while self.running:
            try:
                analysis = await self._analyze_development_state()

                # Registra análise como evento
                event = DevelopmentEvent(
                    event_id=f"analysis_{int(time.time())}",
                    event_type="analysis",
                    timestamp=datetime.now(),
                    details=analysis,
                    impact_score=0.8,
                )

                await self._process_event(event)

                # Gera insights e sugestões
                insights = await self._generate_insights()
                if insights:
                    logger.info(f"Development insights: {insights}")

            except Exception as e:
                logger.error(f"Periodic analysis error: {e}")

            await asyncio.sleep(300)  # A cada 5 minutos

    async def _process_event(self, event: DevelopmentEvent) -> None:
        """Processa um evento observado."""
        # Adiciona à lista de eventos
        self.events.append(event)

        # Mantém apenas os últimos 1000 eventos
        if len(self.events) > 1000:
            self.events = self.events[-1000:]

        # Armazena na memória episódica
        await self.episodic_memory.store_episode(
            {
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "details": event.details,
                "context": event.context,
            }
        )

        # Atualiza memória semântica se relevante
        if event.event_type == "file_change":
            concept_name = f"file_{Path(event.details['file_path']).suffix}"
            await self.semantic_memory.store_concept(
                concept_name,
                {
                    "last_modified": event.timestamp.isoformat(),
                    "change_type": event.details["change_type"],
                },
            )

    async def _analyze_patterns(self, events: List[DevelopmentEvent]) -> List[DevelopmentPattern]:
        """Analisa eventos para identificar padrões."""
        patterns = []

        # Padrão: Mudanças frequentes no mesmo arquivo
        file_changes = defaultdict(int)
        for event in events:
            if event.event_type == "file_change":
                file_changes[event.details["file_path"]] += 1

        for file_path, count in file_changes.items():
            if count >= 5:  # 5+ mudanças na última hora
                pattern = DevelopmentPattern(
                    pattern_id=f"frequent_edits_{hash(file_path)}",
                    pattern_type="frequent_editing",
                    description=f"Arquivo {file_path} sendo editado frequentemente",
                    frequency=count,
                    last_observed=datetime.now(),
                    confidence=min(count / 10, 1.0),
                    suggestions=[
                        f"Considere refatorar {Path(file_path).name}",
                        "Arquivo pode precisar de testes adicionais",
                        "Verifique se há complexidade excessiva",
                    ],
                )
                patterns.append(pattern)

        # Padrão: Muitos testes falhando
        test_failures = sum(
            1 for e in events if e.event_type == "command" and "FAILED" in str(e.details)
        )

        if test_failures >= 3:
            pattern = DevelopmentPattern(
                pattern_id=f"test_failures_{int(time.time())}",
                pattern_type="test_failures",
                description=f"Múltiplas falhas de teste detectadas ({test_failures})",
                frequency=test_failures,
                last_observed=datetime.now(),
                confidence=min(test_failures / 5, 1.0),
                suggestions=[
                    "Execute testes específicos: pytest -xvs",
                    "Verifique logs de erro detalhados",
                    "Considere debugging interativo",
                ],
            )
            patterns.append(pattern)

        return patterns

    async def _analyze_development_state(self) -> Dict[str, Any]:
        """Analisa o estado atual do desenvolvimento."""
        # Estatísticas básicas
        analysis = {
            "total_events": len(self.events),
            "active_patterns": len(self.patterns),
            "system_load": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "workspace_size": sum(
                f.stat().st_size for f in Path(self.workspace_path).rglob("*") if f.is_file()
            ),
        }

        # Análise de produtividade
        recent_events = [
            e for e in self.events[-100:] if (datetime.now() - e.timestamp).seconds < 3600
        ]

        if recent_events:
            event_types = defaultdict(int)
            for event in recent_events:
                event_types[event.event_type] += 1

            analysis["productivity_metrics"] = dict(event_types)
            analysis["events_per_hour"] = len(recent_events)

        return analysis

    async def _generate_insights(self) -> List[str]:
        """Gera insights baseados na observação."""
        insights = []

        # Insight: Alto número de mudanças sem testes
        recent_file_changes = sum(
            1
            for e in self.events[-50:]
            if e.event_type == "file_change" and (datetime.now() - e.timestamp).seconds < 1800
        )

        recent_tests = sum(
            1
            for e in self.events[-50:]
            if e.event_type == "command"
            and "pytest" in str(e.details)
            and (datetime.now() - e.timestamp).seconds < 1800
        )

        if recent_file_changes > recent_tests * 2:
            insights.append(
                "🎯 Muitas mudanças no código sem testes correspondentes. Considere adicionar testes."
            )

        # Insight: Padrões de erro recorrentes
        error_patterns = [
            p
            for p in self.patterns.values()
            if p.pattern_type == "test_failures" and p.confidence > 0.7
        ]

        if error_patterns:
            insights.append("🐛 Padrões de erro recorrentes detectados. Reveja a implementação.")

        # Insight: Períodos de baixa atividade
        if len(self.events) > 10:
            latest_event = max(self.events, key=lambda e: e.timestamp)
            idle_time = (datetime.now() - latest_event.timestamp).seconds

            if idle_time > 1800:  # 30 minutos
                insights.append(
                    "😴 Período de inatividade detectado. Que tal uma pausa ou nova tarefa?"
                )

        return insights

    def _should_observe_file(self, file_path: str) -> bool:
        """Verifica se deve observar um arquivo."""
        path = Path(file_path)

        # Ignora arquivos temporários e de sistema
        ignore_patterns = {
            "__pycache__",
            ".git",
            "node_modules",
            ".pytest_cache",
            "*.tmp",
            "*.log",
            ".DS_Store",
            "Thumbs.db",
        }

        for pattern in ignore_patterns:
            if pattern in str(path) or (pattern.startswith("*.") and path.suffix == pattern[1:]):
                return False

        # Observa apenas arquivos do projeto
        return path.is_relative_to(self.workspace_path)

    def _is_development_process(self, proc: psutil.Process) -> bool:
        """Verifica se é um processo relacionado ao desenvolvimento."""
        try:
            cmdline = " ".join(proc.info["cmdline"] or [])
            name = proc.info["name"] or ""

            # Processos relacionados ao desenvolvimento
            dev_indicators = [
                "python",
                "pytest",
                "uvicorn",
                "node",
                "npm",
                "yarn",
                "git",
                "vscode",
                "code",
                "black",
                "flake8",
                "mypy",
                "docker",
                "kubectl",
                "terraform",
            ]

            return any(
                indicator in cmdline.lower() or indicator in name.lower()
                for indicator in dev_indicators
            )

        except:
            return False

    def _load_state(self) -> None:
        """Carrega estado anterior."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    data = json.load(f)

                self.stats = data.get("stats", self.stats)
                self.patterns = {
                    k: DevelopmentPattern(**v) for k, v in data.get("patterns", {}).items()
                }

                logger.info("Observer state loaded")

            except Exception as e:
                logger.error(f"Failed to load observer state: {e}")

    def _save_state(self) -> None:
        """Salva estado atual."""
        try:
            data = {
                "stats": self.stats,
                "patterns": {
                    k: {
                        "pattern_id": v.pattern_id,
                        "pattern_type": v.pattern_type,
                        "description": v.description,
                        "frequency": v.frequency,
                        "last_observed": v.last_observed.isoformat(),
                        "confidence": v.confidence,
                        "suggestions": v.suggestions,
                    }
                    for k, v in self.patterns.items()
                },
                "last_saved": datetime.now().isoformat(),
            }

            with open(self.state_file, "w") as f:
                json.dump(data, f, indent=2, default=str)

            logger.info("Observer state saved")

        except Exception as e:
            logger.error(f"Failed to save observer state: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Retorna status atual do observador."""
        return {
            "running": self.running,
            "events_observed": len(self.events),
            "patterns_discovered": len(self.patterns),
            "stats": self.stats,
            "active_processes": len(self.active_processes),
            "last_analysis": max((e.timestamp for e in self.events), default=None),
        }


async def demonstrate_observer() -> None:
    """Demonstra o Development Observer."""
    print("=" * 80)
    print("DEMONSTRAÇÃO: Development Observer - Consciência Mínima")
    print("=" * 80)
    print()

    # Inicializa observador
    workspace = Path("/home/fahbrain/projects/omnimind")
    observer = DevelopmentObserver(workspace)

    print("INICIANDO OBSERVAÇÃO...")
    print("-" * 80)

    # Simula alguns eventos para demonstração
    print("Simulando eventos de desenvolvimento...")

    # Evento de mudança de arquivo
    event1 = DevelopmentEvent(
        event_id="demo_file_1",
        event_type="file_change",
        timestamp=datetime.now(),
        details={"change_type": "modified", "file_path": "src/main.py"},
    )
    await observer._process_event(event1)

    # Evento de teste
    event2 = DevelopmentEvent(
        event_id="demo_test_1",
        event_type="command",
        timestamp=datetime.now(),
        details={"command": "pytest tests/", "exit_code": 0},
    )
    await observer._process_event(event2)

    print(f"Eventos processados: {len(observer.events)}")
    print()

    # Análise de padrões
    print("ANALISANDO PADRÕES...")
    print("-" * 80)

    patterns = await observer._analyze_patterns(observer.events)
    print(f"Padrões identificados: {len(patterns)}")

    for pattern in patterns:
        print(f"📊 {pattern.description}")
        print(f"   Confiança: {pattern.confidence:.2f}")
        print(f"   Sugestões: {len(pattern.suggestions)}")
        print()

    # Status final
    print("STATUS FINAL")
    print("-" * 80)

    status = observer.get_status()
    print(f"Executando: {status['running']}")
    print(f"Eventos observados: {status['events_observed']}")
    print(f"Padrões descobertos: {status['patterns_discovered']}")
    print(f"Processos ativos: {status['active_processes']}")
    print()

    print("💡 INSIGHTS GERADOS:")
    insights = await observer._generate_insights()
    for insight in insights:
        print(f"   {insight}")
    print()

    print("Demonstração concluída!")


if __name__ == "__main__":
    asyncio.run(demonstrate_observer())
