from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set
import structlog


"""
OmniMind Project - Artificial Consciousness System
Copyright (C) 2024-2025 Fabrício da Silva

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Contact: fabricioslv@hotmail.com.br
"""

"""
Task Isolation Engine - OmniMind
Isolamento seguro de tarefas para execução em provedores externos de IA

Garante que dados sensíveis do OmniMind não sejam compartilhados com AIs externas.
"""


logger = structlog.get_logger(__name__)


@dataclass
class IsolatedTask:
    """Tarefa isolada para execução externa"""

    task_id: str
    prompt: str
    context: Optional[Dict[str, Any]] = None
    files: Optional[List[Dict[str, str]]] = None
    metadata: Optional[Dict[str, Any]] = None
    isolation_hash: str = ""  # Hash para verificar integridade

    def __post_init__(self) -> None:
        """Calcula hash de isolamento após inicialização"""
        self.isolation_hash = self._calculate_isolation_hash()

    def _calculate_isolation_hash(self) -> str:
        """Calcula hash SHA-256 do conteúdo isolado"""
        content = f"{self.task_id}|{self.prompt}"
        if self.context:
            content += f"|{str(sorted(self.context.items()))}"
        if self.files:
            for file_info in sorted(self.files, key=lambda x: x.get("name", "")):
                content += f"|{file_info.get('name', '')}|{file_info.get('content', '')}"

        return hashlib.sha256(content.encode("utf-8")).hexdigest()


class TaskIsolationEngine:
    """
    Engine de isolamento de tarefas para provedores externos.

    Remove dados sensíveis, sanitiza prompts e limita escopo de execução.
    """

    def __init__(self, isolation_config: Optional[Dict[str, Any]] = None):
        """
        Inicializa engine de isolamento.

        Args:
            isolation_config: Configuração de isolamento
        """
        self.config = isolation_config or self._get_default_config()
        self.forbidden_patterns = self._compile_forbidden_patterns()
        self.sanitization_rules = self.config.get("sanitization_rules", {})

        logger.info("Task isolation engine initialized", level=self.config.get("level"))

    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão de isolamento"""
        return {
            "level": "strict",  # strict, moderate, permissive
            "forbidden_patterns": [
                r".*password.*",
                r".*secret.*",
                r".*token.*",
                r".*key.*",
                r".*credential.*",
                r".*private.*",
                r".*internal.*",
                r".*confidential.*",
                r".*auth.*",
                r".*session.*",
                r".*cookie.*",
                r".*bearer.*",
                r".*authorization.*",
                r".*api[_-]?key.*",
                r".*access[_-]?token.*",
                r".*refresh[_-]?token.*",
                r".*client[_-]?secret.*",
                r".*client[_-]?id.*",
                r".*database[_-]?url.*",
                r".*db[_-]?connection.*",
                r".*connection[_-]?string.*",
                r".*env.*",
                r".*config.*",
                r".*\.env.*",
                r".*\.key.*",
                r".*\.pem.*",
                r".*\.crt.*",
                r".*127\.0\.0\.1.*",
                r".*localhost.*",
                r".*0\.0\.0\.0.*",
            ],
            "sanitization_rules": {
                "remove_file_paths": True,
                "remove_ip_addresses": True,
                "remove_email_addresses": True,
                "mask_sensitive_data": True,
                "remove_comments": False,  # Pode conter informações úteis
            },
            "resource_limits": {
                "max_prompt_length": 10000,
                "max_context_files": 5,
                "max_file_size_kb": 100,
                "max_context_size_kb": 500,
            },
            "allowed_file_extensions": [
                ".py",
                ".js",
                ".ts",
                ".java",
                ".cpp",
                ".c",
                ".h",
                ".md",
                ".txt",
                ".json",
                ".yaml",
                ".yml",
                ".xml",
                ".html",
                ".css",
                ".sql",
                ".sh",
                ".bat",
            ],
        }

    def _compile_forbidden_patterns(self) -> List[re.Pattern]:
        """Compila padrões regex proibidos"""
        patterns = []
        for pattern in self.config.get("forbidden_patterns", []):
            try:
                compiled = re.compile(pattern, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                patterns.append(compiled)
            except re.error as e:
                logger.warning("Invalid forbidden pattern", pattern=pattern, error=str(e))

        return patterns

    async def isolate_context(self, task_spec: Any) -> IsolatedTask:
        """
        Isola contexto de tarefa para execução externa.

        Args:
            task_spec: Especificação da tarefa original

        Returns:
            Tarefa isolada segura
        """
        logger.info("Isolating task context", task_id=getattr(task_spec, "task_id", "unknown"))

        # Sanitiza prompt
        clean_prompt = self._sanitize_text(task_spec.prompt)

        # Limita tamanho do prompt
        clean_prompt = self._limit_prompt_length(clean_prompt)

        # Isola contexto
        clean_context = None
        if hasattr(task_spec, "context") and task_spec.context:
            clean_context = await self._isolate_context_data(task_spec.context)

        # Filtra arquivos permitidos
        clean_files = None
        if hasattr(task_spec, "files") and task_spec.files:
            clean_files = await self._filter_allowed_files(task_spec.files)

        # Sanitiza metadados
        clean_metadata = None
        if hasattr(task_spec, "metadata") and task_spec.metadata:
            clean_metadata = self._sanitize_metadata(task_spec.metadata)

        # Cria tarefa isolada
        isolated_task = IsolatedTask(
            task_id=getattr(task_spec, "task_id", "unknown"),
            prompt=clean_prompt,
            context=clean_context,
            files=clean_files,
            metadata=clean_metadata,
        )

        logger.info(
            "Task context isolated",
            task_id=isolated_task.task_id,
            prompt_length=len(isolated_task.prompt),
            files_count=len(isolated_task.files) if isolated_task.files else 0,
            isolation_hash=isolated_task.isolation_hash[:8],
        )

        return isolated_task

    def _sanitize_text(self, text: str) -> str:
        """
        Sanitiza texto removendo conteúdo sensível.

        Args:
            text: Texto original

        Returns:
            Texto sanitizado
        """
        if not text:
            return text

        sanitized = text

        # Regras de sanitização específicas primeiro
        if self.sanitization_rules.get("remove_email_addresses"):
            sanitized = re.sub(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", "[EMAIL]", sanitized)

        if self.sanitization_rules.get("remove_ip_addresses"):
            sanitized = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "[IP_ADDRESS]", sanitized)

        if self.sanitization_rules.get("remove_file_paths"):
            sanitized = re.sub(r"/[^\s]+\.[a-zA-Z0-9]+", "[FILE_PATH]", sanitized)
            sanitized = re.sub(r"\\[^\s]+\.[a-zA-Z0-9]+", "[FILE_PATH]", sanitized)

        # Aplica padrões proibidos - mas de forma mais inteligente
        # Em vez de substituir a string inteira, substitui apenas palavras-chave sensíveis
        sensitive_keywords = [
            "password",
            "secret",
            "token",
            "key",
            "credential",
            "private",
            "internal",
            "confidential",
            "auth",
            "session",
            "cookie",
            "bearer",
            "authorization",
            "api_key",
            "access_token",
            "refresh_token",
            "client_secret",
            "client_id",
            "database_url",
            "db_connection",
            "connection_string",
            "env",
            "config",
        ]

        for keyword in sensitive_keywords:
            # Substitui palavra-chave seguida de = ou : e valor
            pattern = rf"\b{re.escape(keyword)}\s*[=:]\s*([^\s,]*)"
            sanitized = re.sub(pattern, f"{keyword}=[REDACTED]", sanitized, flags=re.IGNORECASE)

        return sanitized

    def _limit_prompt_length(self, prompt: str) -> str:
        """Limita tamanho do prompt"""
        max_length = self.config.get("resource_limits", {}).get("max_prompt_length", 10000)

        if len(prompt) > max_length:
            truncated = prompt[: max_length - 3] + "..."
            logger.warning(
                "Prompt truncated due to length limit",
                original_length=len(prompt),
                truncated_length=len(truncated),
            )
            return truncated

        return prompt

    async def _isolate_context_data(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Isola dados de contexto"""
        isolated = {}

        # Limita tamanho total do contexto
        max_context_size = (
            self.config.get("resource_limits", {}).get("max_context_size_kb", 500) * 1024
        )

        # Chaves sensíveis que devem ter seus valores mascarados
        sensitive_keys = {
            "password",
            "secret",
            "token",
            "key",
            "credential",
            "private",
            "internal",
            "confidential",
            "auth",
            "session",
            "cookie",
            "bearer",
            "authorization",
            "api_key",
            "access_token",
            "refresh_token",
            "client_secret",
            "client_id",
            "database_url",
            "db_connection",
            "connection_string",
            "env",
            "config",
        }

        for key, value in context.items():
            # Se a chave for sensível, mascara o valor
            if key.lower() in sensitive_keys:
                isolated[key] = "[REDACTED]"
            elif isinstance(value, str):
                # Sanitiza strings
                isolated[key] = self._sanitize_text(value)
            elif isinstance(value, (int, float, bool)):
                # Mantém valores primitivos
                isolated[key] = value
            elif isinstance(value, dict):
                # Processa dicionários recursivamente (limitado)
                if len(str(value)) < 1000:  # Limita tamanho de subdicionários
                    isolated[key] = await self._isolate_context_data(value)
                else:
                    isolated[key] = "[CONTEXT_TOO_LARGE]"
            else:
                # Converte outros tipos para string e sanitiza
                isolated[key] = self._sanitize_text(str(value))

        # Verifica tamanho total
        context_size = len(str(isolated).encode("utf-8"))
        if context_size > max_context_size:
            logger.warning(
                "Context size exceeds limit, truncating",
                size_kb=context_size / 1024,
                limit_kb=max_context_size / 1024,
            )
            # Mantém apenas chaves essenciais
            essential_keys = ["task_type", "description", "requirements"]
            isolated = {k: v for k, v in isolated.items() if k in essential_keys}

        return isolated

    async def _filter_allowed_files(self, files: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Filtra arquivos permitidos baseado em regras de segurança"""
        allowed_files = []
        max_files = self.config.get("resource_limits", {}).get("max_context_files", 5)
        max_file_size = self.config.get("resource_limits", {}).get("max_file_size_kb", 100) * 1024
        allowed_extensions = set(self.config.get("allowed_file_extensions", []))

        for file_info in files[:max_files]:  # Limita número de arquivos
            file_name = file_info.get("name", "")
            file_content = file_info.get("content", "")

            # Verifica extensão
            if not self._is_extension_allowed(file_name, allowed_extensions):
                logger.warning("File extension not allowed", file=file_name)
                continue

            # Verifica tamanho
            if len(file_content.encode("utf-8")) > max_file_size:
                logger.warning(
                    "File size exceeds limit",
                    file=file_name,
                    size_kb=len(file_content) / 1024,
                    limit_kb=max_file_size / 1024,
                )
                continue

            # Sanitiza conteúdo do arquivo
            clean_content = self._sanitize_text(file_content)

            allowed_files.append({"name": file_name, "content": clean_content})

        logger.info(
            "Files filtered",
            original_count=len(files),
            allowed_count=len(allowed_files),
        )

        return allowed_files

    def _is_extension_allowed(self, filename: str, allowed_extensions: Set[str]) -> bool:
        """Verifica se extensão do arquivo é permitida"""
        if not allowed_extensions:
            return True  # Se não há restrições, permite tudo

        import os

        _, ext = os.path.splitext(filename.lower())
        return ext in allowed_extensions

    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitiza metadados da tarefa"""
        sanitized = {}

        # Mantém apenas metadados seguros
        safe_keys = {
            "task_type",
            "priority",
            "timeout",
            "created_at",
            "user_id",
            "session_id",
            "correlation_id",
        }

        for key, value in metadata.items():
            if key in safe_keys:
                if isinstance(value, str):
                    sanitized[key] = self._sanitize_text(value)
                else:
                    sanitized[key] = value

        return sanitized

    def validate_isolation_integrity(self, isolated_task: IsolatedTask) -> bool:
        """
        Valida integridade do isolamento.

        Args:
            isolated_task: Tarefa isolada

        Returns:
            True se isolamento está íntegro
        """
        current_hash = isolated_task._calculate_isolation_hash()
        return current_hash == isolated_task.isolation_hash

    def get_isolation_report(
        self, original_task: Any, isolated_task: IsolatedTask
    ) -> Dict[str, Any]:
        """
        Gera relatório de isolamento.

        Args:
            original_task: Tarefa original
            isolated_task: Tarefa isolada

        Returns:
            Relatório detalhado
        """
        return {
            "task_id": isolated_task.task_id,
            "isolation_level": self.config.get("level"),
            "integrity_check": self.validate_isolation_integrity(isolated_task),
            "original_prompt_length": len(getattr(original_task, "prompt", "")),
            "isolated_prompt_length": len(isolated_task.prompt),
            "files_filtered": len(isolated_task.files) if isolated_task.files else 0,
            "sanitization_applied": True,
            "forbidden_patterns_matched": self._count_forbidden_matches(
                getattr(original_task, "prompt", "")
            ),
            "isolation_hash": isolated_task.isolation_hash[:16],
        }

    def _count_forbidden_matches(self, text: str) -> int:
        """Conta quantos padrões proibidos foram encontrados"""
        count = 0
        for pattern in self.forbidden_patterns:
            matches = pattern.findall(text)
            count += len(matches)
        return count
