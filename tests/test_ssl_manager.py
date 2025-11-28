from __future__ import annotations

from pathlib import Path
import pytest
from src.security.ssl_manager import (


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
Tests for SSL/TLS Manager.
"""




    SSLConfig,
    SSLManager,
    create_production_ssl_config,
)


@pytest.fixture
def temp_ssl_dir(tmp_path: Path) -> Path:
    """Create temporary SSL directory."""
    ssl_dir = tmp_path / "ssl"
    ssl_dir.mkdir()
    return ssl_dir


@pytest.fixture
def ssl_manager(temp_ssl_dir: Path) -> SSLManager:
    """Create SSL manager instance."""
    return SSLManager(ssl_dir=temp_ssl_dir)


def test_ssl_manager_initialization(ssl_manager: SSLManager, temp_ssl_dir: Path) -> None:
    """Test SSL manager initializes correctly."""
    assert ssl_manager.ssl_dir == temp_ssl_dir
    assert temp_ssl_dir.exists()
    assert ssl_manager.config is not None


def test_generate_self_signed_cert(ssl_manager: SSLManager) -> None:
    """Test self-signed certificate generation."""
    cert_path, key_path = ssl_manager.generate_self_signed_cert(
        common_name="test.local",
        organization="Test Org",
        validity_days=365,
        key_size=2048,
    )

    assert cert_path.exists()
    assert key_path.exists()
    assert oct(key_path.stat().st_mode)[-3:] == "600"  # Check permissions


def test_validate_certificate(ssl_manager: SSLManager) -> None:
    """Test certificate validation."""
    # Generate certificate
    ssl_manager.generate_self_signed_cert()

    # Validate
    assert ssl_manager.validate_certificate()


def test_get_certificate_info(ssl_manager: SSLManager) -> None:
    """Test getting certificate information."""
    ssl_manager.generate_self_signed_cert(
        common_name="test.local",
        organization="Test Org",
    )

    cert_info = ssl_manager.get_certificate_info()

    assert cert_info.subject
    assert cert_info.issuer
    assert cert_info.valid_from
    assert cert_info.valid_until
    assert cert_info.key_size >= 2048
    assert cert_info.is_self_signed  # Self-signed cert


def test_get_hsts_header(ssl_manager: SSLManager) -> None:
    """Test HSTS header generation."""
    header = ssl_manager.get_hsts_header()

    assert "max-age=" in header
    assert str(ssl_manager.config.hsts_max_age) in header


def test_get_security_headers(ssl_manager: SSLManager) -> None:
    """Test security headers."""
    headers = ssl_manager.get_security_headers()

    assert "Strict-Transport-Security" in headers
    assert "X-Content-Type-Options" in headers
    assert "X-Frame-Options" in headers
    assert "X-XSS-Protection" in headers
    assert "Content-Security-Policy" in headers


def test_get_uvicorn_ssl_config(ssl_manager: SSLManager) -> None:
    """Test Uvicorn SSL configuration."""
    ssl_manager.generate_self_signed_cert()

    config = ssl_manager.get_uvicorn_ssl_config()

    assert "ssl_certfile" in config
    assert "ssl_keyfile" in config
    assert "ssl_ciphers" in config


def test_export_certificate_status(ssl_manager: SSLManager) -> None:
    """Test certificate status export."""
    # Without certificate
    status = ssl_manager.export_certificate_status()
    assert status["certificate_exists"] is False

    # With certificate
    ssl_manager.generate_self_signed_cert()
    status = ssl_manager.export_certificate_status()
    assert status["certificate_exists"] is True
    assert status["certificate_valid"] is True
    assert "days_until_expiry" in status


def test_create_production_ssl_config() -> None:
    """Test production SSL config creation."""
    config = create_production_ssl_config(domain="example.com")

    assert config.min_tls_version == "1.2"
    assert config.max_tls_version == "1.3"
    assert config.hsts_max_age == 31536000
    assert config.hsts_include_subdomains is True


def test_ssl_config_to_dict() -> None:
    """Test SSL config serialization."""
    cert_path = Path("/tmp/cert.crt")
    key_path = Path("/tmp/key.key")

    config = SSLConfig(cert_path=cert_path, key_path=key_path)
    config_dict = config.to_dict()

    assert config_dict["cert_path"] == str(cert_path)
    assert config_dict["key_path"] == str(key_path)
    assert "ciphers" in config_dict
    assert "min_tls_version" in config_dict
