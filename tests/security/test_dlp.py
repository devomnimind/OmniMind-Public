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
Testes para DLP Validator (dlp.py).

Cobertura de:
- Políticas DLP
- Validação de dados
- Enforcement de políticas
- Violation handling
- Carregamento de políticas customizadas
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.security.dlp import (
    DLPPolicy,
    DLPValidator,
    DLPViolation,
    DLPViolationError,
)


class TestDLPPolicy:
    """Testes para DLPPolicy dataclass."""

    def test_dlp_policy_initialization(self) -> None:
        """Testa inicialização de DLPPolicy."""
        policy = DLPPolicy(
            name="test_policy",
            pattern=r"password=\S+",
            action="block",
            severity="high",
            description="Test policy",
        )

        assert policy.name == "test_policy"
        assert policy.action == "block"
        assert policy.severity == "high"
        assert policy.compiled is not None

    def test_dlp_policy_pattern_compilation(self) -> None:
        """Testa compilação de padrão regex."""
        policy = DLPPolicy(
            name="email",
            pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            action="alert",
        )

        # Test pattern matches
        assert policy.compiled.search("test@example.com") is not None
        assert policy.compiled.search("no-email-here") is None

    def test_dlp_policy_case_insensitive(self) -> None:
        """Testa que padrões são case-insensitive."""
        policy = DLPPolicy(
            name="password",
            pattern=r"password=\S+",
            action="block",
        )

        # Should match both cases
        assert policy.compiled.search("password=secret") is not None
        assert policy.compiled.search("PASSWORD=SECRET") is not None


class TestDLPViolation:
    """Testes para DLPViolation dataclass."""

    def test_dlp_violation_initialization(self) -> None:
        """Testa inicialização de DLPViolation."""
        violation = DLPViolation(
            rule="credentials",
            action="block",
            severity="high",
            snippet="password=secret123",
        )

        assert violation.rule == "credentials"
        assert violation.action == "block"
        assert violation.severity == "high"
        assert violation.snippet == "password=secret123"
        assert violation.timestamp != ""

    def test_dlp_violation_with_details(self) -> None:
        """Testa DLPViolation com detalhes."""
        violation = DLPViolation(
            rule="test",
            action="alert",
            severity="medium",
            snippet="test data",
            details={"source": "api", "user": "test_user"},
        )

        assert "source" in violation.details
        assert violation.details["user"] == "test_user"


class TestDLPViolationError:
    """Testes para DLPViolationError exception."""

    def test_dlp_violation_error(self) -> None:
        """Testa inicialização de DLPViolationError."""
        violation = DLPViolation(
            rule="test",
            action="block",
            severity="high",
            snippet="test",
        )

        error = DLPViolationError(violation)

        assert error.violation == violation
        assert "test" in str(error)
        assert "block" in str(error)


class TestDLPValidator:
    """Testes para DLPValidator."""

    @pytest.fixture
    def temp_policy_file(self) -> Path:
        """Cria arquivo de políticas temporário."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
policies:
  - name: test_credentials
    pattern: '(api_key|secret)=\\S+'
    action: block
    severity: high
    description: Test credentials policy
  - name: test_ip
    pattern: '192\\.168\\.\\d+\\.\\d+'
    action: alert
    severity: medium
    description: Test IP policy
"""
            )
            path = Path(f.name)

        yield path

        # Cleanup
        if path.exists():
            path.unlink()

    def test_initialization_with_defaults(self) -> None:
        """Testa inicialização com políticas padrão."""
        validator = DLPValidator()

        assert validator is not None
        assert len(validator.policies) > 0
        # Should have at least the default policies (from config file if exists)
        policy_names = [p.name for p in validator.policies]
        assert "credentials" in policy_names
        # Config file may have internal_network instead of internal_ip
        assert "internal_network" in policy_names or "internal_ip" in policy_names

    def test_initialization_with_custom_policy_file(self, temp_policy_file: Path) -> None:
        """Testa inicialização com arquivo de políticas customizado."""
        validator = DLPValidator(policy_path=str(temp_policy_file))

        # Should load policies from custom file
        policy_names = [p.name for p in validator.policies]
        assert "test_credentials" in policy_names
        assert "test_ip" in policy_names

    def test_initialization_missing_policy_file(self) -> None:
        """Testa inicialização com arquivo de políticas ausente."""
        validator = DLPValidator(policy_path="/nonexistent/path/policies.yaml")

        # Should fallback to defaults
        assert len(validator.policies) > 0
        policy_names = [p.name for p in validator.policies]
        assert "credentials" in policy_names

    def test_validate_no_violation(self) -> None:
        """Testa validação sem violação."""
        validator = DLPValidator()

        violation = validator.validate("This is clean text")

        assert violation is None

    def test_validate_empty_payload(self) -> None:
        """Testa validação com payload vazio."""
        validator = DLPValidator()

        violation = validator.validate("")

        assert violation is None

    def test_validate_credentials_violation(self) -> None:
        """Testa detecção de credenciais."""
        validator = DLPValidator()

        violation = validator.validate("api_key=12345secret")

        assert violation is not None
        assert violation.rule == "credentials"
        assert violation.severity == "high"
        assert "api_key" in violation.snippet

    def test_validate_password_violation(self) -> None:
        """Testa detecção de senha."""
        validator = DLPValidator()

        violation = validator.validate("password=mysecret123")

        assert violation is not None
        assert violation.rule == "credentials"
        assert "password" in violation.snippet

    def test_validate_token_violation(self) -> None:
        """Testa detecção de token."""
        validator = DLPValidator()

        violation = validator.validate("token=abcd1234efgh")

        assert violation is not None
        assert violation.rule == "credentials"

    def test_validate_internal_ip_violation(self) -> None:
        """Testa detecção de IP interno."""
        validator = DLPValidator()

        violation = validator.validate("Server IP: 192.168.1.100")

        assert violation is not None
        # Config file uses "internal_network", code default uses "internal_ip"
        assert violation.rule in ["internal_network", "internal_ip"]
        assert violation.severity == "medium"
        assert "192.168" in violation.snippet

    def test_validate_10_network_ip(self) -> None:
        """Testa detecção de IP da rede 10.x."""
        validator = DLPValidator()

        violation = validator.validate("Connect to 10.0.0.1")

        assert violation is not None
        assert violation.rule in ["internal_network", "internal_ip"]
        assert "10." in violation.snippet

    def test_validate_172_network_ip(self) -> None:
        """Testa detecção de IP da rede 172.16-31.x."""
        validator = DLPValidator()

        violation = validator.validate("Database at 172.16.5.10")

        assert violation is not None
        assert violation.rule in ["internal_network", "internal_ip"]
        assert "172." in violation.snippet

    @patch("src.security.dlp.log_action")
    def test_validate_logs_violation(self, mock_log_action: Mock) -> None:
        """Testa que violações são registradas."""
        validator = DLPValidator()

        violation = validator.validate("api_key=secret123")

        assert violation is not None
        mock_log_action.assert_called_once()
        call_args = mock_log_action.call_args
        assert call_args[0][0] == "dlp.violation"
        assert call_args[1]["category"] == "security"

    def test_enforce_no_violation(self) -> None:
        """Testa enforce sem violação."""
        validator = DLPValidator()

        # Should not raise
        result = validator.enforce("Clean text")

        assert result is None

    def test_enforce_alert_violation(self) -> None:
        """Testa enforce com violação de tipo alert."""
        validator = DLPValidator()

        # Should not raise, but return violation
        result = validator.enforce("Internal IP: 192.168.1.1")

        assert result is not None
        assert result.action == "alert"

    def test_enforce_block_violation_raises(self) -> None:
        """Testa que enforce com block levanta exceção."""
        validator = DLPValidator()

        with pytest.raises(DLPViolationError) as exc_info:
            validator.enforce("password=secret123")

        assert exc_info.value.violation.action == "block"
        assert exc_info.value.violation.rule == "credentials"

    def test_validate_multiple_violations_first_match(self) -> None:
        """Testa que apenas a primeira violação é retornada."""
        validator = DLPValidator()

        # Has both credential and IP violations
        violation = validator.validate("api_key=secret at 192.168.1.1")

        assert violation is not None
        # Should return first match (order depends on policy list)
        assert violation.rule in ["credentials", "internal_ip"]

    def test_validate_case_insensitive(self) -> None:
        """Testa que validação é case-insensitive."""
        validator = DLPValidator()

        violation1 = validator.validate("api_key=secret")
        violation2 = validator.validate("API_KEY=secret")

        assert violation1 is not None
        assert violation2 is not None

    def test_validate_with_details(self) -> None:
        """Testa que violação inclui detalhes."""
        validator = DLPValidator()

        violation = validator.validate("password=test123")

        assert violation is not None
        assert "description" in violation.details
        assert "payload_sample" in violation.details
        assert len(violation.details["payload_sample"]) <= 200

    def test_load_policies_invalid_yaml(self) -> None:
        """Testa carregamento de YAML inválido."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            path = Path(f.name)

        try:
            validator = DLPValidator(policy_path=str(path))

            # Should fallback to defaults
            assert len(validator.policies) > 0
            policy_names = [p.name for p in validator.policies]
            assert "credentials" in policy_names
        finally:
            if path.exists():
                path.unlink()

    def test_load_policies_not_list(self) -> None:
        """Testa carregamento quando policies não é uma lista."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
policies: not_a_list
"""
            )
            path = Path(f.name)

        try:
            validator = DLPValidator(policy_path=str(path))

            # Should fallback to defaults
            assert len(validator.policies) > 0
        finally:
            if path.exists():
                path.unlink()

    def test_default_policies_coverage(self) -> None:
        """Testa que políticas padrão cobrem casos comuns."""
        validator = DLPValidator()

        # Should detect common credential patterns (token needs at least 4 chars)
        test_cases = [
            ("api_key=abc123", True),
            ("secret=mysecret", True),
            ("password=test1234", True),
            ("token=xyz12345", True),  # Need at least 4 chars after =
            ("regular text", False),
        ]

        for text, should_violate in test_cases:
            violation = validator.validate(text)
            if should_violate:
                assert violation is not None, f"Should detect violation in: {text}"
            else:
                assert violation is None, f"Should not detect violation in: {text}"

    def test_default_policies_ip_coverage(self) -> None:
        """Testa que políticas padrão detectam IPs internos."""
        validator = DLPValidator()

        internal_ips = [
            "192.168.1.1",
            "10.0.0.1",
            "172.16.0.1",
            "172.20.5.10",
            "172.31.255.255",
        ]

        for ip in internal_ips:
            violation = validator.validate(f"Server: {ip}")
            assert violation is not None, f"Should detect internal IP: {ip}"
            assert violation.rule in ["internal_network", "internal_ip"]

    def test_snippet_extraction(self) -> None:
        """Testa que snippet é extraído corretamente."""
        validator = DLPValidator()

        violation = validator.validate("Some text with api_key=secret123 in it")

        assert violation is not None
        assert violation.snippet == "api_key=secret123"
