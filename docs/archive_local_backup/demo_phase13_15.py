#!/usr/bin/env python3
"""
Comprehensive Demonstration of Phases 13-15 Implementation.

This script demonstrates:
- Phase 13: Autonomous Decision Making
- Phase 14: Collective Intelligence
- Phase 15: Quantum-Enhanced AI

Author: OmniMind Project
Date: 2025-11-19
"""

import math
import random
from typing import Any, Dict, List

# Phase 13 imports
from src.decision_making import (
    DecisionTreeBuilder,
    DecisionCriterion,
    QLearningAgent,
    RLState,
    RLAction,
    RLReward,
    EthicalDecisionMaker,
    EthicalDilemma,
    EthicalFramework,
    GoalSetter,
    GoalPriority,
)

# Phase 14 imports
from src.collective_intelligence import (
    ParticleSwarmOptimizer,
    AntColonyOptimizer,
    DistributedProblem,
    DistributedSolver,
    EmergenceDetector,
    CollectiveLearner,
    SharedExperience,
)

# Phase 15 imports
from src.quantum_ai import (
    GroverSearch,
    QuantumAnnealer,
    SuperpositionProcessor,
    QuantumClassifier,
    QAOAOptimizer,
)


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def demo_phase13_decision_trees() -> None:
    """Demonstrate intelligent decision trees."""
    print_section("PHASE 13.1: Intelligent Decision Trees")

    # Build a simple decision tree
    builder = DecisionTreeBuilder(name="approval_tree")

    builder.add_node(
        node_id="root",
        criterion_type=DecisionCriterion.THRESHOLD,
        question="Credit score >= 700?",
        threshold=700,
    )
    builder.add_node(
        node_id="approved",
        criterion_type=DecisionCriterion.THRESHOLD,
        question="",
        action="approve_loan",
    )
    builder.add_node(
        node_id="denied",
        criterion_type=DecisionCriterion.THRESHOLD,
        question="",
        action="deny_loan",
    )

    builder.add_edge("root", "approved", "high")
    builder.add_edge("root", "denied", "low")

    tree = builder.build(enable_adaptation=True)

    # Make decisions
    print("Making loan approval decisions...")
    test_cases = [
        {"value": 750, "expected": "approve_loan"},
        {"value": 650, "expected": "deny_loan"},
        {"value": 800, "expected": "approve_loan"},
    ]

    for i, case in enumerate(test_cases, 1):
        outcome = tree.decide(case)
        print(f"\n  Case {i}: Credit Score = {case['value']}")
        print(f"    Decision: {outcome.action}")
        print(f"    Confidence: {outcome.confidence:.2f}")
        print(f"    Path: {' → '.join(outcome.path)}")

        # Provide feedback
        success = outcome.action == case["expected"]
        tree.provide_feedback(outcome, success)

    # Show performance metrics
    metrics = tree.get_performance_metrics()
    print(f"\n  Performance Metrics:")
    print(f"    Total Decisions: {metrics['total_decisions']}")
    print(f"    Success Rate: {metrics['success_rate']:.1%}")
    print(f"    Tree Depth: {metrics['tree_depth']}")


def demo_phase13_reinforcement_learning() -> None:
    """Demonstrate reinforcement learning."""
    print_section("PHASE 13.2: Reinforcement Learning")

    # Create Q-Learning agent
    agent = QLearningAgent(
        name="grid_navigator",
        learning_rate=0.1,
        discount_factor=0.95,
        exploration_rate=0.2,
    )

    print("Training Q-Learning agent on grid navigation...")

    # Simulate training episodes
    num_episodes = 50
    for episode in range(num_episodes):
        # Simulate an episode
        state = RLState(features={"position": 0})
        total_reward = 0

        for step in range(10):
            # Available actions
            actions = [
                RLAction("move_left"),
                RLAction("move_right"),
                RLAction("stay"),
            ]

            # Select action
            action = agent.select_action(state, actions)

            # Simulate environment response
            next_position = state.features["position"]
            if action.action_id == "move_right":
                next_position = min(10, next_position + 1)
                reward_value = 1.0 if next_position == 10 else 0.1
            elif action.action_id == "move_left":
                next_position = max(0, next_position - 1)
                reward_value = -0.1
            else:
                reward_value = -0.05

            next_state = RLState(features={"position": next_position})
            reward = RLReward(value=reward_value)
            done = next_position == 10

            # Update agent
            from src.decision_making.reinforcement_learning import RLTransition

            transition = RLTransition(
                state=state,
                action=action,
                next_state=next_state,
                reward=reward,
                done=done,
            )
            agent.update(transition)

            total_reward += reward_value
            state = next_state

            if done:
                break

        # Decay exploration
        if episode % 10 == 0:
            agent.decay_exploration()

    # Show learned policy
    metrics = agent.get_policy_metrics()
    print(f"\n  Learned Policy Metrics:")
    print(f"    States Explored: {metrics['num_states']}")
    print(f"    Actions Learned: {metrics['num_actions']}")
    print(f"    Average Q-Value: {metrics['avg_q_value']:.2f}")
    print(f"    Total Reward: {metrics['total_reward']:.1f}")


def demo_phase13_ethical_decisions() -> None:
    """Demonstrate ethical decision making."""
    print_section("PHASE 13.3: Ethical Decision Framework")

    maker = EthicalDecisionMaker(primary_framework=EthicalFramework.HYBRID)

    # Create an ethical dilemma
    dilemma = EthicalDilemma(
        dilemma_id="privacy_vs_security",
        description="Should we share user data to prevent a security threat?",
        options=[
            "Share all data immediately",
            "Share minimal data with consent",
            "Do not share any data",
        ],
        stakeholders=["users", "company", "public"],
    )

    print(f"Ethical Dilemma: {dilemma.description}")
    print(f"\nOptions:")
    for i, option in enumerate(dilemma.options, 1):
        print(f"  {i}. {option}")

    # Make ethical decision
    outcome = maker.decide(dilemma)

    print(f"\n  Decision: {outcome.chosen_option}")
    print(f"  Framework: {outcome.framework_used.value}")
    print(f"  Ethical Score: {outcome.ethical_score:.2f}")
    print(f"  Confidence: {outcome.confidence:.2f}")
    print(f"\n  Justification:")
    for line in outcome.justification.split(" | "):
        print(f"    {line}")

    # Show ethics metrics
    metrics = maker.get_ethics_metrics()
    print(f"\n  Ethics Metrics:")
    print(f"    Total Decisions: {metrics['total_decisions']}")
    print(f"    Average Ethical Score: {metrics['avg_ethical_score']:.2f}")


def demo_phase13_goal_setting() -> None:
    """Demonstrate autonomous goal setting."""
    print_section("PHASE 13.4: Autonomous Goal Setting")

    setter = GoalSetter(max_concurrent_goals=3)

    print("Generating autonomous goals based on system context...")

    # Generate goals based on different contexts
    contexts = [
        {"resource_usage": 0.85, "error_rate": 0.05},
        {"performance_score": 0.65, "user_satisfaction": 0.75},
        {"security_score": 0.88, "critical_error": False},
    ]

    for i, context in enumerate(contexts, 1):
        goal = setter.generate_goal(context)
        print(f"\n  Goal {i}:")
        print(f"    Description: {goal.description}")
        print(f"    Priority: {goal.priority.name}")
        print(f"    Deadline: {goal.time_remaining():.0f} seconds from now")

        # Activate goal
        if setter.activate_goal(goal.goal_id):
            print(f"    Status: ACTIVATED")

    # Show metrics
    metrics = setter.get_metrics()
    print(f"\n  Goal Setting Metrics:")
    print(f"    Total Goals: {metrics['total_goals']}")
    print(f"    Active Goals: {metrics['active_goals']}")
    print(f"    Pending Goals: {metrics['pending_goals']}")


def demo_phase14_swarm_intelligence() -> None:
    """Demonstrate swarm intelligence."""
    print_section("PHASE 14.1: Swarm Intelligence (PSO)")

    # Define a simple optimization problem (Sphere function)
    def sphere_function(x: List[float]) -> float:
        return sum(xi**2 for xi in x)

    print("Optimizing 2D Sphere function using Particle Swarm Optimization...")
    print("  Objective: minimize f(x, y) = x² + y²")
    print("  Optimal solution: (0, 0) with value 0")

    optimizer = ParticleSwarmOptimizer(dimension=2, population_size=20)

    best_position, best_value = optimizer.optimize(
        objective=sphere_function,
        max_iterations=50,
    )

    print(f"\n  PSO Results:")
    print(f"    Best Position: ({best_position[0]:.4f}, {best_position[1]:.4f})")
    print(f"    Best Value: {best_value:.6f}")
    print(f"    Error from Optimal: {best_value:.6f}")

    # Ant Colony Optimization for TSP
    print("\n  Ant Colony Optimization for Traveling Salesman Problem...")

    # Create a small distance matrix (5 cities)
    num_cities = 5
    distance_matrix = [[0.0] * num_cities for _ in range(num_cities)]
    for i in range(num_cities):
        for j in range(i + 1, num_cities):
            dist = random.uniform(10, 100)
            distance_matrix[i][j] = dist
            distance_matrix[j][i] = dist

    aco = AntColonyOptimizer(num_ants=20)
    best_path, best_cost = aco.optimize(distance_matrix, max_iterations=30)

    print(f"\n  ACO Results:")
    print(f"    Best Path: {best_path}")
    print(f"    Total Distance: {best_cost:.2f}")


def demo_phase14_distributed_solving() -> None:
    """Demonstrate distributed problem solving."""
    print_section("PHASE 14.2: Distributed Problem Solving")

    # Create a distributed problem
    problem = DistributedProblem(
        description="Compute sum of large dataset",
        data={"items": list(range(100))},
        num_subtasks=5,
    )

    # Create distributed solver
    solver = DistributedSolver(num_agents=5)

    # Define agent solver function
    def agent_solver(subtask: Dict[str, Any]) -> Dict[str, Any]:
        items = subtask["data"].get("items", [])
        partial_sum = sum(items)
        return {
            "result": partial_sum,
            "confidence": 0.95,
        }

    print(f"Problem: {problem.description}")
    print(f"  Dataset size: 100 items")
    print(f"  Number of agents: 5")

    # Solve distributedly
    solution = solver.solve(problem, agent_solver)

    print(f"\n  Solution:")
    print(f"    Result: {solution.result}")
    print(f"    Confidence: {solution.confidence:.2f}")
    print(f"    Consensus Score: {solution.consensus_score:.2f}")
    print(f"    Agents Contributed: {len(solution.agent_contributions)}")


def demo_phase14_emergent_behaviors() -> None:
    """Demonstrate emergent behavior detection."""
    print_section("PHASE 14.3: Emergent Behavior Detection")

    detector = EmergenceDetector()

    # Simulate agent states
    agent_states = [
        {
            "agent_id": f"agent_{i}",
            "action": "cooperate",
            "value": 0.7 + random.uniform(-0.1, 0.1),
        }
        for i in range(10)
    ]

    print("Detecting emergent patterns in multi-agent system...")
    print(f"  Number of agents: {len(agent_states)}")

    patterns = detector.detect_patterns(agent_states)

    print(f"\n  Patterns Detected: {len(patterns)}")
    for pattern in patterns:
        print(f"\n    Pattern Type: {pattern.pattern_type.value}")
        print(f"    Confidence: {pattern.confidence:.2f}")
        print(f"    Participants: {len(pattern.participants)}")
        print(f"    Characteristics: {pattern.characteristics}")


def demo_phase14_collective_learning() -> None:
    """Demonstrate collective learning."""
    print_section("PHASE 14.4: Collective Learning")

    learner = CollectiveLearner(num_agents=5, use_federated=False)

    print("Training agents collectively through shared experiences...")

    # Simulate shared experiences from multiple agents
    for agent_id in range(5):
        for episode in range(3):
            experience = SharedExperience(
                agent_id=f"agent_{agent_id}",
                context={"episode": episode},
                action=f"action_{random.randint(0, 2)}",
                outcome=random.uniform(0.5, 1.0),
                confidence=0.8,
            )
            learner.learn_from_experience(f"agent_{agent_id}", experience)

    # Get collective model
    model = learner.get_collective_model()

    print(f"\n  Collective Learning Results:")
    print(f"    Agents Participated: 5")
    print(f"    Total Experiences: 15")
    print(f"    Collective Model Parameters: {len(model)}")


def demo_phase15_quantum_algorithms() -> None:
    """Demonstrate quantum algorithms."""
    print_section("PHASE 15.1: Quantum Algorithms")

    # Grover's Search
    print("Grover's Quantum Search Algorithm")
    print("  Searching for marked item in database of size 16...")

    # Target item
    target = 7

    def oracle(index: int) -> bool:
        return index == target

    grover = GroverSearch(search_space_size=16)
    result = grover.search(oracle)

    print(f"\n  Search Results:")
    print(f"    Target Item: {target}")
    print(f"    Found Item: {result}")
    print(f"    Correct: {'✓' if result == target else '✗'}")

    # Quantum Annealing
    print("\n  Quantum Annealing for Optimization")
    print("  Minimizing function: f(x) = sum(xi²)")

    def energy_function(state: List[int]) -> float:
        # Convert binary to real values
        x = [(2 * bit - 1) for bit in state]
        return sum(xi**2 for xi in x)

    annealer = QuantumAnnealer(num_variables=4)
    best_state, best_energy = annealer.anneal(energy_function, num_steps=100)

    print(f"\n  Annealing Results:")
    print(f"    Best State: {best_state}")
    print(f"    Best Energy: {best_energy:.4f}")


def demo_phase15_superposition() -> None:
    """Demonstrate superposition computing."""
    print_section("PHASE 15.2: Superposition Computing")

    processor = SuperpositionProcessor()

    # Quantum parallel function evaluation
    def square(x: float) -> float:
        return x**2

    inputs = [1, 2, 3, 4, 5]

    print(f"Evaluating function in quantum superposition...")
    print(f"  Function: f(x) = x²")
    print(f"  Inputs: {inputs}")

    superposition = processor.evaluate_parallel(square, inputs)

    print(f"\n  Superposition Results:")
    print(f"    Number of states: {len(superposition.states)}")
    print(f"    Results: {superposition.states}")

    # Collapse to single result
    result = superposition.collapse()
    print(f"    Collapsed to: {result}")


def demo_phase15_quantum_ml() -> None:
    """Demonstrate quantum machine learning."""
    print_section("PHASE 15.3: Quantum Machine Learning")

    # Generate sample data
    print("Training Quantum Classifier...")

    X_train = [
        [0.1, 0.2],
        [0.2, 0.3],
        [0.8, 0.9],
        [0.9, 0.8],
    ]
    y_train = [0, 0, 1, 1]

    classifier = QuantumClassifier(num_qubits=4)
    classifier.fit(X_train, y_train)

    print(f"  Training Data: {len(X_train)} samples")

    # Make predictions
    test_samples = [[0.15, 0.25], [0.85, 0.85]]

    print(f"\n  Predictions:")
    for i, sample in enumerate(test_samples, 1):
        prediction = classifier.predict(sample)
        proba = classifier.predict_proba(sample)
        print(f"    Sample {i}: {sample}")
        print(f"      Predicted Class: {prediction}")
        print(f"      Probabilities: Class 0={proba[0]:.2f}, Class 1={proba[1]:.2f}")


def demo_phase15_quantum_optimization() -> None:
    """Demonstrate quantum optimization."""
    print_section("PHASE 15.4: Quantum Optimization (QAOA)")

    # Define optimization problem
    def rastrigin(x: List[float]) -> float:
        """Rastrigin function (challenging optimization problem)."""
        A = 10
        n = len(x)
        return A * n + sum(xi**2 - A * math.cos(2 * math.pi * xi) for xi in x)

    print("Optimizing Rastrigin function using QAOA...")
    print("  Dimension: 2")
    print("  Optimal solution: (0, 0)")

    optimizer = QAOAOptimizer(dimension=2, num_layers=3)

    bounds = [(-5.12, 5.12), (-5.12, 5.12)]
    best_solution, best_value = optimizer.optimize(rastrigin, bounds, max_iterations=30)

    print(f"\n  QAOA Results:")
    print(f"    Best Solution: ({best_solution[0]:.4f}, {best_solution[1]:.4f})")
    print(f"    Best Value: {best_value:.4f}")
    print(f"    Global Optimum: 0.0")


def main() -> None:
    """Run all demonstrations."""
    print("\n" + "=" * 80)
    print("  OmniMind Phase 13-15 Comprehensive Demonstration")
    print("  Advanced Autonomous AI Capabilities")
    print("=" * 80)

    # Phase 13: Autonomous Decision Making
    demo_phase13_decision_trees()
    demo_phase13_reinforcement_learning()
    demo_phase13_ethical_decisions()
    demo_phase13_goal_setting()

    # Phase 14: Collective Intelligence
    demo_phase14_swarm_intelligence()
    demo_phase14_distributed_solving()
    demo_phase14_emergent_behaviors()
    demo_phase14_collective_learning()

    # Phase 15: Quantum-Enhanced AI
    demo_phase15_quantum_algorithms()
    demo_phase15_superposition()
    demo_phase15_quantum_ml()
    demo_phase15_quantum_optimization()

    print("\n" + "=" * 80)
    print("  Demonstration Complete!")
    print("  All Phase 13-15 capabilities successfully showcased")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
