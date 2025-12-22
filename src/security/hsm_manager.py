"""
Hardware Security Module (HSM) Manager
Provides secure key management and cryptographic operations
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import threading
from dataclasses import dataclass
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class KeyMetadata:
    """Metadata for cryptographic keys"""

    key_id: str
    algorithm: str
    key_size: int
    created_at: str
    expires_at: Optional[str] = None
    usage_count: int = 0
    max_usage: Optional[int] = None
    status: str = "active"


class HSMManager:
    """
    Simulated Hardware Security Module for production key management.
    In production, this would interface with actual HSM hardware.
    """

    _instance: Optional["HSMManager"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "HSMManager":
        """Singleton pattern to avoid multiple expensive initializations"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        # Only initialize once due to singleton
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self.keys: Dict[str, Dict[str, Any]] = {}
        self.master_key = self._generate_master_key()
        self.key_counter = 0
        logger.info("HSM Manager initialized")

    def _generate_master_key(self) -> bytes:
        """Generate or load master key (simulated HSM master key)"""
        # In production, this would be stored in HSM secure memory
        master_key_file = ".omnimind/hsm/master.key"

        if os.path.exists(master_key_file):
            with open(master_key_file, "rb") as f:
                encrypted_data = f.read()
                # Extract salt (first 32 bytes) and encrypted master key
                if len(encrypted_data) < 32:
                    raise ValueError("Invalid master key file format")
                salt = encrypted_data[:32]
                encrypted_master = encrypted_data[32:]

                # Derive system key using stored salt (increased iterations for security)
                system_key = hashlib.pbkdf2_hmac("sha256", os.urandom(32), salt, 100000, dklen=32)

                master_key = self._decrypt_data(encrypted_master, system_key)
                return master_key
        else:
            # Generate new master key
            os.makedirs(os.path.dirname(master_key_file), exist_ok=True)
            master_key = secrets.token_bytes(32)  # 256-bit key

            # Generate unique salt for this master key
            salt = secrets.token_bytes(32)  # 256-bit salt

            # Derive system key using random salt (increased iterations for security)
            system_key = hashlib.pbkdf2_hmac("sha256", os.urandom(32), salt, 100000, dklen=32)

            encrypted_master = self._encrypt_data(master_key, system_key)

            # Store salt + encrypted master key
            with open(master_key_file, "wb") as f:
                f.write(salt + encrypted_master)

            logger.info("New master key generated and stored")
            return master_key

    def _encrypt_data(self, data: bytes, key: bytes) -> bytes:
        """Real AES-based encryption using Fernet (cryptography)."""
        from cryptography.fernet import Fernet
        import base64

        # Fernet requires 32-byte key encoded in base64
        f_key = base64.urlsafe_b64encode(key)
        f = Fernet(f_key)
        return f.encrypt(data)

    def _decrypt_data(self, encrypted_data: bytes, key: bytes) -> bytes:
        """Real AES-based decryption."""
        from cryptography.fernet import Fernet
        import base64

        f_key = base64.urlsafe_b64encode(key)
        f = Fernet(f_key)
        return f.decrypt(encrypted_data)

    def generate_key(
        self,
        algorithm: str = "RSA",
        key_size: int = 2048,
        max_usage: Optional[int] = None,
    ) -> str:
        """
        Generate a new cryptographic key in the HSM

        Args:
            algorithm: Cryptographic algorithm (RSA, ECDSA, etc.)
            key_size: Key size in bits
            max_usage: Maximum number of times this key can be used

        Returns:
            Key ID for the generated key
        """
        self.key_counter += 1
        key_id = f"omnimind_key_{self.key_counter:04d}"

        # Generate key material (simulated)
        if algorithm == "RSA":
            # In production, this would generate actual RSA key pair in HSM
            private_key = secrets.token_bytes(key_size // 8)
            public_key = hashlib.sha256(private_key).digest()  # Simulated public key
        elif algorithm == "AES":
            private_key = secrets.token_bytes(key_size // 8)
            public_key = None
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        # Store key metadata
        self.keys[key_id] = {
            "private_key": private_key,
            "public_key": public_key,
            "algorithm": algorithm,
            "key_size": key_size,
            "metadata": KeyMetadata(
                key_id=key_id,
                algorithm=algorithm,
                key_size=key_size,
                created_at=os.environ.get("CURRENT_TIME", "2025-11-19T12:00:00Z"),
                max_usage=max_usage,
            ),
        }

        logger.info(
            "Cryptographic key generated",
            key_id=key_id,
            algorithm=algorithm,
            key_size=key_size,
        )

        return key_id

    def sign_data(self, key_id: str, data: bytes) -> bytes:
        """
        Sign data using the specified key

        Args:
            key_id: ID of the key to use for signing
            data: Data to sign

        Returns:
            Digital signature

        Raises:
            ValueError: If key not found or usage limit exceeded
        """
        if key_id not in self.keys:
            raise ValueError(f"Key not found: {key_id}")

        key_data = self.keys[key_id]
        metadata = key_data["metadata"]

        # Check usage limits
        if metadata.max_usage and metadata.usage_count >= metadata.max_usage:
            raise ValueError(f"Key usage limit exceeded: {key_id}")

        # Update usage counter
        metadata.usage_count += 1

        # Generate signature (simulated)
        private_key = key_data["private_key"]
        signature = hmac.new(private_key, data, hashlib.sha256).digest()

        logger.info(
            "Data signed",
            key_id=key_id,
            data_size=len(data),
            usage_count=metadata.usage_count,
        )

        return signature

    def verify_signature(self, key_id: str, data: bytes, signature: bytes) -> bool:
        """
        Verify a digital signature

        Args:
            key_id: ID of the key used for signing
            data: Original data
            signature: Signature to verify

        Returns:
            True if signature is valid
        """
        if key_id not in self.keys:
            return False

        key_data = self.keys[key_id]
        private_key = key_data["private_key"]

        # Verify signature (simulated)
        expected_signature = hmac.new(private_key, data, hashlib.sha256).digest()

        is_valid = hmac.compare_digest(signature, expected_signature)

        logger.info("Signature verification", key_id=key_id, is_valid=is_valid)

        return is_valid

    def encrypt_data(self, key_id: str, plaintext: bytes) -> bytes:
        """
        Encrypt data using the specified key

        Args:
            key_id: ID of the encryption key
            plaintext: Data to encrypt

        Returns:
            Encrypted data
        """
        if key_id not in self.keys:
            raise ValueError(f"Key not found: {key_id}")

        key_data = self.keys[key_id]
        private_key = key_data["private_key"]

        # Simple XOR encryption for demonstration
        # In production, use proper AES encryption
        encrypted = bytes(
            a ^ b for a, b in zip(plaintext, private_key * (len(plaintext) // len(private_key) + 1))
        )

        logger.info("Data encrypted", key_id=key_id, data_size=len(plaintext))

        return encrypted

    def decrypt_data(self, key_id: str, ciphertext: bytes) -> bytes:
        """
        Decrypt data using the specified key

        Args:
            key_id: ID of the decryption key
            ciphertext: Data to decrypt

        Returns:
            Decrypted data
        """
        if key_id not in self.keys:
            raise ValueError(f"Key not found: {key_id}")

        key_data = self.keys[key_id]
        private_key = key_data["private_key"]

        # Reverse XOR encryption
        decrypted = bytes(
            a ^ b
            for a, b in zip(ciphertext, private_key * (len(ciphertext) // len(private_key) + 1))
        )

        logger.info("Data decrypted", key_id=key_id, data_size=len(ciphertext))

        return decrypted

    def get_key_info(self, key_id: str) -> Optional[KeyMetadata]:
        """
        Get metadata for a specific key

        Args:
            key_id: Key identifier

        Returns:
            Key metadata or None if key not found
        """
        if key_id not in self.keys:
            return None

        metadata: KeyMetadata = self.keys[key_id]["metadata"]
        return metadata

    def list_keys(self) -> Dict[str, KeyMetadata]:
        """
        List all keys managed by the HSM

        Returns:
            Dictionary of key_id -> KeyMetadata
        """
        return {key_id: key_data["metadata"] for key_id, key_data in self.keys.items()}

    def destroy_key(self, key_id: str) -> bool:
        """
        Securely destroy a key

        Args:
            key_id: ID of the key to destroy

        Returns:
            True if key was destroyed
        """
        if key_id in self.keys:
            # In production, this would securely erase key material from HSM
            del self.keys[key_id]
            logger.info("Key destroyed", key_id=key_id)
            return True

        return False

    def reset_for_testing(self) -> None:
        """
        Reset HSM state for testing purposes.
        WARNING: This method should only be used in test environments.
        """
        self.keys.clear()
        self.key_counter = 0
        logger.warning("HSM state reset for testing")

    def get_hsm_status(self) -> Dict[str, Any]:
        """
        Get HSM operational status

        Returns:
            Status information
        """
        total_keys = len(self.keys)
        active_keys = sum(1 for k in self.keys.values() if k["metadata"].status == "active")

        return {
            "status": "operational",
            "total_keys": total_keys,
            "active_keys": active_keys,
            "master_key_initialized": self.master_key is not None,
            "supported_algorithms": ["RSA", "AES"],
            "fips_compliant": False,  # This is a simulation
            "tamper_detected": False,
        }

    def backup_keys(self, backup_path: str) -> bool:
        """
        Create encrypted backup of all keys

        Args:
            backup_path: Path to store backup

        Returns:
            True if backup successful
        """
        try:
            # This is a simplified backup - in production, use proper key backup procedures
            backup_data = {
                "keys": self.keys,
                "backup_date": os.environ.get("CURRENT_TIME", "2025-11-19T12:00:00Z"),
                "version": "1.0",
            }

            # Encrypt backup with master key
            import json

            backup_json = json.dumps(backup_data, default=str).encode()
            encrypted_backup = self._encrypt_data(backup_json, self.master_key)

            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            with open(backup_path, "wb") as f:
                f.write(encrypted_backup)

            logger.info("Key backup created", backup_path=backup_path)
            return True

        except Exception as e:
            logger.error("Key backup failed", error=str(e))
            return False

    def restore_keys(self, backup_path: str, master_key: bytes) -> bool:
        """
        Restore keys from encrypted backup

        Args:
            backup_path: Path to backup file
            master_key: Master key for decryption

        Returns:
            True if restore successful
        """
        try:
            with open(backup_path, "rb") as f:
                encrypted_backup = f.read()

            # Decrypt backup
            backup_json = self._decrypt_data(encrypted_backup, master_key)

            import json

            backup_data = json.loads(backup_json.decode())

            self.keys = backup_data["keys"]
            logger.info("Keys restored from backup", backup_path=backup_path)
            return True

        except Exception as e:
            logger.error("Key restore failed", error=str(e))
            return False


# Global HSM manager instance - lazy initialization to avoid import-time overhead
_hsm_manager_instance: Optional[HSMManager] = None


def get_hsm_manager() -> HSMManager:
    """Get global HSM manager instance (lazy initialization)"""
    global _hsm_manager_instance
    if _hsm_manager_instance is None:
        _hsm_manager_instance = HSMManager()
    return _hsm_manager_instance


# Keep backward compatibility
hsm_manager = None  # Will be set on first access
