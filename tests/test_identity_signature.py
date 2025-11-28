import json
import tempfile
from pathlib import Path
import pytest
from src.identity.agent_signature import (

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
Testes para Identity - Agent Signature and Digital Identity.

Group 14: Integration Layer - identity/
"""



    AgentIdentity,
    ReputationScore,
    WorkSignature,
)


class TestWorkSignature:
    """Testa WorkSignature dataclass."""

    def test_initialization(self) -> None:
        """Testa inicialização de WorkSignature."""
        sig = WorkSignature(
            agent_id="test-agent",
            artifact_hash="abc123",
            timestamp="2025-01-01T00:00:00Z",
            autonomy_level=0.8,
        )

        assert sig.agent_id == "test-agent"
        assert sig.artifact_hash == "abc123"
        assert sig.timestamp == "2025-01-01T00:00:00Z"
        assert sig.autonomy_level == pytest.approx(0.8)
        assert sig.human_oversight is None
        assert sig.reputation_at_signing == pytest.approx(0.0)
        assert sig.metadata == {}

    def test_to_dict(self) -> None:
        """Testa conversão para dicionário."""
        sig = WorkSignature(
            agent_id="test-agent",
            artifact_hash="abc123",
            timestamp="2025-01-01T00:00:00Z",
            autonomy_level=0.8,
            human_oversight="John Doe",
            reputation_at_signing=0.75,
            metadata={"key": "value"},
        )

        sig_dict = sig.to_dict()

        assert isinstance(sig_dict, dict)
        assert sig_dict["agent_id"] == "test-agent"
        assert sig_dict["artifact_hash"] == "abc123"
        assert sig_dict["autonomy_level"] == pytest.approx(0.8)
        assert sig_dict["human_oversight"] == "John Doe"
        assert sig_dict["reputation_at_signing"] == pytest.approx(0.75)
        assert sig_dict["metadata"]["key"] == "value"


class TestReputationScore:
    """Testa ReputationScore tracking."""

    def test_initialization(self) -> None:
        """Testa inicialização com valores padrão."""
        rep = ReputationScore()

        assert rep.overall_score == pytest.approx(0.0)
        assert rep.code_quality == pytest.approx(0.0)
        assert rep.task_completion == pytest.approx(0.0)
        assert rep.autonomy == pytest.approx(0.0)
        assert rep.reliability == pytest.approx(0.0)
        assert rep.community_feedback == pytest.approx(0.0)
        assert rep.total_tasks == 0
        assert rep.successful_tasks == 0
        assert rep.failed_tasks == 0

    def test_update_from_successful_task(self) -> None:
        """Testa atualização com tarefa bem-sucedida."""
        rep = ReputationScore()

        rep.update_from_task(success=True, quality_score=0.9, autonomy_level=0.8)

        assert rep.total_tasks == 1
        assert rep.successful_tasks == 1
        assert rep.failed_tasks == 0
        assert rep.task_completion == pytest.approx(1.0)  # 100% success rate
        assert rep.code_quality > 0.0
        assert rep.autonomy > 0.0
        assert rep.reliability > 0.0
        assert rep.overall_score > 0.0

    def test_update_from_failed_task(self) -> None:
        """Testa atualização com tarefa falhada."""
        rep = ReputationScore()

        rep.update_from_task(success=False, quality_score=0.3, autonomy_level=0.5)

        assert rep.total_tasks == 1
        assert rep.successful_tasks == 0
        assert rep.failed_tasks == 1
        assert rep.task_completion == pytest.approx(0.0)
        assert rep.overall_score >= 0.0

    def test_update_multiple_tasks(self) -> None:
        """Testa múltiplas atualizações."""
        rep = ReputationScore()

        # 3 tarefas bem-sucedidas
        for _ in range(3):
            rep.update_from_task(success=True, quality_score=0.9, autonomy_level=0.8)

        # 1 tarefa falhada
        rep.update_from_task(success=False, quality_score=0.4, autonomy_level=0.6)

        assert rep.total_tasks == 4
        assert rep.successful_tasks == 3
        assert rep.failed_tasks == 1
        assert rep.task_completion == pytest.approx(0.75)  # 75% success rate

    def test_exponential_moving_average(self) -> None:
        """Testa que scores usam média móvel exponencial."""
        rep = ReputationScore()

        # Primeira tarefa com qualidade alta
        rep.update_from_task(success=True, quality_score=1.0, autonomy_level=1.0)
        first_quality = rep.code_quality
        first_autonomy = rep.autonomy

        # Segunda tarefa com qualidade baixa
        rep.update_from_task(success=True, quality_score=0.0, autonomy_level=0.0)

        # Scores devem estar entre os valores (não simplesmente média)
        # alpha = 0.1, então novo_score = 0.9 * old + 0.1 * new
        assert 0.0 < rep.code_quality < first_quality
        assert 0.0 < rep.autonomy < first_autonomy

    def test_overall_score_calculation(self) -> None:
        """Testa cálculo do overall score."""
        rep = ReputationScore()
        rep.code_quality = 0.8
        rep.task_completion = 0.9
        rep.autonomy = 0.7
        rep.reliability = 0.85

        # overall = 0.3*code + 0.3*completion + 0.2*autonomy + 0.2*reliability
        # expected = 0.8 * 0.3 + 0.9 * 0.3 + 0.7 * 0.2 + 0.85 * 0.2

        # Calcular através de update
        rep.update_from_task(success=True, quality_score=0.8, autonomy_level=0.7)

        # Overall score deve ser aproximadamente o esperado
        assert 0.0 <= rep.overall_score <= 1.0

    def test_to_dict(self) -> None:
        """Testa conversão para dicionário."""
        rep = ReputationScore()
        rep.update_from_task(success=True, quality_score=0.9, autonomy_level=0.8)

        rep_dict = rep.to_dict()

        assert isinstance(rep_dict, dict)
        assert "overall_score" in rep_dict
        assert "code_quality" in rep_dict
        assert "total_tasks" in rep_dict
        assert rep_dict["total_tasks"] == 1


class TestAgentIdentity:
    """Testa AgentIdentity para gerenciamento de identidade digital."""

    @pytest.fixture
    def temp_state_file(self) -> Path:
        """Cria arquivo temporário para estado."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir / "identity_state.json"
        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_initialization_default(self, temp_state_file: Path) -> None:
        """Testa inicialização com valores padrão."""
        identity = AgentIdentity(state_file=temp_state_file)

        assert identity.agent_id is not None
        assert "DevBrain-v1.0-" in identity.agent_id
        assert identity.legal_name == "DevBrain Autonomous Systems"
        assert "Brasil" in identity.jurisdiction
        assert identity.reputation is not None
        assert len(identity.signatures) == 0

    def test_initialization_custom(self, temp_state_file: Path) -> None:
        """Testa inicialização com valores customizados."""
        identity = AgentIdentity(
            agent_id="custom-agent-123",
            legal_name="Custom Agent Inc.",
            jurisdiction="US-CA",
            state_file=temp_state_file,
        )

        assert identity.agent_id == "custom-agent-123"
        assert identity.legal_name == "Custom Agent Inc."
        assert identity.jurisdiction == "US-CA"

    def test_generate_agent_id(self, temp_state_file: Path) -> None:
        """Testa geração de ID único."""
        identity1 = AgentIdentity(state_file=temp_state_file)

        temp_state_file2 = temp_state_file.parent / "identity_state2.json"
        identity2 = AgentIdentity(state_file=temp_state_file2)

        # IDs devem ser diferentes
        assert identity1.agent_id != identity2.agent_id
        assert identity1.agent_id.startswith("DevBrain-v1.0-")
        assert len(identity1.agent_id) > len("DevBrain-v1.0-")

    def test_sign_work(self, temp_state_file: Path) -> None:
        """Testa assinatura de trabalho."""
        identity = AgentIdentity(state_file=temp_state_file)
        artifact = "print('Hello, World!')"

        signature = identity.sign_work(
            artifact=artifact,
            metadata={"language": "python"},
            autonomy_level=0.9,
            human_supervisor="John Doe",
        )

        assert isinstance(signature, WorkSignature)
        assert signature.agent_id == identity.agent_id
        assert len(signature.artifact_hash) == 64  # SHA-256 hex
        assert signature.autonomy_level == pytest.approx(0.9)
        assert signature.human_oversight == "John Doe"
        assert signature.metadata["language"] == "python"
        assert len(identity.signatures) == 1

    def test_sign_work_hash_consistency(self, temp_state_file: Path) -> None:
        """Testa que o hash é consistente para mesmo artefato."""
        identity = AgentIdentity(state_file=temp_state_file)
        artifact = "test artifact"

        sig1 = identity.sign_work(artifact=artifact)
        sig2 = identity.sign_work(artifact=artifact)

        # Mesmo artefato deve gerar mesmo hash
        assert sig1.artifact_hash == sig2.artifact_hash

        # Mas timestamps devem ser diferentes
        assert sig1.timestamp != sig2.timestamp

    def test_verify_signature_valid(self, temp_state_file: Path) -> None:
        """Testa verificação de assinatura válida."""
        identity = AgentIdentity(state_file=temp_state_file)
        artifact = "test code"

        signature = identity.sign_work(artifact=artifact)
        is_valid = identity.verify_signature(artifact, signature)

        assert is_valid is True

    def test_verify_signature_invalid(self, temp_state_file: Path) -> None:
        """Testa verificação de assinatura inválida."""
        identity = AgentIdentity(state_file=temp_state_file)
        artifact = "original code"

        signature = identity.sign_work(artifact=artifact)

        # Tentar verificar com artefato diferente
        tampered_artifact = "modified code"
        is_valid = identity.verify_signature(tampered_artifact, signature)

        assert is_valid is False

    def test_update_reputation(self, temp_state_file: Path) -> None:
        """Testa atualização de reputação."""
        identity = AgentIdentity(state_file=temp_state_file)

        initial_score = identity.reputation.overall_score

        new_score = identity.update_reputation(success=True, quality_score=0.9, autonomy_level=0.8)

        assert new_score > initial_score
        assert identity.reputation.total_tasks == 1
        assert identity.reputation.successful_tasks == 1

    def test_get_identity_info(self, temp_state_file: Path) -> None:
        """Testa obtenção de informações completas."""
        identity = AgentIdentity(state_file=temp_state_file)
        identity.sign_work("test")

        info = identity.get_identity_info()

        assert isinstance(info, dict)
        assert info["agent_id"] == identity.agent_id
        assert info["legal_name"] == identity.legal_name
        assert info["jurisdiction"] == identity.jurisdiction
        assert "reputation" in info
        assert info["total_signatures"] == 1
        assert "capabilities" in info
        assert "accountability" in info

    def test_state_persistence(self, temp_state_file: Path) -> None:
        """Testa persistência de estado."""
        # Criar identidade e fazer algumas operações
        identity1 = AgentIdentity(agent_id="test-agent", state_file=temp_state_file)
        identity1.sign_work("artifact1")
        identity1.update_reputation(success=True, quality_score=0.9, autonomy_level=0.8)

        # Criar nova instância com mesmo state_file
        identity2 = AgentIdentity(agent_id="test-agent", state_file=temp_state_file)

        # Estado deve ser restaurado
        assert identity2.reputation.total_tasks == identity1.reputation.total_tasks
        assert identity2.reputation.overall_score == identity1.reputation.overall_score

    def test_signature_audit_log(self, temp_state_file: Path) -> None:
        """Testa log de auditoria de assinaturas."""
        identity = AgentIdentity(state_file=temp_state_file)

        # Assinar alguns artefatos
        identity.sign_work("artifact1")
        identity.sign_work("artifact2")

        # Verificar que arquivo de auditoria existe
        audit_file = temp_state_file.parent / "signature_audit.jsonl"
        assert audit_file.exists()

        # Verificar conteúdo
        with audit_file.open("r") as f:
            lines = f.readlines()

        assert len(lines) == 2

        # Cada linha deve ser JSON válido
        for line in lines:
            sig_data = json.loads(line)
            assert "agent_id" in sig_data
            assert "artifact_hash" in sig_data
            assert "timestamp" in sig_data

    def test_multiple_signatures_tracking(self, temp_state_file: Path) -> None:
        """Testa rastreamento de múltiplas assinaturas."""
        identity = AgentIdentity(state_file=temp_state_file)

        # Assinar 5 artefatos
        for i in range(5):
            identity.sign_work(f"artifact_{i}")

        assert len(identity.signatures) == 5

        # Todas as assinaturas devem ter hashes únicos
        hashes = [sig.artifact_hash for sig in identity.signatures]
        assert len(set(hashes)) == 5
