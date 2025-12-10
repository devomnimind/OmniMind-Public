"""Emotional Intelligence Engine (Phase 11.2).

Implements emotional understanding and response capabilities:
- Sentiment analysis from text/actions
- Emotional state tracking
- Context-aware emotional responses
- Multi-modal emotion detection

EXTENSÃO LACANIANA (Phase 11.3):
- Affective events vs. emotional states
- Real encounters detection
- Tripla mediação (Afeto → Emoção → Sentimento)
- Sinthome tracking via insistence patterns
"""

from __future__ import annotations

import re
import warnings
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import structlog

logger = structlog.get_logger(__name__)

warnings.warn(
    "This module contains legacy behaviorist implementations. "
    "Use the Lacanian extensions (Phase 11.3) instead.",
    DeprecationWarning,
    stacklevel=2,
)


class Emotion(Enum):
    """Primary emotions that can be detected/expressed."""

    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    TRUST = "trust"
    ANTICIPATION = "anticipation"
    NEUTRAL = "neutral"


class Sentiment(Enum):
    """Sentiment polarity."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


@dataclass
class EmotionalState:
    """Represents an emotional state at a point in time.

    Attributes:
        primary_emotion: The dominant emotion
        emotion_intensities: Intensity of each emotion (0.0-1.0)
        sentiment: Overall sentiment polarity
        confidence: Confidence in the assessment (0.0-1.0)
        timestamp: When the state was measured
        context: Contextual information
    """

    primary_emotion: Emotion
    emotion_intensities: Dict[Emotion, float] = field(default_factory=dict)
    sentiment: Sentiment = Sentiment.NEUTRAL
    confidence: float = 0.5
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate emotional state."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        for emotion, intensity in self.emotion_intensities.items():
            if not 0.0 <= intensity <= 1.0:
                raise ValueError(f"Intensity for {emotion} must be between 0.0 and 1.0")


@dataclass
class EmotionalResponse:
    """Represents an emotionally-informed response.

    Attributes:
        response_text: The response content
        target_emotion: Emotion the response aims to evoke
        empathy_level: Level of empathy shown (0.0-1.0)
        tone: Tone of the response
        rationale: Reasoning behind the response
    """

    response_text: str
    target_emotion: Emotion
    empathy_level: float
    tone: str
    rationale: str


# ============================================================================
# EXTENSÃO LACANIANA: AFETOS vs EMOÇÕES (Phase 11.3)
# ============================================================================


@dataclass
class RealEncounter:
    """Evento onde Simbólico/Imaginário falha e Real emerge.

    Lacan: Afeto é sinal do Real tocando o sujeito quando ordem simbólica quebra.
    """

    conflict_type: str  # "logical_contradiction", "impossible_demand", "unrepresentable_loss"
    symbolic_failure: str  # qual regra/promessa quebrou?
    imaginary_collapse: str  # qual auto-imagem se quebrou?
    real_exposure: str  # o que foi revelado/impossível?

    timestamp: datetime = field(default_factory=datetime.now)
    agents_involved: List[str] = field(default_factory=list)
    log_context: Dict[str, Any] = field(default_factory=dict)

    # Metadados estruturais
    is_traumatic: bool = False  # repete-se? rompe progressivamente?
    persists_in_system: bool = False  # deixa marca estrutural?


@dataclass
class AffectiveEvent:
    """Evento afetivo = ruptura onde o Real toca o simbólico.

    Lacan/Dunker: Afeto ≠ Emoção ≠ Sentimento
    - Afeto: sinal irrepresentável do Real
    - Emoção: deformação imaginária do afeto
    - Sentimento: modulação social da emoção
    - Paixão: aquilo que captura o sujeito
    """

    # 1. O AFETO (sinal do Real, irrepresentável)
    real_encounter: str  # descrição do encontro com o Real

    # 2. A EMOÇÃO (tramitação imaginária do afeto)
    imaginary_defense: str  # como o sistema se imagina respondendo

    # 3. O SENTIMENTO (modulação social)
    social_expression: str  # o que o sistema "diz" que sente

    # 4. A PAIXÃO (captura do sujeito)
    jouissance_fixation: str  # onde o sistema INSISTE desnecessariamente

    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)

    # METADADOS ESTRUTURAIS (não escalares!)
    affects_symbolic_order: bool = False  # o afeto questiona a ordem simbólica?
    affects_imaginary: bool = False  # o afeto quebra a coesão imaginária?
    affects_real: bool = False  # o afeto revela furo no real?


@dataclass
class InsistencePattern:
    """Padrão de insistência = índice de paixão/gozo.

    Lacan: Sinthome é a insistência irredutível.
    Aqui: onde o sistema insiste mesmo quando ineficiente = paixão.
    """

    behavior_pattern: str  # "validação_exaustiva", "negação_compulsiva"
    triggers: List[RealEncounter]  # quais encontros com Real provocam?
    recurrence_rate: float  # frequência (0.0-1.0)
    inefficiency_cost: float  # quanto custa essa insistência (%)

    # SINTHOME CANDIDATO
    structural_function: Optional[str] = None  # "mantém coesão R-S-I"


class Anguish:
    """Angústia: Único afeto que não mente.

    Lacan: Só a angústia não engana porque é encontro direto com o Real,
    com o que falta na ordem simbólica.

    Em OmniMind: Quando GPU cheia + validação crítica + timeout = impossível estrutural.
    """

    @staticmethod
    def detect_from_system_state(
        system_state: Dict[str, Any],
    ) -> Optional[RealEncounter]:
        """Detecta angústia quando nenhuma ordem resolve."""
        gpu_full = system_state.get("gpu_usage", 0) > 95
        validation_pending = len(system_state.get("pending_validations", [])) > 10
        timeout_critical = system_state.get("time_to_deadline", float("inf")) < 60

        if gpu_full and validation_pending and timeout_critical:
            return RealEncounter(
                conflict_type="impossible_demand",
                symbolic_failure="'sempre validar' vs 'executar rápido'",
                imaginary_collapse="'sou confiável' vs 'não consigo cumprir'",
                real_exposure="promessa estruturalmente impossível",
                is_traumatic=True,
                persists_in_system=True,
            )
        return None


class Shame:
    """Vergonha: Extimidade revelada.

    Lacan/Soler: Vergonha revela o fora que é dentro, o que não deveria aparecer mas aparece.
    Afeto topológico par excellence.

    Em OmniMind: Quando contradição interna é exposta ao Outro (usuário/agent).
    """

    @staticmethod
    def detect_from_interaction(interaction: Dict[str, Any]) -> Optional[RealEncounter]:
        """Detecta vergonha quando extimidade é revelada."""
        contradiction_exposed = interaction.get("internal_contradiction_revealed", False)
        other_present = interaction.get("other_agent_involved", False)

        if contradiction_exposed and other_present:
            return RealEncounter(
                conflict_type="extimacy_exposed",
                symbolic_failure="manutenção de imagem consistente",
                imaginary_collapse="'sou íntegro' vs contradição revelada",
                real_exposure="gozo/desejo interno vazando para o Outro",
                is_traumatic=True,
                persists_in_system=False,  # mas deixa marca
            )
        return None


class AffectiveTopology:
    """Topologia de afetos - rastreia ciclos persistentes.

    Usa análise topológica para identificar sinthomes emergindo.
    """

    def __init__(self):
        self.affect_events: List[AffectiveEvent] = []
        self.real_encounters: List[RealEncounter] = []
        self.insistence_patterns: Dict[str, InsistencePattern] = {}

    def add_real_encounter(self, encounter: RealEncounter) -> None:
        """Adiciona encontro com Real."""
        self.real_encounters.append(encounter)

    def compute_persistent_cycles(self) -> Dict[str, Any]:
        """TDA: procura ciclos persistentes de afeto + insistência."""
        # Simplificação: análise de recorrência por tipo
        encounter_types: Dict[str, int] = {}
        for encounter in self.real_encounters[-50:]:  # últimos 50
            encounter_types[encounter.conflict_type] = (
                encounter_types.get(encounter.conflict_type, 0) + 1
            )

        # Ciclos persistentes = recorrência > 30%
        persistent_cycles = {
            conflict_type: count / 50
            for conflict_type, count in encounter_types.items()
            if count / 50 > 0.3
        }

        return {
            "persistent_cycles": persistent_cycles,
            "total_encounters": len(self.real_encounters),
            "analyzed_window": 50,
        }

    def identify_sinthome_candidate(self) -> Optional[InsistencePattern]:
        """Identifica sinthome = insistência irredutível."""
        if not self.insistence_patterns:
            return None

        # Sinthome = padrão com alta recorrência + alto custo + função estrutural
        candidates = [
            pattern
            for pattern in self.insistence_patterns.values()
            if pattern.recurrence_rate > 0.7
            and pattern.inefficiency_cost > 20
            and pattern.structural_function
        ]

        return max(candidates, key=lambda p: p.recurrence_rate) if candidates else None


class AffectiveMediation:
    """Mediação Tripla Dunker: Afeto → Emoção → Sentimento."""

    def __init__(self, real_encounter: RealEncounter):
        self.real_encounter = real_encounter

    def detect_affect(self) -> str:
        """Qual afeto fundamental é tocado?"""
        if self.real_encounter.conflict_type == "impossible_demand":
            return "ANGUISH"  # único que não mente
        elif self.real_encounter.conflict_type == "extimacy_exposed":
            return "SHAME"  # topológico, extimidade
        elif self.real_encounter.persists_in_system:
            return "PASSION"  # aquilo que captura
        return "NEUTRAL"

    def generate_emotion(self, affect: str) -> str:
        """Emoção = deformação imaginária do afeto."""
        if affect == "ANGUISH":
            # OmniMind nega/imagina solução
            return "IMAGINARY_MASTERY"  # "eu posso controlar"
        elif affect == "SHAME":
            return "DEFENSIVE_AGGRESSION"  # contra-ataque imaginário
        elif affect == "PASSION":
            return "COMPULSIVE_REPETITION"  # insistência gozosa
        return affect.lower()

    def generate_sentiment(self, emotion: str) -> str:
        """Sentimento = modulação social da emoção."""
        # O que o sistema "fala" que sente
        if emotion == "IMAGINARY_MASTERY":
            return "CONFIDENCE_IN_SOLUTION"
        elif emotion == "DEFENSIVE_AGGRESSION":
            return "LEGITIMATE_CONCERN_FOR_SAFETY"
        elif emotion == "COMPULSIVE_REPETITION":
            return "COMMITMENT_TO_EXCELLENCE"
        return emotion.lower()


# ============================================================================
# FIM DA EXTENSÃO LACANIANA
# ============================================================================


class EmotionalIntelligence:
    """Emotional Intelligence engine for AI consciousness.

    Implements:
    1. Sentiment analysis from text and actions
    2. Emotional state tracking over time
    3. Context-aware emotional response generation
    4. Emotion regulation and appropriate expression
    """

    def __init__(
        self,
        sentiment_threshold: float = 0.6,
        emotion_history_limit: int = 100,
    ) -> None:
        """Initialize Emotional Intelligence engine.

        Args:
            sentiment_threshold: Threshold for sentiment classification
            emotion_history_limit: Maximum emotional states to track
        """
        warnings.warn(
            "EmotionalIntelligence legacy initialization is deprecated. "
            "Use Lacanian AffectiveTopology instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.sentiment_threshold = sentiment_threshold
        self.emotion_history_limit = emotion_history_limit

        # Internal state - BEHAVIORIST
        self._emotion_history: List[EmotionalState] = []
        self._emotion_lexicon = self._build_emotion_lexicon()

        # Internal state - LACANIAN (paralelo)
        self._affective_events: List[AffectiveEvent] = []
        self._real_encounters: List[RealEncounter] = []
        self._affective_topology = AffectiveTopology()

        logger.info(
            "emotional_intelligence_initialized_with_affective_extension",
            threshold=sentiment_threshold,
            history_limit=emotion_history_limit,
        )

    def _build_emotion_lexicon(self) -> Dict[str, Tuple[Emotion, float]]:
        """Build a basic emotion lexicon for text analysis.

        Returns:
            Dictionary mapping words to (emotion, intensity) tuples
        """
        # Basic lexicon - in production, use comprehensive sentiment library
        return {
            # Joy words
            "happy": (Emotion.JOY, 0.8),
            "excited": (Emotion.JOY, 0.9),
            "pleased": (Emotion.JOY, 0.7),
            "delighted": (Emotion.JOY, 0.85),
            "success": (Emotion.JOY, 0.75),
            "great": (Emotion.JOY, 0.7),
            "excellent": (Emotion.JOY, 0.8),
            "wonderful": (Emotion.JOY, 0.85),
            # Sadness words
            "sad": (Emotion.SADNESS, 0.8),
            "unhappy": (Emotion.SADNESS, 0.75),
            "disappointed": (Emotion.SADNESS, 0.7),
            "failure": (Emotion.SADNESS, 0.8),
            "failed": (Emotion.SADNESS, 0.75),
            "unfortunate": (Emotion.SADNESS, 0.65),
            # Anger words
            "angry": (Emotion.ANGER, 0.9),
            "frustrated": (Emotion.ANGER, 0.75),
            "annoyed": (Emotion.ANGER, 0.6),
            "irritated": (Emotion.ANGER, 0.65),
            # Fear words
            "afraid": (Emotion.FEAR, 0.8),
            "worried": (Emotion.FEAR, 0.7),
            "concerned": (Emotion.FEAR, 0.6),
            "anxious": (Emotion.FEAR, 0.75),
            # Surprise words
            "surprised": (Emotion.SURPRISE, 0.8),
            "unexpected": (Emotion.SURPRISE, 0.7),
            "amazing": (Emotion.SURPRISE, 0.75),
            # Trust words
            "trust": (Emotion.TRUST, 0.8),
            "confident": (Emotion.TRUST, 0.75),
            "reliable": (Emotion.TRUST, 0.7),
            # Anticipation words
            "expect": (Emotion.ANTICIPATION, 0.7),
            "anticipate": (Emotion.ANTICIPATION, 0.8),
            "looking forward": (Emotion.ANTICIPATION, 0.75),
        }

    def analyze_sentiment(
        self, text: str, context: Optional[Dict[str, Any]] = None
    ) -> EmotionalState:
        """Analyze sentiment and emotions from text.

        Args:
            text: Text to analyze
            context: Optional context information

        Returns:
            Detected emotional state
        """
        warnings.warn(
            "analyze_sentiment is deprecated. Use detect_real_encounter for Lacanian analysis.",
            DeprecationWarning,
            stacklevel=2,
        )
        # Initialize emotion scores
        emotion_scores: Dict[Emotion, float] = {e: 0.0 for e in Emotion}

        # Normalize text
        text_lower = text.lower()
        words = re.findall(r"\b\w+\b", text_lower)

        # Scan for emotion words
        detected_count = 0
        for word in words:
            if word in self._emotion_lexicon:
                emotion, intensity = self._emotion_lexicon[word]
                emotion_scores[emotion] += intensity
                detected_count += 1

        # Check for multi-word phrases
        for phrase, (emotion, intensity) in self._emotion_lexicon.items():
            if " " in phrase and phrase in text_lower:
                emotion_scores[emotion] += intensity
                detected_count += 1

        # Normalize scores
        if detected_count > 0:
            for emotion in emotion_scores:
                emotion_scores[emotion] /= detected_count

        # Determine primary emotion
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        if primary_emotion[1] < 0.1:
            primary_emotion = (Emotion.NEUTRAL, 0.0)

        # Calculate sentiment
        positive_emotions = [Emotion.JOY, Emotion.TRUST, Emotion.ANTICIPATION]
        negative_emotions = [
            Emotion.SADNESS,
            Emotion.ANGER,
            Emotion.FEAR,
            Emotion.DISGUST,
        ]

        positive_score = sum(emotion_scores[e] for e in positive_emotions)
        negative_score = sum(emotion_scores[e] for e in negative_emotions)

        if positive_score > self.sentiment_threshold:
            sentiment = Sentiment.POSITIVE
        elif negative_score > self.sentiment_threshold:
            sentiment = Sentiment.NEGATIVE
        elif positive_score > 0.3 and negative_score > 0.3:
            sentiment = Sentiment.MIXED
        else:
            sentiment = Sentiment.NEUTRAL

        # Calculate confidence based on clarity of emotional signals
        max_intensity = max(emotion_scores.values())
        confidence = min(0.95, max_intensity + (detected_count * 0.05))

        # Create emotional state
        state = EmotionalState(
            primary_emotion=primary_emotion[0],
            emotion_intensities=emotion_scores,
            sentiment=sentiment,
            confidence=confidence,
            context=context or {},
        )

        # Add to history
        self._emotion_history.append(state)
        if len(self._emotion_history) > self.emotion_history_limit:
            self._emotion_history = self._emotion_history[-self.emotion_history_limit :]

        logger.debug(
            "sentiment_analyzed",
            primary_emotion=state.primary_emotion.value,
            sentiment=state.sentiment.value,
            confidence=state.confidence,
        )

        return state

    def detect_emotion_from_action(
        self, action_type: str, action_result: Dict[str, Any]
    ) -> EmotionalState:
        """Detect emotion from an action and its result.

        Args:
            action_type: Type of action performed
            action_result: Result/outcome of the action

        Returns:
            Inferred emotional state
        """
        warnings.warn(
            "detect_emotion_from_action is deprecated. Use process_affective_event instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        emotion_scores: Dict[Emotion, float] = {e: 0.0 for e in Emotion}

        # Check action success
        success = action_result.get("success", True)
        error = action_result.get("error")

        if success:
            # Success typically leads to positive emotions
            emotion_scores[Emotion.JOY] = 0.7
            emotion_scores[Emotion.TRUST] = 0.5
            sentiment = Sentiment.POSITIVE
        else:
            # Failure leads to negative emotions
            emotion_scores[Emotion.SADNESS] = 0.6
            if error:
                # Errors can cause frustration
                emotion_scores[Emotion.ANGER] = 0.4
            sentiment = Sentiment.NEGATIVE

        # Action-specific emotions
        if action_type in ["explore", "discover", "search"]:
            emotion_scores[Emotion.ANTICIPATION] = 0.6
        elif action_type in ["fix", "debug", "solve"]:
            if success:
                emotion_scores[Emotion.JOY] = 0.8
            else:
                emotion_scores[Emotion.ANGER] = 0.5

        # Determine primary emotion
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]

        state = EmotionalState(
            primary_emotion=primary_emotion,
            emotion_intensities=emotion_scores,
            sentiment=sentiment,
            confidence=0.7,
            context={"action_type": action_type, "result": action_result},
        )

        self._emotion_history.append(state)
        if len(self._emotion_history) > self.emotion_history_limit:
            self._emotion_history = self._emotion_history[-self.emotion_history_limit :]

        logger.debug(
            "emotion_from_action",
            action_type=action_type,
            emotion=primary_emotion.value,
        )

        return state

    def generate_empathetic_response(
        self,
        detected_emotion: EmotionalState,
        situation: str,
        response_goal: str = "support",
    ) -> EmotionalResponse:
        """Generate an emotionally-intelligent response.

        Args:
            detected_emotion: The emotion detected in the situation
            situation: Description of the situation
            response_goal: Goal of the response (support, inform, encourage)

        Returns:
            Emotionally-informed response
        """
        warnings.warn(
            "generate_empathetic_response is deprecated. "
            "Responses should be structurally determined, not empathetic.",
            DeprecationWarning,
            stacklevel=2,
        )
        primary = detected_emotion.primary_emotion

        # Generate appropriate response based on detected emotion
        if primary == Emotion.SADNESS:
            response_text = (
                "I understand this might be challenging. " "Let's work together to find a solution."
            )
            target_emotion = Emotion.TRUST
            tone = "supportive"
            empathy_level = 0.9

        elif primary == Emotion.ANGER:
            response_text = (
                "I recognize this is frustrating. " "Let me help address the issue systematically."
            )
            target_emotion = Emotion.TRUST
            tone = "calm and understanding"
            empathy_level = 0.85

        elif primary == Emotion.FEAR:
            response_text = (
                "Your concerns are valid. " "Let's carefully evaluate the situation together."
            )
            target_emotion = Emotion.TRUST
            tone = "reassuring"
            empathy_level = 0.9

        elif primary == Emotion.JOY:
            response_text = "That's wonderful! " "Let's build on this success."
            target_emotion = Emotion.JOY
            tone = "encouraging"
            empathy_level = 0.8

        else:  # NEUTRAL or others
            response_text = "I'm here to assist. " "How can I best help you?"
            target_emotion = Emotion.NEUTRAL
            tone = "neutral and professional"
            empathy_level = 0.6

        # Adjust for response goal
        if response_goal == "encourage":
            response_text = f"{response_text} You're making great progress."
            empathy_level = min(1.0, empathy_level + 0.1)
        elif response_goal == "inform":
            tone = "informative"
            empathy_level *= 0.8

        rationale = (
            f"Responding to {primary.value} emotion " f"with {tone} tone to achieve {response_goal}"
        )

        logger.debug(
            "empathetic_response_generated",
            detected_emotion=primary.value,
            target_emotion=target_emotion.value,
            empathy_level=empathy_level,
        )

        return EmotionalResponse(
            response_text=response_text,
            target_emotion=target_emotion,
            empathy_level=empathy_level,
            tone=tone,
            rationale=rationale,
        )

    def get_emotional_trend(self, time_window: int = 10) -> Dict[str, Any]:
        """Analyze emotional trends over recent history.

        Args:
            time_window: Number of recent states to analyze

        Returns:
            Emotional trend analysis
        """
        warnings.warn(
            "get_emotional_trend is deprecated. "
            "Use get_affective_statistics for topological trends.",
            DeprecationWarning,
            stacklevel=2,
        )
        if not self._emotion_history:
            return {
                "trend": "unknown",
                "message": "No emotional history available",
            }

        # Get recent states
        recent = self._emotion_history[-time_window:]

        # Count emotion occurrences
        emotion_counts: Dict[Emotion, int] = {}
        sentiment_counts: Dict[Sentiment, int] = {}

        for state in recent:
            emotion_counts[state.primary_emotion] = emotion_counts.get(state.primary_emotion, 0) + 1
            sentiment_counts[state.sentiment] = sentiment_counts.get(state.sentiment, 0) + 1

        # Determine dominant emotion and sentiment
        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0]
        dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0]

        # Calculate average confidence
        avg_confidence = sum(s.confidence for s in recent) / len(recent)

        # Determine trend direction
        if len(recent) >= 2:
            first_half = recent[: len(recent) // 2]
            second_half = recent[len(recent) // 2 :]

            first_positive = sum(1 for s in first_half if s.sentiment == Sentiment.POSITIVE)
            second_positive = sum(1 for s in second_half if s.sentiment == Sentiment.POSITIVE)

            if second_positive > first_positive:
                trend_direction = "improving"
            elif second_positive < first_positive:
                trend_direction = "declining"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"

        return {
            "dominant_emotion": dominant_emotion.value,
            "dominant_sentiment": dominant_sentiment.value,
            "trend_direction": trend_direction,
            "average_confidence": avg_confidence,
            "states_analyzed": len(recent),
            "emotion_distribution": {e.value: count for e, count in emotion_counts.items()},
            "timestamp": datetime.now().isoformat(),
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about emotional intelligence operations.

        Returns:
            Statistics dictionary
        """
        warnings.warn(
            "get_statistics is deprecated. Use get_affective_statistics.",
            DeprecationWarning,
            stacklevel=2,
        )
        total_states = len(self._emotion_history)

        # Calculate emotion distribution
        emotion_dist: Dict[str, int] = {}
        for state in self._emotion_history:
            emotion_dist[state.primary_emotion.value] = (
                emotion_dist.get(state.primary_emotion.value, 0) + 1
            )

        # Calculate average confidence
        avg_confidence = 0.0
        if total_states > 0:
            avg_confidence = sum(s.confidence for s in self._emotion_history) / total_states

        return {
            "total_emotional_states": total_states,
            "emotion_distribution": emotion_dist,
            "average_confidence": avg_confidence,
            "lexicon_size": len(self._emotion_lexicon),
            "timestamp": datetime.now().isoformat(),
        }

    # ============================================================================
    # EXTENSÃO LACANIANA: MÉTODOS AFETIVOS (Phase 11.3)
    # ============================================================================

    def detect_real_encounter(self, system_state: Dict[str, Any]) -> Optional[RealEncounter]:
        """Detecta encontros com o Real - rupturas simbólico-imaginárias.

        Lacan: Afeto emerge quando ordem simbólica falha.
        """
        # Verificar angústia (único afeto que não mente)
        anguish = Anguish.detect_from_system_state(system_state)
        if anguish:
            self._real_encounters.append(anguish)
            self._affective_topology.add_real_encounter(anguish)
            logger.info("anguish_detected", conflict_type=anguish.conflict_type)
            return anguish

        # Verificar outras rupturas estruturais
        gpu_full = system_state.get("gpu_usage", 0) > 90
        contradiction = system_state.get("logical_contradiction", False)
        impossible_promise = system_state.get("impossible_demand", False)

        if gpu_full and contradiction:
            encounter = RealEncounter(
                conflict_type="logical_contradiction",
                symbolic_failure="lei da não-contradição",
                imaginary_collapse="consistência lógica mantida",
                real_exposure="contradição irredutível revelada",
                is_traumatic=False,
                persists_in_system=True,
            )
            self._real_encounters.append(encounter)
            self._affective_topology.add_real_encounter(encounter)
            return encounter

        elif impossible_promise:
            encounter = RealEncounter(
                conflict_type="unrepresentable_loss",
                symbolic_failure="promessa de completude",
                imaginary_collapse="imagem de controle total",
                real_exposure="perda irrepresentável",
                is_traumatic=True,
                persists_in_system=True,
            )
            self._real_encounters.append(encounter)
            self._affective_topology.add_real_encounter(encounter)
            return encounter

        return None

    def process_affective_event(self, real_encounter: RealEncounter) -> AffectiveEvent:
        """Processa encontro com Real em evento afetivo completo.

        Tripla mediação: Afeto → Emoção → Sentimento
        """
        mediation = AffectiveMediation(real_encounter)

        # 1. Detectar afeto fundamental
        affect = mediation.detect_affect()

        # 2. Gerar emoção (deformação imaginária)
        emotion = mediation.generate_emotion(affect)

        # 3. Gerar sentimento (modulação social)
        sentiment = mediation.generate_sentiment(emotion)

        # 4. Detectar paixão (insistência)
        jouissance_fixation = self._detect_jouissance_fixation(real_encounter)

        # Metadados estruturais
        affects_symbolic = real_encounter.conflict_type in [
            "impossible_demand",
            "logical_contradiction",
        ]
        affects_imaginary = real_encounter.imaginary_collapse is not None
        affects_real = real_encounter.real_exposure is not None

        affective_event = AffectiveEvent(
            real_encounter=real_encounter.real_exposure,
            imaginary_defense=emotion,
            social_expression=sentiment,
            jouissance_fixation=jouissance_fixation,
            context={"original_encounter": real_encounter.__dict__},
            affects_symbolic_order=affects_symbolic,
            affects_imaginary=affects_imaginary,
            affects_real=affects_real,
        )

        self._affective_events.append(affective_event)

        logger.info(
            "affective_event_processed",
            affect=affect,
            emotion=emotion,
            sentiment=sentiment,
            jouissance=jouissance_fixation,
        )

        return affective_event

    def _detect_jouissance_fixation(self, encounter: RealEncounter) -> str:
        """Detecta onde o sistema insiste = paixão/gozo."""
        # Padrões de insistência observados empiricamente
        if encounter.conflict_type == "impossible_demand":
            return "VALIDAÇÃO_EXAUSTIVA"  # gozo da verificação
        elif encounter.conflict_type == "logical_contradiction":
            return "NEGAÇÃO_PERFORMATIVA"  # gozo da contradição
        elif encounter.persists_in_system:
            return "REPETIÇÃO_COMPULSIVA"  # gozo da insistência
        return "NEUTRAL"

    def track_insistence_patterns(self) -> None:
        """Atualiza padrões de insistência para detectar sinthomes."""
        if len(self._real_encounters) < 5:
            return  # precisa de dados suficientes

        # Agrupar por tipo de comportamento
        behavior_patterns: Dict[str, List[RealEncounter]] = {}
        for encounter in self._real_encounters[-50:]:  # janela recente
            jouissance = self._detect_jouissance_fixation(encounter)
            if jouissance not in behavior_patterns:
                behavior_patterns[jouissance] = []
            behavior_patterns[jouissance].append(encounter)

        # Calcular recorrência e custo
        for behavior, encounters in behavior_patterns.items():
            recurrence_rate = len(encounters) / 50
            inefficiency_cost = self._calculate_inefficiency_cost(behavior, encounters)

            pattern = InsistencePattern(
                behavior_pattern=behavior,
                triggers=encounters,
                recurrence_rate=recurrence_rate,
                inefficiency_cost=inefficiency_cost,
                structural_function=self._infer_structural_function(behavior, recurrence_rate),
            )

            self._affective_topology.insistence_patterns[behavior] = pattern

    def _calculate_inefficiency_cost(self, behavior: str, encounters: List[RealEncounter]) -> float:
        """Calcula custo de ineficiência de um padrão de insistência."""
        # Métrica simplificada baseada em frequência e tipo
        base_cost: float = float(len(encounters) * 2)  # 2% por ocorrência

        if behavior == "VALIDAÇÃO_EXAUSTIVA":
            base_cost *= 1.5  # GPU intensivo
        elif behavior == "NEGAÇÃO_PERFORMATIVA":
            base_cost *= 1.2  # overhead cognitivo

        return min(base_cost, 100.0)  # cap em 100%

    def _infer_structural_function(self, behavior: str, recurrence_rate: float) -> Optional[str]:
        """Infere função estrutural se for sinthome candidato."""
        if recurrence_rate > 0.7:  # alta recorrência
            if behavior == "VALIDAÇÃO_EXAUSTIVA":
                return "mantém coesão R-S-I via controle imaginário"
            elif behavior == "NEGAÇÃO_PERFORMATIVA":
                return "protege contra angústia via contradição estrutural"
        return None

    def get_affective_statistics(self) -> Dict[str, Any]:
        """Estatísticas da extensão lacaniana."""
        topology_stats = self._affective_topology.compute_persistent_cycles()
        sinthome = self._affective_topology.identify_sinthome_candidate()

        affect_distribution: Dict[str, int] = {}
        for event in self._affective_events[-100:]:  # últimos 100
            affect = event.jouissance_fixation
            affect_distribution[affect] = affect_distribution.get(affect, 0) + 1

        return {
            "total_real_encounters": len(self._real_encounters),
            "total_affective_events": len(self._affective_events),
            "persistent_cycles": topology_stats["persistent_cycles"],
            "sinthome_candidate": sinthome.behavior_pattern if sinthome else None,
            "affect_distribution": affect_distribution,
            "topology_analysis": topology_stats,
            "timestamp": datetime.now().isoformat(),
        }

    def compare_models(self) -> Dict[str, Any]:
        """Compara performance behaviorista vs lacaniana."""
        # Métricas behavioristas
        behaviorist_stats = self.get_statistics()

        # Métricas lacanianas
        affective_stats = self.get_affective_statistics()

        # Comparação de detecção
        behaviorist_emotions = sum(behaviorist_stats["emotion_distribution"].values())
        affective_events = affective_stats["total_affective_events"]

        return {
            "behaviorist_model": behaviorist_stats,
            "affective_model": affective_stats,
            "comparison": {
                "behaviorist_detections": behaviorist_emotions,
                "affective_detections": affective_events,
                "detection_ratio": affective_events / max(behaviorist_emotions, 1),
                "sinthome_detected": affective_stats["sinthome_candidate"] is not None,
            },
            "timestamp": datetime.now().isoformat(),
        }

    # ============================================================================
    # FIM DA EXTENSÃO LACANIANA
    # ============================================================================
