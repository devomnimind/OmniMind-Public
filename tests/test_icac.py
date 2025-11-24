"""
Tests for ICAC (Introspective Clustering for Autonomous Correction).
"""

from src.autopoietic.icac import ICAC, DissonanceEvent


def test_icac_initialization():
    icac = ICAC(dissonance_threshold=0.8)
    assert icac.dissonance_threshold == 0.8


def test_detect_dissonance_no_conflict():
    icac = ICAC()
    events = [
        {"type": "decision", "confidence": 0.9},
        {"type": "decision", "confidence": 0.85},
    ]
    dissonances = icac.detect_dissonance(events)
    assert len(dissonances) == 0


def test_detect_dissonance_with_conflict():
    icac = ICAC(dissonance_threshold=0.8)
    events = [
        {
            "type": "decision_conflict",
            "event_id": "evt_1",
            "description": "Conflict A vs B",
            "resolution": {"confidence": 0.5},
            "agents": ["Id", "Ego"],
        }
    ]
    dissonances = icac.detect_dissonance(events)
    assert len(dissonances) == 1
    assert dissonances[0].conflict_score == 0.5
    assert "Id" in dissonances[0].involved_agents


def test_trigger_correction():
    icac = ICAC()
    dissonance = DissonanceEvent(
        event_ids=["1"],
        conflict_score=0.4,
        description="Test Conflict",
        involved_agents=["Id"],
    )
    action = icac.trigger_correction(dissonance)
    assert action["type"] == "weight_adjustment"
    assert "Id" in action["target_agents"]
