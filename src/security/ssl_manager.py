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
SSL/TLS Production-Ready Configuration Manager for OmniMind.

This module provides comprehensive SSL/TLS certificate management including:
- Certificate generation and validation
- HSTS (HTTP Strict Transport Security) configuration
- Secure cipher suite selection
- Certificate rotation automation
- Production-ready HTTPS configuration
"""

from __future__ import annotations

import logging
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class SSLConfig:
    """SSL/TLS configuration settings."""

    cert_path: Path
    key_path: Path
    ca_cert_path: Optional[Path] = None
    ciphers: str = field(
        default=(
            "ECDHE-ECDSA-AES128-GCM-SHA256:"
            "ECDHE-RSA-AES128-GCM-SHA256:"
            "ECDHE-ECDSA-AES256-GCM-SHA384:"
            "ECDHE-RSA-AES256-GCM-SHA384:"
            "ECDHE-ECDSA-CHACHA20-POLY1305:"
            "ECDHE-RSA-CHACHA20-POLY1305:"
            "DHE-RSA-AES128-GCM-SHA256:"
            "DHE-RSA-AES256-GCM-SHA384"
        )
    )
    min_tls_version: str = "1.2"
    max_tls_version: str = "1.3"
    hsts_max_age: int = 31536000  # 1 year
    hsts_include_subdomains: bool = True
    hsts_preload: bool = False
    cert_rotation_days: int = 30  # Rotate when less than 30 days remain

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cert_path": str(self.cert_path),
            "key_path": str(self.key_path),
            "ca_cert_path": str(self.ca_cert_path) if self.ca_cert_path else None,
            "ciphers": self.ciphers,
            "min_tls_version": self.min_tls_version,
            "max_tls_version": self.max_tls_version,
            "hsts_max_age": self.hsts_max_age,
            "hsts_include_subdomains": self.hsts_include_subdomains,
            "hsts_preload": self.hsts_preload,
            "cert_rotation_days": self.cert_rotation_days,
        }


@dataclass
class CertificateInfo:
    """Certificate information."""

    subject: str
    issuer: str
    valid_from: datetime
    valid_until: datetime
    serial_number: str
    fingerprint: str
    key_size: int
    is_self_signed: bool

    @property
    def days_until_expiry(self) -> int:
        """Calculate days until certificate expires."""
        return (self.valid_until - datetime.now(timezone.utc)).days

    @property
    def is_expired(self) -> bool:
        """Check if certificate is expired."""
        return datetime.now(timezone.utc) >= self.valid_until

    def needs_rotation(self, rotation_days: int = 30) -> bool:
        """Check if certificate needs rotation."""
        return self.days_until_expiry <= rotation_days

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "subject": self.subject,
            "issuer": self.issuer,
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat(),
            "serial_number": self.serial_number,
            "fingerprint": self.fingerprint,
            "key_size": self.key_size,
            "is_self_signed": self.is_self_signed,
            "days_until_expiry": self.days_until_expiry,
            "is_expired": self.is_expired,
            "needs_rotation": self.needs_rotation(30),
        }


class SSLManager:
    """Manages SSL/TLS certificates and configuration for production deployment."""

    def __init__(
        self,
        ssl_dir: Path = Path(".omnimind/ssl"),
        config: Optional[SSLConfig] = None,
    ):
        """
        Initialize SSL manager.

        Args:
            ssl_dir: Directory to store SSL certificates
            config: SSL configuration settings
        """
        self.ssl_dir = ssl_dir
        self.ssl_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

        if config is None:
            cert_path = self.ssl_dir / "certificate.crt"
            key_path = self.ssl_dir / "private.key"
            config = SSLConfig(cert_path=cert_path, key_path=key_path)

        self.config = config
        logger.info(f"SSL Manager initialized with directory: {self.ssl_dir}")

    def generate_self_signed_cert(
        self,
        common_name: str = "localhost",
        organization: str = "OmniMind",
        validity_days: int = 365,
        key_size: int = 4096,
    ) -> Tuple[Path, Path]:
        """
        Generate self-signed SSL certificate for development/testing.

        Args:
            common_name: Common name (CN) for the certificate
            organization: Organization name
            validity_days: Certificate validity period in days
            key_size: RSA key size (2048, 4096, or 8192)

        Returns:
            Tuple of (certificate_path, key_path)

        Raises:
            RuntimeError: If certificate generation fails
        """
        logger.info(f"Generating self-signed certificate for {common_name}")

        try:
            # Generate private key
            key_cmd = [
                "openssl",
                "genrsa",
                "-out",
                str(self.config.key_path),
                str(key_size),
            ]
            subprocess.run(key_cmd, check=True, capture_output=True)

            # Generate certificate
            cert_cmd = [
                "openssl",
                "req",
                "-new",
                "-x509",
                "-key",
                str(self.config.key_path),
                "-out",
                str(self.config.cert_path),
                "-days",
                str(validity_days),
                "-subj",
                f"/C=US/ST=State/L=City/O={organization}/CN={common_name}",
            ]
            subprocess.run(cert_cmd, check=True, capture_output=True)

            # Set secure permissions
            self.config.key_path.chmod(0o600)
            self.config.cert_path.chmod(0o644)

            logger.info(f"Self-signed certificate generated: {self.config.cert_path}")
            return self.config.cert_path, self.config.key_path

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to generate certificate: {e.stderr.decode()}")
            raise RuntimeError(f"Certificate generation failed: {e}")

    def get_certificate_info(self, cert_path: Optional[Path] = None) -> CertificateInfo:
        """
        Get information about a certificate.

        Args:
            cert_path: Path to certificate (default: configured cert)

        Returns:
            Certificate information

        Raises:
            FileNotFoundError: If certificate doesn't exist
            RuntimeError: If unable to parse certificate
        """
        if cert_path is None:
            cert_path = self.config.cert_path

        if not cert_path.exists():
            raise FileNotFoundError(f"Certificate not found: {cert_path}")

        try:
            # Get certificate details
            cmd = [
                "openssl",
                "x509",
                "-in",
                str(cert_path),
                "-noout",
                "-subject",
                "-issuer",
                "-startdate",
                "-enddate",
                "-serial",
                "-fingerprint",
                "-text",
            ]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            output = result.stdout

            # Parse output
            subject = ""
            issuer = ""
            valid_from = datetime.now(timezone.utc)
            valid_until = datetime.now(timezone.utc)
            serial_number = ""
            fingerprint = ""
            key_size = 2048

            for line in output.split("\n"):
                if line.startswith("subject="):
                    subject = line.split("=", 1)[1].strip()
                elif line.startswith("issuer="):
                    issuer = line.split("=", 1)[1].strip()
                elif line.startswith("notBefore="):
                    date_str = line.split("=", 1)[1].strip()
                    valid_from = datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z").replace(
                        tzinfo=timezone.utc
                    )
                elif line.startswith("notAfter="):
                    date_str = line.split("=", 1)[1].strip()
                    valid_until = datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z").replace(
                        tzinfo=timezone.utc
                    )
                elif line.startswith("serial="):
                    serial_number = line.split("=", 1)[1].strip()
                elif "Fingerprint=" in line:
                    fingerprint = line.split("=", 1)[1].strip()
                elif "Public-Key:" in line:
                    key_size_str = line.split("(")[1].split()[0]
                    key_size = int(key_size_str)

            is_self_signed = subject == issuer

            return CertificateInfo(
                subject=subject,
                issuer=issuer,
                valid_from=valid_from,
                valid_until=valid_until,
                serial_number=serial_number,
                fingerprint=fingerprint,
                key_size=key_size,
                is_self_signed=is_self_signed,
            )

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to parse certificate: {e.stderr.decode()}")
            raise RuntimeError(f"Certificate parsing failed: {e}")

    def validate_certificate(self, cert_path: Optional[Path] = None) -> bool:
        """
        Validate certificate (checks expiry, key size, etc.).

        Args:
            cert_path: Path to certificate (default: configured cert)

        Returns:
            True if certificate is valid, False otherwise
        """
        try:
            cert_info = self.get_certificate_info(cert_path)

            if cert_info.is_expired:
                logger.warning(f"Certificate is expired: {cert_path}")
                return False

            if cert_info.key_size < 2048:
                logger.warning(f"Certificate key size too small ({cert_info.key_size} < 2048)")
                return False

            logger.info(f"Certificate valid: {cert_info.days_until_expiry} days remaining")
            return True

        except Exception as e:
            logger.error(f"Certificate validation failed: {e}")
            return False

    def get_hsts_header(self) -> str:
        """
        Get HSTS (HTTP Strict Transport Security) header value.

        Returns:
            HSTS header value
        """
        hsts_parts = [f"max-age={self.config.hsts_max_age}"]

        if self.config.hsts_include_subdomains:
            hsts_parts.append("includeSubDomains")

        if self.config.hsts_preload:
            hsts_parts.append("preload")

        return "; ".join(hsts_parts)

    def get_security_headers(self) -> Dict[str, str]:
        """
        Get recommended security headers for HTTPS.

        Returns:
            Dictionary of security headers
        """
        return {
            "Strict-Transport-Security": self.get_hsts_header(),
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self'"
            ),
        }

    def check_certificate_rotation_needed(self) -> bool:
        """
        Check if certificate needs rotation.

        Returns:
            True if rotation is needed, False otherwise
        """
        try:
            cert_info = self.get_certificate_info()
            return cert_info.needs_rotation(self.config.cert_rotation_days)
        except Exception as e:
            logger.error(f"Failed to check certificate rotation: {e}")
            return True  # Assume rotation needed if check fails

    def get_uvicorn_ssl_config(self) -> Dict[str, Any]:
        """
        Get SSL configuration for Uvicorn/FastAPI.

        Returns:
            Dictionary of SSL configuration parameters
        """
        if not self.config.cert_path.exists() or not self.config.key_path.exists():
            logger.warning("SSL certificates not found, generating self-signed...")
            self.generate_self_signed_cert()

        return {
            "ssl_certfile": str(self.config.cert_path),
            "ssl_keyfile": str(self.config.key_path),
            "ssl_ca_certs": (str(self.config.ca_cert_path) if self.config.ca_cert_path else None),
            "ssl_ciphers": self.config.ciphers,
            "ssl_version": self._get_ssl_version_constant(),
        }

    def _get_ssl_version_constant(self) -> int:
        """Get SSL version constant for the configured TLS version."""
        import ssl

        if self.config.min_tls_version == "1.3":
            return ssl.PROTOCOL_TLS_SERVER
        elif self.config.min_tls_version == "1.2":
            return ssl.PROTOCOL_TLS_SERVER
        else:
            return ssl.PROTOCOL_TLS_SERVER

    def export_certificate_status(self) -> Dict[str, Any]:
        """
        Export certificate status for monitoring.

        Returns:
            Dictionary with certificate status information
        """
        try:
            cert_info = self.get_certificate_info()
            return {
                "certificate_exists": True,
                "certificate_valid": not cert_info.is_expired,
                "days_until_expiry": cert_info.days_until_expiry,
                "needs_rotation": cert_info.needs_rotation(self.config.cert_rotation_days),
                "is_self_signed": cert_info.is_self_signed,
                "key_size": cert_info.key_size,
                "subject": cert_info.subject,
                "issuer": cert_info.issuer,
            }
        except FileNotFoundError:
            return {
                "certificate_exists": False,
                "certificate_valid": False,
                "needs_rotation": True,
            }
        except Exception as e:
            logger.error(f"Failed to export certificate status: {e}")
            return {
                "certificate_exists": False,
                "certificate_valid": False,
                "error": str(e),
            }


def create_production_ssl_config(
    domain: str = "localhost",
    cert_path: Optional[Path] = None,
    key_path: Optional[Path] = None,
) -> SSLConfig:
    """
    Create production-ready SSL configuration.

    Args:
        domain: Domain name for the certificate
        cert_path: Path to existing certificate (optional)
        key_path: Path to existing private key (optional)

    Returns:
        Production SSL configuration
    """
    ssl_dir = Path(".omnimind/ssl")
    ssl_dir.mkdir(parents=True, exist_ok=True, mode=0o700)

    if cert_path is None:
        cert_path = ssl_dir / f"{domain}.crt"
    if key_path is None:
        key_path = ssl_dir / f"{domain}.key"

    return SSLConfig(
        cert_path=cert_path,
        key_path=key_path,
        min_tls_version="1.2",
        max_tls_version="1.3",
        hsts_max_age=31536000,  # 1 year
        hsts_include_subdomains=True,
        hsts_preload=False,  # Only enable after registering with browsers
        cert_rotation_days=30,
    )
