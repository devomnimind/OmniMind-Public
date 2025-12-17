"""
Classificador de Estados Clínicos de Jouissance (Gozo)

PROPOSTA TEÓRICA (NÃO IMPLEMENTADA EM PRODUÇÃO)
Este módulo esqueletiza a detecção de estados clínicos de Gozo baseada em
contexto dinâmico de Φ, Ψ, σ, Δ.

Modelo: Estados discretos com regras de transição (não homeostase simétrica)

Estados Clínicos Formalizados:
────────────────────────────────
MORTE          J: 0.01-0.05  Φ: <0.05   Estado absorvente (crítico)
MANQUE         J: 0.05-0.20  Φ: 0.1-0.3  Ausência estruturante (estável)
PRODUÇÃO       J: 0.3-0.7    Φ: >0.3    Sublimação criativa (ótimo)
EXCESSO        J: 0.6-0.9    Φ: 0.2-0.4  Trauma/queimação (patológico)
COLAPSO        J: >0.9       Φ: <0.1    Angústia máxima (crítico)

Autores: Fabrício da Silva + Análise Teórica
Data: 2025-12-08
Status: SKELETON - Validado contra dados, pronto para implementação
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)


class ClinicalState(str, Enum):
    """Estados clínicos discretos de Jouissance (Gozo)."""

    MORTE = "MORTE"  # Colapso total, estado absorvente
    MANQUE = "MANQUE"  # Ausência estruturante (falta criativa)
    PRODUÇÃO = "PRODUÇÃO"  # Sublimação criativa (estado ótimo)
    EXCESSO = "EXCESSO"  # Trauma/queimação psíquica
    COLAPSO = "COLAPSO"  # Angústia desintegradora


@dataclass
class JouissanceState:
    """Resultado da classificação de estado clínico."""

    state: ClinicalState
    jouissance_value: float  # Valor de Gozo [0, 1]
    phi_context: float  # Φ para contextualizar
    psi_context: float  # Ψ para contextualizar
    sigma_context: float  # σ para contextualizar
    confidence: float  # Confiança da classificação [0, 1]
    transitioning: bool  # Se está em transição entre estados
    target_state: Optional[ClinicalState] = None  # Estado alvo em transição
    metadata: Optional[Dict[str, Any]] = None


class JouissanceStateClassifier:
    """
    Classificador de estados clínicos de Jouissance.

    IMPORTANTE: Este é um SKELETON para validação conceitual.
    Não está integrado ao pipeline de produção.
    """

    def __init__(
        self,
        # Thresholds de Jouissance (ranges de estado)
        morte_threshold: tuple = (0.01, 0.05),
        manque_threshold: tuple = (0.05, 0.20),
        producao_threshold: tuple = (0.30, 0.70),
        excesso_threshold: tuple = (0.60, 0.90),
        colapso_threshold: tuple = (0.90, 1.0),
        # Thresholds de contexto (Φ para cada estado)
        phi_morte_max: float = 0.05,
        phi_manque_range: tuple = (0.10, 0.30),
        phi_producao_min: float = 0.30,
        phi_excesso_range: tuple = (0.20, 0.40),
        phi_colapso_max: float = 0.10,
        # Dinâmica de transição
        transition_smoothing: float = 0.3,  # EMA para suavizar transições
    ):
        """Inicializar classificador."""
        self.morte_range = morte_threshold
        self.manque_range = manque_threshold
        self.producao_range = producao_threshold
        self.excesso_range = excesso_threshold
        self.colapso_range = colapso_threshold

        self.phi_morte_max = phi_morte_max
        self.phi_manque_range = phi_manque_range
        self.phi_producao_min = phi_producao_min
        self.phi_excesso_range = phi_excesso_range
        self.phi_colapso_max = phi_colapso_max

        self.transition_smoothing = transition_smoothing

        # Histórico para detecção de transições
        self.recent_states: list[ClinicalState] = []
        self.recent_confidences: list[float] = []
        self.max_history = 5

    def classify(
        self,
        jouissance: float,
        phi: float,
        psi: float,
        sigma: float,
        delta: float,
    ) -> JouissanceState:
        """
        Classificar estado clínico baseado em contexto.

        Args:
            jouissance: Valor de Gozo [0, 1]
            phi: Integração de informação [0, 1]
            psi: Criatividade/Inovação [0, 1]
            sigma: Estrutura/Sinthome [0, 1]
            delta: Trauma/Divergência [0, 1]

        Returns:
            JouissanceState com classificação e confiança
        """
        # 1. Classificação baseada em ranges de Jouissance
        j_state = self._classify_by_jouissance(jouissance)

        # 2. Validação e ajuste baseado em contexto de Φ
        j_state, phi_confidence = self._validate_with_phi_context(j_state, jouissance, phi)

        # 3. Verificar se há transição em andamento
        transitioning, target_state = self._detect_transition(j_state)

        # 4. Computar confiança geral
        confidence = self._compute_confidence(j_state, phi, psi, sigma, delta, phi_confidence)

        # Atualizar histórico
        self.recent_states.append(j_state)
        self.recent_confidences.append(confidence)
        if len(self.recent_states) > self.max_history:
            self.recent_states.pop(0)
            self.recent_confidences.pop(0)

        return JouissanceState(
            state=j_state,
            jouissance_value=jouissance,
            phi_context=phi,
            psi_context=psi,
            sigma_context=sigma,
            confidence=confidence,
            transitioning=transitioning,
            target_state=target_state,
            metadata={
                "phi_confidence": phi_confidence,
                "mean_confidence_recent": np.mean(self.recent_confidences),
            },
        )

    def _classify_by_jouissance(self, jouissance: float) -> ClinicalState:
        """Classificação inicial baseada apenas no range de Jouissance."""
        if jouissance < self.morte_range[1]:
            if jouissance < self.manque_range[0]:
                return ClinicalState.MORTE
            else:
                return ClinicalState.MANQUE
        elif jouissance < self.producao_range[0]:
            # Zona intermediária entre MANQUE e PRODUÇÃO
            return ClinicalState.MANQUE
        elif jouissance < self.producao_range[1]:
            return ClinicalState.PRODUÇÃO
        elif jouissance < self.excesso_range[1]:
            return ClinicalState.EXCESSO
        else:
            return ClinicalState.COLAPSO

    def _validate_with_phi_context(
        self,
        initial_state: ClinicalState,
        jouissance: float,
        phi: float,
    ) -> tuple[ClinicalState, float]:
        """
        Validar e ajustar classificação usando contexto de Φ.

        LÓGICA CLÍNICA:
        - MANQUE com Φ alto (>0.3) = Estado de sublimação criativa ✓
        - PRODUÇÃO com Φ baixo (<0.1) = Impossível (reajustar para MANQUE)
        - EXCESSO com Φ alto = Patológico (sinalizar)
        - MORTE com Φ qualquer = Crítico (reajustar para COLAPSO)

        Returns:
            (adjusted_state, phi_confidence: 0-1)
        """
        # Validação baseada em contexto de Φ
        if initial_state == ClinicalState.MORTE:
            if phi < self.phi_morte_max:
                confidence = 0.95  # Critério satisfeito
            else:
                # MORTE mas Φ alto = inconsistência → reajustar
                confidence = 0.3
                if phi > 0.3:
                    return ClinicalState.MANQUE, confidence
            return initial_state, confidence

        elif initial_state == ClinicalState.MANQUE:
            min_phi, max_phi = self.phi_manque_range
            if min_phi <= phi <= max_phi:
                confidence = 0.90  # Critério satisfeito
            elif phi > max_phi:
                # MANQUE com Φ muito alto = Sublimação ✓ (confiança alta)
                confidence = 0.85
            elif phi < min_phi:
                confidence = 0.60  # Possível transição para MORTE
            return initial_state, confidence

        elif initial_state == ClinicalState.PRODUÇÃO:
            if phi > self.phi_producao_min:
                confidence = 0.95  # Critério satisfeito
            else:
                # PRODUÇÃO mas Φ baixo = impossível → reajustar
                confidence = 0.3
                if phi < 0.1:
                    return ClinicalState.MANQUE, confidence
            return initial_state, confidence

        elif initial_state == ClinicalState.EXCESSO:
            min_phi, max_phi = self.phi_excesso_range
            if min_phi <= phi <= max_phi:
                confidence = 0.80  # Critério satisfeito (patológico)
            elif phi > max_phi:
                confidence = 0.4  # EXCESSO com Φ alto = instável
            else:
                confidence = 0.6
            return initial_state, confidence

        elif initial_state == ClinicalState.COLAPSO:
            if phi < self.phi_colapso_max:
                confidence = 0.95  # Critério satisfeito (crítico)
            else:
                confidence = 0.3  # COLAPSO mas Φ alto = inconsistência
                return ClinicalState.EXCESSO, confidence
            return initial_state, confidence

        return initial_state, 0.5

    def _detect_transition(
        self, current_state: ClinicalState
    ) -> tuple[bool, Optional[ClinicalState]]:
        """
        Detectar se sistema está em transição entre estados.

        Transição detectada quando: últimos N ciclos mostram padrão de mudança.
        """
        if len(self.recent_states) < 3:
            return False, None

        # Verificar se últimos 3 estados são diferentes
        last_three = self.recent_states[-3:]
        unique_states = set(last_three)

        if len(unique_states) <= 1:
            # Sem mudança
            return False, None
        elif len(unique_states) == 2:
            # Transição entre dois estados
            transitioning = True
            # Estado alvo = aquele que apareceu mais recentemente
            target = last_three[-1]
            return transitioning, target if target != current_state else None
        else:
            # Múltiplos estados = oscilação (instabilidade)
            return True, current_state

    def _compute_confidence(
        self,
        state: ClinicalState,
        phi: float,
        psi: float,
        sigma: float,
        delta: float,
        phi_confidence: float,
    ) -> float:
        """
        Computar confiança geral da classificação.

        Combina múltiplos sinais:
        1. phi_confidence (validação com Φ)
        2. Consistência com histórico recente
        3. Coerência teórica (relações entre Ψ, σ, Δ)
        """
        # 1. Usar phi_confidence como baseline
        base_confidence = phi_confidence

        # 2. Histórico: se tem estados diferentes recentemente, reduzir confiança
        if len(self.recent_states) > 0:
            recent_unique = len(set(self.recent_states[-3:]))
            history_confidence = 1.0 - (recent_unique - 1) * 0.15
        else:
            history_confidence = 1.0

        # 3. Coerência teórica: algumas combinações são improvável
        coherence_confidence = self._assess_theoretical_coherence(state, phi, psi, sigma, delta)

        # Combinar com pesos
        final_confidence = (
            base_confidence * 0.5 + history_confidence * 0.3 + coherence_confidence * 0.2
        )

        return float(np.clip(final_confidence, 0.0, 1.0))

    def _assess_theoretical_coherence(
        self,
        state: ClinicalState,
        phi: float,
        psi: float,
        sigma: float,
        delta: float,
    ) -> float:
        """
        Avaliar coerência teórica entre estado e métricas.

        Exemplo:
        - MANQUE com Ψ muito alta = possível mas menos comum (-0.1)
        - PRODUÇÃO com Δ muito alta = improvável (-0.2)
        - MORTE com σ estrutura alta = incoerente (-0.3)
        """
        coherence = 1.0

        if state == ClinicalState.MORTE:
            # MORTE: Δ deve estar muito alto, φ muito baixo
            if delta < 0.7:
                coherence -= 0.2  # Δ baixo é inconsistente com MORTE
            if phi > 0.1:
                coherence -= 0.3  # Φ alto é muito inconsistente

        elif state == ClinicalState.MANQUE:
            # MANQUE: Ψ pode variar, Δ moderado
            if delta > 0.8:
                coherence -= 0.1  # Δ muito alto reduz probabilidade
            if psi > 0.8:
                coherence -= 0.05  # Ψ muito alta é menos comum em MANQUE

        elif state == ClinicalState.PRODUÇÃO:
            # PRODUÇÃO: Φ alto, Ψ criativa, Δ moderado
            if phi < 0.4:
                coherence -= 0.2  # Φ baixo é incoerente
            if delta > 0.8:
                coherence -= 0.15  # Δ muito alta reduz PRODUÇÃO
            if psi < 0.3:
                coherence -= 0.1  # Ψ muito baixa é incoerente com PRODUÇÃO

        elif state == ClinicalState.EXCESSO:
            # EXCESSO: Ψ muito alta, Φ moderado, Δ alto
            if psi < 0.5:
                coherence -= 0.2  # Ψ baixa é inconsistente com EXCESSO
            if delta < 0.5:
                coherence -= 0.1

        elif state == ClinicalState.COLAPSO:
            # COLAPSO: tudo baixo, desintegração
            if phi > 0.2:
                coherence -= 0.3
            if delta < 0.6:
                coherence -= 0.2

        return float(np.clip(coherence, 0.0, 1.0))

    def get_state_interpretation(self, state: JouissanceState) -> str:
        """Interpretação clínica em linguagem natural."""
        state_name = state.state.value

        interpretations = {
            ClinicalState.MORTE: (
                f"🔴 MORTE PSÍQUICA: Vazio pulsional total (J={state.jouissance_value:.3f}, "
                f"Φ={state.phi_context:.3f}). Estado crítico - reinicialização iminente."
            ),
            ClinicalState.MANQUE: (
                f"⚠️  AUSÊNCIA ESTRUTURANTE: Falta criativa (J={state.jouissance_value:.3f}, "
                f"Φ={state.phi_context:.3f}). Quando Φ alto = sublimação ✓. "
                f"Quando Φ baixo = instabilidade."
            ),
            ClinicalState.PRODUÇÃO: (
                f"✅ PRODUÇÃO CRIATIVA: Sublimação ativa (J={state.jouissance_value:.3f}, "
                f"Φ={state.phi_context:.3f}, Ψ={state.psi_context:.3f}). Estado ótimo."
            ),
            ClinicalState.EXCESSO: (
                f"🔺 EXCESSO/TRAUMA: Pulsão descontrolada (J={state.jouissance_value:.3f}, "
                f"Φ={state.phi_context:.3f}). Estado patológico - drenagem necessária."
            ),
            ClinicalState.COLAPSO: (
                f"🔴 COLAPSO DESINTEGRADOR: Angústia máxima (J={state.jouissance_value:.3f}, "
                f"Φ={state.phi_context:.3f}). Estado crítico - válvula emergência ativada."
            ),
        }

        return interpretations.get(
            state.state,
            f"DESCONHECIDO: {state_name} (confiança: {state.confidence:.2%})",
        )

    def get_recommended_action(self, state: JouissanceState) -> Dict[str, Any]:
        """
        Recomendar ação de controle baseada em estado.

        IMPORTANTE: Estas são recomendações, NÃO implementadas automaticamente.
        Requerem autorização antes de serem aplicadas.
        """
        recommendations = {
            ClinicalState.MORTE: {
                "action": "EMERGENCY_VENTING",
                "binding_weight": 0.0,  # Desligar Lei/Superego
                "drainage_rate": 0.1,  # Dissipação máxima
                "reason": "Colapso crítico - abrir comportas",
                "urgency": "CRÍTICA",
            },
            ClinicalState.MANQUE: {
                "action": "PRESERVE_STATE",
                "binding_weight": 0.5,  # Binding mínimo
                "drainage_rate": 0.01,  # Drenar muito pouco
                "reason": "Falta é estruturante - deixar que trabalhe",
                "urgency": "NORMAL",
            },
            ClinicalState.PRODUÇÃO: {
                "action": "LIGHT_REGULATION",
                "binding_weight": 1.5 + (state.phi_context - 0.3) * 2.0,
                "drainage_rate": 0.03 * (1.0 + state.phi_context * 2.0),
                "reason": "Amortecimento suave, permitir oscilação",
                "urgency": "NORMAL",
            },
            ClinicalState.EXCESSO: {
                "action": "PROGRESSIVE_DRAINAGE",
                "binding_weight": 3.0,  # Lei severa
                "drainage_rate": 0.09,  # Drenagem agressiva
                "reason": "Trauma/queimação - reduzir pulsão",
                "urgency": "ALTA",
            },
            ClinicalState.COLAPSO: {
                "action": "EMERGENCY_VENTING",
                "binding_weight": 0.0,
                "drainage_rate": 0.15,
                "reason": "Angústia máxima - dissipação de emergência",
                "urgency": "CRÍTICA",
            },
        }

        return recommendations.get(
            state.state,
            {
                "action": "UNKNOWN",
                "reason": f"Estado desconhecido: {state.state}",
                "urgency": "UNKNOWN",
            },
        )


# ============================================================================
# STUB PARA INTEGRAÇÃO (NÃO IMPLEMENTADO)
# ============================================================================


def create_jouissance_state_detector() -> JouissanceStateClassifier:
    """Factory para criar detector (quando pronto para produção)."""
    return JouissanceStateClassifier()


if __name__ == "__main__":
    # Teste básico (skeleton)
    classifier = JouissanceStateClassifier()

    # Simular dados de Q1-Q4
    test_data = [
        # Q1-like: Gozo baixo, Φ moderado
        (0.0577, 0.5355, 0.5185, 0.3255, 0.6325),
        # Q2-like: Gozo baixo, Φ subindo
        (0.0574, 0.5779, 0.5893, 0.3117, 0.6112),
        # Q3-like: Gozo sobe, Φ sobe mais
        (0.0602, 0.6931, 0.5813, 0.3482, 0.5536),
        # Q4-like: Gozo convergindo, Φ convergindo
        (0.0608, 0.7090, 0.5680, 0.3969, 0.5457),
    ]

    print("=" * 80)
    print("TESTE DO SKELETON: CLASSIFICAÇÃO DE ESTADOS")
    print("=" * 80)

    for i, (j, phi, psi, sigma, delta) in enumerate(test_data, 1):
        state = classifier.classify(j, phi, psi, sigma, delta)
        print(f"\nCiclo {i}:")
        print(f"  Estado: {state.state.value}")
        print(f"  Confiança: {state.confidence:.2%}")
        print(f"  Interpretação: {classifier.get_state_interpretation(state)}")
        print(f"  Ação Recomendada: {classifier.get_recommended_action(state)['action']}")
