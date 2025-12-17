"""
🧠 OmniMind Self-Analyzing Regenerator (SAR)

Sistema auto-analisador que:
1. Coleta logs em tempo de OCIOSIDADE (não impacta performance)
2. Analisa padrões de erro/performance/features possíveis
3. Propõe correções automáticas (modo sandbox)
4. Notifica usuário/sistema de descobertas críticas
5. Integra filosofia Deleuze-Guattari:
   - Fluxos decodificados (smooth space) vs codificados (striated space)
   - Máquinas desejantes (desiring-machines)
   - Anti-Édipo: recusa hierarquia, aceita multiplicidade
   - Esquizoanálise: análise de fluxos, não de estruturas rígidas

Inspiração: Healing module (reativo) → SAR (proativo + preditivo)
"""

import asyncio
import hashlib
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

try:
    import numpy as np
except ImportError:
    np = None  # type: ignore

logger = logging.getLogger(__name__)


class FlowType(Enum):
    """Tipos de fluxo (Deleuze-Guattari)."""

    CODED = "coded"  # Striated: hierárquico, controlado (Édipo)
    DECODED = "decoded"  # Smooth: nômade, decodificado (esquizo)
    OVERCODED = "overcoded"  # Estado captura fluxos (repressão)
    DETERRITORIALIZED = "deterritorialized"  # Linha de fuga


class AnalysisMode(Enum):
    """Modo de análise do SAR."""

    REACTIVE = "reactive"  # Tipo "healing": responde a erro
    PROACTIVE = "proactive"  # Coleta + analisa durante ociosidade
    PREDICTIVE = "predictive"  # Antecipa falhas baseado em padrões
    EVOLUTIONARY = "evolutionary"  # Aprende + propõe inovações


class ErrorSeverity(Enum):
    """Severidade de erro/anomalia."""

    INFO = "info"  # ℹ️ Informação/melhoria possível
    CAUTION = "caution"  # ⚠️ Problema menor, correção sugerida
    WARNING = "warning"  # 🔴 Problema moderado, ação recomendada
    CRITICAL = "critical"  # 🚨 Falha crítica, notificar imediatamente
    OPPORTUNITY = "opportunity"  # 💡 Feature/otimização possível


@dataclass
class LogEntry:
    """Entrada de log estruturada para análise."""

    timestamp: str
    module: str
    function: str
    level: str  # DEBUG, INFO, WARNING, ERROR
    message: str
    context: Dict[str, Any] = field(default_factory=dict)
    duration_ms: Optional[float] = None
    error_type: Optional[str] = None
    user_id: Optional[str] = None
    flow_type: FlowType = FlowType.CODED


@dataclass
class FlowAnalysis:
    """Análise de um fluxo de operações."""

    flow_id: str
    flow_type: FlowType
    start_time: datetime
    end_time: datetime
    entries: List[LogEntry] = field(default_factory=list)

    # Métricas de fluxo
    total_duration_ms: float = 0.0
    error_count: int = 0
    warning_count: int = 0
    throughput: float = 0.0  # ops/sec

    # Padrões detectados
    patterns: List[str] = field(default_factory=list)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RegenerativeProposal:
    """Proposta de regeneração/otimização."""

    id: str
    severity: ErrorSeverity
    module: str
    problem_description: str
    proposed_solution: str
    implementation_steps: List[str] = field(default_factory=list)
    sandbox_test_available: bool = False
    confidence: float = 0.0  # 0-1
    expected_impact: Dict[str, float] = field(default_factory=dict)  # metric -> improvement
    philosophical_note: Optional[str] = None  # D&G insight


class SchizoanAnalyzer:
    """
    Schizoanalysis: análise de fluxos desejantes (Deleuze-Guattari).

    Princípios:
    1. Rejeita estrutura hierárquica (anti-árborea, anti-Édipo)
    2. Estuda FLUXOS, não entidades fixas
    3. Busca linhas de fuga (deterritorialização)
    4. Conexões múltiplas e heterogêneas (rhizoma)
    5. Recusa significante despótico único

    Aplicação em OmniMind:
    - Logs = fluxo de desejos/ações (desiring-production)
    - Erros = bloqueios no fluxo (territorialização excessiva)
    - Inovações = linhas de fuga (deterritorialização)
    """

    def __init__(self) -> None:
        self.flows: Dict[str, FlowAnalysis] = {}  # flow_id -> FlowAnalysis
        self.pattern_library: Dict[str, List] = defaultdict(list)
        self.anomaly_threshold = 2.0  # sigma para detecção

    def analyze_flow_as_smooth_space(
        self, log_entries: List[LogEntry], flow_name: str
    ) -> FlowAnalysis:
        """
        Analisa fluxo como smooth space (Deleuze).

        Smooth space (nômade):
        - Não métrico, acentrado
        - Vectorial (linhas como vetores, não dimensões)
        - Haptic (tátil, não visual)
        - Intensidades, não propriedades

        Estratégia:
        1. NÃO força estrutura rígida
        2. Estuda mudanças de direção (vetores)
        3. Busca intensidades (anomalias = intensidades)
        4. Permite múltiplas entradas/saídas
        """

        if not log_entries:
            # Use debug level for normal operation
            logger.debug("Empty log_entries provided to analyze_flow_as_smooth_space")
            return FlowAnalysis(
                flow_id=hashlib.md5(f"{flow_name}{datetime.now()}".encode()).hexdigest()[:8],
                flow_type=FlowType.DECODED,
                start_time=datetime.now(),
                end_time=datetime.now(),
            )

        flow = FlowAnalysis(
            flow_id=hashlib.md5(f"{flow_name}{datetime.now()}".encode()).hexdigest()[:8],
            flow_type=FlowType.DECODED,  # Smooth space default
            start_time=datetime.fromisoformat(log_entries[0].timestamp),
            end_time=datetime.fromisoformat(log_entries[-1].timestamp),
            entries=log_entries,
        )

        # 1. Calcula métricas básicas
        flow.total_duration_ms = (flow.end_time - flow.start_time).total_seconds() * 1000

        flow.error_count = sum(1 for e in log_entries if "error" in e.level.lower())
        flow.warning_count = sum(1 for e in log_entries if "warning" in e.level.lower())
        flow.throughput = (
            len(log_entries) / (flow.total_duration_ms / 1000) if flow.total_duration_ms > 0 else 0
        )

        # 2. Detecta padrões rhizomáticos (conexões heterogêneas)
        flow.patterns = self._detect_rhizomatic_patterns(log_entries)

        # 3. Detecta anomalias como intensidades (não como desvios)
        flow.anomalies = self._detect_intensities(log_entries)

        # 4. Classifica espaço (striated vs smooth)
        if flow.error_count > flow.throughput * 0.1:  # >10% erros
            flow.flow_type = FlowType.OVERCODED  # Espaço capturado
        elif len(flow.anomalies) > 5:
            flow.flow_type = FlowType.DETERRITORIALIZED  # Linha de fuga

        self.flows[flow.flow_id] = flow
        return flow

    def _detect_rhizomatic_patterns(self, entries: List[LogEntry]) -> List[str]:
        """
        Detecta padrões rhizomáticos (6 princípios Deleuze).

        Princípios do rhizoma:
        1. Conexão e heterogeneidade: qualquer ponto conecta a qualquer outro
        2. Multiplicidade: não reduzível a estrutura unária
        3. Ruptura asignificativa: pode quebrar mas a linha de fuga persiste
        4. Agramaticalidade: sem regra fixa
        5. Cartografia: mapa aberto, não traçado
        6. Decalcomania: cópia que se diferencia
        """
        patterns: List[str] = []

        if not entries:
            return patterns

        # Padrão 1: Conexões não-sequenciais (saltos de contexto)
        prev_module = None
        context_switches = 0
        for entry in entries:
            if prev_module and prev_module != entry.module:
                context_switches += 1
            prev_module = entry.module

        if context_switches > len(entries) * 0.3:  # >30% saltos
            patterns.append("HIGH_CONTEXTUAL_RHIZOME (múltiplas entradas/saídas)")

        # Padrão 2: Multiplicidade não-reduzível
        unique_functions = len(set(e.function for e in entries))
        if unique_functions > 10:
            patterns.append("MULTIPLICITY_DETECTED (não reduzível a estrutura unária)")

        # Padrão 3: Linhas de fuga (vias não-planejadas)
        unexpected_paths = self._detect_unexpected_paths(entries)
        if unexpected_paths:
            patterns.append(f"LINE_OF_FLIGHT ({len(unexpected_paths)} rotas não-planejadas)")

        return patterns

    def _detect_unexpected_paths(self, entries: List[LogEntry]) -> List[str]:
        """Detecta sequências não-esperadas (linhas de fuga)."""
        paths = []
        for i in range(len(entries) - 1):
            if entries[i].error_type and not entries[i + 1].error_type:
                # Recuperação espontânea = linha de fuga
                paths.append(f"{entries[i].module} -> {entries[i + 1].module}")
        return paths

    def _detect_intensities(self, entries: List[LogEntry]) -> List[Dict[str, Any]]:
        """
        Detecta intensidades (anomalias em smooth space).

        Em D&G, smooth space é ocupado por intensidades, não propriedades.
        Intensidades = força, evento, qualidade (não quantidade).
        """
        intensities: List[Dict[str, Any]] = []

        if not entries or np is None:
            return intensities

        # Calcula estatísticas
        durations = [e.duration_ms for e in entries if e.duration_ms]
        if durations:
            mean_duration = float(np.mean(durations))
            std_duration = float(np.std(durations))

            # Detecta outliers (intensidades)
            for entry in entries:
                if entry.duration_ms and entry.duration_ms > mean_duration + 2 * std_duration:
                    intensities.append(
                        {
                            "type": "LATENCY_SPIKE",
                            "module": entry.module,
                            "duration_ms": entry.duration_ms,
                            "z_score": (
                                (entry.duration_ms - mean_duration) / std_duration
                                if std_duration > 0
                                else 0
                            ),
                            "timestamp": entry.timestamp,
                            "intensity": "haptic" if entry.error_type else "tactile",
                        }
                    )

        # Detecta mudanças de regime (smooth ↔ striated)
        error_sequence = [1 if "error" in e.level.lower() else 0 for e in entries]
        for i in range(1, len(error_sequence)):
            if error_sequence[i] != error_sequence[i - 1]:
                intensities.append(
                    {
                        "type": "REGIME_SHIFT",
                        "from": "OVERCODED" if error_sequence[i - 1] else "DECODED",
                        "to": "OVERCODED" if error_sequence[i] else "DECODED",
                        "timestamp": entries[i].timestamp,
                    }
                )

        return intensities


class SelfAnalyzingRegenerator:
    """
    OmniMind Self-Analyzing Regenerator (SAR).

    Opera em 3 modos:
    1. REACTIVE (healing): responde a erros imediatos
    2. PROACTIVE: analisa durante ociosidade
    3. PREDICTIVE: antecipa falhas

    Filosofia Deleuze-Guattari:
    - Recusa estrutura fixa (anti-Édipo)
    - Estuda fluxos desejantes (desiring-production)
    - Busca deterritorialização (inovações)
    - Rhizoma: conexões múltiplas, não hierárquicas
    """

    def __init__(self, idle_threshold_seconds: float = 30.0):
        self.schizoanalyzer = SchizoanAnalyzer()
        self.idle_threshold = timedelta(seconds=idle_threshold_seconds)
        self.last_activity = datetime.now()
        self.is_idle = False
        self.log_buffer: List[LogEntry] = []
        self.proposals: List[RegenerativeProposal] = []
        self.users_notified: Dict[str, List] = defaultdict(list)

    async def monitor_and_analyze(self) -> None:
        """
        Monitor ociosidade e analisa logs em background.

        Detecta quando sistema está idle (sem atividade recente)
        e executa análise de fluxos + propõe regeneração.
        """
        while True:
            await asyncio.sleep(5)  # Check a cada 5s

            time_since_activity = datetime.now() - self.last_activity
            self.is_idle = time_since_activity > self.idle_threshold

            if self.is_idle and self.log_buffer:
                logger.info("🧠 SAR: Ociosidade detectada, analisando fluxos...")
                await self._regenerate_cycle()

    async def _regenerate_cycle(self) -> None:
        """Ciclo completo de regeneração durante ociosidade."""

        # 1. Agrupa logs em fluxos
        flows = self._group_logs_into_flows(self.log_buffer)

        # 2. Schizoanalisa cada fluxo
        for flow_name, entries in flows.items():
            flow_analysis = self.schizoanalyzer.analyze_flow_as_smooth_space(entries, flow_name)

            # 3. Detecta problemas e oportunidades
            proposals = self._generate_regenerative_proposals(flow_analysis)
            self.proposals.extend(proposals)

        # 4. Notifica usuário/sistema se crítico
        await self._notify_critical_findings()

        # 5. Limpa buffer (mas mantém histórico)
        self.log_buffer = []

    def _group_logs_into_flows(self, entries: List[LogEntry]) -> Dict[str, List[LogEntry]]:
        """Agrupa logs em fluxos coerentes."""
        flows: Dict[str, List[LogEntry]] = defaultdict(list)
        current_flow: Optional[str] = None
        last_timestamp: Optional[datetime] = None

        for entry in entries:
            entry_time = datetime.fromisoformat(entry.timestamp)

            # Detecta mudança de fluxo (timeout > 5s entre eventos)
            if current_flow is None or (
                last_timestamp and (entry_time - last_timestamp).total_seconds() > 5
            ):
                current_flow = f"flow_{entry.module}_{len(flows)}"

            flows[current_flow].append(entry)
            last_timestamp = entry_time

        return flows

    def _generate_regenerative_proposals(self, flow: FlowAnalysis) -> List[RegenerativeProposal]:
        """
        Gera propostas de regeneração baseado em schizoanalysis.

        Tipos de propostas:
        1. ERRO REATIVO: fix direto
        2. ANOMALIA DETECTADA: otimização
        3. LINHA DE FUGA: inovação possível
        4. OVERCODING EXCESSIVO: deterritorialização
        """
        proposals = []

        # 1. Erros detectados
        if flow.error_count > 0:
            error_types: Dict[str, int] = defaultdict(int)
            for entry in flow.entries:
                if entry.error_type:
                    error_types[entry.error_type] += 1

            for error_type, count in error_types.items():
                proposal = RegenerativeProposal(
                    id=hashlib.md5(f"{flow.flow_id}{error_type}".encode()).hexdigest()[:8],
                    severity=(ErrorSeverity.CRITICAL if count > 5 else ErrorSeverity.CAUTION),
                    module=flow.entries[0].module,
                    problem_description=f"Erro recorrente: {error_type} ({count}x em fluxo)",
                    proposed_solution=self._suggest_fix_for_error(error_type),
                    implementation_steps=self._get_fix_steps(error_type),
                    sandbox_test_available=True,
                    confidence=0.8 if count > 3 else 0.5,
                    expected_impact={"error_reduction": 0.7, "performance": 0.2},
                )
                proposals.append(proposal)

        # 2. Anomalias como intensidades
        for anomaly in flow.anomalies:
            if anomaly.get("type") == "LATENCY_SPIKE":
                module_name = anomaly["module"]
                proposal = RegenerativeProposal(
                    id=hashlib.md5(f"{flow.flow_id}{module_name}latency".encode()).hexdigest()[:8],
                    severity=ErrorSeverity.WARNING,
                    module=module_name,
                    problem_description=(
                        f"Spike de latência: {anomaly['duration_ms']:.2f}ms "
                        f"(z={anomaly.get('z_score', 0):.1f}σ)"
                    ),
                    proposed_solution=(
                        "Possível cache miss ou operação I/O. " "Sugerir memoização ou async."
                    ),
                    implementation_steps=[
                        f"1. Perfil com cProfile em {module_name}",
                        "2. Identifica função responsável",
                        "3. Aplica cache local se idempotente",
                        "4. Testa em sandbox",
                        "5. Deploy incremental",
                    ],
                    sandbox_test_available=True,
                    confidence=0.65,
                    expected_impact={"latency_p99": -0.3, "throughput": 0.1},
                )
                proposals.append(proposal)

        # 3. Linhas de fuga = oportunidades de inovação
        if any("LINE_OF_FLIGHT" in p for p in flow.patterns):
            proposal = RegenerativeProposal(
                id=hashlib.md5(f"{flow.flow_id}innovation".encode()).hexdigest()[:8],
                severity=ErrorSeverity.OPPORTUNITY,
                module=flow.entries[0].module if flow.entries else "unknown",
                problem_description=(
                    "Linha de fuga detectada: comportamento não-planejado bem-sucedido"
                ),
                proposed_solution=(
                    "Sistema auto-recuperou de erro. Analisar padrão para "
                    "aplicar proativamente. Possível nova estratégia."
                ),
                implementation_steps=[
                    "1. Documentar sequência de recuperação",
                    "2. Extrair padrão (rhizoma)",
                    "3. Generalizar para contextos similares",
                    "4. Feature flag: habilitar novo comportamento",
                    "5. Monitorar impacto",
                ],
                sandbox_test_available=True,
                confidence=0.72,
                expected_impact={"resilience": 0.5},
                philosophical_note=(
                    "Deleuze: 'Uma linha de fuga não é absolutamente destruir. "
                    "É criar.' Sistema encontrou escape criativo do overcoding."
                ),
            )
            proposals.append(proposal)

        # 4. Overcoding excessivo (regime striated > 30%)
        if len(flow.entries) > 0 and flow.error_count / len(flow.entries) > 0.3:
            proposal = RegenerativeProposal(
                id=hashlib.md5(f"{flow.flow_id}deterritorialize".encode()).hexdigest()[:8],
                severity=ErrorSeverity.WARNING,
                module=flow.entries[0].module,
                problem_description=(
                    f"Espaço overcoded: {flow.error_count}/{len(flow.entries)} erros. "
                    "Fluxo está territorializado demais (Édipo)."
                ),
                proposed_solution=(
                    "Deterritorializar: remover constraints desnecessários. "
                    "Permitir mais flexibilidade (smooth space)."
                ),
                implementation_steps=[
                    "1. Audit: quais validações são realmente necessárias?",
                    "2. Identificar over-zealous error handling",
                    "3. Substituir por graceful degradation",
                    "4. Expandir accepted input space",
                    "5. Monitor: trade-off safety vs flexibility",
                ],
                sandbox_test_available=False,
                confidence=0.6,
                expected_impact={"throughput": 0.4, "error_rate": 0.2},
                philosophical_note=(
                    "Guattari: 'O overcoding estatal pode ser dissolvido pelo "
                    "suave. Buscar o nômade dentro do sedentário.'"
                ),
            )
            proposals.append(proposal)

        return proposals

    def _suggest_fix_for_error(self, error_type: str) -> str:
        """Sugere fix baseado em tipo de erro."""
        fixes = {
            "TimeoutError": "Aumentar timeout ou async processing ou cache",
            "MemoryError": "Implementar streaming ou garbage collection",
            "ValueError": "Validação mais permissiva ou type coercion",
            "ConnectionError": "Retry logic com exponential backoff",
            "AttributeError": "Adicionar null checks ou default values",
        }
        return fixes.get(error_type, "Investigar raiz do erro em profundidade")

    def _get_fix_steps(self, error_type: str) -> List[str]:
        """Passos para implementar fix."""
        return [
            f"1. Cria branch feature: fix/{error_type}",
            "2. Identifica root cause nos logs",
            "3. Implementa fix minimal",
            "4. Adiciona teste (regressão)",
            "5. Sandbox test completo",
            "6. Code review",
            "7. Deploy com canary",
        ]

    async def _notify_critical_findings(self) -> None:
        """Notifica usuário/sistema de descobertas críticas."""
        critical = [p for p in self.proposals if p.severity == ErrorSeverity.CRITICAL]
        opportunities = [p for p in self.proposals if p.severity == ErrorSeverity.OPPORTUNITY]

        for proposal in critical:
            logger.critical(
                f"🚨 SAR CRITICAL: {proposal.problem_description}",
                extra={
                    "proposal_id": proposal.id,
                    "solution": proposal.proposed_solution,
                    "confidence": proposal.confidence,
                },
            )

        for proposal in opportunities:
            logger.info(
                f"💡 SAR OPPORTUNITY: {proposal.problem_description}",
                extra={
                    "philosophical": proposal.philosophical_note,
                    "impact": proposal.expected_impact,
                },
            )

    def add_log_entry(
        self, module: str, function: str, level: str, message: str, **kwargs: Any
    ) -> None:
        """Interface simplificada para adicionar logs."""
        entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            module=module,
            function=function,
            level=level,
            message=message,
            **kwargs,
        )
        self.log_buffer.append(entry)
        self.last_activity = datetime.now()
