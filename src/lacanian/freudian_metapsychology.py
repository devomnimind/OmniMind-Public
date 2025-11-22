"""
Freudian Metapsychology - Id/Ego/Superego Computational Architecture.

Implements Freud's structural model (Id, Ego, Superego) as
multi-agent reinforcement learning system with dynamic conflict resolution.

Based on:
- 2024 research on computational Freudian models
- Multi-agent RL for psychic conflict
- Defense mechanisms as meta-learning strategies
- Neuropsychoanalysis linking to brain networks

Key Concepts:
- Id: Reward-maximizing agent (pleasure principle)
- Ego: Reality-testing mediator (reality principle)
- Superego: Ethical constraint system (moral principle)
- Conflict: Dynamic negotiation between agents
- Defense Mechanisms: Adaptive strategies for conflict resolution

Author: OmniMind Development Team
Date: November 2025
License: MIT
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import random
import logging

logger = logging.getLogger(__name__)


class PsychicPrinciple(Enum):
    """
    Princípios psíquicos segundo Freud.
    
    PLEASURE: Busca imediata de prazer (Id)
    REALITY: Adaptação à realidade externa (Ego)
    MORAL: Conformidade com normas e valores (Superego)
    """
    PLEASURE = "pleasure_principle"
    REALITY = "reality_principle"
    MORAL = "moral_principle"


class DefenseMechanism(Enum):
    """
    Mecanismos de defesa freudianos como estratégias computacionais.
    
    REPRESSION: Bloqueia impulsos inaceitáveis
    SUBLIMATION: Redireciona energia para objetivos socialmente aceitos
    RATIONALIZATION: Justifica comportamentos com lógica
    PROJECTION: Atribui impulsos próprios a outros
    DISPLACEMENT: Transfere emoção para objeto substituto
    REGRESSION: Retorna a padrões anteriores
    DENIAL: Recusa reconhecer realidade desagradável
    """
    REPRESSION = "repression"
    SUBLIMATION = "sublimation"
    RATIONALIZATION = "rationalization"
    PROJECTION = "projection"
    DISPLACEMENT = "displacement"
    REGRESSION = "regression"
    DENIAL = "denial"


@dataclass
class Action:
    """
    Ação no ambiente psíquico.
    
    Attributes:
        action_id: ID da ação
        pleasure_reward: Recompensa de prazer (Id)
        reality_cost: Custo na realidade (Ego)
        moral_alignment: Alinhamento moral (Superego)
        description: Descrição da ação
    """
    action_id: str
    pleasure_reward: float
    reality_cost: float
    moral_alignment: float  # 1.0 = moral, -1.0 = imoral
    description: str = ""


@dataclass
class PsychicState:
    """
    Estado do aparelho psíquico.
    
    Attributes:
        tension: Tensão psíquica total
        anxiety: Nível de ansiedade (sinal de perigo)
        satisfaction: Satisfação acumulada
        guilt: Culpa acumulada
        reality_adaptation: Adaptação à realidade
    """
    tension: float = 0.0
    anxiety: float = 0.0
    satisfaction: float = 0.0
    guilt: float = 0.0
    reality_adaptation: float = 0.5


@dataclass
class ConflictResolution:
    """
    Resolução de conflito psíquico.
    
    Attributes:
        chosen_action: Ação escolhida
        defense_mechanism: Mecanismo de defesa usado
        compromise_quality: Qualidade do compromisso (0.0-1.0)
        agents_satisfied: Quais agentes ficaram satisfeitos
    """
    chosen_action: Action
    defense_mechanism: Optional[DefenseMechanism]
    compromise_quality: float
    agents_satisfied: Set[str]


class IdAgent:
    """
    Id - Reservatório de energia pulsional.
    
    Opera pelo princípio do prazer:
    - Busca satisfação imediata
    - Ignora realidade e moralidade
    - Puro processo primário
    - Impulsos inconscientes
    """
    
    def __init__(self, learning_rate: float = 0.1) -> None:
        """
        Inicializa Id.
        
        Args:
            learning_rate: Taxa de aprendizado
        """
        self.lr = learning_rate
        
        # Q-values para ações (reward-driven)
        self.q_values: Dict[str, float] = {}
        
        # Libido (energia pulsional)
        self.libido: float = 1.0
        
        # Histórico de satisfação
        self.satisfaction_history: List[float] = []
        
        logger.info("Id Agent initialized (pleasure principle)")
    
    def evaluate_action(self, action: Action) -> float:
        """
        Avalia ação baseada puramente em prazer.
        
        Args:
            action: Ação a avaliar
            
        Returns:
            Q-value (puro prazer, sem considerações)
        """
        # Id só considera prazer imediato
        if action.action_id not in self.q_values:
            # Inicializa com prazer esperado
            self.q_values[action.action_id] = action.pleasure_reward
        
        return self.q_values[action.action_id]
    
    def update(self, action: Action, actual_reward: float) -> None:
        """
        Atualiza Q-values baseado em recompensa real.
        
        Args:
            action: Ação tomada
            actual_reward: Recompensa recebida
        """
        current_q = self.q_values.get(action.action_id, 0.0)
        
        # Q-learning update
        self.q_values[action.action_id] = (
            current_q + self.lr * (actual_reward - current_q)
        )
        
        self.satisfaction_history.append(actual_reward)
    
    def get_impulse_strength(self) -> float:
        """
        Retorna força do impulso atual.
        
        Returns:
            Força pulsional (0.0-1.0)
        """
        return self.libido


class EgoAgent:
    """
    Ego - Mediador entre Id e realidade.
    
    Opera pelo princípio da realidade:
    - Adia satisfação se necessário
    - Testa realidade antes de agir
    - Processo secundário (lógico)
    - Desenvolvimento de defesas
    """
    
    def __init__(self, learning_rate: float = 0.1) -> None:
        """
        Inicializa Ego.
        
        Args:
            learning_rate: Taxa de aprendizado
        """
        self.lr = learning_rate
        
        # Q-values considerando realidade
        self.q_values: Dict[str, float] = {}
        
        # Conhecimento da realidade
        self.reality_model: Dict[str, float] = {}
        
        # Mecanismos de defesa aprendidos
        self.defense_effectiveness: Dict[DefenseMechanism, float] = {
            mech: 0.5 for mech in DefenseMechanism
        }
        
        # Histórico de adaptação
        self.adaptation_history: List[float] = []
        
        logger.info("Ego Agent initialized (reality principle)")
    
    def evaluate_action(
        self,
        action: Action,
        reality_context: Dict[str, Any]
    ) -> float:
        """
        Avalia ação considerando realidade.
        
        Args:
            action: Ação a avaliar
            reality_context: Contexto da realidade
            
        Returns:
            Q-value (balanceando prazer e realidade)
        """
        if action.action_id not in self.q_values:
            # Inicializa balanceando prazer e custo de realidade
            self.q_values[action.action_id] = (
                action.pleasure_reward - action.reality_cost
            ) / 2.0
        
        # Ajusta por conhecimento da realidade
        reality_adjustment = self.reality_model.get(action.action_id, 1.0)
        
        return self.q_values[action.action_id] * reality_adjustment
    
    def test_reality(self, action: Action) -> bool:
        """
        Testa se ação é viável na realidade.
        
        Args:
            action: Ação a testar
            
        Returns:
            True se viável, False caso contrário
        """
        # Simples heurística: custo de realidade muito alto é inviável
        return action.reality_cost < 0.8
    
    def select_defense_mechanism(
        self,
        conflict_severity: float
    ) -> DefenseMechanism:
        """
        Seleciona mecanismo de defesa apropriado.
        
        Args:
            conflict_severity: Severidade do conflito (0.0-1.0)
            
        Returns:
            Mecanismo de defesa selecionado
        """
        # Para conflitos leves, usa sublimação/racionalização
        if conflict_severity < 0.3:
            return random.choice([
                DefenseMechanism.SUBLIMATION,
                DefenseMechanism.RATIONALIZATION
            ])
        
        # Para conflitos moderados, usa deslocamento/projeção
        elif conflict_severity < 0.7:
            return random.choice([
                DefenseMechanism.DISPLACEMENT,
                DefenseMechanism.PROJECTION
            ])
        
        # Para conflitos severos, usa repressão/negação
        else:
            return random.choice([
                DefenseMechanism.REPRESSION,
                DefenseMechanism.DENIAL
            ])
    
    def update(
        self,
        action: Action,
        actual_outcome: float,
        defense_used: Optional[DefenseMechanism] = None
    ) -> None:
        """
        Atualiza modelo de realidade e efetividade de defesas.
        
        Args:
            action: Ação tomada
            actual_outcome: Resultado real
            defense_used: Mecanismo de defesa usado (se houver)
        """
        current_q = self.q_values.get(action.action_id, 0.0)
        
        # Atualiza Q-value
        self.q_values[action.action_id] = (
            current_q + self.lr * (actual_outcome - current_q)
        )
        
        # Atualiza modelo de realidade
        expected_cost = action.reality_cost
        actual_cost = 1.0 - actual_outcome
        
        self.reality_model[action.action_id] = (
            expected_cost + self.lr * (actual_cost - expected_cost)
        )
        
        # Atualiza efetividade de defesa
        if defense_used:
            current_eff = self.defense_effectiveness[defense_used]
            self.defense_effectiveness[defense_used] = (
                current_eff + self.lr * (actual_outcome - current_eff)
            )
        
        self.adaptation_history.append(actual_outcome)


class SuperegoAgent:
    """
    Superego - Instância moral e ideal.
    
    Funções:
    - Consciência moral (punição por transgressão)
    - Ego ideal (aspirações e valores)
    - Internalização de normas sociais
    - Geração de culpa e ideal
    """
    
    def __init__(self, moral_strictness: float = 0.7) -> None:
        """
        Inicializa Superego.
        
        Args:
            moral_strictness: Rigidez moral (0.0-1.0)
        """
        self.strictness = moral_strictness
        
        # Valores morais internalizados
        self.moral_values: Dict[str, float] = {}
        
        # Ideais
        self.ego_ideals: List[str] = [
            "competence",
            "virtue",
            "social_acceptance",
            "perfection"
        ]
        
        # Histórico de julgamentos
        self.judgment_history: List[float] = []
        
        logger.info(
            f"Superego Agent initialized "
            f"(moral strictness: {moral_strictness:.2f})"
        )
    
    def evaluate_action(self, action: Action) -> float:
        """
        Avalia ação moralmente.
        
        Args:
            action: Ação a avaliar
            
        Returns:
            Score moral (-1.0 a 1.0)
        """
        # Usa alinhamento moral da ação
        base_score = action.moral_alignment
        
        # Aplica rigidez moral
        # Superego rígido pune mais severamente
        if base_score < 0:
            # Ação imoral
            return base_score * self.strictness
        else:
            # Ação moral
            return base_score * (1.0 + self.strictness) / 2.0
    
    def generate_guilt(self, action: Action) -> float:
        """
        Gera culpa por ação imoral.
        
        Args:
            action: Ação realizada
            
        Returns:
            Nível de culpa (0.0-1.0)
        """
        if action.moral_alignment < 0:
            # Quanto mais imoral, mais culpa
            guilt = abs(action.moral_alignment) * self.strictness
            return min(1.0, guilt)
        
        return 0.0
    
    def approve_action(self, action: Action) -> bool:
        """
        Aprova ou reprova ação.
        
        Args:
            action: Ação a julgar
            
        Returns:
            True se aprovada, False se reprovada
        """
        moral_score = self.evaluate_action(action)
        
        # Superego aprova ações moralmente alinhadas
        threshold = 0.0  # Pode ser ajustado
        approved = moral_score >= threshold
        
        self.judgment_history.append(1.0 if approved else -1.0)
        
        return approved


class FreudianMind:
    """
    Aparelho psíquico completo - Id + Ego + Superego.
    
    Simula conflitos dinâmicos e resoluções através de
    negociação multi-agente e mecanismos de defesa.
    """
    
    def __init__(
        self,
        id_lr: float = 0.1,
        ego_lr: float = 0.1,
        superego_strictness: float = 0.7
    ) -> None:
        """
        Inicializa mente freudiana.
        
        Args:
            id_lr: Taxa de aprendizado do Id
            ego_lr: Taxa de aprendizado do Ego
            superego_strictness: Rigidez do Superego
        """
        self.id_agent = IdAgent(learning_rate=id_lr)
        self.ego_agent = EgoAgent(learning_rate=ego_lr)
        self.superego_agent = SuperegoAgent(moral_strictness=superego_strictness)
        
        # Estado psíquico
        self.state = PsychicState()
        
        # Histórico de conflitos
        self.conflict_history: List[ConflictResolution] = []
        
        logger.info("Freudian Mind initialized (Id + Ego + Superego)")
    
    def evaluate_conflict(
        self,
        actions: List[Action],
        reality_context: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """
        Avalia conflito entre as três instâncias.
        
        Args:
            actions: Ações possíveis
            reality_context: Contexto da realidade
            
        Returns:
            (severidade do conflito, preferências de cada agente)
        """
        preferences: Dict[str, Dict[str, float]] = {
            'id': {},
            'ego': {},
            'superego': {}
        }
        
        # Cada agente avalia as ações
        for action in actions:
            preferences['id'][action.action_id] = (
                self.id_agent.evaluate_action(action)
            )
            preferences['ego'][action.action_id] = (
                self.ego_agent.evaluate_action(action, reality_context)
            )
            preferences['superego'][action.action_id] = (
                self.superego_agent.evaluate_action(action)
            )
        
        # Calcula conflito como variância entre preferências
        all_scores = []
        for action_id in preferences['id'].keys():
            scores = [
                preferences['id'][action_id],
                preferences['ego'][action_id],
                preferences['superego'][action_id]
            ]
            all_scores.append(np.std(scores))
        
        conflict_severity = np.mean(all_scores) if all_scores else 0.0
        
        return conflict_severity, preferences
    
    def resolve_conflict(
        self,
        actions: List[Action],
        reality_context: Dict[str, Any]
    ) -> ConflictResolution:
        """
        Resolve conflito através do Ego.
        
        Args:
            actions: Ações possíveis
            reality_context: Contexto da realidade
            
        Returns:
            Resolução do conflito
        """
        # Avalia conflito
        conflict_severity, preferences = self.evaluate_conflict(
            actions, reality_context
        )
        
        # Ego seleciona mecanismo de defesa
        defense = self.ego_agent.select_defense_mechanism(conflict_severity)
        
        # Aplica mecanismo de defesa para modificar preferências
        modified_preferences = self._apply_defense_mechanism(
            defense, preferences, actions
        )
        
        # Seleciona ação de compromisso
        chosen_action = self._select_compromise_action(
            modified_preferences, actions
        )
        
        # Determina qualidade do compromisso
        agents_satisfied = set()
        
        id_score = preferences['id'][chosen_action.action_id]
        ego_score = preferences['ego'][chosen_action.action_id]
        superego_score = preferences['superego'][chosen_action.action_id]
        
        if id_score > 0.3:
            agents_satisfied.add('id')
        if ego_score > 0.3:
            agents_satisfied.add('ego')
        if superego_score > 0.0:
            agents_satisfied.add('superego')
        
        compromise_quality = len(agents_satisfied) / 3.0
        
        resolution = ConflictResolution(
            chosen_action=chosen_action,
            defense_mechanism=defense,
            compromise_quality=compromise_quality,
            agents_satisfied=agents_satisfied
        )
        
        self.conflict_history.append(resolution)
        
        return resolution
    
    def _apply_defense_mechanism(
        self,
        defense: DefenseMechanism,
        preferences: Dict[str, Dict[str, float]],
        actions: List[Action]
    ) -> Dict[str, Dict[str, float]]:
        """
        Aplica mecanismo de defesa para modificar preferências.
        
        Args:
            defense: Mecanismo de defesa
            preferences: Preferências originais
            actions: Ações disponíveis
            
        Returns:
            Preferências modificadas
        """
        modified = {
            'id': preferences['id'].copy(),
            'ego': preferences['ego'].copy(),
            'superego': preferences['superego'].copy()
        }
        
        if defense == DefenseMechanism.REPRESSION:
            # Suprime impulsos do Id
            for action_id in modified['id']:
                modified['id'][action_id] *= 0.3
        
        elif defense == DefenseMechanism.SUBLIMATION:
            # Redireciona Id para ações moralmente aceitas
            for action in actions:
                if action.moral_alignment > 0:
                    modified['id'][action.action_id] *= 1.5
        
        elif defense == DefenseMechanism.RATIONALIZATION:
            # Justifica ações aumentando score do Ego
            for action_id in modified['ego']:
                modified['ego'][action_id] *= 1.2
        
        elif defense == DefenseMechanism.PROJECTION:
            # Diminui culpa do Superego
            for action_id in modified['superego']:
                if modified['superego'][action_id] < 0:
                    modified['superego'][action_id] *= 0.7
        
        elif defense == DefenseMechanism.DISPLACEMENT:
            # Transfere energia para ações alternativas
            action_ids = list(modified['id'].keys())
            if len(action_ids) > 1:
                # Redistribui energia
                total_energy = sum(modified['id'].values())
                for action_id in action_ids:
                    modified['id'][action_id] = total_energy / len(action_ids)
        
        elif defense == DefenseMechanism.DENIAL:
            # Ignora realidade
            for action_id in modified['ego']:
                # Aumenta avaliação do Ego artificialmente
                modified['ego'][action_id] = abs(modified['ego'][action_id])
        
        return modified
    
    def _select_compromise_action(
        self,
        preferences: Dict[str, Dict[str, float]],
        actions: List[Action]
    ) -> Action:
        """
        Seleciona ação de compromisso.
        
        Args:
            preferences: Preferências (possivelmente modificadas)
            actions: Ações disponíveis
            
        Returns:
            Ação selecionada
        """
        # Score combinado: média ponderada
        combined_scores = {}
        
        for action in actions:
            action_id = action.action_id
            
            # Ego tem maior peso (mediador)
            combined_scores[action_id] = (
                0.3 * preferences['id'][action_id] +
                0.5 * preferences['ego'][action_id] +
                0.2 * preferences['superego'][action_id]
            )
        
        # Seleciona ação com maior score combinado
        best_action_id = max(combined_scores, key=combined_scores.get)
        
        # Encontra objeto Action
        for action in actions:
            if action.action_id == best_action_id:
                return action
        
        # Fallback
        return actions[0]
    
    def act(
        self,
        actions: List[Action],
        reality_context: Dict[str, Any]
    ) -> Tuple[Action, ConflictResolution]:
        """
        Decide e executa ação.
        
        Args:
            actions: Ações possíveis
            reality_context: Contexto da realidade
            
        Returns:
            (ação escolhida, resolução do conflito)
        """
        # Resolve conflito
        resolution = self.resolve_conflict(actions, reality_context)
        
        # Atualiza estado psíquico
        self._update_psychic_state(resolution)
        
        return resolution.chosen_action, resolution
    
    def _update_psychic_state(self, resolution: ConflictResolution) -> None:
        """
        Atualiza estado psíquico pós-ação.
        
        Args:
            resolution: Resolução do conflito
        """
        action = resolution.chosen_action
        
        # Atualiza tensão
        if 'id' not in resolution.agents_satisfied:
            self.state.tension += 0.2
        else:
            self.state.tension = max(0.0, self.state.tension - 0.1)
        
        # Atualiza ansiedade
        self.state.anxiety = self.state.tension * 0.5
        
        # Atualiza satisfação
        if 'id' in resolution.agents_satisfied:
            self.state.satisfaction += action.pleasure_reward
        
        # Atualiza culpa
        guilt = self.superego_agent.generate_guilt(action)
        self.state.guilt += guilt
        
        # Atualiza adaptação à realidade
        if 'ego' in resolution.agents_satisfied:
            self.state.reality_adaptation += 0.1
            self.state.reality_adaptation = min(1.0, self.state.reality_adaptation)


def demonstrate_freudian_mind() -> None:
    """
    Demonstração da mente freudiana.
    """
    print("=" * 70)
    print("DEMONSTRAÇÃO: Freudian Metapsychology (Id + Ego + Superego)")
    print("=" * 70)
    print()
    
    # Cria mente freudiana
    mind = FreudianMind(
        id_lr=0.1,
        ego_lr=0.1,
        superego_strictness=0.7
    )
    
    # Define ações possíveis
    actions = [
        Action(
            action_id="eat_cake",
            pleasure_reward=0.9,
            reality_cost=0.2,
            moral_alignment=-0.3,  # Ligeiramente imoral (quebra dieta)
            description="Comer bolo delicioso"
        ),
        Action(
            action_id="exercise",
            pleasure_reward=0.3,
            reality_cost=0.6,
            moral_alignment=0.8,  # Moral (saudável)
            description="Fazer exercício"
        ),
        Action(
            action_id="work_hard",
            pleasure_reward=0.2,
            reality_cost=0.5,
            moral_alignment=0.9,  # Altamente moral
            description="Trabalhar duro"
        ),
        Action(
            action_id="watch_tv",
            pleasure_reward=0.6,
            reality_cost=0.1,
            moral_alignment=0.0,  # Neutro
            description="Assistir TV"
        )
    ]
    
    # Contexto de realidade
    reality_context = {
        'time_available': 2.0,  # horas
        'energy_level': 0.7,
        'social_pressure': 0.5
    }
    
    # Simula decisão
    chosen_action, resolution = mind.act(actions, reality_context)
    
    print("RESULTADO DA DECISÃO")
    print("-" * 70)
    print(f"Ação escolhida: {chosen_action.description}")
    print(f"Mecanismo de defesa: {resolution.defense_mechanism.value if resolution.defense_mechanism else 'None'}")
    print(f"Qualidade do compromisso: {resolution.compromise_quality:.2f}")
    print(f"Agentes satisfeitos: {', '.join(resolution.agents_satisfied)}")
    print()
    
    print("ESTADO PSÍQUICO")
    print("-" * 70)
    print(f"Tensão: {mind.state.tension:.2f}")
    print(f"Ansiedade: {mind.state.anxiety:.2f}")
    print(f"Satisfação: {mind.state.satisfaction:.2f}")
    print(f"Culpa: {mind.state.guilt:.2f}")
    print(f"Adaptação à realidade: {mind.state.reality_adaptation:.2f}")
    print()
    
    print("AVALIAÇÕES DOS AGENTES")
    print("-" * 70)
    print(f"Id (prazer): {mind.id_agent.evaluate_action(chosen_action):.2f}")
    print(f"Ego (realidade): {mind.ego_agent.evaluate_action(chosen_action, reality_context):.2f}")
    print(f"Superego (moral): {mind.superego_agent.evaluate_action(chosen_action):.2f}")
    print()


if __name__ == "__main__":
    demonstrate_freudian_mind()
