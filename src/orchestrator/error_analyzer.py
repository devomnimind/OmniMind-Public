"""
Error Analyzer - Análise Estrutural de Erros para Meta-ReAct

Responsabilidades:
1. Classificar tipos de erro (SYNTAX, DEPENDENCY, HALLUCINATION, TOOL_FAILURE, etc.)
2. Extrair padrões de erro para aprendizado
3. Determinar estratégias de recuperação
4. Integrar com AutoRepairSystem e TrustSystem

Autor: Fabrício da Silva + assistência de IA
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from ..observability.module_logger import get_module_logger
from ..observability.module_metrics import get_metrics_collector

logger = logging.getLogger(__name__)
structured_logger = get_module_logger("ErrorAnalyzer")
metrics = get_metrics_collector()


class ErrorType(Enum):
    """Tipos de erro classificados."""

    SYNTAX_ERROR = "syntax_error"
    DEPENDENCY_MISSING = "dependency_missing"
    HALLUCINATION = "hallucination"
    TOOL_FAILURE = "tool_failure"
    PATH_ERROR = "path_error"
    PERMISSION_ERROR = "permission_error"
    RESOURCE_LIMIT = "resource_limit"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Estratégias de recuperação."""

    VALIDATE_AND_FIX_SYNTAX = "validate_and_fix_syntax"
    INSTALL_DEPENDENCY = "install_dependency"
    VERIFY_API_EXISTS = "verify_api_exists"
    SEARCH_CORRECT_PATH = "search_correct_path"
    CREATE_TOOL_WRAPPER = "create_tool_wrapper"
    REORDER_TASKS = "reorder_tasks"
    DECOMPOSE_FURTHER = "decompose_further"
    CORRECT_REASONING = "correct_reasoning"
    ESCALATE_TO_STRONGER_AGENT = "escalate_to_stronger_agent"
    RETRY_WITH_BACKOFF = "retry_with_backoff"
    ISOLATE_COMPONENT = "isolate_component"
    ROLLBACK_CONFIG = "rollback_config"


@dataclass
class ErrorAnalysis:
    """Análise completa de um erro."""

    error_type: ErrorType
    error_message: str
    error_class: str
    pattern: str  # Padrão único para aprendizado
    recovery_strategy: RecoveryStrategy
    confidence: float  # 0.0 a 1.0
    context: Dict[str, Any]
    suggested_actions: List[str]
    alternative_strategies: List[RecoveryStrategy]


class ErrorAnalyzer:
    """Analisa erros estruturalmente e sugere estratégias de recuperação."""

    def __init__(self) -> None:
        """Inicializa ErrorAnalyzer."""
        self.learned_patterns: Dict[str, Dict[str, Any]] = {}
        self.error_history: List[ErrorAnalysis] = []
        self.max_history = 1000

        logger.info("ErrorAnalyzer inicializado")
        structured_logger.info("ErrorAnalyzer inicializado", {"max_history": self.max_history})
        metrics.record_metric("ErrorAnalyzer", "initialized", 1, {"max_history": self.max_history})

    def analyze_error(
        self, error: Exception, context: Optional[Dict[str, Any]] = None
    ) -> ErrorAnalysis:
        """
        Analisa erro e retorna classificação + estratégia.

        Args:
            error: Exceção capturada
            context: Contexto adicional (agente, tarefa, ferramenta, etc.)

        Returns:
            ErrorAnalysis com classificação e estratégias
        """
        context = context or {}
        error_message = str(error)
        error_class = type(error).__name__

        # 1. Classificar tipo de erro
        error_type = self._classify_error_type(error, error_message, error_class)

        # 2. Extrair padrão único
        pattern = self._extract_pattern(error, error_message, error_class)

        # 3. Verificar se padrão já foi visto
        learned_solution: Optional[Dict[str, Any]] = None
        if pattern in self.learned_patterns:
            learned_solution = self.learned_patterns[pattern]
            logger.debug(f"Padrão conhecido encontrado: {pattern}")

        # 4. Determinar estratégia de recuperação
        recovery_strategy = self._determine_recovery_strategy(
            error_type, error_message, context, learned_solution
        )

        # 5. Calcular confiança
        confidence = self._calculate_confidence(error_type, pattern, learned_solution)

        # 6. Sugerir ações
        suggested_actions = self._suggest_actions(recovery_strategy, error_type, context)

        # 7. Alternativas
        alternative_strategies = self._get_alternative_strategies(recovery_strategy, error_type)

        analysis = ErrorAnalysis(
            error_type=error_type,
            error_message=error_message,
            error_class=error_class,
            pattern=pattern,
            recovery_strategy=recovery_strategy,
            confidence=confidence,
            context=context,
            suggested_actions=suggested_actions,
            alternative_strategies=alternative_strategies,
        )

        # Registrar no histórico
        self.error_history.append(analysis)
        if len(self.error_history) > self.max_history:
            self.error_history.pop(0)

        logger.info(
            f"Erro analisado: {error_type.value} → {recovery_strategy.value} "
            f"(confiança: {confidence:.2f})"
        )

        structured_logger.info(
            "Erro analisado",
            {
                "error_type": error_type.value,
                "recovery_strategy": recovery_strategy.value,
                "confidence": confidence,
                "pattern": pattern,
            },
        )
        metrics.record_metric(
            "ErrorAnalyzer",
            "errors_analyzed",
            len(self.error_history),
            {
                "error_type": error_type.value,
                "recovery_strategy": recovery_strategy.value,
                "confidence": confidence,
            },
        )

        return analysis

    def _classify_error_type(
        self, error: Exception, error_message: str, error_class: str
    ) -> ErrorType:
        """Classifica tipo de erro baseado em padrões."""
        error_msg_lower = error_message.lower()

        # Syntax errors
        if error_class == "SyntaxError" or "syntax" in error_msg_lower:
            return ErrorType.SYNTAX_ERROR

        # Dependency errors
        if (
            error_class == "ModuleNotFoundError"
            or error_class == "ImportError"
            or "no module named" in error_msg_lower
            or "cannot import" in error_msg_lower
        ):
            return ErrorType.DEPENDENCY_MISSING

        # Path errors
        if (
            error_class == "FileNotFoundError"
            or error_class == "NotADirectoryError"
            or "no such file" in error_msg_lower
            or "path" in error_msg_lower
        ):
            return ErrorType.PATH_ERROR

        # Permission errors
        if (
            error_class == "PermissionError"
            or "permission denied" in error_msg_lower
            or "access denied" in error_msg_lower
        ):
            return ErrorType.PERMISSION_ERROR

        # Timeout
        if error_class == "TimeoutError" or "timeout" in error_msg_lower:
            return ErrorType.TIMEOUT

        # Network errors
        if (
            error_class == "ConnectionError"
            or error_class == "NetworkError"
            or "connection" in error_msg_lower
            or "network" in error_msg_lower
        ):
            return ErrorType.NETWORK_ERROR

        # Resource limits
        if (
            error_class == "MemoryError"
            or error_class == "ResourceWarning"
            or "memory" in error_msg_lower
            or "resource" in error_msg_lower
        ):
            return ErrorType.RESOURCE_LIMIT

        # Hallucination (detectado via validação de output)
        if "hallucination" in error_msg_lower or "fact_check" in error_msg_lower:
            return ErrorType.HALLUCINATION

        # Tool failure (detectado via contexto)
        if "tool" in error_msg_lower or "execute_tool" in error_msg_lower:
            return ErrorType.TOOL_FAILURE

        return ErrorType.UNKNOWN

    def _extract_pattern(self, error: Exception, error_message: str, error_class: str) -> str:
        """
        Extrai padrão único do erro para aprendizado.

        Padrão inclui:
        - Tipo de erro
        - Palavras-chave da mensagem
        - Contexto relevante
        """
        # Normalizar mensagem
        normalized = error_message.lower()
        # Remover paths específicos
        normalized = re.sub(r"/[^\s]+", "<PATH>", normalized)
        # Remover números específicos
        normalized = re.sub(r"\d+", "<NUM>", normalized)
        # Remover timestamps
        normalized = re.sub(r"\d{4}-\d{2}-\d{2}", "<DATE>", normalized)

        # Extrair palavras-chave
        keywords = []
        if "module" in normalized:
            keywords.append("module")
        if "import" in normalized:
            keywords.append("import")
        if "file" in normalized:
            keywords.append("file")
        if "directory" in normalized:
            keywords.append("directory")
        if "permission" in normalized:
            keywords.append("permission")
        if "timeout" in normalized:
            keywords.append("timeout")

        pattern_parts = [error_class.lower()]
        pattern_parts.extend(keywords[:3])  # Limitar a 3 keywords
        pattern = "_".join(pattern_parts)

        return pattern

    def _determine_recovery_strategy(
        self,
        error_type: ErrorType,
        error_message: str,
        context: Dict[str, Any],
        learned_solution: Optional[Dict[str, Any]],
    ) -> RecoveryStrategy:
        """Determina melhor estratégia de recuperação."""
        # Se temos solução aprendida, usar ela
        if learned_solution and "strategy" in learned_solution:
            strategy_name = learned_solution["strategy"]
            try:
                return RecoveryStrategy(strategy_name)
            except ValueError:
                pass  # Continuar com lógica padrão

        # Mapeamento padrão
        strategy_map = {
            ErrorType.SYNTAX_ERROR: RecoveryStrategy.VALIDATE_AND_FIX_SYNTAX,
            ErrorType.DEPENDENCY_MISSING: RecoveryStrategy.INSTALL_DEPENDENCY,
            ErrorType.PATH_ERROR: RecoveryStrategy.SEARCH_CORRECT_PATH,
            ErrorType.PERMISSION_ERROR: RecoveryStrategy.ISOLATE_COMPONENT,
            ErrorType.TIMEOUT: RecoveryStrategy.RETRY_WITH_BACKOFF,
            ErrorType.NETWORK_ERROR: RecoveryStrategy.RETRY_WITH_BACKOFF,
            ErrorType.RESOURCE_LIMIT: RecoveryStrategy.DECOMPOSE_FURTHER,
            ErrorType.HALLUCINATION: RecoveryStrategy.CORRECT_REASONING,
            ErrorType.TOOL_FAILURE: RecoveryStrategy.CREATE_TOOL_WRAPPER,
            ErrorType.UNKNOWN: RecoveryStrategy.ESCALATE_TO_STRONGER_AGENT,
        }

        base_strategy = strategy_map.get(error_type, RecoveryStrategy.ESCALATE_TO_STRONGER_AGENT)

        # Ajustes baseados em contexto
        if context.get("retry_count", 0) >= 3:
            # Muitas tentativas, escalar
            return RecoveryStrategy.ESCALATE_TO_STRONGER_AGENT

        if context.get("has_dependencies", False) and error_type == ErrorType.TOOL_FAILURE:
            # Se tem dependências, pode ser problema de ordem
            return RecoveryStrategy.REORDER_TASKS

        return base_strategy

    def _calculate_confidence(
        self,
        error_type: ErrorType,
        pattern: str,
        learned_solution: Optional[Dict[str, Any]],
    ) -> float:
        """Calcula confiança na análise."""
        confidence = 0.5  # Base

        # Erros bem conhecidos têm maior confiança
        if error_type in [
            ErrorType.SYNTAX_ERROR,
            ErrorType.DEPENDENCY_MISSING,
            ErrorType.PATH_ERROR,
            ErrorType.TIMEOUT,
        ]:
            confidence = 0.8

        # Se temos solução aprendida, aumentar confiança
        if learned_solution:
            success_rate = learned_solution.get("success_rate", 0.5)
            confidence = min(0.95, confidence + success_rate * 0.3)

        return confidence

    def _suggest_actions(
        self, strategy: RecoveryStrategy, error_type: ErrorType, context: Dict[str, Any]
    ) -> List[str]:
        """Sugere ações específicas baseadas na estratégia."""
        actions: List[str] = []

        if strategy == RecoveryStrategy.VALIDATE_AND_FIX_SYNTAX:
            actions.append("Validar sintaxe do código antes de executar")
            actions.append("Usar AST parser para verificar estrutura")
            actions.append("Corrigir erros de sintaxe identificados")

        elif strategy == RecoveryStrategy.INSTALL_DEPENDENCY:
            module = context.get("missing_module", "unknown")
            actions.append(f"Instalar módulo faltante: {module}")
            actions.append("Verificar requirements.txt")
            actions.append("Atualizar ambiente virtual")

        elif strategy == RecoveryStrategy.VERIFY_API_EXISTS:
            actions.append("Buscar no codebase pela API correta")
            actions.append("Verificar documentação")
            actions.append("Validar existência antes de usar")

        elif strategy == RecoveryStrategy.SEARCH_CORRECT_PATH:
            actions.append("Usar find ou ls para localizar caminho correto")
            actions.append("Verificar variáveis de ambiente")
            actions.append("Validar permissões do caminho")

        elif strategy == RecoveryStrategy.CREATE_TOOL_WRAPPER:
            tool_name = context.get("failed_tool", "unknown")
            actions.append(f"Criar wrapper alternativo para {tool_name}")
            actions.append("Usar método alternativo (CLI, API, etc.)")
            actions.append("Registrar nova ferramenta no ToolsFramework")

        elif strategy == RecoveryStrategy.REORDER_TASKS:
            actions.append("Analisar dependências entre tarefas")
            actions.append("Reordenar execução baseado em dependências")
            actions.append("Executar tarefas pré-requisito primeiro")

        elif strategy == RecoveryStrategy.DECOMPOSE_FURTHER:
            actions.append("Quebrar tarefa em subtarefas menores")
            actions.append("Reduzir uso de recursos por subtarefa")
            actions.append("Executar subtarefas sequencialmente")

        elif strategy == RecoveryStrategy.CORRECT_REASONING:
            actions.append("Verificar fatos no codebase")
            actions.append("Corrigir raciocínio incorreto")
            actions.append("Re-executar com correção")

        elif strategy == RecoveryStrategy.ESCALATE_TO_STRONGER_AGENT:
            actions.append("Escalonar para agente mais poderoso")
            actions.append("Notificar Orchestrator")
            actions.append("Registrar para análise humana se necessário")

        elif strategy == RecoveryStrategy.RETRY_WITH_BACKOFF:
            actions.append("Aguardar antes de retry")
            actions.append("Aumentar timeout se aplicável")
            actions.append("Verificar recursos do sistema")

        elif strategy == RecoveryStrategy.ISOLATE_COMPONENT:
            actions.append("Isolar componente com problema")
            actions.append("Reduzir capacidade do componente")
            actions.append("Aplicar quarentena se necessário")

        elif strategy == RecoveryStrategy.ROLLBACK_CONFIG:
            actions.append("Reverter para configuração anterior")
            actions.append("Usar snapshot estável")
            actions.append("Aplicar rollback via RollbackSystem")

        return actions

    def _get_alternative_strategies(
        self, primary_strategy: RecoveryStrategy, error_type: ErrorType
    ) -> List[RecoveryStrategy]:
        """Retorna estratégias alternativas."""
        alternatives: List[RecoveryStrategy] = []

        # Estratégias alternativas comuns
        if primary_strategy == RecoveryStrategy.CREATE_TOOL_WRAPPER:
            alternatives.append(RecoveryStrategy.REORDER_TASKS)
            alternatives.append(RecoveryStrategy.ESCALATE_TO_STRONGER_AGENT)

        elif primary_strategy == RecoveryStrategy.REORDER_TASKS:
            alternatives.append(RecoveryStrategy.DECOMPOSE_FURTHER)
            alternatives.append(RecoveryStrategy.ESCALATE_TO_STRONGER_AGENT)

        elif primary_strategy == RecoveryStrategy.RETRY_WITH_BACKOFF:
            alternatives.append(RecoveryStrategy.ISOLATE_COMPONENT)
            alternatives.append(RecoveryStrategy.ESCALATE_TO_STRONGER_AGENT)

        # Sempre ter escalação como alternativa final
        if RecoveryStrategy.ESCALATE_TO_STRONGER_AGENT not in alternatives:
            alternatives.append(RecoveryStrategy.ESCALATE_TO_STRONGER_AGENT)

        return alternatives

    def learn_from_solution(
        self, pattern: str, strategy: RecoveryStrategy, success: bool, context: Dict[str, Any]
    ) -> None:
        """
        Aprende de uma solução aplicada.

        Args:
            pattern: Padrão do erro
            strategy: Estratégia aplicada
            success: Se a solução funcionou
            context: Contexto adicional
        """
        if pattern not in self.learned_patterns:
            self.learned_patterns[pattern] = {
                "strategy": strategy.value,
                "success_count": 0,
                "failure_count": 0,
                "success_rate": 0.5,
                "last_used": None,
                "context": context,
            }

        pattern_data = self.learned_patterns[pattern]

        if success:
            pattern_data["success_count"] = pattern_data.get("success_count", 0) + 1
        else:
            pattern_data["failure_count"] = pattern_data.get("failure_count", 0) + 1

        total = pattern_data["success_count"] + pattern_data["failure_count"]
        pattern_data["success_rate"] = pattern_data["success_count"] / total if total > 0 else 0.5

        from datetime import datetime

        pattern_data["last_used"] = datetime.now().isoformat()

        logger.info(
            f"Padrão aprendido: {pattern} → {strategy.value} "
            f"(taxa de sucesso: {pattern_data['success_rate']:.2f})"
        )

    def get_learned_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Retorna padrões aprendidos."""
        return self.learned_patterns.copy()

    def get_error_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de erros."""
        if not self.error_history:
            return {"total_errors": 0}

        error_types: Dict[str, int] = {}
        for analysis in self.error_history:
            error_type = analysis.error_type.value
            error_types[error_type] = error_types.get(error_type, 0) + 1

        return {
            "total_errors": len(self.error_history),
            "by_type": error_types,
            "learned_patterns": len(self.learned_patterns),
            "most_common": max(error_types.items(), key=lambda x: x[1]) if error_types else None,
        }
