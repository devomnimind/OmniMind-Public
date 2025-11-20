"""Tests for HSM Manager"""

import pytest
from src.security.hsm_manager import HSMManager


class TestHSMManager:
    """Test HSM Manager functionality"""

    def test_hsm_initialization(self) -> None:
        """Test HSM manager initialization"""
        hsm = HSMManager()
        assert hsm.master_key is not None
        assert isinstance(hsm.keys, dict)
        assert hsm.key_counter == 0

    def test_generate_key_rsa(self) -> None:
        """Test RSA key generation"""
        hsm = HSMManager()
        key_id = hsm.generate_key("RSA", 2048)

        assert key_id.startswith("omnimind_key_")
        assert key_id in hsm.keys

        key_data = hsm.keys[key_id]
        assert key_data["algorithm"] == "RSA"
        assert key_data["key_size"] == 2048

        metadata = key_data["metadata"]
        assert metadata.key_id == key_id
        assert metadata.algorithm == "RSA"
        assert metadata.status == "active"
        assert metadata.usage_count == 0

    def test_generate_key_aes(self) -> None:
        """Test AES key generation"""
        hsm = HSMManager()
        key_id = hsm.generate_key("AES", 256)

        assert key_id in hsm.keys
        key_data = hsm.keys[key_id]
        assert key_data["algorithm"] == "AES"
        assert key_data["key_size"] == 256

    def test_generate_key_invalid_algorithm(self) -> None:
        """Test invalid algorithm rejection"""
        hsm = HSMManager()

        with pytest.raises(ValueError, match="Unsupported algorithm"):
            hsm.generate_key("INVALID", 256)

    def test_sign_and_verify_data(self) -> None:
        """Test data signing and verification"""
        hsm = HSMManager()
        key_id = hsm.generate_key("RSA", 2048)

        test_data = b"Hello, World!"
        signature = hsm.sign_data(key_id, test_data)

        assert isinstance(signature, bytes)
        assert len(signature) > 0

        # Verify signature
        is_valid = hsm.verify_signature(key_id, test_data, signature)
        assert is_valid is True

        # Verify with wrong data
        is_valid_wrong = hsm.verify_signature(key_id, b"Wrong data", signature)
        assert is_valid_wrong is False

    def test_sign_usage_limits(self) -> None:
        """Test key usage limits"""
        hsm = HSMManager()
        key_id = hsm.generate_key("RSA", 2048, max_usage=2)

        # Use key twice
        hsm.sign_data(key_id, b"data1")
        hsm.sign_data(key_id, b"data2")

        # Third use should fail
        with pytest.raises(ValueError, match="usage limit exceeded"):
            hsm.sign_data(key_id, b"data3")

    def test_encrypt_decrypt_data(self) -> None:
        """Test data encryption and decryption"""
        hsm = HSMManager()
        key_id = hsm.generate_key("AES", 256)

        test_data = b"Sensitive information"
        encrypted = hsm.encrypt_data(key_id, test_data)

        assert isinstance(encrypted, bytes)
        assert encrypted != test_data  # Should be encrypted

        decrypted = hsm.decrypt_data(key_id, encrypted)
        assert decrypted == test_data

    def test_get_key_info(self) -> None:
        """Test key information retrieval"""
        hsm = HSMManager()
        key_id = hsm.generate_key("RSA", 2048)

        info = hsm.get_key_info(key_id)
        assert info is not None
        assert info.key_id == key_id
        assert info.algorithm == "RSA"

        # Test non-existent key
        info_none = hsm.get_key_info("nonexistent")
        assert info_none is None

    def test_list_keys(self) -> None:
        """Test key listing"""
        hsm = HSMManager()

        # Generate multiple keys
        key1 = hsm.generate_key("RSA", 2048)
        key2 = hsm.generate_key("AES", 256)

        keys = hsm.list_keys()
        assert len(keys) == 2
        assert key1 in keys
        assert key2 in keys

        assert keys[key1].algorithm == "RSA"
        assert keys[key2].algorithm == "AES"

    def test_destroy_key(self) -> None:
        """Test key destruction"""
        hsm = HSMManager()
        key_id = hsm.generate_key("RSA", 2048)

        assert key_id in hsm.keys

        # Destroy key
        result = hsm.destroy_key(key_id)
        assert result is True
        assert key_id not in hsm.keys

        # Try to destroy non-existent key
        result_none = hsm.destroy_key("nonexistent")
        assert result_none is False

    def test_hsm_status(self) -> None:
        """Test HSM status reporting"""
        hsm = HSMManager()

        # Generate some keys
        hsm.generate_key("RSA", 2048)
        hsm.generate_key("AES", 256)

        status = hsm.get_hsm_status()

        assert status["status"] == "operational"
        assert status["total_keys"] == 2
        assert status["active_keys"] == 2
        assert status["master_key_initialized"] is True
        assert "RSA" in status["supported_algorithms"]
        assert "AES" in status["supported_algorithms"]

    def test_key_backup_restore(self) -> None:
        """Test key backup and restore"""
        import tempfile
        import os

        hsm1 = HSMManager()
        key_id = hsm1.generate_key("RSA", 2048)

        # Create backup
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            backup_path = tmp.name

        try:
            success = hsm1.backup_keys(backup_path)
            assert success is True
            assert os.path.exists(backup_path)

            # Create new HSM and restore
            hsm2 = HSMManager()
            success_restore = hsm2.restore_keys(backup_path, hsm1.master_key)
            assert success_restore is True

            # Check if key was restored
            assert key_id in hsm2.keys

        finally:
            # Cleanup
            if os.path.exists(backup_path):
                os.unlink(backup_path)
