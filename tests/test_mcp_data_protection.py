import pytest
from src.integrations.mcp_data_protection import (

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
Testes para o sistema de proteção de dados MCP.
"""


    MCPDataProtection,
    SensitivePattern,
    get_data_protection,
    protect_for_mcp,
)


class TestSensitivePattern:
    """Testes para SensitivePattern."""

    def test_pattern_creation(self) -> None:
        """Testa criação de padrão."""
        pattern = SensitivePattern(
            name="test",
            pattern=r"test_\d+",
            severity="high",
            action="hash",
            description="Test pattern",
        )

        assert pattern.name == "test"
        assert pattern.compiled is not None
        assert pattern.compiled.match("test_123") is not None


class TestMCPDataProtection:
    """Testes para MCPDataProtection."""

    def test_initialization(self) -> None:
        """Testa inicialização."""
        protection = MCPDataProtection()

        assert len(protection.patterns) > 0
        assert protection.cipher is not None
        assert protection.dlp_validator is not None

    def test_hash_data(self) -> None:
        """Testa hash de dados."""
        protection = MCPDataProtection()

        hashed = protection._hash_data("sensitive_data_123")

        assert "[HASHED:" in hashed
        assert "sensitive_data_123" not in hashed

    def test_mask_data(self) -> None:
        """Testa máscara de dados."""
        protection = MCPDataProtection()

        masked = protection._mask_data("test@example.com")

        assert masked.startswith("tes")
        assert masked.endswith("com")
        assert "*" in masked

    def test_detect_api_key(self) -> None:
        """Testa detecção de API key."""
        protection = MCPDataProtection()

        content = "api_key=sk_test_1234567890abcdefghijklmnop"
        detections = protection.detect_sensitive_data(content)

        assert len(detections) > 0
        assert any(d["pattern"] == "api_key" for d in detections)

    def test_detect_password(self) -> None:
        """Testa detecção de password."""
        protection = MCPDataProtection()

        content = "password=MySecretPassword123"
        detections = protection.detect_sensitive_data(content)

        assert len(detections) > 0
        assert any(d["pattern"] == "password" for d in detections)

    def test_detect_email(self) -> None:
        """Testa detecção de email."""
        protection = MCPDataProtection()

        content = "Contact: user@example.com"
        detections = protection.detect_sensitive_data(content)

        assert len(detections) > 0
        assert any(d["pattern"] == "email" for d in detections)

    def test_detect_private_ip(self) -> None:
        """Testa detecção de IP privado."""
        protection = MCPDataProtection()

        content = "Server at 192.168.1.100"
        detections = protection.detect_sensitive_data(content)

        assert len(detections) > 0
        assert any(d["pattern"] == "ipv4_private" for d in detections)

    def test_protect_content_with_api_key(self) -> None:
        """Testa proteção de conteúdo com API key."""
        protection = MCPDataProtection()

        content = "Connect with api_key=sk_test_1234567890"
        protected, result = protection.protect_content(content)

        assert "sk_test_1234567890" not in protected
        assert "[HASHED:" in protected
        assert len(result.detections) > 0
        assert "Hashed api_key" in result.actions_taken

    def test_protect_content_with_password(self) -> None:
        """Testa proteção de conteúdo com password."""
        protection = MCPDataProtection()

        content = "Login with password=SuperSecret123"
        protected, result = protection.protect_content(content)

        assert "SuperSecret123" not in protected
        assert len(result.detections) > 0

    def test_sanitize_dict_removes_sensitive_fields(self) -> None:
        """Testa sanitização de dict removendo campos sensíveis."""
        protection = MCPDataProtection()

        data = {
            "username": "john",
            "password": "secret123",
            "email": "john@example.com",
            "api_key": "sk_test_123",
        }

        sanitized = protection.sanitize_dict(data)

        assert sanitized["username"] == "john"
        assert sanitized["password"] == "[PROTECTED]"
        assert sanitized["api_key"] == "[PROTECTED]"
        assert "@" not in sanitized["email"]  # Email should be masked

    def test_sanitize_dict_nested(self) -> None:
        """Testa sanitização de dict aninhado."""
        protection = MCPDataProtection()

        data = {
            "config": {
                "database": {
                    "host": "localhost",
                    "password": "db_secret",
                }
            }
        }

        sanitized = protection.sanitize_dict(data)

        assert sanitized["config"]["database"]["host"] == "localhost"
        assert sanitized["config"]["database"]["password"] == "[PROTECTED]"

    def test_sanitize_path_absolute_to_relative(self) -> None:
        """Testa sanitização de path absoluto."""
        protection = MCPDataProtection()

        absolute_path = "/home/user/projects/omnimind/src/test.py"
        sanitized = protection.sanitize_path(absolute_path)

        assert not sanitized.startswith("/home/user")
        assert "test.py" in sanitized

    def test_sanitize_for_mcp_string(self) -> None:
        """Testa sanitize_for_mcp com string."""
        protection = MCPDataProtection()

        data = "api_key=sk_test_12345 and password=secret"
        sanitized, result = protection.sanitize_for_mcp(data)

        assert "sk_test_12345" not in sanitized
        assert "secret" not in sanitized
        assert result.sanitized is True

    def test_sanitize_for_mcp_dict(self) -> None:
        """Testa sanitize_for_mcp com dict."""
        protection = MCPDataProtection()

        data = {"token": "abc123", "user": "john"}
        sanitized, result = protection.sanitize_for_mcp(data)

        assert sanitized["token"] == "[PROTECTED]"
        assert sanitized["user"] == "john"
        assert result.sanitized is True

    def test_sanitize_for_mcp_list(self) -> None:
        """Testa sanitize_for_mcp com lista."""
        protection = MCPDataProtection()

        data = ["item1", "password=secret", "item3"]
        sanitized, result = protection.sanitize_for_mcp(data)

        assert sanitized[0] == "item1"
        assert "secret" not in sanitized[1]
        assert sanitized[2] == "item3"

    def test_cache_enabled(self) -> None:
        """Testa que cache funciona."""
        protection = MCPDataProtection(enable_cache=True)

        data = "api_key=sk_test_123"

        # Primeira detecção
        detections1 = protection.detect_sensitive_data(data)

        # Segunda detecção (deve usar cache)
        detections2 = protection.detect_sensitive_data(data)

        assert detections1 == detections2
        assert len(protection._detection_cache) > 0

    def test_cache_disabled(self) -> None:
        """Testa que cache pode ser desabilitado."""
        protection = MCPDataProtection(enable_cache=False)

        data = "api_key=sk_test_123"
        protection.detect_sensitive_data(data)

        assert len(protection._detection_cache) == 0

    def test_statistics(self) -> None:
        """Testa obtenção de estatísticas."""
        protection = MCPDataProtection()

        content = "api_key=sk_test_123"
        protection.protect_content(content)

        stats = protection.get_statistics()

        assert stats["total_detections"] > 0
        assert stats["actions"]["hashed"] > 0

    def test_clear_cache(self) -> None:
        """Testa limpeza de cache."""
        protection = MCPDataProtection(enable_cache=True)

        data = "api_key=sk_test_123"
        protection.detect_sensitive_data(data)

        assert len(protection._detection_cache) > 0

        protection.clear_cache()

        assert len(protection._detection_cache) == 0

    def test_add_custom_pattern(self) -> None:
        """Testa adição de padrão customizado."""
        protection = MCPDataProtection()

        initial_count = len(protection.patterns)

        custom_pattern = SensitivePattern(
            name="custom",
            pattern=r"CUSTOM_\w+",
            severity="high",
            action="hash",
        )

        protection.add_pattern(custom_pattern)

        assert len(protection.patterns) == initial_count + 1

        # Testar detecção com padrão customizado
        content = "Secret: CUSTOM_SECRET_123"
        detections = protection.detect_sensitive_data(content)

        assert any(d["pattern"] == "custom" for d in detections)


class TestGlobalProtection:
    """Testes para funções globais."""

    def test_get_data_protection(self) -> None:
        """Testa obtenção de instância global."""
        protection1 = get_data_protection()
        protection2 = get_data_protection()

        # Deve retornar mesma instância
        assert protection1 is protection2

    def test_protect_for_mcp(self) -> None:
        """Testa função conveniente protect_for_mcp."""
        data = "password=secret123"
        protected, result = protect_for_mcp(data)

        assert "secret123" not in protected
        assert result.sanitized is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
