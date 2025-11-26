#!/usr/bin/env python3
"""
Integration Tests for Enhanced Agent System

Testa integração entre AST parser, comunicação inter-agentes e agentes aprimorados.
"""

import pytest
from pathlib import Path
from src.agents.code_agent import CodeAgent
from src.agents.architect_agent import ArchitectAgent
from src.agents.agent_protocol import (
    MessageType,
    MessagePriority,
    get_message_bus,
)


class TestCodeAgentIntegration:
    """Testes de integração do CodeAgent com AST parser"""

    @pytest.fixture
    def code_agent(self, tmp_path: Path) -> CodeAgent:
        """Fixture para criar CodeAgent"""
        # Criar arquivo de configuração temporário
        config_file = tmp_path / "config.yaml"
        config_content = """
model:
  name: qwen2.5-coder:3b
  base_url: http://localhost:11434
  temperature: 0.7

memory:
  qdrant_url: http://localhost:6333
  collection_name: test_episodes

system:
  mcp_allowed_dirs:
    - /tmp
  shell_whitelist:
    - echo
    - ls
  shell_timeout: 30
"""
        config_file.write_text(config_content)
        return CodeAgent(str(config_file))

    def test_code_agent_ast_integration(
        self, code_agent: CodeAgent, tmp_path: Path
    ) -> None:
        """Testa integração do CodeAgent com AST parser"""
        # Criar arquivo Python de teste
        test_file = tmp_path / "test_code.py"
        test_file.write_text(
            """
import os
from typing import List

def greet(name: str) -> str:
    '''Greet a person'''
    return f"Hello, {name}!"

class Calculator:
    '''Simple calculator'''
    def add(self, x: int, y: int) -> int:
        return x + y
"""
        )

        # Analisar estrutura
        result = code_agent.analyze_code_structure(str(test_file))

        assert result["filepath"] == str(test_file)
        assert len(result["classes"]) == 1
        assert result["classes"][0]["name"] == "Calculator"
        assert len(result["functions"]) >= 1
        assert any(f["name"] == "greet" for f in result["functions"])
        assert "os" in result["dependencies"]

    def test_code_agent_syntax_validation(self, code_agent: CodeAgent) -> None:
        """Testa validação de sintaxe"""
        # Código válido
        valid_code = "def test(): return 42"
        result = code_agent.validate_code_syntax(valid_code)
        assert result["valid"] is True
        assert result["error"] is None

        # Código inválido
        invalid_code = "def test( return 42"
        result = code_agent.validate_code_syntax(invalid_code)
        assert result["valid"] is False
        assert result["error"] is not None

    def test_code_agent_security_analysis(self, code_agent: CodeAgent) -> None:
        """Testa análise de segurança"""
        # Código inseguro
        dangerous_code = """
def unsafe():
    user_input = input("Enter code: ")
    result = eval(user_input)
    return result
"""
        result = code_agent.analyze_code_security(dangerous_code)
        assert result["safe"] is False
        assert len(result["warnings"]) > 0
        assert result["severity"] == "high"

    def test_code_agent_skeleton_generation(self, code_agent: CodeAgent) -> None:
        """Testa geração de esqueleto de código"""
        methods = [
            ("__init__", ["name: str"], "None"),
            ("process", ["data: dict"], "str"),
        ]
        skeleton = code_agent.generate_code_skeleton("DataProcessor", methods)

        assert "class DataProcessor:" in skeleton
        assert "def __init__(self, name: str) -> None:" in skeleton
        assert "def process(self, data: dict) -> str:" in skeleton


class TestArchitectAgentIntegration:
    """Testes de integração do ArchitectAgent"""

    @pytest.fixture
    def architect_agent(self, tmp_path: Path) -> ArchitectAgent:
        """Fixture para criar ArchitectAgent"""
        config_file = tmp_path / "config.yaml"
        config_content = """
model:
  name: qwen2.5-coder:3b
  base_url: http://localhost:11434
  temperature: 0.7

memory:
  qdrant_url: http://localhost:6333
  collection_name: test_episodes

system:
  mcp_allowed_dirs:
    - /tmp
  shell_whitelist:
    - echo
  shell_timeout: 30
"""
        config_file.write_text(config_content)
        return ArchitectAgent(str(config_file))

    def test_architect_dependency_analysis(
        self, architect_agent: ArchitectAgent, tmp_path: Path
    ) -> None:
        """Testa análise de dependências"""
        # Criar requirements.txt
        req_file = tmp_path / "requirements.txt"
        req_file.write_text("pytest>=7.0.0\nfastapi>=0.100.0\n")

        result = architect_agent.analyze_dependencies(str(tmp_path))

        assert result["directory"] == str(tmp_path)
        assert "python" in result["dependencies"]
        assert "pytest>=7.0.0" in result["dependencies"]["python"]
        assert result["total_deps"] >= 2

    def test_architect_diagram_generation(
        self, architect_agent: ArchitectAgent
    ) -> None:
        """Testa geração de diagramas"""
        components = ["Frontend", "Backend", "Database"]
        connections = [
            ("Frontend", "Backend"),
            ("Backend", "Database"),
        ]

        diagram = architect_agent.create_architecture_diagram(components, connections)

        assert "```mermaid" in diagram
        assert "graph TD" in diagram
        assert "A[Frontend]" in diagram
        assert "B[Backend]" in diagram
        assert "C[Database]" in diagram
        assert "A --> B" in diagram

    def test_architect_spec_generation(
        self, architect_agent: ArchitectAgent, tmp_path: Path
    ) -> None:
        """Testa geração de especificação"""
        sections = {
            "Overview": "This is a test specification",
            "Architecture": "The system consists of 3 components",
        }

        output_path = tmp_path / "spec.md"
        result = architect_agent.generate_spec_document(
            "Test Specification", sections, str(output_path)
        )

        assert result["success"] is True
        assert output_path.exists()

        content = output_path.read_text()
        assert "# Test Specification" in content
        assert "## Overview" in content
        assert "## Architecture" in content


@pytest.mark.asyncio
class TestAgentCommunicationIntegration:
    """Testes de integração de comunicação inter-agentes"""

    @pytest.fixture
    async def message_bus(self):
        """Fixture para message bus"""
        bus = get_message_bus()
        await bus.start()
        # Limpar estado anterior
        bus._queues.clear()
        bus._subscriptions.clear()
        bus._pending_responses.clear()
        yield bus
        await bus.stop()

    async def test_code_agent_communication(self, message_bus, tmp_path: Path) -> None:
        """Testa comunicação do CodeAgent"""
        config_file = tmp_path / "config.yaml"
        config_content = """
model:
  name: qwen2.5-coder:3b
  base_url: http://localhost:11434
  temperature: 0.7

memory:
  qdrant_url: http://localhost:6333
  collection_name: test_episodes

system:
  mcp_allowed_dirs:
    - /tmp
  shell_whitelist:
    - echo
  shell_timeout: 30
"""
        config_file.write_text(config_content)

        agent = CodeAgent(str(config_file))
        message_bus.register_agent(agent.agent_id)
        message_bus.subscribe(agent.agent_id, [MessageType.REQUEST])

        # Enviar mensagem para o agente
        await agent.send_message(
            recipient=agent.agent_id,
            message_type=MessageType.REQUEST,
            payload={"action": "analyze", "file": "test.py"},
        )

        # Receber mensagem
        received = await agent.receive_message(timeout=1.0)

        assert received is not None
        assert received.message_type == MessageType.REQUEST
        assert received.payload["action"] == "analyze"

    async def test_multi_agent_coordination(self, message_bus, tmp_path: Path) -> None:
        """Testa coordenação entre múltiplos agentes"""
        config_file = tmp_path / "config.yaml"
        config_content = """
model:
  name: qwen2.5-coder:3b
  base_url: http://localhost:11434
  temperature: 0.7

memory:
  qdrant_url: http://localhost:6333
  collection_name: test_episodes

system:
  mcp_allowed_dirs:
    - /tmp
  shell_whitelist:
    - echo
  shell_timeout: 30
"""
        config_file.write_text(config_content)

        code_agent = CodeAgent(str(config_file))
        architect_agent = ArchitectAgent(str(config_file))

        message_bus.register_agent(code_agent.agent_id)
        message_bus.register_agent(architect_agent.agent_id)

        # ArchitectAgent envia tarefa para CodeAgent
        await architect_agent.send_message(
            recipient=code_agent.agent_id,
            message_type=MessageType.TASK_DELEGATION,
            payload={"task": "implement_feature", "spec": "Feature X"},
            priority=MessagePriority.HIGH,
        )

        # CodeAgent recebe tarefa
        task = await code_agent.receive_message(timeout=1.0)

        assert task is not None
        assert task.message_type == MessageType.TASK_DELEGATION
        assert task.sender == architect_agent.agent_id
        assert task.priority == MessagePriority.HIGH


# ============================================================================
# EXPORTAÇÕES
# ============================================================================

__all__ = [
    "TestCodeAgentIntegration",
    "TestArchitectAgentIntegration",
    "TestAgentCommunicationIntegration",
]
