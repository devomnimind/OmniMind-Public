#!/usr/bin/env python3
"""
Unsign Modules - Remove Code Signatures Safely

This script removes all signature blocks from modules, reverting them to
their original state without affecting actual code.

Usage:
    python scripts/code_signing/unsign_modules.py [--dry-run] [--module-path src]
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from typing import Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CodeUnsigner:
    """
    Utility to safely remove code signatures from modules.

    This class removes only signature blocks, leaving all actual code intact.
    """

    SIGNATURE_HEADER_START = "# ┌─ MODULE SIGNATURE"
    SIGNATURE_HEADER_END = "# └─ END MODULE SIGNATURE"

    def __init__(self, dry_run: bool = False) -> None:
        """
        Initialize code unsigner.

        Args:
            dry_run: If True, don't write changes to files
        """
        self.dry_run = dry_run
        logger.info("Code Unsigner initialized")

    @staticmethod
    def _remove_signature(content: str) -> tuple[str, bool]:
        """
        Remove signature block from content.

        Args:
            content: File content

        Returns:
            Tuple of (modified_content, was_signed)
        """
        pattern = rf"{re.escape(CodeUnsigner.SIGNATURE_HEADER_START)}.*?{re.escape(CodeUnsigner.SIGNATURE_HEADER_END)}\n?"
        match = re.search(pattern, content, flags=re.DOTALL)

        if not match:
            return content, False

        # Remove the signature block
        modified = re.sub(pattern, "", content, flags=re.DOTALL)
        return modified, True

    def unsign_module(self, module_path: Path) -> bool:
        """
        Remove signature from a module.

        Args:
            module_path: Path to module

        Returns:
            True if unsigned successfully, False otherwise
        """
        if not module_path.exists():
            logger.error(f"Module not found: {module_path}")
            return False

        if not module_path.suffix == ".py":
            logger.warning(f"Skipping non-Python file: {module_path}")
            return False

        try:
            with open(module_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            modified_content, was_signed = self._remove_signature(original_content)

            if not was_signed:
                logger.debug(f"Not signed: {module_path}")
                return False

            if self.dry_run:
                logger.info(f"[DRY RUN] Would unsign: {module_path}")
            else:
                with open(module_path, "w", encoding="utf-8") as f:
                    f.write(modified_content)
                logger.info(f"✓ Unsigned: {module_path}")

            return True

        except Exception as e:
            logger.error(f"Failed to unsign {module_path}: {e}")
            return False

    def unsign_directory(
        self, root_path: Path, recursive: bool = True
    ) -> Dict[str, int]:
        """
        Remove signatures from all modules in directory.

        Args:
            root_path: Root directory to scan
            recursive: If True, scan subdirectories

        Returns:
            Dictionary with statistics
        """
        if not root_path.exists():
            raise ValueError(f"Path does not exist: {root_path}")

        stats = {"total": 0, "unsigned": 0, "not_signed": 0, "failed": 0}

        pattern = "**/*.py" if recursive else "*.py"
        python_files = sorted(root_path.glob(pattern))

        logger.info(f"Found {len(python_files)} Python files in {root_path}")

        for py_file in python_files:
            stats["total"] += 1

            # Skip __pycache__ and hidden files
            if any(part.startswith(".") for part in py_file.parts):
                logger.debug(f"Skipping hidden file: {py_file}")
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                _, was_signed = self._remove_signature(content)

                if was_signed:
                    if self.unsign_module(py_file):
                        stats["unsigned"] += 1
                    else:
                        stats["failed"] += 1
                else:
                    stats["not_signed"] += 1

            except Exception as e:
                logger.error(f"Error checking {py_file}: {e}")
                stats["failed"] += 1

        return stats


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Remove code signatures from OmniMind modules"
    )
    parser.add_argument(
        "--module-path",
        type=Path,
        default=Path("src"),
        help="Path to modules to unsign (default: src)",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be done without making changes"
    )

    args = parser.parse_args()

    try:
        unsigner = CodeUnsigner(dry_run=args.dry_run)

        logger.info(f"Removing signatures from modules in {args.module_path}...")
        stats = unsigner.unsign_directory(args.module_path)

        logger.info("\n" + "=" * 70)
        logger.info("UNSIGNING SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total files found:     {stats['total']}")
        logger.info(f"Files unsigned:        {stats['unsigned']}")
        logger.info(f"Files not signed:      {stats['not_signed']}")
        logger.info(f"Files failed:          {stats['failed']}")

        if args.dry_run:
            logger.warning("\n⚠️  This was a DRY RUN. No files were modified.")
            logger.info("Run without --dry-run to apply changes.")

        return 0 if stats["failed"] == 0 else 1

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
