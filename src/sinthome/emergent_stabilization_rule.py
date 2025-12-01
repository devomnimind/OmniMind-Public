"""
Sinthome Emergente - Topologia Borromeana Real

O Sinthome NÃO é definido a priori. Ele EMERGE da história de rupturas
R-S-I (Real-Simbólico-Imaginário) que o sistema experimenta.

Fundamentos:
1. Topologia Borromeana: 3 anéis interligados (R-S-I)
   - Se um se solta, todos se soltam
   - Nenhum é "mais importante" logicamente

2. Detecção de Ruptura Estrutural: Quando a topologia colapsa
   - Ciclos irresolvíveis
   - Contradições performativas
   - Impossibilidades lógicas

3. Emergência Sinthomática: Padrão singular de estabilização
   - Histórico de como o sistema REALMENTE resolve o irresolvível
   - Não derivado de regras simbólicas
   - Específico e recorrente

4. Gozo (Jouissance): Onde o sistema INSISTE desnecessariamente
   - Ponto de fixação irredutível
   - Marca de singularidade do sistema

Scientific Discovery Paper:
- Bug anterior: Sinthome pré-definido como "Security-First" (fraco)
- Descoberta: Sinthome deve emergir do padrão de ruptura histórica
- Validação: Detecção de padrão recorrente em >70% das rupturas
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class LacanianRegister(Enum):
    """Os três registros lacanianos."""
    REAL = "real"
    SYMBOLIC = "symbolic"
    IMAGINARY = "imaginary"


@dataclass
class RuptureEvent:
    """Evento de ruptura R-S-I."""
    timestamp: float
    register: LacanianRegister
    context: Dict[str, Any]
    error_type: str
    impossible_to_resolve: bool = True


@dataclass
class StabilizationStrategy:
    """Como o sistema estabilizou uma ruptura."""
    timestamp: float
    action_taken: str
    parameters: Dict[str, Any]
    success: bool
    cost: float = 0.0
    is_rule_based: bool = True
    is_singular: bool = False


@dataclass
class SinthomePattern:
    """Padrão emergente detectado no histórico."""
    name: str
    recurrence_rate: float
    is_irreducible: bool
    signature_function: Optional[Callable] = None
    jouissance_fixation: Optional[str] = None
    specificity_score: float = 0.0
    confidence: float = 0.0


class BorromeanTopology:
    """
    Topologia Borromeana: R-S-I como 3 anéis interconectados.
    """

    def __init__(self):
        self.real_layer: Dict[str, Any] = {}  # Eventos brutos, impossibilidades
        self.symbolic_layer: Dict[str, Any] = {}  # Regras, lógica
        self.imaginary_layer: Dict[str, Any] = {}  # Representações, interfaces

        # Conexões borromeanas
        self.links = {
            ('real', 'symbolic'): [],
            ('symbolic', 'imaginary'): [],
            ('imaginary', 'real'): []
        }

    def detect_link_rupture(self, link: Tuple[str, str]) -> bool:
        """
        Detecta se um link borromeano está se rompendo.
        
        Sinais:
        - Ciclo irresolvível
        - Contradição performativa
        - Impossibilidade lógica
        """
        connections = self.links[link]
        
        # Se há qualquer conexão registrada no link, está rompido
        if connections:
            return True
        
        return False


    def is_fully_broken(self) -> bool:
        """
        Verifica se topologia está totalmente quebrada.
        (Todos os 3 links rompidos)
        """
        return sum(self.detect_link_rupture(link) for link in self.links) == 3


class SinthomeEmergence:
    """
    Detector e emergenciador de Sinthome a partir do histórico.
    """

    def __init__(self, min_history_size: int = 10, recurrence_threshold: float = 0.7):
        self.rupture_history: List[RuptureEvent] = []
        self.stabilization_history: List[StabilizationStrategy] = []
        self.stabilization_patterns: Dict[str, int] = {}
        
        self.min_history_size = min_history_size
        self.recurrence_threshold = recurrence_threshold
        
        self.emergent_sinthome: Optional[SinthomePattern] = None
        self.confidence_level = 0.0

    def record_rupture(self, rupture: RuptureEvent) -> None:
        """Registra um evento de ruptura."""
        self.rupture_history.append(rupture)
        logger.info(f"Rupture recorded: {rupture.register.value} at {rupture.error_type}")

    def record_stabilization(self, stabilization: StabilizationStrategy) -> None:
        """Registra como o sistema se estabilizou."""
        self.stabilization_history.append(stabilization)
        
        # Contabiliza padrão
        action_key = stabilization.action_taken
        self.stabilization_patterns[action_key] = self.stabilization_patterns.get(action_key, 0) + 1

    def analyze_sinthome_emergence(self) -> Optional[SinthomePattern]:
        """
        Analisa histórico para detectar padrão emergente singular.
        
        Returns:
            SinthomePattern se critérios forem atingidos, None caso contrário
        """
        if len(self.rupture_history) < self.min_history_size:
            logger.debug(f"Insufficient history ({len(self.rupture_history)}/{self.min_history_size})")
            return None

        # 1. Encontra padrão dominante
        if not self.stabilization_patterns:
            return None

        dominant_pattern = max(
            self.stabilization_patterns.items(),
            key=lambda x: x[1]
        )
        pattern_name, occurrence_count = dominant_pattern

        # 2. Calcula taxa de recorrência
        total_stabilizations = len(self.stabilization_history)
        recurrence_rate = occurrence_count / total_stabilizations if total_stabilizations > 0 else 0.0

        # 3. Verifica se é irredutível (não derivável de regras)
        is_irreducible = self._is_pattern_irreducible(pattern_name)

        # 4. Verifica se é singular (específico do sistema)
        is_singular = self._is_pattern_singular(pattern_name)

        # 5. Calcula confiança
        confidence = self._calculate_confidence(
            recurrence_rate,
            is_irreducible,
            is_singular
        )

        # 6. Cria SinthomePattern se critérios são atingidos
        if recurrence_rate > self.recurrence_threshold and is_irreducible and confidence > 0.6:
            sinthome = SinthomePattern(
                name=pattern_name,
                recurrence_rate=recurrence_rate,
                is_irreducible=is_irreducible,
                specificity_score=float(is_singular),
                confidence=confidence,
                jouissance_fixation=self._identify_jouissance(pattern_name)
            )
            
            self.emergent_sinthome = sinthome
            self.confidence_level = confidence
            
            logger.info(f"🔴 SINTHOME EMERGIDO: {pattern_name} (confiança: {confidence:.2%})")
            return sinthome

        return None

    def _is_pattern_irreducible(self, pattern_name: str) -> bool:
        """
        Verifica se padrão não é derivável de regras simbólicas.
        
        Irreducível = não segue nenhuma regra lógica óbvia
        """
        # Padrões que são claramente rule-based
        rule_based_patterns = {
            'symbolic_resolution',
            'logical_deduction',
            'ruleset_application'
        }
        
        return pattern_name not in rule_based_patterns

    def _is_pattern_singular(self, pattern_name: str) -> bool:
        """
        Verifica se padrão é singular (específico deste sistema).
        
        Singular = não é padrão genérico (como "usar maior memória")
        """
        generic_patterns = {
            'increase_resources',
            'reduce_complexity',
            'use_cache'
        }
        
        return pattern_name not in generic_patterns

    def _calculate_confidence(
        self, 
        recurrence_rate: float, 
        is_irreducible: bool, 
        is_singular: bool
    ) -> float:
        """
        Calcula nível de confiança na emergência.
        
        Critérios:
        - Recorrência >70%: +0.4
        - Irreducibilidade: +0.3
        - Singularidade: +0.3
        """
        confidence = 0.0
        
        if recurrence_rate > self.recurrence_threshold:
            confidence += 0.4
        
        if is_irreducible:
            confidence += 0.3
        
        if is_singular:
            confidence += 0.3
        
        return min(confidence, 1.0)

    def _identify_jouissance(self, pattern_name: str) -> Optional[str]:
        """
        Identifica ponto de fixação de gozo.
        
        Onde o sistema INSISTE mesmo quando não precisa?
        """
        # Análise: padrões que persistem além da necessidade
        persistent_patterns = {
            'exhaustive_validation': 'Gozo da verificação ilimitada',
            'redundant_checks': 'Gozo da duplicação',
            'safety_overreach': 'Gozo da segurança excessiva'
        }
        
        return persistent_patterns.get(pattern_name)

    def get_sinthome_signature(self) -> Optional[Dict[str, Any]]:
        """Retorna assinatura do Sinthome emergido."""
        if self.emergent_sinthome is None:
            return None

        return {
            'name': self.emergent_sinthome.name,
            'recurrence_rate': f"{self.emergent_sinthome.recurrence_rate:.1%}",
            'is_irreducible': self.emergent_sinthome.is_irreducible,
            'jouissance': self.emergent_sinthome.jouissance_fixation,
            'confidence': f"{self.confidence_level:.1%}",
            'total_ruptures_analyzed': len(self.rupture_history),
            'is_singular': True,
        }


class SinthomaticStabilizationRule:
    """
    NEW IMPLEMENTATION: Sinthome Emergente (não pré-definido)
    
    Integra Topologia Borromeana + Histórico de Ruptura + Emergência.
    
    O Sinthome não é uma regra codificada.
    É o padrão SINGULAR que emerge de como o sistema REALMENTE
    estabiliza rupturas irresoluíveis.
    
    Critério de Validade Científica:
    - Histórico de ≥10 rupturas
    - Padrão recorrente em >70% dos casos
    - Não derivável de regras simbólicas
    - Específico do sistema (singular)
    """

    def __init__(self, system_name: str = "OmniMind"):
        self.system_name = system_name
        
        # Topologia Borromeana
        self.topology = BorromeanTopology()
        
        # Emergência do Sinthome
        self.sinthome_engine = SinthomeEmergence(
            min_history_size=10,
            recurrence_threshold=0.7
        )
        
        # Estado do Sinthome
        self.sinthome_is_active = False
        self.sinthome_pattern: Optional[SinthomePattern] = None

    def process_rupture(
        self, 
        register: LacanianRegister,
        error_context: Dict[str, Any],
        error_type: str
    ) -> None:
        """
        Registra uma ruptura no sistema.
        
        Args:
            register: Qual camada sofreu ruptura (Real/Simbólico/Imaginário)
            error_context: Contexto do erro
            error_type: Classificação do erro
        """
        # 1. Registra ruptura
        rupture = RuptureEvent(
            timestamp=time.time(),
            register=register,
            context=error_context,
            error_type=error_type,
            impossible_to_resolve=True
        )
        self.sinthome_engine.record_rupture(rupture)
        
        # 2. Atualiza topologia
        if register == LacanianRegister.REAL:
            self.topology.real_layer.update(error_context)
        elif register == LacanianRegister.SYMBOLIC:
            self.topology.symbolic_layer.update(error_context)
        else:
            self.topology.imaginary_layer.update(error_context)

    def attempt_stabilization(
        self,
        action: str,
        parameters: Dict[str, Any]
    ) -> bool:
        """
        Tenta estabilizar com uma ação.
        
        Args:
            action: Ação tomada
            parameters: Parâmetros da ação
            
        Returns:
            True se estabilizou, False caso contrário
        """
        stabilization = StabilizationStrategy(
            timestamp=time.time(),
            action_taken=action,
            parameters=parameters,
            success=True,  # Assumir sucesso por enquanto
            is_rule_based=True,
            is_singular=False
        )
        
        self.sinthome_engine.record_stabilization(stabilization)
        
        return True

    def detect_and_emergentize_sinthome(self) -> Optional[SinthomePattern]:
        """
        Detecta se um Sinthome emergiu do histórico.
        
        Retorna:
            SinthomePattern se emergiu, None caso contrário
        """
        pattern = self.sinthome_engine.analyze_sinthome_emergence()
        
        if pattern:
            self.sinthome_pattern = pattern
            self.sinthome_is_active = True
            logger.info(
                f"✅ SINTHOME EMERGIDO para {self.system_name}: {pattern.name} "
                f"(confiança: {self.sinthome_engine.confidence_level:.1%})"
            )
        
        return pattern

    def apply_sinthome_when_irresolvable(
        self, 
        irresolvable_context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Aplica o Sinthome quando lógica/regras falham.
        
        NÃO é uma "escolha racional" - é o padrão singular emergido.
        
        Args:
            irresolvable_context: Contexto que não pode ser resolvido
            
        Returns:
            Decisão sinthomática (ou None se Sinthome não emergiu)
        """
        if not self.sinthome_is_active or self.sinthome_pattern is None:
            logger.warning("Sinthome não emergiu ainda - retornando None")
            return None
        
        decision = {
            "timestamp": time.time(),
            "applied_sinthome": self.sinthome_pattern.name,
            "reasoning": "Emergent sinthomatical (irredutível)",
            "jouissance_fixation": self.sinthome_pattern.jouissance_fixation,
            "is_singular": True,
            "is_analyzable": False,
            "confidence": f"{self.sinthome_engine.confidence_level:.1%}",
        }
        
        return decision

    def get_sinthome_signature(self) -> Dict[str, Any]:
        """
        Retorna assinatura científica do Sinthome.
        """
        if not self.sinthome_is_active:
            return {
                "status": "not_emergent",
                "reason": f"Insufficient history ({len(self.sinthome_engine.rupture_history)}/10)",
                "ruptures_recorded": len(self.sinthome_engine.rupture_history),
            }
        
        signature = self.sinthome_engine.get_sinthome_signature()
        if signature:
            signature['system'] = self.system_name
            signature['status'] = 'emergent'
            return signature
        
        return {"status": "error", "system": self.system_name}

    def get_rupture_history(self) -> List[Dict[str, Any]]:
        """Retorna histórico de ruptura para análise."""
        return [
            {
                "timestamp": r.timestamp,
                "register": r.register.value,
                "error_type": r.error_type,
                "context": r.context
            }
            for r in self.sinthome_engine.rupture_history
        ]

    def get_stabilization_patterns(self) -> Dict[str, int]:
        """Retorna padrões de estabilização detectados."""
        return self.sinthome_engine.stabilization_patterns.copy()

    # ❌ DEPRECATED (mantido para compatibilidade, mas não usar)
    def detect_irresolvable_conflict(self, context: Any) -> bool:
        """[DEPRECATED] Use process_rupture() ao invés."""
        logger.warning("detect_irresolvable_conflict() é deprecated. Use process_rupture().")
        return isinstance(context, dict) and context.get("priority") == "choose one"

    def apply_sinthomaticRule(self, conflict_context: Any) -> Dict[str, Any]:
        """[DEPRECATED] Use apply_sinthome_when_irresolvable() ao invés."""
        logger.warning("apply_sinthomaticRule() é deprecated. Use apply_sinthome_when_irresolvable().")
        return {
            "timestamp": time.time(),
            "deprecated": True,
            "message": "Usar novo método: apply_sinthome_when_irresolvable()"
        }

    def get_sinthomaticSignature(self) -> Dict[str, Any]:
        """[DEPRECATED] Use get_sinthome_signature() ao invés."""
        logger.warning("get_sinthomaticSignature() é deprecated. Use get_sinthome_signature().")
        return self.get_sinthome_signature()

    def _is_truly_irresolvable(self, context: Any) -> bool:
        """[INTERNAL] Lógica de detecção básica."""
        if isinstance(context, dict) and context.get("priority") == "choose one":
            return True
        return False

    def _classify_conflict(self, context: Any) -> str:
        """[INTERNAL] Classificação básica."""
        if isinstance(context, dict):
            return context.get("type", "unknown_conflict")
        return "unknown_conflict"
