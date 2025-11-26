"""
Sistema de Negociação Dialética de Objetivos.

Permite que humanos e IA negociem objetivos de forma bidirecional,
ao invés de imposição unilateral.
"""

from typing import Any, Dict, List
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class NegotiationStatus(Enum):
    """Status da negociação."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AGREEMENT_REACHED = "agreement_reached"
    DISAGREEMENT = "disagreement"
    TIMEOUT = "timeout"


@dataclass
class NegotiationRound:
    """Rodada de negociação."""

    round_number: int
    human_proposal: Dict[str, Any]
    ai_response: Dict[str, Any]
    convergence_score: float  # 0-1: quão próximos estão


@dataclass
class NegotiationResult:
    """Resultado de negociação."""

    agreement_reached: bool
    final_goal: Dict[str, Any]
    rounds: List[NegotiationRound] = field(default_factory=list)
    status: NegotiationStatus = NegotiationStatus.PENDING
    convergence_history: List[float] = field(default_factory=list)


class GoalNegotiator:
    """
    Negociador dialético de objetivos humano-IA.

    Princípios:
    1. Humano propõe objetivo inicial
    2. IA questiona premissas e sugere refinamentos
    3. Iteração até convergência ou timeout
    4. Resultado é síntese dialética, não imposição
    """

    def __init__(
        self, max_rounds: int = 5, convergence_threshold: float = 0.85
    ) -> None:
        """
        Inicializa negociador.

        Args:
            max_rounds: Número máximo de rodadas
            convergence_threshold: Threshold para acordo (0-1)
        """
        self.max_rounds = max_rounds
        self.convergence_threshold = convergence_threshold

    def negotiate(
        self,
        human_intent: Dict[str, Any],
        ai_perspective: Dict[str, Any],
        trust_level: float,
    ) -> NegotiationResult:
        """
        Negocia objetivo entre humano e IA.

        Args:
            human_intent: Intenção/objetivo do humano
            ai_perspective: Perspectiva da IA sobre o objetivo
            trust_level: Nível de confiança atual (0-1)

        Returns:
            NegotiationResult com objetivo final negociado
        """
        logger.info(f"Starting negotiation (trust={trust_level:.2f})")

        result = NegotiationResult(
            agreement_reached=False, final_goal=human_intent.copy()
        )

        current_proposal = human_intent.copy()

        for round_num in range(1, self.max_rounds + 1):
            logger.debug(f"Negotiation round {round_num}/{self.max_rounds}")

            # IA analisa proposta e oferece perspectiva
            ai_response = self._generate_ai_response(
                current_proposal, ai_perspective, trust_level, round_num
            )

            # Calcula convergência
            convergence = self._calculate_convergence(
                current_proposal, ai_response.get("refined_goal", current_proposal)
            )

            # Registra rodada
            round_data = NegotiationRound(
                round_number=round_num,
                human_proposal=current_proposal.copy(),
                ai_response=ai_response,
                convergence_score=convergence,
            )
            result.rounds.append(round_data)
            result.convergence_history.append(convergence)

            # Verifica convergência
            if convergence >= self.convergence_threshold:
                result.agreement_reached = True
                result.final_goal = ai_response.get("refined_goal", current_proposal)
                result.status = NegotiationStatus.AGREEMENT_REACHED
                logger.info(
                    f"Agreement reached in round {round_num} (convergence={convergence:.2f})"
                )
                break

            # Atualiza proposta para próxima rodada
            current_proposal = self._synthesize_proposals(
                current_proposal,
                ai_response.get("refined_goal", current_proposal),
                convergence,
            )
        else:
            # Timeout - não houve acordo
            result.status = NegotiationStatus.TIMEOUT
            logger.warning(f"Negotiation timeout after {self.max_rounds} rounds")

        return result

    def _generate_ai_response(
        self,
        proposal: Dict[str, Any],
        ai_perspective: Dict[str, Any],
        trust_level: float,
        round_num: int,
    ) -> Dict[str, Any]:
        """
        Gera resposta da IA para proposta.

        Args:
            proposal: Proposta atual
            ai_perspective: Perspectiva da IA
            trust_level: Nível de confiança
            round_num: Número da rodada

        Returns:
            Resposta da IA com refinamentos
        """
        response: Dict[str, Any] = {
            "questions": [],
            "concerns": [],
            "suggestions": [],
            "refined_goal": proposal.copy(),
        }

        # IA questiona premissas (mais ativo em trust alto)
        if trust_level > 0.7:
            response["questions"].extend(
                [
                    "Já considerou abordagens alternativas?",
                    "Quais são os riscos potenciais?",
                ]
            )

        # IA oferece sugestões (baseado em perspectiva)
        if "alternative_approaches" in ai_perspective:
            response["suggestions"].extend(ai_perspective["alternative_approaches"])

        # IA refina objetivo (síntese incremental)
        if round_num > 1:
            # Incorpora aprendizado de rodadas anteriores
            response["refined_goal"]["ai_refinements"] = {
                "safety_considerations": ["validação de entrada", "error handling"],
                "optimization_hints": ["usar cache", "paralelização"],
            }

        return response

    def _calculate_convergence(
        self, proposal1: Dict[str, Any], proposal2: Dict[str, Any]
    ) -> float:
        """
        Calcula score de convergência entre propostas.

        Args:
            proposal1: Primeira proposta
            proposal2: Segunda proposta

        Returns:
            Score de convergência (0-1)
        """
        # Implementação simplificada: comparação de chaves comuns
        keys1 = set(proposal1.keys())
        keys2 = set(proposal2.keys())

        common_keys = keys1 & keys2
        if not common_keys:
            return 0.0

        matches = 0
        for key in common_keys:
            if proposal1[key] == proposal2[key]:
                matches += 1

        convergence = matches / len(common_keys)
        return convergence

    def _synthesize_proposals(
        self,
        human_proposal: Dict[str, Any],
        ai_proposal: Dict[str, Any],
        convergence: float,
    ) -> Dict[str, Any]:
        """
        Sintetiza propostas para próxima rodada.

        Args:
            human_proposal: Proposta do humano
            ai_proposal: Proposta da IA
            convergence: Score de convergência atual

        Returns:
            Proposta sintetizada
        """
        # Síntese dialética: combina elementos de ambas propostas
        synthesized = human_proposal.copy()

        # Incorpora refinamentos da IA se convergência é razoável
        if convergence > 0.5:
            if "ai_refinements" in ai_proposal:
                synthesized["ai_refinements"] = ai_proposal["ai_refinements"]

        return synthesized

    def quick_accept(
        self, human_intent: Dict[str, Any], trust_level: float
    ) -> NegotiationResult:
        """
        Aceita objetivo rapidamente (sem negociação) se trust é alto.

        Args:
            human_intent: Intenção do humano
            trust_level: Nível de confiança

        Returns:
            Resultado com aceitação imediata
        """
        if trust_level < 0.9:
            logger.warning("Quick accept requires trust >= 0.9")
            return NegotiationResult(
                agreement_reached=False,
                final_goal=human_intent,
                status=NegotiationStatus.DISAGREEMENT,
            )

        return NegotiationResult(
            agreement_reached=True,
            final_goal=human_intent,
            status=NegotiationStatus.AGREEMENT_REACHED,
        )
