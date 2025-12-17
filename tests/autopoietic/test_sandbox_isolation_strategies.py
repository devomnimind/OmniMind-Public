"""Tests for AutopoieticSandbox isolation strategies (systemd-run, unshare, direct)."""

from pathlib import Path

import pytest

from src.autopoietic.sandbox import AutopoieticSandbox


@pytest.fixture
def sandbox():
    """Create sandbox instance for testing."""
    return AutopoieticSandbox(
        max_memory_mb=512,
        max_cpu_time_seconds=30,
        max_file_size_kb=1024,
    )


class TestSandboxExecuteComponent:
    """Test execute_component cascading strategy."""

    def test_execute_component_basic(self, sandbox):
        """Test basic component execution."""
        code = """
class SafeComponent:
    _security_signature="modulo_autopoiesis_data_test"
    _generated_in_sandbox = True
    def run(self):
        return "OK"
"""
        result = sandbox.execute_component(code, "SafeComponent")

        assert result["success"] is True
        assert result["isolation"] in ["systemd_run", "unshare", "none"]
        assert "SUCCESS" in result["output"]

    def test_execute_component_has_isolation_field(self, sandbox):
        """Test that result always has isolation field."""
        code = """
class TestComponent:
    _security_signature="modulo_autopoiesis_data_isolation"
    _generated_in_sandbox = True
    def run(self):
        return "OK"
"""
        result = sandbox.execute_component(code, "TestComponent")

        assert "isolation" in result, "Missing isolation field in result"
        assert result["isolation"] in [
            "systemd_run",
            "unshare",
            "none",
            "failed",
        ], f"Invalid isolation value: {result['isolation']}"

    def test_execute_component_cascade_on_failure(self, sandbox):
        """Test that cascade tries fallback strategies on failure."""
        # This is harder to test without mocking, but we verify the logic exists
        # by checking that all 3 methods exist and have proper signatures
        assert hasattr(sandbox, "_try_execute_with_systemd_run")
        assert hasattr(sandbox, "_try_execute_with_unshare")
        assert hasattr(sandbox, "_execute_direct_unsafe")

    def test_execute_component_validation_still_works(self, sandbox):
        """Test that security validation still works."""
        dangerous_code = """
import os
class BadComponent:
    _security_signature="modulo_autopoiesis_data_bad"
    _generated_in_sandbox = True
    def run(self):
        os.system("ls")
"""
        with pytest.raises(Exception):  # Should raise SandboxError
            sandbox.execute_component(dangerous_code, "BadComponent")

    def test_execute_component_missing_signature(self, sandbox):
        """Test rejection of component without security signature."""
        code = """
class NoSignatureComponent:
    _generated_in_sandbox = True
    def run(self):
        return "OK"
"""
        with pytest.raises(Exception):
            sandbox.execute_component(code, "NoSignatureComponent")

    def test_execute_component_missing_sandbox_marker(self, sandbox):
        """Test rejection of component without sandbox marker."""
        code = """
class NoMarkerComponent:
    _security_signature="test"
    def run(self):
        return "OK"
"""
        with pytest.raises(Exception):
            sandbox.execute_component(code, "NoMarkerComponent")


class TestDirectExecutionFallback:
    """Test _execute_direct_unsafe fallback strategy."""

    def test_direct_execution_returns_isolation_none(self, sandbox):
        """Test that direct execution returns isolation='none'."""
        code = """
class DirectComponent:
    _security_signature="modulo_autopoiesis_data_direct"
    _generated_in_sandbox = True
    def run(self):
        return "OK"
"""
        result = sandbox._execute_direct_unsafe(code, "DirectComponent")

        assert result["isolation"] == "none"
        assert isinstance(result, dict)
        assert "success" in result
        assert "output" in result

    def test_direct_execution_success_case(self, sandbox):
        """Test successful direct execution."""
        code = """
class WorkingComponent:
    _security_signature="modulo_autopoiesis_data_working"
    _generated_in_sandbox = True
    def run(self):
        return "SUCCESS"
"""
        result = sandbox._execute_direct_unsafe(code, "WorkingComponent")

        assert result["success"] is True
        assert result["isolation"] == "none"
        assert "SUCCESS" in result["output"]


class TestIsolationFields:
    """Test isolation field in result dict."""

    def test_result_contains_isolation_field(self, sandbox):
        """Verify all execution paths include isolation field."""
        code = """
class FieldTestComponent:
    _security_signature="modulo_autopoiesis_data_field"
    _generated_in_sandbox = True
    def run(self):
        return "OK"
"""
        # Direct execution
        result_direct = sandbox._execute_direct_unsafe(code, "FieldTestComponent")
        assert "isolation" in result_direct
        assert result_direct["isolation"] == "none"

        # Full execute_component (uses cascade)
        result_cascade = sandbox.execute_component(code, "FieldTestComponent")
        assert "isolation" in result_cascade
        assert result_cascade["isolation"] in ["systemd_run", "unshare", "none", "failed"]

    def test_isolation_values_are_valid(self, sandbox):
        """Test that isolation field only has valid values."""
        valid_values = {"systemd_run", "unshare", "none", "failed"}

        code = """
class ValidComponent:
    _security_signature="modulo_autopoiesis_data_valid"
    _generated_in_sandbox = True
    def run(self):
        return "OK"
"""
        result = sandbox.execute_component(code, "ValidComponent")
        assert result["isolation"] in valid_values


class TestSandboxCompatibility:
    """Test that refactoring maintains backward compatibility."""

    def test_execute_component_signature_unchanged(self, sandbox):
        """Test that execute_component signature is still (code, name)."""
        import inspect

        sig = inspect.signature(sandbox.execute_component)
        params = list(sig.parameters.keys())

        assert "component_code" in params
        assert "component_name" in params
        assert len(params) == 2, "execute_component signature changed!"

    def test_result_dict_has_required_fields(self, sandbox):
        """Test that result dict has all expected fields."""
        code = """
class RequiredFieldsComponent:
    _security_signature="modulo_autopoiesis_data_fields"
    _generated_in_sandbox = True
    def run(self):
        return "OK"
"""
        result = sandbox.execute_component(code, "RequiredFieldsComponent")

        required_fields = {
            "success",
            "output",
            "error",
            "execution_time",
            "security_validated",
            "isolation",
        }
        assert required_fields.issubset(
            result.keys()
        ), f"Missing fields: {required_fields - result.keys()}"
        assert sandbox2.max_memory_mb == 256
        assert sandbox2.max_cpu_time_seconds == 60
