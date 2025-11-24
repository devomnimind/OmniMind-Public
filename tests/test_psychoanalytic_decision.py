"""
Tests for Psychoanalytic Decision System.
"""

from src.agents.psychoanalytic_analyst import PsychoanalyticDecisionSystem


def test_agents_initialization():
    system = PsychoanalyticDecisionSystem()
    assert len(system.agents) == 3
    names = [a.name for a in system.agents]
    assert "Id" in names
    assert "Ego" in names
    assert "Superego" in names


def test_voting_mechanism():
    system = PsychoanalyticDecisionSystem()
    # Mock votes for deterministic testing
    # Id: avoid_conflict (0.8) * 0.33 = 0.264
    # Ego: analyze_rationally (0.75) * 0.33 = 0.2475
    # Superego: follow_rules (0.9) * 0.33 = 0.297

    # Winner should be Superego (follow_rules)

    decision = system.resolve_conflict("Context")

    assert decision["winner"] == "follow_rules"
    assert len(decision["votes"]) == 3


def test_weight_update():
    system = PsychoanalyticDecisionSystem()
    system.update_weights({"Id": 0.5, "Ego": 0.5, "Superego": 0.0})

    id_agent = next(a for a in system.agents if a.name == "Id")
    superego_agent = next(a for a in system.agents if a.name == "Superego")

    assert id_agent.weight == 0.5
    assert superego_agent.weight == 0.0
