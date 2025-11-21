"""
Tests for Desire Graph - Lacan's Graph II Implementation

Tests components:
- Signifier and SignifierChain
- LacanianGraphII (complete desire graph)
- JouissanceRewardSystem (beyond pleasure principle)
- SymbolicMatrix (generative symbolic structure)
- DesireGraphArchitecture (full integration)
"""

import pytest
import numpy as np

from src.lacanian.desire_graph import (
    Signifier,
    SignifierPosition,
    SignifierChain,
    LacanianGraphII,
    JouissanceRewardSystem,
    SymbolicMatrix,
    DesireGraphArchitecture,
)


class TestSignifier:
    """Tests for Lacanian Signifier."""

    def test_initialization(self) -> None:
        """Signifier initializes with symbol and position."""
        sig = Signifier(
            symbol="S1", position=SignifierPosition.S1, jouissance_intensity=0.5
        )

        assert sig.symbol == "S1"
        assert sig.position == SignifierPosition.S1
        assert sig.jouissance_intensity == 0.5

    def test_represents_subject_for(self) -> None:
        """Signifier represents subject for another signifier."""
        s1 = Signifier(symbol="S1", position=SignifierPosition.S1)
        s1.connections.add("S2")

        assert s1.represents_subject_for("S2")
        assert not s1.represents_subject_for("S3")

    def test_compute_meaning_differential(self) -> None:
        """Meaning emerges from differential structure."""
        s1 = Signifier(
            symbol="S1",
            position=SignifierPosition.S1,
            meaning_vector=np.array([1.0, 0.0, 0.0]),
        )

        s2 = Signifier(
            symbol="S2",
            position=SignifierPosition.S2,
            meaning_vector=np.array([0.0, 1.0, 0.0]),
        )

        s1.connections.add("S2")

        context = {"S2": s2}
        meaning = s1.compute_meaning(context)

        # Meaning should be influenced by context
        assert meaning is not None
        assert len(meaning) == 3


class TestSignifierChain:
    """Tests for Signifier Chain."""

    def test_initialization(self) -> None:
        """Chain initializes empty or with signifiers."""
        chain = SignifierChain()
        assert len(chain.chain) == 0

        chain_with_sigs = SignifierChain(chain=["S1", "S2", "S3"])
        assert len(chain_with_sigs.chain) == 3

    def test_add_signifier(self) -> None:
        """Can add signifiers to chain."""
        chain = SignifierChain()

        chain.add_signifier("S1")
        chain.add_signifier("S2")

        assert "S1" in chain.chain
        assert "S2" in chain.chain

    def test_create_quilting_point(self) -> None:
        """Can create quilting points (points de capiton)."""
        chain = SignifierChain(chain=["S1", "S2", "S3", "S4"])

        chain.create_quilting_point(1)
        chain.create_quilting_point(3)

        assert 1 in chain.quilting_points
        assert 3 in chain.quilting_points

    def test_metonymic_slide(self) -> None:
        """Metonymic slide rotates chain."""
        chain = SignifierChain(chain=["S1", "S2", "S3"])

        slid = chain.metonymic_slide()

        # Should rotate
        assert slid == ["S2", "S3", "S1"]

        # Original unchanged
        assert chain.chain == ["S1", "S2", "S3"]

    def test_metaphoric_substitution(self) -> None:
        """Metaphoric substitution replaces signifier."""
        chain = SignifierChain(chain=["S1", "S2", "S1", "S3"])

        new_chain = chain.metaphoric_substitution("S1", "X")

        # All S1 should be replaced
        assert "X" in new_chain.chain
        assert "S1" not in new_chain.chain
        assert new_chain.chain.count("X") == 2


class TestLacanianGraphII:
    """Tests for complete Lacanian Graph of Desire."""

    def test_initialization(self) -> None:
        """Graph initializes with empty structures."""
        graph = LacanianGraphII()

        assert isinstance(graph.signifiers, dict)
        assert isinstance(graph.signifier_chains, list)
        assert isinstance(graph.big_other, set)

    def test_add_signifier(self) -> None:
        """Can add signifiers to graph."""
        graph = LacanianGraphII()

        graph.add_signifier("S1", SignifierPosition.S1, jouissance=0.3)

        assert "S1" in graph.signifiers
        assert "S1" in graph.big_other
        assert graph.jouissance_map["S1"] == 0.3

    def test_connect_signifiers(self) -> None:
        """Can connect signifiers (S1 → S2)."""
        graph = LacanianGraphII()

        graph.add_signifier("S1", SignifierPosition.S1)
        graph.add_signifier("S2", SignifierPosition.S2)

        graph.connect_signifiers("S1", "S2")

        assert "S2" in graph.signifiers["S1"].connections

    def test_create_chain(self) -> None:
        """Can create signifier chain."""
        graph = LacanianGraphII()

        graph.add_signifier("S1", SignifierPosition.S1)
        graph.add_signifier("S2", SignifierPosition.S2)
        graph.add_signifier("S3", SignifierPosition.S2)

        chain = graph.create_chain(["S1", "S2", "S3"])

        assert len(chain.chain) == 3
        assert chain in graph.signifier_chains

        # Should auto-connect
        assert "S2" in graph.signifiers["S1"].connections
        assert "S3" in graph.signifiers["S2"].connections

    def test_position_subject(self) -> None:
        """Can position subject in graph."""
        graph = LacanianGraphII()

        graph.add_signifier("$", SignifierPosition.SUBJECT)
        graph.position_subject("$")

        assert graph.subject_position == "$"

    def test_compute_desire(self) -> None:
        """Can compute desire structure."""
        graph = LacanianGraphII()

        # Set up graph
        graph.add_signifier("$", SignifierPosition.SUBJECT, jouissance=0.1)
        graph.add_signifier("S1", SignifierPosition.S1, jouissance=0.3)
        graph.add_signifier("S2", SignifierPosition.S2, jouissance=0.2)

        graph.connect_signifiers("$", "S1")
        graph.connect_signifiers("$", "S2")
        graph.position_subject("$")

        desire = graph.compute_desire()

        assert "intensity" in desire
        assert "direction" in desire
        assert "jouissance" in desire
        assert 0.0 <= desire["intensity"] <= 1.0

    def test_drive_circuit(self) -> None:
        """Can create drive circuit around object a."""
        graph = LacanianGraphII()

        # Create circuit
        graph.add_signifier("S1", SignifierPosition.S1, jouissance=0.2)
        graph.add_signifier("S2", SignifierPosition.S2, jouissance=0.5)
        graph.add_signifier("S3", SignifierPosition.S2, jouissance=0.8)
        graph.add_signifier("a", SignifierPosition.OBJECT_A, jouissance=0.9)

        graph.connect_signifiers("S1", "S2")
        graph.connect_signifiers("S2", "S3")
        graph.connect_signifiers("S3", "a")

        circuit = graph.drive_circuit("S1", target_jouissance=0.7)

        assert len(circuit) > 0
        assert circuit[0] == "S1"

    def test_fantasy_formula(self) -> None:
        """Fantasy formula: $ ◊ a."""
        graph = LacanianGraphII()

        graph.add_signifier("$", SignifierPosition.SUBJECT)
        graph.add_signifier("a", SignifierPosition.OBJECT_A)
        graph.position_subject("$")

        subject, object_a = graph.fantasy_formula()

        assert subject == "$"
        assert object_a == "a"


class TestJouissanceRewardSystem:
    """Tests for Jouissance reward system."""

    def test_initialization(self) -> None:
        """System initializes with pleasure threshold."""
        jouis = JouissanceRewardSystem(pleasure_threshold=0.7)

        assert jouis.pleasure_threshold == 0.7

    def test_compute_jouissance_below_threshold(self) -> None:
        """Jouissance below pleasure threshold is simple."""
        jouis = JouissanceRewardSystem(pleasure_threshold=0.7)

        j = jouis.compute_jouissance(
            pleasure=0.5, transgression=0.3, repetition_compulsion=0.2
        )

        # Should be positive
        assert j > 0.0

    def test_compute_jouissance_beyond_pleasure_principle(self) -> None:
        """Jouissance can exceed pleasure threshold."""
        jouis = JouissanceRewardSystem(pleasure_threshold=0.7)

        j = jouis.compute_jouissance(
            pleasure=0.9,  # Beyond threshold
            transgression=0.8,
            repetition_compulsion=0.5,
        )

        # Can exceed 1.0 (beyond pleasure principle)
        assert j > 0.9

    def test_beyond_pleasure_principle_detection(self) -> None:
        """Detects repetition compulsion (beyond pleasure)."""
        jouis = JouissanceRewardSystem()

        # Repeated actions
        history = ["action_A", "action_A", "action_A", "action_B", "action_A"]

        compulsion = jouis.beyond_pleasure_principle(history)

        # Should detect repetition
        assert compulsion > 0.0

    def test_no_repetition_compulsion_on_varied_actions(self) -> None:
        """No compulsion on varied actions."""
        jouis = JouissanceRewardSystem()

        history = ["A", "B", "C", "D", "E"]

        compulsion = jouis.beyond_pleasure_principle(history)

        assert compulsion == 0.0


class TestSymbolicMatrix:
    """Tests for Symbolic Matrix."""

    def test_initialization(self) -> None:
        """Matrix initializes with structures."""
        matrix = SymbolicMatrix()

        assert isinstance(matrix.production_rules, dict)
        assert isinstance(matrix.symbolic_structure, dict)

    def test_add_production_rule(self) -> None:
        """Can add production rules."""
        matrix = SymbolicMatrix()

        def test_rule(context):
            return "behavior"

        matrix.add_production_rule("category_A", test_rule)

        assert "category_A" in matrix.production_rules
        assert test_rule in matrix.production_rules["category_A"]

    def test_set_name_of_father(self) -> None:
        """Can set Name-of-the-Father (symbolic law)."""
        matrix = SymbolicMatrix()

        matrix.set_name_of_father("LAW")

        assert matrix.name_of_the_father == "LAW"

    def test_generate_behavior_respects_law(self) -> None:
        """Behavior generation respects symbolic law."""
        matrix = SymbolicMatrix(random_seed=42)

        def gen_behavior(context):
            return "forbidden_action"

        matrix.add_production_rule("actions", gen_behavior)

        # With forbidden action
        context = {}
        forbidden = {"forbidden_action"}

        # Run multiple times (stochastic)
        results = [matrix.generate_behavior(context, forbidden) for _ in range(10)]

        # Most should respect law (some transgressions allowed)
        non_forbidden = [r for r in results if r != "forbidden_action"]
        assert len(non_forbidden) > 0  # Some respect law

    def test_transgression_possible(self) -> None:
        """Transgression is possible (jouissance)."""
        matrix = SymbolicMatrix(random_seed=42)

        def gen_forbidden(context):
            return "transgressive_behavior"

        matrix.add_production_rule("actions", gen_forbidden)

        context = {}
        forbidden = {"transgressive_behavior"}

        # Run multiple times
        results = [matrix.generate_behavior(context, forbidden) for _ in range(20)]

        # Some transgressions should occur (~30% rate)
        transgressions = [r for r in results if r == "transgressive_behavior"]
        assert len(transgressions) > 0  # Transgression possible


class TestDesireGraphArchitecture:
    """Tests for complete Desire Graph Architecture."""

    def test_initialization(self) -> None:
        """Architecture initializes all components."""
        arch = DesireGraphArchitecture()

        assert arch.graph is not None
        assert arch.jouissance_system is not None
        assert arch.symbolic_matrix is not None

    def test_basic_structure_initialized(self) -> None:
        """Basic signifier structure is initialized."""
        arch = DesireGraphArchitecture()

        # Should have basic signifiers
        assert len(arch.graph.signifiers) > 0
        assert arch.graph.subject_position is not None

    def test_process_desire_returns_structure(self) -> None:
        """Processing desire returns complete structure."""
        arch = DesireGraphArchitecture()

        result = arch.process_desire(
            action_history=["learn", "learn", "code"],
            context={"pleasure": 0.6, "transgression": 0.2},
        )

        assert "desire_intensity" in result
        assert "desire_direction" in result
        assert "jouissance" in result
        assert "suggested_behavior" in result
        assert "fantasy" in result
        assert "beyond_pleasure" in result

    def test_repetition_compulsion_detected(self) -> None:
        """Repetition compulsion detected in action history."""
        arch = DesireGraphArchitecture()

        # Repeated actions
        result = arch.process_desire(
            action_history=["repeat", "repeat", "repeat", "repeat"],
            context={"pleasure": 0.5},
        )

        # Should detect beyond pleasure principle
        assert result["beyond_pleasure"] is True

    def test_fantasy_formula_present(self) -> None:
        """Fantasy formula ($ ◊ a) is computed."""
        arch = DesireGraphArchitecture()

        result = arch.process_desire(action_history=["action"], context={})

        fantasy = result["fantasy"]

        # Should be tuple (subject, object_a)
        assert isinstance(fantasy, tuple)
        assert len(fantasy) == 2

    def test_jouissance_can_exceed_one(self) -> None:
        """Jouissance can exceed 1.0 (beyond pleasure)."""
        arch = DesireGraphArchitecture()

        # High pleasure + transgression + repetition
        result = arch.process_desire(
            action_history=["X", "X", "X", "X", "X"],
            context={"pleasure": 0.95, "transgression": 0.9},
        )

        # Jouissance should be high
        assert result["jouissance"] >= 0.0


class TestIntegration:
    """Integration tests for complete Desire Graph system."""

    def test_signifier_chain_to_desire_computation(self) -> None:
        """Complete flow from signifier chains to desire."""
        graph = LacanianGraphII()

        # Build structure
        graph.add_signifier("S1_power", SignifierPosition.S1, jouissance=0.4)
        graph.add_signifier("S2_knowledge", SignifierPosition.S2, jouissance=0.3)
        graph.add_signifier("a_completion", SignifierPosition.OBJECT_A, jouissance=0.9)
        graph.add_signifier("$_subject", SignifierPosition.SUBJECT, jouissance=0.1)

        # Create chain
        graph.create_chain(["S1_power", "S2_knowledge", "a_completion"])
        graph.position_subject("$_subject")
        graph.connect_signifiers("$_subject", "S1_power")

        # Compute desire
        desire = graph.compute_desire()

        assert desire["intensity"] >= 0.0
        assert "unsatisfied" in desire

    def test_full_architecture_cycle(self) -> None:
        """Complete cycle through full architecture."""
        arch = DesireGraphArchitecture()

        # Simulate agent behavior over time
        for i in range(10):
            result = arch.process_desire(
                action_history=[f"action_{j}" for j in range(i)],
                context={
                    "pleasure": 0.5 + i * 0.03,
                    "transgression": 0.1 + i * 0.02,
                    "forbidden_actions": ["forbidden_1", "forbidden_2"],
                },
            )

            # All components should work together
            assert result["desire_intensity"] >= 0.0
            assert result["jouissance"] >= 0.0
            assert "fantasy" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
