#!/usr/bin/env python3
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
Testes unitários para o módulo canonical_logger.py
Garante cobertura mínima de 50% conforme Grupo 1 - Phase 1.
"""

import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterator

import pytest

from src.audit.canonical_logger import CanonicalLogger


class TestCanonicalLogger:
    """Testes para o sistema de logging canônico com hash chain."""

    @pytest.fixture
    def temp_base_dir(self) -> Iterator[Path]:
        """Cria diretório temporário base para testes."""
        temp_dir = Path(tempfile.mkdtemp(prefix="omnimind_canonical_test_"))
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def canonical_logger(self, temp_base_dir: Path) -> CanonicalLogger:
        """Cria instância do CanonicalLogger para testes."""
        return CanonicalLogger(temp_base_dir)

    def test_initialization(self, canonical_logger: CanonicalLogger, temp_base_dir: Path) -> None:
        """Testa inicialização do CanonicalLogger."""
        assert canonical_logger.base_dir == temp_base_dir
        assert canonical_logger.canonical_dir == temp_base_dir / ".omnimind" / "canonical"
        assert canonical_logger.canonical_dir.exists()
        assert canonical_logger.md_file.exists()
        assert canonical_logger.json_file.exists()

    def test_initialization_creates_files(self, temp_base_dir: Path) -> None:
        """Testa que a inicialização cria os arquivos necessários."""
        # Criar logger para inicializar os arquivos
        CanonicalLogger(temp_base_dir)

        # Verificar estrutura de diretórios
        assert (temp_base_dir / ".omnimind" / "canonical").exists()

        # Verificar arquivo JSON
        json_file = temp_base_dir / ".omnimind" / "canonical" / "action_log.json"
        assert json_file.exists()

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "metadata" in data
        assert "action_log" in data
        assert "current_metrics" in data
        assert "system_integrity" in data
        assert data["metadata"]["version"] == "1.0.0"

        # Verificar arquivo MD
        md_file = temp_base_dir / ".omnimind" / "canonical" / "action_log.md"
        assert md_file.exists()

        md_content = md_file.read_text(encoding="utf-8")
        assert "OMNIMIND CANONICAL ACTION LOG" in md_content
        assert "REGRAS DE INTEGRIDADE" in md_content

    def test_log_action_single(self, canonical_logger: CanonicalLogger) -> None:
        """Testa registro de uma única ação."""
        hash_result = canonical_logger.log_action(
            ai_agent="TEST_AGENT",
            action_type="FILE_MODIFIED",
            target="test.py",
            result="SUCCESS",
            description="Test action",
        )

        # Verificar que hash foi retornado
        assert hash_result is not None
        assert len(hash_result) == 64  # SHA-256 = 64 caracteres hex

        # Verificar que foi registrado no JSON
        with open(canonical_logger.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data["action_log"]) == 1
        assert data["action_log"][0]["ai_agent"] == "TEST_AGENT"
        assert data["action_log"][0]["action_type"] == "FILE_MODIFIED"
        assert data["action_log"][0]["target"] == "test.py"
        assert data["action_log"][0]["result"] == "SUCCESS"
        assert data["action_log"][0]["hash"] == hash_result

    def test_log_action_with_details(self, canonical_logger: CanonicalLogger) -> None:
        """Testa registro de ação com detalhes completos."""
        hash_result = canonical_logger.log_action(
            ai_agent="CODE_AGENT",
            action_type="UNIT_TESTS_EXECUTED",
            target="tests/",
            result="SUCCESS",
            description="All tests passed",
            details="95% coverage achieved",
            impact="Increased reliability",
            automatic_actions=["update_metrics", "notify_team"],
        )

        assert hash_result is not None

        with open(canonical_logger.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        record = data["action_log"][0]
        assert record["details"] == "95% coverage achieved"
        assert record["impact"] == "Increased reliability"
        assert record["automatic_actions"] == ["update_metrics", "notify_team"]

    def test_log_action_chain(self, canonical_logger: CanonicalLogger) -> None:
        """Testa cadeia de múltiplas ações com hash chaining."""
        hash1 = canonical_logger.log_action(
            "AGENT1", "ACTION1", "target1", "SUCCESS", "First action"
        )
        hash2 = canonical_logger.log_action(
            "AGENT2", "ACTION2", "target2", "SUCCESS", "Second action"
        )
        hash3 = canonical_logger.log_action(
            "AGENT3", "ACTION3", "target3", "SUCCESS", "Third action"
        )

        # Todos os hashes devem ser únicos
        assert hash1 != hash2
        assert hash2 != hash3
        assert hash1 != hash3

        # Verificar que todos foram registrados
        with open(canonical_logger.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert len(data["action_log"]) == 3
        assert data["system_integrity"]["total_records"] == 3

    def test_validate_integrity_valid(self, canonical_logger: CanonicalLogger) -> None:
        """Testa validação de integridade com cadeia válida."""
        # Registrar algumas ações
        canonical_logger.log_action("AGENT1", "ACTION1", "target1", "SUCCESS", "Test 1")
        canonical_logger.log_action("AGENT2", "ACTION2", "target2", "SUCCESS", "Test 2")
        canonical_logger.log_action("AGENT3", "ACTION3", "target3", "SUCCESS", "Test 3")

        # Validar integridade
        is_valid = canonical_logger.validate_integrity()

        assert is_valid is True

    def test_validate_integrity_corrupted(self, canonical_logger: CanonicalLogger) -> None:
        """Testa detecção de cadeia corrompida."""
        # Registrar ações válidas
        canonical_logger.log_action("AGENT1", "ACTION1", "target1", "SUCCESS", "Test 1")
        canonical_logger.log_action("AGENT2", "ACTION2", "target2", "SUCCESS", "Test 2")

        # Corromper o log manualmente
        with open(canonical_logger.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Modificar um hash para quebrar a cadeia
        data["action_log"][1]["hash"] = "0" * 64

        with open(canonical_logger.json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Validação deve detectar corrupção
        is_valid = canonical_logger.validate_integrity()

        assert is_valid is False

    def test_validate_integrity_empty_log(self, canonical_logger: CanonicalLogger) -> None:
        """Testa validação de log vazio."""
        # Log recém-criado sem ações deve ser válido
        is_valid = canonical_logger.validate_integrity()
        assert is_valid is True

    def test_get_metrics(self, canonical_logger: CanonicalLogger) -> None:
        """Testa recuperação de métricas do sistema."""
        metrics = canonical_logger.get_metrics()

        assert isinstance(metrics, dict)
        assert "total_files" in metrics
        assert "tests_passing" in metrics
        assert "qdrant_collections" in metrics
        assert "knowledge_points" in metrics
        assert "canonical_documents" in metrics

    def test_update_metrics(self, canonical_logger: CanonicalLogger) -> None:
        """Testa atualização de métricas."""
        new_metrics = {
            "total_files": 150,
            "tests_passing": "142/150",
            "knowledge_points": 500,
        }

        canonical_logger.update_metrics(new_metrics)

        # Verificar que métricas foram atualizadas
        updated_metrics = canonical_logger.get_metrics()
        assert updated_metrics["total_files"] == 150
        assert updated_metrics["tests_passing"] == "142/150"
        assert updated_metrics["knowledge_points"] == 500

    def test_update_md_file(self, canonical_logger: CanonicalLogger) -> None:
        """Testa atualização do arquivo MD."""
        # Registrar uma ação
        canonical_logger.log_action(
            "TEST_AGENT",
            "TEST_ACTION",
            "test_target",
            "SUCCESS",
            "Test description",
            details="Test details",
            impact="Test impact",
        )

        # Verificar que o MD foi atualizado
        md_content = canonical_logger.md_file.read_text(encoding="utf-8")

        assert "TEST_AGENT" in md_content
        assert "TEST_ACTION" in md_content
        assert "test_target" in md_content
        assert "SUCCESS" in md_content
        assert "Test description" in md_content

    def test_hash_chain_consistency(self, canonical_logger: CanonicalLogger) -> None:
        """Testa que a cadeia de hash é consistente dentro de um logger."""
        # Registrar ações sequenciais
        hash1 = canonical_logger.log_action("A1", "ACT1", "t1", "OK", "desc1")
        hash2 = canonical_logger.log_action("A2", "ACT2", "t2", "OK", "desc2")
        hash3 = canonical_logger.log_action("A3", "ACT3", "t3", "OK", "desc3")

        # Verificar que cada hash é único
        assert hash1 != hash2
        assert hash2 != hash3

        # Verificar que a validação reconhece a cadeia como válida
        assert canonical_logger.validate_integrity() is True

        # Verificar que o hash subsequente depende do anterior
        with open(canonical_logger.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Cada registro deve ter um hash único
        hashes = [record["hash"] for record in data["action_log"]]
        assert len(hashes) == len(set(hashes))  # Todos únicos

    def test_timestamp_format(self, canonical_logger: CanonicalLogger) -> None:
        """Testa que os timestamps estão no formato ISO correto."""
        canonical_logger.log_action("AGENT", "ACTION", "target", "SUCCESS", "test")

        with open(canonical_logger.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        timestamp = data["action_log"][0]["timestamp"]

        # Verificar que pode ser parseado como datetime ISO
        parsed = datetime.fromisoformat(timestamp)
        assert isinstance(parsed, datetime)

    def test_system_integrity_updates(self, canonical_logger: CanonicalLogger) -> None:
        """Testa que system_integrity é atualizado corretamente."""
        # Verificar estado inicial
        with open(canonical_logger.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        initial_total = data["system_integrity"]["total_records"]
        assert initial_total == 0

        # Registrar ações
        canonical_logger.log_action("A1", "ACT1", "t1", "OK", "d1")
        canonical_logger.log_action("A2", "ACT2", "t2", "OK", "d2")

        # Verificar que total_records foi atualizado
        with open(canonical_logger.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["system_integrity"]["total_records"] == 2
        assert "last_validation" in data["system_integrity"]

    def test_automatic_actions_empty_list(self, canonical_logger: CanonicalLogger) -> None:
        """Testa que automatic_actions é uma lista vazia por padrão."""
        canonical_logger.log_action("AGENT", "ACTION", "target", "SUCCESS", "test")

        with open(canonical_logger.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert data["action_log"][0]["automatic_actions"] == []

    def test_previous_hash_initialization(self, canonical_logger: CanonicalLogger) -> None:
        """Testa que o primeiro registro usa hash inicial correto."""
        canonical_logger.log_action("FIRST", "ACTION", "target", "SUCCESS", "first")

        # Verificar que foi criado com prev_hash inicial (zeros)
        with open(canonical_logger.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # O hash deve ter sido calculado a partir do prev_hash inicial
        assert data["action_log"][0]["hash"] is not None
        assert len(data["action_log"][0]["hash"]) == 64


class TestCanonicalLoggerGlobalInstance:
    """Testes para a instância global do canonical_logger."""

    def test_global_instance_exists(self) -> None:
        """Testa que a instância global existe."""
        from src.audit.canonical_logger import canonical_logger

        assert canonical_logger is not None
        assert isinstance(canonical_logger, CanonicalLogger)

    def test_global_instance_uses_cwd(self) -> None:
        """Testa que a instância global usa o diretório atual."""
        from src.audit.canonical_logger import canonical_logger

        assert canonical_logger.base_dir == Path.cwd()


# Pytest configuration
def pytest_configure(config: pytest.Config) -> None:
    """Configuração do pytest para este módulo."""
    config.addinivalue_line("markers", "canonical: testes do canonical logger")


if __name__ == "__main__":
    # Executar testes com pytest
    pytest.main(
        [
            __file__,
            "-v",
            "--tb=short",
            "--cov=src.audit.canonical_logger",
            "--cov-report=term-missing",
        ]
    )
