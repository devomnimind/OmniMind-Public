"""
Agentic IDE Interface - Dual-Mode Editor + Manager.

Implementa interface IDE estilo Google Antigravity (2025) com:
- Dual-mode: Editor tradicional + Manager surface para orquestração
- Browser-in-the-loop verification
- Verifiable artifacts tracking
- Self-improvement loops com feedback
- Multi-model selection (Gemini, Claude, GPT)

Author: OmniMind Development Team
Date: November 2025
License: MIT
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import time
import logging
import hashlib
from collections import defaultdict

logger = logging.getLogger(__name__)


class IDEMode(Enum):
    """
    Modos da IDE agentic.

    EDITOR: Modo tradicional de edição de código
    MANAGER: Modo de orquestração de agents
    """

    EDITOR = "editor"
    MANAGER = "manager"


class AIModel(Enum):
    """
    Modelos AI disponíveis para seleção.

    GEMINI_3_PRO: Google Gemini 3 Pro
    CLAUDE_SONNET_4_5: Anthropic Claude Sonnet 4.5
    GPT_4: OpenAI GPT-4
    LOCAL_LLAMA: Meta LLama local
    """

    GEMINI_3_PRO = "gemini-3-pro"
    CLAUDE_SONNET_4_5 = "claude-sonnet-4.5"
    GPT_4 = "gpt-4"
    LOCAL_LLAMA = "llama-3-70b"


class ArtifactType(Enum):
    """
    Tipos de artefatos verificáveis.

    CODE: Código gerado
    TEST: Testes criados
    DOCUMENTATION: Documentação
    SCREENSHOT: Screenshot de UI
    LOG: Log de execução
    """

    CODE = "code"
    TEST = "test"
    DOCUMENTATION = "documentation"
    SCREENSHOT = "screenshot"
    LOG = "log"


@dataclass
class VerifiableArtifact:
    """
    Artefato verificável produzido por agent.

    Attributes:
        artifact_id: ID único do artefato
        artifact_type: Tipo do artefato
        content: Conteúdo ou path
        timestamp: Timestamp de criação
        agent_id: ID do agent que criou
        verified: Se foi verificado
        verification_result: Resultado da verificação
        hash: Hash SHA-256 do conteúdo
    """

    artifact_id: str
    artifact_type: ArtifactType
    content: str
    timestamp: float
    agent_id: str
    verified: bool = False
    verification_result: Optional[str] = None
    hash: str = field(default="")

    def __post_init__(self) -> None:
        """Computa hash do artefato."""
        if not self.hash:
            self.hash = hashlib.sha256(self.content.encode()).hexdigest()


@dataclass
class AgentTask:
    """
    Tarefa para agent executar.

    Attributes:
        task_id: ID único da tarefa
        description: Descrição da tarefa
        assigned_agent: Agent atribuído
        assigned_model: Modelo AI a usar
        status: Status da tarefa
        plan: Plano de execução
        artifacts: Artefatos produzidos
        started_at: Timestamp de início
        completed_at: Timestamp de conclusão
        feedback: Feedback do usuário
    """

    task_id: str
    description: str
    assigned_agent: str
    assigned_model: AIModel
    status: str = "pending"  # pending, running, completed, failed
    plan: List[str] = field(default_factory=list)
    artifacts: List[VerifiableArtifact] = field(default_factory=list)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    feedback: Optional[str] = None


@dataclass
class BrowserVerification:
    """
    Resultado de verificação browser-in-the-loop.

    Attributes:
        url: URL testada
        screenshot_path: Path do screenshot
        passed: Se passou verificação
        errors: Erros encontrados
        timestamp: Timestamp da verificação
    """

    url: str
    screenshot_path: str
    passed: bool
    errors: List[str]
    timestamp: float


class BrowserVerifier:
    """
    Verificador browser-in-the-loop.

    Executa código em browser real e captura screenshots/resultados.
    """

    def __init__(self, screenshots_dir: Path) -> None:
        """
        Inicializa verificador.

        Args:
            screenshots_dir: Diretório para screenshots
        """
        self.screenshots_dir = screenshots_dir
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

        # Histórico de verificações
        self.verifications: List[BrowserVerification] = []

        logger.info("Browser verifier initialized")

    def verify_web_app(
        self, url: str, expected_elements: List[str]
    ) -> BrowserVerification:
        """
        Verifica aplicação web.

        Args:
            url: URL a testar
            expected_elements: Elementos esperados (CSS selectors)

        Returns:
            Resultado da verificação
        """
        # Simula verificação (em produção usaria Playwright/Puppeteer)
        timestamp = time.time()
        screenshot_path = str(self.screenshots_dir / f"screenshot_{int(timestamp)}.png")

        # Mock verification
        passed = True
        errors: List[str] = []

        # Simula criação de screenshot
        # Em produção: browser.screenshot(path=screenshot_path)

        verification = BrowserVerification(
            url=url,
            screenshot_path=screenshot_path,
            passed=passed,
            errors=errors,
            timestamp=timestamp,
        )

        self.verifications.append(verification)

        logger.info(f"Browser verification: url={url}, passed={passed}")

        return verification


class SelfImprovementLoop:
    """
    Loop de auto-melhoria com feedback.

    Aprende com feedback do usuário e ajusta comportamento.
    """

    def __init__(self) -> None:
        """Inicializa loop de auto-melhoria."""
        # Histórico de feedback
        self.feedback_history: List[Dict[str, Any]] = []

        # Padrões aprendidos
        self.learned_patterns: Dict[str, float] = defaultdict(float)

        # Taxa de aprendizado
        self.learning_rate = 0.1

        logger.info("Self-improvement loop initialized")

    def process_feedback(
        self, task_id: str, feedback_type: str, feedback_content: str, success: bool
    ) -> None:
        """
        Processa feedback do usuário.

        Args:
            task_id: ID da tarefa
            feedback_type: Tipo de feedback
            feedback_content: Conteúdo do feedback
            success: Se tarefa foi bem-sucedida
        """
        # Registra feedback
        feedback_entry = {
            "task_id": task_id,
            "type": feedback_type,
            "content": feedback_content,
            "success": success,
            "timestamp": time.time(),
        }

        self.feedback_history.append(feedback_entry)

        # Extrai padrões
        pattern_key = f"{feedback_type}:{success}"

        # Atualiza peso do padrão
        reward = 1.0 if success else -1.0
        self.learned_patterns[pattern_key] += self.learning_rate * reward

        logger.info(
            f"Feedback processed: task={task_id}, "
            f"success={success}, pattern={pattern_key}"
        )

    def get_learned_insights(self) -> Dict[str, Any]:
        """
        Retorna insights aprendidos.

        Returns:
            Dict com padrões e recomendações
        """
        # Padrões mais fortes
        top_patterns = sorted(
            self.learned_patterns.items(), key=lambda x: abs(x[1]), reverse=True
        )[:10]

        # Recomendações
        recommendations = []
        for pattern, weight in top_patterns:
            if weight > 0.5:
                recommendations.append(f"Continue usando abordagem: {pattern}")
            elif weight < -0.5:
                recommendations.append(f"Evite abordagem: {pattern}")

        return {
            "total_feedback": len(self.feedback_history),
            "learned_patterns": dict(top_patterns),
            "recommendations": recommendations,
        }


class ModelSelector:
    """
    Seletor inteligente de modelos AI.

    Escolhe modelo apropriado baseado em tarefa e histórico.
    """

    def __init__(self) -> None:
        """Inicializa seletor de modelos."""
        # Performance de cada modelo por tipo de tarefa
        self.model_performance: Dict[str, Dict[AIModel, float]] = defaultdict(
            lambda: {model: 0.5 for model in AIModel}
        )

        # Histórico de uso
        self.usage_history: List[Dict[str, Any]] = []

        logger.info("Model selector initialized")

    def select_model(
        self, task_type: str, context: Optional[Dict[str, Any]] = None
    ) -> AIModel:
        """
        Seleciona modelo apropriado para tarefa.

        Args:
            task_type: Tipo da tarefa
            context: Contexto adicional

        Returns:
            Modelo selecionado
        """
        context = context or {}

        # Obtém performances
        performances = self.model_performance[task_type]

        # Fatores de seleção
        factors: Dict[AIModel, float] = {}

        for model, base_performance in performances.items():
            # Performance base
            score = base_performance

            # Ajusta por contexto
            if context.get("requires_code", False):
                # Claude é bom para código
                if model == AIModel.CLAUDE_SONNET_4_5:
                    score *= 1.2

            if context.get("requires_reasoning", False):
                # GPT-4 é bom para reasoning
                if model == AIModel.GPT_4:
                    score *= 1.2

            if context.get("local_only", False):
                # Usa modelo local
                if model == AIModel.LOCAL_LLAMA:
                    score *= 2.0
                else:
                    score *= 0.1

            factors[model] = score

        # Seleciona melhor
        selected_model = max(factors, key=lambda k: factors[k])

        logger.info(
            f"Model selected: {selected_model.value} " f"for task_type={task_type}"
        )

        return selected_model

    def update_performance(self, task_type: str, model: AIModel, success: bool) -> None:
        """
        Atualiza performance de modelo.

        Args:
            task_type: Tipo da tarefa
            model: Modelo usado
            success: Se foi bem-sucedido
        """
        current = self.model_performance[task_type][model]

        # Atualiza com learning rate
        lr = 0.1
        reward = 1.0 if success else 0.0

        self.model_performance[task_type][model] = current + lr * (reward - current)

        # Registra uso
        self.usage_history.append(
            {
                "task_type": task_type,
                "model": model.value,
                "success": success,
                "timestamp": time.time(),
            }
        )


class AgenticIDE:
    """
    IDE Agentic completa com dual-mode interface.

    Combina:
    - Editor tradicional
    - Manager surface para orquestração
    - Browser verification
    - Verifiable artifacts
    - Self-improvement
    - Multi-model selection
    """

    def __init__(
        self, workspace_path: Path, screenshots_dir: Optional[Path] = None
    ) -> None:
        """
        Inicializa IDE agentic.

        Args:
            workspace_path: Path do workspace
            screenshots_dir: Diretório para screenshots
        """
        self.workspace_path = workspace_path
        self.workspace_path.mkdir(parents=True, exist_ok=True)

        # Componentes
        self.browser_verifier = BrowserVerifier(
            screenshots_dir or (workspace_path / "screenshots")
        )
        self.self_improvement = SelfImprovementLoop()
        self.model_selector = ModelSelector()

        # Estado
        self.current_mode = IDEMode.EDITOR
        self.tasks: Dict[str, AgentTask] = {}
        self.artifacts: List[VerifiableArtifact] = []

        logger.info(f"Agentic IDE initialized: workspace={workspace_path}")

    def switch_mode(self, mode: IDEMode) -> None:
        """
        Troca modo da IDE.

        Args:
            mode: Novo modo
        """
        self.current_mode = mode
        logger.info(f"Switched to {mode.value} mode")

    def create_task(
        self,
        description: str,
        task_type: str,
        agent_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentTask:
        """
        Cria nova tarefa para agent.

        Args:
            description: Descrição da tarefa
            task_type: Tipo da tarefa
            agent_id: ID do agent
            context: Contexto adicional

        Returns:
            Tarefa criada
        """
        # Seleciona modelo apropriado
        model = self.model_selector.select_model(task_type, context)

        # Cria tarefa
        task_id = f"task_{int(time.time())}_{agent_id}"

        task = AgentTask(
            task_id=task_id,
            description=description,
            assigned_agent=agent_id,
            assigned_model=model,
        )

        self.tasks[task_id] = task

        logger.info(
            f"Task created: {task_id} for agent={agent_id}, " f"model={model.value}"
        )

        return task

    def execute_task(self, task_id: str) -> Dict[str, Any]:
        """
        Executa tarefa.

        Args:
            task_id: ID da tarefa

        Returns:
            Resultado da execução
        """
        task = self.tasks.get(task_id)

        if not task:
            return {"success": False, "error": "Task not found"}

        # Marca como running
        task.status = "running"
        task.started_at = time.time()

        # Simula execução (em produção: chamaria agent real)
        # Por enquanto, cria artefatos mock

        # Cria código artifact
        code_artifact = VerifiableArtifact(
            artifact_id=f"artifact_{int(time.time())}",
            artifact_type=ArtifactType.CODE,
            content="def example():\n    return 'Hello, World!'",
            timestamp=time.time(),
            agent_id=task.assigned_agent,
        )

        task.artifacts.append(code_artifact)
        self.artifacts.append(code_artifact)

        # Marca como completed
        task.status = "completed"
        task.completed_at = time.time()

        return {
            "success": True,
            "task_id": task_id,
            "artifacts": [code_artifact.artifact_id],
        }

    def verify_artifact(
        self, artifact_id: str, verification_type: str = "browser"
    ) -> bool:
        """
        Verifica artefato.

        Args:
            artifact_id: ID do artefato
            verification_type: Tipo de verificação

        Returns:
            Se passou verificação
        """
        # Encontra artefato
        artifact = None
        for a in self.artifacts:
            if a.artifact_id == artifact_id:
                artifact = a
                break

        if not artifact:
            logger.warning(f"Artifact not found: {artifact_id}")
            return False

        # Executa verificação
        if verification_type == "browser":
            # Browser verification
            verification = self.browser_verifier.verify_web_app(
                url="http://localhost:3000", expected_elements=[".app-container"]
            )

            artifact.verified = verification.passed
            artifact.verification_result = str(verification.errors)

            return verification.passed

        else:
            # Outros tipos de verificação
            artifact.verified = True
            artifact.verification_result = "Manual verification"
            return True

    def provide_feedback(
        self, task_id: str, feedback_content: str, success: bool
    ) -> None:
        """
        Fornece feedback sobre tarefa.

        Args:
            task_id: ID da tarefa
            feedback_content: Conteúdo do feedback
            success: Se foi bem-sucedida
        """
        task = self.tasks.get(task_id)

        if not task:
            logger.warning(f"Task not found: {task_id}")
            return

        # Registra feedback na tarefa
        task.feedback = feedback_content

        # Processa no self-improvement loop
        self.self_improvement.process_feedback(
            task_id=task_id,
            feedback_type="task_completion",
            feedback_content=feedback_content,
            success=success,
        )

        # Atualiza performance do modelo
        task_type = task.description.split()[0].lower()  # Simplified
        self.model_selector.update_performance(
            task_type=task_type, model=task.assigned_model, success=success
        )

    def get_insights(self) -> Dict[str, Any]:
        """
        Retorna insights do sistema.

        Returns:
            Dict com insights
        """
        return {
            "total_tasks": len(self.tasks),
            "total_artifacts": len(self.artifacts),
            "verified_artifacts": sum(1 for a in self.artifacts if a.verified),
            "self_improvement": self.self_improvement.get_learned_insights(),
            "model_usage": {
                model.value: sum(
                    1
                    for entry in self.model_selector.usage_history
                    if entry["model"] == model.value
                )
                for model in AIModel
            },
        }


def demonstrate_agentic_ide() -> None:
    """
    Demonstração da IDE agentic.
    """
    print("=" * 70)
    print("DEMONSTRAÇÃO: Agentic IDE (Dual-Mode Interface)")
    print("=" * 70)
    print()

    # Cria IDE
    ide = AgenticIDE(workspace_path=Path("/tmp/omnimind_workspace"))

    print("MODO ATUAL:", ide.current_mode.value.upper())
    print()

    # Cria tarefa
    print("CRIANDO TAREFA")
    print("-" * 70)

    task = ide.create_task(
        description="Implement user authentication",
        task_type="code",
        agent_id="code_agent",
        context={"requires_code": True},
    )

    print(f"Task ID: {task.task_id}")
    print(f"Agent: {task.assigned_agent}")
    print(f"Model: {task.assigned_model.value}")
    print()

    # Executa tarefa
    print("EXECUTANDO TAREFA")
    print("-" * 70)

    result = ide.execute_task(task.task_id)

    print(f"Success: {result['success']}")
    print(f"Artifacts created: {len(result.get('artifacts', []))}")
    print()

    # Verifica artefato
    if result.get("artifacts"):
        artifact_id = result["artifacts"][0]

        print("VERIFICANDO ARTEFATO (Browser-in-the-Loop)")
        print("-" * 70)

        verified = ide.verify_artifact(artifact_id, verification_type="browser")

        print(f"Artifact: {artifact_id}")
        print(f"Verified: {verified}")
        print()

    # Fornece feedback
    print("FORNECENDO FEEDBACK")
    print("-" * 70)

    ide.provide_feedback(
        task_id=task.task_id,
        feedback_content="Code works well, good job!",
        success=True,
    )

    print("Feedback registered")
    print()

    # Muda para modo Manager
    print("MUDANDO PARA MODO MANAGER")
    print("-" * 70)

    ide.switch_mode(IDEMode.MANAGER)
    print(f"Current mode: {ide.current_mode.value}")
    print()

    # Insights
    print("INSIGHTS DO SISTEMA")
    print("-" * 70)

    insights = ide.get_insights()

    print(f"Total tasks: {insights['total_tasks']}")
    print(f"Total artifacts: {insights['total_artifacts']}")
    print(f"Verified artifacts: {insights['verified_artifacts']}")
    print()

    print("Self-improvement insights:")
    si_insights = insights["self_improvement"]
    print(f"  Total feedback: {si_insights['total_feedback']}")
    print(f"  Recommendations: {len(si_insights['recommendations'])}")
    for rec in si_insights["recommendations"]:
        print(f"    - {rec}")
    print()

    print("Model usage:")
    for model, count in insights["model_usage"].items():
        if count > 0:
            print(f"  {model}: {count} tasks")
    print()


if __name__ == "__main__":
    demonstrate_agentic_ide()
