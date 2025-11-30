"""
Lacanian Discourse Discovery (LDD) - NLP para Análise Psicanalítica.

Implementa detecção automática de discursos lacanianos em texto usando
Natural Language Processing (NLP) e análise de sentimentos.

Baseado em:
- arXiv 2024: "Combining psychoanalysis and computer science"
- Lacanian Discourse Discovery (LDD) methodology
- 4 Discursos Lacanianos: Master, University, Hysteric, Analyst

Conceitos:
- Discurso do Mestre: Comando, autoridade, poder
- Discurso Universitário: Conhecimento, saber, burocracia
- Discurso da Histérica: Questionamento, desejo, sintoma
- Discurso do Analista: Escuta, vazio, produção de saber

Author: This work was conceived by Fabrício da Silva and implemented with AI assistance
from GitHub Copilot (Claude Haiku 4.5 and Grok Code Fast 1), with constant code review
and debugging across various models including Gemini and Perplexity AI, under
theoretical coordination by the author.
Date: November 2025
License: MIT
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class LacanianDiscourse(Enum):
    """
    Os quatro discursos lacanianos.

    MASTER: Discurso do Mestre (comando, lei, autoridade)
    UNIVERSITY: Discurso Universitário (saber, conhecimento)
    HYSTERIC: Discurso da Histérica (questionamento, sintoma)
    ANALYST: Discurso do Analista (escuta, objeto a)
    """

    MASTER = "master"
    UNIVERSITY = "university"
    HYSTERIC = "hysteric"
    ANALYST = "analyst"


class EmotionalSignature(Enum):
    """
    Assinaturas emocionais associadas aos discursos.

    AUTHORITY: Autoritário, imperativo
    KNOWLEDGE: Didático, explicativo
    QUESTIONING: Questionador, sintomático
    LISTENING: Receptivo, silencioso
    """

    AUTHORITY = "authority"
    KNOWLEDGE = "knowledge"
    QUESTIONING = "questioning"
    LISTENING = "listening"


@dataclass
class DiscourseMarkers:
    """
    Marcadores linguísticos de cada discurso.

    Attributes:
        keywords: Palavras-chave características
        grammatical_patterns: Padrões gramaticais
        speech_acts: Atos de fala típicos
        emotional_tone: Tom emocional dominante
    """

    keywords: Set[str]
    grammatical_patterns: List[str]
    speech_acts: Set[str]
    emotional_tone: EmotionalSignature


@dataclass
class DiscourseAnalysisResult:
    """
    Resultado da análise de discurso.

    Attributes:
        text: Texto analisado
        dominant_discourse: Discurso dominante
        discourse_scores: Scores de cada discurso
        key_markers: Marcadores identificados
        emotional_signature: Assinatura emocional
        confidence: Confiança da classificação
    """

    text: str
    dominant_discourse: LacanianDiscourse
    discourse_scores: Dict[LacanianDiscourse, float]
    key_markers: List[str]
    emotional_signature: EmotionalSignature
    confidence: float


class LacanianDiscourseAnalyzer:
    """
    Analisador de discursos lacanianos em texto.

    Implementa LDD (Lacanian Discourse Discovery) para
    identificação automática de estruturas discursivas.
    """

    def __init__(self) -> None:
        """Inicializa analisador de discursos."""
        # Marcadores de cada discurso
        self.discourse_markers = self._initialize_markers()

        # Histórico de análises
        self.analysis_history: List[DiscourseAnalysisResult] = []

        logger.info("Lacanian Discourse Analyzer initialized")

    def _initialize_markers(self) -> Dict[LacanianDiscourse, DiscourseMarkers]:
        """
        Inicializa marcadores linguísticos dos discursos.

        Returns:
            Dicionário de marcadores por discurso
        """
        markers = {
            LacanianDiscourse.MASTER: DiscourseMarkers(
                keywords={
                    # Português
                    "deve",
                    "precisa",
                    "ordem",
                    "comando",
                    "autoridade",
                    "lei",
                    "regra",
                    "obrigação",
                    "dever",
                    "imperativo",
                    "faça",
                    "execute",
                    "cumpra",
                    "obedeça",
                    # Inglês
                    "must",
                    "should",
                    "command",
                    "order",
                    "authority",
                    "law",
                    "rule",
                    "obligation",
                    "duty",
                    "imperative",
                },
                grammatical_patterns=[
                    r"\b(deve|must|should)\b",
                    r"\b(faça|do|execute)\b",
                    r"\b(ordem|command|order)\b",
                ],
                speech_acts={
                    "command",
                    "order",
                    "directive",
                    "imperative",
                    "comando",
                    "ordem",
                    "diretiva",
                },
                emotional_tone=EmotionalSignature.AUTHORITY,
            ),
            LacanianDiscourse.UNIVERSITY: DiscourseMarkers(
                keywords={
                    # Português
                    "saber",
                    "conhecimento",
                    "teoria",
                    "conceito",
                    "definição",
                    "explicação",
                    "segundo",
                    "conforme",
                    "portanto",
                    "logo",
                    "assim",
                    "consequentemente",
                    "método",
                    "sistema",
                    "estrutura",
                    "procedimento",
                    # Inglês
                    "knowledge",
                    "theory",
                    "concept",
                    "definition",
                    "explanation",
                    "according",
                    "therefore",
                    "thus",
                    "method",
                    "system",
                    "structure",
                    "procedure",
                },
                grammatical_patterns=[
                    r"\b(segundo|according to)\b",
                    r"\b(portanto|therefore|thus)\b",
                    r"\b(definição|definition)\b",
                    r"\b(conceito|concept)\b",
                ],
                speech_acts={
                    "explanation",
                    "definition",
                    "classification",
                    "explicação",
                    "definição",
                    "classificação",
                },
                emotional_tone=EmotionalSignature.KNOWLEDGE,
            ),
            LacanianDiscourse.HYSTERIC: DiscourseMarkers(
                keywords={
                    # Português
                    "por que",
                    "como",
                    "será",
                    "talvez",
                    "dúvida",
                    "questão",
                    "pergunta",
                    "sintoma",
                    "sofrimento",
                    "desejo",
                    "falta",
                    "impossível",
                    "não sei",
                    # Inglês
                    "why",
                    "how",
                    "perhaps",
                    "maybe",
                    "doubt",
                    "question",
                    "symptom",
                    "suffering",
                    "desire",
                    "lack",
                    "impossible",
                    "don't know",
                },
                grammatical_patterns=[
                    r"\?",  # Interrogações
                    r"\b(por que|why|how)\b",
                    r"\b(talvez|perhaps|maybe)\b",
                    r"\b(não sei|don\'t know)\b",
                ],
                speech_acts={
                    "question",
                    "doubt",
                    "complaint",
                    "symptom",
                    "pergunta",
                    "dúvida",
                    "queixa",
                    "sintoma",
                },
                emotional_tone=EmotionalSignature.QUESTIONING,
            ),
            LacanianDiscourse.ANALYST: DiscourseMarkers(
                keywords={
                    # Português
                    "escute",
                    "ouça",
                    "diga",
                    "fale",
                    "continue",
                    "silêncio",
                    "vazio",
                    "espaço",
                    "abertura",
                    "produção",
                    "emergência",
                    "surgimento",
                    # Inglês
                    "listen",
                    "hear",
                    "tell",
                    "speak",
                    "continue",
                    "silence",
                    "void",
                    "space",
                    "opening",
                    "production",
                    "emergence",
                    "arising",
                },
                grammatical_patterns=[
                    r"\b(escute|listen)\b",
                    r"\b(continue|go on)\b",
                    r"\b(silêncio|silence)\b",
                    r"\.\.\.",  # Reticências (abertura)
                ],
                speech_acts={
                    "invitation",
                    "listening",
                    "silence",
                    "opening",
                    "convite",
                    "escuta",
                    "silêncio",
                    "abertura",
                },
                emotional_tone=EmotionalSignature.LISTENING,
            ),
        }

        return markers

    def analyze_text(self, text: str) -> DiscourseAnalysisResult:
        """
        Analisa texto para identificar discurso lacaniano.

        Args:
            text: Texto a analisar

        Returns:
            Resultado da análise
        """
        # Normaliza texto
        text_lower = text.lower()

        # Computa scores para cada discurso
        discourse_scores: Dict[LacanianDiscourse, float] = {}
        all_markers: List[str] = []

        for discourse, markers in self.discourse_markers.items():
            score = self._compute_discourse_score(text_lower, markers)
            discourse_scores[discourse] = score

            # Identifica marcadores presentes
            for keyword in markers.keywords:
                if keyword.lower() in text_lower:
                    all_markers.append(keyword)

        # Identifica discurso dominante
        dominant_discourse = max(discourse_scores, key=lambda k: discourse_scores[k])

        # Assinatura emocional do discurso dominante
        emotional_signature = self.discourse_markers[dominant_discourse].emotional_tone

        # Confiança (diferença entre top e segundo)
        sorted_scores = sorted(discourse_scores.values(), reverse=True)
        if len(sorted_scores) > 1 and sorted_scores[0] > 0:
            confidence = (sorted_scores[0] - sorted_scores[1]) / sorted_scores[0]
        elif sorted_scores[0] > 0:
            confidence = 1.0
        else:
            # Todos os scores são zero - nenhum marcador encontrado
            confidence = 0.0

        # Cria resultado
        result = DiscourseAnalysisResult(
            text=text,
            dominant_discourse=dominant_discourse,
            discourse_scores=discourse_scores,
            key_markers=all_markers,
            emotional_signature=emotional_signature,
            confidence=confidence,
        )

        # Salva histórico
        self.analysis_history.append(result)

        return result

    def _compute_discourse_score(self, text: str, markers: DiscourseMarkers) -> float:
        """
        Computa score de um discurso específico.

        Args:
            text: Texto a analisar
            markers: Marcadores do discurso

        Returns:
            Score (0.0-1.0)
        """
        score = 0.0
        total_weight = 0.0

        # Keywords (peso 0.4)
        keyword_matches = 0
        for keyword in markers.keywords:
            if keyword.lower() in text:
                keyword_matches += 1

        if markers.keywords:
            keyword_score = keyword_matches / len(markers.keywords)
            score += keyword_score * 0.4
            total_weight += 0.4

        # Grammatical patterns (peso 0.3)
        pattern_matches = 0
        for pattern in markers.grammatical_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                pattern_matches += 1

        if markers.grammatical_patterns:
            pattern_score = pattern_matches / len(markers.grammatical_patterns)
            score += pattern_score * 0.3
            total_weight += 0.3

        # Speech acts (peso 0.3)
        speech_act_matches = 0
        for act in markers.speech_acts:
            if act.lower() in text:
                speech_act_matches += 1

        if markers.speech_acts:
            speech_act_score = speech_act_matches / len(markers.speech_acts)
            score += speech_act_score * 0.3
            total_weight += 0.3

        # Normaliza
        if total_weight > 0:
            score = score / total_weight

        return score

    def analyze_batch(self, texts: List[str]) -> List[DiscourseAnalysisResult]:
        """
        Analisa múltiplos textos.

        Args:
            texts: Lista de textos

        Returns:
            Lista de resultados
        """
        return [self.analyze_text(text) for text in texts]

    def get_discourse_distribution(
        self, results: Optional[List[DiscourseAnalysisResult]] = None
    ) -> Dict[LacanianDiscourse, int]:
        """
        Retorna distribuição de discursos.

        Args:
            results: Resultados a analisar (usa histórico se None)

        Returns:
            Contagem por discurso
        """
        if results is None:
            results = self.analysis_history

        distribution = Counter([r.dominant_discourse for r in results])

        return dict(distribution)

    def export_analysis(
        self, results: Optional[List[DiscourseAnalysisResult]] = None
    ) -> List[Dict[str, Any]]:
        """
        Exporta análises em formato estruturado.

        Args:
            results: Resultados a exportar (usa histórico se None)

        Returns:
            Lista de dicts com análises
        """
        if results is None:
            results = self.analysis_history

        exported = []
        for result in results:
            exported.append(
                {
                    "text": result.text,
                    "dominant_discourse": result.dominant_discourse.value,
                    "discourse_scores": {
                        d.value: score for d, score in result.discourse_scores.items()
                    },
                    "key_markers": result.key_markers,
                    "emotional_signature": result.emotional_signature.value,
                    "confidence": result.confidence,
                }
            )

        return exported


def demonstrate_lacanian_discourse_discovery() -> None:
    """
    Demonstração do sistema LDD.
    """
    print("=" * 70)
    print("DEMONSTRAÇÃO: Lacanian Discourse Discovery (LDD)")
    print("=" * 70)
    print()

    # Cria analisador
    analyzer = LacanianDiscourseAnalyzer()

    # Textos de exemplo
    texts = [
        # Discurso do Mestre
        "Você deve seguir as regras estabelecidas. É uma ordem clara.",
        # Discurso Universitário
        "Segundo a teoria lacaniana, o sujeito é barrado. "
        "Portanto, podemos definir o conceito de falta estrutural.",
        # Discurso da Histérica
        "Por que sempre sofro assim? Não sei o que fazer. "
        "Talvez seja impossível encontrar o que desejo?",
        # Discurso do Analista
        "Continue falando... Escute o que emerge. " "O silêncio também produz saber.",
    ]

    # Analisa textos
    print("ANÁLISE DE TEXTOS")
    print("-" * 70)

    results = analyzer.analyze_batch(texts)

    for i, result in enumerate(results, 1):
        print(f'\nTexto {i}: "{result.text[:60]}..."')
        print(f"Discurso dominante: {result.dominant_discourse.value.upper()}")
        print(f"Assinatura emocional: {result.emotional_signature.value}")
        print(f"Confiança: {result.confidence:.2%}")
        print("Scores:")
        for discourse, score in sorted(
            result.discourse_scores.items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {discourse.value}: {score:.2f}")
        print(f"Marcadores-chave: {', '.join(result.key_markers[:5])}")

    print()

    # Distribuição de discursos
    print("DISTRIBUIÇÃO DE DISCURSOS")
    print("-" * 70)

    distribution = analyzer.get_discourse_distribution()

    for discourse, count in distribution.items():
        print(f"{discourse.value}: {count}")

    print()

    # Exporta análises
    print("EXPORTAÇÃO DE ANÁLISES")
    print("-" * 70)

    exported = analyzer.export_analysis()

    print(f"Total de análises exportadas: {len(exported)}")
    print("Exemplo de análise exportada:")
    print(f"  Discurso: {exported[0]['dominant_discourse']}")
    print(f"  Confiança: {exported[0]['confidence']:.2%}")
    print()


if __name__ == "__main__":
    demonstrate_lacanian_discourse_discovery()
