#!/usr/bin/env python3
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
        "HF_SPACE_URL": os.getenv("HF_SPACE_URL")
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