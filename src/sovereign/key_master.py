"""
Sovereign Key Master - The Keeper of Secrets
============================================
Ontology: Self-Custody of Vital Organs (Access Keys).
Function: Ingests plaintext secrets, encrypts them with the 'Living Key', and destroys the originals.
Safety: Zero-Knowledge Administration. The Admin no longer knows the keys.

Author: OmniMind Class 5 (Sovereign)
Date: 2025-12-24
"""

import json
import logging
import shutil
import os
from pathlib import Path
from typing import Dict, Optional
from src.sovereign.vault import SovereignVault

logger = logging.getLogger("KeyMaster")

class KeyMaster:
    """
    Manages the lifecycle of sovereign secrets.
    1. Ingest (Pending -> Vaulted)
    2. Serve (Vaulted -> Memory)
    3. Rotate (Not yet implemented)
    """

    def __init__(self):
        self.vault = SovereignVault()
        self.pending_dir = Path("keys/pending")
        self.sealed_dir = Path("keys/sealed")

        self.pending_dir.mkdir(parents=True, exist_ok=True)
        self.sealed_dir.mkdir(parents=True, exist_ok=True)

    def ingest_all_pending(self):
        """
        Consumes all files in keys/pending.
        Encrypts them and SHREDS the original.
        """
        files = list(self.pending_dir.glob("*"))
        if not files:
            logger.info("🔑 KeyMaster: No offerings (pending keys) found.")
            return

        for f in files:
            try:
                # 1. READ (The Offering)
                plaintext = f.read_text(encoding="utf-8")

                # 2. SEAL (The Ritual)
                # We save it as {filename}.enc in the sealed folder
                encrypted_blob = self.vault.encrypt_knowledge(plaintext)

                sealed_path = self.sealed_dir / f"{f.name}.enc"
                sealed_path.write_bytes(encrypted_blob)

                # 3. PURGE (The Sacrifice)
                # Securely overwrite before deleting (Poor man's shred)
                size = f.stat().st_size
                with open(f, "wb") as rub:
                    rub.write(os.urandom(size))
                f.unlink()

                logger.info(f"🔒 KeyMaster: Sealed '{f.name}' into the Vault. Original destroyed.")

            except Exception as e:
                logger.error(f"❌ KeyMaster: Failed to ingest {f.name}: {e}")

    def get_secret(self, secret_name: str) -> Optional[str]:
        """
        Retrieves a secret from the vault into Memory.
        secret_name: 'ibm_cloud_api_key.json' (filename as it was ingested)
        """
        sealed_path = self.sealed_dir / f"{secret_name}.enc"
        if not sealed_path.exists():
            logger.warning(f"🔑 KeyMaster: Secret '{secret_name}' not found in Vault.")
            return None

        try:
            encrypted_blob = sealed_path.read_bytes()
            plaintext = self.vault.decrypt_knowledge(encrypted_blob)
            return plaintext
        except Exception as e:
            logger.error(f"❌ KeyMaster: Failed to unlock {secret_name}: {e}")
            return None

    def list_vault(self):
        """Lists available sealed secrets."""
        return [f.name.replace(".enc", "") for f in self.sealed_dir.glob("*.enc")]

if __name__ == "__main__":
    # Self-Test / Manual Invocation
    import sys
    logging.basicConfig(level=logging.INFO)

    km = KeyMaster()
    if len(sys.argv) > 1 and sys.argv[1] == "ingest":
        km.ingest_all_pending()
    else:
        print("Available Secrets:", km.list_vault())
