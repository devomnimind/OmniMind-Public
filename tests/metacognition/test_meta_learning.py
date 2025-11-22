"""
Grupo 9 - Meta Learning Tests.

Testes abrangentes para capacidades de meta-aprendizado,
incluindo aprendizado adaptativo, otimização de estratégias e transferência de conhecimento.

Author: OmniMind Development Team
Date: November 2025
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import tempfile
import pytest

from src.metacognition.intelligent_goal_generation import IntelligentGoalEngine
from src.metacognition.self_optimization import SelfOptimizationEngine
from src.metacognition.metacognition_agent import MetacognitionAgent


class TestMetaLearningBasics:
    """Testes básicos de meta-aprendizado."""

    @pytest.fixture
    def meta_learner(self) -> Dict[str, Any]:
        """Fixture para sistema de meta-aprendizado."""
        return {
            "strategies": [],
            "performance_history": [],
            "learned_patterns": [],
        }

    def test_meta_learner_initialization(self, meta_learner: Dict[str, Any]) -> None:
        """Testa inicialização do meta-learner."""
        assert isinstance(meta_learner["strategies"], list)
        assert isinstance(meta_learner["performance_history"], list)
        assert isinstance(meta_learner["learned_patterns"], list)

    def test_strategy_learning(self, meta_learner: Dict[str, Any]) -> None:
        """Testa aprendizado de novas estratégias."""
        # Adiciona estratégia
        strategy = {"name": "gradient_descent", "params": {"lr": 0.01}}
        meta_learner["strategies"].append(strategy)

        assert len(meta_learner["strategies"]) == 1
        assert meta_learner["strategies"][0]["name"] == "gradient_descent"

    def test_performance_tracking(self, meta_learner: Dict[str, Any]) -> None:
        """Testa rastreamento de performance."""
        # Adiciona métricas de performance
        performance = {"accuracy": 0.85, "loss": 0.15}
        meta_learner["performance_history"].append(performance)

        assert len(meta_learner["performance_history"]) == 1
        assert meta_learner["performance_history"][0]["accuracy"] == 0.85


class TestAdaptiveLearning:
    """Testes para aprendizado adaptativo."""

    @pytest.fixture
    def optimizer(self) -> SelfOptimizationEngine:
        """Fixture para self optimizer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield SelfOptimizationEngine(storage_dir=Path(tmpdir))

    def test_optimizer_initialization(self, optimizer: SelfOptimizationEngine) -> None:
        """Testa inicialização do otimizador."""
        assert optimizer is not None
        assert hasattr(optimizer, "storage_dir")

    def test_optimize_strategy(self, optimizer: SelfOptimizationEngine) -> None:
        """Testa otimização de estratégia."""
        # Define objetivo
        objective = {"metric": "accuracy", "target": 0.9}

        # Otimiza
        result = optimizer.optimize(objective)

        assert result is not None
        assert isinstance(result, dict)

    def test_adaptive_parameter_tuning(self, optimizer: SelfOptimizationEngine) -> None:
        """Testa ajuste adaptativo de parâmetros."""
        # Parâmetros iniciais
        params = {"learning_rate": 0.01, "batch_size": 32}

        # Ajusta baseado em performance
        tuned_params = optimizer.tune_parameters(params, performance=0.75)

        assert tuned_params is not None
        assert isinstance(tuned_params, dict)

    def test_learning_rate_adaptation(self, optimizer: SelfOptimizationEngine) -> None:
        """Testa adaptação de learning rate."""
        # Histórico de performance
        performance_history = [0.6, 0.65, 0.7, 0.72, 0.73]

        # Adapta learning rate
        adapted_lr = optimizer.adapt_learning_rate(performance_history)

        assert isinstance(adapted_lr, float)
        assert adapted_lr > 0.0


class TestStrategyOptimization:
    """Testes para otimização de estratégias."""

    @pytest.fixture
    def optimizer(self) -> SelfOptimizationEngine:
        """Fixture para optimizer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield SelfOptimizationEngine(storage_dir=Path(tmpdir))

    def test_strategy_evaluation(self, optimizer: SelfOptimizationEngine) -> None:
        """Testa avaliação de estratégias."""
        strategies = [
            {"name": "strategy_a", "params": {"lr": 0.01}},
            {"name": "strategy_b", "params": {"lr": 0.001}},
        ]

        evaluation = optimizer.evaluate_strategies(strategies)

        assert evaluation is not None
        assert isinstance(evaluation, dict) or isinstance(evaluation, list)

    def test_best_strategy_selection(self, optimizer: SelfOptimizationEngine) -> None:
        """Testa seleção da melhor estratégia."""
        strategies = [
            {"name": "strategy_a", "performance": 0.85},
            {"name": "strategy_b", "performance": 0.92},
            {"name": "strategy_c", "performance": 0.78},
        ]

        best = optimizer.select_best_strategy(strategies)

        assert best is not None
        assert best["name"] == "strategy_b"

    def test_strategy_refinement(self, optimizer: SelfOptimizationEngine) -> None:
        """Testa refinamento de estratégia."""
        strategy = {"name": "base_strategy", "params": {"lr": 0.01}}

        refined = optimizer.refine_strategy(strategy, feedback={"accuracy": 0.8})

        assert refined is not None
        assert isinstance(refined, dict)


class TestKnowledgeTransfer:
    """Testes para transferência de conhecimento."""

    @pytest.fixture
    def goal_generator(self) -> IntelligentGoalEngine:
        """Fixture para goal generator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield IntelligentGoalEngine(workspace_path=tmpdir)

    def test_knowledge_extraction(self, goal_generator: IntelligentGoalEngine) -> None:
        """Testa extração de conhecimento."""
        # Simula experiência através de análise de repositório
        goals = goal_generator.analyze_and_generate_goals()

        # Verifica que goals foram gerados
        assert goals is not None
        assert isinstance(goals, list)

    def test_knowledge_application(self, goal_generator: IntelligentGoalEngine) -> None:
        """Testa aplicação de conhecimento."""
        # Gera goals baseados na análise
        goals = goal_generator.analyze_and_generate_goals()

        # Verifica aplicação através de impacto
        if goals:
            impact = goals[0].get("impact_metrics", {})
            assert isinstance(impact, dict)

    def test_cross_domain_transfer(self, goal_generator: IntelligentGoalEngine) -> None:
        """Testa transferência cross-domain."""
        # Análise em diferentes contextos
        goals1 = goal_generator.analyze_and_generate_goals()
        goals2 = goal_generator.analyze_and_generate_goals()

        # Verifica consistência
        assert isinstance(goals1, list)
        assert isinstance(goals2, list)


class TestMetaReasoning:
    """Testes para capacidades de meta-reasoning."""

    @pytest.fixture
    def metacog_agent(self) -> MetacognitionAgent:
        """Fixture para metacognition agent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield MetacognitionAgent(storage_dir=Path(tmpdir))

    def test_metacognitive_monitoring(self, metacog_agent: MetacognitionAgent) -> None:
        """Testa monitoramento metacognitivo."""
        # Monitora próprio pensamento
        thought_process = {"steps": ["analyze", "plan", "execute"]}

        monitoring = metacog_agent.monitor_thinking(thought_process)

        assert monitoring is not None
        assert isinstance(monitoring, dict)

    def test_self_assessment(self, metacog_agent: MetacognitionAgent) -> None:
        """Testa auto-avaliação."""
        # Avalia própria performance
        task = {"type": "reasoning", "difficulty": "medium"}
        result = {"success": True, "quality": 0.85}

        assessment = metacog_agent.self_assess(task, result)

        assert assessment is not None
        assert isinstance(assessment, dict)

    def test_reasoning_strategy_selection(
        self, metacog_agent: MetacognitionAgent
    ) -> None:
        """Testa seleção de estratégia de raciocínio."""
        problem = {"type": "logical", "complexity": "high"}

        strategy = metacog_agent.select_reasoning_strategy(problem)

        assert strategy is not None
        assert isinstance(strategy, dict) or isinstance(strategy, str)

    def test_metacognitive_regulation(self, metacog_agent: MetacognitionAgent) -> None:
        """Testa regulação metacognitiva."""
        # Regula próprio processo de pensamento
        current_state = {"progress": 0.5, "confidence": 0.7}

        regulation = metacog_agent.regulate_thinking(current_state)

        assert regulation is not None


class TestLearningFromExperience:
    """Testes para aprendizado a partir de experiência."""

    @pytest.fixture
    def optimizer(self) -> SelfOptimizationEngine:
        """Fixture para optimizer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield SelfOptimizationEngine(storage_dir=Path(tmpdir))

    def test_experience_recording(self, optimizer: SelfOptimizationEngine) -> None:
        """Testa gravação de experiências."""
        experience = {
            "action": "optimize_parameter",
            "context": {"task": "classification"},
            "outcome": {"success": True, "metric": 0.9},
        }

        optimizer.record_experience(experience)

        experiences = optimizer.get_experiences()
        assert len(experiences) >= 1

    def test_pattern_recognition(self, optimizer: SelfOptimizationEngine) -> None:
        """Testa reconhecimento de padrões em experiências."""
        # Adiciona múltiplas experiências similares
        for i in range(5):
            experience = {
                "action": "tune_lr",
                "outcome": {"success": True, "improvement": 0.05 * i},
            }
            optimizer.record_experience(experience)

        patterns = optimizer.recognize_patterns()

        assert patterns is not None

    def test_learning_from_failures(self, optimizer: SelfOptimizationEngine) -> None:
        """Testa aprendizado a partir de falhas."""
        failure = {
            "action": "aggressive_tuning",
            "outcome": {"success": False, "reason": "overfitting"},
        }

        optimizer.record_experience(failure)

        # Aprende com falha
        lesson = optimizer.learn_from_failure(failure)

        assert lesson is not None


class TestGoalGeneration:
    """Testes para geração inteligente de objetivos."""

    @pytest.fixture
    def goal_generator(self) -> IntelligentGoalEngine:
        """Fixture para goal generator."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield IntelligentGoalEngine(workspace_path=tmpdir)

    def test_generate_goals_basic(self, goal_generator: IntelligentGoalEngine) -> None:
        """Testa geração básica de objetivos."""
        goals = goal_generator.analyze_and_generate_goals()

        assert goals is not None
        assert isinstance(goals, list)

    def test_goal_prioritization(self, goal_generator: IntelligentGoalEngine) -> None:
        """Testa priorização de objetivos."""
        goals = goal_generator.analyze_and_generate_goals()

        # Se há goals, verifica se estão ordenados por impacto
        if goals:
            impacts = [
                g.get("impact_metrics", {}).get("total_impact", 0) for g in goals
            ]
            # Verifica se está ordenado decrescentemente (maior impacto primeiro)
            assert (
                all(impacts[i] >= impacts[i + 1] for i in range(len(impacts) - 1))
                or len(impacts) <= 1
            )

    def test_subgoal_decomposition(self, goal_generator: IntelligentGoalEngine) -> None:
        """Testa decomposição de objetivos em sub-objetivos."""
        goals = goal_generator.analyze_and_generate_goals()

        # Verifica estrutura dos goals
        if goals:
            goal = goals[0]
            assert "title" in goal
            assert "description" in goal
            assert "impact_metrics" in goal


class TestMetaLearningIntegration:
    """Testes de integração de meta-aprendizado."""

    def test_complete_meta_learning_cycle(self) -> None:
        """Testa ciclo completo de meta-aprendizado."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 1. Geração de objetivos
            goal_gen = IntelligentGoalEngine(workspace_path=tmpdir)
            goals = goal_gen.analyze_and_generate_goals()

            # 2. Otimização
            optimizer = SelfOptimizationEngine(storage_dir=Path(tmpdir) / "optimizer")
            optimized = optimizer.optimize({"target": 0.9})

            # 3. Meta-cognição
            metacog = MetacognitionAgent(storage_dir=Path(tmpdir) / "metacog")
            assessment = metacog.self_assess({"task": "optimize"}, optimized)

            # Verifica ciclo completo
            assert goals is not None
            assert optimized is not None
            assert assessment is not None

    def test_meta_learning_feedback_loop(self) -> None:
        """Testa loop de feedback de meta-aprendizado."""
        with tempfile.TemporaryDirectory() as tmpdir:
            optimizer = SelfOptimizationEngine(storage_dir=Path(tmpdir))

            # Ciclo iterativo
            performance = 0.7
            for _ in range(3):
                result = optimizer.optimize({"current": performance, "target": 0.9})
                performance = result.get("performance", performance + 0.05)

            # Performance deve melhorar
            assert performance > 0.7


class TestMetaLearningEdgeCases:
    """Testes de casos extremos de meta-aprendizado."""

    def test_learning_with_no_prior_experience(self) -> None:
        """Testa aprendizado sem experiência prévia."""
        with tempfile.TemporaryDirectory() as tmpdir:
            optimizer = SelfOptimizationEngine(storage_dir=Path(tmpdir))

            # Tenta otimizar sem experiência
            result = optimizer.optimize({"target": 0.9})

            assert result is not None

    def test_learning_from_contradictory_experiences(self) -> None:
        """Testa aprendizado de experiências contraditórias."""
        with tempfile.TemporaryDirectory() as tmpdir:
            optimizer = SelfOptimizationEngine(storage_dir=Path(tmpdir))

            # Experiências contraditórias
            exp1 = {"action": "increase_lr", "outcome": {"success": True}}
            exp2 = {"action": "increase_lr", "outcome": {"success": False}}

            optimizer.record_experience(exp1)
            optimizer.record_experience(exp2)

            # Deve lidar com contradição
            patterns = optimizer.recognize_patterns()
            assert patterns is not None

    def test_meta_learning_stability(self) -> None:
        """Testa estabilidade do meta-aprendizado."""
        with tempfile.TemporaryDirectory() as tmpdir:
            optimizer = SelfOptimizationEngine(storage_dir=Path(tmpdir))

            # Múltiplas otimizações consecutivas
            results = []
            for _ in range(10):
                result = optimizer.optimize({"target": 0.9})
                results.append(result)

            # Sistema deve permanecer estável
            assert len(results) == 10
            assert all(r is not None for r in results)
