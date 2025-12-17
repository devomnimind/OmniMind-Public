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
Deploy OmniMind Test Suite to Hugging Face Spaces
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional


def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        from dotenv import load_dotenv

        load_dotenv(env_file)
        print("✓ Loaded environment from .env file")


def run_command(cmd: list[str], cwd: Optional[Path] = None) -> bool:
    """Run a command and return success status."""
    try:
        subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=True)
        print(f"✓ {cmd[0]} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {cmd[0]} failed: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def deploy_to_huggingface():
    """Deploy the test suite to Hugging Face Spaces."""

    # Load environment variables
    load_env_file()

    # Get project root
    project_root = Path(__file__).parent.parent
    space_dir = project_root / "deploy" / "huggingface" / "tests"

    if not space_dir.exists():
        print(f"✗ Space directory not found: {space_dir}")
        return False

    # Check if huggingface_hub is installed
    try:
        import importlib.util

        if not importlib.util.find_spec("huggingface_hub"):
            raise ImportError
    except ImportError:
        print("Installing huggingface_hub...")
        if not run_command([sys.executable, "-m", "pip", "install", "huggingface_hub"]):
            return False

    # Get token from environment
    token = os.getenv("HUGGING_FACE_HUB_TOKEN") or os.getenv("HF_TOKEN")
    if not token:
        print(
            "✗ No Hugging Face token found. Set HUGGING_FACE_HUB_TOKEN or HF_TOKEN environment variable."
        )
        return False

    # Set space name with namespace
    space_name = "fabricioslv/omnimind-tests"

    print(f"🚀 Deploying OmniMind tests to Hugging Face Space: {space_name}")

    # Use huggingface_hub API to create/update the space
    try:
        from huggingface_hub import HfApi, create_repo

        api = HfApi(token=token)

        # Create space if it doesn't exist
        if not api.repo_exists(f"{space_name}", repo_type="space"):
            print("Creating new space...")
            create_repo(space_name, token=token, repo_type="space", space_sdk="docker")
            print("✓ Space created")
        else:
            print("Space already exists, updating...")

        # Upload files
        print("Uploading files...")
        api.upload_folder(
            folder_path=str(space_dir), repo_id=space_name, repo_type="space", token=token
        )
        print("✓ Files uploaded")

    except Exception as e:
        print(f"✗ API deployment failed: {e}")
        return False

    print(f"✅ Successfully deployed to https://huggingface.co/spaces/{space_name}")
    return True


def space_exists(space_name: str, token: str) -> bool:
    """Check if space already exists."""
    try:
        from huggingface_hub import HfApi

        api = HfApi(token=token)
        return api.repo_exists(f"{space_name}", repo_type="space")
    except Exception:
        return False


if __name__ == "__main__":
    success = deploy_to_huggingface()
    sys.exit(0 if success else 1)
