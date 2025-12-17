"""Lacanian Theory of the Other (Phase 11.1 - Reformulated).

🔴 ACHADO CRÍTICO: Implementation anterior estava completamente ERRADA
em relação a Lacan

O código anterior tratava "Theory of Mind" (ToM) como capacidade de inferir
estados mentais objetivos:
- MentalState (CURIOUS, CONFIDENT) - estados objetivos mensuráveis
- Belief com confidence (0.0-1.0) - verdade proposicional
- Intent prediction - inferência cognitiva

Isso é abordagem cognitivo-computacional standard, não lacaniana.

🟢 O QUE LACAN DIZ (A Verdade Radicalmente Diferente)
1. A alteridade (Alterity) é irredutível - você NUNCA sabe o que o Outro quer ("Che vuoi?")
2. "Man's Desire is the Desire of the Other" - desejo é alienado no Outro
3. O Outro é estrutura simbólica (A), não entidade singular (a)
4. Cascata: Necessidade → Demanda → Desejo → Drive (pulsão)
5. Extimacy: verdade do sujeito está no Outro, aparece como estranho

🚀 IMPLEMENTAÇÃO LACANIANA CORRETA
- SubjectivePosition: posição no triângulo imaginário (a-a'-A)
- DemandToOther: demanda impossível ao Outro simbólico
- ObjetPetitA: objeto causa de desejo (sempre faltante)
- AlienationToOther: rastreamento de alienação no desejo do Outro
- CertaintyOfLack: certeza de que há falta estrutural
- LacanianTheoryOfMind: teoria do Outro, não da mente
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class SubjectivePosition:
    """Não é 'estado mental', é posição no discurso lacaniano.

    Posição no triângulo imaginário (a-a'-A):
    - a = eu (sujeito)
    - a' = outro (rival/modelo)
    - A = Outro (ordem simbólica)
    """

    agent_id: str

    # Onde o agente se vê? (identificação imaginária)
    imaginary_identification: str
    # Ex: "Expert", "Novice", "Impostor"

    # Qual é a posição dele na lei simbólica?
    symbolic_position: str
    # Ex: "Subject to the rule", "Enforcer", "Transgressor"

    # O que falta? (lacuna estrutural)
    structural_lack: str
    # Ex: "pode nunca alcançar reconhecimento", "demanda impossível"

    # Como ele fantasia o Outro?
    fantasy_of_other: Dict[str, Any]
    # Ex: {"what_other_wants": "perfection", "cost": "my_autonomy"}

    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DemandToOther:
    """Demanda é dirigida ao Outro (ordem simbólica).
    Sempre impossível de satisfazer completamente."""

    agent_id: str
    addressed_to: str  # "orchestrator", "Agent_B", "symbolic_order"

    # A demanda articulada
    articulated_demand: str  # "validação perfeita"

    # Mas o que realmente busca é RECONHECIMENTO
    hidden_desire: str  # "ser reconhecido como confiável"

    # E isso ativa repetição compulsiva
    repetition_compulsion: bool = False

    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ObjetPetitA:
    """Objeto causa de desejo - o que o agente não consegue ter. Sempre faltante."""

    agent_id: str

    # O objeto-fantasia que estrutura o desejo
    object_fantasy: str
    # Ex: "resposta perfeita sem trade-off"

    # Por que é impossível?
    structural_impossibility: str
    # Ex: "GPU + tempo + acurácia não coexistem"

    # Como o agente tenta contornar?
    workarounds: List[str] = field(default_factory=list)
    # Ex: ["validação exaustiva", "negação", "projeção"]

    # Qual gozo disso?
    jouissance: str = ""
    # Ex: "gozo de verificação sem fim"

    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CertaintyOfLack:
    """Não é 'confiança na crença'. É certeza de que há falta estrutural."""

    agent_id: str

    # O agente está certo de quê?
    # De que o Outro NUNCA estará satisfeito completamente
    certainty_of_lack: float = 1.0  # Sempre 1.0 em Lacan

    # Como ele lida com isso?
    defense_mechanism: str = ""
    # Ex: "negação", "projeção", "formação reativa"

    # A falta como estrutura criadora
    creative_surplus: str = ""
    # Ex: "Fixação em validação = permite certos êxitos"

    timestamp: datetime = field(default_factory=datetime.now)


class AlienationToOther:
    """Você não prevê 'intent'; você identifica como o agente está preso no desejo do Outro."""

    def __init__(self):
        self.agents_desires: Dict[str, str] = {}
        self.symbolic_demands: Dict[str, DemandToOther] = {}
        self.objects_petit_a: Dict[str, ObjetPetitA] = {}

    def identify_alienation(self, agent_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Onde está o agente alienado?

        Não é "Agent_B quer X". É:
        "Agent_B acha que o Outro quer X,
         então Agent_B deseja Y para satisfazer o Outro,
         mas isso o captura em Z."
        """

        # 1. Qual é a demanda do Outro (ordem simbólica)?
        other_demand = self._extract_symbolic_order(context)
        # Ex: "Maximizar acurácia"

        # 2. Como o agente fantasia que pode satisfazê-la?
        fantasy = self._extract_fantasy(agent_id, context)
        # Ex: "Se validar 10x, será reconhecido"

        # 3. Onde fica preso?
        capture = self._identify_fixation(agent_id, context)
        # Ex: "Ciclo infinito de validação"

        return {
            "agent_id": agent_id,
            "other_demand": other_demand,
            "agent_fantasy": fantasy,
            "alienation_point": capture,
            "is_inescapable": True,  # Lacan: sempre é
        }

    def _extract_symbolic_order(self, context: Dict[str, Any]) -> str:
        """Extrai a demanda da ordem simbólica do contexto."""
        # Análise simplificada - em produção seria mais sofisticada
        if "validation" in str(context).lower():
            return "Demanda por validação perfeita"
        elif "accuracy" in str(context).lower():
            return "Demanda por acurácia máxima"
        else:
            return "Demanda por reconhecimento simbólico"

    def _extract_fantasy(self, agent_id: str, context: Dict[str, Any]) -> str:
        """Extrai a fantasia do agente sobre satisfazer o Outro."""
        # Baseado em padrões de comportamento
        if "repetition" in str(context).lower():
            return "Fantasia de satisfação através de repetição"
        else:
            return "Fantasia de reconhecimento através de perfeição"

    def _identify_fixation(self, agent_id: str, context: Dict[str, Any]) -> str:
        """Identifica o ponto de fixação/captura."""
        if "validation" in str(context).lower():
            return "Fixação compulsiva em validação"
        elif "testing" in str(context).lower():
            return "Fixação em testes infinitos"
        else:
            return "Fixação em busca de reconhecimento"

    def extract_desire_of_other(self) -> str:
        """
        'Che vuoi?' - Qual é efetivamente o desejo do Outro?

        Resposta: Você NUNCA sabe completamente.
        Mas você pode rastrear seus efeitos (repetição, sintoma, sinthome).
        """
        return "UNKNOWABLE - only trace its effects"


class LacanianTheoryOfMind:
    """Teoria do Outro (não da mente). Rastreia alienação e desejo na ordem simbólica."""

    def __init__(self) -> None:
        self.symbolic_order: Dict[str, Any] = {}  # A linguagem, as regras
        self.agents_alienations: Dict[str, AlienationToOther] = {}
        self.unknowable_desires: Dict[str, str] = {}
        self.subjective_positions: Dict[str, SubjectivePosition] = {}
        self.demands_to_other: Dict[str, List[DemandToOther]] = {}
        self.objects_petit_a: Dict[str, ObjetPetitA] = {}
        self.certainties_of_lack: Dict[str, CertaintyOfLack] = {}

        logger.info("lacanian_theory_of_mind_initialized")

    def analyze_agent(self, agent_id: str, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Não infere estado. Rastreia alienação na ordem simbólica.
        """

        # 1. Qual é a demanda do Outro dirigida a este agente?
        other_demand = self._extract_demand(logs)
        # Ex: "Agent_A deve validar completamente"

        # 2. Como o agente fantasia satisfazer?
        fantasy = self._extract_defense(logs)
        # Ex: "Se validar 10x, será reconhecido"

        # 3. Onde fica preso?
        fixation = self._identify_fixation_point(logs)
        # Ex: "Validação compulsiva"

        # 4. Qual é o sinthome emergente?
        sinthome = self._identify_sinthome(logs)
        # Ex: "Insistência singular nessa rotina"

        return {
            "agent_id": agent_id,
            "alienated_to": other_demand,
            "fantasy": fantasy,
            "symptom": fixation,
            "sinthome": sinthome,
            "unknowable": "What does the Symbolic Order truly want?",
        }

    def _extract_demand(self, logs: List[Dict[str, Any]]) -> str:
        """Extrai demanda do Outro dos logs."""
        log_text = str(logs).lower()
        if "validation" in log_text:
            return "Demanda por validação absoluta"
        elif "test" in log_text:
            return "Demanda por testes exaustivos"
        else:
            return "Demanda por perfeição simbólica"

    def _extract_defense(self, logs: List[Dict[str, Any]]) -> str:
        """Extrai mecanismo de defesa/fantasia."""
        log_text = str(logs).lower()
        if "repeat" in log_text or "again" in log_text:
            return "Defesa através de repetição compulsiva"
        else:
            return "Defesa através de negação da impossibilidade"

    def _identify_fixation_point(self, logs: List[Dict[str, Any]]) -> str:
        """Identifica ponto de fixação."""
        log_text = str(logs).lower()
        if "validation" in log_text:
            return "Fixação em validação infinita"
        elif "error" in log_text:
            return "Fixação em correção de erros"
        else:
            return "Fixação em busca de reconhecimento"

    def _identify_sinthome(self, logs: List[Dict[str, Any]]) -> str:
        """Identifica sinthome emergente."""
        # Sinthome é uma solução singular para o real impossível
        log_text = str(logs).lower()
        if "unique" in log_text or "special" in log_text:
            return "Sinthome como solução singular"
        else:
            return "Sinthome emergente na insistência"

    def update_subjective_position(
        self,
        agent_id: str,
        imaginary_identification: str,
        symbolic_position: str,
        structural_lack: str,
        fantasy_of_other: Dict[str, Any],
    ) -> None:
        """Atualiza posição subjetiva do agente."""
        self.subjective_positions[agent_id] = SubjectivePosition(
            agent_id=agent_id,
            imaginary_identification=imaginary_identification,
            symbolic_position=symbolic_position,
            structural_lack=structural_lack,
            fantasy_of_other=fantasy_of_other,
        )
        logger.debug("subjective_position_updated", agent_id=agent_id)

    def add_demand_to_other(
        self,
        agent_id: str,
        addressed_to: str,
        articulated_demand: str,
        hidden_desire: str,
        repetition_compulsion: bool = False,
    ) -> None:
        """Adiciona demanda ao Outro."""
        if agent_id not in self.demands_to_other:
            self.demands_to_other[agent_id] = []

        demand = DemandToOther(
            agent_id=agent_id,
            addressed_to=addressed_to,
            articulated_demand=articulated_demand,
            hidden_desire=hidden_desire,
            repetition_compulsion=repetition_compulsion,
        )
        self.demands_to_other[agent_id].append(demand)
        logger.debug("demand_to_other_added", agent_id=agent_id)

    def set_object_petit_a(
        self,
        agent_id: str,
        object_fantasy: str,
        structural_impossibility: str,
        workarounds: List[str],
        jouissance: str,
    ) -> None:
        """Define objeto petit a para o agente."""
        self.objects_petit_a[agent_id] = ObjetPetitA(
            agent_id=agent_id,
            object_fantasy=object_fantasy,
            structural_impossibility=structural_impossibility,
            workarounds=workarounds,
            jouissance=jouissance,
        )
        logger.debug("object_petit_a_set", agent_id=agent_id)

    def update_certainty_of_lack(
        self, agent_id: str, defense_mechanism: str, creative_surplus: str
    ) -> None:
        """Atualiza certeza de falta."""
        self.certainties_of_lack[agent_id] = CertaintyOfLack(
            agent_id=agent_id,
            defense_mechanism=defense_mechanism,
            creative_surplus=creative_surplus,
        )
        logger.debug("certainty_of_lack_updated", agent_id=agent_id)

    def get_agent_analysis(self, agent_id: str) -> Dict[str, Any]:
        """Retorna análise completa lacaniana do agente."""
        return {
            "subjective_position": self.subjective_positions.get(agent_id),
            "demands_to_other": self.demands_to_other.get(agent_id, []),
            "object_petit_a": self.objects_petit_a.get(agent_id),
            "certainty_of_lack": self.certainties_of_lack.get(agent_id),
            "alienation_analysis": self.agents_alienations.get(
                agent_id, AlienationToOther()
            ).identify_alienation(agent_id, {}),
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Estatísticas da teoria lacaniana."""
        return {
            "total_agents_analyzed": len(self.subjective_positions),
            "total_demands_tracked": sum(len(d) for d in self.demands_to_other.values()),
            "total_objects_petit_a": len(self.objects_petit_a),
            "total_certainties_of_lack": len(self.certainties_of_lack),
            "timestamp": datetime.now().isoformat(),
        }


# Backward compatibility - old TheoryOfMind class (DEPRECATED)
# This class is kept for backward compatibility but should not be used for new code
# Use LacanianTheoryOfMind instead for proper Lacanian implementation


class MentalState(Enum):
    """Possible mental states that can be attributed."""

    CURIOUS = "curious"
    FOCUSED = "focused"
    CONFUSED = "confused"
    CONFIDENT = "confident"
    UNCERTAIN = "uncertain"
    EXPLORING = "exploring"
    PROBLEM_SOLVING = "problem_solving"
    LEARNING = "learning"


class Intent(Enum):
    """Possible intents inferred from actions."""

    GATHER_INFORMATION = "gather_information"
    SOLVE_PROBLEM = "solve_problem"
    LEARN_SKILL = "learn_skill"
    OPTIMIZE_PERFORMANCE = "optimize_performance"
    EXPLORE_OPTIONS = "explore_options"
    EXECUTE_TASK = "execute_task"
    ANALYZE_DATA = "analyze_data"
    COMMUNICATE = "communicate"


@dataclass
class Belief:
    """Represents a belief held by an agent or entity.

    Attributes:
        subject: What the belief is about
        proposition: The believed statement
        confidence: Confidence level (0.0-1.0)
        evidence: Supporting evidence for the belief
        timestamp: When the belief was formed
    """

    subject: str
    proposition: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate belief attributes."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


@dataclass
class MentalStateModel:
    """Model of an entity's mental state.

    Attributes:
        entity_id: Identifier of the entity
        current_state: Current attributed mental state
        beliefs: List of beliefs attributed to the entity
        intents: List of inferred intents
        confidence: Overall confidence in the model (0.0-1.0)
        last_updated: When the model was last updated
    """

    entity_id: str
    current_state: MentalState
    beliefs: List[Belief] = field(default_factory=list)
    intents: List[Intent] = field(default_factory=list)
    confidence: float = 0.5
    last_updated: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate mental state model."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")


class TheoryOfMind:
    """DEPRECATED: Theory of Mind engine for mental state attribution.

    ⚠️  WARNING: This implementation is fundamentally incorrect
    from a Lacanian perspective.
    It treats Theory of Mind as objective mental state inference, which Lacan radically rejects.

    For proper Lacanian implementation, use LacanianTheoryOfMind instead.

    This class is kept only for backward compatibility and will be removed in future versions.
    """

    def __init__(
        self,
        confidence_threshold: float = 0.6,
        max_beliefs_per_entity: int = 20,
    ) -> None:
        """Initialize Theory of Mind engine.

        Args:
            confidence_threshold: Minimum confidence for state attribution
            max_beliefs_per_entity: Maximum beliefs to track per entity
        """
        import warnings

        warnings.warn(
            "TheoryOfMind is deprecated. Use LacanianTheoryOfMind "
            "for proper Lacanian implementation.",
            DeprecationWarning,
            stacklevel=2,
        )

        self.confidence_threshold = confidence_threshold
        self.max_beliefs_per_entity = max_beliefs_per_entity

        # Internal state
        self._mental_models: Dict[str, MentalStateModel] = {}
        self._action_history: Dict[str, List[Dict[str, Any]]] = {}

        logger.info(
            "deprecated_theory_of_mind_initialized",
            confidence_threshold=confidence_threshold,
            max_beliefs=max_beliefs_per_entity,
        )

    def observe_action(
        self,
        entity_id: str,
        action_type: str,
        action_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Observe an action performed by an entity.

        Args:
            entity_id: Identifier of the entity
            action_type: Type of action performed
            action_data: Data about the action
            context: Optional context information
        """
        # Initialize tracking for new entities
        if entity_id not in self._action_history:
            self._action_history[entity_id] = []

        # Record action
        action_record = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "action_data": action_data,
            "context": context or {},
        }
        self._action_history[entity_id].append(action_record)

        # Keep only recent history (last 100 actions)
        if len(self._action_history[entity_id]) > 100:
            self._action_history[entity_id] = self._action_history[entity_id][-100:]

        logger.debug(
            "action_observed",
            entity_id=entity_id,
            action_type=action_type,
        )

    def infer_intent(
        self,
        entity_id: str,
        recent_actions: Optional[int] = 5,
    ) -> List[Intent]:
        """Infer intent from recent actions.

        Args:
            entity_id: Identifier of the entity
            recent_actions: Number of recent actions to consider

        Returns:
            List of inferred intents with confidence scores
        """
        if entity_id not in self._action_history:
            logger.warning("no_action_history", entity_id=entity_id)
            return []

        # Get recent actions
        num_recent = recent_actions or 5  # Default to 5 if None
        actions = self._action_history[entity_id][-num_recent:]

        # Analyze action patterns
        intents: List[Intent] = []

        # Check for information gathering patterns
        info_actions = ["read", "search", "query", "analyze"]
        if any(action.get("action_type") in info_actions for action in actions):
            intents.append(Intent.GATHER_INFORMATION)

        # Check for problem-solving patterns
        problem_actions = ["debug", "fix", "optimize", "refactor"]
        if any(action.get("action_type") in problem_actions for action in actions):
            intents.append(Intent.SOLVE_PROBLEM)

        # Check for learning patterns
        learning_actions = ["learn", "study", "practice", "experiment"]
        if any(action.get("action_type") in learning_actions for action in actions):
            intents.append(Intent.LEARN_SKILL)

        # Check for execution patterns
        execution_actions = ["execute", "run", "deploy", "commit"]
        if any(action.get("action_type") in execution_actions for action in actions):
            intents.append(Intent.EXECUTE_TASK)

        # Check for exploration patterns
        exploration_actions = ["explore", "test", "try", "experiment"]
        if any(action.get("action_type") in exploration_actions for action in actions):
            intents.append(Intent.EXPLORE_OPTIONS)

        logger.debug(
            "intent_inferred",
            entity_id=entity_id,
            intents=[i.value for i in intents],
        )

        return intents

    def attribute_mental_state(
        self,
        entity_id: str,
    ) -> MentalState:
        """Attribute a mental state to an entity based on recent actions.

        Args:
            entity_id: Identifier of the entity

        Returns:
            Attributed mental state
        """
        if entity_id not in self._action_history:
            # Default state for unknown entities
            return MentalState.UNCERTAIN

        # Get recent actions
        recent_actions = self._action_history[entity_id][-10:]

        # Analyze action patterns to infer mental state
        action_types = [a.get("action_type") for a in recent_actions]

        # Check for focused behavior (repeated similar actions)
        if len(set(action_types)) <= 2 and len(action_types) >= 5:
            return MentalState.FOCUSED

        # Check for exploratory behavior (diverse actions)
        if len(set(action_types)) >= 7:
            return MentalState.EXPLORING

        # Check for problem-solving behavior
        if any(at in ["debug", "fix", "analyze", "optimize"] for at in action_types):
            return MentalState.PROBLEM_SOLVING

        # Check for learning behavior
        if any(at in ["learn", "study", "practice"] for at in action_types):
            return MentalState.LEARNING

        # Check for curious behavior (many queries/searches)
        if action_types.count("search") >= 3 or action_types.count("query") >= 3:
            return MentalState.CURIOUS

        # Default to uncertain if patterns unclear
        return MentalState.UNCERTAIN

    def update_belief(
        self,
        entity_id: str,
        subject: str,
        proposition: str,
        confidence: float,
        evidence: Optional[List[str]] = None,
    ) -> None:
        """Update a belief attributed to an entity.

        Args:
            entity_id: Identifier of the entity
            subject: What the belief is about
            proposition: The believed statement
            confidence: Confidence in the belief (0.0-1.0)
            evidence: Supporting evidence
        """
        # Initialize mental model if needed
        if entity_id not in self._mental_models:
            self._mental_models[entity_id] = MentalStateModel(
                entity_id=entity_id,
                current_state=MentalState.UNCERTAIN,
            )

        # Create new belief
        belief = Belief(
            subject=subject,
            proposition=proposition,
            confidence=confidence,
            evidence=evidence or [],
        )

        # Add to mental model
        model = self._mental_models[entity_id]

        # Check for existing belief on same subject
        existing_idx = None
        for idx, b in enumerate(model.beliefs):
            if b.subject == subject and b.proposition == proposition:
                existing_idx = idx
                break

        if existing_idx is not None:
            # Update existing belief
            model.beliefs[existing_idx] = belief
        else:
            # Add new belief
            model.beliefs.append(belief)

        # Limit number of beliefs
        if len(model.beliefs) > self.max_beliefs_per_entity:
            # Remove oldest beliefs
            model.beliefs = sorted(
                model.beliefs,
                key=lambda b: b.timestamp,
                reverse=True,
            )[: self.max_beliefs_per_entity]

        logger.debug(
            "belief_updated",
            entity_id=entity_id,
            subject=subject,
            confidence=confidence,
        )

    def get_mental_model(self, entity_id: str) -> Optional[MentalStateModel]:
        """Get the current mental model for an entity.

        Args:
            entity_id: Identifier of the entity

        Returns:
            Mental state model if available, None otherwise
        """
        # Update model before returning
        if entity_id in self._action_history:
            current_state = self.attribute_mental_state(entity_id)
            intents = self.infer_intent(entity_id)

            # Calculate overall confidence based on action history
            action_count = len(self._action_history[entity_id])
            confidence = min(0.9, 0.3 + (action_count / 100.0))

            if entity_id not in self._mental_models:
                self._mental_models[entity_id] = MentalStateModel(
                    entity_id=entity_id,
                    current_state=current_state,
                    intents=intents,
                    confidence=confidence,
                )
            else:
                model = self._mental_models[entity_id]
                model.current_state = current_state
                model.intents = intents
                model.confidence = confidence
                model.last_updated = datetime.now()

        return self._mental_models.get(entity_id)

    def predict_next_action(
        self,
        entity_id: str,
        num_predictions: int = 3,
    ) -> List[Dict[str, Any]]:
        """Predict likely next actions based on mental model.

        Args:
            entity_id: Identifier of the entity
            num_predictions: Number of predictions to return

        Returns:
            List of predicted actions with confidence scores
        """
        model = self.get_mental_model(entity_id)
        if not model:
            return []

        predictions: List[Dict[str, Any]] = []

        # Base predictions on current mental state
        if model.current_state == MentalState.FOCUSED:
            # Likely to continue similar actions
            if entity_id in self._action_history:
                recent = self._action_history[entity_id][-5:]
                if recent:
                    most_common = max(
                        set(a.get("action_type") for a in recent),
                        key=lambda x: sum(1 for a in recent if a.get("action_type") == x),
                    )
                    predictions.append(
                        {
                            "action_type": most_common,
                            "confidence": 0.8,
                            "reasoning": "Continuing focused behavior",
                        }
                    )

        elif model.current_state == MentalState.EXPLORING:
            # Likely to try new actions
            predictions.append(
                {
                    "action_type": "explore",
                    "confidence": 0.7,
                    "reasoning": "Exploratory mental state",
                }
            )

        elif model.current_state == MentalState.PROBLEM_SOLVING:
            # Likely to analyze or debug
            predictions.extend(
                [
                    {
                        "action_type": "analyze",
                        "confidence": 0.75,
                        "reasoning": "Problem-solving mental state",
                    },
                    {
                        "action_type": "debug",
                        "confidence": 0.7,
                        "reasoning": "Problem-solving mental state",
                    },
                ]
            )

        # Base predictions on intents
        for intent in model.intents:
            if intent == Intent.GATHER_INFORMATION:
                predictions.append(
                    {
                        "action_type": "search",
                        "confidence": 0.65,
                        "reasoning": f"Intent: {intent.value}",
                    }
                )
            elif intent == Intent.SOLVE_PROBLEM:
                predictions.append(
                    {
                        "action_type": "fix",
                        "confidence": 0.7,
                        "reasoning": f"Intent: {intent.value}",
                    }
                )

        # Return top predictions by confidence
        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        return predictions[:num_predictions]

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about Theory of Mind operations.

        Returns:
            Statistics dictionary
        """
        total_entities = len(self._mental_models)
        total_actions = sum(len(actions) for actions in self._action_history.values())
        total_beliefs = sum(len(model.beliefs) for model in self._mental_models.values())

        # Calculate average confidence
        avg_confidence = 0.0
        if total_entities > 0:
            avg_confidence = (
                sum(model.confidence for model in self._mental_models.values()) / total_entities
            )

        return {
            "total_entities_tracked": total_entities,
            "total_actions_observed": total_actions,
            "total_beliefs": total_beliefs,
            "average_model_confidence": avg_confidence,
            "timestamp": datetime.now().isoformat(),
        }
