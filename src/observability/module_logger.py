"""
Sistema de Logging Estruturado para Módulos OmniMind

Logging estruturado com JSON e integração ao audit chain.
Exceto o próprio sistema de auditoria (conceito teórico).

Autor: Fabrício da Silva + assistência de IA
Data: 2025-12-06
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class StructuredModuleLogger:
    """
    Logger estruturado para módulos OmniMind.

    Características:
    - Logs estruturados em JSON
    - Integração com audit chain (exceto próprio sistema de auditoria)
    - Arquivos de log dedicados por módulo
    - Rotação automática
    """

    # Componentes que NÃO devem ser auditados (conceito teórico)
    # 1. O sistema de auditoria não pode se auditar
    # 2. O inconsciente não pode ser auditado - se tudo fosse auditado, não haveria inconsciente
    EXCLUDED_FROM_AUDIT = {
        # Sistema de auditoria
        "ImmutableAuditSystem",
        "audit_system",
        "audit",
        # Inconsciente (conceito teórico fundamental)
        "machinic_unconscious",
        "unconscious",
        "DesireFlow",
        "QuantumUnconscious",
        "EncryptedUnconsciousLayer",
        "SystemicMemoryTrace",
        "topological_void",
        "repressed",
        "deterritorialization",
        "desire_flow",
        "sinthome",
        "quantum_unconscious",
    }

    def __init__(self, module_name: str, log_dir: str = "logs/modules"):
        """
        Inicializa logger estruturado.

        Args:
            module_name: Nome do módulo
            log_dir: Diretório para logs
        """
        self.module_name = module_name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Arquivo de log dedicado do módulo
        self.log_file = self.log_dir / f"{module_name.lower()}.jsonl"

        # Logger Python padrão
        self.python_logger = logging.getLogger(f"omnimind.{module_name}")

        self._is_excluded = self._is_excluded_from_audit(module_name)

    def _is_excluded_from_audit(self, module_name: str) -> bool:
        """Verifica se módulo está excluído de auditoria."""
        return any(excluded in module_name for excluded in self.EXCLUDED_FROM_AUDIT)

    def _log_structured(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        audit: bool = True,
    ) -> None:
        """
        Registra log estruturado.

        Args:
            level: Nível do log (info, warning, error, etc.)
            message: Mensagem do log
            context: Contexto adicional
            audit: Se True, integra com audit chain (exceto módulos excluídos)
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        entry = {
            "timestamp": timestamp,
            "module": self.module_name,
            "level": level,
            "message": message,
            "context": context or {},
        }

        # Persistir em JSONL
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception as e:
            self.python_logger.error(f"Erro ao persistir log: {e}")

        # Log Python padrão
        log_method = getattr(self.python_logger, level.lower(), self.python_logger.info)
        log_method(message)

        # Integrar com audit chain (exceto módulos excluídos)
        if audit and not self._is_excluded:
            try:
                from ..audit.immutable_audit import get_audit_system

                audit_system = get_audit_system()
                audit_system.log_action(
                    action="module_log",
                    details={
                        "component": self.module_name,
                        "level": level,
                        "message": message,
                        "context": context or {},
                    },
                    category="observability",
                )
            except Exception as e:
                self.python_logger.debug(f"Erro ao integrar com audit chain: {e}")

    def info(
        self, message: str, context: Optional[Dict[str, Any]] = None, audit: bool = True
    ) -> None:
        """Log de informação."""
        self._log_structured("info", message, context, audit)

    def warning(
        self, message: str, context: Optional[Dict[str, Any]] = None, audit: bool = True
    ) -> None:
        """Log de aviso."""
        self._log_structured("warning", message, context, audit)

    def error(
        self, message: str, context: Optional[Dict[str, Any]] = None, audit: bool = True
    ) -> None:
        """Log de erro."""
        self._log_structured("error", message, context, audit)

    def debug(
        self, message: str, context: Optional[Dict[str, Any]] = None, audit: bool = True
    ) -> None:
        """Log de debug."""
        self._log_structured("debug", message, context, audit)

    def critical(
        self, message: str, context: Optional[Dict[str, Any]] = None, audit: bool = True
    ) -> None:
        """Log crítico."""
        self._log_structured("critical", message, context, audit)


def get_module_logger(module_name: str) -> StructuredModuleLogger:
    """
    Retorna logger estruturado para módulo.

    Args:
        module_name: Nome do módulo

    Returns:
        StructuredModuleLogger
    """
    return StructuredModuleLogger(module_name)
