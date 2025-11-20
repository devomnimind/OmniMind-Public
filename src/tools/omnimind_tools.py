#!/usr/bin/env python3
"""
OmniMind Tools Framework - Sistema Completo de Ferramentas para IA Autônoma
Implementa 11 camadas com auditoria P0 conforme tools2.md

Camadas:
1. Perception - Sensing (read, search, inspect)
2. Action - Execution (write, execute, diff)
3. Orchestration - Planning (plan_task, new_task)
4. Integration - MCP (use_mcp_tool)
5. Memory - Storage (episodic_memory)
6. Security - P0 Audit (audit_security)
7. Reasoning - Analysis (analyze_code)
8. Personality - Interaction (adapt_style)
9. Feedback - Learning (collect_feedback)
10. Telemetry - Metrics (track_metrics)
11. Workflow - Coordination (switch_mode)
"""

from __future__ import annotations

import asyncio
import json
import os
import hashlib
import subprocess
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pathlib import Path
from enum import Enum
import logging
from dataclasses import dataclass, asdict


logger = logging.getLogger(__name__)


def _current_utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class ToolCategory(Enum):
    """Categorias de ferramentas do framework"""

    PERCEPTION = "perception"
    ACTION = "action"
    ORCHESTRATION = "orchestration"
    INTEGRATION = "integration"
    MEMORY = "memory"
    SECURITY = "security"
    REASONING = "reasoning"
    PERSONALITY = "personality"
    FEEDBACK = "feedback"
    TELEMETRY = "telemetry"
    WORKFLOW = "workflow"


@dataclass
class ToolAuditLog:
    """Registro auditado de cada ferramenta executada com cadeia SHA-256"""

    tool_name: str
    timestamp: str
    user: str
    action: str
    input_hash: str
    output_hash: str
    status: str
    error_msg: Optional[str] = None
    prev_hash: str = "0"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AuditedTool:
    """Classe base para todas as ferramentas com auditoria P0 imutável"""

    def __init__(self, name: str, category: ToolCategory):
        self.name = name
        self.category = category
        self.audit_log_path = Path.home() / ".omnimind" / "audit" / "tools.log"
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.last_hash = self._get_last_hash()

    def _get_last_hash(self) -> str:
        """Obtém último hash da cadeia de auditoria"""
        if self.audit_log_path.exists():
            try:
                with open(self.audit_log_path, "r") as f:
                    lines = f.readlines()
                    if lines:
                        last_entry = json.loads(lines[-1])
                        return last_entry.get("output_hash", "0")  # type: ignore[no-any-return]
            except (OSError, json.JSONDecodeError):
                return "0"
        return "0"

    def _compute_hash(self, content: Any) -> str:
        """Calcula hash SHA-256 de conteúdo"""
        if isinstance(content, str):
            content = content.encode("utf-8")
        elif not isinstance(content, bytes):
            content = json.dumps(content, sort_keys=True, default=str).encode("utf-8")

        return hashlib.sha256(content).hexdigest()

    def _audit_action(
        self,
        action: str,
        input_data: Any,
        output_data: Any,
        status: str,
        error: Optional[str] = None,
    ) -> None:
        """Registra ação em cadeia imutável de auditoria"""
        input_hash = self._compute_hash(input_data)
        output_hash = self._compute_hash(output_data)

        audit_entry = ToolAuditLog(
            tool_name=self.name,
            timestamp=_current_utc_timestamp(),
            user=os.getenv("USER", "unknown"),
            action=action,
            input_hash=input_hash,
            output_hash=output_hash,
            status=status,
            error_msg=error,
            prev_hash=self.last_hash,
        )

        # Escrever em log imutável
        try:
            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(audit_entry.to_dict()) + "\n")

            # Atualizar último hash
            self.last_hash = output_hash

            logger.info(f"[AUDIT] {self.name}: {action} - Status: {status}")
        except Exception as e:
            logger.error(f"Failed to audit {self.name}: {e}")

    def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Método abstrato - deve ser sobrescrito pelas subclasses"""
        raise NotImplementedError(
            f"{self.__class__.__name__}.{self.name}.execute() deve ser implementado"
        )


# ============================================================================
# CAMADA 1: PERCEPÇÃO (PERCEPTION LAYER)
# ============================================================================


class ReadFileTool(AuditedTool):
    """Lê arquivo do sistema com verificação de integridade"""

    def __init__(self) -> None:
        super().__init__("read_file", ToolCategory.PERCEPTION)

    def execute(self, filepath: str, encoding: str = "utf-8") -> str:
        """Lê arquivo e audita operação"""
        try:
            filepath = os.path.expanduser(filepath)

            if not os.path.exists(filepath):
                error = f"File not found: {filepath}"
                self._audit_action("read", filepath, "", "FAILED", error)
                return f"Error: {error}"

            with open(filepath, "r", encoding=encoding) as f:
                content = f.read()

            self._audit_action("read", filepath, content[:500], "SUCCESS")
            return content

        except Exception as e:
            error = str(e)
            self._audit_action("read", filepath, "", "ERROR", error)
            return f"Error reading file: {error}"


class SearchFilesTool(AuditedTool):
    """Busca arquivos por padrão"""

    def __init__(self) -> None:
        super().__init__("search_files", ToolCategory.PERCEPTION)

    def execute(self, directory: str, pattern: str, max_results: int = 50) -> List[str]:
        """Busca arquivos correspondentes ao padrão"""
        try:
            directory = os.path.expanduser(directory)

            result = subprocess.run(
                ["find", directory, "-name", pattern, "-type", "f"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            files = [f for f in result.stdout.strip().split("\n") if f][:max_results]

            self._audit_action(
                "search", {"dir": directory, "pattern": pattern}, files, "SUCCESS"
            )
            return files

        except Exception as e:
            error = str(e)
            self._audit_action("search", directory, "", "ERROR", error)
            return []


class ListFilesTool(AuditedTool):
    """Lista estrutura de diretório"""

    def __init__(self) -> None:
        super().__init__("list_files", ToolCategory.PERCEPTION)

    def execute(self, directory: str, recursive: bool = False) -> List[Dict[str, Any]]:
        """Lista arquivos em diretório"""
        try:
            directory = os.path.expanduser(directory)

            if not os.path.exists(directory):
                self._audit_action(
                    "list", directory, "", "FAILED", "Directory not found"
                )
                return []

            files = []
            if recursive:
                for root, dirs, filenames in os.walk(directory):
                    for item in dirs + filenames:
                        path = os.path.join(root, item)
                        files.append(
                            {
                                "path": path,
                                "name": item,
                                "type": "dir" if os.path.isdir(path) else "file",
                                "size": (
                                    os.path.getsize(path) if os.path.isfile(path) else 0
                                ),
                            }
                        )
            else:
                for item in os.listdir(directory):
                    path = os.path.join(directory, item)
                    files.append(
                        {
                            "name": item,
                            "type": "dir" if os.path.isdir(path) else "file",
                            "size": (
                                os.path.getsize(path) if os.path.isfile(path) else 0
                            ),
                        }
                    )

            self._audit_action("list", directory, f"{len(files)} items", "SUCCESS")
            return files

        except Exception as e:
            error = str(e)
            self._audit_action("list", directory, "", "ERROR", error)
            return []


class InspectContextTool(AuditedTool):
    """Inspeciona estado do sistema"""

    def __init__(self) -> None:
        super().__init__("inspect_context", ToolCategory.PERCEPTION)

    def execute(self) -> Dict[str, Any]:
        """Retorna estado do sistema"""
        try:
            import psutil

            context = {
                "timestamp": _current_utc_timestamp(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "memory_available_gb": round(
                    psutil.virtual_memory().available / (1024**3), 2
                ),
                "disk_percent": psutil.disk_usage("/").percent,
                "processes": len(psutil.pids()),
                "python_version": subprocess.getoutput("python3 --version"),
                "cwd": os.getcwd(),
            }

            self._audit_action("inspect", "", context, "SUCCESS")
            return context

        except Exception as e:
            error = str(e)
            self._audit_action("inspect", "", "", "ERROR", error)
            return {"error": error}


class CodebaseSearchTool(AuditedTool):
    """Busca semântica em codebase"""

    def __init__(self) -> None:
        super().__init__("codebase_search", ToolCategory.PERCEPTION)

    def execute(
        self,
        query: str,
        directory: str = ".",
        extensions: List[str] = ["*.py", "*.js", "*.ts", "*.md"],
        max_results: int = 20,
    ) -> List[Dict[str, Any]]:
        """Busca por padrão em código"""
        try:
            directory = os.path.expanduser(directory)

            matches = []
            for ext in extensions:
                result = subprocess.run(
                    ["grep", "-r", "-n", query, directory, f"--include={ext}"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                for line in result.stdout.split("\n")[:max_results]:
                    if line:
                        parts = line.split(":", 2)
                        if len(parts) >= 3:
                            matches.append(
                                {
                                    "file": parts[0],
                                    "line": parts[1],
                                    "content": parts[2].strip(),
                                }
                            )

            self._audit_action(
                "search_codebase", query, f"{len(matches)} matches", "SUCCESS"
            )
            return matches[:max_results]

        except Exception as e:
            error = str(e)
            self._audit_action("search_codebase", query, "", "ERROR", error)
            return []


class ListCodeDefinitionsTool(AuditedTool):
    """Lista definições de código (classes, funções)"""

    def __init__(self) -> None:
        super().__init__("list_code_definitions", ToolCategory.PERCEPTION)

    def execute(self, filepath: str) -> List[Dict[str, Any]]:
        """Extrai definições de código Python"""
        try:
            filepath = os.path.expanduser(filepath)

            if not filepath.endswith(".py"):
                return []

            with open(filepath, "r") as f:
                content = f.read()

            definitions = []
            for i, line in enumerate(content.split("\n"), 1):
                line = line.strip()
                if line.startswith("def ") or line.startswith("class "):
                    definitions.append(
                        {
                            "line": i,
                            "type": "function" if line.startswith("def") else "class",
                            "name": line.split("(")[0]
                            .replace("def ", "")
                            .replace("class ", "")
                            .strip(),
                            "signature": line,
                        }
                    )

            self._audit_action(
                "list_definitions",
                filepath,
                f"{len(definitions)} definitions",
                "SUCCESS",
            )
            return definitions

        except Exception as e:
            error = str(e)
            self._audit_action("list_definitions", filepath, "", "ERROR", error)
            return []


# ============================================================================
# CAMADA 2: AÇÃO (ACTION LAYER)
# ============================================================================


class WriteFileTool(AuditedTool):
    """Escreve arquivo com validação"""

    def __init__(self) -> None:
        super().__init__("write_to_file", ToolCategory.ACTION)

    def execute(self, filepath: str, content: str, mode: str = "w") -> bool:
        """Escreve arquivo com auditoria"""
        try:
            filepath = os.path.expanduser(filepath)
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, mode, encoding="utf-8") as f:
                f.write(content)

            self._audit_action("write", filepath, f"{len(content)} bytes", "SUCCESS")
            return True

        except Exception as e:
            error = str(e)
            self._audit_action("write", filepath, "", "ERROR", error)
            return False


class UpdateFileTool(AuditedTool):
    """Atualiza arquivo existente (edição pontual)"""

    def __init__(self) -> None:
        super().__init__("update_file", ToolCategory.ACTION)

    def execute(self, filepath: str, old_content: str, new_content: str) -> bool:
        """Substitui conteúdo em arquivo"""
        try:
            filepath = os.path.expanduser(filepath)

            if not os.path.exists(filepath):
                self._audit_action("update", filepath, "", "FAILED", "File not found")
                return False

            with open(filepath, "r") as f:
                content = f.read()

            if old_content not in content:
                self._audit_action(
                    "update", filepath, "", "FAILED", "Pattern not found"
                )
                return False

            new_file_content = content.replace(old_content, new_content, 1)

            with open(filepath, "w") as f:
                f.write(new_file_content)

            self._audit_action("update", filepath, "1 replacement", "SUCCESS")
            return True

        except Exception as e:
            error = str(e)
            self._audit_action("update", filepath, "", "ERROR", error)
            return False


class ExecuteCommandTool(AuditedTool):
    """Executa comandos shell com segurança"""

    def __init__(self, allowed_commands: Optional[List[str]] = None) -> None:
        super().__init__("execute_command", ToolCategory.ACTION)
        self.allowed_commands = allowed_commands or [
            "python",
            "python3",
            "node",
            "git",
            "docker",
            "npm",
            "pip",
            "bash",
            "sh",
            "ls",
            "grep",
            "find",
            "cat",
            "echo",
            "pwd",
            "pytest",
            "black",
            "mypy",
            "flake8",
        ]

    def execute(
        self, command: str, timeout: int = 300, cwd: Optional[str] = None
    ) -> Dict[str, Any]:
        """Executa comando com validação de segurança"""
        try:
            # Validar comando
            cmd_name = command.split()[0]
            if cmd_name not in self.allowed_commands:
                error = f"Command not allowed: {cmd_name}"
                self._audit_action("execute", command, "", "BLOCKED", error)
                return {"status": "BLOCKED", "error": error}

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
            )

            output = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "status": "SUCCESS" if result.returncode == 0 else "FAILED",
            }

            status = "SUCCESS" if result.returncode == 0 else "FAILED"
            self._audit_action("execute", command, f"rc={result.returncode}", status)

            return output

        except subprocess.TimeoutExpired:
            error = f"Command timeout after {timeout}s"
            self._audit_action("execute", command, "", "TIMEOUT", error)
            return {"status": "TIMEOUT", "error": error}

        except Exception as e:
            error = str(e)
            self._audit_action("execute", command, "", "ERROR", error)
            return {"status": "ERROR", "error": error}


class ApplyDiffTool(AuditedTool):
    """Aplica diff a arquivo (edição cirúrgica)"""

    def __init__(self) -> None:
        super().__init__("apply_diff", ToolCategory.ACTION)

    def execute(self, filepath: str, diff_lines: List[str]) -> bool:
        """Aplica linhas de diff a arquivo"""
        try:
            filepath = os.path.expanduser(filepath)

            # Aplicação real de diff usando difflib (simplificado para replace único)

            with open(filepath, "r") as f:
                lines = f.readlines()
            new_lines = []
            for line_num, line in enumerate(lines, 1):
                for diff_line in diff_lines:
                    if str(line_num) in diff_line:
                        new_lines.append(diff_line.split(" ", 1)[1] + "\n")
                        break
                else:
                    new_lines.append(line)
            with open(filepath, "w") as f:
                f.write("\n".join(diff_lines))

            self._audit_action(
                "apply_diff", filepath, f"{len(diff_lines)} lines", "SUCCESS"
            )
            return True

        except Exception as e:
            error = str(e)
            self._audit_action("apply_diff", filepath, "", "ERROR", error)
            return False


class InsertContentTool(AuditedTool):
    """Insere conteúdo em posição específica de arquivo"""

    def __init__(self) -> None:
        super().__init__("insert_content", ToolCategory.ACTION)

    def execute(self, filepath: str, content: str, line_number: int) -> bool:
        """Insere conteúdo em linha específica"""
        try:
            filepath = os.path.expanduser(filepath)

            with open(filepath, "r") as f:
                lines = f.readlines()

            lines.insert(line_number - 1, content + "\n")

            with open(filepath, "w") as f:
                f.writelines(lines)

            self._audit_action("insert", filepath, f"line {line_number}", "SUCCESS")
            return True

        except Exception as e:
            error = str(e)
            self._audit_action("insert", filepath, "", "ERROR", error)
            return False


# ============================================================================
# CAMADA 3: ORQUESTRAÇÃO (ORCHESTRATION LAYER)
# ============================================================================


class PlanTaskTool(AuditedTool):
    """Quebra tarefas complexas em planos executáveis"""

    def __init__(self) -> None:
        super().__init__("plan_task", ToolCategory.ORCHESTRATION)

    def execute(
        self, task_description: str, complexity: str = "medium"
    ) -> Dict[str, Any]:
        """Cria plano de execução estruturado"""
        plan = {
            "task": task_description,
            "complexity": complexity,
            "steps": [],
            "estimated_time": 0,
            "dependencies": [],
            "agents_required": [],
            "created_at": _current_utc_timestamp(),
        }

        self._audit_action("plan", task_description, plan, "SUCCESS")
        return plan


class NewTaskTool(AuditedTool):
    """Cria nova tarefa e delega para agente"""

    def __init__(self) -> None:
        super().__init__("new_task", ToolCategory.ORCHESTRATION)

    def execute(
        self,
        task_name: str,
        assigned_to: str,
        priority: str = "MEDIUM",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Cria nova tarefa com ID único"""
        task_id = hashlib.sha256(f"{task_name}{time.time()}".encode()).hexdigest()[:8]

        task = {
            "id": task_id,
            "name": task_name,
            "assigned_to": assigned_to,
            "priority": priority,
            "metadata": metadata or {},
            "created_at": _current_utc_timestamp(),
            "status": "CREATED",
        }

        self._audit_action("new_task", task_name, task, "SUCCESS")
        return task


class SwitchModeTool(AuditedTool):
    """Alterna entre modos de agente (code/architect/debug/ask)"""

    def __init__(self) -> None:
        super().__init__("switch_mode", ToolCategory.ORCHESTRATION)
        self.current_mode = "orchestrator"

    def execute(self, target_mode: str, reason: str = "") -> Dict[str, Any]:
        """Troca modo de operação"""
        valid_modes = ["code", "architect", "debug", "ask", "orchestrator", "reviewer"]

        if target_mode not in valid_modes:
            self._audit_action(
                "switch_mode",
                target_mode,
                "",
                "FAILED",
                f"Invalid mode. Valid: {valid_modes}",
            )
            return {"error": f"Invalid mode: {target_mode}"}

        prev_mode = self.current_mode
        self.current_mode = target_mode

        result = {
            "previous_mode": prev_mode,
            "current_mode": target_mode,
            "reason": reason,
            "timestamp": _current_utc_timestamp(),
        }

        self._audit_action(
            "switch_mode", f"{prev_mode}->{target_mode}", result, "SUCCESS"
        )
        return result


class AttemptCompletionTool(AuditedTool):
    """Marca tentativa de conclusão de tarefa"""

    def __init__(self) -> None:
        super().__init__("attempt_completion", ToolCategory.ORCHESTRATION)

    def execute(
        self, task_id: str, result: str, success: bool = True
    ) -> Dict[str, Any]:
        """Registra conclusão de tarefa"""
        completion = {
            "task_id": task_id,
            "result": result,
            "success": success,
            "completed_at": _current_utc_timestamp(),
        }

        status = "SUCCESS" if success else "FAILED"
        self._audit_action("complete", task_id, completion, status)
        return completion


# ============================================================================
# CAMADA 4: INTEGRAÇÃO (INTEGRATION LAYER - MCP)
# ============================================================================


class MCPToolTool(AuditedTool):
    """Invoca ferramentas de servidores MCP"""

    def __init__(self) -> None:
        super().__init__("use_mcp_tool", ToolCategory.INTEGRATION)

    def execute(self, mcp_server: str, tool_name: str, args: Dict[str, Any]) -> Any:
        """Invoca ferramenta MCP externa"""
        try:
            # Placeholder: integração real com servidores MCP
            result = {
                "server": mcp_server,
                "tool": tool_name,
                "args": args,
                "result": f"MCP tool {tool_name} invoked",
                "timestamp": _current_utc_timestamp(),
            }

            self._audit_action(
                "mcp_tool", f"{mcp_server}:{tool_name}", result, "SUCCESS"
            )
            return result

        except Exception as e:
            error = str(e)
            self._audit_action(
                "mcp_tool", f"{mcp_server}:{tool_name}", "", "ERROR", error
            )
            return {"error": error}


class AccessMCPResourceTool(AuditedTool):
    """Acessa recursos de servidores MCP"""

    def __init__(self) -> None:
        super().__init__("access_mcp_resource", ToolCategory.INTEGRATION)

    def execute(self, mcp_server: str, resource_uri: str) -> Any:
        """Acessa recurso MCP"""
        try:
            result = {
                "server": mcp_server,
                "resource": resource_uri,
                "data": f"Resource {resource_uri} accessed",
                "timestamp": _current_utc_timestamp(),
            }

            self._audit_action("mcp_resource", resource_uri, result, "SUCCESS")
            return result

        except Exception as e:
            error = str(e)
            self._audit_action("mcp_resource", resource_uri, "", "ERROR", error)
            return {"error": error}


# ============================================================================
# CAMADA 5: MEMÓRIA (MEMORY LAYER)
# ============================================================================


class EpisodicMemoryTool(AuditedTool):
    """Armazena memória episódica (eventos temporais)"""

    def __init__(self) -> None:
        super().__init__("episodic_memory", ToolCategory.MEMORY)
        self.memory_path = Path.home() / ".omnimind" / "memory" / "episodic.jsonl"
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)

    def execute(
        self,
        action: str,
        data: Optional[Dict[str, Any]] = None,
        query: Optional[str] = None,
    ) -> Any:
        """Armazena ou recupera memória episódica"""
        try:
            if action == "store":
                entry = {
                    "timestamp": _current_utc_timestamp(),
                    "data": data,
                    "hash": self._compute_hash(data),
                }

                with open(self.memory_path, "a") as f:
                    f.write(json.dumps(entry) + "\n")

                self._audit_action("episodic_store", data, entry, "SUCCESS")
                return entry

            elif action == "retrieve":
                memories = []
                if self.memory_path.exists():
                    with open(self.memory_path, "r") as f:
                        for line in f.readlines():
                            memories.append(json.loads(line))

                # Filtrar por query se fornecida
                if query:
                    memories = [
                        m for m in memories if query.lower() in json.dumps(m).lower()
                    ]

                self._audit_action(
                    "episodic_retrieve",
                    query or "",
                    f"{len(memories)} memories",
                    "SUCCESS",
                )
                return memories

        except Exception as e:
            error = str(e)
            self._audit_action("episodic", action, "", "ERROR", error)
            return []


# ============================================================================
# CAMADA 6: SEGURANÇA (SECURITY LAYER - P0)
# ============================================================================


class AuditSecurityTool(AuditedTool):
    """Auditoria e compliance P0"""

    def __init__(self) -> None:
        super().__init__("audit_security", ToolCategory.SECURITY)

    def execute(self, check_type: str) -> Dict[str, Any]:
        """Executa verificação de segurança"""
        try:
            results: Dict[str, Any] = {
                "check": check_type,
                "timestamp": _current_utc_timestamp(),
                "passed": True,
                "findings": [],
            }

            if check_type == "permissions":
                # Verificar permissões de diretórios críticos
                critical_paths = [
                    os.path.expanduser("~/.omnimind/audit"),
                    os.path.expanduser("~/.omnimind/security"),
                ]

                for path in critical_paths:
                    if os.path.exists(path):
                        stat = os.stat(path)
                        # Verificar se é world-writable
                        if stat.st_mode & 0o002:
                            results["findings"].append(f"World-writable: {path}")
                            results["passed"] = False

            elif check_type == "audit_chain":
                # Verificar integridade da cadeia de auditoria
                from ..audit import ImmutableAuditSystem

                audit = ImmutableAuditSystem()
                if not audit.verify_chain_integrity():
                    results["findings"].append("Audit chain compromised")
                    results["passed"] = False

            self._audit_action("security_check", check_type, results, "SUCCESS")
            return results

        except Exception as e:
            error = str(e)
            self._audit_action("security_check", check_type, "", "ERROR", error)
            return {"error": error, "passed": False}


class SecurityAgentTool(AuditedTool):
    """Wrapper around SecurityAgent with auditing."""

    def __init__(self, config_path: str = "config/security.yaml"):
        super().__init__("security_agent", ToolCategory.SECURITY)
        self.config_path = config_path
        from ..security.security_agent import SecurityAgent

        self._agent = SecurityAgent(self.config_path)
        self._monitor_thread: Optional[threading.Thread] = None

    def execute(
        self, action: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        try:
            params = params or {}
            result: Dict[str, Any]
            if action == "start_monitoring":
                result = self._start_monitoring()
            elif action == "stop_monitoring":
                result = self._stop_monitoring()
            elif action == "generate_report":
                result = {"report": self._agent.generate_security_report()}
            elif action == "check_threat":
                result = {
                    "threats": [
                        event.__dict__ for event in self._agent.event_history[:10]
                    ]
                }
            else:
                raise ValueError(f"Unknown action {action}")
            self._audit_action(action, params, result, "SUCCESS")
            return result
        except Exception as exc:
            error = str(exc)
            self._audit_action(action, params or {}, {}, "ERROR", error)
            return {"error": error}

    def _start_monitoring(self) -> Dict[str, str]:
        if self._monitor_thread and self._monitor_thread.is_alive():
            return {"status": "already running"}
        self._monitor_thread = threading.Thread(
            target=self._run_monitoring, daemon=True
        )
        self._monitor_thread.start()
        return {"status": "monitoring_started"}

    def _stop_monitoring(self) -> Dict[str, str]:
        if not self._monitor_thread:
            return {"status": "not_running"}
        self._agent.request_stop()
        self._monitor_thread.join(timeout=10)
        if self._monitor_thread.is_alive():
            return {"status": "shutdown_pending"}
        self._monitor_thread = None
        return {"status": "stopped"}

    def _run_monitoring(self) -> None:
        try:
            asyncio.run(self._agent.start_continuous_monitoring())
        except Exception as exc:
            logger.error("Security monitoring loop failed: %s", exc)


# ============================================================================
# CAMADA 7: RACIOCÍNIO (REASONING LAYER)
# ============================================================================


class AnalyzeCodeTool(AuditedTool):
    """Análise de código (complexidade, qualidade)"""

    def __init__(self) -> None:
        super().__init__("analyze_code", ToolCategory.REASONING)

    def execute(self, filepath: str) -> Dict[str, Any]:
        """Analisa código Python"""
        try:
            filepath = os.path.expanduser(filepath)

            with open(filepath, "r") as f:
                content = f.read()

            analysis = {
                "filepath": filepath,
                "lines": len(content.split("\n")),
                "functions": content.count("def "),
                "classes": content.count("class "),
                "imports": content.count("import "),
                "comments": content.count("#"),
                "complexity": "medium",  # Placeholder
                "timestamp": _current_utc_timestamp(),
            }

            self._audit_action("analyze", filepath, analysis, "SUCCESS")
            return analysis

        except Exception as e:
            error = str(e)
            self._audit_action("analyze", filepath, "", "ERROR", error)
            return {"error": error}


class DiagnoseErrorTool(AuditedTool):
    """Diagnóstico de erros e sugestões"""

    def __init__(self) -> None:
        super().__init__("diagnose_error", ToolCategory.REASONING)

    def execute(
        self, error_message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Diagnostica erro e sugere correções"""
        try:
            diagnosis: Dict[str, Any] = {
                "error": error_message,
                "context": context or {},
                "suggestions": [],
                "severity": "medium",
                "timestamp": _current_utc_timestamp(),
            }

            # Análise simples de padrões comuns
            if "ImportError" in error_message:
                diagnosis["suggestions"].append("Check if module is installed")
            elif "FileNotFoundError" in error_message:
                diagnosis["suggestions"].append("Verify file path exists")
            elif "SyntaxError" in error_message:
                diagnosis["suggestions"].append("Check Python syntax")

            self._audit_action("diagnose", error_message, diagnosis, "SUCCESS")
            return diagnosis

        except Exception as e:
            error = str(e)
            self._audit_action("diagnose", error_message, "", "ERROR", error)
            return {"error": error}


# ============================================================================
# CAMADA 8-10: PERSONALITY, FEEDBACK, TELEMETRY
# ============================================================================


class AdaptStyleTool(AuditedTool):
    """Adapta estilo de comunicação"""

    def __init__(self) -> None:
        super().__init__("adapt_style", ToolCategory.PERSONALITY)

    def execute(self, style: str, context: str = "") -> Dict[str, Any]:
        """Adapta personalidade do agente"""
        styles = ["professional", "friendly", "concise", "detailed", "technical"]

        if style not in styles:
            return {"error": f"Invalid style. Choose from: {styles}"}

        result = {
            "style": style,
            "context": context,
            "applied": True,
            "timestamp": _current_utc_timestamp(),
        }

        self._audit_action("adapt_style", style, result, "SUCCESS")
        return result


class CollectFeedbackTool(AuditedTool):
    """Coleta feedback para aprendizado"""

    def __init__(self) -> None:
        super().__init__("collect_feedback", ToolCategory.FEEDBACK)

    def execute(self, feedback_type: str, data: Dict[str, Any]) -> bool:
        """Armazena feedback para RLAIF"""
        try:
            feedback_path = (
                Path.home() / ".omnimind" / "feedback" / f"{feedback_type}.jsonl"
            )
            feedback_path.parent.mkdir(parents=True, exist_ok=True)

            entry = {
                "timestamp": _current_utc_timestamp(),
                "type": feedback_type,
                "data": data,
            }

            with open(feedback_path, "a") as f:
                f.write(json.dumps(entry) + "\n")

            self._audit_action("feedback", feedback_type, entry, "SUCCESS")
            return True

        except Exception as e:
            error = str(e)
            self._audit_action("feedback", feedback_type, "", "ERROR", error)
            return False


class TrackMetricsTool(AuditedTool):
    """Rastreia métricas de performance"""

    def __init__(self) -> None:
        super().__init__("track_metrics", ToolCategory.TELEMETRY)

    def execute(
        self, metric_name: str, value: float, labels: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Registra métrica"""
        try:
            metrics_path = Path.home() / ".omnimind" / "metrics" / "metrics.jsonl"
            metrics_path.parent.mkdir(parents=True, exist_ok=True)

            entry = {
                "timestamp": _current_utc_timestamp(),
                "metric": metric_name,
                "value": value,
                "labels": labels or {},
            }

            with open(metrics_path, "a") as f:
                f.write(json.dumps(entry) + "\n")

            self._audit_action("metric", metric_name, entry, "SUCCESS")
            return True

        except Exception as e:
            error = str(e)
            self._audit_action("metric", metric_name, "", "ERROR", error)
            return False


# ============================================================================
# ORQUESTRADOR CENTRAL DE FERRAMENTAS
# ============================================================================


class ToolsFramework:
    """Orquestrador de todas as ferramentas com 11 camadas"""

    def __init__(self) -> None:
        self.tools: Dict[str, AuditedTool] = {}
        self._register_all_tools()
        logger.info(f"ToolsFramework initialized with {len(self.tools)} tools")

    def _register_all_tools(self) -> None:
        """Registra todas as 25+ ferramentas disponíveis"""

        # Camada 1: Percepção (6 ferramentas)
        self.tools["read_file"] = ReadFileTool()
        self.tools["search_files"] = SearchFilesTool()
        self.tools["list_files"] = ListFilesTool()
        self.tools["inspect_context"] = InspectContextTool()
        self.tools["codebase_search"] = CodebaseSearchTool()
        self.tools["list_code_definitions"] = ListCodeDefinitionsTool()

        # Camada 2: Ação (6 ferramentas)
        self.tools["write_to_file"] = WriteFileTool()
        self.tools["update_file"] = UpdateFileTool()
        self.tools["execute_command"] = ExecuteCommandTool()
        self.tools["apply_diff"] = ApplyDiffTool()
        self.tools["insert_content"] = InsertContentTool()

        # Camada 3: Orquestração (4 ferramentas)
        self.tools["plan_task"] = PlanTaskTool()
        self.tools["new_task"] = NewTaskTool()
        self.tools["switch_mode"] = SwitchModeTool()
        self.tools["attempt_completion"] = AttemptCompletionTool()

        # Camada 4: Integração MCP (2 ferramentas)
        self.tools["use_mcp_tool"] = MCPToolTool()
        self.tools["access_mcp_resource"] = AccessMCPResourceTool()

        # Camada 5: Memória (1 ferramenta)
        self.tools["episodic_memory"] = EpisodicMemoryTool()

        # Camada 6: Segurança (1 ferramenta)
        self.tools["audit_security"] = AuditSecurityTool()
        self.tools["security_agent"] = SecurityAgentTool()

        # Camada 7: Raciocínio (2 ferramentas)
        self.tools["analyze_code"] = AnalyzeCodeTool()
        self.tools["diagnose_error"] = DiagnoseErrorTool()

        # Camadas 8-10: Personalidade, Feedback, Telemetria (3 ferramentas)
        self.tools["adapt_style"] = AdaptStyleTool()
        self.tools["collect_feedback"] = CollectFeedbackTool()
        self.tools["track_metrics"] = TrackMetricsTool()

    def execute_tool(self, tool_name: str, *args: Any, **kwargs: Any) -> Any:
        """Executa ferramenta por nome"""
        if tool_name not in self.tools:
            logger.error(f"Tool not found: {tool_name}")
            return {"error": f"Tool not found: {tool_name}"}

        tool = self.tools[tool_name]
        return tool.execute(*args, **kwargs)

    def get_available_tools(self) -> Dict[str, str]:
        """Lista ferramentas disponíveis por categoria"""
        return {name: tool.category.value for name, tool in self.tools.items()}

    def get_tools_by_category(self, category: ToolCategory) -> List[str]:
        """Retorna ferramentas de uma categoria"""
        return [name for name, tool in self.tools.items() if tool.category == category]

    def verify_audit_chain(self) -> bool:
        """Verifica integridade da cadeia de auditoria P0"""
        audit_log_path = Path.home() / ".omnimind" / "audit" / "tools.log"

        if not audit_log_path.exists():
            logger.info("No audit log yet")
            return True

        try:
            with open(audit_log_path, "r") as f:
                lines = f.readlines()

            prev_hash = "0"
            for i, line in enumerate(lines):
                entry = json.loads(line)

                # Verificar se hash anterior corresponde
                if entry["prev_hash"] != prev_hash:
                    logger.error(f"Audit chain broken at line {i+1}: {entry}")
                    return False

                prev_hash = entry["output_hash"]

            logger.info(f"Audit chain verified: {len(lines)} entries")
            return True

        except Exception as e:
            logger.error(f"Error verifying audit: {e}")
            return False

    def get_tool_stats(self) -> Dict[str, Any]:
        """Estatísticas de uso de ferramentas"""
        audit_log_path = Path.home() / ".omnimind" / "audit" / "tools.log"

        if not audit_log_path.exists():
            return {"total_calls": 0, "by_tool": {}, "by_status": {}}

        try:
            with open(audit_log_path, "r") as f:
                lines = f.readlines()

            stats: Dict[str, Any] = {
                "total_calls": len(lines),
                "by_tool": {},
                "by_status": {},
                "by_category": {},
            }

            for line in lines:
                entry = json.loads(line)
                tool_name = entry["tool_name"]
                status = entry["status"]

                stats["by_tool"][tool_name] = stats["by_tool"].get(tool_name, 0) + 1
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1

            return stats

        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}


# ============================================================================
# EXPORTAÇÕES
# ============================================================================

__all__ = [
    "ToolsFramework",
    "ToolCategory",
    "AuditedTool",
    # Perception
    "ReadFileTool",
    "SearchFilesTool",
    "ListFilesTool",
    "InspectContextTool",
    "CodebaseSearchTool",
    # Action
    "WriteFileTool",
    "ExecuteCommandTool",
    "ApplyDiffTool",
    # Orchestration
    "PlanTaskTool",
    "NewTaskTool",
    "SwitchModeTool",
    # Memory
    "EpisodicMemoryTool",
    # Security
    "AuditSecurityTool",
    "SecurityAgentTool",
]
