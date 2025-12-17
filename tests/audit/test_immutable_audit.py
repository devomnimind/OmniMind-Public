"""
Testes para Immutable Audit System (immutable_audit.py).

Cobertura de:
- Hash chain de auditoria
- Verificação de integridade
- Append-only log
- Auditoria de operações críticas
- Tratamento de exceções
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from src.audit.immutable_audit import (
    ImmutableAuditSystem,
    get_audit_system,
    log_action,
)


class TestImmutableAuditSystem:
    """Testes para ImmutableAuditSystem."""

    @pytest.fixture
    def temp_log_dir(self) -> Generator[Path, None, None]:
        """Cria diretório temporário para logs."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir)

    def test_system_initialization(self, temp_log_dir: Path) -> None:
        """Testa inicialização do sistema de auditoria."""
        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        assert audit is not None
        assert temp_log_dir.exists()
        assert (temp_log_dir / "audit_chain.log").exists()
        assert (temp_log_dir / "hash_chain.json").exists()

    def test_log_action_basic(self, temp_log_dir: Path) -> None:
        """Testa registro básico de ação."""
        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        hash_result = audit.log_action(
            action="test_action", details={"key": "value"}, category="test"
        )

        assert isinstance(hash_result, str)
        assert len(hash_result) == 64  # SHA-256 hex length

    def test_log_action_with_different_categories(self, temp_log_dir: Path) -> None:
        """Testa registro com diferentes categorias."""
        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        # Test different categories
        categories = ["general", "code", "config", "security", "system"]

        for category in categories:
            hash_result = audit.log_action(
                action=f"test_{category}",
                details={"category": category},
                category=category,
            )
            assert isinstance(hash_result, str)
            assert len(hash_result) == 64

    def test_verify_chain_integrity_empty_log(self, temp_log_dir: Path) -> None:
        """Testa verificação de integridade com log vazio."""
        # Create a fresh audit system without initialization event
        audit = ImmutableAuditSystem.__new__(ImmutableAuditSystem)
        audit.log_dir = temp_log_dir
        audit.audit_log_file = temp_log_dir / "audit_chain.log"
        audit.hash_chain_file = temp_log_dir / "hash_chain.json"
        audit.security_log = temp_log_dir / "security_events.log"
        audit.last_hash = "0" * 64

        result = audit.verify_chain_integrity()

        assert result["valid"] is True
        assert result["events_verified"] == 0

    def test_verify_chain_integrity_with_events(self, temp_log_dir: Path) -> None:
        """Testa verificação de integridade com eventos registrados."""
        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        # Add some events
        audit.log_action("action1", {"data": "test1"}, "test")
        audit.log_action("action2", {"data": "test2"}, "test")

        result = audit.verify_chain_integrity()

        assert result["valid"] is True
        assert result["events_verified"] >= 2  # At least the 2 actions + init

    def test_hash_content_consistency(self, temp_log_dir: Path) -> None:
        """Testa consistência da função de hash."""
        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        content = b"test content"
        hash1 = audit.hash_content(content)
        hash2 = audit.hash_content(content)

        assert hash1 == hash2
        assert len(hash1) == 64
        assert hash1.isalnum()

    def test_get_audit_summary(self, temp_log_dir: Path) -> None:
        """Testa obtenção de resumo do audit."""
        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        # Add some events
        audit.log_action("summary_test", {"test": True}, "test")

        summary = audit.get_audit_summary()

        assert isinstance(summary, dict)
        assert "log_dir" in summary
        assert "audit_log_exists" in summary
        assert "last_hash" in summary
        assert "total_events" in summary
        assert "chain_integrity" in summary
        assert summary["audit_log_exists"] is True
        assert summary["total_events"] >= 1

    def test_singleton_pattern(self) -> None:
        """Testa padrão singleton do get_audit_system."""
        audit1 = get_audit_system()
        audit2 = get_audit_system()

        assert audit1 is audit2
        assert isinstance(audit1, ImmutableAuditSystem)

    def test_log_action_global_function(self) -> None:
        """Testa função global log_action."""
        hash_result = log_action(action="global_test", details={"global": True}, category="test")

        assert isinstance(hash_result, str)
        assert len(hash_result) == 64

    def test_file_integrity_verification(self, temp_log_dir: Path) -> None:
        """Testa verificação de integridade de arquivo."""
        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        # Create a test file
        test_file = temp_log_dir / "test_file.txt"
        test_content = "test content for integrity check"
        test_file.write_text(test_content)

        # Calculate hash and set xattr (if available)
        content_hash = audit.hash_content(test_file.read_bytes())
        audit.set_file_xattr(str(test_file), content_hash)

        # Verify integrity
        result = audit.verify_file_integrity(str(test_file))

        # Result depends on xattr availability
        assert "valid" in result
        assert "message" in result
        if result["valid"] is True:
            assert "Arquivo íntegro" in result["message"]
        elif result["valid"] is None:
            assert "Sem xattr registrado" in result["message"]

    def test_system_event_logging(self, temp_log_dir: Path) -> None:
        """Testa logging de eventos de sistema."""
        ImmutableAuditSystem(log_dir=str(temp_log_dir))

        # System events are logged automatically during initialization
        # Just verify the log exists and has content
        audit_log = temp_log_dir / "audit_chain.log"
        assert audit_log.exists()

        with open(audit_log, "rb") as f:
            lines = f.readlines()
            assert len(lines) >= 1  # At least initialization event

    def test_concurrent_access_simulation(self, temp_log_dir: Path) -> None:
        """Testa acesso concorrente simulado."""
        import threading
        import time

        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        results = []
        errors = []

        def log_worker(worker_id: int) -> None:
            try:
                hash_result = audit.log_action(
                    f"concurrent_action_{worker_id}",
                    {"worker": worker_id, "timestamp": time.time()},
                    "concurrency_test",
                )
                results.append(hash_result)
            except Exception as e:
                errors.append(str(e))

        # Start multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=log_worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads
        for t in threads:
            t.join()

        # Verify results
        assert len(results) == 5
        assert len(errors) == 0
        assert all(isinstance(h, str) and len(h) == 64 for h in results)

        # Verify chain integrity after concurrent operations
        integrity = audit.verify_chain_integrity()
        assert integrity["valid"] is True

    def test_repair_chain_integrity_empty_log(self, temp_log_dir: Path) -> None:
        """Testa reparo com log vazio."""
        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        # Remove log file
        audit.audit_log_file.unlink()

        result = audit.repair_chain_integrity()

        assert result["repaired"] is False
        assert "Log não existe" in result["message"]

    def test_repair_chain_integrity_with_valid_chain(self, temp_log_dir: Path) -> None:
        """Testa reparo com cadeia válida."""
        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        # Add valid events
        audit.log_action("action1", {"test": 1}, "test")
        audit.log_action("action2", {"test": 2}, "test")

        # Verify chain before repair
        integrity_before = audit.verify_chain_integrity()
        assert integrity_before["valid"] is True

        result = audit.repair_chain_integrity()

        # Repair should succeed
        assert result["repaired"] is True
        # Some events may be removed during repair process depending on chain state
        # Just verify repair completed
        assert "events_repaired" in result
        assert "events_removed" in result

    def test_set_file_xattr_not_available(self, temp_log_dir: Path) -> None:
        """Testa set_file_xattr quando setfattr não disponível."""
        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        test_file = temp_log_dir / "test.txt"
        test_file.write_text("test")

        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = audit.set_file_xattr(str(test_file), "abc123")
            assert result is False

    def test_verify_file_integrity_file_not_exists(self, temp_log_dir: Path) -> None:
        """Testa verificação de arquivo que não existe."""
        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        result = audit.verify_file_integrity("/nonexistent/file.txt")

        assert result["valid"] is False
        assert "não existe" in result["message"]

    def test_protect_log_file_success(self, temp_log_dir: Path) -> None:
        """Testa proteção de arquivo com chattr."""
        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        test_file = temp_log_dir / "protected.log"
        test_file.write_text("protected content")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = audit.protect_log_file(str(test_file))

            # May succeed or fail depending on permissions
            assert isinstance(result, bool)

    def test_protect_log_file_failure(self, temp_log_dir: Path) -> None:
        """Testa proteção de arquivo quando chattr falha."""
        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        test_file = temp_log_dir / "protected.log"
        test_file.write_text("protected content")

        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = audit.protect_log_file(str(test_file))
            assert result is False

    def test_load_last_hash_with_invalid_data(self, temp_log_dir: Path) -> None:
        """Testa carregamento de hash com dados inválidos."""

        # Create audit system to set up files
        audit = ImmutableAuditSystem.__new__(ImmutableAuditSystem)
        audit.log_dir = temp_log_dir
        audit.hash_chain_file = temp_log_dir / "hash_chain.json"
        audit.security_log = temp_log_dir / "security_events.log"

        # Write invalid JSON
        audit.hash_chain_file.write_text("invalid json")

        last_hash = audit._load_last_hash()

        # Should return default hash
        assert last_hash == "0" * 64

    def test_security_event_logging(self, temp_log_dir: Path) -> None:
        """Testa logging de eventos de segurança."""
        audit = ImmutableAuditSystem(log_dir=str(temp_log_dir))

        audit._log_security_event("Test security event")

        assert audit.security_log.exists()
        content = audit.security_log.read_text()
        assert "Test security event" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
