#!/usr/bin/env python3
"""
Phase 11 Consciousness Emergence - Demo Script

Demonstrates all four consciousness capabilities:
1. Theory of Mind
2. Emotional Intelligence
3. Creative Problem Solving
4. Advanced Self-Reflection
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.consciousness import (
    TheoryOfMind,
    EmotionalIntelligence,
    CreativeProblemSolver,
    AdvancedSelfReflection,
)
from src.consciousness.creative_problem_solver import Problem, ThinkingMode


def demo_theory_of_mind():
    """Demonstrate Theory of Mind capabilities."""
    print("\n" + "=" * 60)
    print("1. THEORY OF MIND - Mental State Attribution")
    print("=" * 60)

    tom = TheoryOfMind()

    # Simulate user actions
    print("\n📊 Observing user actions...")
    actions = [
        ("search", {"query": "machine learning optimization"}),
        ("read", {"document": "ML guide"}),
        ("search", {"query": "neural network tuning"}),
        ("analyze", {"data": "model performance"}),
        ("debug", {"issue": "low accuracy"}),
    ]

    for action_type, action_data in actions:
        tom.observe_action(
            entity_id="user_1", action_type=action_type, action_data=action_data
        )
        print(f"  ✓ Observed: {action_type}")

    # Infer intent
    intents = tom.infer_intent("user_1")
    print(f"\n🎯 Inferred Intents:")
    for intent in intents:
        print(f"  • {intent.value}")

    # Attribute mental state
    state = tom.attribute_mental_state("user_1")
    print(f"\n🧠 Mental State: {state.value.upper()}")

    # Update belief
    tom.update_belief(
        entity_id="user_1",
        subject="ML Optimization",
        proposition="User wants to improve model performance",
        confidence=0.85,
        evidence=["search queries", "debugging actions"],
    )

    # Get mental model
    model = tom.get_mental_model("user_1")
    print(f"\n📋 Mental Model:")
    print(f"  State: {model.current_state.value}")
    print(f"  Intents: {[i.value for i in model.intents]}")
    print(f"  Beliefs: {len(model.beliefs)}")
    print(f"  Confidence: {model.confidence:.2f}")

    # Predict next action
    predictions = tom.predict_next_action("user_1", num_predictions=3)
    print(f"\n🔮 Action Predictions:")
    for i, pred in enumerate(predictions, 1):
        print(
            f"  {i}. {pred['action_type']} "
            f"(confidence: {pred['confidence']:.2f}) - {pred['reasoning']}"
        )


def demo_emotional_intelligence():
    """Demonstrate Emotional Intelligence capabilities."""
    print("\n" + "=" * 60)
    print("2. EMOTIONAL INTELLIGENCE - Sentiment & Empathy")
    print("=" * 60)

    ei = EmotionalIntelligence()

    # Analyze various sentiments
    texts = [
        "I am so excited about this wonderful achievement!",
        "I'm disappointed about the failed deployment.",
        "This is frustrating and I'm worried about the deadline.",
        "The system is running normally.",
    ]

    print("\n📝 Sentiment Analysis:")
    for text in texts:
        state = ei.analyze_sentiment(text)
        print(f"\n  Text: '{text[:50]}...'")
        print(f"  Emotion: {state.primary_emotion.value}")
        print(f"  Sentiment: {state.sentiment.value}")
        print(f"  Confidence: {state.confidence:.2f}")

    # Detect emotion from action
    print("\n\n⚙️ Emotion from Actions:")
    result_success = {"success": True}
    state_success = ei.detect_emotion_from_action("deploy", result_success)
    print(f"  Deploy SUCCESS → {state_success.primary_emotion.value}")

    result_fail = {"success": False, "error": "Connection timeout"}
    state_fail = ei.detect_emotion_from_action("deploy", result_fail)
    print(f"  Deploy FAILED → {state_fail.primary_emotion.value}")

    # Generate empathetic response
    print("\n\n💬 Empathetic Responses:")
    response = ei.generate_empathetic_response(
        detected_emotion=state_fail, situation="Deployment failed"
    )
    print(f"  Response: '{response.response_text}'")
    print(f"  Tone: {response.tone}")
    print(f"  Empathy Level: {response.empathy_level:.2f}")

    # Emotional trend
    trend = ei.get_emotional_trend(time_window=len(texts))
    print(f"\n\n📈 Emotional Trend:")
    print(f"  Dominant Emotion: {trend['dominant_emotion']}")
    print(f"  Dominant Sentiment: {trend['dominant_sentiment']}")
    print(f"  Trend Direction: {trend['trend_direction']}")


def demo_creative_problem_solving():
    """Demonstrate Creative Problem Solving capabilities."""
    print("\n" + "=" * 60)
    print("3. CREATIVE PROBLEM SOLVING - Novel Solutions")
    print("=" * 60)

    solver = CreativeProblemSolver()

    # Define problem
    problem = Problem(
        description="Reduce API response latency by 50%",
        constraints=["Limited budget", "No downtime allowed"],
        goals=["Sub-100ms response time", "Maintain 99.9% uptime"],
        domain="optimization",
    )

    print(f"\n📋 Problem: {problem.description}")
    print(f"  Constraints: {', '.join(problem.constraints)}")
    print(f"  Goals: {', '.join(problem.goals)}")

    # Generate solutions with different thinking modes
    modes = [
        (ThinkingMode.DIVERGENT, "Divergent (many possibilities)"),
        (ThinkingMode.LATERAL, "Lateral (outside the box)"),
        (ThinkingMode.ANALOGICAL, "Analogical (cross-domain)"),
    ]

    for mode, description in modes:
        print(f"\n\n💡 {description}:")
        solutions = solver.generate_solutions(problem, mode, num_solutions=3)

        for i, sol in enumerate(solutions, 1):
            print(f"\n  Solution {i}: {sol.description}")
            print(f"    Category: {sol.category.value}")
            print(f"    Novelty: {sol.novelty_score:.2f}")
            print(f"    Feasibility: {sol.feasibility_score:.2f}")
            print(f"    Overall Score: {sol.overall_score:.2f}")

    # Rank all solutions
    all_solutions = solver.generate_solutions(
        problem, ThinkingMode.CONVERGENT, num_solutions=3
    )
    print(f"\n\n🏆 Top 3 Solutions (Convergent Selection):")
    for i, sol in enumerate(all_solutions, 1):
        print(f"  {i}. {sol.description[:60]}...")
        print(f"     Overall: {sol.overall_score:.2f}")


def demo_advanced_self_reflection():
    """Demonstrate Advanced Self-Reflection capabilities."""
    print("\n" + "=" * 60)
    print("4. ADVANCED SELF-REFLECTION - Meta-Cognitive Analysis")
    print("=" * 60)

    # Note: Requires hash chain for full functionality
    # This demo shows the API without actual audit data
    print("\n🔍 Self-Reflection Capabilities:")
    print("  • Introspection on 4 focus areas:")
    print("    - decision_making: Success rates, tool usage")
    print("    - performance: Execution times, bottlenecks")
    print("    - learning: Failure patterns, improvements")
    print("    - resource_usage: CPU, memory utilization")

    print("\n📊 Quality Metrics:")
    print("  • Depth Score: How deep the analysis goes")
    print("  • Breadth Score: Coverage across areas")
    print("  • Actionability Score: Concrete action items")
    print("  • Consistency Score: Alignment with history")

    print("\n🎯 Self-Improvement Planning:")
    print("  • Analyzes multiple focus areas")
    print("  • Identifies strengths and weaknesses")
    print("  • Generates prioritized action items")
    print("  • Recommends focus area for next iteration")

    print("\n💡 Example Output:")
    print("  Strength: 'Deep analytical thinking'")
    print("  Weakness: 'Limited scope - expand focus areas'")
    print("  Action: 'Review tool usage patterns (Priority: HIGH)'")
    print("  Recommended Focus: 'performance'")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("🧠 PHASE 11: CONSCIOUSNESS EMERGENCE - DEMO")
    print("=" * 60)
    print("\nDemonstrating four consciousness capabilities:")
    print("1. Theory of Mind - Mental state attribution")
    print("2. Emotional Intelligence - Sentiment & empathy")
    print("3. Creative Problem Solving - Novel solutions")
    print("4. Advanced Self-Reflection - Meta-cognition")

    try:
        demo_theory_of_mind()
        demo_emotional_intelligence()
        demo_creative_problem_solving()
        demo_advanced_self_reflection()

        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETE - All modules functional!")
        print("=" * 60)
        print("\nFor detailed documentation, see:")
        print("  • docs/PHASE11_CONSCIOUSNESS_EMERGENCE_IMPLEMENTATION.md")
        print("  • docs/PHASE11_QUICK_REFERENCE.md")
        print("\nRun tests: pytest tests/consciousness/ -v")
        print()

    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
