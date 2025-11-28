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
Testes para Compliance - GDPR Framework.

Group 13: System Services - compliance/
"""

from datetime import datetime

from src.compliance.gdpr_compliance import (
    ConsentStatus,
    DataCategory,
    DataProcessingPurpose,
    DataProcessingRecord,
    DataSubject,
    GDPRController,
    RetentionPeriod,
)


class TestEnums:
    """Testa enums de GDPR."""

    def test_data_processing_purpose_values(self) -> None:
        """Testa valores de DataProcessingPurpose."""
        assert DataProcessingPurpose.CONSENT.value == "consent"
        assert DataProcessingPurpose.CONTRACT.value == "contract"
        assert DataProcessingPurpose.LEGAL_OBLIGATION.value == "legal_obligation"

    def test_data_category_values(self) -> None:
        """Testa valores de DataCategory."""
        assert DataCategory.IDENTIFIERS.value == "identifiers"
        assert DataCategory.FINANCIAL.value == "financial"
        assert DataCategory.HEALTH.value == "health"

    def test_consent_status_values(self) -> None:
        """Testa valores de ConsentStatus."""
        assert ConsentStatus.PENDING.value == "pending"
        assert ConsentStatus.GRANTED.value == "granted"
        assert ConsentStatus.DENIED.value == "denied"
        assert ConsentStatus.WITHDRAWN.value == "withdrawn"


class TestDataSubject:
    """Testa DataSubject para representação de usuários."""

    def test_initialization(self) -> None:
        """Testa inicialização de DataSubject."""
        subject = DataSubject(subject_id="user123", email="test@example.com")

        assert subject.subject_id == "user123"
        assert subject.email == "test@example.com"
        assert isinstance(subject.created_at, datetime)
        assert isinstance(subject.last_activity, datetime)
        assert subject.consents == {}
        assert subject.data_processing_records == []
        assert subject.rights_requests == []

    def test_grant_consent(self) -> None:
        """Testa concessão de consentimento."""
        subject = DataSubject(subject_id="user123")

        consent_id = subject.grant_consent(
            purpose="analytics",
            data_categories=[DataCategory.BEHAVIORAL, DataCategory.TECHNICAL],
            retention_period=RetentionPeriod.SIX_MONTHS,
        )

        assert isinstance(consent_id, str)
        assert len(consent_id) > 0
        assert consent_id in subject.consents

        consent = subject.consents[consent_id]
        assert consent["purpose"] == "analytics"
        assert "behavioral" in consent["data_categories"]
        assert "technical" in consent["data_categories"]
        assert consent["status"] == ConsentStatus.GRANTED.value

    def test_withdraw_consent(self) -> None:
        """Testa retirada de consentimento."""
        subject = DataSubject(subject_id="user123")

        # Conceder consentimento
        consent_id = subject.grant_consent(
            purpose="marketing",
            data_categories=[DataCategory.IDENTIFIERS],
            retention_period=RetentionPeriod.ONE_YEAR,
        )

        # Retirar consentimento
        result = subject.withdraw_consent(consent_id)

        assert result is True
        assert subject.consents[consent_id]["status"] == ConsentStatus.WITHDRAWN.value
        assert "withdrawn_at" in subject.consents[consent_id]

    def test_withdraw_nonexistent_consent(self) -> None:
        """Testa retirada de consentimento inexistente."""
        subject = DataSubject(subject_id="user123")

        result = subject.withdraw_consent("nonexistent_id")

        assert result is False

    def test_has_consent_valid(self) -> None:
        """Testa verificação de consentimento válido."""
        subject = DataSubject(subject_id="user123")

        subject.grant_consent(
            purpose="analytics",
            data_categories=[DataCategory.BEHAVIORAL],
            retention_period=RetentionPeriod.ONE_YEAR,
        )

        has_consent = subject.has_consent("analytics", DataCategory.BEHAVIORAL)

        assert has_consent is True

    def test_has_consent_wrong_purpose(self) -> None:
        """Testa que consentimento não vale para propósito diferente."""
        subject = DataSubject(subject_id="user123")

        subject.grant_consent(
            purpose="analytics",
            data_categories=[DataCategory.BEHAVIORAL],
            retention_period=RetentionPeriod.ONE_YEAR,
        )

        has_consent = subject.has_consent("marketing", DataCategory.BEHAVIORAL)

        assert has_consent is False

    def test_has_consent_wrong_category(self) -> None:
        """Testa que consentimento não vale para categoria diferente."""
        subject = DataSubject(subject_id="user123")

        subject.grant_consent(
            purpose="analytics",
            data_categories=[DataCategory.BEHAVIORAL],
            retention_period=RetentionPeriod.ONE_YEAR,
        )

        has_consent = subject.has_consent("analytics", DataCategory.FINANCIAL)

        assert has_consent is False

    def test_has_consent_withdrawn(self) -> None:
        """Testa que consentimento retirado não é válido."""
        subject = DataSubject(subject_id="user123")

        consent_id = subject.grant_consent(
            purpose="analytics",
            data_categories=[DataCategory.BEHAVIORAL],
            retention_period=RetentionPeriod.ONE_YEAR,
        )

        subject.withdraw_consent(consent_id)

        has_consent = subject.has_consent("analytics", DataCategory.BEHAVIORAL)

        assert has_consent is False

    def test_consent_expiration(self) -> None:
        """Testa que consentimento com retention period tem data de expiração."""
        subject = DataSubject(subject_id="user123")

        consent_id = subject.grant_consent(
            purpose="session",
            data_categories=[DataCategory.TECHNICAL],
            retention_period=RetentionPeriod.SESSION_ONLY,
        )

        consent = subject.consents[consent_id]
        assert consent["expires_at"] is not None
        assert isinstance(consent["expires_at"], str)


class TestDataProcessingRecord:
    """Testa DataProcessingRecord para registro de atividades."""

    def test_initialization(self) -> None:
        """Testa inicialização de DataProcessingRecord."""
        record = DataProcessingRecord(
            subject_id="user123",
            purpose=DataProcessingPurpose.CONSENT,
            data_categories=[DataCategory.IDENTIFIERS, DataCategory.BEHAVIORAL],
            data_controller="OmniMind Inc.",
        )

        assert record.subject_id == "user123"
        assert record.purpose == DataProcessingPurpose.CONSENT
        assert DataCategory.IDENTIFIERS in record.data_categories
        assert record.data_controller == "OmniMind Inc."
        assert isinstance(record.record_id, str)
        assert len(record.record_id) > 0
        assert record.processed_data_hash is None

    def test_record_processing(self) -> None:
        """Testa registro de processamento de dados."""
        record = DataProcessingRecord(
            subject_id="user123",
            purpose=DataProcessingPurpose.CONSENT,
            data_categories=[DataCategory.TECHNICAL],
            data_controller="OmniMind Inc.",
        )

        data_hash = "abc123hash"
        record.record_processing(data_hash)

        assert record.processed_data_hash == data_hash

    def test_unique_record_ids(self) -> None:
        """Testa que record IDs são únicos."""
        record1 = DataProcessingRecord(
            subject_id="user123",
            purpose=DataProcessingPurpose.CONSENT,
            data_categories=[DataCategory.TECHNICAL],
            data_controller="OmniMind Inc.",
        )

        # Small delay to ensure different timestamp
        import time

        time.sleep(0.01)

        record2 = DataProcessingRecord(
            subject_id="user123",
            purpose=DataProcessingPurpose.CONSENT,
            data_categories=[DataCategory.TECHNICAL],
            data_controller="OmniMind Inc.",
        )

        assert record1.record_id != record2.record_id


class TestGDPRController:
    """Testa GDPRController para controle de compliance."""

    def test_initialization(self) -> None:
        """Testa inicialização de GDPRController."""
        controller = GDPRController()

        assert controller.data_subjects == {}
        assert controller.processing_records == []
        assert isinstance(controller.retention_schedule, dict)
        assert len(controller.retention_schedule) > 0

    def test_register_data_subject(self) -> None:
        """Testa registro de data subject."""
        controller = GDPRController()

        subject = controller.register_data_subject(subject_id="user123", email="test@example.com")

        assert isinstance(subject, DataSubject)
        assert subject.subject_id == "user123"
        assert subject.email == "test@example.com"
        assert "user123" in controller.data_subjects

    def test_register_duplicate_subject(self) -> None:
        """Testa que registrar subject duplicado retorna o existente."""
        controller = GDPRController()

        subject1 = controller.register_data_subject(subject_id="user123")
        subject2 = controller.register_data_subject(subject_id="user123")

        assert subject1 is subject2

    def test_process_data_with_consent(self) -> None:
        """Testa processamento de dados com consentimento."""
        controller = GDPRController()

        # Registrar e dar consentimento
        subject = controller.register_data_subject(subject_id="user123")
        subject.grant_consent(
            purpose="consent",  # Use the purpose value, not "analytics"
            data_categories=[DataCategory.BEHAVIORAL],
            retention_period=RetentionPeriod.ONE_YEAR,
        )

        # Processar dados
        result = controller.process_data(
            subject_id="user123",
            purpose=DataProcessingPurpose.CONSENT,
            data_categories=[DataCategory.BEHAVIORAL],
            data={"session_id": "abc123"},  # Use 'data' instead of 'data_hash'
        )

        assert result is True
        assert len(controller.processing_records) == 1

    def test_retention_schedule(self) -> None:
        """Testa schedule de retenção de dados."""
        controller = GDPRController()

        # Verificar que categorias têm períodos de retenção definidos
        assert DataCategory.IDENTIFIERS in controller.retention_schedule
        assert DataCategory.FINANCIAL in controller.retention_schedule

        # Períodos devem ser RetentionPeriod
        for category, period in controller.retention_schedule.items():
            assert isinstance(category, DataCategory)
            assert isinstance(period, RetentionPeriod)

    def test_get_subject_via_dict(self) -> None:
        """Testa obtenção de data subject via dicionário."""
        controller = GDPRController()

        controller.register_data_subject(subject_id="user123")
        subject = controller.data_subjects.get("user123")

        assert subject is not None
        assert subject.subject_id == "user123"

    def test_get_nonexistent_subject_via_dict(self) -> None:
        """Testa obtenção de subject inexistente via dicionário."""
        controller = GDPRController()

        subject = controller.data_subjects.get("nonexistent")

        assert subject is None

    def test_compliance_report(self) -> None:
        """Testa geração de relatório de compliance."""
        controller = GDPRController()

        # Adicionar alguns subjects
        controller.register_data_subject(subject_id="user1")
        controller.register_data_subject(subject_id="user2")

        report = controller.generate_compliance_report()

        assert isinstance(report, dict)
        assert "statistics" in report
        assert report["statistics"]["total_data_subjects"] == 2
        assert "total_processing_records" in report["statistics"]
