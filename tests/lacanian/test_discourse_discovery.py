"""
Testes completos para Lacanian Discourse Discovery (discourse_discovery.py).

Cobertura de:
- Detecção de discursos lacanianos (Master, University, Hysteric, Analyst)
- Análise de marcadores linguísticos (keywords, padrões gramaticais, speech acts)
- Cálculo de scores e confiança
- Análise batch de textos
- Distribuição de discursos
- Exportação de análises
- Casos especiais e edge cases
"""

from __future__ import annotations

from src.lacanian.discourse_discovery import (
    DiscourseAnalysisResult,
    DiscourseMarkers,
    EmotionalSignature,
    LacanianDiscourse,
    LacanianDiscourseAnalyzer,
)


class TestLacanianDiscourseEnum:
    """Testes para enum LacanianDiscourse."""

    def test_discourse_values(self) -> None:
        """Testa valores dos discursos."""
        assert LacanianDiscourse.MASTER.value == "master"
        assert LacanianDiscourse.UNIVERSITY.value == "university"
        assert LacanianDiscourse.HYSTERIC.value == "hysteric"
        assert LacanianDiscourse.ANALYST.value == "analyst"


class TestEmotionalSignatureEnum:
    """Testes para enum EmotionalSignature."""

    def test_signature_values(self) -> None:
        """Testa valores das assinaturas emocionais."""
        assert EmotionalSignature.AUTHORITY.value == "authority"
        assert EmotionalSignature.KNOWLEDGE.value == "knowledge"
        assert EmotionalSignature.QUESTIONING.value == "questioning"
        assert EmotionalSignature.LISTENING.value == "listening"


class TestDiscourseMarkers:
    """Testes para DiscourseMarkers."""

    def test_markers_initialization(self) -> None:
        """Testa inicialização de marcadores."""
        markers = DiscourseMarkers(
            keywords={"test", "keyword"},
            grammatical_patterns=[r"\btest\b"],
            speech_acts={"command"},
            emotional_tone=EmotionalSignature.AUTHORITY,
        )

        assert "test" in markers.keywords
        assert len(markers.grammatical_patterns) == 1
        assert "command" in markers.speech_acts
        assert markers.emotional_tone == EmotionalSignature.AUTHORITY


class TestDiscourseAnalysisResult:
    """Testes para DiscourseAnalysisResult."""

    def test_result_initialization(self) -> None:
        """Testa inicialização de resultado."""
        result = DiscourseAnalysisResult(
            text="Test text",
            dominant_discourse=LacanianDiscourse.MASTER,
            discourse_scores={
                LacanianDiscourse.MASTER: 0.8,
                LacanianDiscourse.UNIVERSITY: 0.2,
            },
            key_markers=["deve", "ordem"],
            emotional_signature=EmotionalSignature.AUTHORITY,
            confidence=0.75,
        )

        assert result.text == "Test text"
        assert result.dominant_discourse == LacanianDiscourse.MASTER
        assert result.confidence == 0.75
        assert "deve" in result.key_markers


class TestLacanianDiscourseAnalyzer:
    """Testes para LacanianDiscourseAnalyzer."""

    def test_analyzer_initialization(self) -> None:
        """Testa inicialização do analisador."""
        analyzer = LacanianDiscourseAnalyzer()

        assert len(analyzer.discourse_markers) == 4
        assert LacanianDiscourse.MASTER in analyzer.discourse_markers
        assert LacanianDiscourse.UNIVERSITY in analyzer.discourse_markers
        assert LacanianDiscourse.HYSTERIC in analyzer.discourse_markers
        assert LacanianDiscourse.ANALYST in analyzer.discourse_markers
        assert len(analyzer.analysis_history) == 0

    def test_markers_initialization(self) -> None:
        """Testa inicialização dos marcadores de cada discurso."""
        analyzer = LacanianDiscourseAnalyzer()

        # Master
        master_markers = analyzer.discourse_markers[LacanianDiscourse.MASTER]
        assert "deve" in master_markers.keywords
        assert "ordem" in master_markers.keywords
        assert master_markers.emotional_tone == EmotionalSignature.AUTHORITY

        # University
        university_markers = analyzer.discourse_markers[LacanianDiscourse.UNIVERSITY]
        assert "conhecimento" in university_markers.keywords
        assert "teoria" in university_markers.keywords
        assert university_markers.emotional_tone == EmotionalSignature.KNOWLEDGE

        # Hysteric
        hysteric_markers = analyzer.discourse_markers[LacanianDiscourse.HYSTERIC]
        assert "por que" in hysteric_markers.keywords
        assert "dúvida" in hysteric_markers.keywords
        assert hysteric_markers.emotional_tone == EmotionalSignature.QUESTIONING

        # Analyst
        analyst_markers = analyzer.discourse_markers[LacanianDiscourse.ANALYST]
        assert "escute" in analyst_markers.keywords
        assert "silêncio" in analyst_markers.keywords
        assert analyst_markers.emotional_tone == EmotionalSignature.LISTENING

    def test_analyze_master_discourse_portuguese(self) -> None:
        """Testa detecção do Discurso do Mestre em português."""
        analyzer = LacanianDiscourseAnalyzer()

        text = "Você deve seguir as regras estabelecidas. É uma ordem clara e um comando direto."
        result = analyzer.analyze_text(text)

        assert result.dominant_discourse == LacanianDiscourse.MASTER
        assert result.emotional_signature == EmotionalSignature.AUTHORITY
        assert result.confidence > 0.0
        assert len(result.key_markers) > 0

    def test_analyze_master_discourse_english(self) -> None:
        """Testa detecção do Discurso do Mestre em inglês."""
        analyzer = LacanianDiscourseAnalyzer()

        text = "You must follow the rules. This is a command and you should obey the law."
        result = analyzer.analyze_text(text)

        assert result.dominant_discourse == LacanianDiscourse.MASTER
        assert result.emotional_signature == EmotionalSignature.AUTHORITY

    def test_analyze_university_discourse_portuguese(self) -> None:
        """Testa detecção do Discurso Universitário em português."""
        analyzer = LacanianDiscourseAnalyzer()

        text = (
            "Segundo a teoria lacaniana, o sujeito é barrado. "
            "Portanto, podemos definir o conceito de falta estrutural. "
            "O conhecimento é fundamental para compreender o sistema."
        )
        result = analyzer.analyze_text(text)

        assert result.dominant_discourse == LacanianDiscourse.UNIVERSITY
        assert result.emotional_signature == EmotionalSignature.KNOWLEDGE
        assert "segundo" in [m.lower() for m in result.key_markers]

    def test_analyze_university_discourse_english(self) -> None:
        """Testa detecção do Discurso Universitário em inglês."""
        analyzer = LacanianDiscourseAnalyzer()

        text = (
            "According to the theory, we can define the concept. "
            "Therefore, knowledge is the basis of the system."
        )
        result = analyzer.analyze_text(text)

        assert result.dominant_discourse == LacanianDiscourse.UNIVERSITY
        assert result.emotional_signature == EmotionalSignature.KNOWLEDGE

    def test_analyze_hysteric_discourse_portuguese(self) -> None:
        """Testa detecção do Discurso da Histérica em português."""
        analyzer = LacanianDiscourseAnalyzer()

        text = (
            "Por que sempre sofro assim? Não sei o que fazer. "
            "Talvez seja impossível encontrar o que desejo? "
            "A dúvida me consome."
        )
        result = analyzer.analyze_text(text)

        assert result.dominant_discourse == LacanianDiscourse.HYSTERIC
        assert result.emotional_signature == EmotionalSignature.QUESTIONING
        assert "por que" in [m.lower() for m in result.key_markers]

    def test_analyze_hysteric_discourse_english(self) -> None:
        """Testa detecção do Discurso da Histérica em inglês."""
        analyzer = LacanianDiscourseAnalyzer()

        text = (
            "Why do I always suffer? I don't know what to do. "
            "Perhaps it's impossible to find what I desire? "
            "Maybe there's no answer."
        )
        result = analyzer.analyze_text(text)

        assert result.dominant_discourse == LacanianDiscourse.HYSTERIC
        assert result.emotional_signature == EmotionalSignature.QUESTIONING

    def test_analyze_analyst_discourse_portuguese(self) -> None:
        """Testa detecção do Discurso do Analista em português."""
        analyzer = LacanianDiscourseAnalyzer()

        text = (
            "Continue falando... Escute o que emerge. "
            "O silêncio também produz saber. "
            "Diga mais sobre isso."
        )
        result = analyzer.analyze_text(text)

        assert result.dominant_discourse == LacanianDiscourse.ANALYST
        assert result.emotional_signature == EmotionalSignature.LISTENING
        assert "escute" in [m.lower() for m in result.key_markers] or "silêncio" in [
            m.lower() for m in result.key_markers
        ]

    def test_analyze_analyst_discourse_english(self) -> None:
        """Testa detecção do Discurso do Analista em inglês."""
        analyzer = LacanianDiscourseAnalyzer()

        text = (
            "Continue speaking... Listen to what emerges. "
            "Silence also produces knowledge. "
            "Tell me more..."
        )
        result = analyzer.analyze_text(text)

        assert result.dominant_discourse == LacanianDiscourse.ANALYST
        assert result.emotional_signature == EmotionalSignature.LISTENING

    def test_compute_discourse_score(self) -> None:
        """Testa cálculo de score de discurso."""
        analyzer = LacanianDiscourseAnalyzer()

        # Texto com múltiplos marcadores do Mestre
        text = "deve ordem comando lei regra autoridade"
        markers = analyzer.discourse_markers[LacanianDiscourse.MASTER]

        score = analyzer._compute_discourse_score(text, markers)

        assert 0.0 <= score <= 1.0
        assert score > 0.0  # Deve ter algum score devido aos marcadores

    def test_compute_discourse_score_no_matches(self) -> None:
        """Testa score quando não há marcadores."""
        analyzer = LacanianDiscourseAnalyzer()

        # Texto sem marcadores
        text = "xyz abc 123"
        markers = analyzer.discourse_markers[LacanianDiscourse.MASTER]

        score = analyzer._compute_discourse_score(text, markers)

        assert score == 0.0

    def test_analyze_batch(self) -> None:
        """Testa análise em lote."""
        analyzer = LacanianDiscourseAnalyzer()

        texts = [
            "Você deve seguir as regras.",
            "Segundo a teoria, o conceito é válido.",
            "Por que isso acontece?",
            "Continue falando...",
        ]

        results = analyzer.analyze_batch(texts)

        assert len(results) == 4
        assert results[0].dominant_discourse == LacanianDiscourse.MASTER
        assert results[1].dominant_discourse == LacanianDiscourse.UNIVERSITY
        assert results[2].dominant_discourse == LacanianDiscourse.HYSTERIC
        assert results[3].dominant_discourse == LacanianDiscourse.ANALYST

    def test_analysis_history(self) -> None:
        """Testa armazenamento de histórico de análises."""
        analyzer = LacanianDiscourseAnalyzer()

        assert len(analyzer.analysis_history) == 0

        analyzer.analyze_text("Teste 1")
        assert len(analyzer.analysis_history) == 1

        analyzer.analyze_text("Teste 2")
        assert len(analyzer.analysis_history) == 2

    def test_get_discourse_distribution(self) -> None:
        """Testa distribuição de discursos."""
        analyzer = LacanianDiscourseAnalyzer()

        # Analisa vários textos
        texts = [
            "Você deve obedecer a ordem.",
            "Você deve seguir o comando.",
            "Segundo a teoria, o conceito é válido.",
            "Por que isso acontece?",
        ]
        analyzer.analyze_batch(texts)

        distribution = analyzer.get_discourse_distribution()

        assert LacanianDiscourse.MASTER in distribution
        assert distribution[LacanianDiscourse.MASTER] == 2  # 2 textos

    def test_get_discourse_distribution_with_custom_results(self) -> None:
        """Testa distribuição com resultados customizados."""
        analyzer = LacanianDiscourseAnalyzer()

        # Cria resultados manualmente
        results = [
            DiscourseAnalysisResult(
                text="Test",
                dominant_discourse=LacanianDiscourse.MASTER,
                discourse_scores={},
                key_markers=[],
                emotional_signature=EmotionalSignature.AUTHORITY,
                confidence=0.9,
            ),
            DiscourseAnalysisResult(
                text="Test",
                dominant_discourse=LacanianDiscourse.MASTER,
                discourse_scores={},
                key_markers=[],
                emotional_signature=EmotionalSignature.AUTHORITY,
                confidence=0.9,
            ),
        ]

        distribution = analyzer.get_discourse_distribution(results)

        assert distribution[LacanianDiscourse.MASTER] == 2

    def test_export_analysis(self) -> None:
        """Testa exportação de análises."""
        analyzer = LacanianDiscourseAnalyzer()

        # Analisa texto
        analyzer.analyze_text("Você deve seguir a ordem.")

        exported = analyzer.export_analysis()

        assert len(exported) == 1
        assert "text" in exported[0]
        assert "dominant_discourse" in exported[0]
        assert "discourse_scores" in exported[0]
        assert "key_markers" in exported[0]
        assert "emotional_signature" in exported[0]
        assert "confidence" in exported[0]

    def test_export_analysis_with_custom_results(self) -> None:
        """Testa exportação com resultados customizados."""
        analyzer = LacanianDiscourseAnalyzer()

        # Cria resultado manualmente
        results = [
            DiscourseAnalysisResult(
                text="Test text",
                dominant_discourse=LacanianDiscourse.MASTER,
                discourse_scores={
                    LacanianDiscourse.MASTER: 0.8,
                    LacanianDiscourse.UNIVERSITY: 0.2,
                },
                key_markers=["deve", "ordem"],
                emotional_signature=EmotionalSignature.AUTHORITY,
                confidence=0.75,
            )
        ]

        exported = analyzer.export_analysis(results)

        assert len(exported) == 1
        assert exported[0]["text"] == "Test text"
        assert exported[0]["dominant_discourse"] == "master"
        assert exported[0]["confidence"] == 0.75
        assert "deve" in exported[0]["key_markers"]

    def test_confidence_calculation(self) -> None:
        """Testa cálculo de confiança."""
        analyzer = LacanianDiscourseAnalyzer()

        # Texto claramente Master
        text_clear = "Você deve obedecer a ordem e seguir o comando da lei."
        result_clear = analyzer.analyze_text(text_clear)

        # Texto ambíguo
        text_ambiguous = "palavra neutra genérica comum"
        result_ambiguous = analyzer.analyze_text(text_ambiguous)

        # Confiança do texto claro deve ser maior
        assert result_clear.confidence >= result_ambiguous.confidence

    def test_discourse_scores_all_present(self) -> None:
        """Testa que todos os 4 discursos têm scores."""
        analyzer = LacanianDiscourseAnalyzer()

        result = analyzer.analyze_text("Texto de teste qualquer.")

        assert len(result.discourse_scores) == 4
        assert LacanianDiscourse.MASTER in result.discourse_scores
        assert LacanianDiscourse.UNIVERSITY in result.discourse_scores
        assert LacanianDiscourse.HYSTERIC in result.discourse_scores
        assert LacanianDiscourse.ANALYST in result.discourse_scores

    def test_empty_text(self) -> None:
        """Testa análise de texto vazio."""
        analyzer = LacanianDiscourseAnalyzer()

        result = analyzer.analyze_text("")

        # Deve retornar algum resultado sem erro
        assert result.text == ""
        assert result.dominant_discourse in LacanianDiscourse
        assert 0.0 <= result.confidence <= 1.0

    def test_very_long_text(self) -> None:
        """Testa análise de texto muito longo."""
        analyzer = LacanianDiscourseAnalyzer()

        # Texto longo com padrão Master
        long_text = " ".join(["Você deve obedecer a ordem."] * 100)
        result = analyzer.analyze_text(long_text)

        assert result.dominant_discourse == LacanianDiscourse.MASTER

    def test_mixed_discourse_text(self) -> None:
        """Testa texto com múltiplos discursos misturados."""
        analyzer = LacanianDiscourseAnalyzer()

        # Texto misturando vários discursos
        text = (
            "Você deve seguir as regras. "  # Master
            "Segundo a teoria, o conceito é válido. "  # University
            "Por que isso acontece? "  # Hysteric
            "Continue falando..."  # Analyst
        )
        result = analyzer.analyze_text(text)

        # Deve identificar um discurso dominante
        assert result.dominant_discourse in LacanianDiscourse
        # Todos os discursos devem ter algum score
        assert all(score >= 0.0 for score in result.discourse_scores.values())

    def test_grammatical_patterns_detection(self) -> None:
        """Testa detecção de padrões gramaticais."""
        analyzer = LacanianDiscourseAnalyzer()

        # Texto com interrogação (Hysteric)
        text_question = "Por que isso acontece? O que fazer?"
        result = analyzer.analyze_text(text_question)

        # Deve ter score alto no Hysteric devido às interrogações
        assert result.discourse_scores[LacanianDiscourse.HYSTERIC] > 0.0

    def test_speech_acts_detection(self) -> None:
        """Testa detecção de atos de fala."""
        analyzer = LacanianDiscourseAnalyzer()

        # Texto com comando (Master)
        text_command = "Execute o comando imediatamente. É uma ordem."
        result = analyzer.analyze_text(text_command)

        assert result.dominant_discourse == LacanianDiscourse.MASTER

    def test_case_insensitivity(self) -> None:
        """Testa que a análise é case-insensitive."""
        analyzer = LacanianDiscourseAnalyzer()

        text_lower = "você deve seguir a ordem"
        text_upper = "VOCÊ DEVE SEGUIR A ORDEM"
        text_mixed = "VoCê DeVe SeGuIr A oRdEm"

        result_lower = analyzer.analyze_text(text_lower)
        result_upper = analyzer.analyze_text(text_upper)
        result_mixed = analyzer.analyze_text(text_mixed)

        # Todos devem identificar o mesmo discurso
        assert result_lower.dominant_discourse == result_upper.dominant_discourse
        assert result_lower.dominant_discourse == result_mixed.dominant_discourse

    def test_bilingual_detection(self) -> None:
        """Testa detecção em texto bilíngue."""
        analyzer = LacanianDiscourseAnalyzer()

        # Mistura português e inglês (Master)
        text = "You must obey the law and você deve seguir the command."
        result = analyzer.analyze_text(text)

        assert result.dominant_discourse == LacanianDiscourse.MASTER

    def test_multiple_markers_accumulation(self) -> None:
        """Testa acumulação de múltiplos marcadores."""
        analyzer = LacanianDiscourseAnalyzer()

        # Texto com muitos marcadores do mesmo discurso
        text = (
            "Você deve obedecer a ordem e seguir o comando da lei. "
            "É uma regra imperativa e uma obrigação clara."
        )
        result = analyzer.analyze_text(text)

        # Deve ter muitos marcadores identificados
        assert len(result.key_markers) > 5
        assert result.dominant_discourse == LacanianDiscourse.MASTER

    def test_empty_batch(self) -> None:
        """Testa análise de batch vazio."""
        analyzer = LacanianDiscourseAnalyzer()

        results = analyzer.analyze_batch([])

        assert len(results) == 0

    def test_distribution_empty_history(self) -> None:
        """Testa distribuição com histórico vazio."""
        analyzer = LacanianDiscourseAnalyzer()

        distribution = analyzer.get_discourse_distribution()

        assert len(distribution) == 0

    def test_export_empty_history(self) -> None:
        """Testa exportação com histórico vazio."""
        analyzer = LacanianDiscourseAnalyzer()

        exported = analyzer.export_analysis()

        assert len(exported) == 0
