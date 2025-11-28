import time
from pathlib import Path
import pytest
from src.integrations.mcp_agentic_client import (
import os

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
Tests for MCP Agentic Client module.
"""



    AuditLogEntry,
    CodeExecutionContext,
    MCPAgenticClient,
    MCPSecurityFramework,
    MCPSecurityLevel,
    MCPTool,
    MCPToolCategory,
)


class TestMCPSecurityLevel:
    """Tests for MCPSecurityLevel enum."""

    def test_enum_values(self) -> None:
        """Test security levels."""
        assert MCPSecurityLevel.SANDBOX.value == "sandbox"
        assert MCPSecurityLevel.RESTRICTED.value == "restricted"
        assert MCPSecurityLevel.TRUSTED.value == "trusted"


class TestMCPToolCategory:
    """Tests for MCPToolCategory enum."""

    def test_enum_values(self) -> None:
        """Test tool categories."""
        categories = [
            MCPToolCategory.FILE_SYSTEM,
            MCPToolCategory.VERSION_CONTROL,
            MCPToolCategory.DATABASE,
            MCPToolCategory.BROWSER,
            MCPToolCategory.COMMUNICATION,
            MCPToolCategory.IDE,
        ]

        assert len(categories) == 6


class TestMCPTool:
    """Tests for MCPTool dataclass."""

    def test_creation(self) -> None:
        """Test tool creation."""

        def handler(x: int) -> int:
            return x * 2

        tool = MCPTool(
            tool_id="test_tool",
            name="test",
            category=MCPToolCategory.FILE_SYSTEM,
            security_level=MCPSecurityLevel.SANDBOX,
            schema={"type": "object"},
            handler=handler,
            description="Test tool",
        )

        assert tool.tool_id == "test_tool"
        assert tool.name == "test"
        assert tool.handler(5) == 10


class TestCodeExecutionContext:
    """Tests for CodeExecutionContext."""

    def test_creation(self) -> None:
        """Test context creation."""
        context = CodeExecutionContext(
            code="x = 1", available_tools={}, timeout=30.0, max_memory_mb=256
        )

        assert context.code == "x = 1"
        assert context.timeout == 30.0
        assert "json" in context.allowed_imports


class TestMCPSecurityFramework:
    """Tests for MCP Security Framework."""

    def test_initialization(self) -> None:
        """Test framework initialization."""
        framework = MCPSecurityFramework(
            audit_log_path=Path("/tmp/test_audit.jsonl"), max_operations_per_minute=50
        )

        assert framework.max_ops_per_minute == 50
        assert len(framework.audit_entries) == 0

    def test_validate_code_safety_safe(self) -> None:
        """Test safe code validation."""
        framework = MCPSecurityFramework()

        safe_code = """
x = 1 + 2
result = x * 3
"""

        context = CodeExecutionContext(code=safe_code, available_tools={})

        is_safe, reason = framework.validate_code_safety(safe_code, context)

        assert is_safe is True

    def test_validate_code_safety_dangerous_import(self) -> None:
        """Test dangerous import detection."""
        framework = MCPSecurityFramework()

        dangerous_code = """
import os
os.system('rm -rf /')
"""

        context = CodeExecutionContext(code=dangerous_code, available_tools={})

        is_safe, reason = framework.validate_code_safety(dangerous_code, context)

        assert is_safe is False
        assert "Dangerous" in reason

    def test_validate_code_safety_file_access(self) -> None:
        """Test file access detection."""
        framework = MCPSecurityFramework()

        file_code = """
with open('/etc/passwd', 'r') as f:
    data = f.read()
"""

        context = CodeExecutionContext(code=file_code, available_tools={})

        is_safe, reason = framework.validate_code_safety(file_code, context)

        assert is_safe is False
        assert "Dangerous import/function: open" in reason

    def test_sandbox_execute_safe(self) -> None:
        """Test sandbox execution of safe code."""
        framework = MCPSecurityFramework()

        safe_code = """
x = 5
y = 10
result = x + y
"""

        context = CodeExecutionContext(code=safe_code, available_tools={})

        execution_result = framework.sandbox_execute(
            code=safe_code, context=context, agent_id="test_agent"
        )

        assert execution_result["success"] is True
        assert execution_result["output"] == 15

    def test_sandbox_execute_unsafe(self) -> None:
        """Test sandbox rejection of unsafe code."""
        framework = MCPSecurityFramework()

        unsafe_code = """
import subprocess
subprocess.call(['rm', '-rf', '/'])
"""

        context = CodeExecutionContext(code=unsafe_code, available_tools={})

        execution_result = framework.sandbox_execute(
            code=unsafe_code, context=context, agent_id="test_agent"
        )

        assert execution_result["success"] is False
        assert "Security violation" in execution_result["error"]

    def test_rate_limit(self) -> None:
        """Test rate limiting."""
        framework = MCPSecurityFramework(max_operations_per_minute=5)

        agent_id = "rate_test_agent"

        # First 5 operations should succeed
        for _ in range(5):
            assert framework.check_rate_limit(agent_id) is True

        # 6th operation should fail
        assert framework.check_rate_limit(agent_id) is False

    def test_audit_log(self) -> None:
        """Test audit logging."""
        framework = MCPSecurityFramework()

        initial_count = len(framework.audit_entries)

        framework._audit_log(
            agent_id="test_agent",
            operation="test_op",
            tool_id="test_tool",
            params={"key": "value"},
            result={"output": 42},
            security_level=MCPSecurityLevel.SANDBOX,
        )

        assert len(framework.audit_entries) == initial_count + 1

        entry = framework.audit_entries[-1]
        assert entry.agent_id == "test_agent"
        assert entry.operation == "test_op"
        assert entry.tool_id == "test_tool"


class TestMCPAgenticClient:
    """Tests for MCP Agentic Client."""

    def test_initialization(self) -> None:
        """Test client initialization."""
        client = MCPAgenticClient(agent_id="test_agent", security_level=MCPSecurityLevel.SANDBOX)

        assert client.agent_id == "test_agent"
        assert client.security_level == MCPSecurityLevel.SANDBOX
        assert len(client.tools) > 0  # Default tools registered

    def test_register_tool(self) -> None:
        """Test tool registration."""
        client = MCPAgenticClient(agent_id="test")

        def custom_handler() -> str:
            return "custom"

        tool = MCPTool(
            tool_id="custom_tool",
            name="custom",
            category=MCPToolCategory.IDE,
            security_level=MCPSecurityLevel.SANDBOX,
            schema={},
            handler=custom_handler,
        )

        initial_count = len(client.tools)
        client.register_tool(tool)

        assert len(client.tools) == initial_count + 1
        assert "custom_tool" in client.tools

    def test_execute_agentic_code_simple(self) -> None:
        """Test simple agentic code execution."""
        client = MCPAgenticClient(agent_id="test")

        code = """
x = 10
y = 20
result = x + y
"""

        execution_result = client.execute_agentic_code(code)

        assert execution_result["success"] is True
        assert execution_result["output"] == 30

    def test_execute_agentic_code_with_tool(self) -> None:
        """Test agentic code execution with tool call."""
        client = MCPAgenticClient(agent_id="test")

        code = """
# Using pre-registered database_query tool
result_data = database_query(
    query="SELECT * FROM users",
    params={}
)

if result_data['success']:
    result = f"Found {result_data['count']} users"
else:
    result = "Error"
"""

        execution_result = client.execute_agentic_code(code)

        assert execution_result["success"] is True
        assert "Found" in str(execution_result["output"])

    def test_execute_agentic_code_dangerous(self) -> None:
        """Test rejection of dangerous agentic code."""
        client = MCPAgenticClient(agent_id="test")

        dangerous_code = """
os.system('whoami')
"""

        execution_result = client.execute_agentic_code(dangerous_code)

        assert execution_result["success"] is False
        assert "Security violation" in execution_result["error"]

    def test_get_context_for_ide(self) -> None:
        """Test IDE context retrieval."""
        client = MCPAgenticClient(agent_id="test")

        context = client.get_context_for_ide(file_path="test.py", cursor_position=(10, 5))

        assert context["file_path"] == "test.py"
        assert context["cursor_position"] == (10, 5)
        assert "available_tools" in context
        assert len(context["available_tools"]) > 0

    def test_get_audit_trail(self) -> None:
        """Test audit trail retrieval."""
        client = MCPAgenticClient(agent_id="test")

        # Execute some code to create audit entries
        client.execute_agentic_code("result = 1 + 1")

        audit = client.get_audit_trail(limit=10)

        assert len(audit) > 0
        assert all(isinstance(entry, AuditLogEntry) for entry in audit)


class TestAuditLogEntry:
    """Tests for AuditLogEntry dataclass."""

    def test_creation(self) -> None:
        """Test audit entry creation."""
        entry = AuditLogEntry(
            timestamp=time.time(),
            agent_id="test_agent",
            operation="test_op",
            tool_id="test_tool",
            params={"key": "value"},
            result_hash="abc123",
            security_level=MCPSecurityLevel.SANDBOX,
        )

        assert entry.agent_id == "test_agent"
        assert entry.operation == "test_op"
        assert entry.security_level == MCPSecurityLevel.SANDBOX


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
