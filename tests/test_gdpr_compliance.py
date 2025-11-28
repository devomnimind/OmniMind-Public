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

"""Tests for GDPR compliance framework"""

from datetime import datetime, timedelta, timezone

from src.compliance.gdpr_compliance import (
    ConsentStatus,
    DataCategory,
    DataProcessingPurpose,
    GDPRController,
    RetentionPeriod,
)


class TestGDPRCompliance:
    """Test GDPR compliance functionality"""

    def test_register_data_subject(self) -> None:
        """Test data subject registration"""
        controller = GDPRController()
        subject = controller.register_data_subject("user123", "user@example.com")

        assert subject.subject_id == "user123"
        assert subject.email == "user@example.com"
        assert subject.consents == {}
        assert len(subject.data_processing_records) == 0

    def test_grant_consent(self) -> None:
        """Test consent granting"""
        controller = GDPRController()
        subject = controller.register_data_subject("user123")

        consent_id = subject.grant_consent(
            "analytics", [DataCategory.BEHAVIORAL], RetentionPeriod.SIX_MONTHS
        )

        assert consent_id in subject.consents
        consent = subject.consents[consent_id]
        assert consent["purpose"] == "analytics"
        assert "behavioral" in consent["data_categories"]
        assert consent["status"] == ConsentStatus.GRANTED.value

    def test_has_consent(self) -> None:
        """Test consent validation"""
        controller = GDPRController()
        subject = controller.register_data_subject("user123")

        # Grant consent
        subject.grant_consent("analytics", [DataCategory.BEHAVIORAL], RetentionPeriod.SIX_MONTHS)

        # Check valid consent
        assert subject.has_consent("analytics", DataCategory.BEHAVIORAL)
        # Check invalid consent
        assert not subject.has_consent("marketing", DataCategory.BEHAVIORAL)

    def test_withdraw_consent(self) -> None:
        """Test consent withdrawal"""
        controller = GDPRController()
        subject = controller.register_data_subject("user123")

        consent_id = subject.grant_consent(
            "analytics", [DataCategory.BEHAVIORAL], RetentionPeriod.SIX_MONTHS
        )

        # Withdraw consent
        result = subject.withdraw_consent(consent_id)
        assert result is True
        assert subject.consents[consent_id]["status"] == ConsentStatus.WITHDRAWN.value

    def test_data_processing(self) -> None:
        """Test data processing with consent"""
        controller = GDPRController()
        subject = controller.register_data_subject("user123")

        # Grant consent for legitimate interests (same as processing purpose)
        subject.grant_consent(
            "legitimate_interests",
            [DataCategory.BEHAVIORAL],
            RetentionPeriod.SIX_MONTHS,
        )

        # Process data
        result = controller.process_data(
            "user123",
            DataProcessingPurpose.LEGITIMATE_INTERESTS,
            [DataCategory.BEHAVIORAL],
            {
                "action": "page_view",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "OmniMind Analytics",
        )

        assert result is True
        assert len(subject.data_processing_records) == 1
        assert len(controller.processing_records) == 1

    def test_data_processing_without_consent(self) -> None:
        """Test data processing without consent fails"""
        controller = GDPRController()

        # Try to process data without consent
        result = controller.process_data(
            "user123",
            DataProcessingPurpose.LEGITIMATE_INTERESTS,
            [DataCategory.BEHAVIORAL],
            {"action": "page_view"},
            "OmniMind Analytics",
        )

        assert result is False

    def test_right_of_access(self) -> None:
        """Test GDPR right of access"""
        controller = GDPRController()
        subject = controller.register_data_subject("user123", "user@example.com")

        # Grant consent and process data
        subject.grant_consent("analytics", [DataCategory.BEHAVIORAL], RetentionPeriod.SIX_MONTHS)
        controller.process_data(
            "user123",
            DataProcessingPurpose.LEGITIMATE_INTERESTS,
            [DataCategory.BEHAVIORAL],
            {"test": "data"},
        )

        # Request access
        response = controller.handle_data_subject_rights("user123", "access")

        assert response["status"] == "success"
        assert "personal_data" in response["data"]
        assert "consents" in response["data"]
        assert "processing_records" in response["data"]

    def test_right_to_erasure(self) -> None:
        """Test GDPR right to erasure"""
        controller = GDPRController()
        subject = controller.register_data_subject("user123", "user@example.com")

        # Grant consent and process data
        subject.grant_consent("analytics", [DataCategory.BEHAVIORAL], RetentionPeriod.SIX_MONTHS)
        controller.process_data(
            "user123",
            DataProcessingPurpose.LEGITIMATE_INTERESTS,
            [DataCategory.BEHAVIORAL],
            {"test": "data"},
        )

        # Request erasure
        response = controller.handle_data_subject_rights(
            "user123", "erasure", reason="User request"
        )

        assert response["status"] == "success"
        assert subject.email is None  # Personal data anonymized
        assert subject.consents == {}  # Consents removed
        assert subject.data_processing_records == []  # Processing records removed

    def test_data_retention_enforcement(self) -> None:
        """Test data retention policy enforcement"""
        controller = GDPRController()
        subject = controller.register_data_subject("user123")

        # Grant consent with short retention
        subject.grant_consent("analytics", [DataCategory.BEHAVIORAL], RetentionPeriod.SESSION_ONLY)

        # Manually expire the consent by setting old date
        old_date = datetime.now(timezone.utc) - timedelta(hours=25)
        subject.consents[list(subject.consents.keys())[0]]["expires_at"] = old_date.isoformat()

        # Run retention enforcement
        cleaned_count = controller.enforce_data_retention()

        assert cleaned_count > 0

        # Check that consent is expired
        consent = list(subject.consents.values())[0]
        assert consent["status"] == ConsentStatus.EXPIRED.value
