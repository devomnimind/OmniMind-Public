#!/usr/bin/env python3
"""
Testes para MCPs 4339, 4340, 4341 (Reasoning Observer)
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest  # noqa: E402

from src.integrations.mcp_comparative_intelligence_4341 import ComparativeIntelligence  # noqa: E402
from src.integrations.mcp_model_profile_4340 import ModelProfile  # noqa: E402
from src.integrations.mcp_reasoning_capture_4339 import ReasoningCaptureService  # noqa: E402


class TestReasoningCapture4339:
    """Testa MCP 4339: Reasoning Capture."""

    def test_imports_successfully(self):
        """Verifica imports."""
        assert ReasoningCaptureService is not None

    def test_service_initialization(self):
        """Testa inicialização do serviço."""
        service = ReasoningCaptureService()
        assert service.session_id is not None
        assert len(service.reasoning_steps) == 0

    @pytest.mark.asyncio
    async def test_capture_reasoning_step(self):
        """Testa captura de passo de raciocínio."""
        service = ReasoningCaptureService()
        step = await service.capture_reasoning_step("analysis", "Analisando dados...")

        assert step is not None
        assert step["step_type"] == "analysis"
        assert step["content"] == "Analisando dados..."
        assert "timestamp" in step
        assert "elapsed_ms" in step

    @pytest.mark.asyncio
    async def test_capture_decision_point(self):
        """Testa captura de ponto de decisão."""
        service = ReasoningCaptureService()
        step = await service.capture_decision_point(
            "Qual abordagem usar?",
            ["A", "B", "C"],
            "B",
            "B é melhor",
        )

        assert step["step_type"] == "decision"
        assert step["metadata"]["chosen"] == "B"
        assert len(service.reasoning_steps) == 1

    @pytest.mark.asyncio
    async def test_capture_inference(self):
        """Testa captura de inferência."""
        service = ReasoningCaptureService()
        step = await service.capture_inference("Premissa A", "Conclusão B", 0.9)

        assert step["step_type"] == "inference"
        assert step["metadata"]["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_capture_reflection(self):
        """Testa captura de reflexão."""
        service = ReasoningCaptureService()
        step = await service.capture_reflection("Reflexão metacognitiva")

        assert step["step_type"] == "reflection"
        assert step["metadata"]["meta_level"] is True

    @pytest.mark.asyncio
    async def test_reasoning_chain(self):
        """Testa cadeia de raciocínio completa."""
        service = ReasoningCaptureService()

        await service.capture_reasoning_step("analysis", "Análise inicial")
        await service.capture_decision_point("Q", ["A", "B"], "A", "Escolhi A")
        await service.capture_inference("P1", "C1", 0.85)
        await service.capture_reflection("Meta-análise")

        chain = service.get_reasoning_chain()

        assert chain["step_count"] == 4
        assert chain["summary"]["analyses"] == 1
        assert chain["summary"]["decisions"] == 1
        assert chain["summary"]["inferences"] == 1
        assert chain["summary"]["reflections"] == 1


class TestModelProfile4340:
    """Testa MCP 4340: Model Profile."""

    def test_imports_successfully(self):
        """Verifica imports."""
        assert ModelProfile is not None

    def test_profile_initialization(self):
        """Testa inicialização do perfil."""
        profile = ModelProfile("test-model")

        assert profile.model_name == "test-model"
        assert len(profile.decision_history) == 0

    def test_record_decision(self):
        """Testa registro de decisão."""
        profile = ModelProfile("test")
        record = profile.record_decision("classification", "success", 0.95, 5)

        assert record["type"] == "classification"
        assert record["outcome"] == "success"
        assert record["confidence"] == 0.95
        assert len(profile.decision_history) == 1

    def test_stats_update(self):
        """Testa atualização de estatísticas."""
        profile = ModelProfile("test")

        profile.record_decision("clf", "success", 0.95, 3)
        profile.record_decision("clf", "success", 0.92, 3)
        profile.record_decision("clf", "failure", 0.60, 5)

        stats = profile.stats

        assert stats["total_decisions"] == 3
        assert stats["success_rate"] == pytest.approx(2 / 3)
        assert stats["error_rate"] == pytest.approx(1 / 3)
        assert stats["total_reasoning_steps"] == 11

    def test_patterns_identification(self):
        """Testa identificação de padrões."""
        profile = ModelProfile("test")

        profile.record_decision("classification", "success", 0.95, 5)
        profile.record_decision("classification", "success", 0.92, 4)
        profile.record_decision("reasoning", "success", 0.88, 12)

        patterns = profile.patterns

        assert "classification" in patterns["preferred_approaches"]
        assert patterns["preferred_approaches"]["classification"] == 2

    def test_get_profile(self):
        """Testa retrieval de perfil completo."""
        profile = ModelProfile("test")
        profile.record_decision("clf", "success", 0.95)

        full_profile = profile.get_profile()

        assert full_profile["model_name"] == "test"
        assert full_profile["statistics"]["total_decisions"] == 1
        assert full_profile["decision_count"] == 1


class TestComparativeIntelligence4341:
    """Testa MCP 4341: Comparative Intelligence."""

    def test_imports_successfully(self):
        """Verifica imports."""
        assert ComparativeIntelligence is not None

    def test_initialization(self):
        """Testa inicialização."""
        comp = ComparativeIntelligence()
        assert len(comp.model_profiles) == 0

    def test_add_model_profile(self):
        """Testa adição de perfil de modelo."""
        comp = ComparativeIntelligence()
        profile_data = {"statistics": {"success_rate": 0.95, "avg_confidence": 0.90}}

        comp.add_model_profile("Model A", profile_data)

        assert "Model A" in comp.model_profiles

    def test_compare_success_rates(self):
        """Testa comparação de taxa de sucesso."""
        comp = ComparativeIntelligence()

        comp.add_model_profile(
            "Model A",
            {"statistics": {"success_rate": 0.95}},
        )
        comp.add_model_profile(
            "Model B",
            {"statistics": {"success_rate": 0.80}},
        )

        comparison = comp.compare_success_rates()

        assert list(comparison.keys())[0] == "Model A"
        assert list(comparison.keys())[1] == "Model B"

    def test_compare_confidence(self):
        """Testa comparação de confiança."""
        comp = ComparativeIntelligence()

        comp.add_model_profile(
            "Model A",
            {"statistics": {"avg_confidence": 0.90}},
        )
        comp.add_model_profile(
            "Model B",
            {"statistics": {"avg_confidence": 0.70}},
        )

        comparison = comp.compare_confidence()

        assert list(comparison.keys())[0] == "Model A"

    def test_identify_strengths_weaknesses(self):
        """Testa identificação de pontos fortes/fracos."""
        comp = ComparativeIntelligence()

        comp.add_model_profile(
            "Model A",
            {
                "statistics": {
                    "success_rate": 0.90,
                    "avg_confidence": 0.85,
                    "error_rate": 0.10,
                },
                "patterns": {
                    "successful_strategies": ["classification", "reasoning"],
                    "error_patterns": [],
                },
            },
        )

        analysis = comp.identify_strengths_weaknesses("Model A")

        assert len(analysis["strengths"]) > 0
        assert "High success rate" in analysis["strengths"]

    def test_make_recommendations(self):
        """Testa geração de recomendações."""
        comp = ComparativeIntelligence()

        comp.add_model_profile(
            "Model A",
            {
                "statistics": {
                    "success_rate": 0.95,
                    "avg_confidence": 0.88,
                    "error_rate": 0.05,
                },
                "patterns": {
                    "successful_strategies": ["classification"],
                    "error_patterns": [],
                },
            },
        )

        comp.add_model_profile(
            "Model B",
            {
                "statistics": {
                    "success_rate": 0.70,
                    "avg_confidence": 0.65,
                    "error_rate": 0.30,
                },
                "patterns": {
                    "successful_strategies": [],
                    "error_patterns": ["timeout"],
                },
            },
        )

        recs = comp.make_recommendations()

        assert "Model A" in recs
        assert "Model B" in recs
        assert len(recs["Model B"]) > 0  # Model B deve ter recomendações

    def test_generate_comparison_report(self):
        """Testa geração de relatório completo."""
        comp = ComparativeIntelligence()

        comp.add_model_profile(
            "Model A",
            {
                "statistics": {"success_rate": 0.95, "avg_confidence": 0.90},
                "patterns": {"successful_strategies": [], "error_patterns": []},
            },
        )

        report = comp.generate_comparison_report()

        assert report["model_count"] == 1
        assert "success_rates" in report
        assert "confidence_levels" in report
        assert "strengths_weaknesses" in report
        assert "recommendations" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
    pytest.main([__file__, "-v"])
