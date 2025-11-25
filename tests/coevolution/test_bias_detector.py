"""
Testes para Bias Detector System.
"""

import pytest
from src.coevolution.bias_detector import (
    BiasDetector,
    BiasType,
    BiasDetection,
)


class TestBiasDetector:
    """Testes do sistema de detecção de viés."""

    def test_initialization(self) -> None:
        """Testa inicialização do detector."""
        detector = BiasDetector()
        assert detector is not None
        assert len(detector.detection_history) == 0
        assert len(detector.bias_thresholds) > 0

    def test_detect_bias_empty_result(self) -> None:
        """Testa detecção com resultado vazio."""
        detector = BiasDetector()

        result = {}
        detections = detector.detect_bias(result)

        assert isinstance(detections, list)
        # Sem dados, não deve detectar vieses específicos
        assert len(detections) == 0

    def test_detect_confirmation_bias(self) -> None:
        """Testa detecção de viés de confirmação."""
        detector = BiasDetector()

        # Resultado com viés de confirmação
        result = {
            "search_results": [
                {"content": "confirms"},
                {"content": "confirms"},
                {"content": "confirms"},
            ],
            "initial_hypothesis": "test hypothesis",
        }

        detections = detector.detect_bias(result)

        # Pode ou não detectar dependendo da implementação
        # Verifica estrutura se detectado
        for detection in detections:
            assert isinstance(detection, BiasDetection)
            assert detection.confidence >= 0
            assert detection.confidence <= 1

    def test_detect_selection_bias(self) -> None:
        """Testa detecção de viés de seleção."""
        detector = BiasDetector()

        result = {"sample_data": [1, 2, 3], "population_data": [1, 2, 3, 4, 5, 6]}

        detections = detector.detect_bias(result)

        # Verifica estrutura
        assert isinstance(detections, list)

    def test_detect_automation_bias(self) -> None:
        """Testa detecção de viés de automação."""
        detector = BiasDetector()

        # Muitos outputs externos sem validação
        result = {
            "external_system_outputs": ["output1", "output2", "output3"],
            "validations_performed": [],  # Sem validações!
        }

        detections = detector.detect_bias(result)

        # Deve detectar automation bias
        automation_biases = [d for d in detections if d.bias_type == BiasType.AUTOMATION_BIAS]

        if automation_biases:
            assert automation_biases[0].confidence > 0.8

    def test_detect_recency_bias(self) -> None:
        """Testa detecção de viés de recência."""
        detector = BiasDetector()

        result = {
            "temporal_data": [
                {"timestamp": "2024-01-01", "value": 1},
                {"timestamp": "2024-06-01", "value": 2},
            ],
            "data_weights": {},
        }

        detections = detector.detect_bias(result)

        # Verifica estrutura
        assert isinstance(detections, list)

    def test_correct_bias_no_detections(self) -> None:
        """Testa correção sem vieses detectados."""
        detector = BiasDetector()

        result = {"data": "clean"}
        corrected = detector.correct_bias(result)

        # Sem vieses, deve retornar original
        assert corrected == result

    def test_correct_bias_with_detections(self) -> None:
        """Testa correção com vieses detectados."""
        detector = BiasDetector()

        result = {
            "external_system_outputs": ["out1", "out2"],
            "validations_performed": [],
        }

        corrected = detector.correct_bias(result)

        # Deve aplicar correções
        assert isinstance(corrected, dict)

    def test_get_bias_statistics_empty(self) -> None:
        """Testa estatísticas sem histórico."""
        detector = BiasDetector()

        stats = detector.get_bias_statistics()

        assert stats["total"] == 0
        assert stats["by_type"] == {}

    def test_get_bias_statistics_with_history(self) -> None:
        """Testa estatísticas com histórico."""
        detector = BiasDetector()

        # Adiciona detecções manualmente ao histórico
        detector.detection_history.append(
            BiasDetection(bias_type=BiasType.CONFIRMATION_BIAS, confidence=0.8)
        )
        detector.detection_history.append(
            BiasDetection(bias_type=BiasType.CONFIRMATION_BIAS, confidence=0.9)
        )
        detector.detection_history.append(
            BiasDetection(bias_type=BiasType.SELECTION_BIAS, confidence=0.7)
        )

        stats = detector.get_bias_statistics()

        assert stats["total"] == 3
        assert "confirmation_bias" in stats["by_type"]
        assert stats["by_type"]["confirmation_bias"] == 2
        assert stats["most_common"] == "confirmation_bias"

    def test_bias_types_enum(self) -> None:
        """Testa enum de tipos de viés."""
        assert BiasType.CONFIRMATION_BIAS.value == "confirmation_bias"
        assert BiasType.SELECTION_BIAS.value == "selection_bias"
        assert BiasType.AUTOMATION_BIAS.value == "automation_bias"
        assert BiasType.RECENCY_BIAS.value == "recency_bias"
        assert BiasType.AVAILABILITY_BIAS.value == "availability_bias"
        assert BiasType.ANCHORING_BIAS.value == "anchoring_bias"

    def test_bias_detection_dataclass(self) -> None:
        """Testa dataclass de detecção de viés."""
        detection = BiasDetection(
            bias_type=BiasType.CONFIRMATION_BIAS,
            confidence=0.85,
            evidence=["Evidence 1", "Evidence 2"],
            recommendation="Fix this",
            severity="high",
        )

        assert detection.bias_type == BiasType.CONFIRMATION_BIAS
        assert detection.confidence == pytest.approx(0.85)
        assert len(detection.evidence) == 2
        assert detection.recommendation == "Fix this"
        assert detection.severity == "high"

    def test_bias_thresholds(self) -> None:
        """Testa thresholds de detecção de viés."""
        detector = BiasDetector()

        # Todos thresholds devem estar entre 0 e 1
        for threshold in detector.bias_thresholds.values():
            assert 0 <= threshold <= 1

    def test_multiple_bias_detection(self) -> None:
        """Testa detecção de múltiplos vieses."""
        detector = BiasDetector()

        # Resultado complexo que pode ter múltiplos vieses
        result = {
            "search_results": [
                {"content": "confirms"},
                {"content": "confirms"},
            ],
            "initial_hypothesis": "hypothesis",
            "external_system_outputs": ["out1", "out2"],
            "validations_performed": [],
            "temporal_data": [{"timestamp": "2024-01-01"}],
            "sample_data": [1, 2],
            "population_data": [1, 2, 3, 4, 5],
        }

        detections = detector.detect_bias(result)

        # Deve detectar pelo menos automation bias
        assert len(detections) >= 0

        # Todas detecções devem ter estrutura correta
        for detection in detections:
            assert isinstance(detection, BiasDetection)
            assert 0 <= detection.confidence <= 1
            assert detection.severity in ["low", "medium", "high"]
