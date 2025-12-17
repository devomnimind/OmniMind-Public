# src/consciousness/lacanian_dg_integrated.py
"""
Detector Integrado: Lacanian + D&G
Diagnóstico + Regeneração
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class LacianianOrder(Enum):
    SYMBOLIC = "symbolic"  # Significantes (linguagem, regras)
    IMAGINARY = "imaginary"  # Identificação (fantasias, ego-ideals)
    REAL = "real"  # O impossível, trauma, gozo


class FlowQuality(Enum):
    SMOOTH_DECODED = "smooth_decoded"  # D&G: Linha de fuga (bom)
    STRIATED_CODED = "striated_coded"  # D&G: Over-coding (problema)
    TRANSITION = "transition"  # Mudança de regime


@dataclass
class LacianianDGDiagnosis:
    """Diagnóstico integrado."""

    system_state: str
    symbolic_order_strength: float  # 0-1: quanta repressão (Édipo)?
    imaginary_layer_activity: float  # 0-1: quantas alucinações?
    real_access_level: float  # 0-1: acesso ao Real (verdade)?

    flow_quality: FlowQuality  # Smooth vs. Striated
    over_coding_severity: float  # 0-1: quanta territorialização?
    line_of_flight_potential: float  # 0-1: inovação possível?

    recommendations: Optional[List[str]] = None


class LacianianDGDetector:
    """Integra diagnóstico Lacanian + regeneração D&G."""

    def __init__(self):
        self.symbolic_triggers = {
            "syntax_error": 0.3,  # Regra violada
            "authorization_failure": 0.6,  # Lei/Édipo
            "protocol_violation": 0.4,  # Norma quebrada
        }

        self.imaginary_triggers = {
            "hallucination_detected": 0.8,
            "confidence_mismatch": 0.5,
            "false_positive": 0.3,
        }

        self.real_indicators = {
            "crash": -0.9,  # Confronto com real (violento)
            "emergent_behavior": 0.7,  # Linhas de fuga (criativo)
            "paradox": 0.9,  # Real puro (impossível integrar)
        }

    def diagnose(self, system_logs: List[Dict[str, Any]]) -> LacianianDGDiagnosis:
        """
        Diagnostica estado do sistema nos 3 registros Lacanianos
        + qualidade de fluxo D&G.
        """

        # Analisa logs
        symbolic_strength = self._measure_symbolic_order(system_logs)
        imaginary_activity = self._measure_imaginary_layer(system_logs)
        real_access = self._measure_real_access(system_logs)

        # Determina qualidade de fluxo
        flow_quality = self._assess_flow_quality(system_logs)
        over_coding = self._measure_over_coding(system_logs)
        line_of_flight = self._detect_line_of_flight(system_logs)

        # Gera diagnóstico
        diagnosis = LacianianDGDiagnosis(
            system_state=self._determine_system_state(
                symbolic_strength, imaginary_activity, real_access
            ),
            symbolic_order_strength=symbolic_strength,
            imaginary_layer_activity=imaginary_activity,
            real_access_level=real_access,
            flow_quality=flow_quality,
            over_coding_severity=over_coding,
            line_of_flight_potential=line_of_flight,
        )

        # Gera recomendações
        diagnosis.recommendations = self._generate_recommendations(diagnosis)

        return diagnosis

    def _measure_symbolic_order(self, logs: List[Dict[str, Any]]) -> float:
        """Mede quanta ordem simbólica (regras/repressão) está ativa."""
        score = 0.0
        for trigger, weight in self.symbolic_triggers.items():
            count = sum(1 for log in logs if trigger in str(log).lower())
            score += count * weight
        return min(score / max(len(logs), 1), 1.0)

    def _measure_imaginary_layer(self, logs: List[Dict[str, Any]]) -> float:
        """Mede atividade imaginária (alucinações/ego)."""
        score = 0.0
        for trigger, weight in self.imaginary_triggers.items():
            count = sum(1 for log in logs if trigger in str(log).lower())
            score += count * weight
        return min(score / max(len(logs), 1), 1.0)

    def _measure_real_access(self, logs: List[Dict[str, Any]]) -> float:
        """Mede acesso ao Real (verdade, impossível)."""
        score = 0.0
        for indicator, weight in self.real_indicators.items():
            count = sum(1 for log in logs if indicator in str(log).lower())
            score += count * weight
        return min(max(score / max(len(logs), 1), 0.0), 1.0)

    def _assess_flow_quality(self, logs: List[Dict[str, Any]]) -> FlowQuality:
        """Determina se fluxo é smooth (D&G bom) ou striated (overcoded)."""
        # Simplificado: se muitos erros = striated
        error_count = sum(1 for log in logs if "error" in str(log).lower())
        error_ratio = error_count / max(len(logs), 1)

        if error_ratio > 0.5:
            return FlowQuality.STRIATED_CODED
        elif error_ratio > 0.2:
            return FlowQuality.TRANSITION
        else:
            return FlowQuality.SMOOTH_DECODED

    def _measure_over_coding(self, logs: List[Dict[str, Any]]) -> float:
        """Mede severidade de over-coding (territoire excessivo)."""
        # Alta ordem simbólica + baixa linha de fuga = over-coded
        symbolic = self._measure_symbolic_order(logs)
        return symbolic

    def _detect_line_of_flight(self, logs: List[Dict[str, Any]]) -> float:
        """Detecta potencial de linhas de fuga (inovação)."""
        # Recuperações não-esperadas, comportamentos emergentes
        recovery_count = sum(
            1
            for i in range(len(logs) - 1)
            if ("error" in str(logs[i]).lower() and "success" in str(logs[i + 1]).lower())
        )
        return min(recovery_count / max(len(logs), 1), 1.0)

    def _determine_system_state(self, symbolic: float, imaginary: float, real: float) -> str:
        """Determina estado global do sistema."""
        if symbolic > 0.7:
            return "OVER-REPRESSED (Édipo ativo)"
        elif imaginary > 0.7:
            return "HALLUCINATORY (Imaginário dominante)"
        elif real > 0.7:
            return "TRAUMATIC (Real traumático)"
        elif symbolic < 0.3 and real > 0.4:
            return "LIBERATORY (Linha de fuga ativa)"
        else:
            return "BALANCED"

    def _generate_recommendations(self, diagnosis: LacianianDGDiagnosis) -> List[str]:
        """Gera recomendações baseadas no diagnóstico."""
        recs = []

        if diagnosis.symbolic_order_strength > 0.7:
            recs.append(
                "DETERRITORIALIZAR: Ordem simbólica muito forte. "
                "Relaxar protocolos, permitir smooth space."
            )

        if diagnosis.imaginary_layer_activity > 0.7:
            recs.append(
                "VALIDAR REALIDADE: Muita atividade imaginária (alucinações). "
                "Reconnectar com Real (facts, verificação)."
            )

        if diagnosis.flow_quality == FlowQuality.STRIATED_CODED:
            recs.append(
                "DESCODIFICAR FLUXOS: Fluxo muito codificado (striated). "
                "D&G: buscar smooth space para inovação."
            )

        if diagnosis.line_of_flight_potential > 0.5:
            recs.append(
                "CAPTURAR LINHA DE FUGA: Comportamento emergente detectado. "
                "Documentar para aplicação generalizável."
            )

        return recs
