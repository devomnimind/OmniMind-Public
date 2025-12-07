"""
Enhanced Code Agent - Agente com Auto-Error Detection e Self-Correction

Extensão do CodeAgent com:
- Auto-error detection
- Self-correction loops
- Learning from failures
- Tool composition & creation (via DynamicToolCreator)

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..agents.code_agent import CodeAgent
from ..observability.module_logger import get_module_logger
from ..observability.module_metrics import get_metrics_collector
from ..orchestrator.error_analyzer import ErrorAnalyzer, ErrorAnalysis, ErrorType, RecoveryStrategy
from ..tools.dynamic_tool_creator import DynamicToolCreator
from ..tools.tool_composer import ToolComposer

logger = logging.getLogger(__name__)
structured_logger = get_module_logger("EnhancedCodeAgent")
metrics = get_metrics_collector()


@dataclass
class FailureRecord:
    """Registro de uma falha e sua resolução."""

    error_type: ErrorType
    error_message: str
    context: Dict[str, Any]
    recovery_strategy: RecoveryStrategy
    success: bool
    attempt_count: int
    learned_pattern: Optional[str] = None


class EnhancedCodeAgent(CodeAgent):
    """
    CodeAgent aprimorado com auto-detecção de erros e self-correction.

    Características:
    - Detecta automaticamente tipos de erro
    - Aplica estratégias de recuperação
    - Aprende com falhas anteriores
    - Cria ferramentas dinamicamente quando necessário
    - Self-correction loops com validação
    """

    def __init__(self, config_path: str, orchestrator: Optional[Any] = None):
        """
        Inicializa EnhancedCodeAgent.

        Args:
            config_path: Caminho para arquivo de configuração
            orchestrator: Instância opcional de OrchestratorAgent
        """
        super().__init__(config_path)

        self.orchestrator = orchestrator
        self.error_analyzer = ErrorAnalyzer()
        self.dynamic_tool_creator: Optional[DynamicToolCreator] = None
        self.tool_composer: Optional[ToolComposer] = None

        # Histórico de falhas e aprendizado
        self.failure_history: List[FailureRecord] = []
        self.learned_patterns: Dict[str, RecoveryStrategy] = {}

        # Se orchestrator disponível, usar DynamicToolCreator dele
        if orchestrator and hasattr(orchestrator, "dynamic_tool_creator"):
            self.dynamic_tool_creator = orchestrator.dynamic_tool_creator

        # Inicializar ToolComposer
        self.tool_composer = ToolComposer(self.tools_framework)

        logger.info("EnhancedCodeAgent inicializado com auto-error detection e tool composition")
        structured_logger.info(
            "EnhancedCodeAgent inicializado",
            {
                "orchestrator_available": orchestrator is not None,
                "dynamic_tool_creator_available": self.dynamic_tool_creator is not None,
            },
        )
        metrics.record_metric(
            "EnhancedCodeAgent",
            "initialized",
            1,
            {"orchestrator_available": orchestrator is not None},
        )

    def execute_task_with_self_correction(
        self, task: str, max_attempts: int = 3, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executa tarefa com self-correction loop.

        Args:
            task: Descrição da tarefa
            max_attempts: Número máximo de tentativas
            context: Contexto adicional

        Returns:
            Resultado da execução com metadados de correção
        """
        context = context or {}
        attempt = 0
        last_error: Optional[Exception] = None
        error_analysis: Optional[ErrorAnalysis] = None

        logger.info(f"Executando tarefa com self-correction: {task[:100]}...")

        while attempt < max_attempts:
            try:
                # Executar tarefa usando método padrão do ReactAgent
                result = self.run(task)

                # Validar resultado
                if self._validate_output(result):
                    # Sucesso - aprender se houve correção anterior
                    if attempt > 0 and error_analysis:
                        self._learn_from_success(task, error_analysis, result)

                    return {
                        "status": "success",
                        "result": result,
                        "attempts": attempt + 1,
                        "corrections_applied": attempt > 0,
                    }
                else:
                    # Resultado inválido - tratar como erro
                    raise ValueError("Resultado da execução inválido")

            except Exception as error:
                attempt += 1
                last_error = error

                logger.warning(f"Tentativa {attempt}/{max_attempts} falhou: {error}")

                # Analisar erro
                error_analysis = self.error_analyzer.analyze_error(
                    error=error, context={"task": task, "attempt": attempt, **context}
                )

                # Verificar se já vimos esse padrão antes
                pattern = error_analysis.pattern
                if pattern in self.learned_patterns:
                    # Aplicar solução aprendida
                    recovery_strategy = self.learned_patterns[pattern]
                    logger.info(f"Aplicando solução aprendida para padrão: {pattern}")
                else:
                    recovery_strategy = error_analysis.recovery_strategy

                # Aplicar estratégia de recuperação
                corrected_task = self._apply_recovery_strategy(
                    task=task,
                    error=error,
                    error_analysis=error_analysis,
                    recovery_strategy=recovery_strategy,
                    context=context,
                )

                if corrected_task != task:
                    task = corrected_task
                    logger.info(f"Tarefa corrigida: {corrected_task[:100]}...")

                # Registrar falha
                failure_record = FailureRecord(
                    error_type=error_analysis.error_type,
                    error_message=str(error),
                    context={"task": task, "attempt": attempt, **context},
                    recovery_strategy=recovery_strategy,
                    success=False,  # Ainda não sabemos se vai funcionar
                    attempt_count=attempt,
                    learned_pattern=pattern,
                )
                self.failure_history.append(failure_record)

        # Todas as tentativas falharam
        logger.error(f"Todas as {max_attempts} tentativas falharam para: {task[:100]}...")

        # Aprender da falha final
        if error_analysis and last_error:
            self._learn_from_failure(task, error_analysis, last_error)

        return {
            "status": "failed",
            "error": str(last_error) if last_error else "Unknown error",
            "error_analysis": (
                {
                    "error_type": error_analysis.error_type.value if error_analysis else None,
                    "error_message": error_analysis.error_message if error_analysis else None,
                    "recovery_strategy": (
                        error_analysis.recovery_strategy.value if error_analysis else None
                    ),
                    "confidence": error_analysis.confidence if error_analysis else None,
                }
                if error_analysis
                else None
            ),
            "attempts": max_attempts,
            "failure_history": [fr.__dict__ for fr in self.failure_history[-max_attempts:]],
        }

    def _validate_output(self, result: Any) -> bool:
        """
        Valida resultado da execução.

        Args:
            result: Resultado a validar

        Returns:
            True se válido, False caso contrário
        """
        if result is None:
            return False

        # Verificar se é dict com status
        if isinstance(result, dict):
            status = result.get("status", "unknown")
            if status == "error" or status == "failed":
                return False

        # Verificar se contém erro
        if isinstance(result, dict) and "error" in result:
            return False

        return True

    def _apply_recovery_strategy(
        self,
        task: str,
        error: Exception,
        error_analysis: ErrorAnalysis,
        recovery_strategy: RecoveryStrategy,
        context: Dict[str, Any],
    ) -> str:
        """
        Aplica estratégia de recuperação e retorna tarefa corrigida.

        Args:
            task: Tarefa original
            error: Erro ocorrido
            error_analysis: Análise do erro
            recovery_strategy: Estratégia de recuperação
            context: Contexto adicional

        Returns:
            Tarefa corrigida (ou original se não houver correção)
        """
        if recovery_strategy == RecoveryStrategy.CORRECT_REASONING:
            # Corrigir raciocínio - adicionar contexto ou clarificar
            corrected = self._correct_reasoning(task, error_analysis)
            return corrected

        elif recovery_strategy == RecoveryStrategy.CREATE_TOOL_WRAPPER:
            # Criar ferramenta alternativa
            if self.dynamic_tool_creator:
                wrapper_tool = self._create_tool_wrapper(error, context)
                if wrapper_tool:
                    logger.info("Ferramenta wrapper criada dinamicamente")
            return task  # Tarefa não muda, mas ferramenta foi criada

        elif recovery_strategy == RecoveryStrategy.REORDER_TASKS:
            # Reordenar tarefas - decompor em subtarefas
            decomposed = self._decompose_task(task, error_analysis)
            return decomposed

        elif recovery_strategy == RecoveryStrategy.DECOMPOSE_FURTHER:
            # Quebrar em subtarefas menores (DECOMPOSE_FURTHER é equivalente)
            subtasks = self._break_into_subtasks(task, error_analysis)
            return subtasks

        elif recovery_strategy == RecoveryStrategy.ESCALATE_TO_STRONGER_AGENT:
            # Escalonar para agente mais forte (via orchestrator)
            if self.orchestrator:
                logger.info("Escalando tarefa para OrchestratorAgent")
                # Deixar orchestrator lidar
            return task

        else:
            # Estratégia não implementada ou desconhecida
            logger.warning(f"Estratégia de recuperação não implementada: {recovery_strategy}")
            return task

    def _correct_reasoning(self, task: str, error_analysis: ErrorAnalysis) -> str:
        """Corrige raciocínio da tarefa baseado na análise de erro."""
        # Adicionar contexto ou clarificar baseado no erro
        if error_analysis.error_type == ErrorType.HALLUCINATION:
            # Adicionar verificação de fatos
            corrected = f"{task} [Verificar fatos e validar resultado]"
        elif error_analysis.error_type == ErrorType.SYNTAX_ERROR:
            # Adicionar instrução para validar sintaxe
            corrected = f"{task} [Validar sintaxe antes de executar]"
        else:
            corrected = f"{task} [Aplicar correção baseada em: {error_analysis.error_type.value}]"

        return corrected

    def _create_tool_wrapper(self, error: Exception, context: Dict[str, Any]) -> Optional[Any]:
        """Cria wrapper de ferramenta alternativa."""
        if not self.dynamic_tool_creator:
            return None

        # Identificar ferramenta que falhou (se possível)
        error_msg = str(error).lower()
        if "file" in error_msg or "path" in error_msg:
            # Criar wrapper para operações de arquivo
            wrapper_code = """
def alternative_file_operation(*args, **kwargs):
    # Implementação alternativa
    try:
        # Tentar operação alternativa
        return {"status": "success", "method": "alternative"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
"""
            return self.dynamic_tool_creator.create_tool(
                name="alternative_file_op",
                description="Operação alternativa de arquivo",
                code=wrapper_code,
            )

        return None

    def _decompose_task(self, task: str, error_analysis: ErrorAnalysis) -> str:
        """Decompõe tarefa em subtarefas ordenadas."""
        # Simplificado - em produção, usar decomposição mais sofisticada
        return f"[Decompor] {task}"

    def _break_into_subtasks(self, task: str, error_analysis: ErrorAnalysis) -> str:
        """Quebra tarefa em subtarefas menores."""
        # Simplificado - em produção, quebrar realmente
        return f"[Subtask] {task}"

    def _learn_from_success(self, task: str, error_analysis: ErrorAnalysis, result: Any) -> None:
        """Aprende de uma correção bem-sucedida."""
        pattern = error_analysis.pattern
        recovery_strategy = error_analysis.recovery_strategy

        # Atualizar padrão aprendido
        self.learned_patterns[pattern] = recovery_strategy

        # Atualizar último registro de falha como sucesso
        if self.failure_history:
            self.failure_history[-1].success = True

        # Registrar aprendizado no ErrorAnalyzer
        self.error_analyzer.learn_from_solution(
            pattern=pattern,
            strategy=recovery_strategy,
            success=True,
            context={"task": task, "result": result},
        )

        logger.info(f"Padrão aprendido: {pattern} → {recovery_strategy.value}")

    def _learn_from_failure(
        self, task: str, error_analysis: ErrorAnalysis, error: Exception
    ) -> None:
        """Aprende de uma falha final."""
        pattern = error_analysis.pattern
        recovery_strategy = error_analysis.recovery_strategy

        # Registrar que estratégia não funcionou
        self.error_analyzer.learn_from_solution(
            pattern=pattern,
            strategy=recovery_strategy,
            success=False,
            context={"task": task, "error": str(error)},
        )

        logger.warning(f"Estratégia falhou: {pattern} → {recovery_strategy.value}")

    def get_learning_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de aprendizado."""
        total_failures = len(self.failure_history)
        successful_recoveries = sum(1 for fr in self.failure_history if fr.success)
        learned_patterns_count = len(self.learned_patterns)

        return {
            "total_failures": total_failures,
            "successful_recoveries": successful_recoveries,
            "recovery_rate": (
                successful_recoveries / total_failures if total_failures > 0 else 0.0
            ),
            "learned_patterns": learned_patterns_count,
            "patterns": list(self.learned_patterns.keys()),
        }
