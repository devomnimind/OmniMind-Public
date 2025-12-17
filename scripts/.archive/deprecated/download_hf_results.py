#!/usr/bin/env python3
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
Download test results from Hugging Face Space
"""

import os
import sys
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from huggingface_hub import HfApi


def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        print("✓ Loaded environment from .env file")


def download_test_results():
    """Download test results from the Hugging Face Space."""

    # Load environment variables
    load_env_file()

    # Get token from environment
    token = os.getenv("HUGGING_FACE_HUB_TOKEN") or os.getenv("HF_TOKEN")
    if not token:
        print("✗ No Hugging Face token found.")
        return False

    space_name = "fabricioslv/omnimind-tests"

    try:
        api = HfApi(token=token)

        # Create local directory for results
        results_dir = Path("data/test_reports/huggingface")
        results_dir.mkdir(parents=True, exist_ok=True)

        # Download test reports
        print(f"📥 Downloading test results from {space_name}...")

        # Try to download coverage.json
        try:
            api.hf_hub_download(
                repo_id=space_name,
                filename="data/test_reports/coverage.json",
                local_dir=".",
                repo_type="space",
            )
            print("✓ Downloaded coverage.json")
        except Exception as e:
            print(f"⚠️  Could not download coverage.json: {e}")

        # Try to download htmlcov
        try:
            api.hf_hub_download(
                repo_id=space_name,
                filename="data/test_reports/htmlcov/index.html",
                local_dir=".",
                repo_type="space",
            )
            print("✓ Downloaded HTML coverage report")
        except Exception as e:
            print(f"⚠️  Could not download HTML coverage: {e}")

        print("✅ Test results downloaded to data/test_reports/huggingface/")
        return True

    except Exception as e:
        print(f"✗ Failed to download results: {e}")
        return False


if __name__ == "__main__":
    success = download_test_results()
    sys.exit(0 if success else 1)
