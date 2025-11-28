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
Show secrets that need to be configured in Hugging Face Space
"""

import os
from pathlib import Path


def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        from dotenv import load_dotenv

        load_dotenv(env_file)
        print("✓ Loaded environment from .env file")


def show_secrets():
    """Show the secrets that need to be configured in the Space."""

    load_env_file()

    secrets = {
        "HUGGING_FACE_HUB_TOKEN": os.getenv("HUGGING_FACE_HUB_TOKEN"),
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN"),
        "HF_SPACE_URL": os.getenv("HF_SPACE_URL"),
    }

    print("🔐 Secrets to configure in Hugging Face Space:")
    print("https://huggingface.co/spaces/fabricioslv/omnimind-tests/settings\n")

    for name, value in secrets.items():
        if value:
            # Mask the token for security
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {name}: {masked}")
        else:
            print(f"❌ {name}: NOT FOUND")

    print("\n📋 Copy these values to Space Settings > Secrets")
    print("🔄 After configuring secrets, restart the Space")


if __name__ == "__main__":
    show_secrets()
