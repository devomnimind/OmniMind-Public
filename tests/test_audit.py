"""
Testes unitários para o sistema de auditoria imutável.
Garante cobertura mínima de 90% conforme regras do projeto.
"""

import json
import shutil
import tempfile
from pathlib import Path
from typing import Iterator

import pytest

from src.audit.immutable_audit import ImmutableAuditSystem


class TestImmutableAuditSystem:
    """Testes para o sistema de auditoria com chain hashing."""

    @pytest.fixture
    def temp_audit_dir(self) -> Iterator[str]:
        """Cria diretório temporário para testes."""
        temp_dir = tempfile.mkdtemp(prefix="omnimind_test_")
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def audit_system(self, temp_audit_dir: str) -> ImmutableAuditSystem:
        """Cria instância do sistema de auditoria para testes."""
        return ImmutableAuditSystem(log_dir=temp_audit_dir)

    def test_initialization(
        self, audit_system: ImmutableAuditSystem, temp_audit_dir: str
    ) -> None:
        """Testa inicialização do sistema."""
        assert audit_system.log_dir == Path(temp_audit_dir)
        assert audit_system.last_hash == "0" * 64 or len(audit_system.last_hash) == 64
        assert audit_system.audit_log_file.parent.exists()

    def test_hash_content(self, audit_system: ImmutableAuditSystem) -> None:
        """Testa geração de hash SHA-256."""
        content = b"test content"
        hash1 = audit_system.hash_content(content)
        hash2 = audit_system.hash_content(content)

        # Hash deve ser determinístico
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 = 64 caracteres hex

        # Hash diferente para conteúdo diferente
        hash3 = audit_system.hash_content(b"different content")
        assert hash1 != hash3

    def test_log_action_single(self, audit_system: ImmutableAuditSystem) -> None:
        """Testa registro de ação única."""
        action = "test_action"
        details = {"key": "value", "number": 42}

        hash_result = audit_system.log_action(action, details, "test")

        assert hash_result is not None
        assert len(hash_result) == 64
        assert audit_system.audit_log_file.exists()

    def test_log_action_chain(self, audit_system: ImmutableAuditSystem) -> None:
        """Testa cadeia de múltiplas ações."""
        hash1 = audit_system.log_action("action1", {"data": "first"})
        hash2 = audit_system.log_action("action2", {"data": "second"})
        hash3 = audit_system.log_action("action3", {"data": "third"})

        # Todos os hashes devem ser únicos
        assert hash1 != hash2
        assert hash2 != hash3
        assert hash1 != hash3

        # Verificar que eventos foram registrados
        with open(audit_system.audit_log_file, "r") as f:
            lines = f.readlines()
            # Pelo menos 4 eventos (init + 3 testes)
            assert len(lines) >= 4

    def test_verify_chain_integrity_valid(
        self, audit_system: ImmutableAuditSystem
    ) -> None:
        """Testa verificação de cadeia íntegra."""
        # Registrar algumas ações
        audit_system.log_action("action1", {"test": 1})
        audit_system.log_action("action2", {"test": 2})

        # Verificar integridade
        result = audit_system.verify_chain_integrity()

        assert result["valid"] is True
        assert result["events_verified"] >= 3  # init + 2 ações
        assert "corrupted_events" not in result or len(result["corrupted_events"]) == 0

    def test_verify_chain_integrity_corrupted(
        self, audit_system: ImmutableAuditSystem
    ) -> None:
        """Testa detecção de cadeia corrompida."""
        # Registrar ações
        audit_system.log_action("action1", {"test": 1})
        audit_system.log_action("action2", {"test": 2})

        # Corromper o log manualmente
        with open(audit_system.audit_log_file, "a") as f:
            corrupted_event = {
                "action": "corrupted",
                "category": "test",
                "details": {},
                "timestamp": 0,
                "datetime_utc": "2025-01-01T00:00:00",
                "prev_hash": "invalid_hash",
                "current_hash": "fake_hash",
            }
            f.write(json.dumps(corrupted_event) + "\n")

        # Verificar deve detectar corrupção
        result = audit_system.verify_chain_integrity()

        assert result["valid"] is False
        assert "corrupted_events" in result
        assert len(result["corrupted_events"]) > 0

    def test_file_xattr_operations(
        self, audit_system: ImmutableAuditSystem, temp_audit_dir: str
    ) -> None:
        """Testa operações de extended attributes."""
        # Criar arquivo de teste
        test_file = Path(temp_audit_dir) / "test_file.txt"
        test_content = b"test content for xattr"
        test_file.write_bytes(test_content)

        # Calcular hash
        content_hash = audit_system.hash_content(test_content)

        # Tentar setar xattr (pode falhar se não tiver attr-utils)
        xattr_set = audit_system.set_file_xattr(str(test_file), content_hash)

        if xattr_set:
            # Se xattr foi setado, verificar
            verification = audit_system.verify_file_integrity(str(test_file))
            assert verification["valid"] is True
            assert verification["hash"] == content_hash
        else:
            # Se xattr não disponível, apenas verificar que não quebrou
            verification = audit_system.verify_file_integrity(str(test_file))
            # Can be None or False when xattr is not registered
            assert verification["valid"] in [None, False]

    def test_file_integrity_modified(
        self, audit_system: ImmutableAuditSystem, temp_audit_dir: str
    ) -> None:
        """Testa detecção de arquivo modificado."""
        test_file = Path(temp_audit_dir) / "test_modified.txt"
        original_content = b"original content"
        test_file.write_bytes(original_content)

        # Setar hash original
        original_hash = audit_system.hash_content(original_content)
        xattr_set = audit_system.set_file_xattr(str(test_file), original_hash)

        if xattr_set:
            # Modificar arquivo
            test_file.write_bytes(b"modified content")

            # Verificar deve detectar modificação
            verification = audit_system.verify_file_integrity(str(test_file))
            assert verification["valid"] is False
            assert verification["expected_hash"] == original_hash
            assert verification["current_hash"] != original_hash

    def test_get_audit_summary(self, audit_system: ImmutableAuditSystem) -> None:
        """Testa geração de resumo de auditoria."""
        # Registrar algumas ações
        audit_system.log_action("test1", {"data": 1})
        audit_system.log_action("test2", {"data": 2})

        summary = audit_system.get_audit_summary()

        assert "log_dir" in summary
        assert summary["audit_log_exists"] is True
        assert summary["total_events"] >= 3
        assert summary["log_size_bytes"] > 0
        assert "chain_integrity" in summary
        assert summary["chain_integrity"]["valid"] is True

    def test_thread_safety(self, audit_system: ImmutableAuditSystem) -> None:
        """Testa segurança em multi-threading."""
        import threading

        results = []

        def log_multiple() -> None:
            for i in range(10):
                hash_val = audit_system.log_action(f"thread_action_{i}", {"i": i})
                results.append(hash_val)

        # Criar múltiplas threads
        threads = [threading.Thread(target=log_multiple) for _ in range(5)]

        # Iniciar todas
        for t in threads:
            t.start()

        # Aguardar conclusão
        for t in threads:
            t.join()

        # Verificar que todos os hashes foram registrados
        assert len(results) == 50
        assert len(set(results)) == 50  # Todos únicos

        # Verificar integridade
        integrity = audit_system.verify_chain_integrity()
        assert integrity["valid"] is True

    def test_security_log(self, audit_system: ImmutableAuditSystem) -> None:
        """Testa registro de eventos de segurança."""
        audit_system._log_security_event("Test security event")

        assert audit_system.security_log.exists()

        content = audit_system.security_log.read_text()
        assert "Test security event" in content

    def test_categories(self, audit_system: ImmutableAuditSystem) -> None:
        """Testa registro com diferentes categorias."""
        categories = ["general", "code", "config", "security", "system"]

        for category in categories:
            hash_val = audit_system.log_action(
                f"test_{category}", {"category": category}, category=category
            )
            assert hash_val is not None

        # Verificar que todas foram registradas
        with open(audit_system.audit_log_file, "r") as f:
            content = f.read()
            for category in categories:
                assert f'"category": "{category}"' in content


class TestModuleInterface:
    """Testa interface pública do módulo."""

    def test_imports(self) -> None:
        """Testa que todas as exportações estão disponíveis."""
        from audit import ImmutableAuditSystem, get_audit_system, log_action

        assert ImmutableAuditSystem is not None
        assert get_audit_system is not None
        assert log_action is not None

    def test_singleton_pattern(self) -> None:
        """Testa que get_audit_system retorna singleton."""
        from audit import get_audit_system

        instance1 = get_audit_system()
        instance2 = get_audit_system()

        assert instance1 is instance2


# Pytest configuration
def pytest_configure(config: pytest.Config) -> None:
    """Configuração do pytest."""
    config.addinivalue_line("markers", "slow: marca testes lentos")


if __name__ == "__main__":
    # Executar testes com pytest
    pytest.main(
        [__file__, "-v", "--tb=short", "--cov=audit", "--cov-report=term-missing"]
    )
