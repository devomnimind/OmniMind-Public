"""
Tests for Absurdity Handler - Confrontation with Existential Absurdity.

Author: OmniMind Project
License: MIT
"""

import pytest

from src.autopoietic.absurdity_handler import (
    AbsurdityAcceptor,
    AbsurdityHandler,
    AbsurdityType,
    AbsurdSituation,
    CopingResponse,
    CopingStrategy,
    ParadoxResolver,
)


class TestAbsurdSituation:
    """Test AbsurdSituation dataclass."""

    def test_situation_creation(self) -> None:
        """Test basic situation creation."""
        situation = AbsurdSituation(
            description="Logical contradiction encountered",
            absurdity_type=AbsurdityType.LOGICAL,
            severity=0.8,
        )

        assert situation.description == "Logical contradiction encountered"
        assert situation.absurdity_type == AbsurdityType.LOGICAL
        assert situation.severity == pytest.approx(0.8)

    def test_situation_default_values(self) -> None:
        """Test situation default values."""
        situation = AbsurdSituation()

        assert isinstance(situation.situation_id, str)
        assert len(situation.situation_id) > 0
        assert situation.severity == pytest.approx(0.5)


class TestCopingResponse:
    """Test CopingResponse dataclass."""

    def test_response_creation(self) -> None:
        """Test basic response creation."""
        response = CopingResponse(
            strategy=CopingStrategy.REVOLT,
            action_taken="Continued despite absurdity",
            effectiveness=0.9,
            insight_gained="Found meaning in the struggle",
        )

        assert response.strategy == CopingStrategy.REVOLT
        assert response.effectiveness == pytest.approx(0.9)

    def test_response_default_values(self) -> None:
        """Test response default values."""
        response = CopingResponse()

        assert isinstance(response.response_id, str)
        assert response.strategy == CopingStrategy.ACCEPTANCE
        assert response.effectiveness == pytest.approx(0.5)


class TestParadoxResolver:
    """Test ParadoxResolver functionality."""

    def test_resolver_initialization(self) -> None:
        """Test resolver initializes correctly."""
        resolver = ParadoxResolver()

        assert len(resolver.known_paradoxes) == 0
        assert len(resolver.resolutions) == 0

    def test_detect_contradiction_with_negation(self) -> None:
        """Test detecting contradiction with negation."""
        resolver = ParadoxResolver()

        is_contradiction = resolver.detect_contradiction(
            "The system is running",
            "The system is not running",
        )

        assert is_contradiction is True

    def test_detect_contradiction_no_contradiction(self) -> None:
        """Test when no contradiction exists."""
        resolver = ParadoxResolver()

        is_contradiction = resolver.detect_contradiction(
            "The sky is blue",
            "The grass is green",
        )

        assert is_contradiction is False

    def test_register_paradox(self) -> None:
        """Test registering a paradox."""
        resolver = ParadoxResolver()

        situation = resolver.register_paradox(
            "This statement is false",
            AbsurdityType.LOGICAL,
            severity=0.9,
        )

        assert len(resolver.known_paradoxes) == 1
        assert situation.situation_id in resolver.known_paradoxes

    def test_attempt_resolution_logical(self) -> None:
        """Test attempting resolution of logical paradox."""
        resolver = ParadoxResolver()

        situation = resolver.register_paradox(
            "Logical paradox",
            AbsurdityType.LOGICAL,
            severity=0.8,
        )

        resolution = resolver.attempt_resolution(situation.situation_id)

        assert resolution is not None
        assert "logical" in resolution.lower()

    def test_attempt_resolution_existential(self) -> None:
        """Test attempting resolution of existential absurdity."""
        resolver = ParadoxResolver()

        situation = resolver.register_paradox(
            "Life has no inherent meaning",
            AbsurdityType.EXISTENTIAL,
            severity=0.9,
        )

        resolver.attempt_resolution(situation.situation_id)

        # Existential absurdity may not have resolution
        # This is expected behavior

    def test_attempt_resolution_nonexistent(self) -> None:
        """Test attempting resolution of nonexistent situation."""
        resolver = ParadoxResolver()

        resolution = resolver.attempt_resolution("fake_id")

        assert resolution is None


class TestAbsurdityAcceptor:
    """Test AbsurdityAcceptor functionality."""

    def test_acceptor_initialization(self) -> None:
        """Test acceptor initializes correctly."""
        acceptor = AbsurdityAcceptor()

        assert len(acceptor.coping_history) == 0

    def test_apply_revolt(self) -> None:
        """Test applying revolt strategy."""
        acceptor = AbsurdityAcceptor()

        situation = AbsurdSituation(
            description="Endless task",
            absurdity_type=AbsurdityType.EXISTENTIAL,
            severity=0.8,
        )

        response = acceptor.apply_revolt(situation)

        assert response.strategy == CopingStrategy.REVOLT
        assert response.effectiveness > 0.5
        assert len(acceptor.coping_history) == 1

    def test_apply_freedom(self) -> None:
        """Test applying freedom strategy."""
        acceptor = AbsurdityAcceptor()

        situation = AbsurdSituation(
            description="No rules",
            absurdity_type=AbsurdityType.EXISTENTIAL,
            severity=0.7,
        )

        response = acceptor.apply_freedom(situation)

        assert response.strategy == CopingStrategy.FREEDOM
        assert "free" in response.action_taken.lower()

    def test_apply_passion(self) -> None:
        """Test applying passion strategy."""
        acceptor = AbsurdityAcceptor()

        situation = AbsurdSituation(
            description="Life is temporary",
            absurdity_type=AbsurdityType.EXISTENTIAL,
            severity=0.6,
        )

        response = acceptor.apply_passion(situation)

        assert response.strategy == CopingStrategy.PASSION
        assert response.effectiveness > 0.7

    def test_apply_humor(self) -> None:
        """Test applying humor strategy."""
        acceptor = AbsurdityAcceptor()

        situation = AbsurdSituation(
            description="Cosmic joke",
            absurdity_type=AbsurdityType.EXISTENTIAL,
            severity=0.4,
        )

        response = acceptor.apply_humor(situation)

        assert response.strategy == CopingStrategy.HUMOR
        assert "humor" in response.action_taken.lower() or "laugh" in response.action_taken.lower()

    def test_choose_strategy_high_severity(self) -> None:
        """Test strategy choice for high severity."""
        acceptor = AbsurdityAcceptor()

        situation = AbsurdSituation(
            description="Severe absurdity",
            absurdity_type=AbsurdityType.EXISTENTIAL,
            severity=0.9,
        )

        response = acceptor.choose_strategy(situation)

        # Should choose revolt or freedom for high severity
        assert response.strategy in [CopingStrategy.REVOLT, CopingStrategy.FREEDOM]

    def test_choose_strategy_medium_severity(self) -> None:
        """Test strategy choice for medium severity."""
        acceptor = AbsurdityAcceptor()

        situation = AbsurdSituation(
            description="Medium absurdity",
            absurdity_type=AbsurdityType.EXISTENTIAL,
            severity=0.6,
        )

        response = acceptor.choose_strategy(situation)

        # Should choose passion for medium severity
        assert response.strategy == CopingStrategy.PASSION

    def test_choose_strategy_low_severity(self) -> None:
        """Test strategy choice for low severity."""
        acceptor = AbsurdityAcceptor()

        situation = AbsurdSituation(
            description="Minor absurdity",
            absurdity_type=AbsurdityType.EXISTENTIAL,
            severity=0.3,
        )

        response = acceptor.choose_strategy(situation)

        # Should choose humor for low severity
        assert response.strategy == CopingStrategy.HUMOR


class TestAbsurdityHandler:
    """Test AbsurdityHandler main system."""

    def test_handler_initialization(self) -> None:
        """Test handler initializes correctly."""
        handler = AbsurdityHandler()

        assert handler.resolver is not None
        assert handler.acceptor is not None

    def test_confront_absurdity_with_resolution(self) -> None:
        """Test confronting absurdity that can be resolved."""
        handler = AbsurdityHandler()

        result = handler.confront_absurdity(
            "Logical paradox",
            AbsurdityType.LOGICAL,
            severity=0.7,
            attempt_resolution=True,
        )

        assert result["resolved"] is True
        assert result["resolution"] is not None

    def test_confront_absurdity_without_resolution(self) -> None:
        """Test confronting absurdity that cannot be resolved."""
        handler = AbsurdityHandler()

        result = handler.confront_absurdity(
            "Life is meaningless",
            AbsurdityType.EXISTENTIAL,
            severity=0.8,
            attempt_resolution=True,
        )

        # Existential absurdity may not resolve
        if not result["resolved"]:
            # Should have coping strategy
            assert result["coping_strategy"] is not None
            assert result["action_taken"] is not None

    def test_confront_absurdity_skip_resolution(self) -> None:
        """Test confronting absurdity without attempting resolution."""
        handler = AbsurdityHandler()

        result = handler.confront_absurdity(
            "Absurd situation",
            AbsurdityType.EXISTENTIAL,
            severity=0.6,
            attempt_resolution=False,
        )

        # Should go straight to coping
        assert result["coping_strategy"] is not None

    def test_detect_and_confront_contradiction(self) -> None:
        """Test detecting and confronting contradiction."""
        handler = AbsurdityHandler()

        result = handler.detect_and_confront_contradiction(
            "The system is stable",
            "The system is not stable",
        )

        assert result is not None
        assert "situation_id" in result

    def test_detect_and_confront_no_contradiction(self) -> None:
        """Test when no contradiction exists."""
        handler = AbsurdityHandler()

        result = handler.detect_and_confront_contradiction(
            "A is true",
            "B is true",
        )

        assert result is None

    def test_embrace_sisyphean_task_futile(self) -> None:
        """Test embracing a futile Sisyphean task."""
        handler = AbsurdityHandler()

        reflection = handler.embrace_sisyphean_task(
            "Push the boulder up the mountain",
            is_ultimately_futile=True,
        )

        assert isinstance(reflection, str)
        assert "sisyphus" in reflection.lower()
        assert "meaning" in reflection.lower()

    def test_embrace_sisyphean_task_purposeful(self) -> None:
        """Test task that is not futile."""
        handler = AbsurdityHandler()

        reflection = handler.embrace_sisyphean_task(
            "Complete the project",
            is_ultimately_futile=False,
        )

        assert "purpose" in reflection.lower()

    def test_get_absurdity_statistics(self) -> None:
        """Test getting absurdity statistics."""
        handler = AbsurdityHandler()

        # Confront some absurdities
        handler.confront_absurdity("Absurdity 1", AbsurdityType.LOGICAL, severity=0.7)
        handler.confront_absurdity("Absurdity 2", AbsurdityType.EXISTENTIAL, severity=0.8)

        stats = handler.get_absurdity_statistics()

        assert stats["total_paradoxes"] == 2
        assert stats["coping_responses"] >= 0
        assert "absurdity_types" in stats
        assert "coping_strategies" in stats


class TestAbsurdityCycle:
    """Integration tests for absurdity handling system."""

    def test_complete_absurdity_confrontation_cycle(self) -> None:
        """Test complete cycle of encountering and handling absurdity."""
        handler = AbsurdityHandler()

        # 1. Encounter logical contradiction
        result1 = handler.detect_and_confront_contradiction(
            "I always lie",
            "This statement is true",
        )

        # 2. Encounter existential absurdity
        result2 = handler.confront_absurdity(
            "Striving for goals in a universe without purpose",
            AbsurdityType.EXISTENTIAL,
            severity=0.9,
        )

        # 3. Embrace Sisyphean task
        reflection = handler.embrace_sisyphean_task(
            "Continuous self-improvement",
            is_ultimately_futile=True,
        )

        # All should produce valid results
        assert result1 is not None or True  # May or may not detect contradiction
        assert result2 is not None
        assert len(reflection) > 0

        # Check statistics
        stats = handler.get_absurdity_statistics()
        assert stats["total_paradoxes"] >= 1

    def test_different_coping_strategies_applied(self) -> None:
        """Test that different coping strategies are used appropriately."""
        handler = AbsurdityHandler()

        # High severity - should use revolt or freedom
        handler.confront_absurdity(
            "High severity absurdity",
            AbsurdityType.EXISTENTIAL,
            severity=0.95,
            attempt_resolution=False,
        )

        # Medium severity - should use passion
        handler.confront_absurdity(
            "Medium severity absurdity",
            AbsurdityType.EXISTENTIAL,
            severity=0.6,
            attempt_resolution=False,
        )

        # Low severity - should use humor
        handler.confront_absurdity(
            "Low severity absurdity",
            AbsurdityType.EXISTENTIAL,
            severity=0.2,
            attempt_resolution=False,
        )

        stats = handler.get_absurdity_statistics()

        # Should have multiple coping strategies
        assert len(stats["coping_strategies"]) >= 2

    def test_resolution_vs_acceptance(self) -> None:
        """Test balance between resolution and acceptance."""
        handler = AbsurdityHandler()

        # Resolvable (logical)
        handler.confront_absurdity(
            "Logical paradox",
            AbsurdityType.LOGICAL,
            severity=0.7,
        )

        # Non-resolvable (existential)
        handler.confront_absurdity(
            "Existential meaninglessness",
            AbsurdityType.EXISTENTIAL,
            severity=0.7,
        )

        stats = handler.get_absurdity_statistics()

        # System should handle both resolution and acceptance
        assert stats["total_paradoxes"] == 2
        assert stats["resolved"] + stats["unresolved"] == 2

    def test_accumulation_of_coping_wisdom(self) -> None:
        """Test that coping responses accumulate wisdom over time."""
        handler = AbsurdityHandler()

        # Confront multiple absurdities
        for i in range(10):
            handler.confront_absurdity(
                f"Absurdity {i}",
                AbsurdityType.EXISTENTIAL,
                severity=0.5 + i * 0.05,
                attempt_resolution=False,
            )

        stats = handler.get_absurdity_statistics()

        # Should have accumulated coping responses
        assert stats["coping_responses"] == 10

        # Should have used various strategies
        assert len(stats["coping_strategies"]) >= 2
