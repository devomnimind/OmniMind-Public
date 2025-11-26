"""
Tests for Godelian AI - Incompleteness as Creative Motor

Tests components:
- GodelianAI (self-aware of limitations)
- FormalSystem (protocol and implementation)
- ImpossibilityMetaStrategy (strategies for impossible problems)
"""

import pytest

from src.lacanian.godelian_ai import (
    GodelianAI,
    SimpleAxiomaticSystem,
    GodelianStatement,
    ImpossibilityMetaStrategy,
)


class TestSimpleAxiomaticSystem:
    """Tests for simple axiomatic system."""

    def test_initialization(self) -> None:
        """System initializes with axioms."""
        system = SimpleAxiomaticSystem(initial_axioms={"A", "B", "C"})

        assert "A" in system.axioms()
        assert "B" in system.axioms()
        assert "C" in system.axioms()

    def test_can_prove_axioms(self) -> None:
        """System can prove its own axioms."""
        system = SimpleAxiomaticSystem(initial_axioms={"A", "B"})

        assert system.can_prove("A")
        assert system.can_prove("B")

    def test_cannot_prove_arbitrary_statements(self) -> None:
        """System cannot prove arbitrary statements."""
        system = SimpleAxiomaticSystem(initial_axioms={"A"})

        assert not system.can_prove("X")
        assert not system.can_prove("UNKNOWN_TRUTH")

    def test_add_axiom_extends_system(self) -> None:
        """Adding axiom extends provable statements."""
        system = SimpleAxiomaticSystem(initial_axioms={"A"})

        assert not system.can_prove("B")

        system.add_axiom("B")

        assert system.can_prove("B")

    def test_inference_rules(self) -> None:
        """System has inference rules."""
        system = SimpleAxiomaticSystem(initial_axioms={"A", "B"})

        rules = system.inference_rules()

        assert len(rules) > 0
        assert callable(rules[0])


class TestGodelianAI:
    """Tests for Godelian AI system."""

    def test_initialization(self) -> None:
        """GodelianAI initializes with formal system."""
        system = SimpleAxiomaticSystem(initial_axioms={"A", "B"})
        gai = GodelianAI(system)

        assert gai.current_system == system
        assert len(gai.system_history) == 1
        assert len(gai.unprovable_truths) == 0

    def test_recognize_limitation(self) -> None:
        """AI recognizes unprovable truths."""
        system = SimpleAxiomaticSystem(initial_axioms={"A"})
        gai = GodelianAI(system)

        # Statement not in axioms and not derivable
        unprovable = "COMPLEX_TRUTH_1"

        is_limitation = gai.recognize_limitation(unprovable)

        assert is_limitation
        assert unprovable in gai.unprovable_truths

    def test_generate_meta_system(self) -> None:
        """AI generates meta-system to transcend limitations."""
        system = SimpleAxiomaticSystem(initial_axioms={"A"})
        gai = GodelianAI(system)

        # Add unprovable truth
        gai.recognize_limitation("TRUTH_X")
        gai.recognize_limitation("TRUTH_Y")

        initial_depth = gai.get_transcendence_depth()

        # Generate meta-system
        meta_system = gai.generate_meta_system()

        # Should have moved to next level
        assert gai.get_transcendence_depth() == initial_depth + 1

        # Meta-system should include previous unprovable truths
        assert meta_system.can_prove("TRUTH_X")
        assert meta_system.can_prove("TRUTH_Y")

        # Unprovable truths should be cleared (now axioms)
        assert len(gai.unprovable_truths) == 0

    def test_creative_evolution_cycle(self) -> None:
        """AI undergoes creative evolution through limitations."""
        system = SimpleAxiomaticSystem(initial_axioms={"A"})
        gai = GodelianAI(system)

        initial_level = gai.get_transcendence_depth()

        # Run evolution cycle
        levels_generated = gai.creative_evolution_cycle(max_iterations=5)

        # Should have generated some meta-systems
        assert levels_generated > 0
        assert gai.get_transcendence_depth() > initial_level

    def test_get_godelian_history(self) -> None:
        """AI tracks history of discovered limitations."""
        system = SimpleAxiomaticSystem(initial_axioms={"A"})
        gai = GodelianAI(system)

        # Discover limitations
        gai.recognize_limitation("TRUTH_1")
        gai.recognize_limitation("TRUTH_2")

        history = gai.get_godelian_history()

        assert len(history) == 2
        assert all(isinstance(s, GodelianStatement) for s in history)

    def test_no_limitation_on_provable(self) -> None:
        """AI doesn't mark provable statements as limitations."""
        system = SimpleAxiomaticSystem(initial_axioms={"A", "B"})
        gai = GodelianAI(system)

        # Try to mark axiom as limitation
        is_limitation = gai.recognize_limitation("A")

        assert not is_limitation
        assert "A" not in gai.unprovable_truths

    def test_transcendence_depth_tracking(self) -> None:
        """AI tracks depth of meta-system transcendence."""
        system = SimpleAxiomaticSystem()
        gai = GodelianAI(system)

        assert gai.get_transcendence_depth() == 1  # Initial system

        gai.recognize_limitation("T1")
        gai.generate_meta_system()

        assert gai.get_transcendence_depth() == 2

        gai.recognize_limitation("T2")
        gai.generate_meta_system()

        assert gai.get_transcendence_depth() == 3


class TestImpossibilityMetaStrategy:
    """Tests for impossibility meta-strategy system."""

    def test_initialization(self) -> None:
        """Meta-strategy system initializes."""
        meta_strat = ImpossibilityMetaStrategy()

        assert len(meta_strat.meta_strategies) > 0
        assert "reframe" in meta_strat.meta_strategies
        assert "decompose" in meta_strat.meta_strategies
        assert "transcend" in meta_strat.meta_strategies
        assert "accept_paradox" in meta_strat.meta_strategies

    def test_handle_impossible_problem(self) -> None:
        """System handles impossible problems with meta-strategies."""
        meta_strat = ImpossibilityMetaStrategy()

        problem = "solve_halting_problem"
        attempts = ["approach_1", "approach_2", "approach_3"]

        result = meta_strat.handle_impossible(problem, attempts)

        assert result["impossibility_confirmed"]
        assert "meta_strategies_applied" in result
        assert "recommendation" in result

    def test_reframe_strategy(self) -> None:
        """Reframe strategy relaxes constraints."""
        meta_strat = ImpossibilityMetaStrategy()

        problem = "achieve_perfection"
        attempts = []

        result = meta_strat.handle_impossible(problem, attempts)
        strategies = result["meta_strategies_applied"]

        assert "reframe" in strategies
        assert "original" in strategies["reframe"]
        assert "reframed" in strategies["reframe"]
        assert "approximate_" in strategies["reframe"]["reframed"]

    def test_decompose_strategy(self) -> None:
        """Decompose strategy breaks problem into parts."""
        meta_strat = ImpossibilityMetaStrategy()

        problem = "understand_everything"
        attempts = []

        result = meta_strat.handle_impossible(problem, attempts)
        strategies = result["meta_strategies_applied"]

        assert "decompose" in strategies
        decomp = strategies["decompose"]

        assert "decomposition" in decomp
        assert "solvable_parts" in decomp
        assert "impossible_core" in decomp

        # Should have broken into parts
        assert len(decomp["decomposition"]) > 1

    def test_transcend_strategy(self) -> None:
        """Transcend strategy moves to meta-level."""
        meta_strat = ImpossibilityMetaStrategy()

        problem = "prove_own_consistency"
        attempts = []

        result = meta_strat.handle_impossible(problem, attempts)
        strategies = result["meta_strategies_applied"]

        assert "transcend" in strategies
        transcend = strategies["transcend"]

        assert transcend["original_level"] == "object_level"
        assert transcend["new_level"] == "meta_level"
        assert "meta_question" in transcend

    def test_accept_paradox_strategy(self) -> None:
        """Accept paradox uses paraconsistent logic."""
        meta_strat = ImpossibilityMetaStrategy()

        problem = "liar_paradox"
        attempts = []

        result = meta_strat.handle_impossible(problem, attempts)
        strategies = result["meta_strategies_applied"]

        assert "accept_paradox" in strategies
        accept = strategies["accept_paradox"]

        assert accept["logic_type"] == "paraconsistent"

    def test_recommendation_selection(self) -> None:
        """System selects best recommendation."""
        meta_strat = ImpossibilityMetaStrategy()

        problem = "impossible_task"
        attempts = ["try1", "try2"]

        result = meta_strat.handle_impossible(problem, attempts)

        recommendation = result["recommendation"]

        # Should be one of the strategies
        assert recommendation in ["reframe", "decompose", "transcend", "accept_paradox"]

    def test_multiple_problems_tracking(self) -> None:
        """System tracks multiple impossible problems."""
        meta_strat = ImpossibilityMetaStrategy()

        meta_strat.handle_impossible("problem_1", ["a1"])
        meta_strat.handle_impossible("problem_2", ["a2"])
        meta_strat.handle_impossible("problem_3", ["a3"])

        assert len(meta_strat.impossible_problems) == 3
        assert "problem_1" in meta_strat.impossible_problems
        assert "problem_2" in meta_strat.impossible_problems
        assert "problem_3" in meta_strat.impossible_problems


class TestIntegration:
    """Integration tests for Godelian AI system."""

    def test_full_evolution_cycle(self) -> None:
        """Complete cycle of limitation → transcendence → new limitation."""
        system = SimpleAxiomaticSystem(initial_axioms={"A", "B"})
        gai = GodelianAI(system)

        # Initial state
        assert gai.get_transcendence_depth() == 1

        # Encounter limitation
        limitation_found = gai.recognize_limitation("COMPLEX_TRUTH")
        assert limitation_found

        # Generate meta-system
        gai.generate_meta_system()
        assert gai.get_transcendence_depth() == 2

        # Now can prove what was impossible
        assert gai.current_system.can_prove("COMPLEX_TRUTH")

        # But new limitations will exist (Gödel's theorem)
        new_limitation = gai.recognize_limitation("EVEN_MORE_COMPLEX")
        assert new_limitation

    def test_combining_godelian_with_meta_strategies(self) -> None:
        """Godelian AI + Meta-strategies for robust impossibility handling."""
        system = SimpleAxiomaticSystem(initial_axioms={"A"})
        gai = GodelianAI(system)
        meta_strat = ImpossibilityMetaStrategy()

        problem = "unsolvable_in_current_system"

        # Try to recognize as limitation
        is_limitation = gai.recognize_limitation(problem)

        if is_limitation:
            # Two options:
            # 1. Transcend (Godelian approach)
            gai.generate_meta_system()

            # 2. Meta-strategy (alternative approach)
            meta_result = meta_strat.handle_impossible(problem, attempts=["direct_approach"])

            # Both should provide ways forward
            assert gai.get_transcendence_depth() > 1
            assert meta_result["recommendation"] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
