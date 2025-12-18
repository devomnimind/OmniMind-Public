import json
import os
from pathlib import Path

from dotenv import load_dotenv

# Mock environment like in the script
load_dotenv()

print(f"ENV USER: {os.environ.get('OMNIMIND_DASHBOARD_USER')}")
print(f"ENV PASS: {os.environ.get('OMNIMIND_DASHBOARD_PASS')}")

auth_file = Path("config/dashboard_auth.json")
print(f"Auth File: {auth_file} (Exists: {auth_file.exists()})")

if auth_file.exists():
    with auth_file.open("r") as f:
        print(f"File Content: {f.read()}")


def _get_dashboard_credentials():
    # 1. Try JSON file (Source of Truth for Local Sovereignty)
    auth_file = Path(os.environ.get("OMNIMIND_DASHBOARD_AUTH_FILE", "config/dashboard_auth.json"))
    if auth_file.exists():
        try:
            with auth_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                # The auth.py code:
                return data.get("user", ""), data.get("pass", "")
        except Exception as e:
            print(f"Error reading file: {e}")

    # 2. Try Environment Variables
    env_user = os.getenv("OMNIMIND_DASHBOARD_USER") or os.getenv("DASHBOARD_USER")
    env_pass = os.getenv("OMNIMIND_DASHBOARD_PASS") or os.getenv("DASHBOARD_PASS")

    if env_user and env_pass:
        return env_user, env_pass

    return "admin", "omnimind2025!"


u, p = _get_dashboard_credentials()
print(f"Resolved Credentials: User='{u}', Pass='{p}'")
