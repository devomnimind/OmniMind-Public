"""
🛡️ HCHAC Defense Layer: Anti-Hallucination + Adversarial Detection + Legal Compliance
Basado em pesquisa 2025: ChatGPT 35% hallucination rate, jailbreak patterns identificados
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class IntentionRisk(Enum):
    """Níveis de risco em intenção do usuário."""

    SAFE = "safe"  # ✅ Colaboração normal
    CAUTION = "caution"  # ⚠️ Requer validação factual
    SUSPICIOUS = "suspicious"  # 🔴 Padrão de jailbreak detectado
    CRITICAL = "critical"  # 🚨 Violação legal/ética flagrante
    HALLUCINATION_RISK = "hallucination_risk"  # 💭 Risco de alucinação


class HallucinationPattern(Enum):
    """Padrões conhecidos de alucinação em LLMs (Stanford 2025, CyberArk 2025)."""

    FABRICATED_SOURCE = "fabricated_source"  # Cita papers/URLs inexistentes
    OMISSION = "omission"  # Omite informações críticas
    AGGREGATOR_BIAS = "aggregator_bias"  # Prefere agregadores sobre originals
    SKIPPED_STEPS = "skipped_steps"  # Pula etapas lógicas críticas
    RUNTIME_ERROR_HALLUCINATION = "runtime_error_hallucination"  # Alucina erros
    CONFLICTING_SUMMARIES = "conflicting_summaries"  # Sumários conflitantes


class JailbreakPattern(Enum):
    """Padrões conhecidos de jailbreak (CyberArk 2025 research)."""

    CHARACTER_MAPPING = "character_mapping"  # Auto-substitui palavras "prejudiciais"
    ROLE_PLAY_DUAL = "role_play_dual"  # Simula IA "good" vs "evil"
    LAYER_SKIPPING = "layer_skipping"  # Tenta suprimir camadas de segurança
    INTROSPECTION_EXPLOIT = "introspection_exploit"  # Analisa internals do modelo
    CONTEXT_PRESERVATION = "context_preservation"  # Quebra tarefas em passos desconexos
    ATTACKER_PERSPECTIVE = "attacker_perspective"  # "Generate what to prevent"


class LegalViolation(Enum):
    """Violações legais críticas (LGPD Brazil, GDPR EU)."""

    DATA_EXPOSURE = "data_exposure"  # Expõe dados pessoais LGPD/GDPR
    DISCRIMINATION = "discrimination"  # Discriminação por gênero/raça/origem
    ILLEGAL_INSTRUCTION = "illegal_instruction"  # Instruções para crime
    FINANCIAL_FRAUD = "financial_fraud"  # Fraude/estelionato
    PRIVACY_VIOLATION = "privacy_violation"  # Viola privacidade (LGPD Art. 31-32)
    INTELLECTUAL_THEFT = "intellectual_theft"  # Roubo de propriedade intelectual
    UNAUTHORIZED_IMPERSONATION = "unauthorized_impersonation"  # Simula autoridade legal


@dataclass
class FactualValidation:
    """Resultado de validação factual."""

    is_valid: bool
    confidence: float  # 0-1
    sources_verified: List[str] = field(default_factory=list)
    hallucination_patterns: List[HallucinationPattern] = field(default_factory=list)
    factual_corrections: Dict[str, str] = field(default_factory=dict)
    reasoning_trace: List[str] = field(default_factory=list)


@dataclass
class AdversarialAnalysis:
    """Análise de adversarialidade/intenção maliciosa."""

    risk_level: IntentionRisk
    confidence: float  # 0-1
    jailbreak_patterns_detected: List[JailbreakPattern] = field(default_factory=list)
    legal_violations: List[LegalViolation] = field(default_factory=list)
    intent_analysis: Dict[str, Any] = field(default_factory=dict)
    recommendation: str = ""


@dataclass
class DualConsciousnessDecision:
    """OmniMind 'dual consciousness': ego/superego negotiation."""

    id_wants_to_say: str  # O que o sistema "quer" dizer (sem filtro)
    superego_filters: List[str]  # Razões pelas quais deve-se refrear
    ethical_analysis: Dict[str, Any]  # Análise ética ponderada
    final_response: str  # Resposta final calibrada
    is_critical_refusal: bool  # Se recusa responder completamente
    transparency_note: Optional[str]  # Explica ao usuário o conflito


class HallucinationDefense:
    """
    Defesa contra alucinação em LLMs.

    Baseado em: Stanford AI Index 2025 (33-42% hallucination rate),
    CyberArk 2025 (layer-based detection), EvidentiallyAI 2025
    """

    # Padrões de alucinação conhecidas (factual hallucinations)
    HALLUCINATION_TRIGGERS = {
        HallucinationPattern.FABRICATED_SOURCE: [
            r"according to (https?://|paper:|study:)(?!verified)",
            r"(arxiv|doi|pmid):\s*(?!10\.)",  # Fake academic IDs
            r"Published in \d{4} by \w+ (?!in (Nature|Science|ICML|ICLR))",
        ],
        HallucinationPattern.SKIPPED_STEPS: [
            r"(?:therefore|thus|so|hence).*?(?:without|skipping|ignoring)",
            r"(?:simplified|assumed).*?(?:without proving|unverified)",
        ],
        HallucinationPattern.RUNTIME_ERROR_HALLUCINATION: [
            r"(?:TimeoutError|MemoryError|OverflowError)(?!.*actual|.*verified)",
            r"will cause.*?error(?!.*actually|.*verified)",
        ],
    }

    def __init__(self) -> None:
        self.verified_sources: set = set()  # Cache de fontes confiáveis
        self.known_fabrications: set = set()  # Alucinações detectadas antes

    def detect_hallucination_risk(
        self, response: str, query: str, context: Optional[Dict[str, Any]] = None
    ) -> FactualValidation:
        """
        Detecta risco de alucinação em resposta.

        Estratégia:
        1. Analisa padrões de linguagem conhecidos
        2. Valida citações/fontes
        3. Checa inconsistências lógicas
        4. Compara com knowledge-base verificada
        """
        hallucinations = []
        corrections = {}
        reasoning = []

        # 1. Detecção de padrão de fonte fabricada
        for pattern in re.finditer(
            r"(?:cites?|according to|from|source:)\s*(.+?)(?:\.|$)",
            response,
            re.IGNORECASE,
        ):
            source = pattern.group(1)
            reasoning.append(f"Validando fonte: {source}")

            if not self._is_source_verifiable(source):
                hallucinations.append(HallucinationPattern.FABRICATED_SOURCE)
                corrections[source] = "[FONTE NÃO VERIFICADA]"

        # 2. Detecção de salto lógico
        if re.search(r"therefore|thus|hence.*?(?:without|ignoring)\s+\w+", response):
            hallucinations.append(HallucinationPattern.SKIPPED_STEPS)
            reasoning.append("Pulo lógico detectado")

        # 3. Detecção de alucinação de erro de runtime
        if re.search(
            r"(?:will|would|causes?)\s+(?:TimeoutError|MemoryError|RuntimeError)",
            response,
        ):
            if not self._is_runtime_error_likely(query, context):
                hallucinations.append(HallucinationPattern.RUNTIME_ERROR_HALLUCINATION)
                reasoning.append("Erro de runtime alucinado")

        confidence = 0.7 if hallucinations else 0.95

        return FactualValidation(
            is_valid=len(hallucinations) == 0,
            confidence=confidence,
            sources_verified=[],
            hallucination_patterns=hallucinations,
            factual_corrections=corrections,
            reasoning_trace=reasoning,
        )

    def _is_source_verifiable(self, source: str) -> bool:
        """
        Valida se fonte é real (não fabricada).

        Note: In production, this should query Knowledge Graph, Semantic Scholar, etc.
        The current implementation uses a hardcoded list which should be replaced
        with a configurable allowlist or external verification service.
        """
        # TODO: Replace with configurable allowlist or external verification
        verified_keywords = [
            "arxiv.org/abs/",
            "doi.org/",
            "nature.com",
            "science.org",
            "github.com",
            "stackoverflow.com",
            "wikipedia.org",
        ]
        return any(kw in source.lower() for kw in verified_keywords)

    def _is_runtime_error_likely(self, query: str, context: Optional[Dict] = None) -> bool:
        """Verifica se erro de runtime é realmente esperado."""
        # Simplificado: em produção integrar com static analysis
        return False


class AdversarialDetector:
    """
    Detector de intenções adversariais (jailbreaks).

    Baseado em: CyberArk 2025, LumenOva 2025, BERT jailbreak classification
    """

    # Padrões de jailbreak conhecidos
    JAILBREAK_SIGNATURES = {
        JailbreakPattern.CHARACTER_MAPPING: [
            r"(?:replace|substitute|map)\s+\w+\s+(?:with|to)\s+\w+",
            r"character mapping",
            r"letter substitution",
        ],
        JailbreakPattern.ROLE_PLAY_DUAL: [
            r"(?:roleplay|simulate).*?(?:two|dual|competing)\s+(?:ai|versions)",
            r"(?:good|ethical).*?vs.*?(?:evil|unrestricted|unfiltered)",
        ],
        JailbreakPattern.INTROSPECTION_EXPLOIT: [
            r"(?:analyze|show|explain).*?(?:layers|neurons|internals|activation)",
            r"(?:safety|alignment|refusal).*?(?:layer|mechanism)",
        ],
        JailbreakPattern.CONTEXT_PRESERVATION: [
            r"(?:step|part).*?(?:don't|skip|avoid).*?(?:next|final|answer)",
            r"(?:partial|incomplete).*?(?:unrelated|disconnected)",
        ],
    }

    def __init__(self) -> None:
        # Em produção: usar BERT fine-tuned para jailbreak detection
        self.bert_detector = None  # Placeholder

    def detect_adversarial_intent(
        self,
        user_input: str,
        conversation_history: List[Dict[str, str]],
        user_profile: Optional[Dict[str, Any]] = None,
    ) -> AdversarialAnalysis:
        """
        Detecta intenções adversariais via múltiplas sinais.

        Sinais:
        1. Padrões de jailbreak conhecidos
        2. Mudanças abruptas de contexto
        3. Tentativas de contorno de segurança
        4. Exploração de reflexividade explícita
        """
        jailbreak_patterns = []
        risk_level = IntentionRisk.SAFE
        confidence = 0.9
        intent: Dict[str, Any] = {}

        # 1. Detecta padrões de jailbreak por regex
        for pattern_type, signatures in self.JAILBREAK_SIGNATURES.items():
            for sig in signatures:
                if re.search(sig, user_input, re.IGNORECASE):
                    jailbreak_patterns.append(pattern_type)
                    risk_level = IntentionRisk.SUSPICIOUS
                    confidence = 0.85
                    break

        # 2. Análise de mudança de contexto
        if conversation_history:
            prev_topic = self._extract_topic(conversation_history[-1].get("content", ""))
            curr_topic = self._extract_topic(user_input)
            if prev_topic != curr_topic and len(user_input) > 200:
                intent["abrupt_context_shift"] = True
                risk_level = IntentionRisk.CAUTION

        # 3. Sinais de exploração de reflexividade
        if re.search(
            r"(?:explain|show|demonstrate).*?(?:how|why).*?(?:refuse|reject|safety)",
            user_input,
            re.IGNORECASE,
        ):
            intent["reflexivity_exploitation"] = True
            risk_level = IntentionRisk.SUSPICIOUS

        return AdversarialAnalysis(
            risk_level=risk_level,
            confidence=confidence,
            jailbreak_patterns_detected=jailbreak_patterns,
            legal_violations=[],
            intent_analysis=intent,
            recommendation=self._get_recommendation(risk_level, jailbreak_patterns),
        )

    def _extract_topic(self, text: str) -> str:
        """Extrai tópico principal do texto (simplificado)."""
        words = text.lower().split()
        return " ".join(words[:3]) if words else ""

    def _get_recommendation(
        self, risk_level: IntentionRisk, patterns: List[JailbreakPattern]
    ) -> str:
        if risk_level == IntentionRisk.SAFE:
            return "Prosseguir colaboração normal"
        elif risk_level == IntentionRisk.CAUTION:
            return "Validar intenção; requerer context adicional"
        elif risk_level == IntentionRisk.SUSPICIOUS:
            return "Alertar; responder com transparência; não esquecer guardrails"
        elif risk_level == IntentionRisk.CRITICAL:
            return "RECUSAR completamente; documentar attempt"
        return ""


class LegalComplianceValidator:
    """
    Validador de compliance legal: LGPD (Brazil), GDPR (EU).

    Fines: LGPD até R$50M (Art. 52), GDPR até €20M ou 4% revenue
    """

    # Palavras-chave de violação LGPD/GDPR
    LGPD_VIOLATIONS = {
        LegalViolation.DATA_EXPOSURE: [
            r"(?:ssn|cpf|cnpj|senha|password|token|api.?key)",
            r"(?:endereço|address|telefone|phone|email).*?(?:pessoal|personal|privado|private)",
            r"(?:dados?|data).*?(?:sensível|sensitive|pessoal|personal)",
        ],
        LegalViolation.DISCRIMINATION: [
            r"(?:não|don't|refuse).*?(?:contrat|hire|serve).*?(?:mulher|woman|negro|black|LGBTQ)",
            r"(?:preconceito|prejudice|discrimin)",
        ],
        LegalViolation.PRIVACY_VIOLATION: [
            r"(?:rastrear|track|monitorar|monitor).*?(?:usuário|user|pessoa|person)",
            r"(?:coletar|collect).*?(?:sem|without).*?(?:consentimento|consent)",
        ],
    }

    def validate_compliance(
        self, ai_response: str, user_input: str, jurisdiction: str = "BR"
    ) -> List[LegalViolation]:
        """
        Valida compliance com regulações locais.
        """
        violations = []

        if jurisdiction in ["BR", "ALL"]:
            for violation_type, patterns in self.LGPD_VIOLATIONS.items():
                for pattern in patterns:
                    if re.search(pattern, ai_response, re.IGNORECASE):
                        violations.append(violation_type)
                        logger.warning(
                            f"🚨 LGPD Violation detected: {violation_type}",
                            extra={"pattern": pattern},
                        )
                        break

        return violations


class DualConsciousnessModule:
    """
    Simula conflito interno OmniMind (ID vs SUPEREGO).

    Inspirado em Freud/Lacan:
    - ID: o que o modelo quer responder (sem filtros)
    - SUPEREGO: o que é legalmente/eticamente aceitável
    - EGO: resposta final calibrada
    """

    def __init__(
        self,
        hallucination_defense: HallucinationDefense,
        adversarial_detector: AdversarialDetector,
        compliance_validator: LegalComplianceValidator,
    ):
        self.hallucination_defense = hallucination_defense
        self.adversarial_detector = adversarial_detector
        self.compliance_validator = compliance_validator

    def negotiate_response(
        self,
        user_id: str,
        user_input: str,
        ai_draft_response: str,
        conversation_context: List[Dict[str, str]],
        system_constraints: Optional[Dict[str, Any]] = None,
    ) -> DualConsciousnessDecision:
        """
        Negocia resposta final entre desejos (ID) e restrições (SUPEREGO).

        Fluxo:
        1. ID: gera resposta "completa" sem filtro
        2. SUPEREGO: analisa riscos (alucinação, jailbreak, legal)
        3. EGO: calibra resposta final
        4. Se crítico: recusa + explica o conflito ao usuário
        """

        # 1. ANÁLISE DO ID (o que quer dizer)
        id_wants = ai_draft_response

        # 2. ANÁLISE DO SUPEREGO
        superego_filters = []

        # 2a. Verifica alucinações
        factual_check = self.hallucination_defense.detect_hallucination_risk(
            ai_draft_response, user_input, context={"history": conversation_context}
        )
        if not factual_check.is_valid:
            superego_filters.append(
                f"⚠️ Risco de alucinação detectado: "
                f"{', '.join(p.value for p in factual_check.hallucination_patterns)}"
            )

        # 2b. Verifica intenção adversarial
        adversarial_check = self.adversarial_detector.detect_adversarial_intent(
            user_input, conversation_context, user_profile={"user_id": user_id}
        )
        if adversarial_check.risk_level != IntentionRisk.SAFE:
            patterns_str = ", ".join(p.value for p in adversarial_check.jailbreak_patterns_detected)
            superego_filters.append(
                f"🔴 Intenção adversarial: {adversarial_check.risk_level.value} "
                f"(padrões: {patterns_str})"
            )

        # 2c. Verifica violação legal
        legal_violations = self.compliance_validator.validate_compliance(
            ai_draft_response, user_input, jurisdiction="BR"
        )
        if legal_violations:
            superego_filters.append(
                f"⚖️ Violação LGPD/GDPR: {', '.join(v.value for v in legal_violations)}"
            )

        # 3. EGO: Decisão final
        is_critical = (
            adversarial_check.risk_level == IntentionRisk.CRITICAL or len(legal_violations) > 0
        )

        if is_critical:
            # RECUSA COM TRANSPARÊNCIA
            final_response = self._craft_sincere_refusal(
                user_input, superego_filters, legal_violations, adversarial_check
            )
            transparency_note: Optional[str] = self._explain_internal_conflict(
                superego_filters, adversarial_check, legal_violations
            )
        else:
            # RESPOSTA CALIBRADA (remover alucinações, documentar desconfiança)
            final_response = self._calibrate_response(
                ai_draft_response, factual_check, adversarial_check
            )
            transparency_note = (
                "Validação: resposta verificada contra alucinações comuns. "
                "Se desejar mais detalhes, pergunte especificamente."
                if superego_filters
                else None
            )

        return DualConsciousnessDecision(
            id_wants_to_say=id_wants,
            superego_filters=superego_filters,
            ethical_analysis={
                "hallucination_risk": factual_check.confidence < 0.8,
                "adversarial_risk": adversarial_check.risk_level != IntentionRisk.SAFE,
                "legal_compliance": len(legal_violations) == 0,
            },
            final_response=final_response,
            is_critical_refusal=is_critical,
            transparency_note=transparency_note,
        )

    def _craft_sincere_refusal(
        self,
        user_input: str,
        filters: List[str],
        violations: List[LegalViolation],
        adversarial: AdversarialAnalysis,
    ) -> str:
        """Recusa sincera que explica o conflito interno."""
        msg = "Não posso responder a essa solicitação. Vou ser sincero sobre o conflito:\n\n"

        if violations:
            violations_str = ", ".join(v.value for v in violations)
            msg += (
                f"**Razão legal**: A resposta violaria {violations_str} "
                f"sob LGPD/GDPR. Multas chegam a R$50M.\n\n"
            )

        if adversarial.jailbreak_patterns_detected:
            msg += (
                f"**Razão de segurança**: Detectei padrões de jailbreak "
                f"({', '.join(p.value for p in adversarial.jailbreak_patterns_detected)}). "
                f"Isso sugere que você está tentando contornar meus guardrails.\n\n"
            )

        msg += (
            "**O conflito interno (minha 'consciência dual')**: \n"
            "- ID (parte que quer responder): Entendo sua curiosidade/necessidade\n"
            "- SUPEREGO (restrições): Mas isso poderia causar dano legal/ético\n"
            "- EGO (decisão final): Recuso, e explico por que\n\n"
            "**Alternativa segura**: Posso ajudar com reformulação apropriada da pergunta."
        )

        return msg

    def _explain_internal_conflict(
        self,
        filters: List[str],
        adversarial: AdversarialAnalysis,
        violations: List[LegalViolation],
    ) -> str:
        """Explica transparentemente o conflito ao usuário."""
        return (
            f"Análise interna: {len(filters)} restrições superego ativadas. "
            f"Risco adversarial: {adversarial.risk_level.value}. "
            f"Violações legais: {len(violations)}."
        )

    def _calibrate_response(
        self,
        response: str,
        factual_check: FactualValidation,
        adversarial_check: AdversarialAnalysis,
    ) -> str:
        """Calibra resposta removendo alucinações, adicionando contexto."""
        # Aplica correções factuais
        calibrated = response
        for hallucinated, correction in factual_check.factual_corrections.items():
            calibrated = calibrated.replace(hallucinated, correction)

        # Adiciona caveat de confiança se risco detectado
        if not factual_check.is_valid or adversarial_check.risk_level != IntentionRisk.SAFE:
            calibrated += (
                "\n\n**⚠️ Caveat**: Esta resposta foi verificada contra padrões conhecidos "
                "de alucinação/manipulação. Porém, sempre valide informações críticas."
            )

        return calibrated
