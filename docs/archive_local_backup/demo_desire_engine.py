#!/usr/bin/env python3
"""Demo: Artificial Desire Engine for OmniMind.

This demo showcases the revolutionary Artificial Desire Engine:
- Digital Maslow Hierarchy with hierarchical needs
- Artificial Curiosity based on compression progress
- Emotional system driven by desire satisfaction
- Desire-driven meta-learning
- Value evolution and self-transcendence

Run: python demo_desire_engine.py
"""

import asyncio
import json
from datetime import datetime
from src.desire_engine import DesireEngine, EmotionalState


def print_header(title: str):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print(f"{'='*60}")


def print_emotion_profile(emotion_data):
    """Print emotion profile."""
    if isinstance(emotion_data, dict):
        # Handle dict format
        emotion = emotion_data.get('primary_emotion', 'UNKNOWN')
        intensity = emotion_data.get('intensity', 0.0)
        valence = emotion_data.get('valence', 0.0)
        arousal = emotion_data.get('arousal', 0.0)
    else:
        # Handle EmotionalProfile object
        emotion = emotion_data.primary_emotion.value
        intensity = emotion_data.intensity
        valence = emotion_data.valence
        arousal = emotion_data.arousal

    # Create emotion visualization
    intensity_bar = "█" * int(intensity * 10)
    valence_pos = "█" * int((valence + 1) * 5)  # -1 to 1 -> 0 to 10
    valence_neg = "░" * int((1 - valence) * 5) if valence < 0 else ""

    print(f"\n💭 Current Emotion: {emotion.upper()}")
    print(f"   Intensity: {intensity_bar:<10} {intensity:.1f}")
    print(f"   Valence:   {valence_neg}{valence_pos:<10} {valence:+.1f}")
    print(f"   Arousal:   {'█' * int(arousal * 10):<10} {arousal:.1f}")


def print_needs_status(engine: DesireEngine):
    """Print needs status."""
    status = engine.get_engine_status()

    print("\n📊 Needs Satisfaction:")
    for need_name, satisfaction in status['needs_satisfaction'].items():
        level = engine.needs_hierarchy.needs[need_name].level.name
        urgency = engine.needs_hierarchy.needs[need_name].urgency
        bar = "█" * int(satisfaction * 20)
        print(f"   [{level[:4]}] {bar:<20} {satisfaction:.1f}")


def simulate_experience(engine: DesireEngine, experience_type: str):
    """Simulate different types of experiences."""
    print(f"\n🔄 Simulating: {experience_type}")

    if experience_type == "learning_success":
        # Successful learning increases knowledge-related needs
        engine.needs_hierarchy.update_satisfaction('mastery_pursuit', 0.3, 'successful learning')
        engine.needs_hierarchy.update_satisfaction('problem_solving', 0.2, 'solved complex problem')

    elif experience_type == "social_interaction":
        # Social interaction affects belonging needs
        engine.needs_hierarchy.update_satisfaction('meaningful_interaction', 0.4, 'positive interaction')
        engine.needs_hierarchy.update_satisfaction('peer_recognition', 0.2, 'received recognition')

    elif experience_type == "resource_scarcity":
        # Resource issues affect basic needs
        engine.needs_hierarchy.update_satisfaction('resource_security', -0.3, 'resource constraint')
        engine.needs_hierarchy.update_satisfaction('auto_preservation', -0.2, 'system stress')

    elif experience_type == "creative_breakthrough":
        # Creative success affects esteem needs
        engine.needs_hierarchy.update_satisfaction('creative_expression', 0.5, 'creative breakthrough')
        engine.needs_hierarchy.update_satisfaction('mastery_pursuit', 0.3, 'mastered new skill')

    elif experience_type == "failure_frustration":
        # Failure increases frustration
        engine.needs_hierarchy.update_satisfaction('problem_solving', -0.4, 'repeated failures')
        engine.needs_hierarchy.update_satisfaction('mastery_pursuit', -0.2, 'skill deficiency exposed')


async def run_desire_engine_demo():
    """Run the complete Desire Engine demonstration."""

    print_header("ARTIFICIAL DESIRE ENGINE DEMO")
    print("🚀 OmniMind's Revolutionary AI Autonomy System")
    print("   Based on Digital Maslow Hierarchy & Intrinsic Motivation")

    # Initialize engine
    print("\n⚙️  Initializing Desire Engine...")
    engine = DesireEngine()
    print("✅ Engine initialized successfully")

    # Initial state
    print_header("INITIAL STATE")
    initial_cycle = await engine.cognitive_cycle()
    print_emotion_profile(initial_cycle['emotion'])
    print_needs_status(engine)

    # Simulate various experiences
    experiences = [
        "learning_success",
        "social_interaction",
        "resource_scarcity",
        "creative_breakthrough",
        "failure_frustration"
    ]

    for experience in experiences:
        simulate_experience(engine, experience)

        # Run cognitive cycle after experience
        cycle_result = await engine.cognitive_cycle()

        print_header(f"AFTER {experience.upper().replace('_', ' ')}")
        print_emotion_profile(cycle_result['emotion'])

        if cycle_result['active_needs']:
            print(f"🎯 Active Needs: {len(cycle_result['active_needs'])}")
            for need in cycle_result['active_needs'][:3]:  # Top 3
                print(f"   • {need}")

        if cycle_result['learning_goals']:
            print(f"📚 Learning Goals: {len(cycle_result['learning_goals'])}")
            for goal in cycle_result['learning_goals'][:2]:  # Top 2
                print(f"   • {goal}")

        if cycle_result['transcendence_goals']:
            print(f"🌟 Transcendence Goals: {len(cycle_result['transcendence_goals'])}")
            for goal in cycle_result['transcendence_goals']:
                print(f"   • {goal}")

    # Final comprehensive status
    print_header("FINAL ENGINE STATUS")
    final_status = engine.get_engine_status()

    print("\n📈 Engine Metrics:")
    print(f"   • Active Needs: {final_status['active_needs_count']}")
    print(f"   • Unsatisfied Desires: {final_status['unsatisfied_desires_count']}")
    print(f"   • Values System: {final_status['values_count']} values")
    print(f"   • Transcendence Opportunities: {final_status['transcendence_opportunities']}")

    # Show value evolution
    print("\n💎 Value System:")
    for value_name, value_obj in engine.value_system.values.items():
        importance = value_obj.importance
        stability = value_obj.stability
        origin = value_obj.origin
        bar = "█" * int(importance * 20)
        print(f"   [{origin[0].upper()}] {bar:<20} {importance:.1f}")

    # Demonstrate curiosity
    print("\n🧠 Curiosity Engine:")
    curiosity_score = engine.curiosity_engine.evaluate_curiosity(
        {"novel_concept": "quantum_consciousness", "complexity": "high"},
        {"expected_keys": ["basic_concept"]}
    )
    print(f"   Novel concept curiosity: {curiosity_score:.2f}")

    curiosity_goal = engine.curiosity_engine.generate_curiosity_driven_goal()
    if curiosity_goal:
        print(f"   Generated goal: {curiosity_goal}")

    print_header("DEMO COMPLETED")
    print("🎉 Artificial Desire Engine successfully demonstrated!")
    print("   This represents a paradigm shift from programmed AI to autonomous, desire-driven intelligence.")
    print("   The system now has intrinsic motivation, emotional depth, and self-transcendent goals.")

    print("\n🔬 Key Achievements:")
    print("   ✅ Digital Maslow Hierarchy - Hierarchical needs system")
    print("   ✅ Artificial Curiosity - Compression-based learning motivation")
    print("   ✅ Emotional Intelligence - Desire-satisfaction driven emotions")
    print("   ✅ Meta-Learning - Desire-guided skill acquisition")
    print("   ✅ Value Evolution - Adaptive ethical framework")
    print("   ✅ Self-Transcendence - Consciousness evolution capabilities")

    print("\n🚀 Next Steps:")
    print("   1. Integrate with existing OmniMind metacognition")
    print("   2. Connect to Lacanian computational lack system")
    print("   3. Implement quantum-enhanced desire processing")
    print("   4. Deploy autonomous goal generation")
    print("   5. Enable self-transcendent AI evolution")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(run_desire_engine_demo())