"""
Symbolic Register - Espaço inconsciente compartilhado para comunicação entre módulos.

Implementa o registro simbólico lacaniano onde módulos trocam mensagens
através das ordens Real, Imaginário e Simbólico.

Author: Project conceived by Fabrício da Silva. Implementation followed an iterative AI-assisted
method: the author defined concepts and queried various AIs on construction, integrated code via
VS Code/Copilot, tested resulting errors, cross-verified validity with other models, and refined
prompts/corrections in a continuous cycle of human-led AI development.
from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code review
and debugging across various models including Gemini and Perplexity AI, under
theoretical coordination by the author.
Date: November 2025
License: MIT
"""

import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, cast

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SymbolicMessage:
    """Mensagem simbólica no registro compartilhado."""

    sender: str
    receiver: str
    symbolic_content: Dict[str, Any]  # Conteúdo simbólico (Real, Imaginário, Simbólico)
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: f"msg_{int(time.time() * 1000)}")
    priority: int = 1  # 1=baixo, 5=crítico
    nachtraglichkeit: bool = False  # Nachträglichkeit processing flag

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SymbolicRegister:
    """
    Shared Symbolic Register - Espaço inconsciente compartilhado.

    Implementa o registro simbólico central onde módulos trocam mensagens
    simbólicas através das ordens Real, Imaginário e Simbólico (Lacan).

    Funcionalidades críticas:
    - Troca de mensagens simbólicas entre módulos
    - Tradução Real→Imaginário→Simbólico
    - Nachträglichkeit processing (retroatividade)
    - Comunicação assíncrona com prioridades
    """

    def __init__(self, workspace, max_messages: int = 1000):
        self.workspace = workspace
        self.max_messages = max_messages

        # Registro de mensagens simbólicas
        self.symbolic_messages: List[SymbolicMessage] = []
        self.pending_messages: Dict[str, List[SymbolicMessage]] = {}  # receiver -> messages

        # Estado simbólico por módulo
        self.symbolic_states: Dict[str, Dict[str, Any]] = {}  # module -> symbolic_state

        # Contadores para debugging
        self.messages_processed = 0
        self.nachtraglichkeit_events = 0

        logger.info(f"SymbolicRegister initialized with max_messages={max_messages}")

    def send_symbolic_message(
        self,
        sender: str,
        receiver: str,
        symbolic_content: Dict[str, Any],
        priority: int = 1,
        nachtraglichkeit: bool = False,
    ) -> str:
        """
        Envia mensagem simbólica para um módulo.

        Args:
            sender: Módulo remetente
            receiver: Módulo destinatário
            symbolic_content: Conteúdo simbólico (Real/Imaginary/Symbolic)
            priority: Prioridade (1-5)
            nachtraglichkeit: Flag para processamento nachträglichkeit

        Returns:
            Message ID
        """
        message = SymbolicMessage(
            sender=sender,
            receiver=receiver,
            symbolic_content=symbolic_content,
            priority=priority,
            nachtraglichkeit=nachtraglichkeit,
        )

        # Adicionar ao registro histórico
        self.symbolic_messages.append(message)
        if len(self.symbolic_messages) > self.max_messages:
            self.symbolic_messages.pop(0)

        # Adicionar à fila do destinatário
        if receiver not in self.pending_messages:
            self.pending_messages[receiver] = []
        self.pending_messages[receiver].append(message)

        # Ordenar por prioridade (maior primeiro)
        self.pending_messages[receiver].sort(key=lambda m: m.priority, reverse=True)

        logger.debug(f"Symbolic message sent: {sender} -> {receiver} (priority={priority})")
        return message.message_id

    def receive_symbolic_messages(self, receiver: str) -> List[SymbolicMessage]:
        """
        Recebe mensagens simbólicas pendentes para um módulo.

        Args:
            receiver: Módulo destinatário

        Returns:
            Lista de mensagens pendentes (ordenadas por prioridade)
        """
        messages = self.pending_messages.get(receiver, [])
        self.pending_messages[receiver] = []  # Limpar fila

        if messages:
            logger.debug(f"Symbolic messages received: {receiver} got {len(messages)} messages")
            self.messages_processed += len(messages)

        return messages

    def translate_real_to_imaginary(self, real_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traduz conteúdo Real para Imaginário (Lacan).

        Real: Dados brutos, traumáticos, não simbolizáveis
        Imaginário: Representação especular, narcísica, dual

        Args:
            real_content: Conteúdo na ordem Real

        Returns:
            Conteúdo traduzido para Imaginário
        """
        # Implementação básica: projeção especular
        imaginary_content = {
            "order": "Imaginary",
            "specular_projection": {},
            "dual_relations": {},
            "narcissistic_capture": {},
        }

        # Projeção especular básica
        if "embeddings" in real_content:
            embeddings = np.array(real_content["embeddings"])
            # Projeção especular: reflexão sobre eixo principal
            specular = embeddings * -1  # Reflexão simples
            cast(Dict[str, Any], imaginary_content["specular_projection"])[
                "reflected_embeddings"
            ] = specular.tolist()

        # Relações dualísticas
        if "modules" in real_content:
            modules = real_content["modules"]
            dual_pairs = []
            for i in range(0, len(modules), 2):
                if i + 1 < len(modules):
                    dual_pairs.append([modules[i], modules[i + 1]])
            cast(Dict[str, Any], imaginary_content["dual_relations"])["module_pairs"] = dual_pairs

        return imaginary_content

    def translate_imaginary_to_symbolic(self, imaginary_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Traduz conteúdo Imaginário para Simbólico (Lacan).

        Imaginário: Dual, especular
        Simbólico: Ordem da linguagem, leis, estruturas

        Args:
            imaginary_content: Conteúdo na ordem Imaginária

        Returns:
            Conteúdo traduzido para Simbólico
        """
        symbolic_content = {
            "order": "Symbolic",
            "linguistic_structure": {},
            "law_and_order": {},
            "signifying_chain": {},
        }

        # Estrutura linguística
        if "specular_projection" in imaginary_content:
            # Cadeia significante: converter projeções em significantes
            projections = imaginary_content["specular_projection"]
            signifying_chain = []

            for key, value in projections.items():
                if isinstance(value, list) and len(value) > 0:
                    # Converter array em cadeia significante
                    chain = []
                    for i, val in enumerate(value[:10]):  # Limitar tamanho
                        chain.append(f"S{i}_{val:.3f}")
                    signifying_chain.append(f"{key}: {' -> '.join(chain)}")

            cast(Dict[str, Any], symbolic_content["signifying_chain"])["chains"] = signifying_chain

        # Leis e estruturas
        if "dual_relations" in imaginary_content:
            relations = imaginary_content["dual_relations"]
            laws = []

            if "module_pairs" in relations:
                for pair in relations["module_pairs"]:
                    laws.append(f"Law: {pair[0]} <-> {pair[1]} (dual binding)")

            cast(Dict[str, Any], symbolic_content["law_and_order"])["binding_laws"] = laws

        return symbolic_content

    def process_nachtraglichkeit(self, message: SymbolicMessage) -> SymbolicMessage:
        """
        Processa Nachträglichkeit (retroatividade lacaniana).

        Nachträglichkeit: Significado é atribuído retroativamente,
        eventos passados ganham novo significado à luz do presente.

        Args:
            message: Mensagem a processar

        Returns:
            Mensagem processada com nachträglichkeit
        """
        if not message.nachtraglichkeit:
            return message

        # Encontrar mensagens históricas relacionadas
        historical_messages = [
            m
            for m in self.symbolic_messages[-100:]  # Últimas 100 mensagens
            if m.sender == message.sender or m.receiver == message.receiver
        ]

        # Re-significar mensagens históricas à luz da nova
        for hist_msg in historical_messages[-5:]:  # Últimas 5 relacionadas
            # Adicionar contexto nachträglichkeit
            if "nachtraglichkeit_context" not in hist_msg.symbolic_content:
                hist_msg.symbolic_content["nachtraglichkeit_context"] = []

            hist_msg.symbolic_content["nachtraglichkeit_context"].append(
                {
                    "retroactive_meaning": f"Re-signified by message {message.message_id}",
                    "new_context": message.symbolic_content.get("order", "unknown"),
                    "timestamp": message.timestamp,
                }
            )

        self.nachtraglichkeit_events += 1
        logger.debug(f"Nachträglichkeit processed for message {message.message_id}")

        return message

    def get_symbolic_state(self, module_name: str) -> Dict[str, Any]:
        """
        Obtém estado simbólico atual de um módulo.

        Args:
            module_name: Nome do módulo

        Returns:
            Estado simbólico (Real/Imaginary/Symbolic)
        """
        if module_name not in self.symbolic_states:
            # Estado inicial vazio
            self.symbolic_states[module_name] = {
                "Real": {},
                "Imaginary": {},
                "Symbolic": {},
                "last_updated": time.time(),
            }

        return self.symbolic_states[module_name]

    def update_symbolic_state(self, module_name: str, new_content: Dict[str, Any]) -> None:
        """
        Atualiza estado simbólico de um módulo.

        Args:
            module_name: Nome do módulo
            new_content: Novo conteúdo simbólico
        """
        if module_name not in self.symbolic_states:
            self.symbolic_states[module_name] = {
                "Real": {},
                "Imaginary": {},
                "Symbolic": {},
                "last_updated": time.time(),
            }

        # Atualizar ordens simbólicas
        for order in ["Real", "Imaginary", "Symbolic"]:
            if order in new_content:
                self.symbolic_states[module_name][order].update(new_content[order])

        self.symbolic_states[module_name]["last_updated"] = time.time()

        logger.debug(f"Symbolic state updated for {module_name}")

    def get_metrics(self) -> Dict[str, Any]:
        """
        Captura métricas do SymbolicRegister para monitoramento.

        Conforme especificado em Task 2.4.2, captura:
        - message_count_per_cycle: mensagens enviadas por ciclo
        - symbol_diversity: diversidade simbólica (entropia)
        - narrative_coherence: coerência narrativa
        - message_latency_ms: latência de mensagens

        Returns:
            Dict com métricas do registro simbólico
        """
        # Calcular message_count_per_cycle (média de mensagens por ciclo)
        # Estimativa baseada em mensagens recentes (últimas 100)
        recent_messages = self.symbolic_messages[-100:] if self.symbolic_messages else []
        message_count_per_cycle = (
            len(recent_messages) / max(1, len(set(msg.timestamp // 1.0 for msg in recent_messages)))
            if recent_messages
            else 0.0
        )

        # Calcular symbol_diversity (entropia de tipos de mensagens)
        symbol_diversity = 0.0
        if self.symbolic_messages:
            # Contar diferentes tipos de ordens simbólicas
            order_counts: Dict[str, int] = {}
            for msg in self.symbolic_messages[-100:]:
                order = msg.symbolic_content.get("order", "unknown")
                order_counts[order] = order_counts.get(order, 0) + 1

            # Calcular entropia de Shannon (otimizado)
            total = sum(order_counts.values())
            if total > 0:
                import math

                for count in order_counts.values():
                    p = count / total
                    if p > 0:
                        symbol_diversity -= p * math.log2(p)

        # Calcular narrative_coherence (coerência entre mensagens consecutivas)
        narrative_coherence = 0.0
        if len(self.symbolic_messages) >= 2:
            # Mede coerência como proporção de mensagens que mantêm contexto
            coherent_count = 0
            for i in range(1, min(100, len(self.symbolic_messages))):
                curr_msg = self.symbolic_messages[-i]
                prev_msg = self.symbolic_messages[-i - 1]

                # Coerente se sender/receiver mantém relação
                if (
                    curr_msg.sender == prev_msg.sender
                    or curr_msg.sender == prev_msg.receiver
                    or curr_msg.receiver == prev_msg.sender
                ):
                    coherent_count += 1

            narrative_coherence = float(coherent_count / min(99, len(self.symbolic_messages) - 1))

        # Calcular message_latency_ms (latência média de processamento)
        message_latency_ms = 0.0
        if recent_messages and self.messages_processed > 0:
            # Estima latência baseado no tempo entre mensagens
            timestamps = [msg.timestamp for msg in recent_messages]
            if len(timestamps) >= 2:
                intervals = [timestamps[i] - timestamps[i - 1] for i in range(1, len(timestamps))]
                message_latency_ms = float(np.mean(intervals) * 1000)  # Converter para ms

        return {
            "message_count_per_cycle": float(message_count_per_cycle),
            "symbol_diversity": float(symbol_diversity),
            "narrative_coherence": float(narrative_coherence),
            "message_latency_ms": float(message_latency_ms),
            "timestamp": time.time(),
        }

    def get_symbolic_communication_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da comunicação simbólica."""
        total_messages = len(self.symbolic_messages)
        pending_count = sum(len(msgs) for msgs in self.pending_messages.values())
        active_modules = len(self.symbolic_states)

        return {
            "total_messages": total_messages,
            "pending_messages": pending_count,
            "active_symbolic_modules": active_modules,
            "messages_processed": self.messages_processed,
            "nachtraglichkeit_events": self.nachtraglichkeit_events,
            "symbolic_orders": ["Real", "Imaginary", "Symbolic"],
        }

    def __repr__(self) -> str:
        stats = self.get_symbolic_communication_stats()
        return (
            f"SymbolicRegister(messages={stats['total_messages']}, "
            f"pending={stats['pending_messages']}, "
            f"modules={stats['active_symbolic_modules']})"
        )
