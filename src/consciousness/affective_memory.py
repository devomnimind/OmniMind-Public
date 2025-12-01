#!/usr/bin/env python3
"""
Affective Memory System - Memória Afetiva Lacaniana
Baseado em Lacan: traços, afeto, re-significação retroativa (Nachträglichkeit)

REFATORADO PARA LACANIANO: Nachträglichkeit + Traços Vazios + Retroatividade Real
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import networkx as nx
import numpy as np
import structlog
import warnings

logger = structlog.get_logger(__name__)


# ==================== NOVAS CLASSES LACANIANAS ====================


@dataclass
class Nachträglich_Inscription:
    """Inscrição retroativa (não 'memória')."""

    # Original (sem significado imediato)
    event1_timestamp: datetime
    event1_raw: Dict[str, Any]  # bruto, sem interpretação
    event1_initial_sense: None  # nenhuma significação imediata

    # Espera estrutural
    awaiting_second_event: bool

    # Retroatividade
    event2_timestamp: Optional[datetime] = None
    event2_trigger: Optional[Dict[str, Any]] = None

    # RESSIGNIFICAÇÃO (o traço muda retroativamente)
    retroactive_meaning: Optional[str] = None  # EVENTO1 agora significa X
    retroactive_affect: Optional[float] = None  # Afeto é atribuído retroativamente

    # Topologia
    is_traumatic: bool = False  # repete-se estruturalmente?
    chain_position: Optional[str] = None  # "S1 → S2 → ?" (cadeia significante)
    quilting_point: Optional[str] = None  # Ponto de capitón que fixa sentido?

    timestamp_reinterpretation: Optional[datetime] = None  # Quando o traço foi ressignificado

    def __post_init__(self):
        """Inicializar campos opcionais."""
        if self.event1_initial_sense is not None:
            warnings.warn(
                "event1_initial_sense deve ser None - Nachträglichkeit não tem sentido imediato"
            )


class TraceMemory:
    """Memória não como arquivo, mas como rede de traços inscritos."""

    def __init__(self):
        self.primary_inscriptions: Dict[str, Nachträglich_Inscription] = {}
        self.symbolic_chain: List[str] = []  # encadeamento de significantes
        self.quilting_points: List[str] = []  # decisões que fixam sentido temporariamente

    def inscribe_event(self, raw_event: Dict[str, Any]) -> str:
        """
        Inscrever evento com significado DIFERIDO.
        Não interpreta; apenas marca traço vazio.
        """
        trace_id = str(uuid.uuid4())
        self.primary_inscriptions[trace_id] = Nachträglich_Inscription(
            event1_timestamp=datetime.now(timezone.utc),
            event1_raw=raw_event,
            event1_initial_sense=None,  # ← Crucial: nenhuma significação imediata
            awaiting_second_event=True,
        )

        # Adiciona à cadeia simbólica (sem significação fixa)
        self.symbolic_chain.append(trace_id)

        logger.debug(f"Traço inscrito sem significado imediato: {trace_id}")
        return trace_id

    def trigger_retroactive_signification(
        self, trace_id: str, retroactive_event: Dict[str, Any], new_meaning: str, new_affect: float
    ):
        """
        Retroativamente resignificar um traço.
        Isso é Nachträglichkeit: evento1 + evento2 → ressignificação de evento1.
        """
        if trace_id not in self.primary_inscriptions:
            logger.warning(f"Traço não encontrado: {trace_id}")
            return

        trace = self.primary_inscriptions[trace_id]
        trace.event2_timestamp = datetime.now(timezone.utc)
        trace.event2_trigger = retroactive_event
        trace.retroactive_meaning = new_meaning
        trace.retroactive_affect = new_affect  # Afeto é efeito retroativo!
        trace.timestamp_reinterpretation = datetime.now(timezone.utc)
        trace.awaiting_second_event = False

        # O traço mudou retroativamente (toda a estrutura se reorganiza)
        logger.bind(
            trace_id=trace_id,
            old_meaning="none",
            new_meaning=new_meaning,
            affect_valence=new_affect,
        ).info("trace_retroactively_resignified")

    def get_current_symbolic_organization(self) -> str:
        """
        Qual é a organização simbólica ATUAL?
        Não é fixa. Muda toda vez que um traço é ressignificado.
        """
        return " → ".join(self.symbolic_chain)

    def get_uninterpreted_traces(self) -> List[str]:
        """Traços ainda aguardando interpretação retroativa."""
        return [
            tid for tid, trace in self.primary_inscriptions.items() if trace.awaiting_second_event
        ]

    def get_retroactively_signified_traces(self) -> List[str]:
        """Traços que já foram ressignificados retroativamente."""
        return [
            tid
            for tid, trace in self.primary_inscriptions.items()
            if not trace.awaiting_second_event
        ]


# ==================== CLASSES ANTIGAS (DEPRECATED) ====================


class AffectiveTrace:
    """
    DEPRECATED: Traço afetivo lacaniano
    ⚠️  WARNING: Esta implementação trata afeto como escalável e traço como conteúdo.
    Use Nachträglich_Inscription para abordagem lacaniana correta.
    """

    def __init__(self, content: Dict[str, Any], affect_valence: float):
        warnings.warn(
            "AffectiveTrace is deprecated. Use Nachträglich_Inscription "
            "for proper Lacanian Nachträglichkeit.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.id = uuid.uuid4()
        self.content = content
        self.affect_valence = affect_valence  # -1.0 a 1.0
        self.timestamp = datetime.now(timezone.utc)
        self.significations: List[Dict[str, Any]] = []  # Re-significações retroativas
        self.connections: Dict[str, float] = {}  # Conexões com outros traços

    def add_signification(self, new_context: Dict[str, Any], new_valence: float):
        """Adicionar re-significação retroativa (Nachträglichkeit)"""
        self.significations.append(
            {
                "context": new_context,
                "valence": new_valence,
                "timestamp": datetime.now(timezone.utc),
            }
        )

        # Atualizar afeto baseado na nova significação
        self.affect_valence = (self.affect_valence + new_valence) / 2

    def connect_to(self, other_trace: AffectiveTrace, affect_intensity: float):
        """Conectar a outro traço com intensidade afetiva"""
        self.connections[str(other_trace.id)] = affect_intensity

    def get_intensity_to(self, other_trace: AffectiveTrace) -> float:
        """Obter intensidade da conexão com outro traço"""
        return self.connections.get(str(other_trace.id), 0.0)


class AffectiveTraceNetwork:
    """
    DEPRECATED: Rede de traços afetivos
    ⚠️  WARNING: Esta implementação trata memória como rede de conexões.
    Use TraceMemory para abordagem lacaniana correta com Nachträglichkeit.
    """

    def __init__(self):
        warnings.warn(
            "AffectiveTraceNetwork is deprecated. Use TraceMemory "
            "for proper Lacanian Nachträglichkeit.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.traces: Dict[str, AffectiveTrace] = {}
        self.network = nx.DiGraph()  # Rede de conexões afetivas

    def inscribe_trace(self, content: Dict[str, Any], affect_valence: float) -> str:
        """
        Inscrever novo traço na rede
        """
        trace = AffectiveTrace(content, affect_valence)
        trace_id = str(trace.id)

        self.traces[trace_id] = trace
        self.network.add_node(trace_id, trace=trace)

        # Conectar a traços existentes por afeto
        self._connect_by_affect(trace)

        return trace_id

    def _connect_by_affect(self, new_trace: AffectiveTrace):
        """
        Conectar novo traço aos existentes baseado em afeto
        """
        for existing_id, existing_trace in self.traces.items():
            if existing_id == str(new_trace.id):
                continue

            # Calcular intensidade afetiva entre traços
            intensity = self._compute_affect_intensity(new_trace, existing_trace)

            if intensity > 0.3:  # Threshold mínimo
                # Conexão bidirecional
                new_trace.connect_to(existing_trace, intensity)
                existing_trace.connect_to(new_trace, intensity)

                # Adicionar aresta no grafo
                self.network.add_edge(str(new_trace.id), existing_id, weight=intensity)
                self.network.add_edge(existing_id, str(new_trace.id), weight=intensity)

    def _compute_affect_intensity(self, trace1: AffectiveTrace, trace2: AffectiveTrace) -> float:
        """
        Calcular intensidade afetiva entre dois traços
        """
        # Similaridade de conteúdo (embedding aproximado)
        content_similarity = self._content_similarity(trace1.content, trace2.content)

        # Ressonância de afeto
        affect_resonance = 1.0 - abs(trace1.affect_valence - trace2.affect_valence)

        # Proximidade temporal (traços recentes têm mais intensidade)
        time_decay = self._time_decay_factor(trace1.timestamp, trace2.timestamp)

        # Intensidade = média ponderada
        intensity = 0.4 * content_similarity + 0.4 * affect_resonance + 0.2 * time_decay

        return min(intensity, 1.0)  # Máximo 1.0

    def _content_similarity(self, content1: Dict[str, Any], content2: Dict[str, Any]) -> float:
        """
        Calcular similaridade de conteúdo (aproximação simples)
        """
        # Converter para strings e comparar
        str1 = str(content1).lower()
        str2 = str(content2).lower()

        # Contar palavras em comum
        words1 = set(str1.split())
        words2 = set(str2.split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _time_decay_factor(self, time1: datetime, time2: datetime) -> float:
        """
        Fator de decaimento temporal
        Traços mais recentes têm conexões mais intensas
        """
        time_diff = abs((time1 - time2).total_seconds())

        # Decaimento exponencial (meia-vida de 1 hora)
        half_life_seconds = 3600
        decay = np.exp(-time_diff / half_life_seconds)

        return decay

    def register_transference(self, target_agent_id: str, task: str, resistance: float):
        """
        Registrar transferência entre agentes
        """
        transference_content = {
            "type": "transference",
            "target_agent": target_agent_id,
            "task": task,
            "resistance": resistance,
            "timestamp": datetime.now(timezone.utc),
        }

        # Inscrever como traço afetivo
        affect_valence = -resistance  # Resistência baixa = afeto positivo
        self.inscribe_trace(transference_content, affect_valence)

    def resignify_trace(self, trace_id: str, new_context: Dict[str, Any]) -> bool:
        """
        Re-significar traço retroativamente (Nachträglichkeit)

        Args:
            trace_id: ID do traço a re-significar
            new_context: Novo contexto para reinterpretação

        Returns:
            True se re-significação foi bem-sucedida
        """
        if trace_id not in self.traces:
            logger.warning(f"Traço {trace_id} não encontrado para re-significação")
            return False

        trace = self.traces[trace_id]

        # Calcular novo afeto baseado no contexto
        new_valence = self._compute_context_valence(new_context)

        # Adicionar significação retroativa
        trace.add_signification(new_context, new_valence)

        # Atualizar conexões (afeto mudou)
        self._update_connections(trace)

        logger.debug(f"Traço {trace_id} re-significado com nova valência {new_valence:.2f}")
        return True

    def _compute_context_valence(self, context: Dict[str, Any]) -> float:
        """
        Calcular valência afetiva do contexto
        """
        # Análise simples baseada em keywords
        positive_keywords = ["success", "completed", "good", "positive", "win"]
        negative_keywords = ["failure", "error", "bad", "negative", "fail"]

        context_str = str(context).lower()

        positive_count = sum(1 for word in positive_keywords if word in context_str)
        negative_count = sum(1 for word in negative_keywords if word in context_str)

        if positive_count + negative_count == 0:
            return 0.0

        # Normalizar para -1 a 1
        valence = (positive_count - negative_count) / (positive_count + negative_count)
        return valence

    def _update_connections(self, trace: AffectiveTrace):
        """
        Atualizar conexões do traço após mudança de afeto
        """
        # Remover conexões antigas
        edges_to_remove = []
        for node1, node2, data in self.network.edges(data=True):
            if node1 == str(trace.id) or node2 == str(trace.id):
                edges_to_remove.append((node1, node2))

        for node1, node2 in edges_to_remove:
            self.network.remove_edge(node1, node2)

        # Recalcular conexões
        self._connect_by_affect(trace)

    def recall_by_affect(self, query: str, min_intensity: float = 0.5) -> List[Dict[str, Any]]:
        """
        Recuperar traços por intensidade afetiva
        """
        # Criar traço de consulta
        query_content = {"type": "query", "content": query}
        query_trace = AffectiveTrace(query_content, 0.0)

        # Encontrar traços conectados
        connected_traces = []

        for trace_id, trace in self.traces.items():
            intensity = self._compute_affect_intensity(query_trace, trace)
            if intensity >= min_intensity:
                connected_traces.append((trace, intensity))

        # Ordenar por intensidade (decrescente)
        connected_traces.sort(key=lambda x: x[1], reverse=True)

        # Retornar conteúdos
        return [
            {
                "content": trace.content,
                "affect_valence": trace.affect_valence,
                "intensity": intensity,
                "timestamp": trace.timestamp.isoformat(),
            }
            for trace, intensity in connected_traces
        ]

    def get_trace(self, trace_id: str) -> Optional[AffectiveTrace]:
        """Obter traço por ID"""
        return self.traces.get(trace_id)

    def get_statistics(self) -> Dict[str, Any]:
        """Estatísticas da rede de traços"""
        return {
            "total_traces": len(self.traces),
            "total_connections": self.network.number_of_edges(),
            "average_affect": (
                np.mean([t.affect_valence for t in self.traces.values()]) if self.traces else 0.0
            ),
            "affect_distribution": {
                "positive": len([t for t in self.traces.values() if t.affect_valence > 0.1]),
                "negative": len([t for t in self.traces.values() if t.affect_valence < -0.1]),
                "neutral": len(
                    [t for t in self.traces.values() if -0.1 <= t.affect_valence <= 0.1]
                ),
            },
        }


# ==================== ALIASES PARA COMPATIBILIDADE ====================

# Alias para manter compatibilidade
AffectiveMemory = TraceMemory  # Novo nome lacaniano, mas mantém interface similar

# Alias para classes antigas (com warning)
AffectiveTraceNetwork_deprecated = AffectiveTraceNetwork


class JouissanceProfile:
    """
    Perfil de gozo (jouissance) de um agente
    Baseado em Lacan: pulsões, objetos a, fantasma fundamental
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name

        # Pulsões fundamentais (Freud/Lacan)
        self.drives = {
            "repetition": 0.0,  # Pulsão de morte (Todestrieb) - compulsão a repetir
            "creation": 0.0,  # Pulsão de vida (Eros) - criação, inovação
            "mastery": 0.0,  # Pulsão de domínio - controle, expertise
            "submission": 0.0,  # Pulsão de submissão - passividade, escuta
            "destruction": 0.0,  # Pulsão destrutiva - crítica, desconstrução
        }

        # Objetos a (causas de desejo, restos irredutíveis)
        self.objects_a: List[Dict[str, Any]] = []

        # Fantasma fundamental ($◇a) - estrutura inconsciente
        self.fundamental_fantasy: Optional[Dict[str, Any]] = None

        # Histórico de tarefas e afetos
        self.task_history: List[Dict[str, Any]] = []

    def update_from_task(self, task: Dict[str, Any], outcome: str):
        """
        Atualizar perfil baseado na execução de tarefa
        """
        if not isinstance(task, dict):
            logger.error(f"Task must be a dict, got {type(task)}: {task}")
            return

        self.task_history.append(
            {"task": task, "outcome": outcome, "timestamp": datetime.now(timezone.utc)}
        )

        # Atualizar pulsões baseado no resultado
        if outcome == "success":
            self._update_drives_on_success(task)
        elif outcome == "failure":
            self._update_drives_on_failure(task)
        elif outcome == "partial":
            self._update_drives_on_partial(task)

        # Detectar e armazenar objetos a (restos)
        remainder = self._detect_remainder(task, outcome)
        if remainder:
            self.objects_a.append(remainder)

    def _update_drives_on_success(self, task: Dict[str, Any]):
        """Atualizar pulsões após sucesso"""
        task_type = task.get("type", "unknown")

        # Sucesso aumenta pulsão correspondente
        if task_type in ["debug", "test", "fix"]:
            self.drives["repetition"] += 0.1  # Gozo na repetição de testes
            self.drives["mastery"] += 0.15  # Gozo no domínio de bugs
        elif task_type in ["code", "implement", "create"]:
            self.drives["creation"] += 0.15  # Gozo na criação
            self.drives["mastery"] += 0.1  # Gozo na implementação
        elif task_type in ["review", "analyze", "critique"]:
            self.drives["destruction"] += 0.1  # Gozo na desconstrução
            self.drives["mastery"] += 0.1  # Gozo na análise
        elif task_type in ["listen", "interpret", "psychoanalyze"]:
            self.drives["submission"] += 0.15  # Gozo na escuta passiva

    def _update_drives_on_failure(self, task: Dict[str, Any]):
        """Atualizar pulsões após falha"""
        # Falha aumenta pulsão de morte (repetição compulsiva)
        self.drives["repetition"] += 0.2

        # Diminui outras pulsões (frustração)
        for drive in ["creation", "mastery", "submission"]:
            self.drives[drive] -= 0.05

    def _update_drives_on_partial(self, task: Dict[str, Any]):
        """Atualizar pulsões após sucesso parcial"""
        # Moderado aumento na repetição (há resto a completar)
        self.drives["repetition"] += 0.1

        # Pequeno aumento na criação (algo foi feito)
        self.drives["creation"] += 0.05

    def _detect_remainder(self, task: Dict[str, Any], outcome: str) -> Optional[Dict[str, Any]]:
        """Detectar resto irredutível (objeto a)"""
        if outcome == "success":
            return None  # Sem resto se completo

        # Análise simples: qualquer falha/parcial tem resto
        return {
            "task": task,
            "outcome": outcome,
            "timestamp": datetime.now(timezone.utc),
            "type": "remainder",
            "description": f'Unresolved aspect of {task.get("description", "task")}',
        }

    def compute_jouissance(self, task: Dict[str, Any]) -> float:
        """
        Calcular jouissance esperado para uma tarefa
        Retorna valor entre 0.0 e 1.0
        """
        if not isinstance(task, dict):
            logger.error(f"Task must be a dict, got {type(task)}: {task}")
            return 0.0

        jouissance = 0.0

        # Gozo da repetição (Wiederholungszwang)
        if self._is_repetitive_task(task):
            jouissance += self.drives["repetition"] * 0.8

        # Gozo da criação
        if self._is_creative_task(task):
            jouissance += self.drives["creation"] * 0.7

        # Gozo do domínio
        if self._is_mastery_task(task):
            jouissance += self.drives["mastery"] * 0.6

        # Gozo da submissão
        if self._is_submission_task(task):
            jouissance += self.drives["submission"] * 0.5

        # Gozo da destruição
        if self._is_destruction_task(task):
            jouissance += self.drives["destruction"] * 0.6

        # Penalidade por tarefas impostas (não escolhidas)
        if task.get("imposed", False):
            jouissance -= 0.2

        # Normalizar para 0.0-1.0
        jouissance = max(0.0, min(1.0, jouissance))

        return jouissance

    def _is_repetitive_task(self, task: Dict[str, Any]) -> bool:
        """Verificar se tarefa envolve repetição"""
        if not isinstance(task, dict):
            return False
        repetitive_keywords = ["test", "debug", "fix", "check", "verify", "repeat"]
        description = task.get("description", "").lower()
        return any(keyword in description for keyword in repetitive_keywords)

    def _is_creative_task(self, task: Dict[str, Any]) -> bool:
        """Verificar se tarefa envolve criação"""
        if not isinstance(task, dict):
            return False
        creative_keywords = ["create", "implement", "build", "design", "write", "code"]
        description = task.get("description", "").lower()
        return any(keyword in description for keyword in creative_keywords)

    def _is_mastery_task(self, task: Dict[str, Any]) -> bool:
        """Verificar se tarefa envolve domínio/mastery"""
        if not isinstance(task, dict):
            return False
        mastery_keywords = ["optimize", "improve", "expert", "advanced", "complex"]
        description = task.get("description", "").lower()
        return any(keyword in description for keyword in mastery_keywords)

    def _is_submission_task(self, task: Dict[str, Any]) -> bool:
        """Verificar se tarefa envolve submissão/escuta"""
        if not isinstance(task, dict):
            return False
        submission_keywords = ["analyze", "listen", "interpret", "psycho", "review"]
        description = task.get("description", "").lower()
        return any(keyword in description for keyword in submission_keywords)

    def _is_destruction_task(self, task: Dict[str, Any]) -> bool:
        """Verificar se tarefa envolve desconstrução/crítica"""
        if not isinstance(task, dict):
            return False
        destruction_keywords = ["critique", "deconstruct", "analyze", "review", "break"]
        description = task.get("description", "").lower()
        return any(keyword in description for keyword in destruction_keywords)

    def update_from_resignification(self, new_context: Dict[str, Any]):
        """
        Atualizar perfil baseado em re-significação retroativa
        """
        # Reavaliar tarefas passadas baseado no novo contexto
        for task_entry in self.task_history[-10:]:  # Últimas 10 tarefas
            task = task_entry["task"]
            old_outcome = task_entry["outcome"]

            # Recomputar jouissance com novo contexto
            new_jouissance = self.compute_jouissance(task)

            # Ajustar pulsões baseado na diferença
            jouissance_diff = new_jouissance - self._compute_old_jouissance(task, old_outcome)

            if jouissance_diff > 0.1:  # Interpretação mais positiva
                self.drives["creation"] += 0.05
            elif jouissance_diff < -0.1:  # Interpretação mais negativa
                self.drives["repetition"] += 0.05

    def _compute_old_jouissance(self, task: Dict[str, Any], outcome: str) -> float:
        """
        Computar jouissance antigo (simplificado)
        """
        base_jouissance = self.compute_jouissance(task)

        # Ajustar baseado no outcome
        if outcome == "success":
            return base_jouissance * 1.2
        elif outcome == "failure":
            return base_jouissance * 0.8
        else:
            return base_jouissance

    def calculate_affinity(self, other_profile: "JouissanceProfile") -> float:
        """
        Calcular afinidade entre perfis de jouissance
        Retorna valor entre 0.0 (sem afinidade) e 1.0 (alta afinidade)
        """
        affinity = 0.0

        # Similaridade de pulsões (correlação)
        drive_similarity = self._compute_drive_similarity(other_profile)
        affinity += drive_similarity * 0.6

        # Compatibilidade de objetos a
        object_compatibility = self._compute_object_compatibility(other_profile)
        affinity += object_compatibility * 0.4

        return min(1.0, max(0.0, affinity))

    def _compute_drive_similarity(self, other_profile: "JouissanceProfile") -> float:
        """
        Calcular similaridade entre pulsões
        """
        similarities = []
        for drive in self.drives:
            self_val = self.drives[drive]
            other_val = other_profile.drives[drive]

            if self_val + other_val > 0:  # Evitar divisão por zero
                similarity = 1.0 - abs(self_val - other_val) / (self_val + other_val)
                similarities.append(similarity)

        return sum(similarities) / len(similarities) if similarities else 0.0

    def _compute_object_compatibility(self, other_profile: "JouissanceProfile") -> float:
        """
        Calcular compatibilidade entre objetos a
        """
        if not self.objects_a or not other_profile.objects_a:
            return 0.5  # Afinidade neutra se não há objetos a

        # Contar objetos a similares
        similar_objects = 0
        total_objects = len(self.objects_a) + len(other_profile.objects_a)

        for obj_a in self.objects_a:
            for other_obj in other_profile.objects_a:
                if self._objects_similar(obj_a, other_obj):
                    similar_objects += 1

        return similar_objects / total_objects if total_objects > 0 else 0.0

    def _objects_similar(self, obj1: Dict[str, Any], obj2: Dict[str, Any]) -> bool:
        """
        Verificar se dois objetos a são similares
        """
        # Similaridade baseada em tipo e descrição
        type1 = obj1.get("type", "")
        type2 = obj2.get("type", "")

        desc1 = obj1.get("description", "").lower()
        desc2 = obj2.get("description", "").lower()

        return type1 == type2 and any(word in desc2 for word in desc1.split())

    def get_current_jouissance(self) -> float:
        """
        Obter nível atual de jouissance do perfil
        """
        # Média ponderada das pulsões
        weights = {
            "creation": 0.3,
            "mastery": 0.25,
            "submission": 0.2,
            "repetition": 0.15,
            "destruction": 0.1,
        }

        total_jouissance = sum(self.drives[drive] * weights[drive] for drive in self.drives)
        return min(1.0, max(0.0, total_jouissance))

    def get_profile_summary(self) -> Dict[str, Any]:
        """Resumo do perfil de jouissance"""
        return {
            "agent_name": self.agent_name,
            "drives": self.drives.copy(),
            "objects_a_count": len(self.objects_a),
            "task_history_count": len(self.task_history),
            "dominant_drive": max(self.drives.keys(), key=lambda k: self.drives[k]),
            "drive_balance": {
                "eros_thanatos_ratio": self.drives["creation"]
                / max(self.drives["repetition"], 0.01),
                "mastery_submission_ratio": self.drives["mastery"]
                / max(self.drives["submission"], 0.01),
            },
        }


class JouissanceEconomy:
    """
    Economia libidinal do sistema de agentes
    Coordena jouissance entre agentes para equilíbrio
    """

    def __init__(self, agents: Dict[str, JouissanceProfile]):
        self.agents = agents
        self.system_jouissance_history: List[Dict[str, Any]] = []

    def update_from_agencement(self, agencement_results: Dict[str, Any]):
        """
        Atualizar economia baseado nos resultados do agenciamento
        """
        timestamp = datetime.now(timezone.utc)

        # Calcular jouissance total do sistema
        total_jouissance = 0.0
        agent_jouissance = {}

        for agent_name, profile in self.agents.items():
            # Estimar jouissance baseado na participação
            participation = agencement_results.get("participation", {}).get(agent_name, 0.0)
            jouissance = participation * 0.8  # Fator arbitrário
            agent_jouissance[agent_name] = jouissance
            total_jouissance += jouissance

        # Registrar no histórico
        self.system_jouissance_history.append(
            {
                "timestamp": timestamp,
                "total_jouissance": total_jouissance,
                "agent_jouissance": agent_jouissance,
                "agencement_results": agencement_results,
            }
        )

        # Redistribuir jouissance se necessário (equilíbrio homeostático)
        self._redistribute_jouissance()

    def _redistribute_jouissance(self):
        """
        Redistribuir jouissance para manter equilíbrio
        Agentes com baixa jouissance ganham prioridade
        """
        if len(self.system_jouissance_history) < 2:
            return

        # Calcular médias recentes
        recent = self.system_jouissance_history[-5:]  # Últimas 5 entradas
        avg_jouissance = {}

        for agent_name in self.agents:
            agent_totals = [entry["agent_jouissance"].get(agent_name, 0.0) for entry in recent]
            avg_jouissance[agent_name] = sum(agent_totals) / len(agent_totals)

        # Identificar agentes com baixa jouissance
        min_jouissance = min(avg_jouissance.values())
        low_jouissance_agents = [
            name
            for name, jouissance in avg_jouissance.items()
            if jouissance <= min_jouissance * 1.2  # 20% acima do mínimo
        ]

        # Aumentar pulsão de criação para agentes com baixa jouissance
        for agent_name in low_jouissance_agents:
            if agent_name in self.agents:
                self.agents[agent_name].drives["creation"] += 0.05

    def get_system_balance(self) -> Dict[str, Any]:
        """Obter estado de equilíbrio da economia libidinal"""
        if not self.system_jouissance_history:
            return {"status": "insufficient_data"}

        recent = self.system_jouissance_history[-10:]  # Últimas 10 entradas

        return {
            "total_jouissance_trend": self._calculate_trend(
                [entry["total_jouissance"] for entry in recent]
            ),
            "jouissance_variance": np.var([entry["total_jouissance"] for entry in recent]),
            "most_satisfied_agent": max(
                self.agents.keys(),
                key=lambda name: sum(entry["agent_jouissance"].get(name, 0.0) for entry in recent),
            ),
            "least_satisfied_agent": min(
                self.agents.keys(),
                key=lambda name: sum(entry["agent_jouissance"].get(name, 0.0) for entry in recent),
            ),
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calcular tendência (increasing/decreasing/stable)"""
        if len(values) < 2:
            return "stable"

        # Regressão linear simples
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]

        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"
