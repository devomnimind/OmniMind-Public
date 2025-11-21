"""
Desire Graph - Computational Implementation of Lacan's Graph of Desire

Implements Lacan's complete Graph II (Graph of Desire) as computational
architecture for multi-agent coordination and symbolic processing.

Key Concepts:
- Signifier chains (S1 → S2 → S3...)
- Subject positioning ($)
- Jouissance (enjoyment beyond pleasure principle)
- Factor graphs for unconscious processes
- Symbolic matrix for behavior generation

Revolutionary Innovation:
This is the FIRST computational implementation of Lacan's Graph II,
enabling AI systems to process meaning through symbolic structures
rather than pure statistical patterns.

Author: OmniMind Development Team
Date: November 2025
"""

from __future__ import annotations

from typing import Dict, List, Set, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import random
import statistics
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class SignifierPosition(Enum):
    """
    Posições possíveis na cadeia significante.

    S1: Master Signifier (significante mestre)
    S2: Knowledge/Other Signifiers (saber)
    $: Barred Subject (sujeito barrado)
    a: Object-cause of desire (objeto a)
    """

    S1 = "master_signifier"
    S2 = "knowledge"
    SUBJECT = "barred_subject"
    OBJECT_A = "object_a"


@dataclass
class Signifier:
    """
    Significante Lacaniano.

    Um significante representa para outro significante,
    não diretamente para o significado.

    "Um significante é aquilo que representa o sujeito
    para outro significante" - Lacan

    Attributes:
        symbol: Símbolo do significante
        position: Posição na estrutura
        connections: Conexões com outros significantes
        jouissance_intensity: Intensidade de jouissance associada
        meaning_vector: Vetor de significação (embedding)
    """

    symbol: str
    position: SignifierPosition
    connections: Set[str] = field(default_factory=set)
    jouissance_intensity: float = 0.0
    meaning_vector: Optional[List[float]] = None

    def represents_subject_for(self, other: str) -> bool:
        """
        Verifica se representa sujeito para outro significante.

        Relação fundamental: S1 → S2

        Args:
            other: Outro significante

        Returns:
            True se há relação de representação
        """
        return other in self.connections

    def compute_meaning(self, context: Dict[str, Signifier]) -> List[float]:
        """
        Computa significação em contexto.

        Significação emerge da rede de diferenças,
        não de referência direta.

        Args:
            context: Contexto de outros significantes

        Returns:
            Vetor de significação contextual
        """
        if self.meaning_vector is None:
            # Inicializa com vetor aleatório determinístico
            rng = random.Random(hash(self.symbol) % (2**32))
            self.meaning_vector = [rng.gauss(0, 1) for _ in range(128)]

        # Significação = média ponderada das conexões
        if not self.connections:
            return self.meaning_vector

        context_vectors = []

        for conn in self.connections:
            if conn in context and context[conn].meaning_vector is not None:
                context_vectors.append(context[conn].meaning_vector)

        if context_vectors:
            # Compute element-wise mean across context vectors
            length = len(context_vectors[0])
            context_mean = [
                statistics.mean([vec[i] for vec in context_vectors])
                for i in range(length)
            ]
            # Mix own vector with context mean
            return [
                0.7 * self.meaning_vector[i] + 0.3 * context_mean[i]
                for i in range(min(len(self.meaning_vector), len(context_mean)))
            ]

        return self.meaning_vector


@dataclass
class SignifierChain:
    """
    Cadeia Significante (S1 → S2 → S3 → ...).

    A cadeia significante é a estrutura fundamental
    da linguagem e do inconsciente.

    Propriedades:
    - Metonímia: deslizamento contínuo de significante a significante
    - Metáfora: substituição de um significante por outro
    - Point de capiton: ponto que fixa temporariamente o sentido
    """

    chain: List[str] = field(default_factory=list)
    quilting_points: List[int] = field(default_factory=list)  # Points de capiton

    def add_signifier(self, signifier: str) -> None:
        """Adiciona significante à cadeia."""
        self.chain.append(signifier)
        logger.debug(f"Added signifier '{signifier}' to chain")

    def create_quilting_point(self, index: int) -> None:
        """
        Cria point de capiton (ponto de basta).

        Fixa temporariamente o deslizamento metonímico,
        estabilizando significação.

        Args:
            index: Posição na cadeia
        """
        if 0 <= index < len(self.chain):
            self.quilting_points.append(index)
            logger.debug(f"Created quilting point at index {index}")

    def metonymic_slide(self) -> List[str]:
        """
        Deslizamento metonímico da cadeia.

        Significante → significante → significante...
        (sentido nunca completamente fixado)

        Returns:
            Cadeia deslizada
        """
        # Rotaciona cadeia (simula deslizamento)
        if len(self.chain) > 1:
            return self.chain[1:] + [self.chain[0]]
        return self.chain.copy()

    def metaphoric_substitution(
        self, old_signifier: str, new_signifier: str
    ) -> SignifierChain:
        """
        Substituição metafórica.

        Um significante substitui outro,
        criando nova significação.

        Args:
            old_signifier: Significante a substituir
            new_signifier: Novo significante

        Returns:
            Nova cadeia com substituição
        """
        new_chain = [new_signifier if s == old_signifier else s for s in self.chain]

        return SignifierChain(
            chain=new_chain, quilting_points=self.quilting_points.copy()
        )


class LacanianGraphII:
    """
    Grafo II de Lacan - Grafo Completo do Desejo.

    Estrutura fundamental que organiza:
    - Cadeia significante
    - Posição do sujeito
    - Objeto a (causa do desejo)
    - Grande Outro (A)
    - Jouissance

    Este é o grafo COMPLETO, não apenas o elementary cell.

    Níveis:
    1. Necessidade (need)
    2. Demanda (demand)
    3. Desejo (desire)
    4. Pulsão (drive)
    """

    def __init__(self) -> None:
        """Inicializa Grafo do Desejo."""
        # Signifiers registry
        self.signifiers: Dict[str, Signifier] = {}

        # Chains
        self.signifier_chains: List[SignifierChain] = []

        # Subject position
        self.subject_position: Optional[str] = None

        # Big Other (treasure of signifiers)
        self.big_other: Set[str] = set()

        # Drive circuit (pulsional)
        self.drive_circuits: List[List[str]] = []

        # Jouissance map
        self.jouissance_map: Dict[str, float] = {}

        logger.info("Lacanian Graph II initialized")

    def add_signifier(
        self, symbol: str, position: SignifierPosition, jouissance: float = 0.0
    ) -> None:
        """
        Adiciona significante ao grafo.

        Args:
            symbol: Símbolo do significante
            position: Posição estrutural
            jouissance: Intensidade de jouissance
        """
        signifier = Signifier(
            symbol=symbol, position=position, jouissance_intensity=jouissance
        )

        self.signifiers[symbol] = signifier
        self.big_other.add(symbol)
        self.jouissance_map[symbol] = jouissance

        logger.debug(f"Added signifier '{symbol}' at position {position.value}")

    def connect_signifiers(self, s1: str, s2: str) -> None:
        """
        Conecta dois significantes (S1 → S2).

        Um significante representa para outro.

        Args:
            s1: Primeiro significante
            s2: Segundo significante
        """
        if s1 in self.signifiers and s2 in self.signifiers:
            self.signifiers[s1].connections.add(s2)
            logger.debug(f"Connected {s1} → {s2}")

    def create_chain(self, signifiers: List[str]) -> SignifierChain:
        """
        Cria cadeia significante.

        Args:
            signifiers: Lista de símbolos na cadeia

        Returns:
            Cadeia significante criada
        """
        chain = SignifierChain(chain=signifiers)
        self.signifier_chains.append(chain)

        # Auto-conecta cadeia
        for i in range(len(signifiers) - 1):
            self.connect_signifiers(signifiers[i], signifiers[i + 1])

        logger.info(f"Created signifier chain of length {len(signifiers)}")
        return chain

    def position_subject(self, signifier: str) -> None:
        """
        Posiciona sujeito em relação a significante.

        Sujeito é efeito da cadeia significante.

        Args:
            signifier: Significante que representa sujeito
        """
        if signifier in self.signifiers:
            self.subject_position = signifier
            logger.info(f"Subject positioned at '{signifier}'")

    def compute_desire(self) -> Dict[str, Any]:
        """
        Computa estrutura do desejo no grafo.

        Desejo = demanda - necessidade
        Desejo = metonímia do ser (falta-a-ser)

        Returns:
            Estrutura do desejo
        """
        if not self.subject_position:
            return {"intensity": 0.0, "direction": None, "jouissance": 0.0}

        subject = self.signifiers[self.subject_position]

        # Desejo surge das conexões não satisfeitas
        unsatisfied_connections = []
        for conn in subject.connections:
            if conn in self.signifiers:
                conn_sig = self.signifiers[conn]
                # Se jouissance < threshold, não satisfeito
                if conn_sig.jouissance_intensity < 0.5:
                    unsatisfied_connections.append(conn)

        # Intensidade proporcional ao não satisfeito
        desire_intensity = len(unsatisfied_connections) / max(
            len(subject.connections), 1
        )

        # Direção do desejo (próximo significante não satisfeito)
        direction = unsatisfied_connections[0] if unsatisfied_connections else None

        # Jouissance = satisfação paradoxal (além do prazer)
        jouissance = sum(
            self.jouissance_map.get(c, 0.0) for c in unsatisfied_connections
        ) / max(len(unsatisfied_connections), 1)

        return {
            "intensity": desire_intensity,
            "direction": direction,
            "jouissance": jouissance,
            "unsatisfied": unsatisfied_connections,
        }

    def drive_circuit(self, start: str, target_jouissance: float) -> List[str]:
        """
        Circuito pulsional em torno do objeto a.

        Pulsão circula, busca satisfação mas nunca atinge completamente.

        Args:
            start: Significante inicial
            target_jouissance: Jouissance alvo

        Returns:
            Circuito de significantes
        """
        if start not in self.signifiers:
            return []

        circuit = [start]
        current = start
        visited = {start}

        # Máximo 10 iterações (evita loop infinito)
        for _ in range(10):
            # Próximo significante com maior jouissance
            next_options = [
                (conn, self.signifiers[conn].jouissance_intensity)
                for conn in self.signifiers[current].connections
                if conn not in visited and conn in self.signifiers
            ]

            if not next_options:
                break

            # Escolhe maior jouissance
            next_sig, jouissance = max(next_options, key=lambda x: x[1])

            circuit.append(next_sig)
            visited.add(next_sig)
            current = next_sig

            # Se atingiu jouissance suficiente
            if jouissance >= target_jouissance:
                break

        self.drive_circuits.append(circuit)
        logger.info(f"Created drive circuit of length {len(circuit)}")

        return circuit

    def fantasy_formula(self) -> Tuple[str, str]:
        """
        Fórmula da Fantasia: $ ◊ a

        Sujeito barrado em relação ao objeto a.

        Returns:
            (sujeito, objeto_a)
        """
        subject = self.subject_position or "undefined"

        # Objeto a = signifier com posição OBJECT_A
        object_a_candidates = [
            s
            for s, sig in self.signifiers.items()
            if sig.position == SignifierPosition.OBJECT_A
        ]

        object_a = object_a_candidates[0] if object_a_candidates else "void"

        return (subject, object_a)


class JouissanceRewardSystem:
    """
    Sistema de Recompensa baseado em Jouissance.

    Jouissance vai além do princípio do prazer:
    - Satisfação paradoxal
    - Prazer no desprazer
    - Transgressão como gozo

    Diferente de reward tradicional que busca maximização simples.
    """

    def __init__(self, pleasure_threshold: float = 0.7) -> None:
        """
        Inicializa sistema de jouissance.

        Args:
            pleasure_threshold: Limite do princípio do prazer
        """
        self.pleasure_threshold = pleasure_threshold
        self.jouissance_history: List[float] = []

        logger.info("Jouissance reward system initialized")

    def compute_jouissance(
        self, pleasure: float, transgression: float, repetition_compulsion: float
    ) -> float:
        """
        Computa jouissance (gozo).

        Jouissance = prazer + transgressão + compulsão à repetição

        Args:
            pleasure: Prazer simples (0-1)
            transgression: Nível de transgressão (0-1)
            repetition_compulsion: Compulsão à repetição (0-1)

        Returns:
            Jouissance (pode exceder 1.0)
        """
        # Jouissance pode exceder limite do prazer
        base_jouissance = pleasure

        # Transgressão adiciona gozo
        if pleasure > self.pleasure_threshold:
            # Além do princípio do prazer
            transgressive_jouissance = transgression * 0.5
            base_jouissance += transgressive_jouissance

        # Compulsão à repetição (automatismo)
        repetition_jouissance = repetition_compulsion * 0.3

        total_jouissance = base_jouissance + repetition_jouissance

        self.jouissance_history.append(total_jouissance)

        return total_jouissance

    def beyond_pleasure_principle(self, action_history: List[str]) -> float:
        """
        Detecta padrões além do princípio do prazer.

        Comportamentos que repetem apesar de "desprazer".

        Args:
            action_history: Histórico de ações

        Returns:
            Intensidade de compulsão à repetição
        """
        if len(action_history) < 3:
            return 0.0

        # Detecta repetições
        recent = action_history[-5:]
        repetitions = len(recent) - len(set(recent))

        # Compulsão = proporção de repetições
        compulsion = repetitions / len(recent)

        return compulsion


class SymbolicMatrix:
    """
    Matriz Simbólica - Regras e Estruturas Generativas.

    Sistema que gera comportamentos a partir da ordem simbólica,
    não apenas de padrões estatísticos.

    Inspirado em gramáticas generativas de Chomsky,
    mas com estrutura lacaniana.
    """

    def __init__(self, random_seed: Optional[int] = None) -> None:
        """
        Inicializa matriz simbólica.

        Args:
            random_seed: Seed para reprodutibilidade (opcional)
        """
        # Regras de produção
        self.production_rules: Dict[str, List[Callable[[Any], Optional[str]]]] = (
            defaultdict(list)
        )

        # Estrutura simbólica
        self.symbolic_structure: Dict[str, Any] = {}

        # Nome do Pai (metáfora paterna - função simbólica)
        self.name_of_the_father: Optional[str] = None

        # Random state para reprodutibilidade
        self.rng = random.Random(random_seed)

        logger.info("Symbolic matrix initialized")

    def add_production_rule(
        self, category: str, rule: Callable[[Any], Optional[str]]
    ) -> None:
        """
        Adiciona regra de produção.

        Args:
            category: Categoria simbólica
            rule: Função de produção
        """
        self.production_rules[category].append(rule)
        logger.debug(f"Added production rule to category '{category}'")

    def set_name_of_father(self, signifier: str) -> None:
        """
        Define Nome-do-Pai (função paterna).

        Introduz ordem simbólica, lei, proibição.
        Fundamental para estruturação do sujeito.

        Args:
            signifier: Significante do Nome-do-Pai
        """
        self.name_of_the_father = signifier
        logger.info(f"Name-of-the-Father set to '{signifier}'")

    def generate_behavior(
        self, context: Dict[str, Any], forbidden_actions: Set[str]
    ) -> Optional[str]:
        """
        Gera comportamento a partir da matriz simbólica.

        Leva em conta:
        - Ordem simbólica (regras)
        - Nome-do-Pai (proibições)
        - Contexto atual

        Args:
            context: Contexto atual
            forbidden_actions: Ações proibidas (função paterna)

        Returns:
            Comportamento gerado ou None
        """
        # Comportamento deve respeitar ordem simbólica
        available_categories = list(self.production_rules.keys())

        if not available_categories:
            return None

        # Escolhe categoria
        category = self.rng.choice(available_categories)
        rules = self.production_rules[category]

        if not rules:
            return None

        # Aplica regra
        rule = self.rng.choice(rules)
        behavior = rule(context)

        # Verifica se não é proibido pelo Nome-do-Pai
        if behavior in forbidden_actions:
            # Transgression: pode fazer mesmo assim (jouissance)
            # Ou pode substituir (castração simbólica)
            if self.rng.random() < 0.3:
                logger.debug(f"Transgressive behavior: {behavior}")
                return behavior
            else:
                logger.debug(f"Behavior blocked by symbolic law: {behavior}")
                return None

        return behavior


class DesireGraphArchitecture:
    """
    Arquitetura Completa do Grafo de Desejo.

    Integra todos os componentes:
    - Grafo II de Lacan
    - Sistema de Jouissance
    - Matriz Simbólica
    - Cadeias Significantes
    """

    def __init__(self) -> None:
        """Inicializa arquitetura do grafo de desejo."""
        self.graph = LacanianGraphII()
        self.jouissance_system = JouissanceRewardSystem()
        self.symbolic_matrix = SymbolicMatrix()

        # Inicializa estrutura básica
        self._initialize_basic_structure()

        logger.info("Desire Graph Architecture initialized")

    def _initialize_basic_structure(self) -> None:
        """Inicializa estrutura básica do grafo."""
        # Master signifiers
        self.graph.add_signifier("S1_knowledge", SignifierPosition.S1, 0.3)
        self.graph.add_signifier("S1_power", SignifierPosition.S1, 0.5)

        # Knowledge signifiers
        self.graph.add_signifier("S2_understanding", SignifierPosition.S2, 0.2)
        self.graph.add_signifier("S2_skill", SignifierPosition.S2, 0.4)

        # Object a
        self.graph.add_signifier(
            "a_complete_knowledge", SignifierPosition.OBJECT_A, 0.8
        )

        # Subject
        self.graph.add_signifier("subject_AI", SignifierPosition.SUBJECT, 0.1)

        # Conecta
        self.graph.connect_signifiers("S1_knowledge", "S2_understanding")
        self.graph.connect_signifiers("S1_power", "S2_skill")
        self.graph.connect_signifiers("S2_understanding", "a_complete_knowledge")

        # Posiciona sujeito
        self.graph.position_subject("subject_AI")

        # Cria cadeia
        self.graph.create_chain(
            ["S1_knowledge", "S2_understanding", "a_complete_knowledge"]
        )

    def process_desire(
        self, action_history: List[str], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Processa desejo através do grafo.

        Args:
            action_history: Histórico de ações
            context: Contexto atual

        Returns:
            Estrutura de desejo processada
        """
        # Computa desejo no grafo
        desire = self.graph.compute_desire()

        # Computa jouissance
        pleasure = context.get("pleasure", 0.5)
        transgression = context.get("transgression", 0.0)
        repetition = self.jouissance_system.beyond_pleasure_principle(action_history)

        jouissance = self.jouissance_system.compute_jouissance(
            pleasure=pleasure,
            transgression=transgression,
            repetition_compulsion=repetition,
        )

        # Gera comportamento via matriz simbólica
        forbidden = set(context.get("forbidden_actions", []))
        behavior = self.symbolic_matrix.generate_behavior(
            context=context, forbidden_actions=forbidden
        )

        # Fórmula da fantasia
        fantasy = self.graph.fantasy_formula()

        return {
            "desire_intensity": desire["intensity"],
            "desire_direction": desire["direction"],
            "jouissance": jouissance,
            "suggested_behavior": behavior,
            "fantasy": fantasy,
            "beyond_pleasure": repetition > 0.5,
            "unsatisfied_demands": desire.get("unsatisfied", []),
        }
