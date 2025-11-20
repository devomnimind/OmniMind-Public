"""
GDPR Compliance Framework for OmniMind
Implements data protection and privacy regulations
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timedelta, UTC
from enum import Enum
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger(__name__)


class DataProcessingPurpose(Enum):
    """Legal bases for data processing under GDPR"""

    CONSENT = "consent"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"
    PUBLIC_TASK = "public_task"
    LEGITIMATE_INTERESTS = "legitimate_interests"


class DataCategory(Enum):
    """Categories of personal data"""

    IDENTIFIERS = "identifiers"  # Names, emails, IDs
    FINANCIAL = "financial"  # Payment info, transaction data
    HEALTH = "health"  # Medical data, health metrics
    LOCATION = "location"  # GPS, IP addresses
    BEHAVIORAL = "behavioral"  # Usage patterns, preferences
    TECHNICAL = "technical"  # Device info, logs


class RetentionPeriod(Enum):
    """Data retention periods"""

    SESSION_ONLY = timedelta(hours=24)
    ONE_MONTH = timedelta(days=30)
    SIX_MONTHS = timedelta(days=180)
    ONE_YEAR = timedelta(days=365)
    TWO_YEARS = timedelta(days=730)
    INDEFINITE = None


class ConsentStatus(Enum):
    """User consent status"""

    PENDING = "pending"
    GRANTED = "granted"
    DENIED = "denied"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class DataSubject:
    """Represents a data subject (user) in the system"""

    def __init__(self, subject_id: str, email: Optional[str] = None):
        self.subject_id = subject_id
        self.email = email
        self.created_at = datetime.now(UTC)
        self.last_activity = datetime.now(UTC)
        self.consents: Dict[str, Dict[str, Any]] = {}
        self.data_processing_records: List[Dict[str, Any]] = []
        self.rights_requests: List[Dict[str, Any]] = []

    def grant_consent(
        self,
        purpose: str,
        data_categories: List[DataCategory],
        retention_period: RetentionPeriod,
    ) -> str:
        """Grant consent for data processing"""
        consent_id = hashlib.sha256(
            f"{self.subject_id}:{purpose}:{datetime.now(UTC).isoformat()}".encode()
        ).hexdigest()[:16]

        self.consents[consent_id] = {
            "purpose": purpose,
            "data_categories": [cat.value for cat in data_categories],
            "retention_period": (
                retention_period.value.total_seconds()
                if retention_period.value
                else None
            ),
            "status": ConsentStatus.GRANTED.value,
            "granted_at": datetime.now(UTC).isoformat(),
            "expires_at": (
                (datetime.now(UTC) + retention_period.value).isoformat()
                if retention_period.value
                else None
            ),
        }

        logger.info(
            "Consent granted",
            subject_id=self.subject_id,
            consent_id=consent_id,
            purpose=purpose,
        )
        return consent_id

    def withdraw_consent(self, consent_id: str) -> bool:
        """Withdraw consent for data processing"""
        if consent_id in self.consents:
            self.consents[consent_id]["status"] = ConsentStatus.WITHDRAWN.value
            self.consents[consent_id]["withdrawn_at"] = datetime.now(UTC).isoformat()
            logger.info(
                "Consent withdrawn", subject_id=self.subject_id, consent_id=consent_id
            )
            return True
        return False

    def has_consent(self, purpose: str, data_category: DataCategory) -> bool:
        """Check if subject has valid consent for specific processing"""
        for consent in self.consents.values():
            if (
                consent["purpose"] == purpose
                and data_category.value in consent["data_categories"]
                and consent["status"] == ConsentStatus.GRANTED.value
            ):

                # Check if consent hasn't expired
                if consent.get("expires_at"):
                    expires_at = datetime.fromisoformat(consent["expires_at"])
                    if datetime.now(UTC) > expires_at:
                        consent["status"] = ConsentStatus.EXPIRED.value
                        continue

                return True
        return False


class DataProcessingRecord:
    """Record of data processing activities"""

    def __init__(
        self,
        subject_id: str,
        purpose: DataProcessingPurpose,
        data_categories: List[DataCategory],
        data_controller: str,
    ):
        self.record_id = hashlib.sha256(
            f"{subject_id}:{purpose.value}:{datetime.now(UTC).isoformat()}".encode()
        ).hexdigest()[:16]

        self.subject_id = subject_id
        self.purpose = purpose
        self.data_categories = data_categories
        self.data_controller = data_controller
        self.timestamp = datetime.now(UTC)
        self.processed_data_hash = None  # Will be set when data is processed

    def record_processing(self, data_hash: str) -> None:
        """Record that data processing occurred"""
        self.processed_data_hash = data_hash
        logger.info(
            "Data processing recorded",
            record_id=self.record_id,
            subject_id=self.subject_id,
            purpose=self.purpose.value,
        )


class GDPRController:
    """Main GDPR compliance controller"""

    def __init__(self):
        self.data_subjects: Dict[str, DataSubject] = {}
        self.processing_records: List[DataProcessingRecord] = []
        self.retention_schedule: Dict[DataCategory, RetentionPeriod] = {
            DataCategory.IDENTIFIERS: RetentionPeriod.TWO_YEARS,
            DataCategory.FINANCIAL: RetentionPeriod.SIX_MONTHS,
            DataCategory.HEALTH: RetentionPeriod.ONE_YEAR,
            DataCategory.LOCATION: RetentionPeriod.ONE_MONTH,
            DataCategory.BEHAVIORAL: RetentionPeriod.SIX_MONTHS,
            DataCategory.TECHNICAL: RetentionPeriod.ONE_YEAR,
        }

    def register_data_subject(
        self, subject_id: str, email: Optional[str] = None
    ) -> DataSubject:
        """Register a new data subject"""
        if subject_id in self.data_subjects:
            return self.data_subjects[subject_id]

        subject = DataSubject(subject_id, email)
        self.data_subjects[subject_id] = subject

        logger.info("Data subject registered", subject_id=subject_id)
        return subject

    def process_data(
        self,
        subject_id: str,
        purpose: DataProcessingPurpose,
        data_categories: List[DataCategory],
        data: Any,
        data_controller: str = "OmniMind",
    ) -> bool:
        """Process personal data with GDPR compliance check"""

        subject = self.data_subjects.get(subject_id)
        if not subject:
            logger.warning("Data subject not found", subject_id=subject_id)
            return False

        # Check consent for all data categories
        for category in data_categories:
            if not subject.has_consent(purpose.value, category):
                logger.warning(
                    "No consent for data processing",
                    subject_id=subject_id,
                    purpose=purpose.value,
                    category=category.value,
                )
                return False

        # Create processing record
        record = DataProcessingRecord(
            subject_id, purpose, data_categories, data_controller
        )
        data_hash = hashlib.sha256(
            json.dumps(data, sort_keys=True).encode()
        ).hexdigest()
        record.record_processing(data_hash)

        self.processing_records.append(record)
        subject.data_processing_records.append(
            {
                "record_id": record.record_id,
                "purpose": purpose.value,
                "timestamp": record.timestamp.isoformat(),
                "data_hash": data_hash,
            }
        )

        logger.info(
            "Data processing completed",
            subject_id=subject_id,
            record_id=record.record_id,
        )
        return True

    def handle_data_subject_rights(
        self, subject_id: str, right: str, **kwargs
    ) -> Dict[str, Any]:
        """Handle data subject rights requests (GDPR Article 15-22)"""

        subject = self.data_subjects.get(subject_id)
        if not subject:
            return {"status": "error", "message": "Data subject not found"}

        rights_request = {
            "request_id": hashlib.sha256(
                f"{subject_id}:{right}:{datetime.now(UTC).isoformat()}".encode()
            ).hexdigest()[:16],
            "subject_id": subject_id,
            "right": right,
            "timestamp": datetime.now(UTC).isoformat(),
            "status": "processing",
        }

        subject.rights_requests.append(rights_request)

        if right == "access":
            # Right of access (Article 15)
            return self._handle_access_request(subject)

        elif right == "rectification":
            # Right to rectification (Article 16)
            return self._handle_rectification_request(
                subject, kwargs.get("corrections", {})
            )

        elif right == "erasure":
            # Right to erasure (Article 17)
            return self._handle_erasure_request(subject, kwargs.get("reason", ""))

        elif right == "restriction":
            # Right to restriction of processing (Article 18)
            return self._handle_restriction_request(subject)

        elif right == "portability":
            # Right to data portability (Article 20)
            return self._handle_portability_request(subject)

        elif right == "objection":
            # Right to object (Article 21)
            return self._handle_objection_request(subject, kwargs.get("reason", ""))

        else:
            rights_request["status"] = "invalid_right"
            return {"status": "error", "message": f"Unknown right: {right}"}

    def _handle_access_request(self, subject: DataSubject) -> Dict[str, Any]:
        """Handle right of access request"""
        return {
            "status": "success",
            "data": {
                "personal_data": {
                    "subject_id": subject.subject_id,
                    "email": subject.email,
                    "created_at": subject.created_at.isoformat(),
                    "last_activity": subject.last_activity.isoformat(),
                },
                "consents": subject.consents,
                "processing_records": subject.data_processing_records,
                "rights_requests": [
                    r for r in subject.rights_requests if r["status"] != "erased"
                ],
            },
        }

    def _handle_rectification_request(
        self, subject: DataSubject, corrections: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle right to rectification"""
        if "email" in corrections:
            subject.email = corrections["email"]

        logger.info(
            "Data rectification completed",
            subject_id=subject.subject_id,
            corrections=corrections,
        )
        return {"status": "success", "message": "Data rectified successfully"}

    def _handle_erasure_request(
        self, subject: DataSubject, reason: str
    ) -> Dict[str, Any]:
        """Handle right to erasure (right to be forgotten)"""
        # Mark all data as erased (don't actually delete for audit purposes)
        subject.consents = {}
        subject.data_processing_records = []
        subject.rights_requests = []

        # Anonymize personal data
        subject.email = None

        logger.info(
            "Data erasure completed", subject_id=subject.subject_id, reason=reason
        )
        return {"status": "success", "message": "Data erased successfully"}

    def _handle_restriction_request(self, subject: DataSubject) -> Dict[str, Any]:
        """Handle right to restriction of processing"""
        # Mark subject data as restricted
        subject.consents = {}  # Remove all consents

        logger.info("Processing restriction applied", subject_id=subject.subject_id)
        return {"status": "success", "message": "Processing restricted successfully"}

    def _handle_portability_request(self, subject: DataSubject) -> Dict[str, Any]:
        """Handle right to data portability"""
        portable_data = {
            "subject_id": subject.subject_id,
            "email": subject.email,
            "consents": subject.consents,
            "processing_records": subject.data_processing_records,
            "export_timestamp": datetime.now(UTC).isoformat(),
        }

        logger.info("Data portability export completed", subject_id=subject.subject_id)
        return {
            "status": "success",
            "data": portable_data,
            "format": "JSON",
            "message": "Data export ready for download",
        }

    def _handle_objection_request(
        self, subject: DataSubject, reason: str
    ) -> Dict[str, Any]:
        """Handle right to object"""
        subject.consents = {}  # Remove all consents

        logger.info(
            "Processing objection applied", subject_id=subject.subject_id, reason=reason
        )
        return {"status": "success", "message": "Processing objection applied"}

    def enforce_data_retention(self) -> int:
        """Enforce data retention policies - return number of records cleaned"""
        cleaned_count = 0
        current_time = datetime.now(UTC)

        for subject in self.data_subjects.values():
            # Clean expired consents
            expired_consents = []
            for consent_id, consent in subject.consents.items():
                if consent.get("expires_at"):
                    expires_at = datetime.fromisoformat(consent["expires_at"])
                    if current_time > expires_at:
                        expired_consents.append(consent_id)

            for consent_id in expired_consents:
                subject.consents[consent_id]["status"] = ConsentStatus.EXPIRED.value
                cleaned_count += 1

            # Clean old processing records (keep last 2 years)
            cutoff_date = current_time - timedelta(days=730)
            old_records = [
                record
                for record in subject.data_processing_records
                if datetime.fromisoformat(record["timestamp"]) < cutoff_date
            ]
            cleaned_count += len(old_records)
            # Keep records for audit but mark as archived
            for record in old_records:
                record["archived"] = True

        logger.info(
            "Data retention enforcement completed", cleaned_records=cleaned_count
        )
        return cleaned_count

    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate GDPR compliance report"""
        total_subjects = len(self.data_subjects)
        total_consents = sum(
            len(subject.consents) for subject in self.data_subjects.values()
        )
        total_processing_records = sum(
            len(subject.data_processing_records)
            for subject in self.data_subjects.values()
        )

        # Calculate consent statistics
        consent_stats = {"granted": 0, "denied": 0, "withdrawn": 0, "expired": 0}
        for subject in self.data_subjects.values():
            for consent in subject.consents.values():
                status = consent.get("status", "unknown")
                if status in consent_stats:
                    consent_stats[status] += 1

        return {
            "report_date": datetime.now(UTC).isoformat(),
            "gdpr_version": "GDPR 2018",
            "data_controller": "DevBrain Systems",
            "statistics": {
                "total_data_subjects": total_subjects,
                "total_consents": total_consents,
                "total_processing_records": total_processing_records,
                "consent_status_breakdown": consent_stats,
            },
            "compliance_status": (
                "compliant" if total_subjects > 0 else "not_applicable"
            ),
            "last_retention_enforcement": datetime.now(UTC).isoformat(),
        }


# Global GDPR controller instance
gdpr_controller = GDPRController()
