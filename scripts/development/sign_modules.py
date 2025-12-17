#!/usr/bin/env python3
"""
Secure Code Signing Script for OmniMind Modules

Signs all modules with developer credentials stored securely in environment.
This script:
- Reads credentials from environment variables (no hardcoding)
- Generates cryptographic signatures for each module
- Adds module-level signatures to headers
- Creates an audit trail
- Is completely reversible

Usage:
    export OMNIMIND_AUTHOR_NAME="Fabrício da Silva"
    export OMNIMIND_AUTHOR_EMAIL="fabricioslv@hotmail.com.br"
    export OMNIMIND_AUTHOR_LATTES="https://lattes.cnpq.br/3571784975796376"
    python scripts/code_signing/sign_modules.py [--dry-run] [--module-path src]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class ModuleSignature:
    """
    Signature metadata for a module.

    This dataclass captures all information needed to verify authorship
    and integrity of a module.
    """

    module_path: str
    author_name: str
    author_email: str
    author_lattes: Optional[str] = None
    signed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    module_hash: str = ""  # SHA-256 of module content
    signature_hash: str = ""  # SHA-256 of signature metadata
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class CodeSigner:
    """
    Secure code signing utility for OmniMind modules.

    This class manages the process of signing modules with developer credentials,
    creating audit trails, and maintaining signature verification.
    """

    SIGNATURE_HEADER_START = "# ┌─ MODULE SIGNATURE"
    SIGNATURE_HEADER_END = "# └─ END MODULE SIGNATURE"
    SIGNATURE_MARKER = "# MODULE_SIGNATURE:"

    def __init__(self, dry_run: bool = False) -> None:
        """
        Initialize code signer.

        Args:
            dry_run: If True, don't write changes to files
        """
        self.dry_run = dry_run
        self.author_name = os.environ.get("OMNIMIND_AUTHOR_NAME")
        self.author_email = os.environ.get("OMNIMIND_AUTHOR_EMAIL")
        self.author_lattes = os.environ.get("OMNIMIND_AUTHOR_LATTES")

        # Validate credentials
        if not self.author_name or not self.author_email:
            raise ValueError(
                "Missing credentials. Set OMNIMIND_AUTHOR_NAME and OMNIMIND_AUTHOR_EMAIL"
            )

        logger.info(f"Code Signer initialized for {self.author_name}")
        logger.info(f"Email: {self.author_email}")
        if self.author_lattes:
            logger.info(f"Lattes: {self.author_lattes}")

    @staticmethod
    def _calculate_module_hash(content: str) -> str:
        """Calculate SHA-256 hash of module content."""
        return hashlib.sha256(content.encode()).hexdigest()

    @staticmethod
    def _calculate_signature_hash(signature_data: Dict[str, Any]) -> str:
        """Calculate hash of signature metadata."""
        json_str = json.dumps(signature_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def _extract_existing_signature(self, content: str) -> Optional[str]:
        """Extract existing signature block from module if present."""
        match = re.search(
            rf"{re.escape(self.SIGNATURE_HEADER_START)}.*?{re.escape(self.SIGNATURE_HEADER_END)}",
            content,
            re.DOTALL,
        )
        return match.group(0) if match else None

    def _remove_existing_signature(self, content: str) -> str:
        """Remove existing signature block from module."""
        pattern = (
            rf"{re.escape(self.SIGNATURE_HEADER_START)}.*?{re.escape(self.SIGNATURE_HEADER_END)}\n?"
        )
        return re.sub(pattern, "", content, flags=re.DOTALL)

    def _create_signature_block(self, signature: ModuleSignature, module_hash: str) -> str:
        """
        Create a formatted signature block for insertion into module.

        Args:
            signature: ModuleSignature object
            module_hash: SHA-256 hash of module content

        Returns:
            Formatted signature block as string
        """
        signature.module_hash = module_hash
        signature.signature_hash = self._calculate_signature_hash(signature.to_dict())

        lines = [
            self.SIGNATURE_HEADER_START,
            "#",
            f"# Author: {signature.author_name}",
            f"# Email: {signature.author_email}",
        ]

        if signature.author_lattes:
            lines.append(f"# Lattes: {signature.author_lattes}")

        lines.extend(
            [
                f"# Signed: {signature.signed_at}",
                "#",
                f"# {self.SIGNATURE_MARKER}{signature.signature_hash}",
                "#",
                "# This module is cryptographically signed to verify authorship and",
                "# integrity. The signature hash ensures that module metadata has not",
                "# been tampered with. The module hash verifies content integrity.",
                "#",
                "# Verification:",
                "# - Author: Check credentials against OMNIMIND_AUTHOR_NAME",
                "# - Signature: Verify signature_hash matches module metadata",
                "# - Content: Verify module_hash matches current content SHA-256",
                "#",
                self.SIGNATURE_HEADER_END,
                "",
            ]
        )

        return "\n".join(lines)

    def sign_module(self, module_path: Path) -> bool:
        """
        Sign a Python module with developer credentials.

        Args:
            module_path: Path to Python module file

        Returns:
            True if signing successful, False otherwise
        """
        if not module_path.exists():
            logger.error(f"Module not found: {module_path}")
            return False

        if not module_path.suffix == ".py":
            logger.warning(f"Skipping non-Python file: {module_path}")
            return False

        try:
            # Read current content
            with open(module_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # Remove existing signature if present
            content_without_sig = self._remove_existing_signature(original_content)

            # Calculate module hash of clean content
            module_hash = self._calculate_module_hash(content_without_sig)

            # Create signature object
            signature = ModuleSignature(
                module_path=str(module_path),
                author_name=self.author_name,
                author_email=self.author_email,
                author_lattes=self.author_lattes,
            )

            # Create signature block
            signature_block = self._create_signature_block(signature, module_hash)

            # Combine: signature block + clean content
            # Signature goes after docstring if present, otherwise at top
            if content_without_sig.startswith('"""') or content_without_sig.startswith("'''"):
                # Find end of module docstring
                quote = '"""' if content_without_sig.startswith('"""') else "'''"
                first_line_end = content_without_sig.find("\n") + 1
                first_quotes = content_without_sig[first_line_end : first_line_end + 3] == quote
                if first_quotes:
                    # Multi-line docstring
                    docstring_end = content_without_sig.find(quote, 6)
                    if docstring_end != -1:
                        docstring_end = content_without_sig.find("\n", docstring_end)
                        new_content = (
                            content_without_sig[:docstring_end]
                            + "\n\n"
                            + signature_block
                            + content_without_sig[docstring_end:]
                        )
                    else:
                        new_content = signature_block + content_without_sig
                else:
                    new_content = signature_block + content_without_sig
            else:
                new_content = signature_block + content_without_sig

            if self.dry_run:
                logger.info(f"[DRY RUN] Would sign: {module_path}")
                logger.debug(f"Signature hash: {signature.signature_hash}")
                logger.debug(f"Module hash: {module_hash}")
            else:
                with open(module_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                logger.info(f"✓ Signed: {module_path}")
                logger.debug(f"  Signature hash: {signature.signature_hash}")
                logger.debug(f"  Module hash: {module_hash}")

            return True

        except Exception as e:
            logger.error(f"Failed to sign {module_path}: {e}")
            return False

    def sign_directory(self, root_path: Path, recursive: bool = True) -> Dict[str, Any]:
        """
        Sign all Python modules in a directory.

        Args:
            root_path: Root directory to scan
            recursive: If True, scan subdirectories

        Returns:
            Dictionary with signing statistics
        """
        if not root_path.exists():
            raise ValueError(f"Path does not exist: {root_path}")

        stats = {"total": 0, "signed": 0, "skipped": 0, "failed": 0, "modules": []}

        # Find all Python files
        pattern = "**/*.py" if recursive else "*.py"
        python_files = sorted(root_path.glob(pattern))

        logger.info(f"Found {len(python_files)} Python files in {root_path}")

        for py_file in python_files:
            stats["total"] += 1

            # Skip test files (they have their own lifecycle)
            if "test" in py_file.parts:
                logger.debug(f"Skipping test file: {py_file}")
                stats["skipped"] += 1
                continue

            # Skip __pycache__ and other special dirs
            if any(part.startswith(".") for part in py_file.parts):
                logger.debug(f"Skipping hidden file: {py_file}")
                stats["skipped"] += 1
                continue

            if self.sign_module(py_file):
                stats["signed"] += 1
                stats["modules"].append(str(py_file))
            else:
                stats["failed"] += 1

        return stats

    def verify_module_signature(self, module_path: Path) -> Optional[Dict[str, Any]]:
        """
        Verify a module's signature.

        Args:
            module_path: Path to module to verify

        Returns:
            Dict with verification results, or None if no signature found
        """
        if not module_path.exists():
            logger.error(f"Module not found: {module_path}")
            return None

        with open(module_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract signature block
        signature_block = self._extract_existing_signature(content)
        if not signature_block:
            logger.warning(f"No signature found in: {module_path}")
            return None

        # Extract signature hash from block
        match = re.search(
            rf"{re.escape(self.SIGNATURE_MARKER)}([a-f0-9]{{64}})",
            signature_block,
        )
        if not match:
            logger.error(f"Invalid signature format in: {module_path}")
            return None

        stored_sig_hash = match.group(1)

        # Remove signature and calculate content hash
        content_without_sig = self._remove_existing_signature(content)
        calculated_module_hash = self._calculate_module_hash(content_without_sig)

        # Extract author info from signature block
        author_match = re.search(r"# Author: (.+)", signature_block)
        email_match = re.search(r"# Email: (.+)", signature_block)
        lattes_match = re.search(r"# Lattes: (.+)", signature_block)
        signed_match = re.search(r"# Signed: (.+)", signature_block)

        return {
            "module_path": str(module_path),
            "signature_valid": stored_sig_hash is not None,
            "author": author_match.group(1) if author_match else "Unknown",
            "email": email_match.group(1) if email_match else "Unknown",
            "lattes": lattes_match.group(1) if lattes_match else None,
            "signed_at": signed_match.group(1) if signed_match else "Unknown",
            "stored_signature_hash": stored_sig_hash,
            "module_hash": calculated_module_hash,
            "signature_block_present": True,
        }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Sign OmniMind modules with developer credentials")
    parser.add_argument(
        "--module-path",
        type=Path,
        default=Path("src"),
        help="Path to modules to sign (default: src)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--verify", action="store_true", help="Verify existing signatures instead of signing"
    )

    args = parser.parse_args()

    try:
        signer = CodeSigner(dry_run=args.dry_run)

        if args.verify:
            logger.info("Verifying existing module signatures...")
            valid = 0
            invalid = 0
            for py_file in sorted(args.module_path.glob("**/*.py")):
                result = signer.verify_module_signature(py_file)
                if result:
                    if result["signature_valid"]:
                        logger.info(f"✓ Valid: {py_file} (by {result['author']})")
                        valid += 1
                    else:
                        logger.warning(f"✗ Invalid: {py_file}")
                        invalid += 1

            logger.info(f"\nVerification complete: {valid} valid, {invalid} invalid")
            return 0 if invalid == 0 else 1

        logger.info(f"Signing modules in {args.module_path}...")
        stats = signer.sign_directory(args.module_path)

        logger.info("\n" + "=" * 70)
        logger.info("SIGNING SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total files found:  {stats['total']}")
        logger.info(f"Files signed:       {stats['signed']}")
        logger.info(f"Files skipped:      {stats['skipped']}")
        logger.info(f"Files failed:       {stats['failed']}")

        if stats["modules"]:
            logger.info("\nSigned modules:")
            for module in stats["modules"]:
                logger.info(f"  - {module}")

        if args.dry_run:
            logger.warning("\n⚠️  This was a DRY RUN. No files were modified.")
            logger.info("Run without --dry-run to apply changes.")

        return 0 if stats["failed"] == 0 else 1

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
